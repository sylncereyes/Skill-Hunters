#!/usr/bin/env python3
"""
Test script for model-agnostic LLM client.
Run with: python engine/test_model_agnostic.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import LLMClient, create_provider, OpenRouterProvider, OllamaProvider, AnthropicProvider, ClaudeCLIProvider

def test_providers():
    """Test all provider initializations."""
    print("=" * 60)
    print("Testing Provider Initialization")
    print("=" * 60)

    # Test OpenRouter (no API key - should fail validation but init OK)
    try:
        p = create_provider("openrouter", "nvidia/nemotron-3-ultra", api_key="test", base_url="https://openrouter.ai/api/v1")
        ok, msg = p.validate_config()
        print(f"✓ OpenRouter: init OK, validate={'OK' if ok else 'EXPECTED FAIL'}: {msg}")
    except Exception as e:
        print(f"✗ OpenRouter: {e}")

    # Test Ollama
    try:
        p = create_provider("ollama", "nemotron3-ultra", base_url="http://localhost:11434")
        ok, msg = p.validate_config()
        print(f"✓ Ollama: init OK, validate={'OK' if ok else 'FAIL'}: {msg}")
    except Exception as e:
        print(f"✗ Ollama: {e}")

    # Test Anthropic
    try:
        p = create_provider("anthropic", "claude-sonnet-4-20250514", api_key="test")
        ok, msg = p.validate_config()
        print(f"✓ Anthropic: init OK, validate={'OK' if ok else 'EXPECTED FAIL'}: {msg}")
    except Exception as e:
        print(f"✗ Anthropic: {e}")

    # Test Claude CLI
    try:
        p = create_provider("claude-cli", "claude-sonnet-4-6")
        ok, msg = p.validate_config()
        print(f"✓ Claude CLI: init OK, validate={'OK' if ok else 'FAIL'}: {msg}")
    except Exception as e:
        print(f"✗ Claude CLI: {e}")

    # Test OpenAI-compatible
    try:
        p = create_provider("openai", "gpt-4o-mini", api_key="test", base_url="https://api.openai.com/v1")
        ok, msg = p.validate_config()
        print(f"✓ OpenAI-compatible: init OK, validate={'OK' if ok else 'EXPECTED FAIL'}: {msg}")
    except Exception as e:
        print(f"✗ OpenAI-compatible: {e}")

def test_llm_client():
    """Test LLMClient auto-config."""
    print("\n" + "=" * 60)
    print("Testing LLMClient Auto-Config")
    print("=" * 60)

    # Test with explicit provider
    for provider in ["openrouter", "ollama", "anthropic", "claude-cli", "openai"]:
        try:
            c = LLMClient(provider=provider, model="test-model")
            ok, msg = c.validate()
            print(f"✓ {provider}: model={c.model}, validate={'OK' if ok else 'FAIL'}: {msg}")
        except Exception as e:
            print(f"✗ {provider}: {e}")

def test_engine_integration():
    """Test engine integration with mock."""
    print("\n" + "=" * 60)
    print("Testing Engine Integration (mock mode)")
    print("=" * 60)

    import subprocess
    result = subprocess.run([
        sys.executable, "engine.py",
        "--scope", "engagement.example.json",
        "--mock",
        "--provider", "ollama",
        "--hunt"
    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))

    if result.returncode == 0:
        print("✓ Engine mock run: SUCCESS")
        # Check for key output
        if "engine done" in result.stdout:
            print("  → Engine completed all phases")
        if "arsenal.md" in result.stdout:
            print("  → Arsenal map generated")
        if "report.md" in result.stdout:
            print("  → Report generated")
    else:
        print(f"✗ Engine mock run: FAILED (exit {result.returncode})")
        print(f"  stderr: {result.stderr[:500]}")

if __name__ == "__main__":
    test_providers()
    test_llm_client()
    test_engine_integration()
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)