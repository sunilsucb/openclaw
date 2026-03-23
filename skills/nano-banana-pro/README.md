# Nano Banana Pro (OpenClaw Skill)

Generate or edit images using Google's Gemini 3 Pro Image API.

Forked from [steipete/nano-banana-pro](https://clawhub.ai/steipete/nano-banana-pro) with security and usability improvements.

## Improvements over original

### Security Fixes
- **Path traversal protection** — output filename validated against `..` traversal; must stay within cwd
- **Input image validation** — checks existence, is-file, non-empty, and max size (50MB) before loading
- **Corrupt image detection** — forces `image.load()` to catch corrupt/truncated images early instead of failing silently later
- **Prompt length limit** — prevents abuse via massive prompts (10K char max)
- **Empty image data check** — validates API response contains actual image data before saving

### Usability Improvements
- **Configurable model** — `--model` flag instead of hardcoded model name
- **Configurable timeout** — `--timeout` flag (default 120s)
- **API client timeout** — passes timeout to the HTTP client instead of relying on system default

## Setup

1. Get your API key: https://aistudio.google.com/apikey
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```

## Usage

```bash
# Generate
uv run scripts/generate_image.py --prompt "a cat in space" --filename "space-cat.png"

# Edit
uv run scripts/generate_image.py --prompt "make it sunset" --filename "sunset.png" --input-image "photo.jpg"

# High-res with specific model
uv run scripts/generate_image.py --prompt "mountain landscape" --filename "mountains.png" --resolution 4K --model gemini-3-pro-image
```

## License

MIT
