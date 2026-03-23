"""
Module Loader - 模块加载器
读取 config.json 中的模块开关，按需加载增强功能。
"""
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_config() -> dict:
    config_path = os.path.join(ROOT_DIR, "config.json")
    with open(config_path, "r") as f:
        return json.load(f)


def is_enabled(module_name: str) -> bool:
    """Check if a module is enabled in config.json.

    Config key format: "modules_<module_name>": true/false
    Default: false (disabled)
    """
    config = _get_config()
    return config.get(f"modules_{module_name}", False)


# Convenience functions that check module status and call appropriate function

def get_topic(niche: str, language: str, fallback_fn=None) -> str:
    """Get topic via topic_engine module or fallback."""
    if is_enabled("topic_engine"):
        from modules.topic_engine import generate_unique_topic
        result = generate_unique_topic(niche, language)
        if result:
            return result
    return fallback_fn() if fallback_fn else None


def get_script(topic: str, language: str, sentence_count: int, fallback_fn=None) -> str:
    """Get script via script_enhancer module or fallback."""
    if is_enabled("script_enhancer"):
        from modules.script_enhancer import generate_enhanced_script, polish_script
        script = generate_enhanced_script(topic, language, sentence_count)
        if script:
            script = polish_script(script, language)
            return script
    return fallback_fn() if fallback_fn else None


def get_metadata(topic: str, script: str, language: str, fallback_fn=None) -> dict:
    """Get metadata via seo_optimizer module or fallback."""
    if is_enabled("seo_optimizer"):
        from modules.seo_optimizer import generate_viral_title, generate_seo_description
        return {
            "title": generate_viral_title(topic, script, language),
            "description": generate_seo_description(topic, script, language),
        }
    return fallback_fn() if fallback_fn else None


def get_image_prompts(script: str, topic: str, fallback_fn=None) -> list:
    """Get image prompts via image_prompts_pro module or fallback."""
    if is_enabled("image_prompts_pro"):
        from modules.image_prompts_pro import generate_pro_image_prompts
        import random
        prompts = generate_pro_image_prompts(script, topic, style_index=random.randint(0, 5))
        if prompts:
            return prompts
    return fallback_fn() if fallback_fn else None


def get_tweet(topic: str, language: str, fallback_fn=None) -> str:
    """Get tweet via tweet_variety module or fallback."""
    if is_enabled("tweet_variety"):
        from modules.tweet_variety import generate_diverse_tweet
        return generate_diverse_tweet(topic, language)
    return fallback_fn() if fallback_fn else None
