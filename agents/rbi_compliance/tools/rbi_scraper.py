from typing import List, Dict, Any

def scrape_rbi(query: str, circular_type: str) -> List[Dict[str, Any]]:
    """
    Scrapes rbi.org.in for matching query.
    """
    # Stub response representing a scraped live circular
    return [
        {
            "title": f"RBI Directive on {query}",
            "date": "2026-05-15",
            "url": "https://rbi.org.in/scripts/BS_CircularIndexDisplay.aspx?id=12345",
            "content": f"Live circular details concerning {query} as of May 2026."
        }
    ]
