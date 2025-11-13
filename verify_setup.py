#!/usr/bin/env python3
"""
Verification script for Ollama tool calling setup.

This script checks if your system is properly configured for using
browser and web search tools with Ollama models like Qwen.

Run: python verify_setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_ollama():
    """Check if Ollama is installed and running."""
    print_header("Checking Ollama")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success(f"Ollama installed: {result.stdout.strip()}")
        else:
            print_error("Ollama command failed")
            return False
    except FileNotFoundError:
        print_error("Ollama not found. Install from: https://ollama.com")
        return False
    except subprocess.TimeoutExpired:
        print_error("Ollama command timed out")
        return False
    
    # Check if Ollama is running
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_success("Ollama service is running")
            
            # List available models
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # More than just header
                print_info("Available models:")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        print(f"    {line}")
            else:
                print_warning("No models installed. Install Qwen: ollama pull qwen2.5-coder")
            return True
        else:
            print_error("Ollama list command failed")
            return False
    except Exception as e:
        print_error(f"Failed to check Ollama models: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has necessary keys."""
    print_header("Checking Environment Configuration")
    
    env_path = Path(__file__).parent / 'backend' / '.env'
    
    if not env_path.exists():
        print_warning(f".env file not found at: {env_path}")
        print_info("Local web search will still work (no API keys needed)")
        print_info("Browser tool requires GEMINI_API_KEY for vision features")
        return False
    
    print_success(f".env file found: {env_path}")
    
    # Read .env and check for important keys
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Check for GEMINI_API_KEY (optional, for browser tool)
    if 'GEMINI_API_KEY=' in env_content and not 'GEMINI_API_KEY=""' in env_content:
        print_success("GEMINI_API_KEY configured (browser tool will work)")
    else:
        print_warning("GEMINI_API_KEY not configured")
        print_info("Browser tool won't work, but web search will")
        print_info("Get free key: https://aistudio.google.com/app/apikey")
    
    # Check for paid API keys (should NOT be needed)
    if 'TAVILY_API_KEY=' in env_content and not 'TAVILY_API_KEY=""' in env_content:
        print_info("TAVILY_API_KEY found (optional paid search)")
    
    if 'FIRECRAWL_API_KEY=' in env_content and not 'FIRECRAWL_API_KEY=""' in env_content:
        print_info("FIRECRAWL_API_KEY found (optional paid scraping)")
    
    return True

def check_backend_files():
    """Check if required backend files exist."""
    print_header("Checking Backend Files")
    
    files_to_check = [
        ('backend/core/run.py', 'Main agent runner'),
        ('backend/core/tools/local_web_search_tool.py', 'Local web search tool'),
        ('backend/core/tools/browser_tool.py', 'Browser automation tool'),
        ('backend/core/agentpress/tool_adapter.py', 'Universal tool adapter'),
        ('backend/core/agentpress/response_processor.py', 'Response processor'),
    ]
    
    all_found = True
    for file_path, description in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print_success(f"{description}: {file_path}")
        else:
            print_error(f"{description} NOT FOUND: {file_path}")
            all_found = False
    
    return all_found

def check_python_packages():
    """Check if required Python packages are installed."""
    print_header("Checking Python Dependencies")
    
    packages = [
        'asyncio',
        'aiohttp',
    ]
    
    optional_packages = [
        ('duckduckgo_search', 'For free web search'),
        ('beautifulsoup4', 'For web scraping'),
        ('playwright', 'For browser automation'),
    ]
    
    all_found = True
    
    for package in packages:
        try:
            __import__(package)
            print_success(f"Required: {package}")
        except ImportError:
            print_error(f"Required package missing: {package}")
            all_found = False
    
    for package, purpose in optional_packages:
        try:
            __import__(package)
            print_success(f"Optional: {package} ({purpose})")
        except ImportError:
            print_warning(f"Optional package missing: {package} ({purpose})")
            print_info(f"  Install: pip install {package}")
    
    return all_found

def check_tool_adapter_integration():
    """Check if tool adapter fixes are in place."""
    print_header("Checking Ollama Tool Adapter Integration")
    
    run_py_path = Path(__file__).parent / 'backend' / 'core' / 'run.py'
    
    if not run_py_path.exists():
        print_error("run.py not found")
        return False
    
    with open(run_py_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('if model_provider == "ollama":', 'Ollama detection'),
        ('model_supports_native = False', 'Force XML for Ollama'),
        ('tool_choice_param =', 'tool_choice handling'),
        ('from core.agentpress.tool_adapter import', 'Tool adapter import'),
    ]
    
    all_found = True
    for search_str, description in checks:
        if search_str in content:
            print_success(description)
        else:
            print_error(f"{description} NOT FOUND in run.py")
            print_info(f"  Looking for: {search_str}")
            all_found = False
    
    return all_found

def print_summary(results):
    """Print summary of checks."""
    print_header("Verification Summary")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        if passed:
            print_success(check)
        else:
            print_error(check)
    
    print()
    
    if all_passed:
        print_success("✨ All checks passed! Your system is ready for Ollama tool calling.")
        print()
        print_info("Next steps:")
        print("  1. Start your backend: python start.py")
        print("  2. Look for these logs:")
        print("     - '✅ Registered LOCAL web search tool (FREE)'")
        print("     - '✅ Registered browser_tool with all methods'")
        print("  3. Test with Qwen model: Select 'ollama/qwen2.5-coder'")
        print("  4. Try: 'Search the web for latest Qwen features'")
    else:
        print_warning("⚠️  Some checks failed. See errors above.")
        print()
        print_info("Quick fixes:")
        print("  - Missing Ollama: Install from https://ollama.com")
        print("  - Missing models: Run 'ollama pull qwen2.5-coder'")
        print("  - Missing files: Ensure you have the latest code")
        print("  - Missing packages: Run 'pip install -r requirements.txt'")
        print("  - Missing GEMINI_API_KEY: Get from https://aistudio.google.com/app/apikey")

def main():
    """Run all verification checks."""
    print_header("🔍 Ollama Tool Calling Verification")
    print_info("This script verifies your setup for using tools with Ollama models\n")
    
    results = {
        "Ollama installed and running": check_ollama(),
        "Environment configuration": check_env_file(),
        "Required backend files": check_backend_files(),
        "Python dependencies": check_python_packages(),
        "Tool adapter integration": check_tool_adapter_integration(),
    }
    
    print_summary(results)
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
