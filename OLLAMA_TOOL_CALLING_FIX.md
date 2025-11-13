# Ollama Tool Calling Fix for Qwen and Other Models

## Problem

Ollama models (including Qwen) were not using the browser tool or local web search tools despite having `FUNCTION_CALLING` capabilities enabled in the model registry.

## Root Causes

1. **Inconsistent Native Tool Calling**: While Qwen is marked as supporting function calling, Ollama's implementation is inconsistent and many models don't reliably emit native OpenAI-style tool calls.

2. **tool_choice Parameter**: Ollama's API doesn't accept the `tool_choice` parameter (OpenAI-specific), which was being sent with every request. This can cause silent failures or ignored tools.

3. **Format Preference**: The system was defaulting to native tool calling for models marked with `FUNCTION_CALLING` capability, but XML-based tool calling is far more reliable for Ollama models.

## Solution Implemented

### 1. Force XML Tool Calling for Ollama Models

**File**: `backend/core/run.py` (lines 798-803)

```python
# SPECIAL HANDLING: Force XML for Ollama models
# Ollama models (including Qwen) work better with XML tool calling
# Native function calling support in Ollama is inconsistent
if model_provider == "ollama":
    logger.info(f"🔧 Detected Ollama model - forcing XML tool calling for better compatibility")
    model_supports_native = False
```

**Why this works:**
- XML tool calling uses clear text instructions in the system prompt
- Models can see the tool schemas and examples directly
- More reliable across all Ollama models, not just specific ones
- Works with Qwen, Llama, Mistral, and other Ollama-hosted models

### 2. Disable tool_choice for Ollama

**File**: `backend/core/run.py` (lines 820-822)

```python
# SPECIAL HANDLING: Ollama doesn't support tool_choice parameter
# Using tool_choice with Ollama can cause silent failures or ignored tools
tool_choice_param = "auto" if model_provider != "ollama" else None
```

**Why this works:**
- Ollama's API specification doesn't include `tool_choice`
- Sending unsupported parameters can cause request failures
- Ollama models will naturally choose to use tools when appropriate via XML prompting

### 3. Use Native Only When Truly Supported

**File**: `backend/core/run.py` (line 817)

```python
use_native = model_supports_native   # Enable native only if model truly supports it
use_xml = True                        # Always enable XML (universal fallback)
```

**Why this works:**
- Native is now conditional based on provider
- XML is always available as a reliable fallback
- For Ollama, native is disabled (set to False above)

## How XML Tool Calling Works

### System Prompt Enhancement

When XML tool calling is enabled, the system prompt includes:

1. **Tool Schemas**: JSON schema for each available tool
2. **XML Format Examples**: How to call tools using XML tags
3. **Instructions**: Clear guidance on when and how to use tools

### Example XML Tool Call

```xml
<function_calls>
<invoke name="search_web_free">
<parameter name="query">latest Qwen model features</parameter>
<parameter name="max_results">5</parameter>
</invoke>
</function_calls>
```

### Response Processing

The universal tool adapter:
1. Detects `<function_calls>` blocks in the response
2. Parses tool name and parameters
3. Normalizes to `NormalizedToolCall` format
4. Executes the tool
5. Returns results to the model

## Available Free Tools for Ollama/Qwen

### 1. Local Web Search Tool

**FREE** - No API keys required

Functions:
- `search_web_free(query, max_results)` - Search using DuckDuckGo
- `scrape_webpage_free(url, extract_markdown)` - Scrape any webpage
- `search_and_scrape_free(query, num_results)` - Combined search + scrape

Technologies:
- DuckDuckGo API for search
- BeautifulSoup + Readability for scraping
- html2text for markdown conversion

### 2. Browser Tool

**FREE** - Requires local setup

Functions:
- `browser_navigate_to(url)` - Navigate to a URL
- `browser_act(instruction)` - Perform actions (click, type, scroll)
- `browser_extract_content(instruction)` - Extract specific content
- `browser_screenshot()` - Capture page screenshot

Technologies:
- Playwright for browser automation
- Stagehand API for intelligent actions
- Google Gemini 2.5 Pro for vision (requires `GEMINI_API_KEY`)

**Note**: Browser tool requires `GEMINI_API_KEY` to be configured. Free tier available.

### 3. Other Tools

All standard tools work with Ollama via XML:
- File operations (read, write, list)
- Shell commands
- Image generation/editing
- Knowledge base access
- And more...

## Testing Instructions

### Test 1: Web Search

