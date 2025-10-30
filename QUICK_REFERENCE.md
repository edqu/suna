# Quick Reference Card: Model Selection + Ollama

Quick reference for using the model selection feature with Ollama.

---

## 🚀 Quick Start (2 Minutes)

### Backend
```bash
cd suna/backend
pip install ollama
echo "OLLAMA_API_BASE=http://localhost:11434" >> .env
python test_model_selection.py  # Should pass!
```

### Ollama
```bash
ollama pull llama3.3
ollama pull qwen2.5-coder
```

### Frontend
```bash
cd suna/frontend
npm run dev
# Open agent creation → See Ollama models in dropdown
```

---

## 📝 API Cheat Sheet

### List Models
```bash
GET /api/models
Authorization: Bearer {token}

Response: {
  models: [...],
  default_model: "ollama/llama3.3",
  user_tier: "local"
}
```

### Create Agent with Model
```bash
POST /api/agents
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "My Agent",
  "model": "ollama/llama3.3"
}
```

### Validate Model
```bash
POST /api/models/validate
Content-Type: application/json

{
  "model_id": "ollama/llama3.3"
}
```

---

## 🎯 Model Selection

### Free Models (Ollama)
```
ollama/llama3.3         - General tasks
ollama/qwen2.5-coder    - Coding
ollama/deepseek-r1:70b  - Reasoning
```

### Premium Models (Anthropic)
```
anthropic/claude-haiku-4-5   - $1/$5 per 1M tokens
anthropic/claude-sonnet-4    - $3/$15 per 1M tokens  
anthropic/claude-sonnet-4-5  - $3/$15 per 1M tokens
```

---

## 🔧 Environment Variables

```bash
# Required for local mode
ENV_MODE=local

# Ollama configuration
OLLAMA_API_BASE=http://localhost:11434

# Backend
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_key
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No Ollama models | `ENV_MODE=local` in .env |
| Models not loading | Check `/api/models` endpoint |
| Validation fails | Verify user tier |
| Ollama not working | `curl http://localhost:11434/api/tags` |

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `OLLAMA_SETUP.md` | Ollama installation |
| `MODEL_SELECTION_GUIDE.md` | Complete API guide |
| `FRONTEND_MODEL_SELECTION_INTEGRATION.md` | Frontend guide |
| `QUICK_START_MODEL_SELECTION.md` | 5-min quickstart |

---

## ✅ Testing Checklist

- [ ] Backend tests pass
- [ ] Frontend loads models
- [ ] Ollama models appear
- [ ] Agent creation works
- [ ] Model validation works
- [ ] Pricing displays correctly

---

## 🎨 UI Components

```typescript
// Use in your component
import { AgentModelSelector } from '@/components/agents/config/model-selector';

<AgentModelSelector
  value={selectedModel}
  onChange={setSelectedModel}
/>
```

---

## 💻 Code Examples

### TypeScript
```typescript
// Get available models
const models = await getAvailableModels();

// Create agent with model
const agent = await createAgent({
  name: 'My Agent',
  model: 'ollama/llama3.3'
});

// Validate model
const validation = await validateModel('ollama/llama3.3');
```

### Python
```python
# Test Ollama integration
python test_ollama_integration.py

# Test model selection
python test_model_selection.py
```

### cURL
```bash
# List models
curl http://localhost:8000/api/models \
  -H "Authorization: Bearer TOKEN"

# Create agent
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"Test","model":"ollama/llama3.3"}'
```

---

## 🔑 Key Files

**Backend:**
- `core/models_api.py` - API endpoints
- `core/utils/model_selector.py` - Utilities
- `core/ai_models/registry.py` - Model registry

**Frontend:**
- `src/lib/api.ts` - API client
- `src/components/agents/config/model-selector.tsx` - UI
- `src/hooks/use-model-selection.ts` - Hook

---

## 🎯 Common Tasks

### Add New Ollama Model
1. Edit `backend/core/ai_models/registry.py`
2. Add model in `_initialize_models()`
3. Restart backend
4. Model appears in UI

### Change Default Model
1. Edit user tier in database
2. Backend auto-selects appropriate default
3. Or specify in agent creation

### Debug Model Issues
1. Check `/api/models` response
2. Verify `ENV_MODE` setting
3. Test Ollama connection
4. Check browser console

---

## 📊 Status Check

```bash
# Backend
curl http://localhost:8000/api/health
curl http://localhost:8000/api/models

# Ollama
curl http://localhost:11434/api/tags
ollama list

# Frontend
# Open browser → Agent creation → Check dropdown
```

---

## 🎉 Success Indicators

✅ Ollama models show in dropdown  
✅ Pricing displays correctly  
✅ FREE badge on Ollama models  
✅ Can create agent with model  
✅ Model saves and persists  
✅ Search/filter works  

---

**Quick Links:**
- [Complete Guide](COMPLETE_INTEGRATION_SUMMARY.md)
- [Ollama Setup](backend/OLLAMA_SETUP.md)
- [UI Guide](MODEL_SELECTION_UI_GUIDE.md)

**Need Help?** Check the troubleshooting section or the full documentation.
