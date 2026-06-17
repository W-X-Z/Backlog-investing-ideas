from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from .mapping import load_mappings, map_company
from .models import BioEvent, parse_iso_date
from .store import upsert_events

API = "https://clinicaltrials.gov/api/v2/studies"


def _first(values: list[str] | None, default: str = "") -> str:
    return values[0] if values else default


def summary(company: str, product: str, phase: str, kind: str) -> str:
    if kind == "CLINICAL_PRIMARY_COMPLETION":
        text = f"{company}의 {product} {phase} 주요 완료 예정일입니다."
    elif kind == "CLINICAL_STUDY_COMPLETION":
        text = f"{company}의 {product} {phase} 최종 완료 예정일입니다."
    else:
        text = f"{company}의 임상 상태 변경 이벤트입니다."
    return text[:60]


def extract_events(payload: dict) -> list[BioEvent]:
    events: list[BioEvent] = []
    mappings = load_mappings()
    for study in payload.get("studies", []):
        protocol = study.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        sponsor = protocol.get("sponsorCollaboratorsModule", {})
        conditions = protocol.get("conditionsModule", {})
        arms = protocol.get("armsInterventionsModule", {})
        design = protocol.get("designModule", {})
        nct_id = ident.get("nctId", "")
        lead = sponsor.get("leadSponsor", {}).get("name", "")
        mapped = map_company(lead, mappings)
        if not mapped:
            continue
        product = _first([i.get("name", "") for i in arms.get("interventions", []) if i.get("name")], ident.get("briefTitle", "임상시험"))
        condition = _first(conditions.get("conditions"), "미기재 질환")
        phase = _first(design.get("phases"), "임상 단계 미기재").replace("PHASE", "Phase ").title()
        source_url = f"https://clinicaltrials.gov/study/{nct_id}"
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for date_field, event_type in (("primaryCompletionDateStruct", "CLINICAL_PRIMARY_COMPLETION"), ("completionDateStruct", "CLINICAL_STUDY_COMPLETION")):
            date_value = status.get(date_field, {}).get("date")
            parsed = parse_iso_date(date_value)
            if parsed:
                events.append(BioEvent(str(parsed), event_type, mapped.company_name, mapped.ticker, mapped.market, product, condition, phase, summary(mapped.company_name, product, phase, event_type), "ClinicalTrials.gov", source_url, "A", now))
    return events


def fetch(query: str, limit: int) -> dict:
    params = {"query.term": query, "pageSize": str(limit), "format": "json"}
    with urlopen(f"{API}?{urlencode(params)}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="AREA[OverallStatus]RECRUITING")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    events = extract_events(fetch(args.query, args.limit))
    print(f"stored {upsert_events(events)} mapped events")

if __name__ == "__main__":
    main()
