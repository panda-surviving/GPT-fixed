import sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("app_v6", ROOT / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


def test_company_announcement_parser_is_stock_specific():
    html = '''<html><body><h1>Announcements</h1><table>
    <tr><th>Date</th><th>Title</th><th>Document</th></tr>
    <tr><td>Aug 15, 2026</td><td>Transmission of Quarterly Report</td><td><a href="/download/document/123.pdf">PDF</a></td></tr>
    <tr><td>Aug 14, 2026</td><td>Board Meeting</td><td><a href="/download/document/122.pdf">PDF</a></td></tr>
    </table></body></html>'''
    rows = app._parse_company_announcements(html, "TEST", 20)
    assert len(rows) == 2
    assert all(r["symbol"] == "TEST" for r in rows)
    assert all("download/document" in r["url"] for r in rows)


def test_technical_catalog_does_not_depend_on_local_recording_days():
    original = app.get_recording_progress
    try:
        app.get_recording_progress = lambda: {"days_recorded": 0, "started_on": None}
        sections, _ = app.catalog_with_progress()
        tech = next(x for x in sections if x["section"] == "Technical Analysis")
        live_items = {x["filter_key"]: x for x in tech["items"] if x.get("filter_key")}
        assert live_items["ema20"]["available"] is True
        assert live_items["ema20"].get("activating") is False
        assert "real PSX historical OHLCV" in live_items["ema20"]["reason"]
    finally:
        app.get_recording_progress = original


def test_scan_result_reports_batched_history_prefetch_fields():
    source = (ROOT / "app.py").read_text()
    assert "_prefetch_psx_histories_batch" in source
    assert '"history_prefetched"' in source
    assert '"history_prefetch_seconds"' in source


def test_stock_page_uses_company_specific_endpoint():
    source = (ROOT / "static" / "app.js").read_text()
    assert "/api/psx/announcements?symbol=" in source
    assert "Official PSX filing for" in source


def test_separate_announcements_menu_exists():
    html = (ROOT / "templates" / "index.html").read_text()
    js = (ROOT / "static" / "app.js").read_text()
    assert 'data-page="announcements"' in html
    assert 'id="announcementListAll"' in html
    assert 'async function loadAllPsxAnnouncements()' in js
