"""
Tweet Variety Module - 推文多样化
即插即用：在 config.json 中设置 "modules_tweet_variety": true 启用

功能：
- 多种推文风格轮换（事实、问题、列表、争议、幽默）
- 自动添加 hashtags
- 避免重复内容
"""
import os
import json
import random
from llm_provider import generate_text

TWEET_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".mp", "tweet_history.json")

TWEET_STYLES = [
    "shocking_fact",    # "Did you know...?"
    "hot_take",         # Bold opinion that sparks debate
    "question",         # Engaging question to drive replies
    "mini_list",        # "3 things about X that will blow your mind"
    "story",            # Micro-story in 2 sentences
    "myth_buster",      # "Everyone thinks X, but actually..."
]


def _load_tweet_history() -> list:
    if os.path.exists(TWEET_HISTORY_FILE):
        with open(TWEET_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def _save_tweet_history(history: list):
    os.makedirs(os.path.dirname(TWEET_HISTORY_FILE), exist_ok=True)
    with open(TWEET_HISTORY_FILE, "w") as f:
        json.dump(history[-500:], f)


def generate_diverse_tweet(topic: str, language: str) -> str:
    """Generate a diverse, engaging tweet with rotating styles."""
    style = random.choice(TWEET_STYLES)
    history = _load_tweet_history()
    recent = history[-10:]
    recent_str = "\n".join(f"- {t}" for t in recent) if recent else "None yet."

    style_instructions = {
        "shocking_fact": "Start with 'Did you know' or a shocking statistic. Deliver one mind-blowing fact.",
        "hot_take": "Share a bold, slightly controversial opinion. Be confident but not offensive.",
        "question": "Ask an engaging question that makes people want to reply. Then give a teaser answer.",
        "mini_list": "List 3 surprising things about the topic. Use emojis as bullet points.",
        "story": "Tell a fascinating micro-story in exactly 2 sentences. Make it vivid.",
        "myth_buster": "Start with 'Everyone thinks...' then reveal the surprising truth.",
    }

    prompt = (
        f"Write a viral tweet about: {topic}\n"
        f"Language: {language}\n"
        f"Style: {style_instructions[style]}\n\n"
        f"Rules:\n"
        f"- Max 250 characters (STRICT)\n"
        f"- Add 2-3 relevant hashtags\n"
        f"- Make it engaging and shareable\n"
        f"- NO quotes or asterisks\n"
        f"- Different from these recent tweets:\n{recent_str}\n\n"
        f"Output ONLY the tweet text."
    )

    tweet = generate_text(prompt).strip().replace('"', "").replace("*", "")

    if len(tweet) > 275:
        tweet = tweet[:272] + "..."

    history.append(tweet[:50])
    _save_tweet_history(history)
    return tweet
