#!/usr/bin/env python3
"""Build the full English archive from the supplied MD EN translations."""

import json
import re
import shutil
import tempfile
import unicodedata
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "MD"
ENGLISH_SOURCE_DIR = ROOT / "MD EN"
ARCHIVE_PATH = ROOT / "arsiv.json"
ENGLISH_ARCHIVE_PATH = ROOT / "arsiv-en.json"
ISSUE_INDEX_PATH = ROOT / "issues-en.json"
ISSUE_OUTPUT_DIR = ROOT / "en" / "issues"

MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTHS_TR = {
    "ocak": 1, "subat": 2, "mart": 3, "nisan": 4, "mayis": 5, "haziran": 6,
    "temmuz": 7, "agustos": 8, "eylul": 9, "ekim": 10, "kasim": 11, "aralik": 12,
}
URL_RE = re.compile(r"https?://[^\s)\]>]+", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6}\s+)(.*)$")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")


class BuildError(RuntimeError):
    pass


def fold(value):
    value = unicodedata.normalize("NFKD", value).casefold()
    return "".join(char for char in value if not unicodedata.combining(char))


def month_key(value):
    return fold(value.strip()).replace("ı", "i")


def issue_from_path(path):
    name = unicodedata.normalize("NFC", path.stem.removesuffix("-EN")).casefold()
    match = re.search(r"tipografi-bulteni-(.+)-(20\d{2})$", name)
    if not match:
        raise BuildError(f"Unrecognized issue filename: {path}")
    month = MONTHS_TR.get(month_key(match.group(1)))
    if not month:
        raise BuildError(f"Unrecognized month in issue filename: {path}")
    return int(match.group(2)), month


def normalized_stem(path):
    return unicodedata.normalize("NFC", path.stem.removesuffix("-EN"))


def markdown_sections(markdown):
    sections = []
    active_title = None
    active_body = []
    in_fence = False

    def finish():
        nonlocal active_title, active_body
        if active_title is not None:
            sections.append((active_title, "\n".join(active_body).strip()))
        active_title = None
        active_body = []

    for line in markdown.splitlines():
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
        if not in_fence:
            heading = H2_RE.match(line)
            if heading:
                finish()
                active_title = heading.group(1)
                continue
        if active_title is not None:
            active_body.append(line)
    finish()
    return sections


def plain_text(markdown):
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", markdown)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = URL_RE.sub("", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*(?:[-+*>]|\d+[.)])\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~`]+", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def normalized_heading(title):
    return " ".join(fold(plain_text(title)).split())


def source_urls(markdown):
    return set(URL_RE.findall(markdown))


def short_summary(content, limit=320):
    if len(content) <= limit:
        return content
    cut = content.rfind(" ", 0, limit)
    if cut < limit // 2:
        cut = limit
    return content[:cut].rstrip() + "…"


def english_brand_copy(markdown):
    markdown = markdown.replace("Turkish Typography Community", "Turkish Typography Society")
    markdown = markdown.replace("Typography Bulletin Archive", "Typography Newsletter Archive")
    return markdown


def replace_issue_title(markdown, year, month):
    title = f"# Typography Newsletter: {MONTHS_EN[month - 1]} {year}"
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            lines[index] = title
            return "\n".join(lines).rstrip() + "\n"
    return title + "\n\n" + markdown.lstrip()


