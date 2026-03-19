# DSIP Topic Scraper

Playwright-based scraper for the DoD SBIR/STTR Innovation Portal (DSIP) at dodsbirsttr.mil.

## Setup

```bash
pip install playwright
python -m playwright install chromium
```

## Usage

```bash
python scrape_dsip.py --output ../sbir/dsip_topics_all.json
```

## How It Works

The DSIP portal is a JavaScript-heavy Angular app that doesn't serve topic data via static HTML. This scraper:

1. Launches a headless Chromium browser via Playwright
2. Loads the DSIP topics page to establish a session
3. Hits the discovered internal API endpoint (`/topics/api/public/topics/search`) with `size=100` to get all topics in one request
4. Saves the full topic metadata (IDs, titles, components, dates, Q&A counts, TPOC info) as JSON

## Key Discovery

The DSIP API uses `total`/`data` keys (not the more common `totalElements`/`content`). The search parameters use status IDs `591` (Pre-Release) and `592` (Open).

## Files

- `scrape_dsip.py` - Main scraper (production version)
- Earlier iterations kept in git history
