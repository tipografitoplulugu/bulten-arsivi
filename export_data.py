#!/usr/bin/env python3
"""
Tipografi Bülteni Arşivi — Statik Veri Dışa Aktarma Aracı (export_data.py)
SQLite veritabanındaki tüm haberleri ve app.py içindeki URL eşleştirmelerini
GitHub Pages için 'arsiv.json' dosyasına aktarır.
"""

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tipografi_arsivi.db"
APP_PATH = BASE_DIR / "app.py"
OUTPUT_PATH = BASE_DIR / "arsiv.json"


def get_bulten_urls(app_path: Path) -> dict[str, str]:
    if not app_path.is_file():
        return {}
    content = app_path.read_text(encoding="utf-8")
    match = re.search(r"BULTEN_URLS\s*=\s*(\{[\s\S]*?\n\})", content)
    if not match:
        return {}
    try:
        return eval(match.group(1))
    except Exception:
        return {}


def issue_name(full_name: str) -> str:
    return full_name.split(":", 1)[-1].strip() if ":" in full_name else full_name.strip()


def get_issue_url(name: str, bulten_urls: dict[str, str]) -> str:
    clean_name = issue_name(name)
    if clean_name in bulten_urls:
        return bulten_urls[clean_name]
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    slug = clean_name.lower().translate(tr_map).replace(" ", "-")
    return f"https://tipografi.substack.com/p/{slug}"


def export_json(db_path: Path = DB_PATH, app_path: Path = APP_PATH, output_path: Path = OUTPUT_PATH) -> int:
    bulten_urls = get_bulten_urls(app_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT id, dosya_adi, bulten_adi, yil, ay, baslik, icerik FROM haberler ORDER BY yil DESC, id DESC"
    ).fetchall()

    distinct_issues = set()
    years = set()
    items = []

    for r in rows:
        clean_issue = issue_name(r["bulten_adi"] or "")
        distinct_issues.add(clean_issue)
        if r["yil"]:
            years.add(int(r["yil"]))

        url = get_issue_url(clean_issue, bulten_urls)
        items.append({
            "id": r["id"],
            "bulten": clean_issue,
            "yil": int(r["yil"]) if r["yil"] else None,
            "ay": r["ay"] or "",
            "baslik": r["baslik"] or "",
            "icerik": r["icerik"] or "",
            "url": url,
        })

    conn.close()

    sorted_years = sorted(list(years), reverse=True)
    min_year = min(years) if years else 2019
    max_year = max(years) if years else 2026

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_issues": len(distinct_issues),
            "total_articles": len(items),
            "min_year": min_year,
            "max_year": max_year,
            "years": sorted_years,
        },
        "items": items,
    }

    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=None), encoding="utf-8")
    print(f"✅ {len(items)} haber ve {len(distinct_issues)} bülten '{output_path.name}' dosyasına aktarıldı.")
    return len(items)


if __name__ == "__main__":
    export_json()
