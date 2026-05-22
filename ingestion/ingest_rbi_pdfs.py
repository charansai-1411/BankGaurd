import os
import io
import tempfile
import requests
import pypdf
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from shared.gemini_client import get_embedding
from shared.r2_client import upload_file_to_r2
from ingestion.embed_utils import recursive_character_split, store_embeddings

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts text from PDF bytes using pypdf.
    """
    pdf_file = io.BytesIO(pdf_bytes)
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def extract_text_from_html(html_content: str) -> str:
    """
    Extracts clean text from HTML content, skipping boilerplate scripts/styles.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        script.extract()
    
    # Check for main container elements
    main_content = soup.find(id='form1') or soup.find(class_='table-responsive') or soup.body
    if main_content:
        text = main_content.get_text(separator='\n')
    else:
        text = soup.get_text(separator='\n')
        
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def ingest_pdf(file_path: str, agent_domain: str, document_id: str):
    """
    Parses a local PDF file, chunks text, generates embeddings, uploads PDF to Cloudflare R2,
    and stores chunks in Supabase vector_store.
    """
    print(f"Ingesting PDF: {file_path} for agent domain: {agent_domain}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Local PDF file not found: {file_path}")
        
    # Read text
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    
    text = extract_text_from_pdf_bytes(pdf_bytes)
    if not text.strip():
        return {"status": "error", "message": "Failed to extract text or PDF is empty"}
        
    # Upload to Cloudflare R2
    r2_key = f"rbi_pdfs/{document_id}/{os.path.basename(file_path)}"
    r2_url = upload_file_to_r2(file_path, r2_key)
    
    # Split text
    chunks = recursive_character_split(text, chunk_size=800, chunk_overlap=100)
    
    # Generate embeddings
    embeddings = []
    for chunk in chunks:
        embeddings.append(get_embedding(chunk))
        
    # Save to db
    namespace = f"{agent_domain}_regulation"
    metadata_list = [{
        "document_id": document_id,
        "source": "local_pdf",
        "file_name": os.path.basename(file_path),
        "r2_url": r2_url
    } for _ in chunks]
    
    store_embeddings(namespace, chunks, embeddings, metadata_list)
    return {"status": "success", "chunks_count": len(chunks), "r2_url": r2_url}

def scrape_rbi_notifications(limit: int = 5) -> list[dict]:
    """
    Scrapes the live RBI notifications page to get recent compliance circulars.
    """
    url = "https://rbi.org.in/Scripts/NotificationUser.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        # Disable SSL verification warnings if necessary
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        if r.status_code != 200:
            print(f"Failed to load RBI site: {r.status_code}")
            return []
            
        soup = BeautifulSoup(r.text, 'html.parser')
        notifications = []
        
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if 'NotificationUser.aspx?Id=' in href or href.lower().endswith('.pdf'):
                # Resolve full URL
                if href.startswith('/'):
                    full_url = "https://rbi.org.in" + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = "https://rbi.org.in/Scripts/" + href
                    
                if not any(n['url'] == full_url for n in notifications):
                    notifications.append({
                        "title": text,
                        "url": full_url
                    })
                    if len(notifications) >= limit:
                        break
        return notifications
    except Exception as e:
        print(f"Error scraping RBI notifications: {e}")
        return []

def download_and_ingest_circular(url: str, agent_domain: str, document_id: str):
    """
    Downloads a circular from a given URL, extracts text, chunks it, generates embeddings,
    archives it to Cloudflare R2, and uploads chunks to Supabase.
    """
    print(f"Downloading and ingesting circular from: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=20, verify=False)
        if r.status_code != 200:
            return {"status": "error", "message": f"Failed to download URL. Status: {r.status_code}"}
            
        content_type = r.headers.get('content-type', '').lower()
        is_pdf = 'pdf' in content_type or url.lower().endswith('.pdf')
        
        if is_pdf:
            text = extract_text_from_pdf_bytes(r.content)
            extension = ".pdf"
        else:
            text = extract_text_from_html(r.text)
            extension = ".html"
            
        if not text.strip():
            return {"status": "error", "message": "Extracted text is empty"}
            
        # Write to a temporary file locally so we can upload it to R2
        file_name = f"circular_{document_id}{extension}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_file.write(r.content)
            temp_file_path = temp_file.name
            
        try:
            r2_key = f"rbi_pdfs/{document_id}/{file_name}"
            r2_url = upload_file_to_r2(temp_file_path, r2_key)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
        # Split text
        chunks = recursive_character_split(text, chunk_size=800, chunk_overlap=100)
        
        # Generate embeddings
        embeddings = [get_embedding(chunk) for chunk in chunks]
        
        # Save to db
        namespace = f"{agent_domain}_regulation"
        metadata_list = [{
            "document_id": document_id,
            "source": "web_scraped",
            "url": url,
            "r2_url": r2_url
        } for _ in chunks]
        
        store_embeddings(namespace, chunks, embeddings, metadata_list)
        return {"status": "success", "chunks_count": len(chunks), "r2_url": r2_url}
    except Exception as e:
        print(f"Error in download_and_ingest_circular: {e}")
        return {"status": "error", "message": str(e)}

def search_and_ingest_fallback(query: str, agent_domain: str, document_id: str, limit: int = 2):
    """
    Search DuckDuckGo for relevant RBI circulars, fetches the top results, and ingests them.
    Falls back to Yahoo search if DuckDuckGo fails or blocks the request.
    """
    print(f"Searching web fallback for: {query}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    search_query = f"site:rbi.org.in circular {query}"
    links = []
    
    # 1. Try DuckDuckGo
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(search_query)}"
        r = requests.get(search_url, headers=headers, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', class_='result__a'):
                href = a.get('href')
                if href:
                    if href.startswith('/l/?'):
                        parsed = urlparse(href)
                        uddg = parse_qs(parsed.query).get('uddg')
                        if uddg:
                            href = uddg[0]
                    links.append(href)
        else:
            print(f"DuckDuckGo search returned status: {r.status_code}. Trying Yahoo fallback...")
    except Exception as e:
        print(f"Error querying DuckDuckGo: {e}. Trying Yahoo fallback...")
        
    # 2. Try Yahoo Fallback if DuckDuckGo failed to retrieve any links
    if not links:
        try:
            yahoo_url = f"https://search.yahoo.com/search?p={requests.utils.quote(search_query)}"
            r = requests.get(yahoo_url, headers=headers, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for h3 in soup.find_all('h3'):
                    a = h3.find('a')
                    if a:
                        href = a.get('href', '')
                        if href.startswith('http') and 'yahoo.com' not in href:
                            links.append(href)
            else:
                print(f"Yahoo search returned status: {r.status_code}")
        except Exception as e:
            print(f"Error querying Yahoo search: {e}")
            
    # Filter and ingest top results
    rbi_links = [lnk for lnk in links if "rbi.org.in" in lnk]
    if not rbi_links:
        rbi_links = links[:limit] # fallback to any search result if rbi.org.in is missing
    else:
        rbi_links = rbi_links[:limit]
        
    if not rbi_links:
        return {"status": "error", "message": "No search results found from any provider"}
        
    success_count = 0
    ingested_chunks = 0
    for i, link in enumerate(rbi_links):
        sub_doc_id = f"{document_id}_fallback_{i}"
        res = download_and_ingest_circular(link, agent_domain, sub_doc_id)
        if res.get("status") == "success":
            success_count += 1
            ingested_chunks += res.get("chunks_count", 0)
            
    return {
        "status": "success",
        "searched_links": rbi_links,
        "downloaded_count": success_count,
        "total_chunks_ingested": ingested_chunks
    }
