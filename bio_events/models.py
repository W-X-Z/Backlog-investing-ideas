from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from typing import Literal

EventType = Literal[
    "CLINICAL_PRIMARY_COMPLETION",
    "CLINICAL_STUDY_COMPLETION",
    "CLINICAL_STATUS_CHANGE",
    "FDA_RECALL",
    "PATENT_EXPIRY",
]
ConfidenceLevel = Literal["A", "B", "C"]


@dataclass(frozen=True)
class BioEvent:
    event_date: str
    event_type: EventType
    company_name: str
    ticker: str
    market: str
    product_name: str
    condition_name: str
    clinical_phase: str
    summary_ko: str
    source: str
    source_url: str
    confidence_level: ConfidenceLevel = "A"
    last_updated_at: str = ""
    customer_visible: bool = True

    def to_record(self) -> dict[str, object]:
        record = asdict(self)
        if not record["last_updated_at"]:
            record["last_updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return record


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None
