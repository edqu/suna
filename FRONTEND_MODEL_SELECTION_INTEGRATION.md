# Frontend Model Selection Integration - Complete Guide

## ✅ Integration Complete

The frontend is now fully integrated with the new model selection API! Here's everything you need to know.

---

## What Was Updated

### 1. API Client (`frontend/src/lib/api.ts`)

Added new API functions to interact with the model selection endpoints:

```typescript
// Get all available models for current user
export const getAvailableModels = async (): Promise<AvailableModelsResponse>

// Get models grouped by provider (ollama, anthropic, etc.)
export const getModelsByProvider = async (): Promise<{
  providers: Record<string, Model[]>;
  default_model: string;
  user_tier: string;
}>

// Validate a model is available to the user
export const validateModel = async (modelId: string): Promise<{
  is_valid: boolean;
  error_message?: string;
  model_info?: Model;
}>

// Get detailed information about a specific model
export const getModelInfo = async (modelId: string): Promise<Model>
```

### 2. Updated Endpoint

Changed from `/billing/available-models` → `/models`

The new endpoint provides:
- ✅ All models including Ollama
- ✅ Tier-based filtering
- ✅ Provider grouping
- ✅ Model validation

---

## How It Works

### Current Flow

```
User Opens Agent Settings
        ↓
Frontend calls GET /api/models
        ↓
Backend returns available models
(filtered by user's subscription tier)
        ↓
Frontend displays in AgentModelSelector
        ↓
User selects model (e.g., "ollama/llama3.3")
        ↓
Frontend validates selection
        ↓
Agent created/updated with selected model
```

### Model Selector Component

The existing `AgentModelSelector` component (`frontend/src/components/agents/config/model-selector.tsx`) already:

✅ Fetches models using `useModelSelection()` hook  
✅ Displays models with pricing  
✅ Groups free vs premium models  
✅ Handles subscription paywalls  
✅ Supports custom models (for local mode)  
✅ Shows model capabilities and context windows

**The component automatically works with the new API!**

---

## What Models Show Up

### Local Mode (`ENV_MODE=local`)
**All enabled models**, including:
- `ollama/llama3.3` - Llama 3.3 70B (FREE)
- `ollama/qwen2.5-coder` - Qwen 2.5 Coder (FREE)
- `ollama/deepseek-r1:70b` - DeepSeek R1 70B (FREE)
- `anthropic/claude-haiku-4-5` - Claude Haiku 4.5
- `anthropic/claude-sonnet-4` - Claude Sonnet 4
- `anthropic/claude-sonnet-4-5` - Claude Sonnet 4.5

### Free Tier
- Ollama models only (if installed)

### Paid Tier
- All free tier models
- Premium Anthropic models

---

## User Experience

### Creating an Agent

1. User opens "New Agent" dialog
2. Model selector shows available models
3. Free models appear first (Ollama - $0.00)
4. Premium models appear below with Crown icon
5. User selects model
6. Agent created with that model

### Updating an Agent

1. User opens agent settings
2. Current model is pre-selected
3. User can change to any available model
4. Changes save immediately

### Model Display

```
┌─────────────────────────────────────┐
│ All Models                  [+ Add] │
├─────────────────────────────────────┤
│ Search models...                    │
├─────────────────────────────────────┤
│ Model               Input   Output  │
├─────────────────────────────────────┤
│ 🦙 Llama 3.3 70B     $0.00   $0.00 │
│ 🤖 Qwen 2.5 Coder    $0.00   $0.00 │
│ 🧠 DeepSeek R1       $0.00   $0.00 │
├─────────────────────────────────────┤
│ 👑 Premium Models                   │
├─────────────────────────────────────┤
│ 🤖 Haiku 4.5         $1.00   $5.00 │
│ 🤖 Sonnet 4          $3.00  $15.00 │
│ 🤖 Sonnet 4.5        $3.00  $15.00 │
└─────────────────────────────────────┘
        * Prices per 1M tokens
```

---

## Agent Creation API

### Without Model (uses default)

```typescript
const response = await fetch(`${API_URL}/agents`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: 'My Agent'
  })
});
```

Backend automatically assigns default model based on user's tier.

### With Model

```typescript
const response = await fetch(`${API_URL}/agents`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: 'My Agent',
    model: 'ollama/llama3.3' // Explicitly choose model
  })
});
```

Backend validates the model is available to the user.

---

## Testing the Integration

### 1. Check Models Load

Open browser console and run:

```javascript
// Should show available models
const response = await fetch('/api/models', {
  headers: {
    'Authorization': `Bearer ${yourToken}`
  }
});
const data = await response.json();
console.log('Available models:', data.models);
```

### 2. Create Agent with Model

