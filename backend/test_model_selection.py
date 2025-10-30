"""
Test script for model selection functionality.

This script demonstrates:
1. Listing available models
2. Grouping models by provider
3. Validating model selection
4. Getting model information
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from core.utils.model_selector import model_selector
from core.ai_models import model_manager
from core.utils.config import config


def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_list_all_models():
    """Test listing all available models."""
    print_separator("TEST 1: List All Available Models")
    
    models = model_selector.list_all_models(tier=None)
    
    print(f"\nTotal models available: {len(models)}")
    
    for model in models[:5]:  # Show first 5
        print(f"\n  Model: {model['name']}")
        print(f"    ID: {model['id']}")
        print(f"    Provider: {model['provider']}")
        print(f"    Context: {model['context_window']:,} tokens")
        print(f"    Capabilities: {', '.join(model['capabilities'])}")
        print(f"    Tiers: {', '.join(model['tier_availability'])}")
        
        if model.get('pricing'):
            pricing = model['pricing']
            input_cost = pricing.get('input_per_million', 0)
            output_cost = pricing.get('output_per_million', 0)
            if input_cost == 0 and output_cost == 0:
                print(f"    Cost: FREE")
            else:
                print(f"    Cost: ${input_cost}/M input, ${output_cost}/M output")
    
    if len(models) > 5:
        print(f"\n  ... and {len(models) - 5} more models")


def test_group_by_provider():
    """Test grouping models by provider."""
    print_separator("TEST 2: Group Models by Provider")
    
    models = model_selector.list_all_models(tier=None)
    grouped = model_selector.group_models_by_provider(models)
    
    print(f"\nProviders found: {len(grouped)}")
    
    for provider, provider_models in grouped.items():
        print(f"\n  {provider.upper()}:")
        for model in provider_models:
            free_tag = " [FREE]" if all(c == 0 for c in [
                model.get('pricing', {}).get('input_per_million', 1),
                model.get('pricing', {}).get('output_per_million', 1)
            ]) else ""
            recommended = " ⭐" if model.get('recommended') else ""
            print(f"    - {model['name']}{free_tag}{recommended}")


def test_model_validation():
    """Test model validation."""
    print_separator("TEST 3: Model Validation")
    
    test_models = [
        "ollama/llama3.3",
        "llama3.3",  # Alias
        "qwen2.5-coder",  # Alias
        "invalid-model",  # Invalid
        "anthropic/claude-haiku-4-5"
    ]
    
    print("\nValidating models:\n")
    
    for model_id in test_models:
        is_valid, error_msg = model_selector.validate_model(model_id)
        
        if is_valid:
            resolved = model_manager.resolve_model_id(model_id)
            print(f"  ✓ '{model_id}'")
            if resolved != model_id:
                print(f"      → Resolves to: {resolved}")
        else:
            print(f"  ✗ '{model_id}'")
            print(f"      Error: {error_msg}")


def test_model_info():
    """Test getting detailed model information."""
    print_separator("TEST 4: Get Model Information")
    
    test_model = "ollama/llama3.3"
    
    print(f"\nGetting info for: {test_model}\n")
    
    info = model_selector.get_model_info(test_model)
    
    if info:
        print(f"  Name: {info['name']}")
        print(f"  ID: {info['id']}")
        print(f"  Provider: {info['provider']}")
        print(f"  Context Window: {info['context_window']:,} tokens")
        print(f"  Max Output: {info.get('max_output_tokens', 'N/A')}")
        print(f"  Capabilities: {', '.join(info['capabilities'])}")
        print(f"  Enabled: {info['enabled']}")
        print(f"  Beta: {info['beta']}")
        print(f"  Recommended: {info['recommended']}")
        print(f"  Priority: {info['priority']}")
        print(f"  Tier Availability: {', '.join(info['tier_availability'])}")
        
        if info.get('pricing'):
            pricing = info['pricing']
            print(f"\n  Pricing:")
            print(f"    Input: ${pricing['input_per_million']}/M tokens")
            print(f"    Output: ${pricing['output_per_million']}/M tokens")
    else:
        print(f"  Model not found!")


def test_tier_filtering():
    """Test filtering models by tier."""
    print_separator("TEST 5: Filter Models by Tier")
    
    for tier in ['free', 'paid']:
        models = model_selector.list_all_models(tier=tier)
        print(f"\n  {tier.upper()} Tier Models: {len(models)}")
        
        for model in models[:3]:  # Show first 3
            print(f"    - {model['name']} ({model['id']})")
        
        if len(models) > 3:
            print(f"    ... and {len(models) - 3} more")


def test_ollama_models():
    """Test Ollama-specific models."""
    print_separator("TEST 6: Ollama Models")
    
    all_models = model_selector.list_all_models(tier=None)
    ollama_models = [m for m in all_models if m['provider'] == 'ollama']
    
    print(f"\nOllama models available: {len(ollama_models)}")
    
    if ollama_models:
        print(f"Environment Mode: {config.ENV_MODE.value if config else 'Unknown'}")
        print(f"Ollama API Base: {config.OLLAMA_API_BASE if config else 'Not configured'}")
        
        print("\nOllama Models:")
        for model in ollama_models:
            status = "ENABLED" if model['enabled'] else "DISABLED"
            print(f"\n  [{status}] {model['name']}")
            print(f"    ID: {model['id']}")
            print(f"    Context: {model['context_window']:,} tokens")
            print(f"    Capabilities: {', '.join(model['capabilities'])}")
            print(f"    Cost: FREE (runs locally)")
            print(f"    Tiers: {', '.join(model['tier_availability'])}")
    else:
        print("\n  No Ollama models found.")
        print("  Make sure ENV_MODE=local to enable Ollama models.")


def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "MODEL SELECTION TEST SUITE" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_list_all_models()
        test_group_by_provider()
        test_model_validation()
        test_model_info()
        test_tier_filtering()
        test_ollama_models()
        
        print("\n" + "=" * 70)
        print("  ✓ All tests completed successfully!")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during tests: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
