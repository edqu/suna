# Ollama-First with Gemini Fallback Configuration

## What This Does

Uses **FREE Ollama vision models** (like Qwen2-VL) for browser automation by default, only falling back to Gemini if Ollama fails.

## Why This Is Better

| Aspect | Ollama (Default) | Gemini (Fallback) |
|--------|-----------------|-------------------|
| **Cost** | $0 - Completely FREE | API costs (free tier: 1500/day) |
| **Privacy** | 100% Local - Never leaves your machine | Sent to Google servers |
| **Speed** | Fast with GPU | Very fast (cloud) |
| **Setup** | Requires Ollama install | Just API key |
| **Limits** | None (local) | 15 requests/min |

**Bottom Line:** Use free local Ollama by default, only use Gemini when necessary!

## Setup (3 Minutes)

### Step 1: Install Ollama Vision Model

```bash
# Install Ollama (if not already): https://ollama.com/download

# Pull a vision model (choose one):
ollama pull qwen2-vl        # Recommended - fast and accurate
# or
ollama pull qwen3-vl        # Newer version
# or
ollama pull llava           # Alternative vision model
```

**Verify:**
```bash
ollama list
# Should show your vision model
```

### Step 2: Configure Backend

Edit `backend/.env`:

```env
# ============================================================================
# OLLAMA-FIRST CONFIGURATION (FREE, LOCAL, PRIVATE)
# ============================================================================

# Use Ollama vision model for browser (FREE!)
BROWSER_VISION_MODEL=ollama/qwen2-vl

# Ollama server URL
OLLAMA_API_BASE=http://localhost:11434

# Enable browser-first mode
BROWSER_DEFAULT_FOR_WEB_SEARCH=true

# OPTIONAL: Gemini as fallback (only used if Ollama fails)
GEMINI_API_KEY=your-gemini-key-here

# ============================================================================
# HOW IT WORKS:
# 1. Browser tries Ollama vision model first (qwen2-vl) - FREE!
# 2. If Ollama fails/unavailable, falls back to Gemini
# 3. If both fail, falls back to API search (DuckDuckGo)
# ============================================================================
```

### Step 3: Restart Backend

```bash
python start.py
```

**Look for:**
```
Using vision model: ollama/qwen2-vl
Using Ollama vision model at http://localhost:11434
✅ Stagehand API server initialized successfully
```

### Step 4: Test It

```
Navigate to https://example.com and tell me what you see
```

**Expected:**
- Browser opens
- Uses **Ollama qwen2-vl** for vision (FREE!)
- No Gemini API calls
- Completely local and private

## Fallback Behavior

### Scenario 1: Ollama Works (Normal)

```
User: "Navigate to GitHub"
  ↓
Browser uses: ollama/qwen2-vl for vision
  ↓
Cost: $0
Privacy: 100% local
  ↓
Success! ✅
```

### Scenario 2: Ollama Unavailable (Fallback)

```
User: "Navigate to GitHub"
  ↓
Try: ollama/qwen2-vl
  ↓
Error: Ollama not running
  ↓
Fallback to: google/gemini-2.5-pro
  ↓
Uses Gemini API key
  ↓
Still works! ✅
```

### Scenario 3: Both Fail (Double Fallback)

```
User: "Search for X"
  ↓
Try: ollama/qwen2-vl (browser)
  ↓
Failed
  ↓
Try: google/gemini-2.5-pro (browser)
  ↓
Failed (no API key)
  ↓
Fallback to: web_search (DuckDuckGo API)
  ↓
Still gets results! ✅
```

## Configuration Options

### Option A: Ollama Only (No Gemini)

```env
BROWSER_VISION_MODEL=ollama/qwen2-vl
OLLAMA_API_BASE=http://localhost:11434
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
# Don't set GEMINI_API_KEY
```

**Result:** 100% local, falls back to API search if browser fails

### Option B: Ollama-First with Gemini Fallback (Recommended)

```env
BROWSER_VISION_MODEL=ollama/qwen2-vl
OLLAMA_API_BASE=http://localhost:11434
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=your-key-here
```

**Result:** Tries Ollama first, uses Gemini if Ollama fails

### Option C: Gemini Only (Current Default)

```env
# BROWSER_VISION_MODEL not set (uses default)
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=your-key-here
```

**Result:** Always uses Gemini (what you had before)

## Available Ollama Vision Models

### Recommended

**Qwen2-VL** (`ollama/qwen2-vl`)
- ✅ Best accuracy
- ✅ Fast with GPU
- ✅ Good tool calling
- Size: ~4GB

**Qwen3-VL** (`ollama/qwen3-vl`)  
- ✅ Newer version
- ✅ Improved vision
- ✅ Better understanding
- Size: ~5GB

### Alternatives

**LLaVA** (`ollama/llava`)
- ✅ Smaller size (~3GB)
- ✅ Fast inference
- ⚠️ Less accurate than Qwen
- Good for simple tasks

**MoonDream** (`ollama/moondream`)
- ✅ Tiny size (~1.6GB)
- ✅ Very fast
- ⚠️ Basic vision only
- Good for quick checks

## Performance Comparison

