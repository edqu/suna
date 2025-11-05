# Anthropic Authentication Error - Root Cause & Fix

## Why This Error Occurs

The error `Authentication failed: Please check your API credentials. litellm.AuthenticationError: AnthropicException` happens because:

### 1. **Default Model Selection Logic** (Line 6 in `backend/core/ai_models/registry.py`)
```python
SHOULD_USE_ANTHROPIC = config.ENV_MODE == EnvMode.LOCAL and bool(config.ANTHROPIC_API_KEY)
```

When you're in **LOCAL** mode:
- The system checks if `ANTHROPIC_API_KEY` exists
- If it exists → uses Claude/Anthropic models as defaults
- If it doesn't exist → uses AWS Bedrock models

### 2. **The Problem**
Your `backend/.env` file likely has:
- ✅ `ENV_MODE=local` (or `LOCAL`)
- ❌ Missing or invalid `ANTHROPIC_API_KEY`

This causes a conflict:
1. System detects LOCAL mode
2. System tries to use Anthropic models by default
3. But ANTHROPIC_API_KEY is missing/invalid
4. LiteLLM throws authentication error

## How to Fix

### **Option A: Add Anthropic API Key** (Recommended for LOCAL development)

1. Get an Anthropic API key from https://console.anthropic.com/

2. Add to `backend/.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

3. Restart the backend

### **Option B: Use Alternative Provider**

If you don't have Anthropic API key, use another provider:

**Using OpenAI:**
```env
# In backend/.env
OPENAI_API_KEY=sk-proj-your-openai-key
```

Then in the frontend, select a GPT model instead of Claude.

**Using AWS Bedrock:**
```env
# In backend/.env
ENV_MODE=staging  # or production (not local)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION_NAME=us-west-2
```

### **Option C: Force a Specific Model**

Override the default by explicitly selecting a non-Anthropic model in your agent configuration or when starting a conversation.

## The Fix Location

The problematic logic is in `backend/core/ai_models/registry.py` lines 6-14:

```python
# Current behavior - uses Anthropic in LOCAL mode IF key exists
SHOULD_USE_ANTHROPIC = config.ENV_MODE == EnvMode.LOCAL and bool(config.ANTHROPIC_API_KEY)

if SHOULD_USE_ANTHROPIC:
    FREE_MODEL_ID = "anthropic/claude-haiku-4-5"
    PREMIUM_MODEL_ID = "anthropic/claude-haiku-4-5"
else:  
    FREE_MODEL_ID = "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/heol2zyy5v48"
    PREMIUM_MODEL_ID = "bedrock/converse/arn:aws:bedrock:us-west-2:935064898258:application-inference-profile/heol2zyy5v48"
```

## Quick Diagnosis

Check your backend startup logs for:
```
🌐 Current ENV_MODE: local (or LOCAL)
```

If you see LOCAL mode but don't have ANTHROPIC_API_KEY set, you'll get this error.

## Permanent Solution

Either:
1. ✅ Set `ANTHROPIC_API_KEY` in `.env` (recommended for local dev)
2. ✅ Change `ENV_MODE=staging` or `production` in `.env` (will use Bedrock)
3. ✅ Add `OPENAI_API_KEY` and select GPT models in UI

After changing `.env`, **restart the backend**.
