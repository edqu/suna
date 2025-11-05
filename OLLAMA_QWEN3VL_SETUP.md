# Ollama Auto-Discovery - Automatic Model Registration

## What's Been Added

**Automatic Ollama Model Discovery!** 🎉 

The system now **automatically detects and registers ALL models** you've pulled in Ollama. No need to manually configure each model - just pull it with Ollama and it instantly appears in your Suna frontend!

### Why Qwen3-VL?

✅ **100% FREE** - Runs locally on your machine
✅ **PRIVATE** - Your data never leaves your computer
✅ **VISION CAPABLE** - Can understand and analyze images
✅ **FUNCTION CALLING** - Full tool support
✅ **NO API COSTS** - No usage limits or billing
✅ **128K context window** - Handle large conversations

## How Auto-Discovery Works

The system connects to your Ollama server on startup and:
1. ✅ Fetches the list of all installed models
2. ✅ Automatically registers each model with appropriate capabilities
3. ✅ Detects vision models (qwen, llava, moondream, etc.)
4. ✅ Sets proper context windows and priorities
5. ✅ Makes them instantly available in the frontend

**No manual configuration needed!** Just pull models with Ollama and restart the backend.

## Quick Setup

### Step 1: Install Ollama

**Download and install Ollama:**
- **Windows/Mac/Linux**: Visit https://ollama.com/download
- Follow installation instructions for your OS

### Step 2: Pull Any Model(s)

Pull **any model** you want to use:

```bash
# Vision-capable model (RECOMMENDED)
ollama pull qwen3-vl:latest

# Or other popular models
ollama pull llama3.3:latest
ollama pull gemma2:latest
ollama pull mistral:latest
ollama pull codellama:latest
```

### Step 3: Verify Models are Pulled

Check your installed models:

```bash
ollama list
```

You should see all the models you've pulled.

### Step 4: Configure Backend

Your `backend/.env` should already have (this is the default):

```env
OLLAMA_API_BASE=http://localhost:11434
```

If not, add it now.

### Step 5: Restart Backend

After adding the OLLAMA_API_BASE configuration, restart your backend server.

You'll see log messages like:
```
🔑 Auto-registering 3 Ollama models from http://localhost:11434
  ✓ Registered: qwen3-vl:latest (vision=True)
  ✓ Registered: llama3.3:latest (vision=False)
  ✓ Registered: codellama:latest (vision=False)
✅ Successfully registered 3 Ollama models
```

### Step 6: Use Your Models in Frontend

1. Open your Suna frontend
2. Click on the model selector
3. You'll see ALL your Ollama models automatically listed!
   - **"Qwen3 Vl (Local)"** - Vision model
   - **"Llama3.3 (Local)"** - Fast chat model
   - **"Codellama (Local)"** - Code-focused model
   - And any others you've pulled!
4. Select any model to start using it

## Adding More Models - Zero Configuration!

Want to add more models? Just pull them with Ollama:

```bash
# Pull any model from Ollama library
ollama pull deepseek-r1:latest
ollama pull phi4:latest
ollama pull llava:latest

# Restart backend - they'll automatically appear!
```

**That's it!** No code changes, no configuration files to edit. The system automatically discovers and registers them.

## Model Details

- **Model ID**: `ollama/qwen3-vl:latest`
- **Aliases**: `qwen3-vl`, `qwen3-vl:latest`, `Qwen3 VL`
- **Display Name**: "Qwen3 VL (Local)"
- **Context Window**: 128,000 tokens
- **Capabilities**:
  - 💬 Chat
  - 👁️ Vision (can analyze images)
  - 🔧 Function Calling (tools support)
- **Cost**: $0.00 (completely free, runs locally)

## How Auto-Discovery Works Internally

### 1. Model Registry (`backend/core/ai_models/registry.py`)

**New method: `_register_ollama_models()` (lines 628-730):**

This method:
1. Connects to Ollama API at `/api/tags` endpoint
2. Fetches list of all installed models
3. For each model, determines:
   - **Vision capability** (if model name contains: llava, qwen, qwen2-vl, qwen3-vl, bakllava, moondream)
   - **Context window** (128K for qwen/llama3/gemma2/mixtral, 4K for others)
   - **Priority** (105 for vision models, 85 for text-only)
   - **Recommended status** (qwen3-vl and llama3 models)
4. Auto-registers each model with full configuration

