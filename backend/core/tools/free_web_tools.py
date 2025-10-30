"""
Free Web Search and Scraping Tools

These tools provide web search and scraping without requiring paid API keys.
They use free services and direct HTTP requests.
"""

import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
from core.agentpress.tool import Tool, ToolResult, openapi_schema, tool_metadata
from core.sandbox.tool_base import SandboxToolsBase
from core.agentpress.thread_manager import ThreadManager
from core.utils.logger import logger
import json
from urllib.parse import quote_plus, urljoin
import re


@tool_metadata(
    display_name="Free Web Search",
    description="Search the web for free using DuckDuckGo (no API key required)",
    icon="Search",
    color="bg-blue-100 dark:bg-blue-800/50",
    weight=25,
    visible=True
)
class FreeWebSearchTool(SandboxToolsBase):
    """Free web search using DuckDuckGo HTML scraping (no API key needed)."""

    def __init__(self, project_id: str, thread_manager: ThreadManager):
        super().__init__(project_id, thread_manager)

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "free_web_search",
            "description": "Search the web for free using DuckDuckGo. Returns search results with titles, URLs, and snippets. No API key required. Use this for general web searches when you don't have paid API access.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query. Be specific and include key terms for better results."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-20). Default is 10.",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def free_web_search(
        self, 
        query: str,
        max_results: int = 10
    ) -> ToolResult:
        """
        Search the web using DuckDuckGo (free, no API key needed).
        """
        try:
            if not query or not isinstance(query, str):
                return self.fail_response("A valid search query is required.")
            
            # Normalize max_results
            max_results = max(1, min(int(max_results), 20))
            
            logger.info(f"Executing free web search for: '{query}' (max {max_results} results)")
            
            # Use DuckDuckGo HTML interface
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            
            # Parse HTML results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            result_divs = soup.find_all('div', class_='result')[:max_results]
            
            for div in result_divs:
                try:
                    # Extract title and URL
                    title_link = div.find('a', class_='result__a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Extract snippet
                    snippet_elem = div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                except Exception as e:
                    logger.debug(f"Error parsing result: {e}")
                    continue
            
            if not results:
                return self.fail_response(f"No results found for query: {query}")
            
            # Format response
            response_text = f"Found {len(results)} search results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                response_text += f"{i}. **{result['title']}**\n"
                response_text += f"   URL: {result['url']}\n"
                if result['snippet']:
                    response_text += f"   {result['snippet']}\n"
                response_text += "\n"
            
            return self.success_response(
                response_text,
                metadata={
                    "query": query,
                    "results_count": len(results),
                    "results": results
                }
            )
            
        except Exception as e:
            logger.error(f"Free web search failed: {e}")
            return self.fail_response(f"Search failed: {str(e)}")


@tool_metadata(
    display_name="Free Web Scraper",
    description="Scrape and extract content from any webpage for free (no API key required)",
    icon="FileText",
    color="bg-purple-100 dark:bg-purple-800/50",
    weight=26,
    visible=True
)
class FreeWebScraperTool(SandboxToolsBase):
    """Free web scraping using direct HTTP requests and BeautifulSoup (no API key needed)."""

    def __init__(self, project_id: str, thread_manager: ThreadManager):
        super().__init__(project_id, thread_manager)

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "free_scrape_webpage",
            "description": "Scrape and extract content from any webpage for free. Returns the page title, text content, and links. No API key required. Use this to read the full content of web pages after searching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The complete URL of the webpage to scrape (must start with http:// or https://)."
                    },
                    "extract_links": {
                        "type": "boolean",
                        "description": "Whether to extract all links from the page. Default is false.",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        }
    })
    async def free_scrape_webpage(
        self, 
        url: str,
        extract_links: bool = False
    ) -> ToolResult:
        """
        Scrape a webpage and extract its content (free, no API key needed).
        """
        try:
            if not url or not isinstance(url, str):
                return self.fail_response("A valid URL is required.")
            
            if not url.startswith(('http://', 'https://')):
                return self.fail_response("URL must start with http:// or https://")
            
            logger.info(f"Scraping webpage: {url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else "No title"
            
            # Extract main content
            # Try to find main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main', re.I)) or soup.body
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Limit text length
            max_chars = 8000
            if len(text) > max_chars:
                text = text[:max_chars] + f"\n\n[Content truncated - {len(text)} total characters]"
            
            response_text = f"**Page Title:** {title}\n\n"
            response_text += f"**URL:** {url}\n\n"
            response_text += f"**Content:**\n{text}\n"
            
            metadata = {
                "url": url,
                "title": title,
                "content_length": len(text),
                "full_length": len(response.text)
            }
            
            # Extract links if requested
            if extract_links:
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    link_text = link.get_text(strip=True)
                    if absolute_url.startswith(('http://', 'https://')):
                        links.append({
                            "url": absolute_url,
                            "text": link_text or "No text"
                        })
                
                # Limit links
                links = links[:50]
                metadata["links"] = links
                
                if links:
                    response_text += f"\n**Links found ({len(links)}):**\n"
                    for i, link in enumerate(links[:20], 1):  # Show first 20
                        response_text += f"{i}. [{link['text']}]({link['url']})\n"
                    if len(links) > 20:
                        response_text += f"\n[{len(links) - 20} more links available in metadata]\n"
            
            return self.success_response(
                response_text,
                metadata=metadata
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping {url}: {e}")
            return self.fail_response(f"Failed to fetch page (HTTP {e.response.status_code}): {str(e)}")
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return self.fail_response(f"Scraping failed: {str(e)}")
