---
name: Word / DOCX
slug: word-docx
version: 1.1.0
description: "Create, inspect, read, validate, and edit Microsoft Word .docx files. Use when the task involves Word documents, tracked changes, comments, headers, numbering, fields, tables, templates, or compatibility checks."
metadata:
  {
    "openclaw":
      {
        "emoji": "📘",
        "os": ["linux", "darwin", "win32"],
        "requires": { "bins": ["uv"] },
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

## When to Use

Use when the main artifact is a Microsoft Word document or `.docx` file, especially when tracked changes, comments, headers, numbering, fields, tables, templates, or compatibility matter.

## Tools

### Read document text
```bash
uv run {baseDir}/scripts/docx_tool.py read <file.docx>
```
Extracts all text, styles, and table content as JSON.

### Inspect document structure
```bash
uv run {baseDir}/scripts/docx_tool.py inspect <file.docx>
```
Shows styles, sections, page layout, ZIP parts, and safety warnings.

### Validate document safety
```bash
uv run {baseDir}/scripts/docx_tool.py validate <file.docx>
```
Checks for zip bombs, macros, path traversal in ZIP entries, and suspicious content. Always run this before processing untrusted .docx files.

### Create new document
```bash
uv run {baseDir}/scripts/docx_tool.py create <output.docx> --title "Title" --body "Paragraph 1" "Paragraph 2" --font Calibri --font-size 11
```

## Safety

- **Always validate untrusted .docx files before reading/editing** — they are ZIP archives that can contain zip bombs or macros.
- Max input file size: 100MB
- Zip bomb detection: max 100x decompression ratio, max 5000 entries
- `.docm` / `.dotm` / `.doc` files flagged as potentially dangerous
- Output paths validated against directory traversal

## Core Rules

### 1. Treat DOCX as OOXML, not plain text
- A `.docx` file is a ZIP of XML parts, so structure matters as much as visible text.
- Text may be split across multiple runs; never assume one word or sentence lives in one XML node.
- Use different workflows: structured extraction for reading, style-driven generation for new files, OOXML-aware editing for fragile existing documents.
- Legacy `.doc` inputs usually need conversion before you can trust modern `.docx` assumptions.

### 2. Preserve styles and direct formatting deliberately
- Prefer named styles over direct formatting so the document stays editable.
- When editing an existing file, extend the current style system instead of inventing a parallel one.
- Copying content between documents can silently import foreign styles and numbering definitions.

### 3. Lists and numbering are their own system
- Bullets and numbering belong to Word's numbering definitions, not pasted Unicode characters.
- A list that looks correct in one editor can restart, flatten, or renumber itself later if the underlying numbering state is wrong.

### 4. Page layout lives in sections
- Margins, orientation, headers, footers, and page numbering are section-level behavior.
- Set page size explicitly because A4 and US Letter defaults change pagination and table widths.
- Table geometry depends on page width, margins, and fixed widths.

### 5. Track changes, comments, and fields need precise edits
- Visible text is not the full document when tracked changes are enabled.
- For review workflows, make minimal replacements instead of rewriting whole paragraphs.
- In tracked-change workflows, only the changed span should look changed.
- For legal, academic, or business review documents, default to review-style edits.

### 6. Verify round-trip compatibility before delivery
- Complex documents can shift between Word, LibreOffice, Google Docs, and conversion tools.
- When layout matters, explicit table widths are safer than auto-fit.

## Common Traps

- Copy-paste can import unwanted styles and numbering definitions.
- Header/footer images use part-specific relationships; reusing IDs blindly breaks them.
- One visible phrase can be split across several runs, bookmarks, revision tags, or field boundaries.
- Replacing a whole paragraph to change one clause often breaks review quality, bookmarks, and formatting.
- Table auto-fit behavior can drift between Word, Google Docs, and LibreOffice.
- A document that passes a text check can still fail on pagination, table widths, or reference refresh.
