---
name: career-ops-llm
description: Use when you need to generate text from the currently active LLM (whatever model the Hermes harness is pointed at). The skill reads the model endpoint and auth from the environment / Hermes config and makes a single OpenAI-compatible chat completion call.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Career Ops LLM Wrapper — Model-agnostic text generation

This skill provides a single, reusable tool:

```
llm_generate(
    prompt: str,
    system: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = 2048
) -> str
```

It works with any endpoint that follows the **OpenAI chat-completion** schema:

```
POST {base_url}/v1/chat/completions
Headers: Authorization: Bearer ***
Body: {
    "model": "<model_name_or_empty>",
    "messages": [
        {"role":"system", "content": system or ""},
        {"role":"user",   "content": prompt}
    ],
    "temperature": temperature,
    "max_tokens": max_tokens   # optional – omit for model default
}
```

### Where the configuration comes from

| Source | Priority | What it provides |
|--------|----------|------------------|
| **Environment variable** `HERMES_LLM_ENDPOINT` | 1️⃣ | Full base URL, e.g. `https://ollama.com/v1` or `https://openrouter.ai/api/v1` |
| **Environment variable** `HERMES_LLM_API_KEY` | 1️⃣ | Bearer token for the endpoint |
| **Environment variable** `HERMES_LLM_MODEL` | 2️⃣ | Model name to send in the body (if empty, the model field is omitted – many proxies will use their default) |
| **Hermes config file** `~/.hermes/config.yaml` (keys `llm.endpoint`, `llm.api_key`, `llm.model`) | 3️⃣ | Fallback if the env vars are not set |
| **Hard-coded defaults** (only for local testing) | 4️⃣ | `endpoint: http://127.0.0.1:11434/v1`, `model: ""` |

> **Why this works everywhere:** All the providers you'll encounter in a Hermes harness (Ollama-Cloud, OpenRouter, local Ollama, LMStudio, etc.) expose an OpenAI-compatible chat endpoint. The wrapper therefore only needs to know the *base URL* and an *API key*; the model name is optional and can be left blank so the proxy picks its default.

### Internal implementation (Python)

The skill ships a small helper script `scripts/llm_call.py` that the skill's `execute_code` entry point invokes.

```python
# skills/career-ops-llm/scripts/llm_call.py
import os, json, sys
from hermes_tools import terminal   # Hermes-provided tool for shell calls

def _get_cfg():
    # 1️⃣ Environment
    endpoint = os.getenv("HERMES_LLM_ENDPOINT")
    api_key  = os.getenv("HERMES_LLM_API_KEY")
    model    = os.getenv("HERMES_LLM_MODEL")
    # 2️⃣ Hermes config fallback (read yaml if pyyaml is available)
    if not endpoint or not api_key:
        try:
            import yaml
            cfg_path = os.path.expanduser("~/.hermes/config.yaml")
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f) or {}
            llm = cfg.get("llm", {})
            endpoint = endpoint or llm.get("endpoint")
            api_key  = api_key  or llm.get("api_key")
            model    = model    or llm.get("model")
        except Exception:
            pass   # ignore – we'll fall back to defaults below
    # 3️⃣ Local dev defaults (only used when nothing else is set)
    if not endpoint:
        endpoint = "http://127.0.0.1:11434/v1"
    if not api_key:
        api_key = ""   # many local Ollama instances don't require a key
    if not model:
        model = ""     # empty lets the proxy choose its default
    return endpoint.rstrip("/"), api_key, model

def llm_generate(prompt, system=None, temperature=0.7, max_tokens=None):
    base_url, api_key, model = _get_cfg()
    url = f"{base_url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system or ""},
            {"role": "user",   "content": prompt}
        ],
        "temperature": temperature
    }
    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    # Build curl command – we use the terminal tool because it can do HTTPS
    curl_cmd = (
        f'curl -sS -X POST "{url}" '
        f'-H "Content-Type: application/json" '
        f'{f"-H \"Authorization: Bearer ***\"" if api_key else ""} '
        f'-d \'{json.dumps(data)}\''
    )
    result = terminal(command=curl_cmd, timeout=120)
    if result["exit_code"] != 0:
        raise RuntimeError(f"LLM call failed: {result['error']}")
    try:
        resp = json.loads(result["output"])
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Could not parse LLM response: {e}\nRaw: {result['output']}")

if __name__ == "__main__":
    # Simple CLI for manual testing:  python llm_call.py "Say hello"
    if len(sys.argv) < 2:
        print("Usage: llm_call.py '<prompt>' [system] [temp] [max_tokens]")
        sys.exit(1)
    prompt = sys.argv[1]
    system = sys.argv[2] if len(sys.argv) > 2 else None
    temp   = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
    max_tok = int(sys.argv[4]) if len(sys.argv) > 4 else None
    print(llm_generate(prompt, system=system, temperature=temp, max_tokens=max_tok))
```

**How the skill is used**

From any other skill or from your own Python code you simply do:

```python
from hermes_tools import execute_code

def llm_generate(prompt, system=None, temperature=0.7, max_tokens=None):
    # This runs the wrapper skill in a sub-process and returns the string.
    code = f"""
import json, sys
sys.path.insert(0, '{os.path.expanduser("~/Documents/job-getter/skills/career-ops-llm/scripts")}')
from llm_call import llm_generate
print(llm_generate({json.dumps(prompt)!r},
                   system={json.dumps(system)!r},
                   temperature={temperature},
                   max_tokens={max_tokens}))
    """
    out = execute_code(code=code, reset=False)
    return out["content"].strip()
```

You can now replace every place where a skill previously called `deepseek-v4-pro` (or any hard-coded model) with a call to the helper above.
