# 🚀 START HERE: Browser-First Mode (Option 1)

## What You're Getting

✅ Browser tools as **DEFAULT** for web searches  
✅ API search (DuckDuckGo) as **FALLBACK**  
✅ Best of both worlds: Capability + Reliability  
✅ 2-minute setup  

## Setup Now (2 Minutes)

### 1. Get Gemini API Key (Free)

https://aistudio.google.com/app/apikey

Copy the key that starts with `AIza...`

### 2. Edit backend/.env

Open: `c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\backend\.env`

Add these two lines:

```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=AIzaSy...paste-your-key-here
```

Save the file.

### 3. Restart Backend

```bash
# Stop current backend (Ctrl+C)
python start.py
```

Wait for:
```
🌐 Browser-first mode enabled: Browser tools preferred over API search
✅ Registered LOCAL web search tool (FREE)
✅ Registered browser_tool with all methods
```

## ✅ Done! Test It

Open Suna UI and try:

```
Navigate to https://github.com/trending and tell me the top repository today
```

**What happens:**
1. Model uses `browser_navigate_to` → Opens Chrome in Docker
2. Model uses `browser_extract_content` → Gets trending repos
3. You get result + screenshot
4. If browser fails → Automatically uses `web_search` instead

## Verify It's Working

### Check Backend Logs

```bash
# Look for at startup:
🌐 Browser-first mode enabled

# Look for during execution:
Tool execution: browser_navigate_to
✅ Tool execution completed
```

### If You See API Search Instead

```bash
# Browser might have failed, check logs:
Browser tool failed: ...
Falling back to web_search
```

This is the fallback working correctly!

## What You Have Now

| Feature | Status |
|---------|--------|
| Browser tools | ✅ Default (tried first) |
| API search (DuckDuckGo) | ✅ Fallback (if browser fails) |
| Ollama/Qwen support | ✅ XML tool calling |
| Free web search | ✅ No API keys needed |
| Screenshots | ✅ Captured automatically |
| Knowledge base upload | ✅ Fixed |

## Common Questions

**Q: Will I see the browser?**
A: Not on your Windows screen (runs in Docker headless). You'll see screenshots in Suna UI.

**Q: What if GEMINI_API_KEY is missing?**
A: Browser fails, automatically falls back to free DuckDuckGo search. Still works!

**Q: Is this slower?**
A: Browser: 5-15s. API search: 1-3s. But browser handles JavaScript sites better.

**Q: Can I disable this?**
A: Yes! Set `BROWSER_DEFAULT_FOR_WEB_SEARCH=false` and restart.

**Q: Do I need to install anything?**
A: No! Everything runs in Docker. Just need the API key.

## Toggle Modes

### Current: Browser-First

```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
```

### Switch to API-First

```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
```

Restart backend after changing.

## Next Steps

- ✅ Start using it immediately
- 📖 Read full docs: [`OPTION_1_IMPLEMENTATION_COMPLETE.md`](./OPTION_1_IMPLEMENTATION_COMPLETE.md)
- 🧪 Test different scenarios
- 📊 Monitor which tool gets used

## Need Help?

1. Check startup logs for "Browser-first mode enabled"
2. Verify both tools registered in logs
3. Test with explicit tool calls first
4. See [`OPTION_1_IMPLEMENTATION_COMPLETE.md`](./OPTION_1_IMPLEMENTATION_COMPLETE.md) for details

---

**You're all set! Browser-first mode with reliable fallback.** 🎉
