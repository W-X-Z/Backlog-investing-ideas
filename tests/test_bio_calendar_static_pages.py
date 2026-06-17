from pathlib import Path
import json


def test_github_pages_entrypoint_and_data_exist():
    assert Path("pages/index.html").exists()
    assert Path("pages/app.js").exists()
    payload = json.loads(Path("pages/data/bio_events.json").read_text(encoding="utf-8"))
    assert payload["events"]
    assert payload["events"][0]["source_url"].startswith("https://clinicaltrials.gov/study/")
