# Quick Start: Model Selection

Get started with model selection in 5 minutes!

## 1. View Available Models

```bash
curl http://localhost:8000/api/models \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 2. Create Agent with Specific Model

**Free Option (Ollama - runs locally):**
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Code Assistant",
    "model": "ollama/qwen2.5-coder"
  }'
```

**Premium Option (Anthropic):**
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Premium Assistant",
    "model": "anthropic/claude-haiku-4-5"
  }'
```

## 3. Update Agent Model

```bash
curl -X PUT http://localhost:8000/api/agents/{agent_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/llama3.3"
  }'
```

## Available Models

### FREE (Ollama - Local)
- `ollama/llama3.3` - General tasks (128K context)
- `ollama/qwen2.5-coder` - Code generation (32K context)
- `ollama/deepseek-r1:70b` - Reasoning (64K context)

### PAID (Anthropic - Cloud)
- `anthropic/claude-haiku-4-5` - Fast, affordable
- `anthropic/claude-sonnet-4` - High performance
- `anthropic/claude-sonnet-4-5` - Latest, best quality

## Model Aliases

You can use short names:
- `llama3.3` → `ollama/llama3.3`
- `qwen2.5-coder` → `ollama/qwen2.5-coder`

## Using Ollama (Free Models)

1. **Install Ollama**
   ```bash
   # Download from https://ollama.com
   ```

2. **Pull Models**
   ```bash
   ollama pull llama3.3
   ollama pull qwen2.5-coder
   ```

3. **Set Environment**
   Add to `.env`:
   ```
   ENV_MODE=local
   OLLAMA_API_BASE=http://localhost:11434
   ```

4. **Use in Agents**
   Models will appear in `/api/models` automatically!

## Testing

Run the test suite:
```bash
cd suna/backend
python test_model_selection.py
```

## Documentation

- **Full Guide:** [MODEL_SELECTION_GUIDE.md](./MODEL_SELECTION_GUIDE.md)
- **Ollama Setup:** [OLLAMA_SETUP.md](./OLLAMA_SETUP.md)
- **Summary:** [MODEL_SELECTION_SUMMARY.md](./MODEL_SELECTION_SUMMARY.md)

## Common Use Cases

**Coding Tasks:**
```json
{ "model": "ollama/qwen2.5-coder" }
```

**General Chat:**
```json
{ "model": "ollama/llama3.3" }
```

**Complex Reasoning:**
```json
{ "model": "ollama/deepseek-r1:70b" }
```

**High Quality (Paid):**
```json
{ "model": "anthropic/claude-sonnet-4-5" }
```

---

**Need Help?** See the full guides or run `python test_model_selection.py` to verify your setup!
