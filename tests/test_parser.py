"""Phase 1 tests: run the parser on the sample resumes and sanity-check results."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_parser import clean_text, detect_sections, parse_resume

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"


def test_docx_parse() -> None:
    path = SAMPLE_DIR / "jane_doe_resume.docx"
    text, sections = parse_resume(path)
    assert "Jane Doe" in text
    assert "SQL" in text
    assert {"experience", "education", "skills", "projects"} <= set(sections)
    assert any("retention by 12%" in line for line in sections["experience"])


def test_pdf_parse() -> None:
    path = SAMPLE_DIR / "jane_doe_resume.pdf"
    text, sections = parse_resume(path)
    assert "Jane Doe" in text
    assert "Tableau" in text
    assert "skills" in sections


def test_clean_text_normalizes_bullets() -> None:
    raw = "- item one\r\n\u2022 item two\n\n\n   spaced   out  \r\n"
    cleaned = clean_text(raw)
    assert cleaned.count("\u2022") == 2
    assert "spaced out" in cleaned
    assert "\n\n" not in cleaned


def test_detect_sections_default_header() -> None:
    text = "John Smith\njohn@x.com\n\nSUMMARY\nLoves data.\n"
    sections = detect_sections(text)
    assert sections["header"] == ["John Smith", "john@x.com"]
    assert sections["summary"] == ["Loves data."]


def _demo() -> None:
    print("=" * 60)
    for name in ("jane_doe_resume.docx", "jane_doe_resume.pdf"):
        path = SAMPLE_DIR / name
        text, sections = parse_resume(path)
        print(f"\n--- {name} ({len(text)} chars) ---")
        print("--- CLEAN TEXT ---")
        print(text)
        print("--- SECTIONS DETECTED ---")
        for section, lines in sections.items():
            print(f"[{section}] ({len(lines)} lines): {lines[:2]}...")
    print("=" * 60)


if __name__ == "__main__":
    _demo()
    print("\nAll Phase 1 tests passed.")
