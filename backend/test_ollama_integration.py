"""
Test script to verify Ollama integration with Suna.

This script checks:
1. Model registry includes Ollama models
2. Models have correct configuration
3. Basic model resolution works
"""

import sys
import os

# Fix Windows console encoding for checkmarks/unicode
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.dirname(__file__))

from core.ai_models import model_manager
from core.ai_models.ai_models import ModelProvider
from core.utils.config import config

def test_ollama_integration():
    print("=" * 60)
    print("Testing Ollama Integration")
    print("=" * 60)
    
    # Check if running in local mode
    print(f"\n1. Environment Mode: {config.ENV_MODE.value if config and config.ENV_MODE else 'Unknown'}")
    print(f"   Ollama API Base: {config.OLLAMA_API_BASE if config else 'Not configured'}")
    
    # List all Ollama models in registry
    print("\n2. Ollama Models in Registry:")
    ollama_models = [
        m for m in model_manager.registry.get_all(enabled_only=False) 
        if m.provider == ModelProvider.OLLAMA
    ]
    
    if not ollama_models:
        print("   ⚠️  No Ollama models found in registry!")
        return False
    
    for model in ollama_models:
        status = "✓ ENABLED" if model.enabled else "✗ DISABLED"
        print(f"   {status} - {model.name} ({model.id})")
        print(f"      Context: {model.context_window:,} tokens")
        print(f"      Aliases: {', '.join(model.aliases)}")
        if model.config and model.config.api_base:
            print(f"      API Base: {model.config.api_base}")
    
    # Test model resolution
    print("\n3. Testing Model Resolution:")
    test_aliases = ["llama3.3", "ollama/llama3.3", "qwen2.5-coder"]
    
    for alias in test_aliases:
        resolved = model_manager.resolve_model_id(alias)
        if resolved:
            model = model_manager.get_model(resolved)
            print(f"   ✓ '{alias}' → {resolved}")
            if model and model.config:
                print(f"      API Base: {model.config.api_base}")
        else:
            print(f"   ✗ '{alias}' → Not found")
    
    # Test LiteLLM params generation
    print("\n4. Testing LiteLLM Params Generation:")
    test_model_id = "ollama/llama3.3"
    model = model_manager.get_model(test_model_id)
    
    if model:
        params = model.get_litellm_params(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7
        )
        print(f"   Model: {test_model_id}")
        print(f"   Generated params keys: {list(params.keys())}")
        print(f"   - model: {params.get('model')}")
        print(f"   - api_base: {params.get('api_base')}")
        print(f"   - temperature: {params.get('temperature')}")
    else:
        print(f"   ✗ Model {test_model_id} not found")
    
    # List available models for free tier
    print("\n5. Available Models (Free Tier):")
    free_models = model_manager.get_models_for_tier("free")
    ollama_free = [m for m in free_models if m.provider == ModelProvider.OLLAMA]
    
    if ollama_free:
        for model in ollama_free:
            print(f"   - {model.name} ({model.id})")
    else:
        print("   No Ollama models available in free tier")
    
    print("\n" + "=" * 60)
    print("Ollama Integration Test Complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_ollama_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
