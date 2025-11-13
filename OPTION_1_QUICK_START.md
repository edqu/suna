# Quick Start: Browser-First with API Fallback (Option 1)

## Setup in 3 Steps (2 Minutes)

### Step 1: Get Gemini API Key

Visit: https://aistudio.google.com/app/apikey

- Click "Create API Key"
- Copy the key (starts with `AIza...`)
- **Free tier:** 1500 requests/day!

### Step 2: Configure Backend

Edit `backend/.env` and add:

```env
# Enable browser-first mode
BROWSER_DEFAULT_FOR_WEB_SEARCH=true

# Add your Gemini API key
GEMINI_API_KEY=your-gemini-api-key-here
```

### Step 3: Restart Backend

```bash
python start.py
```

Look for:
```
🌐 Browser-first mode enabled: Browser tools preferred over API search
✅ Registered LOCAL web search tool (FREE)
✅ Registered browser_tool with all methods
```

## ✅ Done! Test It

```
User: Navigate to example.com and tell me what you see
```

Expected:
- Uses `browser_navigate_to` (browser tool)
- Extracts content with vision
- Returns screenshot + content

If browser fails:
- Automatically falls back to `web_search` (DuckDuckGo)
- Still gets results!

## How It Works

### Browser First

```
User: "Search for X"
  ↓
Try: browser_navigate_to + browser_extract_content
  ↓
Success? → Return results with screenshots
  ↓
Failed? → Fallback to web_search (DuckDuckGo)
  ↓
Always get results!
```

### Tools Available

**PRIMARY (Browser):**
- `browser_navigate_to` - Go to URLs
- `browser_extract_content` - Get content
- `browser_act` - Click, type, scroll
- `browser_screenshot` - Capture page

**FALLBACK (API):**
- `web_search` - DuckDuckGo search
- `scrape_webpage_free` - Scrape pages
- `search_and_scrape_free` - Combined

## Toggle On/Off

### Enable Browser-First

```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
```

### Disable (API-First)

```env
BROWSER_DEFAULT_FOR_WEB_SEARCH=false
```

Restart backend after changes.

## Troubleshooting

### No browser tools registered

**Check logs:**
```
✅ Registered browser_tool with all methods
```

If missing, check `browser_tool` not in disabled_tools.

### Browser not being used

**Check logs:**
```
🌐 Browser-first mode enabled
```

If missing, verify `BROWSER_DEFAULT_FOR_WEB_SEARCH=true` in `.env`.

### GEMINI_API_KEY error

Browser tool returns: "GEMINI_API_KEY is not configured"

**Solution:**
1. Get free key: https://aistudio.google.com/app/apikey
2. Add to `backend/.env`: `GEMINI_API_KEY=your-key`
3. Restart backend

**Fallback still works!** API search takes over automatically.

## Cost

- **Browser tools:** Free Gemini tier (1500/day)
- **API search:** $0 (DuckDuckGo is free)
- **Total:** $0 for development!

## Next Steps

See full guide: [`OPTION_1_IMPLEMENTATION_COMPLETE.md`](./OPTION_1_IMPLEMENTATION_COMPLETE.md)

**That's it! Browser-first mode with reliable fallback.** 🚀
