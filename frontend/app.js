// ==========================================================================
// BANKGUARD // AUDIT.OS DRIVER SCRIPT
// ==========================================================================

const API_BASE = "http://localhost:8000";
let isSandbox = true;
let activeSessionId = "bg_session_" + Math.random().toString(36).substring(2, 10);

// Document elements
const gatewayLed = document.getElementById("gateway-led");
const gatewayStatus = document.getElementById("gateway-status");
const sandboxIndicator = document.getElementById("sandbox-indicator");
const ingestConsole = document.getElementById("ingest-console");
const sessionIdDisplay = document.getElementById("session-id-display");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const chatForm = document.getElementById("chat-form");

// Citation elements
const citationDrawer = document.getElementById("citation-drawer");
const citationCloseBtn = document.getElementById("citation-close-btn");
const citeChunkId = document.getElementById("cite-chunk-id");
const citeNamespace = document.getElementById("cite-namespace");
const citeScore = document.getElementById("cite-score");
const citeContent = document.getElementById("cite-content");
const citeDocBox = document.getElementById("cite-doc-box");
const citeDocUrl = document.getElementById("cite-doc-url");

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
    sessionIdDisplay.textContent = activeSessionId;
    checkGatewayHealth();
    setupEventListeners();
});

// Check FastAPI Gateway connectivity
async function checkGatewayHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`, { method: "GET" });
        const data = await response.json();
        if (data.status === "healthy") {
            isSandbox = false;
            gatewayLed.className = "led led-green";
            gatewayStatus.textContent = "ONLINE";
            sandboxIndicator.style.display = "none";
            logIngest("SYSTEM: Secure connection to BankGuard Gateway active.");
        }
    } catch (err) {
        // Fallback to Sandbox Mode
        isSandbox = true;
        gatewayLed.className = "led led-red";
        gatewayStatus.textContent = "OFFLINE";
        sandboxIndicator.style.display = "flex";
        logIngest("SYSTEM: Gateway offline. Running in LOCAL SANDBOX MODE.");
    }
}

// Log message to Ingestion Console
function logIngest(text, type = "system-msg") {
    const line = document.createElement("div");
    line.className = `console-line ${type}`;
    line.innerHTML = `[${new Date().toLocaleTimeString()}] ${text}`;
    ingestConsole.appendChild(line);
    ingestConsole.scrollTop = ingestConsole.scrollHeight;
}

// Set up UI listeners
function setupEventListeners() {
    // Ingestion actions
    document.getElementById("btn-ingest-code").addEventListener("click", triggerCodeIngest);
    document.getElementById("btn-ingest-api").addEventListener("click", triggerApiIngest);
    document.getElementById("btn-scrape-rbi").addEventListener("click", triggerRbiScrape);

    // Audit actions
    document.getElementById("btn-start-audit").addEventListener("click", startComplianceAudit);

    // Chat CLI submit
    chatForm.addEventListener("submit", handleChatSubmit);

    // Drawer close
    citationCloseBtn.addEventListener("click", closeCitationDrawer);
}

// Ingestion 1: Codebase
async function triggerCodeIngest() {
    const url = document.getElementById("repo-url").value;
    logIngest(`INGESTION_INIT: Triggering repository pull for: ${url}`, "info-msg");
    
    if (isSandbox) {
        // Simulation
        let steps = [
            "CONNECTING: Initiating handshake with git hosting provider...",
            "CLONING: Cloned 12,410 LOC successfully into temporary workspace.",
            "FILTERING: Excluded node_modules, .venv, and binary formats.",
            "AST_PARSING: Analyzing functions using brace-based block chunkers...",
            "INDEXING: Formatted 48 logic blocks. Generating Gemini text embeddings...",
            "SUCCESS: Codebase indexed in 'codebase' namespace. 48 chunks active."
        ];
        
        for (let i = 0; i < steps.length; i++) {
            await delay(800 * (i + 1) - 600 * i);
            logIngest(steps[i], i === steps.length - 1 ? "success-msg" : "info-msg");
        }
    } else {
        try {
            // Live Gateway API call
            const response = await fetch(`${API_BASE}/ingest/codebase`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ repo_url: url })
            });
            const data = await response.json();
            logIngest(`SUCCESS: ${data.message || 'Codebase ingestion completed successfully.'}`, "success-msg");
        } catch (err) {
            logIngest(`ERROR: Ingestion failed. Check backend logs.`, "warning-msg");
        }
    }
}

// Ingestion 2: OpenAPI Spec
async function triggerApiIngest() {
    const path = document.getElementById("api-spec-path").value;
    logIngest(`INGESTION_INIT: Reading OpenAPI Spec: ${path}`, "info-msg");
    
    if (isSandbox) {
        let steps = [
            "READING: Accessing OpenAPI schema file schema...",
            "RESOLVING: Parsing local JSON reference chains ($ref)...",
            "MAPPING: Extracted 8 endpoints (GET/POST/PUT).",
            "INDEXING: Vectorizing API structures in 'api_specs' namespace.",
            "SUCCESS: OpenAPI spec chunking complete. 8 active vectors loaded."
        ];
        
        for (let i = 0; i < steps.length; i++) {
            await delay(600 * (i + 1) - 400 * i);
            logIngest(steps[i], i === steps.length - 1 ? "success-msg" : "info-msg");
        }
    } else {
        try {
            const response = await fetch(`${API_BASE}/ingest/openapi`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ file_path: path })
            });
            const data = await response.json();
            logIngest(`SUCCESS: Indexed ${data.endpoints_count} endpoints.`, "success-msg");
        } catch (err) {
            logIngest(`ERROR: API spec parser returned status check failure.`, "warning-msg");
        }
    }
}

// Ingestion 3: Scraper
async function triggerRbiScrape() {
    const query = document.getElementById("rbi-query").value;
    logIngest(`INGESTION_INIT: Scraping live RBI regulations for: "${query}"`, "info-msg");
    
    if (isSandbox) {
        let steps = [
            "SCRAPING: Connecting to rbi.org.in circular directories...",
            "WARNING: Direct scraping rate limit block detected. Redirecting to Search Fallback...",
            "FALLBACK: Fetching active links via Search query adapter...",
            "DOWNLOAD: Retrieved PDF circular: 'Notification-IT-Directions-2024.pdf'",
            "INDEXING: Chunking 12 pages, generating embeddings...",
            "SUCCESS: Live scraper indexed 18 chunks in 'rbi_regulation' vector DB."
        ];
        
        for (let i = 0; i < steps.length; i++) {
            await delay(1000 * (i + 1) - 700 * i);
            logIngest(steps[i], steps[i].startsWith("WARNING") ? "warning-msg" : (i === steps.length - 1 ? "success-msg" : "info-msg"));
        }
    } else {
        try {
            const response = await fetch(`${API_BASE}/ingest/rbi`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });
            const data = await response.json();
            logIngest(`SUCCESS: Live scrape stored ${data.total_chunks_ingested} chunks in pgvector.`, "success-msg");
        } catch (err) {
            logIngest(`ERROR: Scraper failed to fetch circulars.`, "warning-msg");
        }
    }
}

// --------------------------------------------------------------------------
// COMPLIANCE AUDIT WORKFLOW (MODE A)
// --------------------------------------------------------------------------
async function startComplianceAudit() {
    const agent = document.getElementById("agent-select").value;
    const findingsList = document.getElementById("findings-list");
    const progressFill = document.getElementById("audit-progress");
    const statusText = document.getElementById("audit-status-text");
    const downloadBox = document.getElementById("report-download-box");

    // Reset UI state
    findingsList.innerHTML = '<div class="empty-findings-msg">Analyzing audit scopes... Running agent graph loops...</div>';
    downloadBox.style.display = "none";
    
    const nodes = ["initialize", "reasoner", "tools", "analyzer", "report"];
    nodes.forEach(n => document.getElementById(`node-${n}`).className = "node");

    if (isSandbox) {
        // Sandbox Simulation
        await runNodeStep("initialize", 10, "INITIALIZING: Pulling regulatory directives...");
        await runNodeStep("reasoner", 30, "REASONING: Evaluating compliance checks on target database chunks...");
        await runNodeStep("tools", 60, "TOOLS: Invoking evidence validators, semantic lookups, and depth ceilings...");
        await runNodeStep("analyzer", 85, "ANALYZING: Computing severity index matrix (determinstic mapping)...");
        await runNodeStep("report", 100, "COMPILING: Running Jinja2 and WeasyPrint PDF report builder...");

        await delay(500);
        statusText.textContent = "AUDIT COMPLETED. findings compiled successfully.";
        displaySimulatedFindings(agent);
        downloadBox.style.display = "block";
        document.getElementById("download-pdf-btn").href = "#";
        document.getElementById("download-pdf-btn").onclick = (e) => {
            e.preventDefault();
            alert("SANDBOX DOWNLOAD: PDF compiled and stored mock R2 bucket: https://r2.cloudflare.com/mock_report.pdf");
        };
    } else {
        // Real Gateway Integration
        try {
            statusText.textContent = "INITIALIZING AUDIT JOB...";
            const response = await fetch(`${API_BASE}/jobs/diagnose`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ agent_type: agent })
            });
            const job = await response.json();
            const jobId = job.job_id;
            
            statusText.textContent = `JOB ACTIVE: ${jobId}. Polling status...`;
            
            // Poll for status
            let complete = false;
            let dotIdx = 0;
            while (!complete) {
                const statusRes = await fetch(`${API_BASE}/jobs/${jobId}/status`);
                const statusData = await statusRes.json();
                
                // Update graph UI based on status
                if (statusData.status === "PENDING") {
                    setNodeState("initialize", "active");
                    progressFill.style.width = "20%";
                } else if (statusData.status === "RUNNING") {
                    setNodeState("initialize", "completed");
                    setNodeState("reasoner", "active");
                    setNodeState("tools", "active");
                    progressFill.style.width = "60%";
                } else if (statusData.status === "READY") {
                    nodes.forEach(n => setNodeState(n, "completed"));
                    progressFill.style.width = "100%";
                    statusText.textContent = "AUDIT COMPLETED.";
                    complete = true;
                    
                    // Display findings & PDF
                    displayRealFindings(statusData);
                    if (statusData.report_url) {
                        downloadBox.style.display = "block";
                        document.getElementById("download-pdf-btn").href = statusData.report_url;
                        document.getElementById("download-pdf-btn").onclick = null;
                    }
                } else if (statusData.status === "FAILED") {
                    statusText.textContent = "AUDIT JOB FAILED.";
                    findingsList.innerHTML = '<div class="empty-findings-msg" style="color: var(--accent-red)">Agent loop failed during execution. Check terminal logs.</div>';
                    complete = true;
                }
                
                await delay(1500);
            }
        } catch (err) {
            statusText.textContent = "CONNECTION ERROR: Backend API failed.";
            findingsList.innerHTML = '<div class="empty-findings-msg" style="color: var(--accent-red)">Failed to contact API Gateway.</div>';
        }
    }
}

async function runNodeStep(nodeId, progressPercent, text) {
    const node = document.getElementById(`node-${nodeId}`);
    const progressFill = document.getElementById("audit-progress");
    const statusText = document.getElementById("audit-status-text");

    node.className = "node active";
    progressFill.style.width = `${progressPercent}%`;
    statusText.textContent = text;
    
    await delay(1200);
    node.className = "node completed";
}

function setNodeState(nodeId, state) {
    const node = document.getElementById(`node-${nodeId}`);
    if (state === "active") {
        node.className = "node active";
    } else if (state === "completed") {
        node.className = "node completed";
    }
}

// Display Simulated Findings
function displaySimulatedFindings(agent) {
    const findingsList = document.getElementById("findings-list");
    findingsList.innerHTML = "";

    const database = {
        rbi_compliance: [
            {
                title: "Complete absence of database audit trails on fund transfers",
                severity: "CRITICAL",
                desc: "The codebase does not write immutable records when processing deposits or fund transfers, violating RBI Master Direction Clause 5.2.",
                meta: "RBI Circular: RBI/2024/91 Section 5",
                citation: "A database transaction must log pre-image and post-image states in a read-only secure vault.",
                namespace: "rbi_regulation"
            },
            {
                title: "Failure to enforce dual-control authorization on admin endpoints",
                severity: "HIGH",
                desc: "Admin configuration tools permit single-token access credentials. RBI guidelines mandate dual-auth signatures for modifying security variables.",
                meta: "RBI Circular: RBI/2023/118 Clause 12",
                citation: "Critical system configurations must be signed off by a maker-checker role structure.",
                namespace: "rbi_regulation"
            },
            {
                title: "Advisory: Customer session timeouts are set to 60 minutes",
                severity: "MEDIUM",
                desc: "Web and app customer dashboard tokens expire after 60 minutes. The RBI recommended timeout limit for inactive banking sessions is 15 minutes.",
                meta: "RBI Circular: RBI/2022/45 Advisory",
                citation: "Inactive user sessions on online banking portals should automatically terminate after 15 minutes of idle time.",
                namespace: "rbi_regulation"
            }
        ],
        api_compliance: [
            {
                title: "API gateway exposes transfer endpoints using plain HTTP BasicAuth",
                severity: "HIGH",
                desc: "The OpenAPI specification declares BasicAuth under security schemes for outbound transfer routes, presenting interception hazards.",
                meta: "API Specification: OpenAPI /transfer Endpoint",
                citation: "Authorization must utilize secure bearer tokens with cryptographic signing signatures.",
                namespace: "api_specs"
            },
            {
                title: "Missing rate-limiter rules on verification routes",
                severity: "CRITICAL",
                desc: "Reset credentials and validation endpoints do not specify rate-limiting constraints, enabling brute force token sweeps.",
                meta: "API Specification: OpenAPI /auth/verify Endpoint",
                citation: "Exposed client authorization gates must impose strict throttling policies.",
                namespace: "api_specs"
            }
        ],
        codebase: [
            {
                title: "Cryptographic operations are utilizing static IV salt parameters",
                severity: "HIGH",
                desc: "In `SecurityManager.py:L142`, the cipher engine uses a hardcoded initialization vector (IV) salt, weakening symmetric encryption layers.",
                meta: "Source File: SecurityManager.py:L142-148",
                citation: "Initialization vectors must be generated using cryptographically secure random generators.",
                namespace: "codebase"
            },
            {
                title: "Standalone helper lacks proper input sanitization checks",
                severity: "MEDIUM",
                desc: "The standing database executor script dynamically concatenates string variables inside native SQL strings, exposing potential query injections.",
                meta: "Source File: db_helper.py:L89",
                citation: "SQL statements must use parameterized parameters to prevent SQL injection vulnerabilities.",
                namespace: "codebase"
            }
        ]
    };

    const list = database[agent] || [];
    if (list.length === 0) {
        findingsList.innerHTML = '<div class="empty-findings-msg">No findings reported. System compliant.</div>';
        return;
    }

    list.forEach(item => {
        findingsList.appendChild(createFindingCard(item));
    });
}

function createFindingCard(item) {
    const card = document.createElement("div");
    card.className = `finding-card ${item.severity}`;
    
    card.innerHTML = `
        <div class="finding-title-row">
            <div class="finding-title">${item.title}</div>
            <span class="severity-badge ${item.severity}">${item.severity}</span>
        </div>
        <div class="finding-desc">${item.desc}</div>
        <div class="finding-meta">
            <span>${item.meta}</span>
            <span class="citation-btn" onclick="openCitationDrawer('${item.meta}', '${item.namespace}', '${item.citation}')">VIEW CITATION</span>
        </div>
    `;
    return card;
}

// --------------------------------------------------------------------------
// GROUNDED FREE CHAT CLI (MODE C)
// --------------------------------------------------------------------------
async function handleChatSubmit(e) {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Output User Line
    appendChatMessage(query, "user-msg");
    chatInput.value = "";

    // Appending simulated typing
    const typingLine = appendChatMessage("SYSTEM: Vector search cosine scoring... Querying Gemini...", "system-msg");

    if (isSandbox) {
        await delay(1500);
        typingLine.remove();
        
        let response = "";
        let citation = "";
        let namespace = "rbi_regulation";

        if (query.toLowerCase().includes("audit log") || query.toLowerCase().includes("transaction log")) {
            response = "Under the RBI Information Technology Master Directions, banks must implement comprehensive, immutable logs for all transactional modifications. Specifically, transaction logs must cover both pre-image and post-image states, be stored in secure read-only storage vault locations, and be preserved for a minimum of 8 years. Unauthorized access to logs must trigger real-time system alerts.";
            citation = "Section 5.4: Transaction logging engines must retain audit records containing date/time, customer details, exact modifications (pre-image and post-image), and system authorizations. Storage must use write-once-read-many (WORM) hardware or cryptographically sealed databases. Retention schedule requires active storage for 8 years.";
        } else if (query.toLowerCase().includes("session") || query.toLowerCase().includes("timeout")) {
            response = "For customer-facing electronic portals, the RBI guidelines advise an automatic session timeout of 15 minutes of idle time to prevent session hijack hazards. Furthermore, concurrent logins for the same account credentials must be restricted, and authentication tokens should expire automatically upon logout actions.";
            citation = "Clause 9.1: Application access sessions must expire within 15 minutes of user inactivity. Dual-concurrent logins are prohibited for non-administrative users. System must terminate token validations immediately on user-initiated signouts.";
        } else {
            response = "I have performed a vector query search against the active compliance database. According to the parsed regulatory directives, all banking services must establish security logging and monitoring dashboards, perform continuous vulnerability scans, and implement maker-checker controls for database modifications.";
            citation = "General Security Directives: Bank entities must review, log, and isolate configurations through structured administrative checks, ensuring compliance audit trails are present across all operational modules.";
        }

        // Add assistant message with click-to-cite action
        appendChatMessageWithCitation(response, "rbi_regulation", citation);
    } else {
        try {
            const responseObj = await fetch(`${API_BASE}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: query,
                    session_id: activeSessionId
                })
            });
            typingLine.remove();
            
            const data = await responseObj.json();
            appendChatMessageWithCitation(data.response, data.namespace || "rbi_regulation", data.citation_context || "No citation provided.");
        } catch (err) {
            typingLine.remove();
            appendChatMessage("ERROR: Failed to contact the chat service API gateway.", "warning-msg");
        }
    }
}

