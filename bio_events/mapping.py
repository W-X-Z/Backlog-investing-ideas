from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAPPING_PATH = Path(__file__).resolve().parents[1] / "data" / "ticker_mappings.csv"


@dataclass(frozen=True)
class TickerMapping:
    company_name: str
    ticker: str
    market: str
    aliases: tuple[str, ...]


def load_mappings(path: Path = DEFAULT_MAPPING_PATH) -> list[TickerMapping]:
    with path.open(newline="", encoding="utf-8") as fp:
        rows = csv.DictReader(fp)
        return [
            TickerMapping(
                company_name=row["company_name"].strip(),
                ticker=row["ticker"].strip().upper(),
                market=row["market"].strip().upper(),
                aliases=tuple(a.strip() for a in row.get("aliases", "").split(";") if a.strip()),
            )
            for row in rows
        ]


def map_company(name: str, mappings: list[TickerMapping] | None = None) -> TickerMapping | None:
    normalized = name.casefold().strip()
    for mapping in mappings or load_mappings():
        candidates = (mapping.company_name, *mapping.aliases)
        if any(normalized == candidate.casefold().strip() for candidate in candidates):
            return mapping
    for mapping in mappings or load_mappings():
        candidates = (mapping.company_name, *mapping.aliases)
        if any(candidate.casefold().strip() in normalized or normalized in candidate.casefold().strip() for candidate in candidates):
            return mapping
    return None
