#!/usr/bin/env python3
"""
llm_client.py — Model-agnostic LLM client for BugHunter engine.

Supports multiple providers:
- OpenRouter (Nemotron, DeepSeek, Qwen, Llama, etc.)
- OpenAI-compatible APIs (vLLM, TGI, LocalAI, etc.)
- Ollama (local models)
- Anthropic (for CVP-enrolled users)
- Azure OpenAI

Usage:
    client = LLMClient(provider="openrouter", model="nvidia/nemotron-3-ultra", api_key="sk-or-...")
    result = client.chat(system_prompt, user_prompt, max_tokens=4096, temperature=0.1)
"""
from __future__ import annotations
import os
import json
import time
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class LLMResponse:
    """Structured response from LLM call."""
    content: str
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    duration_s: float = 0.0


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        pass

    @abstractmethod
    def validate_config(self) -> tuple[bool, str]:
        """Return (is_valid, error_message)."""
        pass


class OpenRouterProvider(LLMProvider):
    """OpenRouter API — access to Nemotron, DeepSeek, Qwen, Llama, etc."""

    def __init__(self, model: str, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.model = model
        self.api_key = api_key
        self.base_url = (base_url or "https://openrouter.ai/api/v1").rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/sylncereyes/BugHunter-Skills",
            "X-Title": "Claude-BugHunter",
        }

    def validate_config(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "OPENROUTER_API_KEY not set"
        if not HAS_HTTPX:
            return False, "httpx not installed: pip install httpx"
        return True, ""

    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        valid, err = self.validate_config()
        if not valid:
            return LLMResponse("", error=err)

        t0 = time.time()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            with httpx.Client(timeout=300.0) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    usage={"prompt_tokens": usage.get("prompt_tokens", 0),
                           "completion_tokens": usage.get("completion_tokens", 0),
                           "total_tokens": usage.get("total_tokens", 0)},
                    model=self.model,
                    duration_s=round(time.time() - t0, 1)
                )
        except httpx.HTTPStatusError as e:
            return LLMResponse("", error=f"HTTP {e.response.status_code}: {e.response.text}", duration_s=round(time.time() - t0, 1))
        except Exception as e:
            return LLMResponse("", error=f"{type(e).__name__}: {e}", duration_s=round(time.time() - t0, 1))


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API (vLLM, TGI, LocalAI, Together, etc.)."""

    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def validate_config(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "API key not set"
        if not HAS_HTTPX:
            return False, "httpx not installed: pip install httpx"
        return True, ""

    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        valid, err = self.validate_config()
        if not valid:
            return LLMResponse("", error=err)

        t0 = time.time()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            with httpx.Client(timeout=300.0) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    usage={"prompt_tokens": usage.get("prompt_tokens", 0),
                           "completion_tokens": usage.get("completion_tokens", 0),
                           "total_tokens": usage.get("total_tokens", 0)},
                    model=self.model,
                    duration_s=round(time.time() - t0, 1)
                )
        except Exception as e:
            return LLMResponse("", error=f"{type(e).__name__}: {e}", duration_s=round(time.time() - t0, 1))


class OllamaProvider(LLMProvider):
    """Ollama local models (Nemotron, DeepSeek, Qwen, Llama, etc.)."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def validate_config(self) -> tuple[bool, str]:
        if not HAS_HTTPX:
            return False, "httpx not installed: pip install httpx"
        return True, ""

    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        valid, err = self.validate_config()
        if not valid:
            return LLMResponse("", error=err)

        t0 = time.time()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
            "stream": False,
        }

        try:
            with httpx.Client(timeout=600.0) as client:
                resp = client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["message"]["content"]
                return LLMResponse(
                    content=content,
                    model=self.model,
                    duration_s=round(time.time() - t0, 1)
                )
        except Exception as e:
            return LLMResponse("", error=f"{type(e).__name__}: {e}", duration_s=round(time.time() - t0, 1))