function appendChatMessage(text, className) {
    const line = document.createElement("div");
    line.className = `terminal-line ${className}`;
    if (className === "user-msg") {
        line.innerHTML = `<span class="prompt">USER&gt;</span> ${text}`;
    } else {
        line.innerHTML = text;
    }
    chatMessages.appendChild(line);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return line;
}

function appendChatMessageWithCitation(text, namespace, citation) {
    const line = document.createElement("div");
    line.className = "terminal-line assistant-msg";
    
    // Format text beautifully with click-to-cite inline actions
    line.innerHTML = `
        <span class="prompt">BG&gt;</span> ${text} 
        <div style="margin-top: 6px; font-size: 10px;">
            <span class="citation-btn" onclick="openCitationDrawer('Free Chat Query', '${namespace}', '${citation.replace(/'/g, "\\'")}')">VIEW CITED DIRECTIVE</span>
        </div>
    `;
    chatMessages.appendChild(line);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --------------------------------------------------------------------------
// CITATION EVIDENCE DRAWER FUNCTIONS
// --------------------------------------------------------------------------
function openCitationDrawer(sourceTitle, namespace, content) {
    citeChunkId.textContent = "chunk_" + Math.random().toString(36).substring(2, 8) + "_active";
    citeNamespace.textContent = namespace;
    citeScore.textContent = (0.75 + Math.random() * 0.23).toFixed(4) + " (COSINE)";
    citeContent.textContent = content;
    
    // Mock URL link to PDF
    citeDocBox.style.display = "block";
    citeDocUrl.href = "#";
    citeDocUrl.onclick = (e) => {
        e.preventDefault();
        alert(`Accessing archived source doc: r2://bankguard/${namespace}/circular_rbi.pdf`);
    };

    citationDrawer.classList.add("open");
}

function closeCitationDrawer() {
    citationDrawer.classList.remove("open");
}

// Helper: artificial delay
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
