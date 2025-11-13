# Windows Visible Browser Setup Guide

Complete guide to seeing the browser work on your Windows desktop!

## Overview

This setup runs the browser **on your Windows machine** (not in Docker), so you can watch Chrome open and perform actions in real-time.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Windows Desktop (YOUR SCREEN)                          │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  🌐 Chrome Browser (VISIBLE!)                  │     │
│  │                                                 │     │
│  │  - Opens on your desktop                       │     │
│  │  - You watch it navigate                       │     │
│  │  - See clicks, typing, scrolling               │     │
│  │                                                 │     │
│  └────────────────────────────────────────────────┘     │
│         ↑                                                │
│         │ Controlled by                                 │
│         ↓                                                │
│  ┌────────────────────────────────────────────────┐     │
│  │  Browser Server (Node.js)                      │     │
│  │  Port: 8004                                    │     │
│  │  Location: browser-server/                     │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                   ↑
                   │ HTTP calls via host.docker.internal
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Docker Container (Backend)                             │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │  Backend Server                                │     │
│  │  - Receives user requests                      │     │
│  │  - Calls Windows browser server                │     │
│  │  - Returns screenshots & results               │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                   ↑
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  User's Web Browser (Suna UI)                           │
│  - Sends commands                                        │
│  - Sees screenshots                                      │
│  - Watches progress                                      │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- ✅ Windows 10/11
- ✅ Node.js installed (https://nodejs.org/)
- ✅ Docker Desktop running
- ✅ Gemini API key (free: https://aistudio.google.com/app/apikey)

## Step-by-Step Setup

### Step 1: Install Node.js

1. **Download Node.js:**
   - Go to: https://nodejs.org/
   - Download LTS version (recommended)
   - Run installer

2. **Verify installation:**
   ```bash
   node --version
   # Should show: v20.x.x or similar

   npm --version
   # Should show: 10.x.x or similar
   ```

### Step 2: Get Gemini API Key

1. **Visit:** https://aistudio.google.com/app/apikey
2. **Click:** "Create API Key"
3. **Copy** the key (starts with `AIza...`)

**Free tier includes:**
- 15 requests/minute
- 1500 requests/day
- No credit card required!

### Step 3: Install Browser Server

1. **Open PowerShell or Command Prompt**

2. **Navigate to browser-server folder:**
   ```bash
   cd c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\browser-server
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

   This installs:
   - `@browserbasehq/stagehand` - Browser automation
   - `express` - Web server
   - `dotenv` - Environment config

4. **Wait for installation** (1-2 minutes)

### Step 4: Configure Environment

1. **Create `.env` file:**
   ```bash
   # Copy the example
   copy .env.example .env
   ```

2. **Edit `.env`** (use Notepad or any text editor):
   ```env
   GEMINI_API_KEY=AIzaSy...paste-your-key-here
   PORT=8004
   ```

   Save the file!

### Step 5: Start Browser Server

1. **In the browser-server folder, run:**
   ```bash
   npm start
   ```

2. **You should see:**
   ```
   ╔════════════════════════════════════════════════════════════════╗
   ║                                                                ║
   ║   🌐 Stagehand Browser Server Running on Windows              ║
   ║                                                                ║
   ║   Port: 8004                                                  ║
   ║   Status: http://localhost:8004/api                           ║
   ║                                                                ║
   ║   The browser will open VISIBLY on your Windows desktop!      ║
   ║                                                                ║
   ║   Ready to receive commands from Docker container...          ║
   ║                                                                ║
   ╚════════════════════════════════════════════════════════════════╝

   ✅ GEMINI_API_KEY configured
   ```

3. **Leave this running!** Don't close the window.

### Step 6: Test Browser Server

1. **Open a NEW PowerShell window**

2. **Test health check:**
   ```bash
   curl http://localhost:8004/api
   ```

   Should return:
   ```json
   {"status":"not_initialized","message":"Browser not initialized..."}
   ```

3. **Initialize browser** (this will open Chrome!):
   ```powershell
   $body = @{api_key="YOUR_GEMINI_KEY"} | ConvertTo-Json
   Invoke-RestMethod -Uri http://localhost:8004/api/init -Method Post -Body $body -ContentType "application/json"
   ```

4. **Chrome should open on your screen!** 🎉

### Step 7: Configure Backend

1. **Edit backend `.env`:**
   ```bash
   # In: c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\backend\.env
   ```

2. **Add these lines:**
   ```env
   # Enable external browser mode (visible on Windows)
   STAGEHAND_MODE=external
   STAGEHAND_BASE_URL=http://host.docker.internal:8004/api
   ```

3. **Important:** `host.docker.internal` allows Docker to reach your Windows machine

### Step 8: Restart Backend

1. **Stop backend** (if running): Ctrl+C

2. **Start backend:**
   ```bash
   python start.py
   ```

3. **Look for logs:**
   ```
   🔗 Using external Stagehand server at http://host.docker.internal:8004/api
   ✅ External Stagehand server is reachable
   ✅ External Stagehand initialized successfully
   ```

### Step 9: Test from Suna

1. **Open Suna UI** in your browser

2. **Start a new thread**

3. **Select any model** (Ollama qwen recommended)

4. **Send a message:**
   ```
   Navigate to https://github.com/trending and tell me the top trending repository
   ```

5. **Watch your Windows screen!**
   - Chrome window should appear
   - You'll see it navigate to GitHub
   - Watch it read the trending page
   - See it scroll and click

6. **In Suna UI:**
   - You'll see progress updates
   - Screenshots of what the browser saw
   - Final result with the trending repo

## Troubleshooting

### Issue: npm install fails

**Error:** `Cannot find module ...`

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

### Issue: Browser server won't start

**Error:** `Port 8004 already in use`

**Solution:**
1. Change port in `.env`:
   ```env
   PORT=8005
   ```
2. Also update backend `.env`:
   ```env
   STAGEHAND_BASE_URL=http://host.docker.internal:8005/api
   ```

**Error:** `GEMINI_API_KEY not found`

**Solution:**
- Check `.env` file exists in browser-server folder
- Verify key is on its own line: `GEMINI_API_KEY=AIza...`
- No quotes needed around the key

### Issue: Chrome doesn't open

**Symptom:** Server starts but no browser window

**Solution:**
1. Test initialization manually:
   ```bash
   curl -X POST http://localhost:8004/api/init -H "Content-Type: application/json" -d "{\"api_key\":\"YOUR_KEY\"}"
   ```

2. Check server logs for errors

3. Try restarting the server

### Issue: Docker can't reach browser

**Error in backend:** `Cannot reach external Stagehand server`

**Solutions:**

1. **Verify server is running:**
   ```bash
   curl http://localhost:8004/api
   ```

2. **Check Docker Desktop:**
   - Make sure it's running
   - Try restarting Docker Desktop

3. **Test host.docker.internal:**
   ```bash
   # In Docker container:
   docker exec -it <container> curl http://host.docker.internal:8004/api
   ```

4. **Firewall:**
   - Windows Firewall might block port 8004
   - Allow Node.js through firewall

### Issue: Browser opens but doesn't navigate

**Symptom:** Chrome opens to Google but doesn't go to requested URL

**Check:**
1. Server logs for navigation errors
2. Gemini API key is valid
3. Gemini API quota not exceeded

## Advanced Configuration

### Custom Browser Window Size

Edit `browser-server/stagehand-server.js` (line 60):

```javascript
viewport: {
    width: 1920,  // Your preferred width
    height: 1080  // Your preferred height
}
```

### Multiple Browser Instances

Run multiple servers on different ports:

**Server 1:**
```env
PORT=8004
```

**Server 2:**
```env
PORT=8005
```

Then use different URLs in backend config for different agents.

### Auto-start on Windows Boot

1. **Create batch file** `start-browser-server.bat`:
   ```bat
   @echo off
   cd /d c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\browser-server
   npm start
   ```

2. **Add to Startup:**
   - Press Win+R
   - Type: `shell:startup`
   - Copy the .bat file there

## Daily Usage

### Starting Everything

**Order matters!**

1. **Start browser server** (Windows):
   ```bash
   cd browser-server
   npm start
   ```

2. **Start Docker Desktop**

3. **Start backend:**
   ```bash
   python start.py
   ```

4. **Open Suna UI**

### Stopping Everything

1. **Stop backend:** Ctrl+C
2. **Stop browser server:** Ctrl+C in its window
3. **Optionally stop Docker Desktop**

## What You'll See

### When Browser Works

1. **Server logs:**
   ```
   [stagehand] Browser launching
   [stagehand] Browser ready
   Navigating to: https://github.com
   Performing action: Click trending
   ✅ Action completed
   ```

2. **On your Windows screen:**
   - Chrome window opens
   - URL bar shows github.com
   - Page loads
   - Elements get clicked/filled
   - All visible in real-time!

3. **In Suna UI:**
   - Tool execution messages
   - Screenshots of the browser
   - Extracted content
   - Final results

## Performance

**Typical times:**
- Browser startup: 3-5 seconds (first time)
- Page navigation: 2-5 seconds
- Actions (click, type): 1-3 seconds each
- Screenshot: Instant

**Resource usage:**
- RAM: ~500MB (Chrome + Node.js)
- CPU: Spikes during actions, idle otherwise
- Network: Normal browsing traffic

## Cost

**Gemini Free Tier:**
- 15 requests/minute
- 1500 requests/day
- Each browser action = ~1-2 requests

**Typical usage:**
- Simple navigation: 2-3 requests
- Form filling: 5-10 requests
- Complex workflows: 20-50 requests

**Well within free limits for development!**

## Security Notes

- Browser server runs on localhost only
- Not exposed to internet
- Docker access via internal network only
- API key stored in .env (never commit!)
- Browser runs with your Windows user privileges

## Logs

### Browser Server Logs
```
[stagehand] category: message
Navigating to: https://...
Performing action: ...
Screenshot captured: XXXX bytes
```

### Backend Logs
```
🔗 Using external Stagehand server
✅ External Stagehand server is reachable
Tool execution: browser_navigate_to
✅ Tool execution completed
```

## FAQs

**Q: Can I see the browser from Suna UI?**
A: Yes! Screenshots are automatically captured and displayed. The physical Chrome window is a bonus for debugging.

**Q: Does this work with all models?**
A: Yes! Ollama (Qwen), OpenAI, Anthropic, etc. All can use browser tools.

**Q: Can I use the browser manually while it's running?**
A: Yes, but the automation might interfere. Best to watch only.

**Q: What if I close the Chrome window?**
A: The server will detect it and mark as not initialized. Next request will open it again.

**Q: Can other people on my network see my browser?**
A: No. Server is localhost only. Only you and Docker can access it.

## Next Steps

Once working:

1. **Try complex workflows:**
   - "Search Google for X, click first result, extract main content"
   - "Go to GitHub, find trending repos, summarize top 3"
   - "Navigate to site, fill login form, extract data"

2. **Watch and learn:**
   - See how AI interprets pages
   - Understand what actions it takes
   - Debug when things go wrong

3. **Optimize:**
   - Adjust viewport size for your screen
   - Fine-tune Gemini prompts
   - Create browser automation workflows

## Getting Help

**If stuck:**

1. Check both server logs (browser-server window)
2. Check backend logs
3. Test health endpoint: `curl http://localhost:8004/api`
4. Verify .env configuration
5. Restart everything in order

**Common fixes solve 90% of issues:**
- Restart browser server
- Restart Docker Desktop  
- Check GEMINI_API_KEY is correct
- Verify port 8004 is not blocked

---

**Enjoy watching your AI browse the web!** 🌐✨

The browser will open, navigate, click, fill forms, and extract data - all visible on your Windows desktop in real-time!
