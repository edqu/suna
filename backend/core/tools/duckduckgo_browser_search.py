"""
DuckDuckGo Browser Search Tool

This tool uses the browser automation to navigate to DuckDuckGo.com 
and perform searches using the actual DuckDuckGo search interface.

This is different from the API-based search - it actually opens a browser,
goes to duckduckgo.com, types in the search, and extracts results.

Useful when you want visual confirmation of searches or when API limits are hit.
"""

from core.agentpress.tool import Tool, ToolResult, openapi_schema, tool_metadata, method_metadata
from core.agentpress.thread_manager import ThreadManager
from core.tools.browser_tool import BrowserTool
from core.utils.logger import logger
from typing import Optional, List, Dict, Any


@tool_metadata(
    display_name="DuckDuckGo Browser Search",
    description="Search using actual DuckDuckGo website through browser automation",
    icon="Search",
    color="bg-orange-100 dark:bg-orange-800/50",
    weight=58,
    visible=True,
    is_core=False
)
class DuckDuckGoBrowserSearch(Tool):
    """
    Performs web searches by navigating to DuckDuckGo.com in a real browser.
    
    This is a browser-based alternative to the API search, useful when:
    - You want to see the actual search results page
    - API search is rate-limited or unavailable
    - You need to interact with search filters/options
    - You want visual confirmation of results
    """

    def __init__(self, project_id: str, thread_id: str, thread_manager: ThreadManager):
        super().__init__()
        self.project_id = project_id
        self.thread_id = thread_id
        self.thread_manager = thread_manager
        # Create browser tool instance for automation
        self.browser_tool = BrowserTool(
            project_id=project_id,
            thread_id=thread_id,
            thread_manager=thread_manager
        )

    @method_metadata(
        display_name="Search via DuckDuckGo Browser",
        description="Search the web by navigating to DuckDuckGo.com and using the actual search interface",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "search_duckduckgo_browser",
            "description": "Search the web by navigating to DuckDuckGo.com in a browser and extracting results. Returns search results with titles, URLs, and snippets. Uses actual browser navigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute on DuckDuckGo"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to extract (default: 5, max: 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def search_duckduckgo_browser(self, query: str, max_results: int = 5) -> ToolResult:
        """
        Search using DuckDuckGo website via browser automation.
        
        Args:
            query: Search query
            max_results: Number of results to extract (max 10)
            
        Returns:
            ToolResult with search results and screenshot
        """
        try:
            max_results = min(max_results, 10)
            
            logger.info(f"🔍 Searching DuckDuckGo via browser for: '{query}' (max_results={max_results})")
            
            # Step 1: Navigate to DuckDuckGo
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            logger.debug(f"Navigating to: {search_url}")
            
            nav_result = await self.browser_tool.browser_navigate_to(search_url)
            
            if not nav_result.success:
                return self.fail_response(f"Failed to navigate to DuckDuckGo: {nav_result.message}")
            
            # Step 2: Wait for results to load and extract them
            logger.debug("Extracting search results from page")
            
            extract_instruction = f"""
            Extract the top {max_results} search results from this DuckDuckGo search page.
            
            For each result, get:
            - Title (the main link text)
            - URL (the destination link)
            - Snippet (the description text below the title)
            
            Return as a structured list of search results.
            Ignore ads and sponsored results.
            """
            
            extract_result = await self.browser_tool.browser_extract_content(extract_instruction)
            
            if not extract_result.success:
                return self.fail_response(f"Failed to extract search results: {extract_result.message}")
            
            # Format the results
            results_data = {
                "query": query,
                "search_url": search_url,
                "results": extract_result.data.get('data', []) if hasattr(extract_result.data, 'get') else extract_result.data,
                "screenshot_url": nav_result.data.get('image_url') if hasattr(nav_result.data, 'get') else None,
                "search_method": "browser_based",
                "search_engine": "DuckDuckGo"
            }
            
            logger.info(f"✅ Browser-based DuckDuckGo search completed")
            
            return self.success_response(
                message=f"Found search results for '{query}'",
                data=results_data
            )
            
        except Exception as e:
            logger.error(f"Error in DuckDuckGo browser search: {e}")
            return self.fail_response(f"DuckDuckGo browser search failed: {str(e)}")

    @method_metadata(
        display_name="Search and Click Result",
        description="Search DuckDuckGo and click on a specific result to read full content",
        is_core=False,
        visible=True
    )
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "search_and_open_result",
            "description": "Search DuckDuckGo via browser, then click on and extract content from a specific result number",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "result_number": {
                        "type": "integer",
                        "description": "Which result to click on (1 = first result, 2 = second, etc.)",
                        "default": 1
                    }
                },
                "required": ["query"]
            }
        }
    })
    async def search_and_open_result(self, query: str, result_number: int = 1) -> ToolResult:
        """
        Search DuckDuckGo and click on a specific result.
        
        Args:
            query: Search query
            result_number: Which result to open (1-10)
            
        Returns:
            ToolResult with full page content from the clicked result
        """
        try:
            logger.info(f"🔍 Searching DuckDuckGo and opening result #{result_number} for: '{query}'")
            
            # Step 1: Navigate to DuckDuckGo search
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            
            nav_result = await self.browser_tool.browser_navigate_to(search_url)
            if not nav_result.success:
                return self.fail_response(f"Failed to navigate: {nav_result.message}")
            
            # Step 2: Click on the specified result
            result_number = max(1, min(result_number, 10))  # Clamp between 1-10
            
            click_instruction = f"Click on the {self._number_to_ordinal(result_number)} search result link (not an ad)"
            
            click_result = await self.browser_tool.browser_act(click_instruction)
            if not click_result.success:
                return self.fail_response(f"Failed to click result: {click_result.message}")
            
            # Step 3: Extract content from the opened page
            extract_instruction = "Extract the main content from this page including the title, main text, and any important information"
            
            content_result = await self.browser_tool.browser_extract_content(extract_instruction)
            if not content_result.success:
                return self.fail_response(f"Failed to extract content: {content_result.message}")
            
            results_data = {
                "query": query,
                "result_number": result_number,
                "content": content_result.data,
                "screenshot_url": content_result.data.get('image_url') if hasattr(content_result.data, 'get') else None,
                "search_method": "browser_interactive"
            }
            
            logger.info(f"✅ Searched and opened result #{result_number}")
            
            return self.success_response(
                message=f"Opened result #{result_number} for query '{query}'",
                data=results_data
            )
            
        except Exception as e:
            logger.error(f"Error in search and open: {e}")
            return self.fail_response(f"Failed to search and open result: {str(e)}")
    
    @staticmethod
    def _number_to_ordinal(n: int) -> str:
        """Convert number to ordinal string (1 -> 'first', 2 -> 'second', etc.)"""
        ordinals = {
            1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"
        }
        return ordinals.get(n, f"{n}th")
