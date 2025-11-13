# Stagehand Browser Server for Windows

This server runs **on your Windows machine** (not in Docker) and provides browser automation with a **VISIBLE Chrome window** that you can watch in real-time.

## Why This Server?

- ✅ **See the browser** - Chrome opens on your Windows desktop
- ✅ **Watch it work** - See every action as it happens
- ✅ **Debug visually** - Understand what the AI is doing
- ✅ **Full control** - Runs on your machine, not in Docker

## Quick Setup

### 1. Install Node.js

Download and install from: https://nodejs.org/ (LTS version recommended)

Verify installation:
```bash
node --version
npm --version
```

### 2. Install Dependencies

```bash
cd browser-server
npm install
```

This installs:
- `@browserbasehq/stagehand` - Browser automation with AI
- `express` - Web server
- `dotenv` - Environment configuration

### 3. Get Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

**Free tier includes:**
- 15 requests per minute
- 1500 requests per day
- No credit card required

### 4. Configure Environment

Create `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your key:
```env
GEMINI_API_KEY=AIzaSy...your-actual-key-here
PORT=8004
```

### 5. Start the Server

```bash
npm start
```

You should see:
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

### 6. Test the Server

Open a new terminal and test:

```bash
# Check health
curl http://localhost:8004/api

# Should return:
# {"status":"not_initialized","message":"Browser not initialized..."}

# Initialize browser (this opens Chrome!)
curl -X POST http://localhost:8004/api/init ^
  -H "Content-Type: application/json" ^
  -d "{\"api_key\":\"YOUR_KEY\"}"

# A Chrome window should open on your screen!
```

## Usage from Docker

Once the server is running on Windows, your Docker container can use it:

### Backend Configuration

Add to `backend/.env`:
```env
STAGEHAND_BASE_URL=http://host.docker.internal:8004/api
STAGEHAND_MODE=external
```

### How It Works

```
User in Suna UI
    ↓
Docker Container (Backend)
    ↓
Calls http://host.docker.internal:8004/api
    ↓
Windows Host (This Server)
    ↓
Opens Chrome Browser on Windows Desktop ← YOU SEE THIS!
    ↓
Takes Screenshot, Returns Result
    ↓
Docker Container
    ↓
Suna UI Shows Screenshot
```

## API Endpoints

### GET /api
Health check - returns browser status

### POST /api/init
Initialize the browser (opens Chrome window)
```json
{
  "api_key": "your-gemini-api-key"
}
```

### POST /api/navigate
Navigate to a URL
```json
{
  "url": "https://example.com"
}
```

### POST /api/act
Perform an action
```json
{
  "action": "Click the login button",
  "variables": {}
}
```

### POST /api/extract
Extract content from page
```json
{
  "instruction": "Get the main heading"
}
```

### POST /api/screenshot
Take a screenshot
```json
{
  "fullPage": false
}
```

### POST /api/shutdown
Close the browser

## Watching the Browser

Once you run a command from Suna that uses browser tools, you'll see:

1. **Chrome window opens** on your Windows desktop
2. **Page loads** visibly
3. **Actions happen** in real-time (clicks, typing, etc.)
4. **Screenshots captured** and sent back to Suna

Example:
```
User in Suna: "Navigate to GitHub and find trending repositories"

You see on Windows:
1. Chrome opens
2. Goes to github.com
3. Clicks "Trending" 
4. Scrolls through results
5. All visible to you!
```

## Troubleshooting

### Server won't start

**Error: `GEMINI_API_KEY not found`**
- Solution: Create `.env` file with your API key

**Error: `Port 8004 already in use`**
- Solution: Change `PORT=8005` in `.env`

**Error: `Cannot find module @browserbasehq/stagehand`**
- Solution: Run `npm install` again

### Browser won't open

**No Chrome window appears**
- Check server logs for errors
- Verify GEMINI_API_KEY is correct
- Try calling `/api/init` manually

**Error: `Browser not initialized`**
- Call POST `/api/init` first to start browser

### Docker can't connect

**Error: `Connection refused to host.docker.internal`**
- Ensure server is running on Windows
- Check firewall isn't blocking port 8004
- Verify Docker Desktop is running

**Wrong URL in Docker**
- Should be `http://host.docker.internal:8004/api`
- NOT `http://localhost:8004/api` (localhost = Docker, not host)

## Development Mode

For auto-restart on file changes:

```bash
npm run dev
```

Uses `nodemon` to watch for changes.

## Security Notes

- Server runs on localhost only (not exposed to internet)
- API key stored in .env (never commit to git)
- Docker access via `host.docker.internal` (localhost mapping)
- No authentication (localhost only)

## Performance

- **Startup:** 3-5 seconds (browser initialization)
- **Navigation:** 2-5 seconds per page
- **Actions:** 2-10 seconds (depending on complexity)
- **Screenshots:** Instant (base64 encoded)

## Cost

- **Gemini Free Tier:** 15 requests/min, 1500/day
- **Each browser action:** ~1-2 requests
- **Typical usage:** 10-50 requests/hour
- **Well within free limits** for development!

## Logs

Server logs all actions:
```
[stagehand] Browser launching
[stagehand] Browser ready
Navigating to: https://github.com
Performing action: Click trending
✅ Browser initialized successfully
```

## Stopping the Server

Press `Ctrl+C` in the terminal where server is running.

Or call shutdown endpoint:
```bash
curl -X POST http://localhost:8004/api/shutdown
```

## Next Steps

1. ✅ Start this server
2. ✅ Configure backend to use it (see main setup guide)
3. ✅ Test from Suna UI
4. ✅ Watch Chrome work on your desktop!

## Support

If issues persist:
1. Check server logs
2. Verify .env configuration
3. Test endpoints manually with curl
4. Check Docker Desktop is running
5. Restart both server and Docker

## Advanced Configuration

### Custom Browser Options

Edit `stagehand-server.js` line 59-68 to customize browser:

```javascript
localBrowserLaunchOptions: {
    headless: false,  // Keep false to see browser
    viewport: {
        width: 1920,  // Larger viewport
        height: 1080
    },
    args: [
        '--start-maximized',
        '--your-custom-flag'
    ]
}
```

### Multiple Browsers

To run multiple browser instances, change the port:

```env
PORT=8005
```

Then configure different agents to use different ports.

---

Enjoy watching your AI browse the web! 🌐✨
