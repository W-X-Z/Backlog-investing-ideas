# Bio Event Calendar MVP

Public-data based bio event calendar for investment research. The app collects mapped ClinicalTrials.gov events, stores them in SQLite, and exposes a customer-safe static calendar UI.

## GitHub Pages deployment

The `pages/index.html`, `pages/app.js`, and `pages/data/bio_events.json` files are the GitHub Pages site artifact source. If the live URL shows a README page, Pages is still serving an older branch artifact without `index.html`; rerun the `Deploy GitHub Pages` workflow or merge/push this branch so `_site/index.html` is deployed. The workflow builds a minimal `_site` artifact from those files and deploys it on every branch push or manual dispatch.

## Local API quick start

```bash
python -m bio_events.seed
python -m bio_events.local_server --host 127.0.0.1 --port 8000
```

Then open <http://127.0.0.1:8000> or call:

```bash
curl 'http://127.0.0.1:8000/api/bio-events?date_from=2026-01-01&date_to=2026-12-31'
```

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
