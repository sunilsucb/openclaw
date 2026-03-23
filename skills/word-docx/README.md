# Word / DOCX (OpenClaw Skill)

Create, inspect, read, validate, and edit Microsoft Word .docx files.

Forked from [ivangdavila/word-docx](https://clawhub.ai/ivangdavila/word-docx) with tooling and security additions.

## Improvements over original

### Added Tooling (original was knowledge-only)
- **`read`** — Extract text and table content as JSON
- **`inspect`** — Show document structure (styles, sections, ZIP parts)
- **`validate`** — Safety checks before processing untrusted files
- **`create`** — Generate new .docx documents with title, body, font options

### Security Additions
- **Zip bomb detection** — checks decompression ratio (max 100x) and entry count (max 5000)
- **Macro detection** — flags VBA projects and .bin files inside the archive
- **Path traversal protection** — validates both ZIP entry paths and output file paths
- **File size limits** — max 100MB input
- **Legacy format warnings** — .docm, .dotm, .doc flagged as higher risk

### Knowledge Improvements
- Condensed core rules (kept all substance, removed redundancy)
- Added safety-first workflow: always validate untrusted files before processing

## Usage

```bash
# Read document text
uv run scripts/docx_tool.py read report.docx

# Inspect structure
uv run scripts/docx_tool.py inspect report.docx

# Validate safety
uv run scripts/docx_tool.py validate untrusted-file.docx

# Create new document
uv run scripts/docx_tool.py create output.docx --title "My Report" --body "First paragraph" "Second paragraph"
```

## License

MIT
