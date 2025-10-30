# Model Selector Test Guide

## Where to Find Model Selection

### 1. **In Chat Interface** (Already Working)
- Bottom of chat input
- Click the **agent/model dropdown button** (shows current agent icon)
- Two sections:
  - **Agents**: Select which agent to use
  - **Models**: Select which model the agent uses

### 2. **In Agent Configuration Dialog** (Just Added)
1. Go to your agents page
2. Click on any agent card
3. Or click agent settings icon
4. Go to **Instructions** tab
5. You should see **Model** dropdown at the top
6. Below that is the System Prompt editor

## How to Test

### Start the Frontend
```bash
cd frontend
npm run dev
```

### Start the Backend
```bash
cd backend
python api.py
```

Make sure your `.env` has:
```
ENV_MODE=local
OLLAMA_API_BASE=http://localhost:11434
```

## What Should Appear

### In Agent Config Dialog > Instructions Tab:
```
┌─────────────────────────────────┐
│ Model                           │
│ ┌─────────────────────────────┐ │
│ │ 🦙 Llama 3 Instruct      ▼ │ │
│ └─────────────────────────────┘ │
│                                 │
│ System Prompt                   │
│ ┌─────────────────────────────┐ │
│ │                             │ │
│ │ You are a helpful...        │ │
│ │                             │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

When clicked, dropdown shows:
- ollama/llama3:instruct (Recommended)
- ollama/llama3.3
- ollama/qwen2.5-coder
- ollama/deepseek-r1:70b

## Troubleshooting

### If Model Dropdown Doesn't Show
1. Check browser console for errors
2. Verify `AgentModelSelector` component is imported
3. Check `formData.model` has a value
4. Ensure backend is running and `/api/models` endpoint works

### Test Backend Endpoint
```bash
curl http://localhost:8000/api/models
```

Should return JSON with available models.
