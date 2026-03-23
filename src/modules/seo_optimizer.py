"""
SEO Optimizer Module - 标题/描述/标签优化
即插即用：在 config.json 中设置 "modules_seo_optimizer": true 启用

功能：
- 生成高 CTR 标题（含 emoji + 数字 + 关键词）
- SEO 优化描述（含关键词和 hashtag）
- 自动生成 tags
"""
from llm_provider import generate_text


def generate_viral_title(topic: str, script: str, language: str) -> str:
    """Generate a viral, SEO-optimized YouTube Shorts title."""
    prompt = (
        f"Generate a viral YouTube Shorts title.\n"
        f"Topic: {topic}\n"
        f"Language: {language}\n\n"
        f"Rules:\n"
        f"- Max 70 characters (STRICT)\n"
        f"- Include 1-2 relevant emojis\n"
        f"- Use power words (shocking, insane, secret, etc.)\n"
        f"- Include numbers if relevant\n"
        f"- Add 1-2 hashtags at the end\n"
        f"- Make people NEED to click\n"
        f"- Output ONLY the title, nothing else"
    )
    title = generate_text(prompt).strip().replace('"', "").replace("*", "")

    # Enforce 100 char limit
    if len(title) > 100:
        title = title[:97] + "..."
    return title


def generate_seo_description(topic: str, script: str, language: str) -> str:
    """Generate an SEO-optimized YouTube description."""
    prompt = (
        f"Write a YouTube Shorts description for SEO.\n"
        f"Topic: {topic}\n"
        f"Script summary: {script[:200]}\n"
        f"Language: {language}\n\n"
        f"Rules:\n"
        f"- 2-3 short lines\n"
        f"- Include relevant keywords naturally\n"
        f"- Add 5-8 hashtags at the end\n"
        f"- Include a CTA (like, follow, comment)\n"
        f"- Output ONLY the description"
    )
    return generate_text(prompt).strip().replace("*", "")


def generate_tags(topic: str, niche: str) -> list:
    """Generate relevant tags for the video."""
    prompt = (
        f"Generate 10 YouTube tags for a Shorts video.\n"
        f"Topic: {topic}\n"
        f"Niche: {niche}\n"
        f"Output comma-separated tags only, no numbering."
    )
    response = generate_text(prompt).strip()
    return [t.strip() for t in response.split(",") if t.strip()]
