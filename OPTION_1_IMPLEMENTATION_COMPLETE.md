# ✅ Option 1 Implementation: Browser Default with API Fallback

## What Is This?

**Option 1** makes the browser tool your DEFAULT for web searches while keeping API search (DuckDuckGo) as a reliable fallback.

## Benefits

- ✅ **Browser tried first** - Better for JavaScript sites, interactive content
- ✅ **API search fallback** - Reliable backup if browser fails
- ✅ **Both tools available** - Model chooses best tool for the task
- ✅ **Easy to toggle** - One config setting to switch modes
- ✅ **No breaking changes** - Everything still works if browser unavailable

## How It Works

### Before (Default Behavior)

```
User: "Search for Qwen features"
  ↓
Model uses: web_search (DuckDuckGo API)
  ↓
Fast result (1-3 seconds)
```

### After (Browser-First Mode)

```
User: "Search for Qwen features"
  ↓
Model tries: browser_navigate_to + browser_extract_content
  ↓
If successful: Interactive browser result (5-15 seconds)
  ↓
If fails: Falls back to web_search (DuckDuckGo)
  ↓
Reliable result either way!
```

## Setup (2 Minutes)

### Step 1: Enable Browser-First Mode

Edit `backend/.env` and add:

```env
# Make browser the default for web searches (with API fallback)
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
```

### Step 2: Ensure GEMINI_API_KEY Configured

Browser tools require Gemini API key:

```env
# Get free key: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
```

**Important:** If this key is missing, the model will automatically fall back to API search.

### Step 3: Restart Backend

```bash
python start.py
```

Look for:
```
🌐 Browser-first mode enabled: Browser tools preferred over API search
```

### Step 4: Test It

```
User: Navigate to GitHub trending and tell me the top repository
```

The model will:
1. Try `browser_navigate_to` first
2. Use `browser_extract_content` to get data
3. Return results

If browser fails, it automatically uses `web_search` instead!

## Configuration Options

### Enable Browser-First (Option 1)

```env
# backend/.env
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=your-key-here
```

**Result:** Browser tools tried first, API search as fallback

### Disable (Back to API-First)

```env
# backend/.env
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
# or comment it out
```

**Result:** API search (DuckDuckGo) used by default

### Not Set (Default)

If you don't set the variable:

**Result:** API search used (current behavior)

## What the Model Sees

### System Prompt Addition

When `BROWSER_DEFAULT_FOR_WEB_SEARCH=true`, the model receives:

```
=== WEB BROWSING STRATEGY ===

For web research, browsing, or accessing web content:

1. PRIMARY: Use browser tools (browser_navigate_to, browser_extract_content, browser_act)
   - Best for: Interactive sites, JavaScript content, real-time data
   - Use when: Need to see/interact with actual web pages

2. FALLBACK: Use API-based search (web_search, scrape_webpage_free)
   - Use if: Browser tools unavailable or fail
   - Best for: Quick searches, static content

Always try browser tools FIRST for web tasks, but gracefully fall back to API search if needed.
```

This guides the model's decision-making.

## Available Tools

### Browser Tools (Preferred)

- `browser_navigate_to(url)` - Navigate to a URL
- `browser_act(action)` - Perform actions (click, type, etc.)
- `browser_extract_content(instruction)` - Extract specific content
- `browser_screenshot()` - Capture page screenshot

**Requires:** GEMINI_API_KEY configured

### API Search Tools (Fallback)

- `web_search(query)` - DuckDuckGo search
- `scrape_webpage_free(url)` - BeautifulSoup scraping
- `search_and_scrape_free(query)` - Combined search + scrape

**Requires:** Nothing! Always available.

## Use Cases

### When Browser Is Better

✅ **JavaScript-heavy sites:**
- Modern web apps (React, Vue, etc.)
- Single-page applications
- Dynamic content loading

✅ **Interactive tasks:**
- Filling forms
- Clicking buttons
- Dropdown selections
- Multi-step workflows

✅ **Visual content:**
- Screenshots needed
- Layout-dependent extraction
- Verifying what's visible

### When API Search Is Better

✅ **Simple searches:**
- Quick fact lookups
- News searches
- General information

✅ **Static content:**
- Articles
- Documentation
- Blog posts

✅ **Speed priority:**
- Need fast results
- Bulk operations
- Simple queries

## Fallback Behavior

### Automatic Fallback Scenarios

The model automatically falls back to API search when:

1. **GEMINI_API_KEY not configured**
   ```
   Browser tools unavailable → Uses web_search
   ```

2. **Browser initialization fails**
   ```
   Stagehand error → Uses web_search
   ```

3. **Browser action fails**
   ```
   Navigation timeout → Uses web_search
   ```

4. **Sandbox unavailable**
   ```
   Daytona error → Uses web_search
   ```

### Manual Fallback

You can explicitly request API search:

```
User: Use the web_search tool to find information about X
```

The model will honor your explicit tool choice.

## Performance Comparison

| Metric | Browser Tools | API Search |
|--------|--------------|------------|
| **Speed** | 5-15 seconds | 1-3 seconds |
| **JavaScript** | ✅ Handles | ❌ Doesn't handle |
| **Interactions** | ✅ Full support | ❌ Limited |
| **Cost** | Gemini API calls | $0 (free) |
| **Reliability** | Dependent on key | Always available |
| **Screenshots** | ✅ Included | ❌ Not available |

## Cost

### Browser Tools (Gemini)

