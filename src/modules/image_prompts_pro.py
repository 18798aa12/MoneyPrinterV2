"""
Image Prompts Pro Module - 图片提示词质量增强
即插即用：在 config.json 中设置 "modules_image_prompts_pro": true 启用

功能：
- 电影级画面描述
- 统一视觉风格
- 去重 + 安全过滤
"""
from llm_provider import generate_text

# Pre-built visual styles for consistency
VISUAL_STYLES = [
    "cinematic lighting, 4K, vibrant colors, dramatic composition",
    "neon-lit cyberpunk aesthetic, high contrast, moody atmosphere",
    "soft watercolor illustration, warm tones, dreamy quality",
    "hyper-realistic photography, shallow depth of field, golden hour",
    "bold pop-art style, flat colors, graphic novel aesthetic",
    "minimalist design, clean lines, pastel palette, modern",
]


def generate_pro_image_prompts(script: str, topic: str, style_index: int = 0) -> list:
    """Generate high-quality, visually consistent image prompts."""
    style = VISUAL_STYLES[style_index % len(VISUAL_STYLES)]

    # Count sentences to scale image count
    import re as _re
    sentence_count = len([s for s in _re.split(r'[.!?]+', script) if s.strip()])
    # 2-3 images per sentence for rich visual transitions
    target_count = max(sentence_count * 2, 10)
    if target_count > 20:
        target_count = 20

    prompt = (
        f"You are an expert visual director for YouTube Shorts.\n"
        f"Topic: {topic}\n"
        f"Script: {script}\n"
        f"Visual Style: {style}\n\n"
        f"Generate {target_count} image prompts for this video.\n"
        f"Rules:\n"
        f"1. Generate EXACTLY {target_count} prompts — 2-3 per sentence for smooth visual flow\n"
        f"2. Each prompt should be a detailed, cinematic visual description (2-3 sentences)\n"
        f"3. ALL prompts must follow the same visual style: {style}\n"
        f"4. NO text/words in images\n"
        f"5. NO violent, gory, disturbing, or NSFW content\n"
        f"6. NO real people or celebrities\n"
        f"7. Each prompt must show a DIFFERENT angle, perspective, or subject\n"
        f"8. Include a mix of: wide establishing shots, close-ups, dramatic angles, detail shots\n"
        f"9. Portrait orientation (9:16 aspect ratio)\n\n"
        f"Output as a JSON array of strings. ONLY the JSON array, nothing else."
    )

    response = generate_text(prompt)

    # Parse JSON
    import json
    import re

    response = response.replace("```json", "").replace("```", "").strip()
    try:
        prompts = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            try:
                prompts = json.loads(match.group())
            except json.JSONDecodeError:
                return []
        else:
            return []

    # Append style suffix to each prompt for consistency
    enhanced = []
    for p in prompts:
        if isinstance(p, str) and len(p) > 10:
            enhanced.append(f"{p}, {style}")
    return enhanced
