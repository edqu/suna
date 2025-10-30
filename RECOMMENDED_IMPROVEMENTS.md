# Recommended Improvements - Priority Order

## 🔥 High Priority (Do These First)

### 1. **Ollama Health Check Endpoint** (1-2h)
**Problem**: Users can select models that aren't installed or when Ollama is down.

**Solution**: Add real-time status to model list
```typescript
GET /api/models
Response:
{
  "models": [
    {
      "id": "ollama/llama3:instruct",
      "name": "Llama 3 Instruct",
      "status": "installed",  // or "not_installed", "server_down"
      "provider": "ollama",
      "context_window": 8192
    }
  ]
}
```

**Implementation**:
- Backend calls Ollama `/api/tags` with 1.5s timeout
- Cache result for 60s to avoid repeated calls
- Show "Not installed" badge in UI with `ollama pull` command

**Impact**: ⭐⭐⭐⭐⭐ Prevents frustrating "model not found" errors

---

### 2. **Fix Auto-Selection Behavior** (30min)
**Problem**: SimpleModelSelector auto-selects first model, overriding user choice.

**Solution**: Only auto-select if no model is set
```typescript
// Before (problematic):
const safeSelectedModel = value || storeSelectedModel || availableModels[0]?.id;

// After (better):
const safeSelectedModel = value || storeSelectedModel || null;

// Only set if user has a stored preference:
useEffect(() => {
  if (!value && storeSelectedModel) {
    onChange(storeSelectedModel);
  }
}, [value, storeSelectedModel, onChange]);
```

**Impact**: ⭐⭐⭐⭐ Users stay in control

---

### 3. **Case-Insensitive Model Aliases** (30min)
**Problem**: `ollama/Llama3:instruct` fails but `ollama/llama3:instruct` works.

**Solution**: Normalize aliases in registry
```python
# In registry.py register():
for alias in model.aliases + [model.id]:
    self._aliases[alias.lower()] = model.id

# In get():
if model_id in self._models:
    return self._models[model_id]
key = model_id.lower()
if key in self._aliases:
    return self._models[self._aliases[key]]
```

**Impact**: ⭐⭐⭐⭐ Reduces user frustration

---

### 4. **Hide Cloud Models in Local Mode** (15min)
**Problem**: Anthropic models show in dropdown but can't be used without API keys.

**Solution**: Only enable cloud models if API key present
```python
# In registry.py, for cloud models:
self.register(Model(
    id="anthropic/claude-haiku-4-5",
    ...
    enabled=SHOULD_USE_ANTHROPIC,  # Only true if API key exists
))
```

**Impact**: ⭐⭐⭐⭐ Cleaner UI, less confusion

---

## 💪 Medium Priority (Nice to Have)

### 5. **Preflight Validation on Model Update** (2-3h)
**Problem**: Can save a model that isn't installed.

**Solution**: Check before saving
```python
@router.patch("/agents/{agent_id}/model")
async def update_agent_model(...):
    if model_id.startswith("ollama/"):
        # Check Ollama is running
        try:
            tags = await check_ollama_tags()
            model_name = model_id.replace("ollama/", "")
            if model_name not in tags:
                raise HTTPException(
                    status_code=409,
                    detail=f"Model not installed. Run: ollama pull {model_name}"
                )
        except:
            raise HTTPException(
                status_code=503,
                detail="Ollama server not reachable"
            )
```

**Impact**: ⭐⭐⭐⭐ Better error messages

---

### 6. **Improve Model Display in UI** (2h)
**Problem**: Hard to tell models apart.

**Solution**: Add badges and metadata
```tsx
<DropdownMenuItem>
  <div>
    <span>Llama 3 Instruct</span>
    <div className="flex gap-1">
      <Badge>Local</Badge>
      <Badge>8K context</Badge>
      {!installed && <Badge variant="warning">Not installed</Badge>}
    </div>
  </div>
</DropdownMenuItem>
```

**Impact**: ⭐⭐⭐⭐ Better UX

---

### 7. **Runtime Fallback** (2-3h)
**Problem**: Heavy models (deepseek-r1:70b) can crash.

**Solution**: Auto-fallback to smaller model
```python
try:
    response = await llm.generate(model=selected_model, ...)
except OllamaError:
    logger.warning(f"Model {selected_model} failed, falling back to llama3:instruct")
    response = await llm.generate(model="ollama/llama3:instruct", ...)
    # Show notice in UI: "Switched to Llama 3 due to error"
```

**Impact**: ⭐⭐⭐ Better reliability

---

### 8. **Better Logging** (1h)
**Problem**: Hard to debug model issues.

**Solution**: Add structured logs
```python
logger.info(
    "model_changed",
    user_id=user_id,
    agent_id=agent_id,
    old_model=old_model,
    new_model=new_model,
    installed=is_installed
)
```

**Impact**: ⭐⭐⭐ Easier debugging

---

## 🎁 Low Priority (Polish)

### 9. **Model Sorting** (30min)
Sort by: Local first → Recommended → Priority → Name

### 10. **Heavy Model Warning** (1h)
Show one-time warning for deepseek-r1:70b about VRAM requirements

### 11. **Model Testing Button** (2h)
Add "Test" button that sends 1-token request to verify model works

### 12. **Usage Statistics** (3h+)
Track which models are used most, token counts, response times

---

## 📋 Implementation Plan

### Week 1 - Critical Fixes
1. ✅ Fix auto-selection behavior (30min)
2. ✅ Case-insensitive aliases (30min)  
3. ✅ Hide cloud models in local mode (15min)
4. ⏳ Ollama health check endpoint (2h)

**Total: ~3-4 hours**

### Week 2 - Reliability
5. ⏳ Preflight validation (3h)
6. ⏳ Runtime fallback (3h)
7. ⏳ Better logging (1h)

**Total: ~7 hours**

### Week 3 - Polish
8. ⏳ Improve UI display (2h)
9. ⏳ Model sorting (30min)
10. ⏳ Heavy model warning (1h)

**Total: ~3.5 hours**

---

## 🚀 Quick Wins (Do Today)

These take < 1 hour total:

```python
# 1. Hide cloud models (backend/core/ai_models/registry.py)
enabled=is_local  # for Ollama models
enabled=SHOULD_USE_ANTHROPIC  # for cloud models

# 2. Case-insensitive aliases (same file)
self._aliases[alias.lower()] = model.id

# 3. Fix auto-selection (frontend/src/components/agents/config/simple-model-selector.tsx)
const safeSelectedModel = value || storeSelectedModel || null;
```

---

## 📊 Impact Matrix

| Improvement | UX | DX | Reliability | Performance | Effort |
|-------------|----|----|-------------|-------------|--------|
| Ollama health check | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 2h |
| Fix auto-selection | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | - | 30min |
| Case-insensitive | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | - | 30min |
| Hide cloud models | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 15min |
| Preflight validation | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | - | 3h |
| Better UI display | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | - | 2h |
| Runtime fallback | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 3h |
| Better logging | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | - | 1h |

---

## 🎯 Recommendation

**Start with the "Quick Wins"** (1 hour total) - they provide immediate value with minimal effort:

1. Hide cloud models in local mode
2. Case-insensitive aliases
3. Fix auto-selection

Then move to **Ollama health check** - this is the highest impact improvement for user experience.

The rest can be prioritized based on user feedback and pain points.