**Free tier:**
- 15 requests/minute
- 1500 requests/day

**Typical usage:**
- Simple navigation: 2-3 requests
- Complex workflow: 10-20 requests

**Well within free limits!**

### API Search (DuckDuckGo)

**Cost:** $0 (completely free)
**Limits:** None

## Testing

### Test 1: Browser-First Works

```bash
# Enable browser-first
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
```

Send:
```
Navigate to example.com and tell me the main heading
```

Expected:
- Uses `browser_navigate_to`
- Uses `browser_extract_content`
- Returns result with screenshot

### Test 2: Fallback Works

```bash
# Temporarily break browser (remove GEMINI_API_KEY)
# GEMINI_API_KEY=
```

Send:
```
Search for Qwen model features
```

Expected:
- Browser tools fail
- Automatically uses `web_search`
- Still gets results!

### Test 3: Explicit Tool Choice

```
User: Use the web_search tool to find Python tutorials
```

Expected:
- Uses `web_search` directly
- Even if browser is default
- Model respects explicit choice

## Troubleshooting

### Issue: Browser always used (too slow)

**Solution:** Disable browser-first
```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
```

### Issue: Browser never used

**Check:**
1. Is `BROWSER_DEFAULT_FOR_WEB_SEARCH=true`?
2. Is `GEMINI_API_KEY` configured?
3. Are browser tools registered? (Check startup logs)

**Logs to check:**
```
🌐 Browser-first mode enabled
✅ Registered browser_tool with all methods
```

### Issue: Fallback not working

**Symptoms:** Browser fails but no fallback to API search

**Solution:**
- Verify `LocalWebSearchTool` is registered
- Check logs for "Registered LOCAL web search tool"
- Both tools must be available

### Issue: Wrong tool chosen

**Problem:** Model uses API search when browser would be better

**Solutions:**
1. Be more explicit:
   ```
   Navigate to the site and extract...
   ```
   
2. Strengthen guidance (edit system prompt)

3. Explicitly request browser:
   ```
   Use browser_navigate_to to go to...
   ```

## Monitoring

### Startup Logs

```
🔍 Web search preference: local
✅ Registered LOCAL web search tool (FREE)
✅ Registered browser_tool with all methods
🌐 Browser-first mode enabled: Browser tools preferred over API search
```

### Runtime Logs

**Browser used:**
```
Tool execution: browser_navigate_to
Executing tool: browser_navigate_to with params: {...}
✅ Tool execution completed
```

**Fallback triggered:**
```
Browser tool failed: GEMINI_API_KEY not configured
Falling back to web_search
Tool execution: web_search
✅ Tool execution completed
```

## Comparison: Options 1 vs 3

| Feature | Option 1 (This) | Option 3 (Visible Browser) |
|---------|----------------|----------------------------|
| **Browser visibility** | Hidden in Docker | Visible on Windows |
| **Setup complexity** | Very simple (1 config) | Complex (Node.js server) |
| **Performance** | Fast (headless) | Slower (GUI overhead) |
| **Debugging** | Logs + screenshots | Visual + logs |
| **Fallback** | ✅ Automatic | ❌ None |
| **Reliability** | High (has fallback) | Medium (single point) |
| **Best for** | Production use | Development/debugging |

## When to Use Option 1 vs Option 3

### Choose Option 1 (This) If:

- ✅ You want reliability (automatic fallback)
- ✅ You want simplicity (one config flag)
- ✅ You want speed (headless browser)
- ✅ You don't need to see the browser
- ✅ Screenshots are enough for debugging

### Choose Option 3 If:

- ✅ You need to SEE the browser work
- ✅ You're debugging complex workflows
- ✅ You want to watch in real-time
- ✅ You're okay with complex setup
- ✅ You accept no fallback

**Recommendation:** Start with Option 1, switch to Option 3 only if you need visual debugging.

## Migration

### From Current Setup (API-First)

```bash
# Just add one line to backend/.env:
BROWSER_DEFAULT_FOR_WEB_SEARCH=true

# Restart backend
python start.py
```

### From Option 3 (Visible Browser)

```bash
# Remove from backend/.env:
# STAGEHAND_MODE=external
# STAGEHAND_BASE_URL=...

# Add instead:
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
STAGEHAND_MODE=managed

# Can stop the Windows browser server
# Backend will use Docker browser (headless)
```

### Back to API-Only

```bash
# Remove from backend/.env:
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
# or delete the line

# Restart backend
```

## Advanced Configuration

### Custom Guidance

Edit the system prompt section in `run.py` (line ~458) to customize:

```python
browser_guidance = """
Your custom instructions for when to use browser vs API search...
"""
```

### Per-Agent Configuration

Currently global (applies to all agents).

To make per-agent:
1. Add `browser_default` to agent config
2. Check it in `build_system_prompt`
3. Conditionally add browser guidance

## Summary

**What Option 1 Gives You:**

✅ Browser tools as default (better for modern sites)  
✅ API search as fallback (reliable backup)  
✅ Simple setup (one config flag)  
✅ No breaking changes (everything still works)  
✅ Best of both worlds (speed OR capability)  

**Setup Time:** 2 minutes  
**Complexity:** Low  
**Reliability:** High (has fallback)  
**Cost:** Free (Gemini free tier)  

## Quick Reference

```env
# Enable Option 1
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=your-key

# Disable Option 1 (back to normal)
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
```

**That's it!** Simple, reliable, powerful. 🚀
