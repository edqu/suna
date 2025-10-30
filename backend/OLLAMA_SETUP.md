# Ollama Integration Setup

This guide explains how to use Ollama with Suna for local LLM deployment.

## What is Ollama?

Ollama allows you to run open-source LLMs locally on your machine. This is free and doesn't require API keys.

## Installation

### 1. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com)

**Windows/Mac/Linux:**
Follow the installation instructions at https://ollama.com/download

### 2. Pull Models

After installation, pull the models you want to use:

```bash
# Llama 3.3 70B (recommended for general tasks)
ollama pull llama3.3

# Qwen 2.5 Coder (optimized for coding)
ollama pull qwen2.5-coder

# DeepSeek R1 70B (reasoning model)
ollama pull deepseek-r1:70b
```

### 3. Configure Suna

Add to your `.env` file:

```bash
# Ollama API endpoint (default is localhost:11434)
OLLAMA_API_BASE=http://localhost:11434
```

### 4. Verify Ollama is Running

Check that Ollama is running:

```bash
curl http://localhost:11434/api/tags
```

You should see a list of your installed models.

## Available Models

The following Ollama models are configured in Suna (only enabled in local mode):

1. **ollama/llama3.3** - Llama 3.3 70B
   - Best for: General tasks, conversation
   - Context: 128K tokens
   - Free, runs locally

2. **ollama/qwen2.5-coder** - Qwen 2.5 Coder
   - Best for: Code generation, programming tasks
   - Context: 32K tokens
   - Free, runs locally

3. **ollama/deepseek-r1:70b** - DeepSeek R1 70B
   - Best for: Complex reasoning tasks
   - Context: 64K tokens
   - Free, runs locally

## Usage

Once configured, you can select Ollama models in the Suna UI just like any other LLM provider. The models will appear in your model selection dropdown when running in local mode.

## Custom Ollama Base URL

If you're running Ollama on a different host or port, update the `OLLAMA_API_BASE` environment variable:

```bash
# Example: Running on a different port
OLLAMA_API_BASE=http://localhost:8080

# Example: Running on a remote server
OLLAMA_API_BASE=http://192.168.1.100:11434
```

## Troubleshooting

### Models not appearing
- Make sure you're running in `ENV_MODE=local`
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check that models are pulled: `ollama list`

### Connection errors
- Ensure Ollama service is running
- Verify the `OLLAMA_API_BASE` URL is correct
- Check firewall settings if using a remote Ollama server

### Performance issues
- Ollama models run locally and require sufficient RAM/GPU
- Llama 3.3 70B requires ~40GB RAM (or GPU VRAM)
- Consider using smaller models like `llama3.2:3b` for lower resource usage

## Adding More Models

To add custom Ollama models to Suna:

1. Edit `backend/core/ai_models/registry.py`
2. Add a new model entry in the `_initialize_models()` method following the existing pattern
3. Restart the backend server

Example:
```python
self.register(Model(
    id="ollama/your-model-name",
    name="Your Model Display Name",
    provider=ModelProvider.OLLAMA,
    aliases=["your-model-name"],
    context_window=128_000,
    capabilities=[ModelCapability.CHAT, ModelCapability.FUNCTION_CALLING],
    pricing=ModelPricing(
        input_cost_per_million_tokens=0.00,
        output_cost_per_million_tokens=0.00
    ),
    tier_availability=["free", "paid"],
    priority=75,
    enabled=is_local,
    config=ModelConfig(
        api_base=getattr(config, 'OLLAMA_API_BASE', 'http://localhost:11434'),
    )
))
```