| Model | Size | Speed (GPU) | Accuracy | Cost |
|-------|------|-------------|----------|------|
| **ollama/qwen2-vl** | 4GB | Fast | Excellent | $0 |
| **ollama/llava** | 3GB | Fast | Good | $0 |
| **google/gemini-2.5-pro** | N/A | Very Fast | Excellent | API costs |

## Testing

### Test 1: Verify Ollama Vision Model

```bash
ollama pull qwen2-vl
ollama list
# Should show qwen2-vl
```

### Test 2: Test Ollama Vision

```bash
# Try Ollama directly:
ollama run qwen2-vl "Describe this: https://example.com/image.jpg"
```

### Test 3: Test in Browser Tool

```
Navigate to https://github.com and describe what you see
```

**Check logs:**
```
Using vision model: ollama/qwen2-vl
Using Ollama vision model at http://localhost:11434
```

### Test 4: Verify Fallback

```bash
# Stop Ollama temporarily:
# Close Ollama app or: killall ollama

# Try browser command in Suna
# Should fall back to Gemini
```

**Check logs:**
```
Error connecting to Ollama
Falling back to google/gemini-2.5-pro
```

## Cost Savings

### Before (Gemini Only)

**Typical daily usage:**
- 50 browser actions/day
- 100 Gemini API requests
- Within free tier, but tracking needed

### After (Ollama-First)

**Typical daily usage:**
- 50 browser actions/day
- 0 Gemini API requests (all handled by Ollama)
- $0 cost, no limits, no tracking!

**Savings:** 100% of Gemini API costs eliminated

## Privacy Benefits

### With Gemini

```
Your search → Gemini API (Google servers) → Result
❌ Google sees your searches
❌ Data sent to cloud
❌ Requires internet
```

### With Ollama

```
Your search → Ollama (Your machine) → Result
✅ Completely private
✅ No data leaves your computer
✅ Works offline
```

## Troubleshooting

### Ollama model not being used

**Check logs for:**
```
Using vision model: ollama/qwen2-vl
```

**If not there:**
1. Verify `BROWSER_VISION_MODEL=ollama/qwen2-vl` in .env
2. Check Ollama is running: `ollama list`
3. Restart backend

### Ollama connection failed

**Error:** `Failed to connect to Ollama`

**Solutions:**
1. Check Ollama is running
2. Verify `OLLAMA_API_BASE=http://localhost:11434`
3. Test: `curl http://localhost:11434/api/tags`

**Fallback works:** Should automatically use Gemini

### Browser still uses Gemini

**Possible causes:**
1. `BROWSER_VISION_MODEL` not set
2. Ollama model not pulled
3. Ollama not running

**Check:**
```bash
ollama ps
# Should show model loaded
```

### Vision model not working

**Try different model:**
```env
BROWSER_VISION_MODEL=ollama/llava
```

Or test Ollama vision directly:
```bash
ollama run qwen2-vl "Test vision"
```

## Advanced Configuration

### Use Different Model for Browser vs Chat

```env
# Browser vision model (Ollama)
BROWSER_VISION_MODEL=ollama/qwen2-vl

# Chat model (can be different)
# User selects in UI: ollama/qwen2.5-coder
```

**Result:** Ollama vision for browser, Ollama text for chat - 100% local!

### Optimize for Speed

```bash
# Pull quantized model (smaller, faster)
ollama pull qwen2-vl:q4_0

# Configure:
BROWSER_VISION_MODEL=ollama/qwen2-vl:q4_0
```

### Maximize Accuracy

```bash
# Pull full precision model
ollama pull qwen2-vl:latest

# Or use Qwen3-VL:
ollama pull qwen3-vl:latest

# Configure:
BROWSER_VISION_MODEL=ollama/qwen3-vl
```

## Monitoring

### Check Which Model Is Being Used

**Logs will show:**

**Ollama:**
```
Using vision model: ollama/qwen2-vl
Using Ollama vision model at http://localhost:11434
[stagehand] Using model: ollama/qwen2-vl
```

**Gemini (Fallback):**
```
Ollama connection failed
Using vision model: google/gemini-2.5-pro
[stagehand] Using model: google/gemini-2.5-pro
```

### Count API Calls

With Ollama-first:
- Gemini calls should be **0 or very few**
- Only when Ollama unavailable
- Saves API quota for emergencies

## Summary

**What you configured:**
```env
BROWSER_VISION_MODEL=ollama/qwen2-vl
OLLAMA_API_BASE=http://localhost:11434
BROWSER_DEFAULT_FOR_WEB_SEARCH=true
GEMINI_API_KEY=your-key-as-fallback
```

**What you get:**
- ✅ FREE browser vision (Ollama)
- ✅ 100% private (local)
- ✅ No API limits
- ✅ Gemini as backup
- ✅ Triple fallback: Ollama → Gemini → API search

**Cost:** $0/month (vs potential Gemini costs)  
**Privacy:** 100% local (vs cloud processing)  
**Reliability:** Triple fallback (very reliable)  

## Quick Start

```bash
# 1. Install Ollama vision model
ollama pull qwen2-vl

# 2. Add to backend/.env:
BROWSER_VISION_MODEL=ollama/qwen2-vl

# 3. Restart backend
python start.py

# 4. Test
# "Navigate to example.com and describe it"

# Should use Ollama (free!) not Gemini ✅
```

**Enjoy free, private browser automation!** 🦙🔍
