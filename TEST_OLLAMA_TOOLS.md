# Testing Ollama Tool Calling with Qwen

## Quick Start Verification

### Step 1: Restart Backend

Stop and restart your backend to load the Ollama fixes:

```bash
# Stop current backend (Ctrl+C)

# Start backend
python start.py
```

### Step 2: Verify Startup Logs

Look for these success indicators:

```
🔍 Web search preference: local
🔍 Registering LOCAL web search tool (DuckDuckGo + BeautifulSoup)...
✅ Registered LOCAL web search tool (FREE) with all methods
✅ Registered browser_tool with all methods
📋 Available tools: search_web_free, scrape_webpage_free, search_and_scrape_free, browser_navigate_to, browser_act, browser_extract_content, browser_screenshot, ...
```

**If you see:**
- ❌ `NO WEB SEARCH TOOL REGISTERED!` → Check agent config for `web_search_preference`
- ⚠️ `Local web search is disabled` → Enable `local_web_search_tool` in agent config
- Missing browser_tool → Check if `browser_tool` is in disabled_tools list

### Step 3: Select Your Qwen Model

In the Suna UI:
1. Open a new thread
2. Select model: `ollama/qwen2.5-coder` (or any Qwen variant)
3. Look for confirmation logs

**Expected Runtime Logs:**
```
🤖 Model: ollama/qwen2.5-coder (provider: ollama, supports_functions: True)
🔧 Detected Ollama model - forcing XML tool calling for better compatibility
🔧 Universal Tool Adapter: native=False, xml=True (model preference: xml)
🔧 Ollama detected: tool_choice disabled, XML mode enforced
```

## Test Cases

### Test 1: Basic Web Search (Always Works - No API Keys)

**User Message:**
```
Search the web for the latest Qwen model features and summarize the top 3 results.
```

**Expected Behavior:**

1. **Model Response:**
   ```xml
   <function_calls>
   <invoke name="search_web_free">
   <parameter name="query">latest Qwen model features</parameter>
   <parameter name="max_results">5</parameter>
   </invoke>
   </function_calls>
   ```

2. **Backend Logs:**
   ```
   Detected XML tool call in response
   Executing tool: search_web_free
   Tool search_web_free called with: {'query': 'latest Qwen model features', 'max_results': 5}
   DuckDuckGo search completed
   ✅ Tool execution completed successfully
   ```

3. **Tool Result:**
   - List of search results with titles, URLs, and snippets
   - Model receives results and summarizes

4. **Final Response:**
   - Model summarizes the 3 most relevant results
   - Includes key features mentioned

**If It Fails:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| No tool call detected | Model not instructed to use tools | Add "Use the search_web_free tool to..." |
| Tool not found error | LocalWebSearchTool not registered | Check startup logs, restart backend |
| DuckDuckGo error | Internet connectivity issue | Check network, try again |
| XML not parsed | Response processor issue | Check logs for XML parsing errors |

---

### Test 2: Web Scraping (Always Works - No API Keys)

**User Message:**
```
Scrape https://github.com/QwenLM/Qwen and tell me what the repository description says.
```

**Expected Behavior:**

1. **Model Response:**
   ```xml
   <function_calls>
   <invoke name="scrape_webpage_free">
   <parameter name="url">https://github.com/QwenLM/Qwen</parameter>
   <parameter name="extract_markdown">true</parameter>
   </invoke>
   </function_calls>
   ```

2. **Backend Logs:**
   ```
   Executing tool: scrape_webpage_free
   Fetching URL: https://github.com/QwenLM/Qwen
   Using BeautifulSoup + Readability for content extraction
   Successfully extracted 2543 characters
   Converted to markdown
   ✅ Tool execution completed
   ```

3. **Tool Result:**
   - Clean markdown content from the page
   - Main description extracted
   - Links preserved

4. **Final Response:**
   - Model reads the description
   - Provides summary

**If It Fails:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 Forbidden | GitHub blocking scraper | Try a different URL first |
| Timeout | Slow website | Increase timeout in config |
| Empty content | JavaScript-heavy site | Use browser_tool instead |
| SSRF protection error | Private IP/localhost in URL | Only scrape public URLs |

---

### Test 3: Combined Search + Scrape (Always Works)

**User Message:**
```
Search for "Qwen2.5 coder benchmarks" and scrape the top result to get detailed information.
```

**Expected Behavior:**

1. **Model Response (First Call):**
   ```xml
   <function_calls>
   <invoke name="search_and_scrape_free">
   <parameter name="query">Qwen2.5 coder benchmarks</parameter>
   <parameter name="num_results_to_scrape">1</parameter>
   </invoke>
   </function_calls>
   ```

