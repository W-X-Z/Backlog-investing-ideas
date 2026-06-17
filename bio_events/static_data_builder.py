from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .collect_clinical_trials import extract_events, fetch
from .mapping import load_mappings
from .seed import seed_events
from .store import query_events, upsert_events

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "bio_events.sqlite3"
JSON_PATH = ROOT / "pages" / "data" / "bio_events.json"


def build(limit_per_company: int = 50, use_seed_fallback: bool = True) -> dict:
    all_events = []
    errors: list[str] = []
    for mapping in load_mappings():
        try:
            payload = fetch(f'AREA[LeadSponsorName]"{mapping.company_name}"', limit_per_company)
            all_events.extend(extract_events(payload))
        except Exception as exc:  # network/API build should still publish last-known/seed data
            errors.append(f"{mapping.company_name}: {exc}")
    if all_events:
        upsert_events(all_events, DB_PATH)
    elif use_seed_fallback:
        upsert_events(seed_events(), DB_PATH)
    events = query_events({}, DB_PATH)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_mode": "ClinicalTrials.gov API" if all_events else "curated public-source snapshot",
        "errors": errors,
        "events": events,
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build()
    print(f"wrote {len(result['events'])} events to {JSON_PATH} ({result['source_mode']})")
