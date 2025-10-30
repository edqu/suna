# Model Selection Guide

This guide explains how to use model selection in Suna, allowing you to choose which AI model your agents use.

## Overview

Suna now supports selecting specific AI models when creating or updating agents. You can:
- List all available models based on your subscription tier
- Create agents with a specific model
- Update an agent's model
- Validate model availability
- View models grouped by provider (Anthropic, OpenAI, Ollama, etc.)

## API Endpoints

### 1. List Available Models

**GET** `/api/models`

Returns all models available to the current user based on their subscription tier.

**Example Response:**
```json
{
  "models": [
    {
      "id": "anthropic/claude-haiku-4-5",
      "name": "Haiku 4.5",
      "provider": "anthropic",
      "context_window": 200000,
      "max_output_tokens": null,
      "capabilities": ["chat", "function_calling", "vision"],
      "pricing": {
        "input_per_million": 1.0,
        "output_per_million": 5.0
      },
      "enabled": true,
      "beta": false,
      "tier_availability": ["paid"],
      "priority": 102,
      "recommended": true
    },
    {
      "id": "ollama/llama3.3",
      "name": "Llama 3.3 70B",
      "provider": "ollama",
      "context_window": 128000,
      "capabilities": ["chat", "function_calling"],
      "pricing": {
        "input_per_million": 0.0,
        "output_per_million": 0.0
      },
      "enabled": true,
      "tier_availability": ["free", "paid"]
    }
  ],
  "default_model": "anthropic/claude-haiku-4-5",
  "user_tier": "paid"
}
```

### 2. List Models by Provider

**GET** `/api/models/by-provider`

Returns models grouped by provider for easier UI display.

**Example Response:**
```json
{
  "providers": {
    "anthropic": [
      {
        "id": "anthropic/claude-haiku-4-5",
        "name": "Haiku 4.5",
        ...
      }
    ],
    "ollama": [
      {
        "id": "ollama/llama3.3",
        "name": "Llama 3.3 70B",
        ...
      },
      {
        "id": "ollama/qwen2.5-coder",
        "name": "Qwen 2.5 Coder",
        ...
      }
    ]
  },
  "default_model": "anthropic/claude-haiku-4-5",
  "user_tier": "paid"
}
```

### 3. Get Model Info

**GET** `/api/models/{model_id}`

Get detailed information about a specific model.

**Example:**
```bash
GET /api/models/ollama/llama3.3
```

### 4. Validate Model

**POST** `/api/models/validate`

Validate that a model is available to the current user.

**Request:**
```json
{
  "model_id": "ollama/llama3.3"
}
```

**Response:**
```json
{
  "is_valid": true,
  "error_message": null,
  "model_info": {
    "id": "ollama/llama3.3",
    "name": "Llama 3.3 70B",
    ...
  }
}
```

## Agent Creation with Model Selection

### Create Agent with Specific Model

**POST** `/api/agents`

**Request:**
```json
{
  "name": "My Code Assistant",
  "model": "ollama/qwen2.5-coder",
  "system_prompt": "You are a helpful coding assistant",
  "agentpress_tools": {},
  "configured_mcps": [],
  "custom_mcps": []
}
```

If `model` is omitted, the default model for your subscription tier is used.

### Update Agent Model

**PUT** `/api/agents/{agent_id}`

**Request:**
```json
{
  "model": "ollama/llama3.3"
}
```

## Model Selection by Tier

### Free Tier
In local mode (`ENV_MODE=local`), all enabled models are available including:
- Ollama models (free, runs locally)
- Any other models configured in the system

### Paid Tier
Paid users have access to premium models like:
- Claude Haiku 4.5
- Claude Sonnet 4
- Claude Sonnet 4.5
- Plus all free tier models

## Using Ollama Models

Ollama models are free and run locally. To use them:

1. **Install Ollama** (see [OLLAMA_SETUP.md](./OLLAMA_SETUP.md))
   ```bash
   # Download from https://ollama.com
   ```

2. **Pull Models**
   ```bash
   ollama pull llama3.3
   ollama pull qwen2.5-coder
   ollama pull deepseek-r1:70b
   ```

3. **Set Environment**
   ```bash
   ENV_MODE=local
   OLLAMA_API_BASE=http://localhost:11434
   ```

4. **Create Agent with Ollama**
   ```bash
   curl -X POST http://localhost:8000/api/agents \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "name": "Local Code Assistant",
       "model": "ollama/qwen2.5-coder"
     }'
   ```

## Model Aliases

You can use model aliases for convenience:

| Alias | Full ID |
|-------|---------|
| `llama3.3` | `ollama/llama3.3` |
| `qwen2.5-coder` | `ollama/qwen2.5-coder` |
| `deepseek-r1:70b` | `ollama/deepseek-r1:70b` |

**Example:**
```json
{
  "name": "My Agent",
  "model": "llama3.3"  // Resolves to "ollama/llama3.3"
}
```

## Frontend Integration Example

### Fetch Available Models

```javascript
async function getAvailableModels() {
  const response = await fetch('/api/models', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data.models;
}
```

### Create Agent with Selected Model

```javascript
async function createAgent(name, modelId) {
  const response = await fetch('/api/agents', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: name,
      model: modelId
    })
  });
  
  return await response.json();
}
```

### Display Models by Provider

```javascript
async function displayModelsByProvider() {
  const response = await fetch('/api/models/by-provider', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  // data.providers = {
  //   "anthropic": [...],
  //   "ollama": [...],
  //   ...
  // }
  
  Object.entries(data.providers).forEach(([provider, models]) => {
    console.log(`${provider}:`, models);
  });
}
```

## Model Selection Best Practices

1. **Show Default Model**: Display the user's default model prominently
2. **Group by Provider**: Use the `/models/by-provider` endpoint for better UX
3. **Indicate Costs**: Show pricing information for paid models
4. **Highlight Free Options**: Emphasize Ollama models as free alternatives
5. **Validate Selection**: Use `/models/validate` before creating agents
6. **Filter by Capability**: Show relevant models based on agent purpose
   - Coding tasks → Qwen 2.5 Coder
   - General tasks → Llama 3.3
   - Complex reasoning → DeepSeek R1

## Testing Model Selection

### Test Available Models
```bash
curl -X GET http://localhost:8000/api/models \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Agent Creation with Model
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "model": "ollama/llama3.3"
  }'
```

### Test Model Validation
```bash
curl -X POST http://localhost:8000/api/models/validate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "ollama/llama3.3"
  }'
```

## Error Handling

### Invalid Model
```json
{
  "detail": "Invalid model selection: Model 'invalid-model' not found"
}
```

### Tier Restriction
```json
{
  "detail": "Invalid model selection: Model 'anthropic/claude-sonnet-4-5' is not available for your subscription tier"
}
```

### Model Disabled
```json
{
  "detail": "Invalid model selection: Model 'disabled-model' is currently disabled"
}
```

## Files Modified/Created

### New Files
- `core/utils/model_selector.py` - Model selection utility
- `core/models_api.py` - Models API endpoints
- `MODEL_SELECTION_GUIDE.md` - This guide

### Modified Files
- `core/api_models/agents.py` - Added `model` field to `AgentCreateRequest`
- `core/agent_crud.py` - Added model validation on agent creation
- `api.py` - Registered models API router

## Next Steps

1. **Frontend Integration**: Add model selection dropdown to agent creation UI
2. **Model Recommendations**: Suggest appropriate models based on agent purpose
3. **Usage Analytics**: Track which models are most popular
4. **Cost Estimation**: Show estimated costs for different model choices
