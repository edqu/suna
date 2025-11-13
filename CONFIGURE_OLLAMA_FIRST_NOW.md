# Configure Ollama-First Right Now (3 Steps)

## What You're Getting

✅ **FREE** local Ollama vision for browser (instead of Gemini API)  
✅ **PRIVATE** - All processing on your machine  
✅ **NO LIMITS** - Unlimited browser actions  
✅ **Gemini fallback** - Backup if Ollama fails  

## Quick Setup (3 Minutes)

### Step 1: Install Ollama Vision Model

```bash
# If Ollama not installed, get it: https://ollama.com/download

# Pull a vision model (choose one):
ollama pull qwen2-vl        # Recommended - 4GB, fast, accurate
# OR
ollama pull qwen3-vl        # Newer - 5GB, slightly better
# OR  
ollama pull llava           # Alternative - 3GB, good for simple tasks
```

**Verify:**
```bash
ollama list
# Should show your vision model
```

### Step 2: Configure Backend

**Open:** `backend/.env`

**Add these lines:**

```env
# ============================================================================
# OLLAMA-FIRST CONFIGURATION (FREE!)
# ============================================================================

# Use FREE local Ollama for browser vision
BROWSER_VISION_MODEL=ollama/qwen2-vl

# Ollama server URL
OLLAMA_API_BASE=http://localhost:11434

# Enable browser-first web searches
BROWSER_DEFAULT_FOR_WEB_SEARCH=true

# OPTIONAL: Gemini as fallback (only if Ollama fails)
# You already have this set - keep it as backup!
# GEMINI_API_KEY=your-existing-key
```

**Save the file!**

### Step 3: Restart Backend

```bash
# Stop backend (Ctrl+C)
python start.py
```

**MUST see these logs:**

```
✅ VERIFY THESE:

Using vision model: ollama/qwen2-vl
Using Ollama vision model at http://localhost:11434
🌐 Browser-first mode enabled
✅ Registered DuckDuckGo browser search
✅ Registered browser_tool with all methods
```

**If you see all ✅ you're ready!**

## ✅ Test It Now

```
Navigate to https://example.com and describe what you see on the page
```

**What happens:**
1. Browser opens in Docker
2. Uses **ollama/qwen2-vl** for vision (FREE! 🎉)
3. No Gemini API calls
4. Completely local and private
5. Returns description + screenshot

**Check logs:**
```
[stagehand] Using model: ollama/qwen2-vl
✅ No Gemini API calls!
```

## What Changed

### Before (Gemini Only)

```
Browser vision → google/gemini-2.5-pro
Cost: Gemini API calls
Privacy: Sent to Google
```

### After (Ollama-First)

```
Browser vision → ollama/qwen2-vl (FREE!)
Cost: $0
Privacy: 100% local
Fallback → Gemini (only if Ollama fails)
```

## Verify Ollama Is Being Used

### Check Logs

**Should see:**
```
Using vision model: ollama/qwen2-vl
[stagehand] Using model: ollama/qwen2-vl
```

**Should NOT see (for normal operations):**
```
google/gemini-2.5-pro
API key: AIza...
```

If you see Gemini being used, Ollama might not be running!

### Monitor Ollama

```bash
# Check what's loaded:
ollama ps

# Should show:
# NAME        ID        SIZE    PROCESSOR
# qwen2-vl    ...       4.0GB   100% GPU
```

## Cost Savings Calculator

**Typical Daily Usage:**
- 50 browser vision actions/day
- Each action = ~2 Gemini API requests

### Before (Gemini):
- 100 API requests/day
- Within free tier (1500/day)
- But tracked and limited

### After (Ollama):
- 0 API requests/day
- No tracking
- Unlimited usage
- **100% savings!**

## Troubleshooting

### Ollama model not found

```bash
# Pull the model:
ollama pull qwen2-vl

# Verify:
ollama list
```

### Ollama not running

```bash
# Check status:
ollama ps

# If empty, Ollama is installed but idle (normal)
# It will start when first used

# If "connection refused":
# - Windows: Start Ollama app from Start menu
# - Mac: Open Ollama app
# - Linux: systemctl start ollama
```

### Still using Gemini

**Check:**
1. `BROWSER_VISION_MODEL=ollama/qwen2-vl` in backend/.env?
2. Model pulled? `ollama list`
3. Backend restarted?

**Logs should show:**
```
Using vision model: ollama/qwen2-vl
```

### Ollama fails, Gemini works (good!)

This means the fallback is working correctly:
```
Ollama connection failed → Falling back to Gemini
```

**To fix Ollama:**
- Check Ollama is running
- Verify model is pulled
- Check OLLAMA_API_BASE URL

## Advanced: Multiple Models

You can specify different quantization levels:

```env
# Faster (smaller model):
BROWSER_VISION_MODEL=ollama/qwen2-vl:q4_0

# Better accuracy (larger model):
BROWSER_VISION_MODEL=ollama/qwen2-vl:latest

# Tiny and fast:
BROWSER_VISION_MODEL=ollama/llava:7b
```

## Summary

**What you need in backend/.env:**

```env
BROWSER_VISION_MODEL=ollama/qwen2-vl
OLLAMA_API_BASE=http://localhost:11434
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=your-key-as-fallback
```

**What you get:**

- ✅ FREE browser vision (Ollama qwen2-vl)
- ✅ 100% local and private
- ✅ No API costs or limits
- ✅ Gemini as reliable backup
- ✅ Triple fallback system

**Setup time:** 3 minutes  
**Monthly cost:** $0 (was potentially $10-30 with Gemini)  
**Privacy:** 100% local (was cloud-based)  

---

## Next Steps After Configuration

1. ✅ Add config lines to backend/.env
2. ✅ Pull Ollama vision model: `ollama pull qwen2-vl`
3. ✅ Restart backend: `python start.py`
4. ✅ Test: "Navigate to example.com and describe it"
5. ✅ Verify logs show Ollama being used

**Enjoy free, private browser automation!** 🦙🔍✨
