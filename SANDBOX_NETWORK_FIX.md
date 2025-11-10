# Sandbox Network Access Issue

## Problem
Web search tools are failing because the Daytona sandbox environment does not have internet access.

## Diagnosis
I've added network connectivity tests to the local web search tool that will confirm this. Run a web search and check the logs with:

```bash
docker compose logs -f backend | grep -i "network"
```

You should see something like:
```
Network test result: exit_code=1, output=<urlopen error [Errno ...] No route to host>
```

## Root Cause
Daytona sandboxes run in isolated containers that may not have outbound internet access by default. This is typically a security/network configuration issue.

## Solutions

### Option 1: Configure Daytona Sandbox Network Access (Recommended)
Contact your Daytona administrator or check the Daytona documentation to enable outbound internet access for sandboxes. The sandbox needs to be able to make outbound HTTP/HTTPS requests to:
- pypi.org (for pip package installation)
- duckduckgo.com (for free web search)
- tavily.com (for paid web search API)
- firecrawl.dev (for paid web scraping API)
- Any other websites that agents need to access

### Option 2: Use Host Network APIs (Workaround)
Instead of running web searches inside the sandbox, you could:

1. **For Free Search**: Modify `local_web_search_tool.py` to run DuckDuckGo search directly in the backend (not in sandbox)
2. **For Paid Search**: The paid tools (Tavily, Firecrawl) already run on the backend and should work if you have API keys

### Option 3: Check Daytona Target Configuration
Verify your Daytona target is configured with network access:
- Check `DAYTONA_TARGET` in your `.env` file
- Ensure the Daytona target/cluster has internet connectivity enabled
- Check if there are firewall rules blocking outbound traffic

## Testing Network Access

Try this command to test sandbox network access:
```bash
# In your backend logs
docker compose logs -f backend
```

Then trigger a web search. Look for log lines:
- `Sandbox test result:` - Should show exit_code=0 and "SANDBOX_OK"
- `Network test result:` - Should show exit_code=0 and "200" if network is working

## Quick Fix for Testing
If you just want to test the paid search tools:
1. Make sure you have `TAVILY_API_KEY` and `FIRECRAWL_API_KEY` in your `.env`
2. Toggle the agent to use "Paid" web search instead of "Local/Free"
3. The paid tools run on the backend (not in sandbox) so they should work

The paid tools will work even without sandbox network access since they make API calls directly from the backend.
