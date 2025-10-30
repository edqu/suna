# Update Agent Model Route

## New API Endpoint

### Backend: `PATCH /agents/{agent_id}/model`

A dedicated endpoint to update only the model for a specific agent.

#### Parameters
- **Path**: `agent_id` - The ID of the agent to update
- **Query**: `model_id` - The ID of the model to set (e.g., `ollama/llama3:instruct`)

#### Features
- ✅ Validates model exists and is enabled
- ✅ Checks user tier permissions (free vs paid models)
- ✅ Creates a new agent version automatically
- ✅ Faster than full agent update (only touches model field)

#### Example Request

```bash
curl -X PATCH "http://localhost:8000/agents/abc123/model?model_id=ollama/llama3:instruct" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

#### Response

```json
{
  "agent_id": "abc123",
  "name": "My Agent",
  "model": "ollama/llama3:instruct",
  "system_prompt": "You are a helpful assistant...",
  ...
}
```

#### Error Responses

**400 Bad Request** - Invalid model
```json
{
  "detail": "Invalid model: Model 'xyz' not found"
}
```

**403 Forbidden** - Model not available for user tier
```json
{
  "detail": "Model 'anthropic/claude-opus-4' is not available for your subscription tier"
}
```

## Frontend Function

### `updateAgentModel(agentId, modelId)`

Located in: `frontend/src/hooks/react-query/agents/utils.ts`

#### Usage

```typescript
import { updateAgentModel } from '@/hooks/react-query/agents/utils';

// Update agent to use Llama 3 Instruct
const updatedAgent = await updateAgentModel(
  'agent-123',
  'ollama/llama3:instruct'
);

console.log('New model:', updatedAgent.model);
```

#### In React Component

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateAgentModel } from '@/hooks/react-query/agents/utils';

function MyComponent({ agentId }) {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: (modelId: string) => updateAgentModel(agentId, modelId),
    onSuccess: () => {
      queryClient.invalidateQueries(['agents', agentId]);
      toast.success('Model updated!');
    },
    onError: (error) => {
      toast.error(`Failed: ${error.message}`);
    }
  });

  return (
    <button onClick={() => mutation.mutate('ollama/qwen2.5-coder')}>
      Switch to Qwen Coder
    </button>
  );
}
```

## Integration with SimpleModelSelector

The `SimpleModelSelector` component can use this endpoint:

```typescript
const handleModelChange = async (modelId: string) => {
  try {
    await updateAgentModel(agentId, modelId);
    toast.success('Model updated successfully!');
  } catch (error) {
    toast.error('Failed to update model');
  }
};

<SimpleModelSelector
  value={currentModel}
  onChange={handleModelChange}
/>
```

## Benefits

1. **Faster Updates**: Only updates model field, not entire agent config
2. **Validation Built-in**: Backend validates model before saving
3. **Version Control**: Automatically creates new version when model changes
4. **Type Safety**: Full TypeScript support
5. **Error Handling**: Clear error messages for invalid models

## Available Models (Local Mode)

When `ENV_MODE=local`:
- `ollama/llama3:instruct` - Llama 3 8B Instruct (default)
- `ollama/llama3.3` - Llama 3.3 70B
- `ollama/qwen2.5-coder` - Qwen 2.5 Coder
- `ollama/deepseek-r1:70b` - DeepSeek R1 70B

## Testing

### Test the endpoint:

```bash
# Get your auth token from browser dev tools
TOKEN="your_supabase_token"

# Update model
curl -X PATCH \
  "http://localhost:8000/agents/YOUR_AGENT_ID/model?model_id=ollama/llama3.3" \
  -H "Authorization: Bearer $TOKEN"
```

### Verify in UI:

1. Open agent configuration dialog
2. Go to Instructions tab
3. Click model dropdown
4. Select different model
5. Click Save Changes
6. Verify model persists after reload

## Files Modified

### Backend
- `backend/core/agent_crud.py` - Added `update_agent_model()` endpoint

### Frontend
- `frontend/src/hooks/react-query/agents/utils.ts` - Added `updateAgentModel()` function

## Related Documentation

- [Model Selector Fix](./MODEL_SELECTOR_FIX.md)
- [Complete Integration Summary](./COMPLETE_INTEGRATION_SUMMARY.md)
- [Quick Reference](./QUICK_REFERENCE.md)
