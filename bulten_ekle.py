#!/usr/bin/env python3
"""
Tipografi Bülteni Arşivi — Yeni Bülten Ekleme Aracı (bulten_ekle.py)

Kullanım:
    python bulten_ekle.py "bulten_dosyasi.md"
    python bulten_ekle.py "bulten_dosyasi.md" --url "https://tipografi.substack.com/p/..."
    python bulten_ekle.py "bulten_dosyasi.md" --dry-run
"""

import argparse
import os
import re
import sqlite3
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tipografi_arsivi.db"
APP_PATH = BASE_DIR / "app.py"

AYLAR = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]


def normalize_turkish_lower(text: str) -> str:
    """Türkçe karakterleri güvenli küçük harfe ve slug'a çevirir."""
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return text.lower().translate(tr_map)


def parse_newsletter_md(file_path: Path):
    """
    Markdown dosyasını okuyup bülten meta verilerini ve haber bloklarını ayrıştırır.
    """
    content = file_path.read_text(encoding="utf-8")

    # 1. Başlık (# Tipografi Bülteni: Ay Yıl)
    title_match = re.search(r"^#\s+(Tipografi Bülteni:\s*([A-Za-zığüşöçİĞÜŞÖÇ]+)\s+(\d{4}))", content, re.MULTILINE)
    ay = None
    yil = None
    bulten_adi = None

    if title_match:
        bulten_adi = title_match.group(1).strip()
        ay_candidate = title_match.group(2).strip()
        yil = int(title_match.group(3))
        for a in AYLAR:
            if a.lower() == ay_candidate.lower():
                ay = a
                break
        if not ay:
            ay = ay_candidate
    else:
        m = re.search(r"(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+(\d{4})", content)
        if m:
            ay = m.group(1)
            yil = int(m.group(2))
            bulten_adi = f"Tipografi Bülteni: {ay} {yil}"

    if not ay or not yil:
        raise ValueError("Bülten başlığından Ay ve Yıl bilgisi tespit edilemedi (Örn: # Tipografi Bülteni: Ekim 2026).")

    # 2. Kaynak URL
    url_match = re.search(r"\*\*Kaynak:\*\*\s*<?(https?://[^\s>]+)>?", content)
    bulten_url = url_match.group(1).strip() if url_match else None

    # Standart dosya adı
    dosya_adi = f"tipografi-bulteni-{normalize_turkish_lower(ay)}-{yil}.md"

    # 3. Footer temizliği
    footer_idx = content.find("Her türlü görüş ve önerini")
    if footer_idx != -1:
        clean_content = content[:footer_idx]
    else:
        clean_content = content

    # 4. H2 başlıklarına göre böl
    parts = re.split(r"(\n##\s+[^\n]+)", clean_content)
    # parts: [giris, "\n## Baslik1", govde1, "\n## Baslik2", govde2, ...]

    haberler = []

    for i in range(1, len(parts), 2):
        header_raw = parts[i].strip()
        baslik = re.sub(r"^##\s+", "", header_raw).strip()
        preceding = parts[i - 1].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""

        # Sonundaki --- çizgisini temizle
        body = re.sub(r"\n---\s*$", "", body).strip()

        # Başlıktan hemen önce bir görsel açıklaması veya telif satırı var mı?
        image_credit = None
        prec_lines = [l.strip() for l in preceding.split("\n") if l.strip()]
        for line in reversed(prec_lines[-3:]):
            if line.startswith("*") and ("©" in line or "Görsel" in line):
                image_credit = line
                break

        icerik = body
        if image_credit and not icerik.startswith("*"):
            icerik = f"{image_credit}\n\n{icerik}"

        haberler.append({
            "baslik": baslik,
            "icerik": icerik
        })

    return {
        "ay": ay,
        "yil": yil,
        "bulten_adi": bulten_adi,
        "dosya_adi": dosya_adi,
        "bulten_url": bulten_url,
        "haberler": haberler
    }