2. **Backend Logs:**
   ```
   Executing tool: search_and_scrape_free
   Step 1: Searching DuckDuckGo...
   Found 5 results
   Step 2: Scraping top 1 results...
   Scraping: https://example.com/qwen-benchmarks
   Successfully scraped 1/1 pages
   ✅ Combined search + scrape completed
   ```

3. **Tool Result:**
   - Search results with full content from top result
   - Benchmark data extracted

**Alternative Test (Better Reliability):**

```
Search for Qwen benchmarks, then tell me which result looks most relevant, and I'll ask you to scrape it.
```

This gives the model a chance to see results first before scraping.

---

### Test 4: Browser Navigation (Requires GEMINI_API_KEY)

**Setup Required:**
```env
# In backend/.env
GEMINI_API_KEY=your-gemini-api-key-here
```

Get free Gemini key: https://aistudio.google.com/app/apikey

**User Message:**
```
Navigate to https://github.com/trending and tell me what the top trending repository is today.
```

**Expected Behavior:**

1. **Model Response (Navigation):**
   ```xml
   <function_calls>
   <invoke name="browser_navigate_to">
   <parameter name="url">https://github.com/trending</parameter>
   </invoke>
   </function_calls>
   ```

2. **Backend Logs:**
   ```
   Executing tool: browser_navigate_to
   Checking Stagehand API health...
   Stagehand API is healthy
   Navigating to: https://github.com/trending
   Navigation successful
   ```

3. **Model Response (Extract Content):**
   ```xml
   <function_calls>
   <invoke name="browser_extract_content">
   <parameter name="instruction">Extract the name and description of the top trending repository</parameter>
   </invoke>
   </function_calls>
   ```

4. **Backend Logs:**
   ```
   Executing tool: browser_extract_content
   Extracting content with instruction: "Extract the name..."
   Using Gemini vision model for extraction
   Content extracted successfully
   ```

5. **Final Response:**
   - Repository name
   - Description
   - Stars/language info

**If It Fails:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| GEMINI_API_KEY not configured | Missing API key | Add to .env and restart |
| Stagehand API not healthy | Sandbox not started | Check sandbox status |
| Navigation timeout | Slow page load | Increase timeout |
| Extraction failed | Unclear instruction | Be more specific |

---

### Test 5: Browser Interaction (Advanced)

**User Message:**
```
Go to https://example.com, find the "More information" link, and click it.
```

**Expected Behavior:**

1. **Navigate:**
   ```xml
   <invoke name="browser_navigate_to">
   <parameter name="url">https://example.com</parameter>
   </invoke>
   ```

2. **Interact:**
   ```xml
   <invoke name="browser_act">
   <parameter name="instruction">Click on the "More information" link</parameter>
   </invoke>
   ```

3. **Extract:**
   ```xml
   <invoke name="browser_extract_content">
   <parameter name="instruction">Get the main heading and first paragraph</parameter>
   </invoke>
   ```

---

## Debugging Guide

### Check Tool Registration

**At Startup:**
```bash
# Look for in logs:
grep "Registered.*tool" backend.log

# Should show:
✅ Registered LOCAL web search tool
✅ Registered browser_tool with all methods
```

**At Runtime:**
```bash
# Look for:
grep "Available tools" backend.log

# Should include:
search_web_free
scrape_webpage_free
search_and_scrape_free
browser_navigate_to
browser_act
browser_extract_content
browser_screenshot
```

### Check Ollama Detection

```bash
# Look for when using Qwen:
grep "Detected Ollama" backend.log

# Should show:
🔧 Detected Ollama model - forcing XML tool calling for better compatibility
🔧 Ollama detected: tool_choice disabled, XML mode enforced
```

### Check Tool Execution

```bash
# Look for:
grep "Executing tool" backend.log

# Should show:
Executing tool: search_web_free with params: {...}
Tool execution completed: ToolResult(success=True, ...)
```

### Check XML Parsing

```bash
# Look for:
grep "XML tool call" backend.log

# Should show:
Detected XML tool call in response: <invoke name="search_web_free">
Parsed XML tool call: search_web_free
```

## Common Issues & Solutions

### Issue: Model Doesn't Use Tools

**Symptoms:**
- Model responds directly without calling tools
- No XML in response

**Causes:**
1. Not instructed explicitly
2. XML schema not in system prompt
3. Model context full

**Solutions:**

**Be More Explicit:**
```
❌ "Find information about X"
✅ "Use the search_web_free tool to find information about X"
✅ "Search the web for information about X" (implies tool use)
```

**Check System Prompt:**
```bash
# Look for in logs:
grep "tool examples" backend.log

# Should show tool schemas and XML examples
```

**Clear Context:**
- Start a new thread
- Keep messages concise

---

