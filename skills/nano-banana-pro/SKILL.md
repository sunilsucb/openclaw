---
name: nano-banana-pro
description: Generate or edit images using Google's Gemini 3 Pro Image API. Use when the user wants to create images, edit photos, generate art, or modify existing images with AI.
homepage: https://ai.google.dev/
metadata:
  {
    "openclaw":
      {
        "emoji": "🍌",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Nano Banana Pro — Image Generation & Editing

Generate new images or edit existing ones using Google's Gemini 3 Pro Image API.

## Setup

1. Get your API key: https://aistudio.google.com/apikey
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```
3. Or set `skills."nano-banana-pro".apiKey` / `skills."nano-banana-pro".env.GEMINI_API_KEY` in `~/.openclaw/openclaw.json`

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**Edit existing image:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**Additional flags:**
```bash
# Use a different model
uv run {baseDir}/scripts/generate_image.py --prompt "..." --filename "out.png" --model gemini-3-pro-image

# Set API timeout (seconds, default 120)
uv run {baseDir}/scripts/generate_image.py --prompt "..." --filename "out.png" --timeout 180
```

Important: Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Default Workflow (draft → iterate → final)

Goal: fast iteration without burning time on 4K until the prompt is correct.

1. **Draft (1K):** quick feedback loop
   ```bash
   uv run {baseDir}/scripts/generate_image.py --prompt "..." --filename "yyyy-mm-dd-hh-mm-ss-draft.png" --resolution 1K
   ```

2. **Iterate:** adjust prompt in small diffs; keep filename new per run. If editing: keep the same `--input-image` for every iteration until happy.

3. **Final (4K):** only when prompt is locked
   ```bash
   uv run {baseDir}/scripts/generate_image.py --prompt "..." --filename "yyyy-mm-dd-hh-mm-ss-final.png" --resolution 4K
   ```

## Resolution Options

- **1K** (default) — ~1024px resolution
- **2K** — ~2048px resolution
- **4K** — ~4096px resolution

When editing, resolution auto-detects from input image if not explicitly set.

## Filename Generation

Format: `{timestamp}-{descriptive-name}.png`

Examples:
- "A serene Japanese garden" → `2025-11-23-14-23-05-japanese-garden.png`
- "sunset over mountains" → `2025-11-23-15-30-12-sunset-mountains.png`

## Notes

- Output is always PNG format
- RGBA images are converted to RGB with white background
- Input images for editing are validated for existence and size (max 50MB)
- Output filenames are validated against path traversal
