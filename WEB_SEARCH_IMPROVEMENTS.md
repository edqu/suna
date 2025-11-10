# Web Search Tools - Recommended Improvements

Based on Oracle analysis of the web search toggle and tools implementation.

## Critical Issues (Fix Immediately)

### 1. Tool Registration Mismatch ⚠️ CRITICAL
**Problem**: Toggle writes to `agentpress_tools` flags, but `run.py` reads from `agent_config.web_search_preference`

**Location**: `backend/core/run.py` lines 113-165

**Fix**: Derive preference from agentpress_tools flags:
```python
# backend/core/run.py line ~113
web_search_preference = "local"
agentpress_tools = (self.agent_config or {}).get('agentpress_tools', {})

if agentpress_tools.get('web_search_tool', False):
    web_search_preference = "paid"
elif agentpress_tools.get('local_web_search_tool', False):
    web_search_preference = "local"
elif self.agent_config and self.agent_config.get('web_search_preference'):
    # Fallback for backward compatibility
    web_search_preference = self.agent_config['web_search_preference']
```

### 2. Logger Import Error in Paid Tool
**Problem**: `web_search_tool.py` uses `logger` without importing it (lines 36-38)

**Location**: `backend/core/tools/web_search_tool.py`

**Fix**:
```python
from core.utils.logger import logger
# Then use logger.warning() consistently instead of logging.info()
```

### 3. API Key Validation Missing
**Problem**: Users can toggle to "paid" mode without API keys, causing silent failures

**Location**: `backend/core/agent_crud.py` line ~450

**Fix**:
```python
if preference == "paid" and not (config.TAVILY_API_KEY or config.FIRECRAWL_API_KEY):
    raise HTTPException(
        status_code=400, 
        detail="Paid web search requires TAVILY_API_KEY or FIRECRAWL_API_KEY. Configure keys in settings."
    )
```

## High-Impact Improvements

### 4. SSRF Protection for Local Scraper 🔒 SECURITY
**Problem**: Local scraper can be tricked into accessing internal services

**Location**: `backend/core/tools/local_web_search_tool.py` scrape_webpage method

**Fix**: Add URL validation:
```python
from urllib.parse import urlparse
import ipaddress
import socket

def _is_safe_public_url(url: str) -> bool:
    """Validate URL is public HTTP/HTTPS and not accessing private IPs."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        host = parsed.hostname
        if not host:
            return False
            
        # Block localhost variations
        if host.lower() in ('localhost', '127.0.0.1', '::1'):
            return False
        
        # Resolve and check IP addresses
        infos = socket.getaddrinfo(host, None)
        for family, _, _, _, sockaddr in infos:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                return False
            # Block AWS metadata endpoint
            if str(ip) == '169.254.169.254':
                return False
        
        return True
    except Exception:
        return False

# In scrape_webpage, before requests.get:
if not _is_safe_public_url(url):
    return self.fail_response(f"URL is not allowed: {url}")
```

### 5. Make Blocking Calls Async-Safe ⚡ PERFORMANCE
**Problem**: `DDGS().text()` and `requests.get()` block the event loop

**Location**: Both in `local_web_search_tool.py`

**Fix**:
```python
# In web_search method:
def _do_search():
    with DDGS() as ddgs:
        return list(ddgs.text(query, region=region, max_results=max_results, 
                             safesearch="moderate", backend=backend))

results = await asyncio.to_thread(_do_search)

# In scrape_webpage method:
response = await asyncio.to_thread(
    requests.get, url, headers=headers, timeout=15, allow_redirects=False
)
```

### 6. Parallel Scraping in search_and_scrape_free
**Problem**: Scrapes URLs sequentially with 1s delay each (slow)

**Location**: `local_web_search_tool.py` line 487-509

**Fix**:
```python
# Replace sequential scraping with bounded concurrency
semaphore = asyncio.Semaphore(2)  # Max 2 concurrent scrapes

async def scrape_with_limit(url):
    async with semaphore:
        return await self.scrape_webpage(url, extract_markdown=True, include_links=False)

scrape_tasks = [scrape_with_limit(url) for url in urls_to_scrape]
scrape_results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

# Process results
for idx, (url, scrape_result) in enumerate(zip(urls_to_scrape, scrape_results), 1):
    # Handle result or exception
```

## Medium-Priority Improvements

### 7. Result Format Consistency
**Problem**: Local and paid tools return different data structures

**Fix**: Normalize both to return:
```python
data={
    "query": query,
    "results": [{"title": ..., "url": ..., "snippet": ..., "position": ...}],
    "count": len(results),
    "source": "duckduckgo" | "tavily"
}
```

### 8. Better Error Messages
**Improvements**:
- Include which backend(s) were tried when all fail
- Suggest alternative queries for zero results
- Translate technical errors to user-friendly messages
- Log detailed errors but return simplified messages to users

### 9. Configuration & Limits
**Add to environment config**:
```env
# Web search settings
WEB_SEARCH_TIMEOUT=30
WEB_SEARCH_MAX_RESULTS=10
WEB_SCRAPE_TIMEOUT=15
WEB_SCRAPE_MAX_SIZE_MB=10
WEB_SCRAPE_MAX_CONCURRENCY=2
```

### 10. Frontend UX Enhancements
**Improvements**:
- Show which tool is currently active in the UI
- Display API key status (configured/not configured) for paid mode
- Add a "test search" button to verify the tool works
- Show cost estimate when switching to paid mode
- Indicate when backend needs restart for changes to take effect

## Testing Priorities

### Critical Tests
1. **Toggle API with/without API keys**
2. **SSRF protection** - reject localhost, private IPs, metadata endpoint
3. **Tool registration** - verify correct tool loaded based on flags
4. **Zero results handling**
5. **Network timeout handling**

### Integration Tests
1. End-to-end toggle: local → paid → local
2. Search with real query returns results
3. Scrape public page successfully
4. search_and_scrape_free completes successfully

## Documentation Needs

1. **User Guide**:
   - How to configure API keys for paid mode
   - Cost comparison table
   - When to use local vs paid
   - Known limitations (no JS execution, size limits)

2. **Developer Docs**:
   - Architecture diagram showing toggle flow
   - Data flow from toggle → backend → tool registration
   - How to add new search backends
   - Testing instructions

3. **Deployment Guide**:
   - Required packages for backend
   - Environment variables needed
   - How to verify web search is working

## Quick Wins (Implement First)

Priority order for maximum impact:

1. ✅ **Fix run.py registration logic** (30 min) - Makes toggle actually work
2. ✅ **Add API key validation** (30 min) - Prevents confusing errors  
3. ✅ **Fix logger import** (15 min) - Prevents crashes
4. ✅ **Add SSRF protection** (1 hour) - Critical security issue
5. ✅ **Make calls async-safe** (1 hour) - Performance improvement
6. ✅ **Better error messages** (30 min) - UX improvement

Total effort for critical fixes: ~4 hours

## Implementation Order

1. **Phase 1 - Critical Fixes** (4 hours):
   - Fix tool registration mismatch
   - Add API key validation
   - Fix logger import
   - Add SSRF protection
   - Make blocking calls async

2. **Phase 2 - UX & Performance** (3 hours):
   - Parallel scraping
   - Better error messages
   - Frontend status indicators

3. **Phase 3 - Quality & Testing** (4 hours):
   - Write unit tests
   - Add integration tests
   - Update documentation

## Long-term Considerations

- **Caching layer** for repeated searches/scrapes
- **Rate limiting** per domain
- **robots.txt** compliance
- **Headless browser** option for JS-heavy sites
- **Content extraction** improvements
- **Multi-language** support improvements
