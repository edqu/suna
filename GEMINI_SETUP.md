# Google Gemini Setup - Default Model Configuration

## What's Been Set Up

Google Gemini 2.0 Flash is now the **default model** for your Suna installation! 🎉

### Why Gemini 2.0 Flash?

✅ **FREE** during experimental phase ($0/M tokens)
✅ **FAST** - Excellent performance
✅ **CAPABLE** - 1M token context window
✅ **Function calling** - Full tool support
✅ **Vision** - Can process images
✅ **No credit card required** - Get started immediately

## How to Enable

### Step 1: Get Your Gemini API Key

1. Go to: **https://aistudio.google.com/apikey**
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Add to Your .env File

Open `backend/.env` and add:

```env
GEMINI_API_KEY=AIzaSyYOUR-ACTUAL-KEY-HERE
```

### Step 3: Restart Backend

After adding the key, restart your backend server.

You'll see this log message:
```
🔑 Registering Google Gemini models (gemini-2.0-flash-exp)
🤖 Using Google Gemini as default model (FREE, fast, capable)
```

## Available Gemini Models

Once you add `GEMINI_API_KEY`, these models will be available:

### 1. **Gemini 2.0 Flash** (DEFAULT) ⭐
- **Model ID**: `gemini/gemini-2.0-flash-exp`
- **Aliases**: `gemini-2.0-flash`, `Gemini 2.0 Flash`
- **Context**: 1M tokens
- **Cost**: FREE (experimental)
- **Best for**: Everything! Fast, capable, and free

### 2. **Gemini 1.5 Flash**
- **Model ID**: `gemini/gemini-1.5-flash`
- **Context**: 1M tokens
- **Cost**: $0.075/M input, $0.30/M output
- **Best for**: Production workloads needing stability

### 3. **Gemini 1.5 Pro**
- **Model ID**: `gemini/gemini-1.5-pro`
- **Context**: 2M tokens (largest!)
- **Cost**: $1.25/M input, $5.00/M output
- **Best for**: Complex tasks with massive context

## Model Priority System

The system automatically selects the default model based on available API keys:

**Priority Order:**
1. 🥇 **Gemini** (if `GEMINI_API_KEY` is set) - FREE & FAST
2. 🥈 **Anthropic** (if `ANTHROPIC_API_KEY` is set + LOCAL mode)
3. 🥉 **AWS Bedrock** (fallback if no other keys)

This means:
- Add `GEMINI_API_KEY` → Gemini becomes default ✅
- No Gemini key → Falls back to Anthropic (if in LOCAL mode)
- No keys → Uses AWS Bedrock (requires AWS credentials)

## What Changed in the Code

### 1. Model Registry (`backend/core/ai_models/registry.py`)

**Lines 5-10**: Added Gemini API key validation
```python
SHOULD_USE_GEMINI = (
    bool(config.GEMINI_API_KEY) and 
    len(config.GEMINI_API_KEY) > 10
)
```

**Lines 14-24**: Updated default model selection with Gemini priority
```python
if SHOULD_USE_GEMINI:
    FREE_MODEL_ID = "gemini/gemini-2.0-flash-exp"
    PREMIUM_MODEL_ID = "gemini/gemini-2.0-flash-exp"
```

**Lines 244-318**: Registered 3 Gemini models with full configuration

### 2. Environment Template (`backend/.env.example`)

Updated to show Gemini as the recommended provider with setup instructions.

## Testing

After setup, test with a simple message:
```
User: "Hello! What model are you using?"
Agent: "I'm using Gemini 2.0 Flash..."
```

Check the backend logs for:
```
🤖 Using Google Gemini as default model (FREE, fast, capable)
Making LLM API call to model: gemini/gemini-2.0-flash-exp
```

## Troubleshooting

**Error: "Authentication failed: Google AI Studio API Key not found"**
- Make sure `GEMINI_API_KEY` is in your `.env` file
- Key must start with `AIza`
- Restart backend after adding the key

**Not seeing Gemini in model selector?**
- Check backend logs for "🔑 Registering Google Gemini models"
- Verify API key length > 10 characters
- Make sure you restarted backend

**Want to use a different default?**
- Remove `GEMINI_API_KEY` from `.env` to use next priority (Anthropic/Bedrock)
- Or select a different model in the UI model selector

## Switching Back to Anthropic/Bedrock

If you want to use Anthropic or Bedrock as default instead:

**Option 1**: Remove Gemini key from `.env`
```env
# GEMINI_API_KEY=  # Commented out
ANTHROPIC_API_KEY=sk-ant-...  # This becomes default
```

**Option 2**: Select model manually in UI
- Use the model selector in the frontend
- Your selection overrides the default

## Cost Comparison

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Gemini 2.0 Flash | **$0.00** | **$0.00** |
| Gemini 1.5 Flash | $0.075 | $0.30 |
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Claude Sonnet 4 | $3.00 | $15.00 |

**Gemini 2.0 Flash is FREE** during the experimental phase, making it perfect for development and testing! 🎉
