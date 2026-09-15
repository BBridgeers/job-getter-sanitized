# skills/career-ops-llm/scripts/llm_call.py
import os, json, sys

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

    # Build curl command
    import subprocess
    curl_cmd = [
        "curl", "-sS", "-X", "POST", url,
        "-H", "Content-Type: application/json"
    ]
    if api_key:
        curl_cmd.extend(["-H", f"Authorization: Bearer {api_key}"])
    curl_cmd.extend(["-d", json.dumps(data)])
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"LLM call failed: {result.stderr}")
    try:
        resp = json.loads(result.stdout)
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Could not parse LLM response: {e}\nRaw: {result.stdout}")

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
