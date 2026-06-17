from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .models import BioEvent

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "bio_events.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bio_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_date TEXT NOT NULL,
  event_type TEXT NOT NULL,
  company_name TEXT NOT NULL,
  ticker TEXT NOT NULL,
  market TEXT NOT NULL,
  product_name TEXT NOT NULL,
  condition_name TEXT NOT NULL,
  clinical_phase TEXT NOT NULL,
  summary_ko TEXT NOT NULL,
  source TEXT NOT NULL,
  source_url TEXT NOT NULL,
  confidence_level TEXT NOT NULL,
  last_updated_at TEXT NOT NULL,
  customer_visible INTEGER NOT NULL DEFAULT 1,
  UNIQUE(event_date, event_type, ticker, product_name, condition_name, source_url)
);
"""

FIELDS = ["event_date","event_type","company_name","ticker","market","product_name","condition_name","clinical_phase","summary_ko","source","source_url","confidence_level","last_updated_at","customer_visible"]


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def upsert_events(events: Iterable[BioEvent], path: Path = DB_PATH) -> int:
    conn = connect(path)
    count = 0
    with conn:
        for event in events:
            record = event.to_record()
            record["customer_visible"] = int(bool(record["customer_visible"]))
            placeholders = ",".join(":" + field for field in FIELDS)
            updates = ",".join(f"{field}=excluded.{field}" for field in FIELDS if field != "last_updated_at")
            conn.execute(f"INSERT INTO bio_events ({','.join(FIELDS)}) VALUES ({placeholders}) ON CONFLICT(event_date,event_type,ticker,product_name,condition_name,source_url) DO UPDATE SET {updates}, last_updated_at=excluded.last_updated_at", record)
            count += 1
    conn.close()
    return count


def query_events(filters: dict[str, str], path: Path = DB_PATH) -> list[dict[str, object]]:
    conn = connect(path)
    where = ["customer_visible = 1"]
    params: dict[str, object] = {}
    if filters.get("date_from"):
        where.append("event_date >= :date_from"); params["date_from"] = filters["date_from"]
    if filters.get("date_to"):
        where.append("event_date <= :date_to"); params["date_to"] = filters["date_to"]
    for field in ("event_type", "ticker", "market", "confidence_level"):
        if filters.get(field):
            where.append(f"{field} = :{field}"); params[field] = filters[field].upper()
    if not filters.get("confidence_level"):
        where.append("confidence_level IN ('A','B')")
    rows = conn.execute(f"SELECT * FROM bio_events WHERE {' AND '.join(where)} ORDER BY event_date, ticker", params).fetchall()
    conn.close()
    return [{k: row[k] for k in row.keys() if k != "id" and k != "customer_visible"} for row in rows]