**Example:**
```python
# Connects to Ollama server
async with httpx.AsyncClient(timeout=2.0) as client:
    response = await client.get(f"{ollama_base}/api/tags")
    
# For each model found, auto-registers it:
for model_data in models_data:
    model_name = model_data.get("name")  # e.g., "qwen3-vl:latest"
    
    # Auto-detect capabilities
    if "qwen" in model_name or "llava" in model_name:
        capabilities.append(ModelCapability.VISION)
    
    # Register with full config
    self.register(Model(id=f"ollama/{model_name}", ...))
```

### 2. Environment Template (`backend/.env.example`)

Updated with clear instructions:
```env
# Ollama (local LLM deployment - FREE, private, runs on your machine)
# Install Ollama from: https://ollama.com/download
# Then run: ollama pull qwen3-vl:latest
OLLAMA_API_BASE=http://localhost:11434
```

## Testing Your Setup

### Test 1: Text Chat
```
User: "Hello! Tell me about yourself."
Qwen3 VL: "I'm Qwen3-VL, a vision-language model..."
```

### Test 2: Image Analysis (if your UI supports image upload)
```
User: [Upload an image] "What's in this image?"
Qwen3 VL: [Describes the image content]
```

### Test 3: Tool Usage
Send a message that requires tool usage (like web search, file operations, etc.) and verify the model can call tools.

## Troubleshooting

### Model Not Appearing in Frontend

**Check backend logs:**
```
🔑 Registering Ollama models (qwen3-vl:latest) with API base: http://localhost:11434
```

If you don't see this, check:
1. Is `OLLAMA_API_BASE` set in your `.env`?
2. Did you restart the backend?

### "Connection Refused" Error

**Ensure Ollama is running:**
```bash
# Check Ollama status
ollama list

# If not running, start it (usually auto-starts)
# On Windows/Mac: Open Ollama app
# On Linux: systemctl start ollama
```

### Model Not Downloaded

**Pull the model again:**
```bash
ollama pull qwen3-vl:latest
```

### Slow Performance

Qwen3-VL is a large model. For faster inference:
- Use a GPU if available (Ollama automatically uses it)
- Close other applications to free up RAM
- Consider using smaller quantized versions: `ollama pull qwen3-vl:q4_0`

## Using Docker?

If running Ollama in Docker, update your `OLLAMA_API_BASE`:

```env
# For Docker container named 'ollama'
OLLAMA_API_BASE=http://ollama:11434
```

## Supported Model Types

The auto-discovery system intelligently detects model capabilities:

### Vision Models (Auto-detected)
Models with these names get **vision capability**:
- `llava` - Multimodal Llama
- `qwen`, `qwen2-vl`, `qwen3-vl` - Qwen vision models
- `bakllava` - BakLLaVA vision model
- `moondream` - Tiny vision model

### Large Context Models (Auto-detected)
Models with these names get **128K context window**:
- `qwen` series
- `llama3` series
- `gemma2` series
- `mixtral` series
- Others default to 4K context

### Function Calling
**All Ollama models** are registered with function calling capability, enabling full tool support!

## Performance Tips

1. **First run will be slower** - Model needs to load into memory
2. **Keep Ollama running** - Subsequent requests are much faster
3. **Use GPU** - Ollama automatically detects and uses NVIDIA/AMD GPUs
4. **Monitor resources** - Check Task Manager/Activity Monitor for RAM usage

## Comparing to Cloud Models

| Feature | Qwen3-VL (Local) | Gemini 2.0 Flash | Claude Haiku 4.5 |
|---------|------------------|------------------|------------------|
| Cost | **FREE** | FREE (experimental) | $1/M tokens |
| Privacy | **100% Private** | Sent to Google | Sent to Anthropic |
| Speed | Fast (with GPU) | Very Fast | Fast |
| Vision | ✅ | ✅ | ✅ |
| Function Calling | ✅ | ✅ | ✅ |
| Context | 128K | 1M | 200K |
| Setup | Requires install | Just API key | Just API key |

## Switching Between Models

You can switch between cloud and local models anytime:
- **Qwen3-VL**: For private/sensitive data
- **Gemini**: For faster responses without local setup
- **Claude**: For complex reasoning tasks

Just select the model you want in the frontend dropdown!

## Resources

- **Ollama Docs**: https://ollama.com/docs
- **Qwen3-VL Model**: https://ollama.com/library/qwen3-vl
- **Model Details**: https://github.com/QwenLM/Qwen3
