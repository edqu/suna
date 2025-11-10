# Ollama GPU Optimization Guide

## Current Issue
Local models (Ollama) are running slowly, potentially using CPU instead of GPU.

## Check GPU Usage

### 1. Verify Ollama is Using GPU

Run this command to check which models are loaded and if GPU is being used:
```bash
ollama ps
```

You should see output showing VRAM usage if GPU is active.

### 2. Check GPU Availability

**On Windows:**
```powershell
# Check NVIDIA GPU
nvidia-smi

# Check GPU memory
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

**On Linux/Mac:**
```bash
nvidia-smi  # For NVIDIA GPUs
rocm-smi    # For AMD GPUs
```

## Force Ollama to Use GPU

### Method 1: Environment Variables (Recommended)

Set these environment variables before starting Ollama:

**Windows (PowerShell):**
```powershell
# Set GPU layers (higher = more GPU usage)
$env:OLLAMA_NUM_GPU=1
$env:OLLAMA_GPU_LAYERS=999  # Use all layers on GPU

# Restart Ollama service
Restart-Service Ollama
```

**Linux/Mac:**
```bash
export OLLAMA_NUM_GPU=1
export OLLAMA_GPU_LAYERS=999

# Restart Ollama
sudo systemctl restart ollama
```

### Method 2: Modelfile Configuration

Create a custom Modelfile for each model with GPU settings:

```bash
# Create a Modelfile
cat > Modelfile <<EOF
FROM llama3.3

# GPU acceleration settings
PARAMETER num_gpu 1
PARAMETER gpu_layers 999

# Performance tuning
PARAMETER num_thread 8
PARAMETER num_ctx 8192
EOF

# Create model from Modelfile
ollama create llama3.3-gpu -f Modelfile

# Use the optimized model
ollama run llama3.3-gpu
```

### Method 3: Backend Configuration

Add Ollama GPU settings to your backend `.env`:

```bash
# Force GPU usage for Ollama
OLLAMA_NUM_GPU=1
OLLAMA_GPU_LAYERS=999
```

Then modify the backend to pass these to Ollama API calls.

## Verify GPU Usage

### Test GPU Performance

```bash
# Run a test prompt and monitor GPU
ollama run llama3.3 "Write a story about AI"

# In another terminal, watch GPU usage
nvidia-smi -l 1  # Updates every second
```

You should see:
- GPU memory usage increase
- GPU utilization % go up
- Faster response times

### Expected Performance

With GPU:
- **Llama 3.3 70B**: 20-50 tokens/second (depending on GPU)
- **Qwen 2.5 Coder**: 30-80 tokens/second
- **Smaller models**: 50-150 tokens/second

Without GPU (CPU only):
- **Much slower**: 1-5 tokens/second
- High CPU usage
- Slower response times

## Troubleshooting

### GPU Not Detected

**Windows:**
1. Check NVIDIA drivers are installed: `nvidia-smi`
2. Reinstall Ollama (latest version has better GPU support)
3. Make sure CUDA toolkit is installed

**Linux:**
1. Install NVIDIA Container Toolkit:
   ```bash
   sudo apt-get install nvidia-container-toolkit
   ```
2. Restart Docker if using containers

### Models Still Slow

If GPU is detected but models are still slow:

1. **Reduce context window:**
   ```bash
   # Edit model parameters
   ollama show llama3.3 --modelfile > Modelfile
   # Edit PARAMETER num_ctx to lower value (e.g., 4096)
   ollama create llama3.3-fast -f Modelfile
   ```

2. **Use quantized models:**
   ```bash
   # Use smaller quantization (faster but slightly less accurate)
   ollama pull llama3.3:q4_K_M  # 4-bit quantization
   ```

3. **Increase GPU memory allocation:**
   ```bash
   # Allow more VRAM usage
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

4. **Check concurrent requests:**
   - Ollama can slow down with multiple concurrent requests
   - Ensure only one model is loaded at a time

## Advanced: LiteLLM Configuration for Ollama

To ensure LiteLLM (used by Suna) passes GPU parameters to Ollama:

**backend/core/ai_models/ai_models.py:**
```python
# In ModelConfig or get_litellm_params
if self.provider == ModelProvider.OLLAMA:
    params["num_gpu"] = 1  # Enable GPU
    params["gpu_layers"] = 999  # Use all layers on GPU
```

## Monitoring Performance

Add logging to track response times:

**backend/core/services/llm.py:**
```python
import time

start_time = time.time()
response = await litellm.acompletion(...)
duration = time.time() - start_time

logger.info(f"LLM response time: {duration:.2f}s")
```

## Quick Test Commands

```bash
# Test Ollama GPU usage
ollama run llama3.3 "test"

# Check what's loaded
ollama ps

# Check GPU usage
nvidia-smi

# Reload model with GPU
ollama stop llama3.3
ollama run llama3.3
```

## Recommended Settings for Suna

Add to `backend/.env`:
```bash
# Ollama Configuration
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_NUM_GPU=1
OLLAMA_GPU_LAYERS=999
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_THREAD=8
```

## Performance Tips

1. **Keep models warm**: Don't let Ollama unload models between requests
2. **Use appropriate quantization**: Q4_K_M is a good balance
3. **Monitor VRAM**: Ensure you have enough GPU memory
4. **Single model at a time**: Load only one large model
5. **Optimize context window**: Use only what you need (4K-8K is often enough)
