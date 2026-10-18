"""Upsert durable Amala events into a Google Sheet using authorized ADC."""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "data" / "sheet-queue.jsonl"
SHEET = "Operations Events"
HEADERS = ["Key", "Date", "Time block", "Task", "Description", "Tools used", "Expected output", "Actual output path", "Start time IST", "Completion time IST", "Status", "Error or blocker", "Retry count", "Approval status", "YouTube video title", "Upload status", "Actual upload time IST", "Video URL", "GitHub repository", "Commit hash", "Notes"]
STAGE_ROW = {"research": 4, "script": 5, "voice": 6, "graphics": 7, "assemble": 9, "qa": 10, "metadata": 11, "upload": 12}


def pending_events():
    if not QUEUE.exists():
        return OrderedDict()
    latest = OrderedDict()
    for line in QUEUE.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        latest[event["key"]] = event
    return latest


def schedule():
    with (ROOT / "schedule.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def row_for(event, schedule_rows):
    from amala_youtube import state
    date, stage = event["date"], event["stage"]
    day = state(date)
    item = day["upload"] if stage == "upload" else day["stages"][stage]
    plan = schedule_rows[STAGE_ROW[stage] - 1]
    upload = day["upload"]
    outputs = event.get("outputs", item.get("outputs", []))
    return [event["key"], date, plan["Time (IST)"], plan["Workstream"], plan["What Amala does"], plan["Tools"], plan["Expected file / evidence"], "; ".join(outputs), item.get("started_at", ""), item.get("completed_at", ""), event["status"], item.get("note", ""), item.get("retry_count", 0), upload.get("approval", "PENDING"), upload.get("title", ""), upload.get("status", "NOT_UPLOADED"), "", upload.get("url", ""), "https://github.com/amalraj020-a11y/amala-youtube-operations", upload.get("commit_hash", ""), "Published date shown in Studio: " + upload.get("published_date_ist", "") if stage == "upload" else ""]


def sync(sheet_id, session=None):
    if session is None:
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
        session = AuthorizedSession(credentials)
    base = f"https://sheets.googleapis.com/v4/spreadsheets/{quote(sheet_id, safe='')}/values"
    events = pending_events()
    if not events:
        return 0
    def request(method, url, **kwargs):
        response = session.request(method, url, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()
    address = quote(f"'{SHEET}'!A:U", safe="")
    values = request("GET", f"{base}/{address}").get("values", [])
    if not values or values[0] != HEADERS:
        raise RuntimeError("Operations Events headers differ from the expected 21 fields")
    existing = {row[0]: index for index, row in enumerate(values[1:], 2) if row}
    plans = schedule()
    for key, event in events.items():
        row = row_for(event, plans)
        if key in existing:
            cell_range = quote(f"'{SHEET}'!A{existing[key]}:U{existing[key]}", safe="")
            request("PUT", f"{base}/{cell_range}?valueInputOption=RAW", json={"values": [row]})
        else:
            request("POST", f"{base}/{address}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS", json={"values": [row]})
            existing[key] = len(existing) + 2
    # Keep the queue durable as an audit log. Upserts make reruns idempotent.
    return len(events)


if __name__ == "__main__":
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("GOOGLE_SHEET_ID is not set", file=sys.stderr)
        raise SystemExit(2)
    try:
        print(f"Synchronized {sync(sheet_id)} unique stage rows")
    except Exception as exc:
        print(f"Sync pending: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
