from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_home_is_thai_first_and_keeps_real_intake_controls():
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert '<html lang="th">' in html
    assert "อ่านผลแล็บของคุณ" in html
    assert "อัปโหลดใบผลตรวจ" in html
    assert 'id="message-input"' in html
    assert 'id="image-input"' in html
    assert 'id="image-review"' in html
    assert 'data-sample=' in html
    assert "ไม่วินิจฉัย" in html


def test_chat_ui_has_server_owned_sources_and_recovery_paths():
    javascript = (ROOT / "static" / "js" / "chat.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")

    assert "renderCitations" in javascript
    assert "citation.source_url || citation.origin" in javascript
    assert "requestInFlight" in javascript
    assert "error-retry" in javascript
    assert "activeAbortController" in javascript
    assert "/api/v1/images/extract" in javascript
    assert "/api/v1/images/" in javascript
    assert "@media (max-width: 760px)" in css
    assert ".citation-list" in css
    assert "overflow-wrap: anywhere" in css