**Prompt:**
```
Search for the latest Qwen model release notes and summarize them
```

**Expected Behavior:**
1. Model outputs XML: `<invoke name="search_web_free">`
2. Tool executes DuckDuckGo search
3. Results returned to model
4. Model summarizes findings

**Log Indicators:**
```
🔧 Detected Ollama model - forcing XML tool calling for better compatibility
🔧 Universal Tool Adapter: native=False, xml=True (model preference: xml)
🔧 Ollama detected: tool_choice disabled, XML mode enforced
```

### Test 2: Web Scraping

**Prompt:**
```
Scrape https://example.com and tell me what the main heading says
```

**Expected Behavior:**
1. Model outputs: `<invoke name="scrape_webpage_free">`
2. Tool fetches and parses page
3. Content extracted with Readability
4. Model receives clean markdown
5. Model extracts and reports heading

### Test 3: Browser Automation (if configured)

**Prompt:**
```
Go to https://github.com/trending and tell me the top trending repository
```

**Expected Behavior:**
1. Model outputs: `<invoke name="browser_navigate_to">`
2. Browser opens GitHub trending page
3. Model outputs: `<invoke name="browser_extract_content">`
4. Content extracted
5. Model reports trending repo

## Configuration Checklist

### For Local Web Search (Always Works)

✅ No configuration needed!
- DuckDuckGo is free and requires no API key
- BeautifulSoup is installed automatically
- Works out of the box

### For Browser Tool (Optional)

1. **Get Gemini API Key** (Free tier available)
   - Go to: https://aistudio.google.com/app/apikey
   - Create a free API key

2. **Add to Environment**
   ```env
   # In backend/.env
   GEMINI_API_KEY=your-key-here
   ```

3. **Restart Backend**
   ```bash
   python start.py
   ```

4. **Verify in Logs**
   ```
   ✅ Registered browser_tool with all methods
   ```

## Model-Specific Notes

### Qwen Models

**Works Best With:**
- `ollama/qwen2.5-coder` - Excellent at understanding tool schemas
- Auto-discovered Qwen models with vision (qwen2-vl, qwen3-vl)

**Tips:**
- Be explicit in prompts: "Search the web for..." triggers tools better
- Qwen is very literal - clear instructions work best
- Check token limits (32K context for qwen2.5-coder)

### Other Ollama Models

**Tested and Working:**
- Llama 3.1/3.2 series
- Mistral models
- DeepSeek models
- Phi models

**Universal Compatibility:**
- XML tool calling works with ANY text-based Ollama model
- Model doesn't need special fine-tuning for tools
- Just needs to be able to follow instructions

## Troubleshooting

### Tools Not Being Called

**Check:**
1. Backend logs for "Detected Ollama model" message
2. System prompt includes tool schemas (look for JSON schema in logs)
3. Model has sufficient context window for schemas

**Fix:**
- Be more explicit: "Use the search_web_free tool to..."
- Try a different Qwen variant (larger models understand better)
- Check if model's context window is full

### "search_web_free not found" Error

**Cause**: Tool not registered

**Fix:**
```python
# Verify in backend logs:
✅ Registered LOCAL web search tool (FREE - DuckDuckGo + BeautifulSoup)
```

If missing:
1. Check `web_search_preference` in agent config
2. Ensure `local_web_search_tool` is enabled
3. Restart backend

### Browser Tool Not Working

**Cause**: Missing GEMINI_API_KEY

