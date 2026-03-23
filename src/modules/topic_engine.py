"""
Topic Engine Module - 话题去重 + 质量提升
即插即用：在 config.json 中设置 "modules_topic_engine": true 启用

功能：
- 记录已用话题，避免重复
- 生成多个候选话题，选最佳
- 添加 viral/hook 元素
"""
import os
import json
from llm_provider import generate_text

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".mp", "topic_history.json")


def _load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def _save_history(history: list):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-200:], f)  # Keep last 200


def generate_unique_topic(niche: str, language: str) -> str:
    """Generate a unique, high-engagement topic that hasn't been used before."""
    history = _load_history()
    recent = history[-30:] if history else []
    recent_str = "\n".join(f"- {t}" for t in recent) if recent else "None yet."

    prompt = (
        f"You are a viral YouTube Shorts content strategist.\n"
        f"Niche: {niche}\n"
        f"Language: {language}\n\n"
        f"Recently used topics (DO NOT repeat or use similar ones):\n{recent_str}\n\n"
        f"Generate 5 unique, click-worthy YouTube Shorts topic ideas.\n"
        f"Each topic should:\n"
        f"- Start with a HOOK (shocking fact, question, or bold claim)\n"
        f"- Be specific, not generic\n"
        f"- Have viral potential\n"
        f"- Be different from all recent topics\n\n"
        f"Format: one topic per line, numbered 1-5. No extra text."
    )

    response = generate_text(prompt)
    candidates = [line.strip().lstrip("0123456789.)- ") for line in response.strip().split("\n") if line.strip()]
    candidates = [c for c in candidates if c and len(c) > 10]

    # Pick the first candidate that's not too similar to history
    for candidate in candidates:
        if candidate.lower() not in [h.lower() for h in history]:
            history.append(candidate)
            _save_history(history)
            return candidate

    # Fallback: use first candidate anyway
    if candidates:
        history.append(candidates[0])
        _save_history(history)
        return candidates[0]

    return None
