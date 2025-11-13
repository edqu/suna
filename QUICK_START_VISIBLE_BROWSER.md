# Quick Start: Visible Browser on Windows

Get your browser visible in 5 minutes!

## Prerequisites Check

```bash
# 1. Node.js installed?
node --version
# Should show v18+ or v20+

# 2. Docker Desktop running?
docker ps
# Should not error

# 3. Gemini API key ready?
# Get free: https://aistudio.google.com/app/apikey
```

## Setup (One Time)

### 1. Install Browser Server

```bash
cd c:\Users\grego\OneDrive\Documents\GitHub\sunaEDQU\browser-server
npm install
```

### 2. Configure API Key

```bash
# Create .env file
copy .env.example .env

# Edit .env and add your key:
# GEMINI_API_KEY=AIza...your-key-here
```

### 3. Configure Backend

Edit `backend/.env` and add:
```env
STAGEHAND_MODE=external
STAGEHAND_BASE_URL=http://host.docker.internal:8004/api
```

## Daily Usage

### Start Order (Important!)

**1. Start Browser Server (Windows):**
```bash
cd browser-server
npm start
```

Wait for:
```
✅ GEMINI_API_KEY configured
```

**2. Start Backend:**
```bash
python start.py
```

Look for:
```
✅ External Stagehand server is reachable
```

**3. Test in Suna:**
```
User: Navigate to https://github.com and tell me what you see
```

**Chrome should open on your Windows desktop!** 🎉

## Verification

### Test 1: Server Running

```bash
curl http://localhost:8004/api
```

Expected:
```json
{"status":"not_initialized",...}
```

### Test 2: Browser Opens

```powershell
# PowerShell:
$body = '{"api_key":"YOUR_KEY"}' | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8004/api/init -Method Post -Body $body -ContentType "application/json"
```

**Chrome should open!**

### Test 3: From Suna

1. Open Suna UI
2. New thread with Ollama qwen model
3. Send: "Navigate to example.com"
4. **Watch Chrome on your screen!**

## Troubleshooting

### Browser server won't start

```bash
# Check port 8004 not in use:
netstat -ano | findstr :8004

# If in use, change port in .env:
PORT=8005

# And update backend/.env:
STAGEHAND_BASE_URL=http://host.docker.internal:8005/api
```

### Backend can't reach browser

```bash
# 1. Verify server running:
curl http://localhost:8004/api

# 2. Check Docker can reach host:
docker run --rm alpine ping -c 1 host.docker.internal

# 3. Restart Docker Desktop
```

### Chrome doesn't open

1. Check GEMINI_API_KEY in browser-server/.env
2. Look at server logs for errors
3. Restart browser server: Ctrl+C then `npm start`

## What You'll See

When it works:

**In Chrome (on your screen):**
- Window opens automatically
- Navigates to websites
- Clicks buttons
- Fills forms
- Scrolls pages
- All visible to you!

**In Suna UI:**
- Tool execution progress
- Screenshots
- Extracted content
- Results

**In Browser Server Logs:**
```
[stagehand] Browser launching
Navigating to: https://...
Performing action: Click...
Screenshot captured
```

## Stop Everything

```bash
# 1. Stop backend: Ctrl+C
# 2. Stop browser server: Ctrl+C in its window
```

## Next Steps

- See full guide: [WINDOWS_VISIBLE_BROWSER_SETUP.md](./WINDOWS_VISIBLE_BROWSER_SETUP.md)
- Try complex workflows
- Watch the AI browse
- Debug visually

**Enjoy watching your AI in action!** 🌐✨
