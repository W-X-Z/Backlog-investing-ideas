# Bio Event Calendar MVP

Public-data based bio event calendar for investment research. The app collects mapped ClinicalTrials.gov events, stores them in SQLite, and exposes a customer-safe API plus a simple calendar/list UI.

## Quick start

```bash
python -m bio_events.seed
python -m bio_events.server --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000> or call:

```bash
curl 'http://127.0.0.1:8000/api/bio-events?date_from=2026-01-01&date_to=2026-12-31'
```


## GitHub Pages

This repo now includes a static entrypoint (`index.html`) and generated dataset (`data/bio_events.json`) so the service is queryable on GitHub Pages without a Python server. The browser first tries `/api/bio-events` for local/API deployments and automatically falls back to the static JSON file on Pages.

A GitHub Actions workflow refreshes the static dataset from ClinicalTrials.gov on pushes, on a daily schedule, or manually via `workflow_dispatch`. If the live API is unavailable during a build, the workflow keeps publishing the curated public-source snapshot with source links.

## Data policy

* Only mapped tickers are customer-visible.
* The default API response exposes confidence `A` and `B` only.
* Summaries avoid buy/sell, upside, beneficiary, or recommendation language.
* ClinicalTrials.gov completion dates are operational study dates, not result announcement dates.

## Collection

The Phase 1 collector uses ClinicalTrials.gov API v2 and a manual sponsor-to-ticker mapping in `data/ticker_mappings.csv`.

```bash
python -m bio_events.collect_clinical_trials --query "AREA[LeadSponsorName]Moderna" --limit 25
```