class AnthropicProvider(LLMProvider):
    """Anthropic API (requires CVP enrollment for offensive security)."""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def validate_config(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "ANTHROPIC_API_KEY not set"
        if not HAS_HTTPX:
            return False, "httpx not installed: pip install httpx"
        return True, ""

    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        valid, err = self.validate_config()
        if not valid:
            return LLMResponse("", error=err)

        t0 = time.time()
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        try:
            with httpx.Client(timeout=300.0) as client:
                resp = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["content"][0]["text"]
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    usage={"prompt_tokens": usage.get("input_tokens", 0),
                           "completion_tokens": usage.get("output_tokens", 0),
                           "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)},
                    model=self.model,
                    duration_s=round(time.time() - t0, 1)
                )
        except Exception as e:
            return LLMResponse("", error=f"{type(e).__name__}: {e}", duration_s=round(time.time() - t0, 1))


class ClaudeCLIProvider(LLMProvider):
    """Fallback: use `claude -p` CLI (original behavior, subject to cyber safeguards)."""

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model

    def validate_config(self) -> tuple[bool, str]:
        try:
            subprocess.run(["claude", "--version"], capture_output=True, check=True)
            return True, ""
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False, "`claude` CLI not found on PATH"

    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        valid, err = self.validate_config()
        if not valid:
            return LLMResponse("", error=err)

        # Combine system + user for claude -p
        task = f"{system}\n\n{user}\n\nEnd with a fenced ```json``` object."

        t0 = time.time()
        cmd = ["claude", "-p", task,
               "--max-turns", "40",
               "--model", self.model,
               "--output-format", "json",
               "--allowedTools", "Bash(curl:*) Bash(python3:*) Bash(jq:*) Bash(openssl:*) Bash(base64:*)",
               "--permission-mode", "bypassPermissions"]

        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if p.returncode != 0:
                return LLMResponse("", error=f"claude CLI exited {p.returncode}: {p.stderr[:200]}", duration_s=round(time.time() - t0, 1))
            data = json.loads(p.stdout)
            res = data.get("result", "")
            if "usage limit" in res.lower() or "session limit" in res.lower():
                return LLMResponse(res, error="rate-limited", duration_s=round(time.time() - t0, 1))
            return LLMResponse(res, model=self.model, duration_s=round(time.time() - t0, 1))
        except subprocess.TimeoutExpired:
            return LLMResponse("", error="timeout", duration_s=round(time.time() - t0, 1))
        except Exception as e:
            return LLMResponse("", error=f"{type(e).__name__}: {e}", duration_s=round(time.time() - t0, 1))


def create_provider(provider: str, model: str, **kwargs) -> LLMProvider:
    """Factory function to create LLM provider."""
    api_key = kwargs.pop("api_key", None)
    base_url = kwargs.pop("base_url", None)

    if provider == "ollama":
        return OllamaProvider(model, base_url=base_url or "http://localhost:11434")
    elif provider == "claude-cli":
        return ClaudeCLIProvider(model)
    elif provider == "openrouter":
        return OpenRouterProvider(model, api_key=api_key or "", base_url=base_url or "https://openrouter.ai/api/v1")
    elif provider == "openai":
        return OpenAICompatibleProvider(model, api_key=api_key or "", base_url=base_url or "https://api.openai.com/v1")
    elif provider == "anthropic":
        return AnthropicProvider(model, api_key=api_key or "")
    else:
        raise ValueError(f"Unknown provider: {provider}. Choose from: openrouter, ollama, openai, anthropic, claude-cli")


class LLMClient:
    """Main client — auto-detects provider from env or explicit args."""

    def __init__(self,
                 provider: Optional[str] = None,
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None):
        """
        Auto-config from env if not explicit:
        - PROVIDER: openrouter|openai|ollama|anthropic|claude-cli
        - MODEL: model name
        - API_KEY: OPENROUTER_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY
        - BASE_URL: for openai/ollama
        """
        self.provider_name = provider or os.environ.get("LLM_PROVIDER", "openrouter")
        self.model = model or os.environ.get("LLM_MODEL")
        self.api_key = api_key or os.environ.get("LLM_API_KEY") or \
                       os.environ.get("OPENROUTER_API_KEY") or \
                       os.environ.get("OPENAI_API_KEY") or \
                       os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")

        # Default models per provider
        defaults = {
            "openrouter": "nvidia/nemotron-3-ultra",
            "openai": "gpt-4o-mini",
            "ollama": "nemotron3-ultra",
            "anthropic": "claude-sonnet-4-20250514",
            "claude-cli": "claude-sonnet-4-6",
        }
        if not self.model:
            self.model = defaults.get(self.provider_name, "nvidia/nemotron-3-ultra")

        self.provider = create_provider(
            self.provider_name, self.model,
            api_key=self.api_key,
            base_url=self.base_url or ("http://localhost:11434" if self.provider_name == "ollama" else None)
        )

    def chat(self, system: str, user: str, max_tokens: int = 4096, temperature: float = 0.1) -> LLMResponse:
        return self.provider.chat(system, user, max_tokens, temperature)

    def validate(self) -> tuple[bool, str]:
        return self.provider.validate_config()


# Convenience function for simple usage
def run_llm(system: str, user: str, **kwargs) -> LLMResponse:
    """One-shot LLM call with auto-config."""
    client = LLMClient()
    return client.chat(system, user, **kwargs)


if __name__ == "__main__":
    # Self-test
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else "openrouter"
    model = sys.argv[2] if len(sys.argv) > 2 else None
    client = LLMClient(provider=provider, model=model)
    ok, msg = client.validate()
    print(f"Provider: {client.provider_name}")
    print(f"Model: {client.model}")
    print(f"Config: {'OK' if ok else 'FAIL'} — {msg}")
    if ok:
        resp = client.chat("You are a helpful assistant.", "Say 'hello' in JSON: {\"msg\": \"hello\"}")
        print(f"Response: {resp.content[:200]}")
        print(f"Error: {resp.error}")
        print(f"Duration: {resp.duration_s}s")