# Model API Key Mismatch - Why It Happens and How to Fix

## The Problem

You're getting `Authentication failed: AnthropicException` even though you might have API keys configured. This happens because **the model being used doesn't match the API keys you have available**.

## How LiteLLM Selects API Keys

LiteLLM (the library used for AI calls) automatically selects API keys based on the **model prefix**:

| Model Prefix | API Key Needed | Example Model |
|--------------|----------------|---------------|
| `anthropic/` or `claude-` | `ANTHROPIC_API_KEY` | `anthropic/claude-haiku-4-5` |
| `openai/` or `gpt-` | `OPENAI_API_KEY` | `openai/gpt-4o` |
| `groq/` | `GROQ_API_KEY` | `groq/llama-3.3-70b` |
| `gemini/` | `GEMINI_API_KEY` | `gemini/gemini-2.0-flash-exp` |
| `bedrock/` | `AWS_*` credentials | `bedrock/converse/arn:...` |

## Why Your Model Selection is Wrong

Check `backend/core/ai_models/registry.py` lines 6-14:

```python
SHOULD_USE_ANTHROPIC = config.ENV_MODE == EnvMode.LOCAL and bool(config.ANTHROPIC_API_KEY)

if SHOULD_USE_ANTHROPIC:
    FREE_MODEL_ID = "anthropic/claude-haiku-4-5"
    PREMIUM_MODEL_ID = "anthropic/claude-haiku-4-5"
else:  
    FREE_MODEL_ID = "bedrock/converse/arn:aws:bedrock:us-west-2:..."
    PREMIUM_MODEL_ID = "bedrock/converse/arn:aws:bedrock:us-west-2:..."
```

**What's happening:**
1. System is in `ENV_MODE=LOCAL`
2. System checks for `ANTHROPIC_API_KEY`
3. If found OR if the check is wrong → defaults to Claude models
4. But if the key is invalid/expired → authentication fails

## How to Fix

### Solution 1: Add the Missing Anthropic API Key

1. Go to https://console.anthropic.com/
2. Get your API key
3. Add to `backend/.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
   ```
4. Restart backend

### Solution 2: Force Different Model Selection

**Edit `backend/core/ai_models/registry.py` line 6:**

```python
# OLD (automatically picks based on env):
SHOULD_USE_ANTHROPIC = config.ENV_MODE == EnvMode.LOCAL and bool(config.ANTHROPIC_API_KEY)

# NEW (force to NOT use Anthropic):
SHOULD_USE_ANTHROPIC = False

# OR (only use if key is VALID):
SHOULD_USE_ANTHROPIC = config.ENV_MODE == EnvMode.LOCAL and bool(config.ANTHROPIC_API_KEY) and len(config.ANTHROPIC_API_KEY) > 20
```

Then restart backend.

### Solution 3: Use OpenAI Models Instead

1. Add to `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-proj-YOUR-OPENAI-KEY
   ```

2. In frontend, when starting a conversation, select a GPT model instead of Claude

3. Or set a different default model in your agent configuration

### Solution 4: Check Your .env File

Open `backend/.env` and verify:

```env
# Is this set?
ENV_MODE=local  # or LOCAL

# Do you have this? Is it valid?
ANTHROPIC_API_KEY=sk-ant-api03-...

# If you see something like this, it's WRONG:
ANTHROPIC_API_KEY=your-key-here  # This is a placeholder!
ANTHROPIC_API_KEY=  # This is empty!
```

## Quick Diagnosis Script

Run this to see what's configured:

```python
# In backend directory
python -c "
from core.utils.config import config
print(f'ENV_MODE: {config.ENV_MODE.value}')
print(f'ANTHROPIC_API_KEY exists: {bool(config.ANTHROPIC_API_KEY)}')
print(f'ANTHROPIC_API_KEY length: {len(config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else 0}')
print(f'OPENAI_API_KEY exists: {bool(config.OPENAI_API_KEY)}')
"
```

Expected output if working:
```
ENV_MODE: local
ANTHROPIC_API_KEY exists: True
ANTHROPIC_API_KEY length: 108  # Should be ~100+ characters
OPENAI_API_KEY exists: True
```

## Root Cause

The system defaults to Anthropic models when in LOCAL mode, but the ANTHROPIC_API_KEY is either:
- Missing from .env
- Set to a placeholder value like "your-key-here"
- Expired or invalid
- Not loaded properly (need to restart backend)

**Fix it by either:**
1. ✅ Adding a valid Anthropic API key
2. ✅ Forcing the system to use a different provider (edit registry.py)
3. ✅ Selecting a different model in the UI
4. ✅ Changing ENV_MODE to staging/production (uses Bedrock instead)