**Fix:**
1. Add `GEMINI_API_KEY` to `.env`
2. Restart backend
3. Or use web search instead (doesn't require browser)

### XML Not Being Parsed

**Cause**: Response processor not detecting XML

**Debug:**
```python
# Look for in logs:
"Detected XML tool call: <invoke name=\"...\">"
```

**Fix:**
- Ensure `xml_tool_calling=True` in ProcessorConfig
- Check response processor is using universal adapter
- Verify XML format in model output

## Performance Tips

### 1. Optimize Context Window Usage

**Problem**: Tool schemas can be large

**Solution**:
- Only enable tools you need for the task
- Disable unused tools in agent configuration
- Use smaller, focused tool sets

### 2. Response Time

**Typical Times with Ollama:**
- Small models (7B): 2-5 seconds per call
- Medium models (13-34B): 5-15 seconds per call
- Large models (70B+): 15-30+ seconds per call

**Optimization**:
- Use quantized models (Q4, Q5) for faster inference
- GPU acceleration highly recommended
- Keep prompts concise

### 3. Tool Call Reliability

**Make It Explicit:**
```
Bad:  "Find information about X"
Good: "Use search_web_free to find information about X"
Best: "Search the web for information about X and summarize the results"
```

The model is more likely to use tools when:
- You mention searching/browsing explicitly
- You ask for real-time/current information
- You reference external websites

## Comparison: XML vs Native Tool Calling

| Aspect | XML (Ollama) | Native (OpenAI) |
|--------|--------------|-----------------|
| **Reliability** | ✅ Very High | ⚠️ Model-dependent |
| **Speed** | ✅ Same | ✅ Same |
| **Model Support** | ✅ Universal | ⚠️ Specific models |
| **Debugging** | ✅ Easy (visible in text) | ⚠️ Hidden in API |
| **Setup** | ✅ None | ⚠️ Model must support |
| **Format** | XML tags in response | JSON in API metadata |

## Architecture Flow

```
User Message: "Search for Qwen news"
         ↓
Ollama Provider Detected
         ↓
Force XML Mode (model_supports_native = False)
         ↓
Build System Prompt + Tool Schemas + XML Examples
         ↓
Send to Ollama Model (Qwen)
         ↓
Model Responds with:
"Let me search for that.
<function_calls>
<invoke name="search_web_free">
<parameter name="query">Qwen news</parameter>
</invoke>
</function_calls>"
         ↓
Response Processor Detects XML
         ↓
Universal Adapter Normalizes
         ↓
DuckDuckGo Search Executes
         ↓
Results Returned to Model
         ↓
Model Summarizes Results
         ↓
User Receives Answer
```

## Benefits

### 1. Universal Compatibility
- Works with **any** Ollama model
- No special fine-tuning needed
- Consistent behavior across models

### 2. Cost Savings
- **$0/month** for local web search
- No Tavily or Firecrawl subscriptions
- Free Gemini tier for browser (optional)

### 3. Privacy
- DuckDuckGo doesn't track searches
- All processing happens locally
- No data sent to external APIs (except search queries)

### 4. Reliability
- XML parsing is deterministic
- Clear error messages
- Easy to debug

## Next Steps

1. **Test with Your Qwen Model**
   ```
   User: Search for the latest AI research papers
   ```

2. **Monitor Logs**
   Look for:
   - "Detected Ollama model" ✅
   - "forcing XML tool calling" ✅
   - "tool_choice disabled" ✅

3. **Try Different Tools**
   - Web search (always works)
   - Web scraping (always works)
   - Browser (needs GEMINI_API_KEY)
   - File operations (always works)

4. **Optimize**
   - Adjust model size vs speed
   - Enable only needed tools
   - Fine-tune prompts for clarity

## Support

### Logs to Check

**Startup:**
```
🔍 Web search preference: local
✅ Registered LOCAL web search tool (FREE)
✅ Registered browser_tool with all methods
📋 Available tools: search_web_free, scrape_webpage_free, browser_navigate_to, ...
```

**Runtime:**
```
🤖 Model: ollama/qwen2.5-coder (provider: ollama, supports_functions: False)
🔧 Detected Ollama model - forcing XML tool calling
🔧 Universal Tool Adapter: native=False, xml=True
🔧 Ollama detected: tool_choice disabled, XML mode enforced
```

**Tool Execution:**
```
Detected XML tool call: <invoke name="search_web_free">
Executing tool: search_web_free with params: {'query': '...'}
Tool execution completed: ToolResult(success=True, ...)
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "No tools registered" | Check agent config, restart backend |
| "Tool not found" | Verify tool name matches schema exactly |
| "XML not detected" | Check model output for proper XML format |
| "Gemini API error" | Add GEMINI_API_KEY or use web search instead |

## Files Modified

1. ✅ `backend/core/run.py` - Added Ollama detection and XML forcing
2. ✅ `backend/core/agentpress/tool_adapter.py` - Universal adapter (already existed)
3. ✅ `backend/core/tools/local_web_search_tool.py` - Free search tool (already existed)
4. ✅ `backend/core/tools/browser_tool.py` - Browser automation (already existed)

## References

- [Tool Adapter Guide](./TOOL_ADAPTER_GUIDE.md) - Universal tool adapter documentation
- [Free Web Browsing](./FREE_WEB_BROWSING.md) - Local web search setup
- [Ollama GPU Optimization](./OLLAMA_GPU_OPTIMIZATION.md) - Performance tuning

---

**Bottom Line**: Ollama models (including Qwen) now fully support tool calling via XML format. Free web search and browsing work out of the box! 🎉
