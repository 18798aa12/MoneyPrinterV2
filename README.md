# MoneyPrinter V2 — Enhanced Fork

> Forked from [FujiwaraChoki/MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2)

Automated YouTube Shorts + Twitter/X content generation and publishing, powered by **Gemini API** (free tier).

## What's New in This Fork

### Gemini API (No Local GPU Needed)
- Replaced Ollama (local LLM) with **Google Gemini API** for text and image generation
- **Multi-key rotation**: configure multiple API keys, auto-rotate when one hits quota
- Rate limiting (4.5s interval) + exponential backoff on 429 errors
- Also supports **OpenAI-compatible APIs** (GPT, Qwen, DeepSeek, Claude via proxy)

### YouTube Data API Upload
- Replaced Selenium browser upload with **YouTube Data API v3**
- No more "suspicious activity" blocks from Google when uploading from VPS/servers
- OAuth2 refresh token — authorize once, works forever
- Upload progress tracking

### 5 Plug-and-Play Modules
All modules can be toggled on/off in `config.json`:

| Module | What it does |
|--------|-------------|
| `topic_engine` | Deduplicates topics, generates 5 candidates with viral hooks |
| `script_enhancer` | Hook → Content → CTA structure, followed by polish pass |
| `seo_optimizer` | Generates viral titles with emoji + SEO descriptions |
| `image_prompts_pro` | 2-3 cinematic image prompts per sentence, 6 visual styles |
| `tweet_variety` | 6 tweet styles (shocking fact, hot take, question, mini list, story, myth buster) |

### Other Improvements
- **Twitter fix**: Dismiss hashtag autocomplete popup + JavaScript click (fixes silent post failures)
- **Twitter keepalive**: Script to prevent session expiration on headless VPS
- **Richer videos**: 7 sentences + ~16 images per video (configurable)
- **Non-blocking**: Song fetch failure no longer crashes the app
- **Pillow compatibility**: Works with Pillow 9.x (Pillow 10+ removed `ANTIALIAS`)

## Quick Start

### Prerequisites
- Python 3.11+
- Firefox + geckodriver (for Twitter only)
- ImageMagick (for subtitles)

### 1. Clone & Install

```bash
git clone https://github.com/18798aa12/MoneyPrinterV2.git
cd MoneyPrinterV2
cp config.example.json config.json
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
pip install google-auth google-auth-oauthlib google-api-python-client
pip install 'Pillow<10'    # Required for MoviePy compatibility
```

### 2. Get Gemini API Key (Free)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API Key**
3. Add to `config.json`:

```json
{
  "nanobanana2_api_key": "YOUR_KEY_HERE",
  "gemini_api_keys": [
    "KEY_1",
    "KEY_2",
    "KEY_3"
  ]
}
```

> **Tip**: Create multiple Google Cloud projects for more free quota. Each project gets independent limits (250 req/day for Flash).

### 3. Set Up YouTube API Upload

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Enable **YouTube Data API v3**
3. Create **OAuth client ID** → Desktop App
4. Download the `client_secret_*.json` file
5. Run the token script:

```bash
python get_youtube_token.py /path/to/client_secret.json
```

6. Copy the `refresh_token` to `config.json`:

```json
{
  "youtube_upload_method": "api",
  "youtube_client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "youtube_client_secret": "GOCSPX-...",
  "youtube_refresh_token": "1//..."
}
```

### 4. Set Up Twitter (Selenium)

1. Install Firefox
2. Create a Firefox profile and log in to [x.com](https://x.com)
3. Set the profile path in `config.json`:

```json
{
  "firefox_profile": "/path/to/firefox-profile"
}
```

### 5. Configure Modules

All enabled by default. Toggle in `config.json`:

```json
{
  "modules_topic_engine": true,
  "modules_script_enhancer": true,
  "modules_seo_optimizer": true,
  "modules_image_prompts_pro": true,
  "modules_tweet_variety": true
}
```

### 6. Run

```bash
# Interactive mode
python src/main.py

# Headless (for cron jobs)
python src/cron.py youtube <account_uuid>
python src/cron.py twitter <account_uuid>
```

## VPS Deployment (Headless)

For running on a VPS without GUI:

```bash
# Install dependencies
apt install firefox-esr xvfb imagemagick

# Fix ImageMagick security policy (required for subtitles)
sed -i 's|<policy domain="path" rights="none" pattern="@\*"/>|<!-- <policy domain="path" rights="none" pattern="@*" /> -->|' /etc/ImageMagick-6/policy.xml

# Start virtual display
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99

# Create Firefox profile on Linux
firefox-esr -CreateProfile "MPV2 /path/to/firefox-profile"
```

### Cron Schedule Example

```cron
# YouTube Shorts (2/day)
0 6 * * * /path/to/run_task.sh youtube <uuid>
0 18 * * * /path/to/run_task.sh youtube <uuid>

# Tweets (4/day)
0 8 * * * /path/to/run_task.sh twitter <uuid>
0 12 * * * /path/to/run_task.sh twitter <uuid>
0 16 * * * /path/to/run_task.sh twitter <uuid>
0 20 * * * /path/to/run_task.sh twitter <uuid>

# Keep Twitter session alive
0 */6 * * * cd /path/to/MoneyPrinterV2 && source venv/bin/activate && python keep_twitter_alive.py
```

### run_task.sh

```bash
#!/bin/bash
cd /path/to/MoneyPrinterV2
source venv/bin/activate
PLATFORM=$1
ACCOUNT_ID=$2
LOG=logs/${PLATFORM}_$(date +%Y%m%d_%H%M%S).log
mkdir -p logs
python src/cron.py $PLATFORM $ACCOUNT_ID >> $LOG 2>&1
```

## Gemini Free Tier Limits

| Model | RPM | Requests/Day | Best For |
|-------|-----|-------------|----------|
| gemini-2.5-flash | 10 | 250 | Default text generation |
| gemini-2.5-flash-lite | 15 | 1,000 | High-volume, simpler tasks |
| gemini-2.5-pro | 5 | 100 | Complex reasoning |
| Image generation | — | 500/day | Video images |

With 3 API keys, 2 videos + 4 tweets per day uses ~3% of quota.

## Config Reference

| Key | Description | Default |
|-----|-------------|---------|
| `ollama_model` | Model name for text generation | `gemini-2.5-flash` |
| `gemini_api_keys` | Array of Gemini API keys for rotation | `[]` |
| `youtube_upload_method` | `api` or `selenium` | `api` |
| `youtube_client_id` | OAuth2 client ID | `""` |
| `youtube_client_secret` | OAuth2 client secret | `""` |
| `youtube_refresh_token` | OAuth2 refresh token | `""` |
| `script_sentence_length` | Sentences per video script | `7` |
| `modules_*` | Enable/disable enhancement modules | `true` |
| `openai_api_key` | For GPT/Qwen/DeepSeek models | `""` |
| `openai_base_url` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |

## License

AGPL-3.0 — Same as the original project. See [LICENSE](LICENSE).

## Credits

- Original project: [FujiwaraChoki/MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2)
- [KittenTTS](https://github.com/KittenML/KittenTTS)

## Disclaimer

This project is for educational purposes only. The author is not responsible for any misuse of this software.
