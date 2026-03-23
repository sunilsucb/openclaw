#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Google's Gemini 3 Pro Image API.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--api-key KEY]
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Restrict output to current directory or below — no path traversal
FILENAME_UNSAFE_RE = re.compile(r"(^|[\\/])\.\.($|[\\/])")
MAX_PROMPT_LENGTH = 10000


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY")


def validate_filename(filename: str) -> Path:
    """Validate output filename to prevent path traversal."""
    if FILENAME_UNSAFE_RE.search(filename):
        print("Error: filename must not contain '..' path traversal.", file=sys.stderr)
        sys.exit(1)

    path = Path(filename)
    # Resolve and ensure it stays within or below cwd
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        resolved.relative_to(cwd)
    except ValueError:
        print(f"Error: output path must be within current directory ({cwd}).", file=sys.stderr)
        sys.exit(1)

    return path


def validate_prompt(prompt: str) -> str:
    """Validate prompt length."""
    if not prompt.strip():
        print("Error: prompt must not be empty.", file=sys.stderr)
        sys.exit(1)
    if len(prompt) > MAX_PROMPT_LENGTH:
        print(f"Error: prompt exceeds max length ({MAX_PROMPT_LENGTH} chars).", file=sys.stderr)
        sys.exit(1)
    return prompt


def validate_input_image(path_str: str) -> Path:
    """Validate input image exists, is a file, and is within reasonable size."""
    p = Path(path_str)
    if not p.exists():
        print(f"Error: input image not found: {path_str}", file=sys.stderr)
        sys.exit(1)
    if not p.is_file():
        print(f"Error: input image is not a file: {path_str}", file=sys.stderr)
        sys.exit(1)
    # 50MB limit for input images
    max_input_bytes = 50 * 1024 * 1024
    size = p.stat().st_size
    if size > max_input_bytes:
        print(f"Error: input image too large ({size} bytes, max {max_input_bytes}).", file=sys.stderr)
        sys.exit(1)
    if size == 0:
        print("Error: input image is empty (0 bytes).", file=sys.stderr)
        sys.exit(1)
    return p


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Gemini 3 Pro Image"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        help="Optional input image path for editing/modification"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (overrides GEMINI_API_KEY env var)"
    )
    parser.add_argument(
        "--model", "-m",
        default="gemini-3-pro-image-preview",
        help="Model to use (default: gemini-3-pro-image-preview)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=120,
        help="API timeout in seconds (default: 120)"
    )

    args = parser.parse_args()

    # Validate inputs
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    prompt = validate_prompt(args.prompt)
    output_path = validate_filename(args.filename)

    if args.timeout <= 0:
        print("Error: --timeout must be positive.", file=sys.stderr)
        sys.exit(1)

    # Import here after validation to avoid slow import on error
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    # Initialise client
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=args.timeout * 1000),
    )

    # Create parent directories
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input image if provided
    input_image = None
    output_resolution = args.resolution
    if args.input_image:
        img_path = validate_input_image(args.input_image)
        try:
            input_image = PILImage.open(img_path)
            # Force load to catch corrupt images early
            input_image.load()
            print(f"Loaded input image: {args.input_image}")

            # Auto-detect resolution if not explicitly set by user
            if args.resolution == "1K":  # Default value
                width, height = input_image.size
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                else:
                    output_resolution = "1K"
                print(f"Auto-detected resolution: {output_resolution} (from input {width}x{height})")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)

    # Build contents (image first if editing, prompt only if generating)
    if input_image:
        contents = [input_image, prompt]
        print(f"Editing image with resolution {output_resolution}...")
    else:
        contents = prompt
        print(f"Generating image with resolution {output_resolution}...")

    try:
        response = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    image_size=output_resolution
                )
            )
        )

        # Process response and convert to PNG
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                print(f"Model response: {part.text}")
            elif part.inline_data is not None:
                from io import BytesIO

                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    import base64
                    image_data = base64.b64decode(image_data)

                # Validate we got actual image data
                if not image_data or len(image_data) < 8:
                    print("Error: received empty or too-small image data from API.", file=sys.stderr)
                    sys.exit(1)

                image = PILImage.open(BytesIO(image_data))

                # Ensure RGB mode for PNG
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    rgb_image.save(str(output_path), 'PNG')
                elif image.mode == 'RGB':
                    image.save(str(output_path), 'PNG')
                else:
                    image.convert('RGB').save(str(output_path), 'PNG')
                image_saved = True

        if image_saved:
            full_path = output_path.resolve()
            print(f"\nImage saved: {full_path}")
        else:
            print("Error: No image was generated in the response.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
