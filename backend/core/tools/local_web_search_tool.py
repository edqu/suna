"""
Local Web Search Tool - FREE alternative to Tavily + Firecrawl

Uses free services for web search and scraping:
- DuckDuckGo for search (no API key required)
- BeautifulSoup + requests for web scraping (no API key required)
- Readability for content extraction
"""

from core.agentpress.tool import Tool, ToolResult, openapi_schema, tool_metadata, method_metadata
from core.agentpress.thread_manager import ThreadManager
from core.sandbox.tool_base import SandboxToolsBase
from core.utils.logger import logger
from typing import List, Dict, Any, Optional
import json
import asyncio

@tool_metadata(
    display_name="Web Search (Local)",
    description="Free web search and scraping using DuckDuckGo and BeautifulSoup - no API keys required",
    icon="Search",
    color="bg-emerald-100 dark:bg-emerald-800/50",
    weight=55,
    visible=True,
    is_core=False
)
class LocalWebSearchTool(SandboxToolsBase):
    """
    Local Web Search Tool - completely free alternative to Tavily + Firecrawl.
    
    Features:
    - Web search using DuckDuckGo (no API key)
    - Web scraping using BeautifulSoup (no API key)
    - Content extraction using Readability
    - All processing done locally/in sandbox
    """

    def __init__(self, project_id: str, thread_manager: ThreadManager):
        super().__init__(project_id, thread_manager)
        self.max_results = 10
        self.timeout = 30

    @method_metadata(
        display_name="Search Web (Free)",
        description="Search the web using DuckDuckGo - completely free, no API key required",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "search_web_free",
            "description": "Search the web using DuckDuckGo. Returns search results with titles, URLs, and snippets. Completely free with no API key required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute. Use specific keywords for better results."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default: 5, max: 10)",
                        "default": 5
                    },
                    "region": {
                        "type": "string",
                        "description": "Region code for localized results (e.g., 'us-en', 'uk-en', 'de-de'). Default: 'wt-wt' (worldwide)",
                        "default": "wt-wt"
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def search_web_free(self, query: str, max_results: int = 5, region: str = "wt-wt") -> ToolResult:
        """
        Search the web using DuckDuckGo - completely free.
        
        Args:
            query: Search query
            max_results: Number of results to return (max 10)
            region: Region code for results
            
        Returns:
            ToolResult with search results
        """
        try:
            max_results = min(max_results, 10)  # Cap at 10
            
            await self._ensure_sandbox()
            
            # Install required packages in sandbox if not present
            install_cmd = "pip install -q duckduckgo-search beautifulsoup4 lxml 2>&1 | grep -v 'already satisfied' || true"
            await self.sandbox.process.exec(install_cmd, timeout=60)
            
            # Escape single quotes in query for use in Python string
            escaped_query = query.replace("'", "\\'")
            
            # Create Python script to perform search
            search_script = f"""
import json
from duckduckgo_search import DDGS

try:
    with DDGS() as ddgs:
        results = list(ddgs.text(
            '{escaped_query}',
            region='{region}',
            max_results={max_results}
        ))
        print(json.dumps(results))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
            
            # Write script to file
            script_path = "/tmp/search_script.py"
            write_cmd = f"cat > {script_path} << 'EOFSCRIPT'\n{search_script}\nEOFSCRIPT"
            await self.sandbox.process.exec(write_cmd, timeout=10)
            
            # Execute search
            logger.info(f"Searching DuckDuckGo for: '{query}' (max_results={max_results})")
            response = await self.sandbox.process.exec(f"python {script_path}", timeout=self.timeout)
            
            if response.exit_code != 0:
                error_msg = f"Search failed: {response.result}"
                logger.error(error_msg)
                return self.fail_response(error_msg)
            
            # Parse results
            try:
                results = json.loads(response.result)
                
                if "error" in results:
                    return self.fail_response(f"DuckDuckGo search error: {results['error']}")
                
                # Format results
                formatted_results = []
                for idx, result in enumerate(results, 1):
                    formatted_results.append({
                        "title": result.get("title", "No title"),
                        "url": result.get("href", result.get("link", "")),
                        "snippet": result.get("body", result.get("description", "")),
                        "position": idx
                    })
                
                result_text = f"Found {len(formatted_results)} results for '{query}':\n\n"
                for r in formatted_results:
                    result_text += f"{r['position']}. **{r['title']}**\n"
                    result_text += f"   URL: {r['url']}\n"
                    result_text += f"   {r['snippet'][:200]}...\n\n"
                
                logger.info(f"Search completed: {len(formatted_results)} results found")
                
                return ToolResult(
                    output=result_text,
                    data={
                        "query": query,
                        "results": formatted_results,
                        "count": len(formatted_results),
                        "source": "duckduckgo"
                    },
                    success=True
                )
                
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse search results: {str(e)}"
                logger.error(error_msg)
                return self.fail_response(error_msg)
                
        except Exception as e:
            error_msg = f"Web search error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.fail_response(error_msg)

    @method_metadata(
        display_name="Scrape Web Page (Free)",
        description="Scrape and extract clean content from any web page - completely free",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "scrape_webpage_free",
            "description": "Scrape content from a URL and extract clean, readable text. Uses BeautifulSoup and Readability for content extraction. Completely free with no API key required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to scrape. Must be a valid HTTP/HTTPS URL."
                    },
                    "extract_markdown": {
                        "type": "boolean",
                        "description": "Whether to convert content to markdown format for better readability. Default: true",
                        "default": True
                    },
                    "include_links": {
                        "type": "boolean",
                        "description": "Whether to include links from the page. Default: true",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    })
    async def scrape_webpage_free(self, url: str, extract_markdown: bool = True, include_links: bool = True) -> ToolResult:
        """
        Scrape content from a webpage - completely free.
        
        Args:
            url: URL to scrape
            extract_markdown: Convert to markdown
            include_links: Include links in output
            
        Returns:
            ToolResult with scraped content
        """
        try:
            await self._ensure_sandbox()
            
            # Install required packages
            install_cmd = "pip install -q beautifulsoup4 lxml readability-lxml html2text requests 2>&1 | grep -v 'already satisfied' || true"
            await self.sandbox.process.exec(install_cmd, timeout=60)
            
            # Create Python script to scrape
            scrape_script = f"""
import json
import requests
from bs4 import BeautifulSoup
from readability import Document
import html2text

try:
    # Fetch the page
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }}
    response = requests.get('{url}', headers=headers, timeout=30)
    response.raise_for_status()
    
    # Extract main content using Readability
    doc = Document(response.text)
    title = doc.title()
    content_html = doc.summary()
    
    # Parse with BeautifulSoup for cleaning
    soup = BeautifulSoup(content_html, 'lxml')
    
    # Extract text
    text_content = soup.get_text(separator='\\\\n', strip=True)
    
    # Extract links if requested
    links = []
    if {str(include_links).lower()}:
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            link_href = link['href']
            if link_text and link_href:
                # Make relative URLs absolute
                if link_href.startswith('/'):
                    from urllib.parse import urljoin
                    link_href = urljoin('{url}', link_href)
                links.append({{'text': link_text, 'url': link_href}})
    
    # Convert to markdown if requested
    markdown_content = ""
    if {str(extract_markdown).lower()}:
        h = html2text.HTML2Text()
        h.ignore_links = not {str(include_links).lower()}
        h.ignore_images = True
        markdown_content = h.handle(content_html)
    
    result = {{
        'title': title,
        'url': '{url}',
        'text_content': text_content[:50000],  # Limit to 50K chars
        'markdown_content': markdown_content[:50000] if markdown_content else "",
        'links': links[:50],  # Limit to 50 links
        'success': True
    }}
    
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({{'error': str(e), 'success': False}}))
"""
            
            # Write and execute script
            script_path = "/tmp/scrape_script.py"
            write_cmd = f"cat > {script_path} << 'EOFSCRIPT'\n{scrape_script}\nEOFSCRIPT"
            await self.sandbox.process.exec(write_cmd, timeout=10)
            
            logger.info(f"Scraping URL: {url}")
            response = await self.sandbox.process.exec(f"python {script_path}", timeout=45)
            
            if response.exit_code != 0:
                error_msg = f"Scraping failed: {response.result}"
                logger.error(error_msg)
                return self.fail_response(error_msg)
            
            # Parse results
            try:
                result = json.loads(response.result)
                
                if not result.get("success"):
                    return self.fail_response(f"Scraping error: {result.get('error', 'Unknown error')}")
                
                # Format output
                content = f"# {result['title']}\n\n"
                content += f"**URL**: {result['url']}\n\n"
                
                if extract_markdown and result.get('markdown_content'):
                    content += "## Content (Markdown)\n\n"
                    content += result['markdown_content']
                else:
                    content += "## Content (Text)\n\n"
                    content += result['text_content']
                
                if include_links and result.get('links'):
                    content += f"\n\n## Links Found ({len(result['links'])})\n\n"
                    for link in result['links'][:20]:  # Show first 20
                        content += f"- [{link['text']}]({link['url']})\n"
                
                logger.info(f"Successfully scraped {url}: {len(result.get('text_content', ''))} chars")
                
                return ToolResult(
                    output=content,
                    data={
                        "title": result['title'],
                        "url": url,
                        "text_length": len(result.get('text_content', '')),
                        "links_found": len(result.get('links', [])),
                        "source": "local_scraper"
                    },
                    success=True
                )
                
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse scraping results: {str(e)}"
                logger.error(error_msg)
                return self.fail_response(error_msg)
                
        except Exception as e:
            error_msg = f"Web scraping error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.fail_response(error_msg)

    @method_metadata(
        display_name="Search & Scrape (Free)",
        description="Search and scrape multiple pages in one call - completely free",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "search_and_scrape_free",
            "description": "Search the web and automatically scrape the top results. Combines search and scraping in one call. Completely free with no API key required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute"
                    },
                    "num_results_to_scrape": {
                        "type": "integer",
                        "description": "Number of top results to scrape (default: 3, max: 5)",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def search_and_scrape_free(self, query: str, num_results_to_scrape: int = 3) -> ToolResult:
        """
        Search and scrape top results - completely free.
        
        Args:
            query: Search query
            num_results_to_scrape: How many top results to scrape
            
        Returns:
            ToolResult with search results and scraped content
        """
        try:
            # Cap scraping to avoid excessive load
            num_results_to_scrape = min(num_results_to_scrape, 5)
            
            # First, perform search
            logger.info(f"Search and scrape: '{query}' (will scrape top {num_results_to_scrape})")
            search_result = await self.search_web_free(query, max_results=num_results_to_scrape)
            
            if not search_result.success:
                return search_result
            
            # Extract URLs from search results
            search_data = search_result.data
            if not search_data or "results" not in search_data:
                return self.fail_response("No search results to scrape")
            
            urls_to_scrape = [r["url"] for r in search_data["results"][:num_results_to_scrape]]
            
            # Scrape each URL
            scraped_pages = []
            for idx, url in enumerate(urls_to_scrape, 1):
                logger.info(f"Scraping {idx}/{len(urls_to_scrape)}: {url}")
                scrape_result = await self.scrape_webpage_free(url, extract_markdown=True, include_links=False)
                
                if scrape_result.success:
                    scraped_pages.append({
                        "url": url,
                        "title": scrape_result.data.get("title", "No title"),
                        "content": scrape_result.output,
                        "length": scrape_result.data.get("text_length", 0)
                    })
                else:
                    logger.warning(f"Failed to scrape {url}: {scrape_result.output}")
                    scraped_pages.append({
                        "url": url,
                        "title": "Scraping failed",
                        "content": f"Error: {scrape_result.output}",
                        "length": 0
                    })
                
                # Small delay between requests to be respectful
                if idx < len(urls_to_scrape):
                    await asyncio.sleep(1)
            
            # Format combined output
            output = f"# Search Results for '{query}'\n\n"
            output += f"Found and scraped {len(scraped_pages)} pages:\n\n"
            output += "---\n\n"
            
            for page in scraped_pages:
                output += page['content']
                output += "\n\n---\n\n"
            
            logger.info(f"Search and scrape completed: {len(scraped_pages)} pages processed")
            
            return ToolResult(
                output=output,
                data={
                    "query": query,
                    "pages_scraped": len(scraped_pages),
                    "pages": scraped_pages,
                    "source": "local_search_and_scrape"
                },
                success=True
            )
            
        except Exception as e:
            error_msg = f"Search and scrape error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.fail_response(error_msg)
