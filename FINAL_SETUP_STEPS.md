# Final Setup Steps - Do This Now!

## Current Status

✅ All code implemented  
✅ All documentation created  
⏳ **Need to activate configuration**  

## What to Do Right Now

### Step 1: Configure backend/.env

You need to add configuration to your `backend/.env` file.

**Open this file:**
```
c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\backend\.env
```

**Add these lines at the end:**

```env
# ============================================================================
# BROWSER-FIRST MODE (Option 1) - Browser with API Fallback
# ============================================================================

# Enable browser as default for web searches (with DuckDuckGo fallback)
BROWSER_DEFAULT_FOR_WEB_SEARCH=true

# REQUIRED: Gemini API key for browser tools (get free: https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-api-key-here

# Browser mode (managed = runs in Docker, external = runs on Windows)
STAGEHAND_MODE=managed

# ============================================================================
# If you don't have GEMINI_API_KEY:
# 1. Visit: https://aistudio.google.com/app/apikey
# 2. Click "Create API Key" (FREE - no credit card)
# 3. Copy the key (starts with AIza...)
# 4. Paste above replacing "your-gemini-api-key-here"
# ============================================================================
```

**IMPORTANT:** Replace `your-gemini-api-key-here` with your actual API key!

### Step 2: Save the File

Make sure to save `backend\.env` after adding those lines.

### Step 3: Restart Backend

```bash
# Stop current backend (Ctrl+C in the terminal running it)

# Start backend again
python start.py
```

### Step 4: Check Startup Logs

You MUST see these messages:

```
✅ CRITICAL CHECKS:

1. Browser-first mode:
   🌐 Browser-first mode enabled: Browser tools preferred over API search

2. Both tools registered:
   ✅ Registered LOCAL web search tool (FREE) with all methods
   ✅ Registered browser_tool with all methods

3. Ollama support (if using Qwen):
   🔧 Detected Ollama model - forcing XML tool calling for better compatibility
   🔧 Ollama detected: tool_choice disabled, XML mode enforced
```

**If you don't see these messages:**
- Double-check the .env file was saved
- Verify no typos in variable names
- Make sure you restarted the backend

### Step 5: Test in Suna UI

Open Suna and try this command:

```
Navigate to https://httpbin.org/html and extract the main heading
```

**What should happen:**

1. **Model outputs:**
   ```xml
   <function_calls>
   <invoke name="browser_navigate_to">
   <parameter name="url">https://httpbin.org/html</parameter>
   </invoke>
   </function_calls>
   ```

2. **Backend logs:**
   ```
   Executing tool: browser_navigate_to
   Navigating to: https://httpbin.org/html
   Browser initialized successfully
   ✅ Tool execution completed
   ```

3. **Model outputs:**
   ```xml
   <function_calls>
   <invoke name="browser_extract_content">
   <parameter name="instruction">Get the main heading</parameter>
   </invoke>
   </function_calls>
   ```

4. **Final response:**
   - Main heading text
   - Screenshot showing the page
   - Success!

### Step 6: Test Fallback (Optional)

To verify fallback works:

1. **Temporarily comment out GEMINI_API_KEY in backend/.env:**
   ```env
   # GEMINI_API_KEY=your-key
   ```

2. **Restart backend**

3. **Same test:**
   ```
   Search for Qwen model features
   ```

4. **Should automatically use web_search instead!**

5. **Re-enable:**
   ```env
   GEMINI_API_KEY=your-key
   ```

6. **Restart again**

## Quick Visual Checklist

### ☐ backend/.env Updated
- [ ] Added `BROWSER_DEFAULT_FOR_WEB_SEARCH=true`
- [ ] Added `GEMINI_API_KEY=your-actual-key`
- [ ] File saved

### ☐ Backend Restarted
- [ ] Stopped old backend (Ctrl+C)
- [ ] Started new backend (`python start.py`)
- [ ] Saw "Browser-first mode enabled" in logs

### ☐ Tools Verified
- [ ] Saw "Registered LOCAL web search tool"
- [ ] Saw "Registered browser_tool"
- [ ] Both tools showing in logs

### ☐ Tested
- [ ] Sent test message in Suna
- [ ] Model used browser tools
- [ ] Got results with screenshot
- [ ] Success! 🎉

## If You Get Stuck

### Can't find backend/.env file?

**Location:**
```
c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\backend\.env
```

**If it doesn't exist:**
- Create it (copy from .env.example if available)
- Or create new empty file and add the config lines

### GEMINI_API_KEY Issues

**Don't have a key?**
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy entire key
5. Paste into .env file

**Key not working?**
- Check it starts with `AIza`
- No quotes around the key
- No extra spaces
- On its own line

### Backend won't start

**Error messages?**
- Share the error
- Check Python dependencies installed
- Verify Docker is running

### Tools not registered

**Check:**
- Docker Desktop running
- Sandbox can start
- No errors in startup logs

## What You'll Have After Setup

✅ **Browser tools as default**
- Used first for web searches
- Better for JavaScript sites
- Includes screenshots

✅ **API search as fallback**  
- Automatically used if browser fails
- Fast and reliable
- Always available

✅ **Ollama/Qwen compatible**
- XML tool calling enabled
- Works with all Ollama models
- No native function calling issues

✅ **Free operation**
- Gemini free tier (1500/day)
- DuckDuckGo API ($0 forever)
- No costs for development

## Expected Results

### Test 1: Browser Works
```
User: Navigate to example.com
Result: Uses browser, returns screenshot + content
Time: 5-10 seconds
```

### Test 2: Quick Search
```
User: Search for Python tutorials
Result: Might use browser OR API (model decides)
Time: 1-10 seconds
```

### Test 3: Explicit Browser
```
User: Go to GitHub and extract trending repos
Result: Uses browser (navigation words trigger it)
Time: 5-15 seconds
```

### Test 4: Fallback
```
User: Search for news (with GEMINI_API_KEY disabled)
Result: Uses web_search fallback
Time: 1-3 seconds
```

## One-Liner Setup

If you just want the commands:

```bash
# 1. Edit backend/.env and add:
#    BROWSER_DEFAULT_FOR_WEB_SEARCH=true
#    GEMINI_API_KEY=your-key

# 2. Restart:
python start.py

# 3. Test:
#    "Navigate to example.com"
```

## After It's Working

Try these commands to see browser-first in action:

### Web Research
```
Navigate to GitHub trending and find the top Python repository this week
```

### Content Extraction
```
Go to https://news.ycombinator.com and extract the top 3 story titles
```

### Interactive Sites
```
Navigate to DuckDuckGo, search for "Qwen AI", and summarize the first result
```

### Fallback Test
```
Search the web for latest AI news
(If browser fails, will use DuckDuckGo API)
```

## Support

**Still stuck?** Check these docs:

- **Quick guide:** [`START_HERE_OPTION_1.md`](./START_HERE_OPTION_1.md)
- **Full details:** [`OPTION_1_IMPLEMENTATION_COMPLETE.md`](./OPTION_1_IMPLEMENTATION_COMPLETE.md)
- **Quick reference:** [`OPTION_1_QUICK_START.md`](./OPTION_1_QUICK_START.md)

---

**Do the 3 steps above and you're done!** The browser will be your default with reliable fallback. 🚀
