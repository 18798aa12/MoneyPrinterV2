import time
import json
import os
import requests

from config import (
    get_nanobanana2_api_key,
    get_nanobanana2_api_base_url,
    get_ollama_base_url,
    get_openai_api_key,
    get_openai_base_url,
)

# Rate limiting: track last request time, enforce min interval
_last_request_time = 0
_MIN_REQUEST_INTERVAL = 4.5  # seconds (15 RPM = 1 per 4s, add buffer)

_selected_model: str | None = None

# Gemini API key rotation
_gemini_key_index = 0
_exhausted_keys: dict[str, float] = {}  # key -> timestamp when exhausted
_KEY_COOLDOWN = 3600  # 1 hour before retrying an exhausted key

# Model prefix routing:
#   gemini-*          → Gemini API
#   gpt-* / o1-* / o3-* / o4-*  → OpenAI API
#   qwen-*            → OpenAI-compatible (Qwen/DashScope)
#   deepseek-*        → OpenAI-compatible (DeepSeek)
#   claude-*          → OpenAI-compatible (Anthropic via proxy)
#   everything else   → Ollama (local)

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

OPENAI_COMPATIBLE_PREFIXES = ("gpt-", "o1-", "o3-", "o4-", "qwen-", "deepseek-", "claude-")


def _is_gemini_model(model: str) -> bool:
    return model.startswith("gemini")


def _is_openai_compatible(model: str) -> bool:
    return any(model.startswith(p) for p in OPENAI_COMPATIBLE_PREFIXES)


def _get_gemini_keys() -> list[str]:
    """Get all Gemini API keys from config (gemini_api_keys list + fallback to single key)."""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(root_dir, "config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        keys = config.get("gemini_api_keys", [])
        if keys:
            return [k for k in keys if k]
    except Exception:
        pass
    # Fallback to single key
    single = get_nanobanana2_api_key()
    return [single] if single else []


def _get_next_gemini_key() -> str:
    """Get next available Gemini API key, skipping exhausted ones."""
    global _gemini_key_index
    keys = _get_gemini_keys()
    if not keys:
        raise RuntimeError("No Gemini API keys configured.")

    now = time.time()
    # Clear keys that have cooled down
    for k in list(_exhausted_keys):
        if now - _exhausted_keys[k] > _KEY_COOLDOWN:
            del _exhausted_keys[k]

    # Try each key starting from current index
    for _ in range(len(keys)):
        key = keys[_gemini_key_index % len(keys)]
        _gemini_key_index = (_gemini_key_index + 1) % len(keys)
        if key not in _exhausted_keys:
            return key

    # All keys exhausted — find the one that will recover soonest
    earliest_key = min(_exhausted_keys, key=lambda k: _exhausted_keys[k])
    wait = _KEY_COOLDOWN - (now - _exhausted_keys[earliest_key])
    raise RuntimeError(
        f"All {len(keys)} Gemini API keys exhausted. "
        f"Earliest recovery in {int(wait)}s. "
        f"Add more keys to gemini_api_keys in config.json."
    )


def _mark_key_exhausted(key: str):
    """Mark a key as exhausted (spending cap / daily limit hit)."""
    _exhausted_keys[key] = time.time()
    print(f"[Key rotation] Key ...{key[-8:]} exhausted, rotating to next key.")


def list_models() -> list[str]:
    """Lists available models (Gemini + Ollama if reachable)."""
    models = list(GEMINI_MODELS)
    try:
        import ollama
        client = ollama.Client(host=get_ollama_base_url())
        response = client.list()
        models.extend(sorted(m.model for m in response.models))
    except Exception:
        pass
    return models


def select_model(model: str) -> None:
    global _selected_model
    _selected_model = model


def get_active_model() -> str | None:
    return _selected_model


def _rate_limit():
    """Enforce minimum interval between Gemini API requests."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def _generate_gemini(prompt: str, model: str, max_retries: int = 3) -> str:
    base_url = get_nanobanana2_api_base_url().rstrip("/")
    endpoint = f"{base_url}/models/{model}:generateContent"

    keys = _get_gemini_keys()
    total_attempts = max_retries * max(len(keys), 1)

    for attempt in range(total_attempts):
        api_key = _get_next_gemini_key()
        _rate_limit()

        response = requests.post(
            endpoint,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60,
        )

        if response.status_code == 429:
            error_body = {}
            try:
                error_body = response.json().get("error", {})
            except Exception:
                pass

            msg = error_body.get("message", "")
            # "spending cap" or "quota" = key is done for the day → rotate
            if "spending" in msg.lower() or "quota" in msg.lower() or "exhausted" in msg.lower():
                _mark_key_exhausted(api_key)
                continue  # Try next key immediately

            # Regular rate limit (RPM) → wait and retry with same pool
            wait = 30 * (attempt + 1)
            if wait > 120:
                wait = 120
            print(f"[Rate limited] Waiting {wait}s before retry {attempt + 1}/{total_attempts}...")
            time.sleep(wait)
            continue

        response.raise_for_status()

        body = response.json()
        for candidate in body.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if text := part.get("text"):
                    return text.strip()

        raise RuntimeError(f"Gemini returned no text. Response: {body}")

    raise RuntimeError(
        f"Gemini API failed after {total_attempts} attempts. "
        f"Keys available: {len(keys)}, exhausted: {len(_exhausted_keys)}. "
        f"Add more keys to gemini_api_keys in config.json."
    )


def _generate_openai_compatible(prompt: str, model: str) -> str:
    """OpenAI-compatible API — works with GPT, Qwen, DeepSeek, Claude (via proxy), etc."""
    api_key = get_openai_api_key()
    base_url = get_openai_base_url().rstrip("/")

    if not api_key:
        raise RuntimeError("No OpenAI API key. Set openai_api_key in config.json.")

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()

    body = response.json()
    return body["choices"][0]["message"]["content"].strip()


def _generate_ollama(prompt: str, model: str) -> str:
    import ollama
    client = ollama.Client(host=get_ollama_base_url())
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()


def generate_text(prompt: str, model_name: str = None) -> str:
    """
    Generates text using the appropriate provider based on model name prefix.

    Routing:
        gemini-*                    → Google Gemini API
        gpt-*/o1-*/qwen-*/deepseek-*/claude-* → OpenAI-compatible API
        everything else             → Local Ollama
    """
    model = model_name or _selected_model
    if not model:
        model = "gemini-2.5-flash"

    if _is_gemini_model(model):
        return _generate_gemini(prompt, model)
    elif _is_openai_compatible(model):
        return _generate_openai_compatible(prompt, model)
    else:
        return _generate_ollama(prompt, model)
