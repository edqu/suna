# Enable Browser-First Mode Right Now

## Current Status

✅ Code is ready  
✅ Documentation created  
⏳ Configuration needed  

## What You Need to Do

### Step 1: Configure Backend (1 minute)

Open this file in your editor:
```
c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\backend\.env
```

Add these two lines (or update if they exist):

```env
# Enable browser-first mode with API fallback
BROWSER_DEFAULT_FOR_WEB_SEARCH=true

# REQUIRED: Get free key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
```

**Important:** Replace `your-gemini-api-key-here` with your actual Gemini API key!

If you don't have a Gemini key yet:
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. Paste it into the .env file

### Step 2: Restart Backend (1 minute)

```bash
# Stop current backend if running (Ctrl+C)

# Start backend
python start.py
```

### Step 3: Verify Startup Logs (30 seconds)

Look for these messages:

```
✅ MUST SEE THIS:
🌐 Browser-first mode enabled: Browser tools preferred over API search

✅ VERIFY BOTH TOOLS:
✅ Registered LOCAL web search tool (FREE) with all methods
✅ Registered browser_tool with all methods

✅ OLLAMA SUPPORT:
🔧 Detected Ollama model - forcing XML tool calling for better compatibility
```

**If you see all three ✅ sections, you're ready!**

### Step 4: Test It (1 minute)

Open Suna UI and send:

```
Navigate to https://example.com and tell me what the main heading is
```

**Expected behavior:**
1. Model uses `browser_navigate_to(url="https://example.com")`
2. Browser opens in Docker (you won't see it, but it's working)
3. Model uses `browser_extract_content(instruction="Get the main heading")`
4. You get the heading text + screenshot

**Backend logs should show:**
```
Executing tool: browser_navigate_to
Navigating to: https://example.com
Browser initialized successfully
Tool execution completed
```

## Troubleshooting

### Issue: "Browser-first mode enabled" not in logs

**Solution:** Check `backend/.env` file:
- Line must be: `BROWSER_DEFAULT_FOR_WEB_SEARCH=true`
- No typos in variable name
- Save file and restart backend

### Issue: "GEMINI_API_KEY is not configured"

**Solution:**
1. Get free key: https://aistudio.google.com/app/apikey
2. Add to `backend/.env`: `GEMINI_API_KEY=AIza...`
3. Restart backend

**Fallback still works:** If this happens, the model automatically uses `web_search` (DuckDuckGo) instead!

### Issue: Browser tool not registered

**Check startup logs for:**
```
✅ Registered browser_tool with all methods
```

**If missing:**
- Check `browser_tool` is not in disabled_tools
- Verify no errors during tool registration
- Check Docker/sandbox is running

**Fallback still works:** API search is always available!

### Issue: Model still uses web_search

**Possible causes:**
1. Browser initialization failed (check logs)
2. Model decided API search was better for that query
3. Browser-first guidance not in system prompt

**Solutions:**
- Be more explicit: "Use browser_navigate_to to go to..."
- Check for browser initialization errors
- Verify "Browser-first mode enabled" in logs

## What Happens in Different Scenarios

### Scenario 1: Everything Working

```
User: "Navigate to GitHub"
  ↓
Model: browser_navigate_to
  ↓
Browser opens in Docker
  ↓
Screenshot + content returned
  ↓
Success! ✅
```

### Scenario 2: Browser Fails (Fallback Kicks In)

```
User: "Search for Qwen features"
  ↓
Model: browser_navigate_to
  ↓
Browser initialization fails (e.g., GEMINI_API_KEY missing)
  ↓
Model: web_search (DuckDuckGo API)
  ↓
Still gets results! ✅
```

### Scenario 3: Explicit Tool Choice

```
User: "Use web_search to find Python tutorials"
  ↓
Model: web_search
  ↓
Respects explicit instruction
  ↓
Uses API search directly ✅
```

## Performance

**Browser tools:**
- First request: 5-10 seconds (initialization)
- Subsequent: 3-7 seconds (navigation/actions)
- Screenshots: Included automatically

**API search (fallback):**
- Always: 1-3 seconds
- No initialization needed
- No screenshots

## Cost

**Both are FREE for development:**

- **Browser:** Gemini free tier (1500 requests/day)
- **API search:** $0 (DuckDuckGo is free forever)

**You won't pay anything with normal usage!**

## Quick Commands Reference

### Enable browser-first:
```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
```

### Disable browser-first (API-first):
```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
```

### Force browser usage in prompt:
```
Navigate to [url] and extract [content]
```

### Force API search in prompt:
```
Use web_search to find [query]
```

## Testing Checklist

After enabling, test these:

### ✅ Browser Works
```
Navigate to https://github.com/trending
```
Should use browser tools.

### ✅ Fallback Works
```bash
# Temporarily remove GEMINI_API_KEY from .env
# Restart backend
```
```
Search for Qwen features
```
Should fall back to web_search.

### ✅ Both Available
```
Use web_search to find news about AI
```
Should respect explicit choice.

### ✅ Ollama Compatible
```bash
# Select ollama/qwen2.5-coder model
```
```
Navigate to example.com
```
Should work with XML tool calling.

## Verification Commands

### Check config is loaded:
```bash
# In backend terminal, look for:
grep "BROWSER_DEFAULT_FOR_WEB_SEARCH" backend/.env
```

### Check tools registered:
```bash
# In backend startup logs:
grep "Registered.*tool" 

# Should show BOTH:
# ✅ Registered LOCAL web search tool
# ✅ Registered browser_tool
```

### Check browser-first active:
```bash
# In backend startup logs:
grep "Browser-first mode"

# Should show:
# 🌐 Browser-first mode enabled
```

## Summary

**What you configured:**
- ✅ `BROWSER_DEFAULT_FOR_WEB_SEARCH=true` in backend/.env
- ✅ `GEMINI_API_KEY` in backend/.env
- ✅ Both browser and API search tools available
- ✅ System prompt guides model to prefer browser

**What happens:**
- Browser tools tried first for web tasks
- API search used if browser fails
- Reliable results either way
- Works with all models (Ollama/Qwen included)

**Time investment:** 2 minutes setup  
**Complexity:** Low (just config)  
**Reliability:** High (has fallback)  
**Cost:** Free (within free tiers)  

---

## Ready to Enable?

1. ✅ Add `BROWSER_DEFAULT_FOR_WEB_SEARCH=true` to `backend/.env`
2. ✅ Add `GEMINI_API_KEY=your-key` to `backend/.env`
3. ✅ Restart: `python start.py`
4. ✅ Test: "Navigate to example.com"

**That's it! Browser-first mode with reliable fallback.** 🎉