def add_to_database(bulten_data: dict, db_path: Path):
    """
    SQLite veritabanına ve FTS tablosuna haberleri ekler.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    dosya_adi = bulten_data["dosya_adi"]
    bulten_adi = bulten_data["bulten_adi"]
    yil = bulten_data["yil"]
    ay = bulten_data["ay"]

    # Önce bu dosya daha önce eklenmiş mi kontrol et
    cur.execute("SELECT id FROM haberler WHERE dosya_adi = ?", (dosya_adi,))
    existing_ids = [row[0] for row in cur.fetchall()]

    if existing_ids:
        print(f"⚠️  '{dosya_adi}' için mevcut {len(existing_ids)} kayıt bulundu. Güncellenmek üzere eski kayıtlar siliniyor...")
        for old_id in existing_ids:
            cur.execute("DELETE FROM haberler_fts WHERE rowid = ?", (old_id,))
        cur.execute("DELETE FROM haberler WHERE dosya_adi = ?", (dosya_adi,))

    eklenen = 0
    for h in bulten_data["haberler"]:
        baslik = h["baslik"]
        icerik = h["icerik"]

        # haberler tablosuna ekle
        cur.execute("""
            INSERT INTO haberler (dosya_adi, bulten_adi, yil, ay, baslik, icerik)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (dosya_adi, bulten_adi, yil, ay, baslik, icerik))

        new_id = cur.lastrowid

        # haberler_fts tablosuna ekle
        cur.execute("""
            INSERT INTO haberler_fts (rowid, baslik, icerik, bulten_adi)
            VALUES (?, ?, ?, ?)
        """, (new_id, baslik, icerik, bulten_adi))

        eklenen += 1

    conn.commit()
    conn.close()
    return eklenen


def update_app_py_urls(ay: str, yil: int, url: str, app_path: Path):
    """
    app.py içindeki BULTEN_URLS sözlüğüne yeni bülteni ekler.
    """
    if not app_path.is_file() or not url:
        return False

    app_text = app_path.read_text(encoding="utf-8")
    key = f'"{ay} {yil}"'
    entry = f'    "{ay} {yil}": "{url}",\n'

    if key in app_text:
        print(f"ℹ️  app.py içinde {key} bağlantısı zaten mevcut.")
        return False

    # BULTEN_URLS = { ... } bloğunu bul
    pattern = r"(BULTEN_URLS\s*=\s*\{[\s\S]*?)(\n\})"
    match = re.search(pattern, app_text)
    if not match:
        print("⚠️  app.py içinde BULTEN_URLS sözlüğü bulunamadı.")
        return False

    before = match.group(1).rstrip()
    if not before.endswith(","):
        before += ","
    replacement = f"{before}\n{entry}}}"
    new_app_text = app_text[:match.start()] + replacement + app_text[match.end():]

    app_path.write_text(new_app_text, encoding="utf-8")
    print(f"✅ app.py içindeki BULTEN_URLS sözlüğüne '{ay} {yil}' eklendi.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Tipografi Bülteni Arşivi — Yeni Bülten Ekleme Aracı")
    parser.add_argument("dosya", type=str, help="Eklenecek bülten markdown (.md) dosyası")
    parser.add_argument("--url", type=str, default=None, help="Bültenin Substack/Medium URL adresi")
    parser.add_argument("--dry-run", action="store_true", help="Veritabanına yazmadan sadece önizleme yapar")
    args = parser.parse_args()

    md_path = Path(args.dosya).resolve()
    if not md_path.is_file():
        print(f"❌ Dosya bulunamadı: {md_path}")
        return

    data = parse_newsletter_md(md_path)
    if args.url:
        data["bulten_url"] = args.url

    print("=" * 60)
    print(f"📰 Bülten Adı : {data['bulten_adi']}")
    print(f"📅 Dönem      : {data['ay']} {data['yil']}")
    print(f"📁 Dosya Adı  : {data['dosya_adi']}")
    print(f"🔗 Bağlantı   : {data['bulten_url'] or '(Belirtilmedi)'}")
    print(f"📑 Haber Sayısı: {len(data['haberler'])}")
    print("-" * 60)
    for idx, h in enumerate(data["haberler"], 1):
        preview = h['icerik'].split('\n')[0][:80]
        print(f"  {idx}. {h['baslik']}")
        print(f"     Özet: {preview}...")
    print("=" * 60)

    if args.dry_run:
        print("🔍 [DRY-RUN] Modu devrede. Veritabanına veya app.py dosyasına yazılmadı.")
        return

    # Veritabanına ekle
    eklenen = add_to_database(data, DB_PATH)
    print(f"✅ Veritabanına {eklenen} haber başarıyla eklendi.")

    # app.py güncelle
    if data["bulten_url"]:
        update_app_py_urls(data["ay"], data["yil"], data["bulten_url"], APP_PATH)

    print("\n🚀 Tamamlandı! Şimdi GitHub'a göndermek için:")
    print("   git add tipografi_arsivi.db app.py")
    print(f'   git commit -m "Yeni bülten eklendi: {data["ay"]} {data["yil"]}"')
    print("   git push")


if __name__ == "__main__":
    main()
