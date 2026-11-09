#!/usr/bin/env python3
"""
agent.py — the engine's LLM dispatch. Only recon/hunt/validate are model-driven;
the orchestrator, scope, and state are deterministic code.

Supports multiple LLM providers via llm_client.py:
- OpenRouter (Nemotron, DeepSeek, Qwen, Llama, etc.)
- OpenAI-compatible (vLLM, TGI, LocalAI, Together, etc.)
- Ollama (local models)
- Anthropic (requires CVP enrollment)
- Claude CLI (fallback, subject to cyber safeguards)

Agents are asked to end with a fenced ```json``` block which we parse into structured data.
"""
import json
import os
import re
import sys
import time

# Add engine dir to path for llm_client import
ENGINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ENGINE)
from llm_client import LLMClient, LLMResponse

# Burp MCP config (used when provider supports tool calling)
MCP_CONFIG = os.path.join(ENGINE, "burp-mcp.json")
ALLOWED_TOOLS = " ".join([
    "mcp__burp__send_http1_request", "mcp__burp__send_http2_request",
    "mcp__burp__get_collaborator_interactions", "mcp__burp__generate_collaborator_payload",
    "Bash(curl:*)", "Bash(python3:*)", "Bash(jq:*)", "Bash(openssl:*)", "Bash(base64:*)",
])


# Global client instance (lazy init)
_CLIENT: LLMClient | None = None


def get_client(provider: str | None = None, model: str | None = None, base_url: str | None = None) -> LLMClient:
    """Get or create LLM client with optional override."""
    global _CLIENT
    if _CLIENT is None or provider or model or base_url:
        _CLIENT = LLMClient(provider=provider, model=model, base_url=base_url)
    return _CLIENT


def run_agent(task, skills_on=False, model="claude-sonnet-4-6", max_turns=40, timeout=600,
              provider: str | None = None, use_mcp: bool = False, base_url: str | None = None):
    """
    Run an agent task with the configured LLM provider.

    Args:
        task: The task prompt (system + user combined)
        skills_on: Whether to enable slash commands (not used for non-Claude providers)
        model: Model name (overrides env)
        max_turns: Max conversation turns (Claude CLI only)
        timeout: Request timeout in seconds
        provider: Explicit provider override (openrouter, ollama, anthropic, claude-cli, openai)
        use_mcp: Whether to include Burp MCP tools (Claude CLI only)

    Returns:
        Dict with: result, error, duration_s, cost_usd, num_turns
    """
    client = get_client(provider=provider, model=model, base_url=base_url)

    # For non-Claude providers, we don't have MCP tool calling.
    # The task prompt already includes curl-first instructions.
    # If use_mcp=True and provider is claude-cli, we could add MCP config.
    # For now, all providers use curl-first approach via prompt instructions.

    t0 = time.time()

    # Validate config first
    ok, msg = client.validate()
    if not ok:
        return {"result": "", "error": f"config: {msg}", "duration_s": round(time.time() - t0, 1)}

    # Ensure task ends with JSON instruction
    if "```json" not in task:
        task += '\n\nEnd with a fenced ```json``` object.'

    try:
        resp: LLMResponse = client.chat(
            system="You are a senior bug hunter / red team operator. Follow the rules of engagement strictly.",
            user=task,
            max_tokens=8192,
            temperature=0.1
        )
    except Exception as e:
        return {"result": "", "error": f"llm_client:{type(e).__name__}: {e}", "duration_s": round(time.time() - t0, 1)}

    duration = round(time.time() - t0, 1)

    if resp.error:
        return {"result": resp.content, "error": resp.error, "duration_s": duration}

    # Check for rate limiting in response
    if "usage limit" in resp.content.lower() or "session limit" in resp.content.lower():
        return {"result": resp.content, "error": "rate-limited", "duration_s": duration}

    return {
        "result": resp.content,
        "cost_usd": 0.0,  # Could calculate from usage if provider returns it
        "num_turns": 1,   # Single-turn for API providers
        "error": None,
        "duration_s": duration,
    }


def extract_json(text):
    """Pull the last valid JSON array/object out of an agent reply."""
    if not text:
        return None
    blocks = re.findall(r"```json\s*(.*?)```", text, re.S)
    blocks += re.findall(r"```\s*(\[.*?\]|\{.*?\})\s*```", text, re.S)
    for b in reversed(blocks):
        try:
            return json.loads(b.strip())
        except Exception:
            pass
    for b in reversed(re.findall(r"(\[.*\]|\{.*\})", text, re.S)):
        try:
            return json.loads(b)
        except Exception:
            pass
    return None


if __name__ == "__main__":
    # offline self-test of the JSON extractor (no agent call)
    assert extract_json('blah ```json\n[{"a":1}]\n``` end') == [{"a": 1}]
    assert extract_json('text {"x": "y"} more') == {"x": "y"}
    assert extract_json("no json here") is None
    assert extract_json('first {"a":1} then ```json\n{"b":2}\n```') == {"b": 2}  # prefers fenced/last
    print("agent.py extractor self-test: PASS")

    # Test client init
    client = get_client()
    ok, msg = client.validate()
    print(f"LLM Client: {client.provider_name} / {client.model} — {'OK' if ok else 'FAIL'}: {msg}")


def extract_json(text):
    """Pull the last valid JSON array/object out of an agent reply."""
    if not text:
        return None
    blocks = re.findall(r"```json\s*(.*?)```", text, re.S)
    blocks += re.findall(r"```\s*(\[.*?\]|\{.*?\})\s*```", text, re.S)
    for b in reversed(blocks):
        try:
            return json.loads(b.strip())
        except Exception:
            pass
    for b in reversed(re.findall(r"(\[.*\]|\{.*\})", text, re.S)):
        try:
            return json.loads(b)
        except Exception:
            pass
    return None


if __name__ == "__main__":
    # offline self-test of the JSON extractor (no agent call)
    assert extract_json('blah ```json\n[{"a":1}]\n``` end') == [{"a": 1}]
    assert extract_json('text {"x": "y"} more') == {"x": "y"}
    assert extract_json("no json here") is None
    assert extract_json('first {"a":1} then ```json\n{"b":2}\n```') == {"b": 2}  # prefers fenced/last
    print("agent.py extractor self-test: PASS")