def build():
    source_files = sorted(SOURCE_DIR.glob("*/*.md"))
    english_files = sorted(ENGLISH_SOURCE_DIR.glob("*/*.md"))
    if len(source_files) != 94 or len(english_files) != 94:
        raise BuildError(f"Expected 94 Turkish and English issues; found {len(source_files)} and {len(english_files)}.")

    source_by_stem = {normalized_stem(path): path for path in source_files}
    english_by_stem = {normalized_stem(path): path for path in english_files}
    if len(source_by_stem) != 94 or len(english_by_stem) != 94:
        raise BuildError("Issue filenames are not unique after Unicode normalization.")
    if source_by_stem.keys() != english_by_stem.keys():
        missing = sorted(source_by_stem.keys() - english_by_stem.keys())
        extra = sorted(english_by_stem.keys() - source_by_stem.keys())
        raise BuildError(f"Turkish/English filenames do not match. Missing: {missing[:3]}; extra: {extra[:3]}.")

    archive = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
    archive_items = archive.get("items", [])
    archive_by_issue = defaultdict(list)
    for item in archive_items:
        month = MONTHS_TR.get(month_key(item.get("ay", "")))
        if month:
            archive_by_issue[(int(item["yil"]), month)].append(item)

    manifest_issues = []
    english_items = {}
    issue_documents = {}
    max_year = 0

    for stem, source_path in source_by_stem.items():
        english_path = english_by_stem[stem]
        year, month = issue_from_path(source_path)
        max_year = max(max_year, year)
        source_markdown = source_path.read_text(encoding="utf-8-sig")
        translated_markdown = english_brand_copy(english_path.read_text(encoding="utf-8-sig"))
        source_sections = markdown_sections(source_markdown)
        translated_sections = markdown_sections(translated_markdown)
        if len(source_sections) != len(translated_sections):
            raise BuildError(f"Heading count changed in {english_path.name}: {len(source_sections)} -> {len(translated_sections)}.")
        if source_urls(source_markdown) != source_urls(translated_markdown):
            raise BuildError(f"A URL target changed or disappeared in {english_path.name}.")

        issue_records = archive_by_issue.get((year, month), [])
        records_by_title = defaultdict(deque)
        for item in issue_records:
            records_by_title[normalized_heading(item["baslik"])].append(item)

        for (source_title, _), (english_title, english_body) in zip(source_sections, translated_sections):
            key = normalized_heading(source_title)
            matching_records = records_by_title.get(key)
            if not matching_records:
                if key == normalized_heading("Küçük Puntolar"):
                    continue
                raise BuildError(f"Could not map section {source_title!r} in {source_path.name}.")
            item = matching_records.popleft()
            translated_title = plain_text(english_title)
            translated_content = english_brand_copy(english_body)
            content_text = plain_text(translated_content)
            english_items[str(item["id"])] = {
                "title": translated_title,
                "summary": short_summary(content_text),
                "content": translated_content,
            }

        remaining = [item["baslik"] for queue in records_by_title.values() for item in queue]
        if remaining:
            raise BuildError(f"Unmapped archive records in {source_path.name}: {remaining[:3]}.")

        translated_markdown = replace_issue_title(translated_markdown, year, month)
        output_name = f"{year}-{month:02d}.md"
        issue_documents[output_name] = translated_markdown
        original_url = issue_records[0].get("url", "") if issue_records else ""
        manifest_issues.append({
            "year": year,
            "month": month,
            "title": f"{MONTHS_EN[month - 1]} {year}",
            "path": f"en/issues/{output_name}",
            "url": original_url,
        })

    if len(issue_documents) != 94 or len(english_items) != len(archive_items):
        raise BuildError(f"Incomplete archive: {len(issue_documents)} issues and {len(english_items)}/{len(archive_items)} entries.")

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    issue_manifest = {
        "updated_at": timestamp,
        "translation_source": "MD EN",
        "issues": sorted(manifest_issues, key=lambda issue: (issue["year"], issue["month"])),
    }
    translations = {"updated_at": timestamp, "coverage": max_year, "items": english_items}

    staging = Path(tempfile.mkdtemp(prefix=".english-archive-build-", dir=ROOT / "en"))
    staged_issues = staging / "issues"
    staged_issues.mkdir()
    try:
        for filename, markdown in issue_documents.items():
            (staged_issues / filename).write_text(markdown, encoding="utf-8")
        (staging / "issues-en.json").write_text(json.dumps(issue_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (staging / "arsiv-en.json").write_text(json.dumps(translations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if ISSUE_OUTPUT_DIR.exists():
            raise BuildError(f"Output directory already exists: {ISSUE_OUTPUT_DIR}.")
        staged_issues.replace(ISSUE_OUTPUT_DIR)
        (staging / "issues-en.json").replace(ISSUE_INDEX_PATH)
        (staging / "arsiv-en.json").replace(ENGLISH_ARCHIVE_PATH)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    print(f"Created {len(issue_documents)} English issues and {len(english_items)} searchable news entries.")


if __name__ == "__main__":
    try:
        build()
    except (BuildError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"English archive was not published: {error}")
