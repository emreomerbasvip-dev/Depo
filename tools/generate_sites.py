#!/usr/bin/env python3
"""
leads CSV'sindeki her dükkan için kişiselleştirilmiş demo site üretir.

    python3 tools/generate_sites.py leads/leads.csv
    -> sites/<dukkan-slug>/index.html

Klasörü Netlify / Vercel / GitHub Pages'e atınca her dükkanın linki olur:
    https://<alan-adınız>/<dukkan-slug>/
"""
import csv
import datetime
import html
import os
import re
import sys
import urllib.parse

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SABLON = os.path.join(KOK, "site-template", "index.html")
TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def slug(s):
    s = s.translate(TR).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "dukkan"


def wa_numara(tel):
    d = re.sub(r"\D", "", tel or "")
    if d.startswith("0"):
        d = "90" + d[1:]
    elif len(d) == 10:
        d = "90" + d
    return d


def uret(satir, sablon):
    tel = satir.get("telefon", "")
    deg = {
        "ISIM": satir.get("isim", ""),
        "ILCE": satir.get("ilce", ""),
        "ADRES": satir.get("adres", ""),
        "TELEFON": tel,
        "PUAN": satir.get("puan", ""),
        "YORUM_SAYISI": satir.get("yorum_sayisi", ""),
        "YIL": str(datetime.date.today().year),
    }
    out = sablon
    if not satir.get("puan"):  # puan yoksa uydurma; bölümü kaldır
        out = re.sub(r"<!--PUAN_BAS-->.*?<!--PUAN_SON-->", "", out, flags=re.S)
    for k, v in deg.items():
        out = out.replace("{{%s}}" % k, html.escape(str(v)))
    # URL bağlamındaki alanlar ayrıca kodlanır
    out = out.replace("{{TEL_LINK}}", "+" + wa_numara(tel) if tel else "")
    out = out.replace("{{WA}}", wa_numara(satir.get("telefon_uluslararasi") or tel))
    out = out.replace("{{ADRES_URL}}", urllib.parse.quote(f"{deg['ISIM']} {deg['ADRES']}"))
    out = out.replace("{{HARITA}}", html.escape(satir.get("harita") or
                      "https://www.google.com/maps/search/?api=1&query=" +
                      urllib.parse.quote(deg["ISIM"] + " " + deg["ADRES"])))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("Kullanım: python3 tools/generate_sites.py leads/leads.csv")
    sablon = open(SABLON, encoding="utf-8").read()
    with open(sys.argv[1], encoding="utf-8-sig") as f:
        satirlar = list(csv.DictReader(f))
    for s in satirlar:
        if not s.get("isim"):
            continue
        hedef = os.path.join(KOK, "sites", slug(s["isim"] + "-" + s.get("ilce", "")))
        os.makedirs(hedef, exist_ok=True)
        with open(os.path.join(hedef, "index.html"), "w", encoding="utf-8") as f:
            f.write(uret(s, sablon))
        print("✓", os.path.relpath(hedef, KOK))


if __name__ == "__main__":
    main()
