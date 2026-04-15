# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A desktop tool for generating standardized task descriptions for digital marketing campaigns. It parses structured campaign names, fetches video assets from Google Sheets, and publishes tasks to Notion.

## Architecture

The app has two components:

- **`app.py`** — Python launcher that copies the HTML file to a writable location and opens it in Microsoft Edge app mode (`--app=file:///...`) with `--disable-web-security` to allow cross-origin API calls. Packaged into `dist/app.exe` via PyInstaller (`app.spec`).
- **`campaign-task-generator.html`** — The entire frontend: a single-file vanilla JS SPA. This is the main file to edit. `view_generator.html` is just a runtime copy and should not be edited directly.

## Building the Executable

```bash
pyinstaller app.spec
```

Output: `dist/app.exe`. The spec bundles `campaign-task-generator.html` as embedded data inside the executable.

## Frontend Architecture (`campaign-task-generator.html`)

**State management**: A single `state` object holds all UI state. The `render()` function rebuilds relevant DOM sections from state. Events call `setState()` or direct mutations then `render()`.

**Three-panel layout** (CSS grid: `360px | 1fr | 1fr`):
1. **Left** — Inputs: campaign name, priority, pricing (BEP/CPA/budget), country selection, settings
2. **Middle** — Content: video fetching/selection for DGV/GDN campaigns
3. **Right** — Output: generated task text + Notion publish button

**Campaign name format**: `Country | Brand | Product | Type | Date | Creator` (pipe-delimited). `parseCampaignName()` splits this into `state` fields.

**Campaign types** drive template selection:
- `DGV` — Display Google Video (uses video selector with country-block grouping)
- `DG` — Display Google (no videos)
- `GDN` — Google Display Network (single video selector)

**Video data flow**:
1. `fetchSheetTab()` queries Google Sheets via the Visualization Query API (CSV export)
2. `parseVideos()` groups YouTube URLs by country code and block number
3. User selects videos per country; `generateOutput()` builds the task description

**API integrations**:
- **Google Sheets**: Read-only via Visualization Query API (no auth needed)
- **Notion**: Write via a Cloudflare Worker proxy (stored in `localStorage` as `notionProxy`) to bypass CORS. Notion API key also stored in `localStorage`.

**Hardcoded IDs** (in the HTML constants section):
- Google Sheet ID: `1a2JrH9S-kjZmNk2FV57u0IFuoURaLuhVvIAueoyRbhE`
- Notion DB IDs: `NOTION_DB = { SOL: "e8d941b4...", VI: "253ff746..." }` — brand-specific

**Countries split**:
- Core: BG, CZ, HR, HU, PL, RO, SK, DE, GR, IT
- Extended: LT, LV, AT, RS, EE, NL
- All: also includes ES, PT (ES and PT auto-append `EXCLUDE LOCATIONS` block for island regions)
- Country pair: AT+DE share videos in DGV output (labeled "AT, DE" / "DE, AT")
- Brands: SOL (SOLDIUS), OR (ORBITALIS), TR (TOPRABAT), VI (VIGOSHOP)

**VIGOSHOP (VI) differences**:
- Uses a separate Notion database with a different schema: property `"BRAND"` (not `"Brand"`), and `Status` as `select` (not `status`)
- Has its own Notion API key, proxy URL, and notes stored in `localStorage` under `notion_api_key_vi`, `notion_proxy_vi`, `notion_notes_vi`
- VI proxy falls back to SOL proxy if left empty

**OTHER mode** (DGV only): Controls whether the "OTHER" video block is distributed to all countries or only those without a local video assignment.

## Development

**Run locally** (without building the exe): `python serve.py` — starts a plain HTTP server on port 3456, serving `campaign-task-generator.html` at `/`. This avoids the Edge `--disable-web-security` flag, so Google Sheets API calls may be blocked by CORS in this mode. Useful for layout/logic iteration.

**Build the exe**: `pyinstaller app.spec` → `dist/app.exe`. The spec bundles `campaign-task-generator.html` as embedded data. The exe copies it to `view_generator.html` next to itself at runtime, then opens it in Edge app mode with `--disable-web-security` and `--user-data-dir=C:/temp_edge_generator`.

## Key Conventions

- UI language is **Slovenian**.
- No build step for the HTML — edit `campaign-task-generator.html` directly; changes are live on next app launch (or `serve.py` reload).
- Settings (API key, proxy URL) are user-configured via the collapsible settings panel and persisted to `localStorage` — they are not in code.
- `view_generator.html` in the project root and in `dist/` are runtime copies — never edit them directly.
- Debounce delays: 50ms for re-render, 800ms for Google Sheets fetch triggered by campaign name input.