### Issue: XML Not Detected

**Symptoms:**
- Backend logs show no "Detected XML tool call"
- Model uses XML but tool doesn't execute

**Debug:**

1. **Check Response Processor:**
   ```bash
   grep "xml_tool_calling" backend.log
   
   # Should show:
   xml_tool_calling=True
   ```

2. **Check XML Format:**
   - Must have `<function_calls>` wrapper
   - Must have `<invoke name="...">`
   - Must have `<parameter name="...">value</parameter>`

3. **Verify Universal Adapter:**
   ```bash
   grep "Universal Tool Adapter" backend.log
   
   # Should show:
   Universal Tool Adapter: native=False, xml=True
   ```

**Solutions:**
- Ensure `xml_tool_calling=True` in ProcessorConfig
- Check `use_xml=True` in run.py
- Verify response processor is using adapter

---

### Issue: Tool Registered But Not Available

**Symptoms:**
- Startup shows tool registered
- Runtime shows "tool not found"

**Debug:**

1. **Check Tool Registry:**
   ```python
   # In thread_manager
   logger.info(f"Tool registry keys: {list(tool_registry.tools.keys())}")
   ```

2. **Check Function Names:**
   - Tool class method name must match exactly
   - Check for typos in XML invoke name

**Solutions:**
- Verify tool name matches exactly (case-sensitive)
- Check tool wasn't disabled mid-session
- Restart backend to refresh registry

---

### Issue: Browser Tool Fails

**Symptoms:**
```
Error: GEMINI_API_KEY is not configured
```

**Solution:**
```bash
# Get free key from:
https://aistudio.google.com/app/apikey

# Add to backend/.env:
GEMINI_API_KEY=AIza...

# Restart backend
python start.py
```

**Alternative (If No Gemini):**
- Use `scrape_webpage_free` instead
- Works for static content
- No API key required

---

## Performance Tips

### For Faster Responses

1. **Use Smaller Models:**
   - `qwen2.5-coder:7b` (faster) vs `qwen2.5-coder:32b` (slower but better)

2. **Use Quantized Models:**
   - Q4 quantization (much faster)
   - Q5 quantization (balanced)
   - Full precision (slowest, best quality)

3. **GPU Acceleration:**
   ```bash
   # Check if GPU is used:
   ollama ps
   
   # Should show GPU memory usage
   ```

4. **Reduce Context:**
   - Start new threads for new tasks
   - Don't include full web page content in context

### For Better Tool Calling

1. **Be Explicit:**
   ```
   Good: "Search the web for X"
   Better: "Use search_web_free to find X"
   Best: "I need current information about X, please search for it"
   ```

2. **One Task at a Time:**
   ```
   ❌ "Search for X, Y, and Z and compare them"
   ✅ "Search for X" (wait) → "Now search for Y" (wait) → etc.
   ```

3. **Clear Instructions:**
   ```
   ❌ "Find stuff about Qwen"
   ✅ "Search for Qwen 2.5 coder release notes"
   ```

## Success Metrics

**You'll know it's working when:**

✅ Startup logs show all tools registered  
✅ Ollama detection message appears  
✅ XML mode enforced message appears  
✅ Model outputs `<function_calls>` blocks  
✅ Tools execute and return results  
✅ Model incorporates results in final response  

**Example Success Flow:**
```
User: "Search for Qwen benchmarks"
  ↓
🔧 Detected Ollama model - forcing XML tool calling
  ↓
Model: "<function_calls><invoke name="search_web_free">..."
  ↓
Executing tool: search_web_free
  ↓
✅ Tool execution completed: 5 results found
  ↓
Model: "Based on the search results, here are the benchmarks..."
  ↓
✅ SUCCESS!
```

## Next Steps

Once basic tools work:

1. **Explore More Tools:**
   - File operations (read, write, list)
   - Shell commands
   - Image generation
   - Vision (with images)

2. **Chain Multiple Tools:**
   - Search → Scrape → Summarize
   - Navigate → Extract → Analyze

3. **Build Workflows:**
   - Research assistant (search + scrape + analyze)
   - Web monitoring (navigate + extract + compare)
   - Data gathering (search + scrape multiple sources)

## Support

**If stuck:**

1. Check this doc's debugging section
2. Review backend logs for errors
3. Try with a simple test case first
4. Verify Ollama is running: `ollama list`
5. Check model is loaded: `ollama ps`

**Log Files:**
- Backend: Check terminal output or log file
- Frontend: Check browser console (F12)

**Helpful Commands:**
```bash
# Check Ollama status
ollama list
ollama ps

# Test Ollama directly
ollama run qwen2.5-coder "test"

# Check if tools are in system prompt
grep -A 50 "tool examples" backend.log
```
