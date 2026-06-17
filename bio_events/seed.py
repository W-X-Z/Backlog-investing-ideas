from __future__ import annotations

from datetime import datetime, timezone
from .models import BioEvent
from .store import upsert_events


def seed_events() -> list[BioEvent]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return [
        BioEvent("2026-08-15", "CLINICAL_PRIMARY_COMPLETION", "Moderna", "MRNA", "NASDAQ", "mRNA-1283", "COVID-19", "Phase 3", "Moderna의 mRNA-1283 Phase 3 주요 완료 예정일입니다.", "ClinicalTrials.gov", "https://clinicaltrials.gov/study/NCT05815498", "A", now),
        BioEvent("2026-09-30", "CLINICAL_STUDY_COMPLETION", "Gilead Sciences", "GILD", "NASDAQ", "Lenacapavir", "HIV Prevention", "Phase 3", "Gilead Sciences의 Lenacapavir Phase 3 최종 완료 예정일입니다.", "ClinicalTrials.gov", "https://clinicaltrials.gov/study/NCT04994509", "A", now),
        BioEvent("2026-10-20", "CLINICAL_PRIMARY_COMPLETION", "Pfizer", "PFE", "NYSE", "PF-07220060", "Breast Cancer", "Phase 3", "Pfizer의 PF-07220060 Phase 3 주요 완료 예정일입니다.", "ClinicalTrials.gov", "https://clinicaltrials.gov/study/NCT05563220", "B", now),
    ]

if __name__ == "__main__":
    print(f"stored {upsert_events(seed_events())} seed events")
