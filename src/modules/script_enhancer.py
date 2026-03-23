"""
Script Enhancer Module - 脚本质量增强
即插即用：在 config.json 中设置 "modules_script_enhancer": true 启用

功能：
- 专业的 Shorts 脚本结构（Hook → 内容 → CTA）
- 自动控制节奏和时长
- 生成后自动润色
"""
from llm_provider import generate_text


def generate_enhanced_script(topic: str, language: str, sentence_count: int = 4) -> str:
    """Generate a high-quality YouTube Shorts script with viral structure."""
    prompt = (
        f"Write a YouTube Shorts script about: {topic}\n"
        f"Language: {language}\n\n"
        f"STRICT RULES:\n"
        f"1. Exactly {sentence_count} sentences\n"
        f"2. Structure:\n"
        f"   - Sentence 1: HOOK - shocking/surprising opening that stops scrolling\n"
        f"   - Sentence 2-{sentence_count-1}: CONTENT - deliver the facts with energy\n"
        f"   - Sentence {sentence_count}: CTA - end with a mind-blow or call to action\n"
        f"3. Use short, punchy sentences (max 15 words each)\n"
        f"4. Write for SPOKEN delivery (natural speech, not essay)\n"
        f"5. NO markdown, NO formatting, NO speaker labels\n"
        f"6. NO asterisks, NO quotes\n"
        f"7. Output ONLY the script text, nothing else\n"
    )

    script = generate_text(prompt)
    # Clean up
    script = script.replace("*", "").replace('"', "").strip()

    # Remove any accidental labels
    for label in ["HOOK:", "CONTENT:", "CTA:", "VOICEOVER:", "NARRATOR:", "VO:"]:
        script = script.replace(label, "")

    return script.strip()


def polish_script(script: str, language: str) -> str:
    """Polish an existing script for better flow and engagement."""
    prompt = (
        f"Polish this YouTube Shorts script for maximum engagement.\n"
        f"Language: {language}\n"
        f"Keep the same number of sentences. Make it punchier and more conversational.\n"
        f"Output ONLY the polished script, no explanation.\n\n"
        f"Script:\n{script}"
    )
    polished = generate_text(prompt)
    polished = polished.replace("*", "").replace('"', "").strip()
    return polished if len(polished) < 5000 else script
