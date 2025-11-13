# Making Browser the Default for Web Searches - Options

## Current Situation

You have **two** web search tools:

1. **API-Based Search** (`web_search` - DuckDuckGo)
   - ✅ Free (no API keys)
   - ✅ Very fast (1-3 seconds)
   - ✅ Low resource usage
   - ❌ No visual browser
   - ❌ Can't interact with pages

2. **Browser Tool** (`browser_navigate_to`)
   - ✅ Real browser with full JavaScript
   - ✅ Can click, fill forms, etc.
   - ✅ Screenshots show what you see
   - ❌ Slower (5-15 seconds per action)
   - ❌ Requires GEMINI_API_KEY (costs money)
   - ❌ Higher resource usage

## Your Request

You want:
1. Browser to be the **default** for web searches
2. See the browser **visually** (not just screenshots)
3. Browser visible in tool details UI

## Three Implementation Options

### Option 1: Browser as Default with API Fallback (Recommended)

**What it does:**
- Browser is tried first for web searches
- If browser fails or GEMINI_API_KEY missing, falls back to API search
- Both tools remain available

**Pros:**
- ✅ Best of both worlds
- ✅ Reliable (fallback if browser fails)
- ✅ Can toggle back easily
- ✅ Fast when browser isn't needed

**Cons:**
- ⚠️ Need GEMINI_API_KEY for browser
- ⚠️ Slower for simple searches

**Implementation:**
- Add config flag: `BROWSER_DEFAULT_FOR_WEB_SEARCH=true`
- Modify system prompt to prefer browser
- Keep both tools registered

---

### Option 2: Browser ONLY (Replace API Search)

**What it does:**
- Completely disables API-based search
- Only browser tool available
- No fallback

**Pros:**
- ✅ Simple (one tool only)
- ✅ Consistent behavior

**Cons:**
- ❌ Much slower for everything
- ❌ Breaks if GEMINI_API_KEY missing
- ❌ Higher costs
- ❌ No fallback if browser fails

**Implementation:**
- Disable `local_web_search_tool` registration
- Only register `browser_tool`

---

### Option 3: Visible Browser on Windows Host (Advanced)

**What it does:**
- Runs browser ON YOUR WINDOWS MACHINE (not in Docker)
- Browser window actually appears
- Docker calls your local browser

**Pros:**
- ✅ See the browser window on Windows
- ✅ Can watch it work in real-time
- ✅ Debug visually

**Cons:**
- ⚠️ More complex setup
- ⚠️ Requires running Stagehand server on Windows
- ⚠️ Security implications (host access)

**Implementation:**
1. Install Node.js on Windows
2. Install Stagehand: `npm install @browserbasehq/stagehand`
3. Run local Stagehand server
4. Configure Docker to call `host.docker.internal:8004`

---

## Making Browser Visible - Two Approaches

### Approach A: Host-Mode (Easiest for Windows)

**Steps:**

1. **Install on Windows:**
   ```bash
   npm install -g @browserbasehq/stagehand
   # or use yarn/pnpm
   ```

2. **Create Stagehand server on Windows:**
   ```bash
   # Create browser-server.js
   # Run: node browser-server.js
   ```

3. **Update Docker config:**
   ```env
   STAGEHAND_BASE_URL=http://host.docker.internal:8004/api
   STAGEHAND_MODE=external
   ```

4. **Browser opens on Windows!**
   - Visible Chrome window
   - Can watch it work
   - Screenshots still captured

---

### Approach B: VNC in Docker (Complex)

**Steps:**

1. Install VNC server in Docker container
2. Expose port 6080
3. Open http://localhost:6080 in browser
4. See Docker's browser through VNC

**Not recommended** - very complex on Windows.

---

## Recommended Solution

**For your use case, I recommend:**

### Phase 1: Browser as Default (Today)
1. Add `BROWSER_DEFAULT_FOR_WEB_SEARCH=true` to config
2. Update system prompt to prefer browser
3. Keep API search as fallback

**Result:** Browser used first, API search as backup

### Phase 2: Visible Browser (If Needed)
1. Set up host-mode Stagehand server on Windows
2. Browser opens visibly on your screen
3. Still works from Docker

**Result:** See the browser work in real-time

### Phase 3: UI Improvements (Polish)
1. Show browser state in tool details
2. Display screenshots inline
3. Add "Open in my browser" button

**Result:** Better visibility without complexity

---

## Quick Decision Guide

**Answer these questions:**

1. **Do you need API search as fallback?**
   - Yes → Option 1 (Default with fallback)
   - No → Option 2 (Browser only)

2. **Do you need to SEE the browser window?**
   - Yes, absolutely → Option 3 (Host-mode)
   - No, screenshots OK → Phase 1 only

3. **Is GEMINI_API_KEY configured?**
   - Yes → Can proceed
   - No → Get free key first: https://aistudio.google.com/app/apikey

4. **What's your priority?**
   - Speed + reliability → Keep API search as default
   - Visual debugging → Set up host-mode
   - Simple web research → Browser as default (Phase 1)

---

## What I'll Implement

Based on your request, I'll implement:

**✅ Phase 1: Browser as Default with Fallback**
- Fastest to implement
- Safest (has fallback)
- Easily reversible

**Then if you confirm:**

**Phase 2: Host-Mode for Visible Browser**
- Shows browser on Windows
- More setup but cleaner than VNC

**And:**

**Phase 3: UI Improvements**
- Better tool visibility
- Inline screenshots
- Browser state panel

---

## Commands to Get Started

### Check if GEMINI_API_KEY is configured:
```bash
# In backend/.env, look for:
GEMINI_API_KEY=AIza...

# If not there, get free key:
# https://aistudio.google.com/app/apikey
```

### Test current browser tool:
```
User: Navigate to https://example.com and show me a screenshot
```

### After implementation, test browser as default:
```
User: Search for Qwen model features
# Should use browser instead of API search
```

---

## Cost Implications

### API Search (Current Default):
- **Cost:** $0/month (free DuckDuckGo)
- **Speed:** 1-3 seconds
- **Limits:** None

### Browser (New Default):
- **Cost:** Uses Gemini API for vision
  - Free tier: 15 requests/minute
  - Paid: ~$0.01 per 1000 characters
- **Speed:** 5-15 seconds per action
- **Limits:** Gemini rate limits

**Recommendation:** Use free tier for testing, monitor usage.

---

## Next Steps

1. **Confirm** which option you want:
   - Option 1: Browser default with API fallback ✅
   - Option 2: Browser only (no fallback) ⚠️
   - Option 3: Visible browser on Windows (advanced) ⚡

2. **Check** GEMINI_API_KEY in `.env`

3. **I'll implement** based on your choice

**Ready to proceed?**
