# X Search (OpenClaw Skill)

Search X (Twitter) posts using the xAI Grok API with real-time access to X content.

Forked from [Jaaneek/x-search](https://clawhub.ai/Jaaneek/x-search) with improvements:

## Improvements over original

- **Configurable model** — `--model` flag instead of hardcoded model
- **Rate limit retry** — automatic exponential backoff on 429 errors (up to 3 retries)
- **Response size limit** — prevents memory exhaustion from oversized responses (default 2MB, configurable via `--max-response`)
- **Reduced timeout** — 90s instead of 120s for faster failure feedback

## Setup

1. Get your API key: https://console.x.ai
2. Set environment variable:
   ```bash
   export XAI_API_KEY="xai-your-key-here"
   ```

## Usage

```bash
python3 scripts/search.py "what is trending in AI right now"

# Filter by handles
python3 scripts/search.py --handles elonmusk,OpenAI "latest posts"

# Date range
python3 scripts/search.py --from 2026-03-01 --to 2026-03-20 "AI news"

# Use a different model
python3 scripts/search.py --model grok-3 "trending topics"
```

## License

MIT
