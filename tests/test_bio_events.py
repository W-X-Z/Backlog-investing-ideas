from pathlib import Path

from bio_events.collect_clinical_trials import extract_events
from bio_events.models import BioEvent
from bio_events.store import query_events, upsert_events


def test_store_defaults_to_customer_visible_ab_only(tmp_path: Path):
    db = tmp_path / "events.sqlite3"
    upsert_events([
        BioEvent("2026-01-01", "CLINICAL_PRIMARY_COMPLETION", "Moderna", "MRNA", "NASDAQ", "Drug", "Cancer", "Phase 3", "Moderna의 Drug Phase 3 주요 완료 예정일입니다.", "ClinicalTrials.gov", "https://clinicaltrials.gov/study/NCT1", "A"),
        BioEvent("2026-01-02", "CLINICAL_PRIMARY_COMPLETION", "Moderna", "MRNA", "NASDAQ", "Drug", "Cancer", "Phase 3", "검수 필요 이벤트입니다.", "ClinicalTrials.gov", "https://clinicaltrials.gov/study/NCT2", "C"),
    ], db)
    events = query_events({}, db)
    assert len(events) == 1
    assert events[0]["confidence_level"] == "A"


def test_extract_clinical_trials_maps_only_known_tickers():
    payload = {"studies": [{"protocolSection": {"identificationModule": {"nctId": "NCT123", "briefTitle": "Trial"}, "statusModule": {"primaryCompletionDateStruct": {"date": "2026-08-15"}}, "sponsorCollaboratorsModule": {"leadSponsor": {"name": "ModernaTX"}}, "conditionsModule": {"conditions": ["COVID-19"]}, "armsInterventionsModule": {"interventions": [{"name": "mRNA-1283"}]}, "designModule": {"phases": ["PHASE3"]}}}]}
    events = extract_events(payload)
    assert len(events) == 1
    assert events[0].ticker == "MRNA"
    assert events[0].event_type == "CLINICAL_PRIMARY_COMPLETION"
    assert "매수" not in events[0].summary_ko