```javascript
// Create agent with Ollama model
const response = await fetch('/api/agents', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${yourToken}`
  },
  body: JSON.stringify({
    name: 'Test Agent',
    model: 'ollama/llama3.3'
  })
});
const agent = await response.json();
console.log('Created agent:', agent);
```

### 3. Verify in UI

1. Go to agent settings
2. Open model selector dropdown
3. Should see all available models
4. Free Ollama models should show $0.00
5. Premium models should show pricing

---

## Troubleshooting

### Models Not Showing Up

**Problem:** No models in dropdown  
**Solution:** Check that API endpoint is accessible:
```bash
curl http://localhost:8000/api/models \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ollama Models Missing

**Problem:** Ollama models don't appear  
**Solution:** Ensure:
1. `ENV_MODE=local` in .env
2. Ollama is running: `curl http://localhost:11434/api/tags`
3. Models are pulled: `ollama list`

### Invalid Model Error

**Problem:** "Model not available for your tier"  
**Solution:** User's subscription doesn't allow that model
- Upgrade to paid tier for premium models
- Use free Ollama models instead

### Model Validation Fails

**Problem:** Can't create agent with specific model  
**Solution:** Validate model first:
```javascript
const validation = await fetch('/api/models/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    model_id: 'ollama/llama3.3'
  })
});
const result = await validation.json();
console.log('Valid?', result.is_valid);
```

---

## Component Integration Examples

### Using in a Custom Component

```typescript
import { useModelSelection } from '@/hooks/use-model-selection';
import { AgentModelSelector } from '@/components/agents/config/model-selector';

export function MyCustomAgentForm() {
  const [selectedModel, setSelectedModel] = useState('');
  
  return (
    <div>
      <label>Choose Model:</label>
      <AgentModelSelector
        value={selectedModel}
        onChange={setSelectedModel}
      />
    </div>
  );
}
```

### Direct API Usage

```typescript
import { getAvailableModels, validateModel } from '@/lib/api';

// Fetch models
const modelsData = await getAvailableModels();
console.log('Available:', modelsData.models);
console.log('User tier:', modelsData.subscription_tier);

// Validate a model
const validation = await validateModel('ollama/llama3.3');
if (validation.is_valid) {
  console.log('Model is valid!', validation.model_info);
} else {
  console.error('Invalid:', validation.error_message);
}
```

---

## Files Modified

### Frontend
✅ `frontend/src/lib/api.ts` - Updated API functions  
✅ `frontend/src/hooks/use-model-selection.ts` - Already compatible  
✅ `frontend/src/components/agents/config/model-selector.tsx` - Already compatible

### Backend (for reference)
✅ `backend/core/models_api.py` - New models API  
✅ `backend/core/utils/model_selector.py` - Model selection utility  
✅ `backend/core/api_models/agents.py` - Added model field  
✅ `backend/core/agent_crud.py` - Added model validation  

---

## Next Steps for UI Improvements

### 1. Model Recommendations
Show recommended models based on agent purpose:
```typescript
// For coding agents
if (agentPurpose === 'coding') {
  recommendedModel = 'ollama/qwen2.5-coder';
}
```

### 2. Cost Estimation
Show estimated monthly costs:
```typescript
const monthlyCost = calculateMonthlyCost(
  selectedModel,
  estimatedTokenUsage
);
```

### 3. Model Comparison
Add side-by-side comparison:
```tsx
<ModelComparison
  models={['ollama/llama3.3', 'anthropic/claude-haiku-4-5']}
/>
```

### 4. Usage Analytics
Track which models are most popular:
```typescript
posthog.capture('model_selected', {
  model_id: selectedModel,
  tier: userTier
});
```

---

## API Response Examples

### GET /api/models

```json
{
  "models": [
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
      "tier_availability": ["free", "paid"],
      "recommended": false
    },
    {
      "id": "anthropic/claude-haiku-4-5",
      "name": "Haiku 4.5",
      "provider": "anthropic",
      "context_window": 200000,
      "capabilities": ["chat", "function_calling", "vision"],
      "pricing": {
        "input_per_million": 1.0,
        "output_per_million": 5.0
      },
      "enabled": true,
      "tier_availability": ["paid"]
    }
  ],
  "default_model": "ollama/llama3.3",
  "user_tier": "local"
}
```

### POST /api/models/validate

Request:
```json
{
  "model_id": "ollama/llama3.3"
}
```

Response:
```json
{
  "is_valid": true,
  "error_message": null,
  "model_info": {
    "id": "ollama/llama3.3",
    "name": "Llama 3.3 70B",
    "provider": "ollama",
    ...
  }
}
```

---

## Summary

✅ **Frontend is fully integrated!**  
✅ **Model selector automatically works with new API**  
✅ **Ollama models show up in local mode**  
✅ **Tier-based access control in place**  
✅ **Agent creation supports model selection**  

**The integration is complete and ready to use!**

Users can now:
- 🎯 See all available models in the dropdown
- 💰 View pricing for each model
- 🆓 Use free Ollama models
- ✨ Create agents with specific models
- 🔄 Change agent models anytime

For detailed backend documentation, see:
- [MODEL_SELECTION_GUIDE.md](../backend/MODEL_SELECTION_GUIDE.md)
- [OLLAMA_SETUP.md](../backend/OLLAMA_SETUP.md)
