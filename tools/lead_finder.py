#!/usr/bin/env python3
"""
İstanbul'da web sitesi OLMAYAN pet shopları bulur.

Google Places API (New) - Text Search kullanır. Her ilçe için "pet shop"
araması yapar, websiteUri alanı boş olan işletmeleri leads/leads.csv
dosyasına yazar.

Kullanım:
    export GOOGLE_MAPS_API_KEY=...        # Google Cloud'da "Places API (New)" açık olmalı
    python3 tools/lead_finder.py                       # tüm ilçeler
    python3 tools/lead_finder.py --ilce Kadıköy Üsküdar
    python3 tools/lead_finder.py --sorgu "akvaryum"    # farklı sektör/anahtar kelime

Sadece standart kütüphane kullanır, kurulum gerektirmez.
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.internationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.businessStatus",
    "places.googleMapsUri",
    "nextPageToken",
])

ILCELER = [
    "Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler",
    "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü",
    "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt",
    "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kağıthane",
    "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer",
    "Silivri", "Sultanbeyli", "Sultangazi", "Şile", "Şişli", "Tuzla",
    "Ümraniye", "Üsküdar", "Zeytinburnu",
]

# Sosyal medya / pazar yeri linkleri "gerçek web sitesi" sayılmaz -> yine lead.
SOSYAL = ("instagram.com", "facebook.com", "wa.me", "whatsapp.com",
          "linktr.ee", "trendyol.com", "hepsiburada.com", "sahibinden.com",
          "business.site", "google.com")


def ara(api_key, sorgu, page_token=None):
    body = {"textQuery": sorgu, "languageCode": "tr", "regionCode": "TR",
            "pageSize": 20}
    if page_token:
        body["pageToken"] = page_token
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELDS,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def site_yok_mu(website):
    if not website:
        return True, "site yok"
    if any(s in website.lower() for s in SOSYAL):
        return True, "sadece sosyal medya: " + website
    return False, ""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ilce", nargs="*", default=ILCELER)
    p.add_argument("--sorgu", default="pet shop")
    p.add_argument("--cikti", default="leads/leads.csv")
    p.add_argument("--sayfa", type=int, default=3, help="ilçe başına max sayfa (20'şer)")
    a = p.parse_args()

    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        sys.exit("GOOGLE_MAPS_API_KEY ortam değişkeni gerekli.")

    goruldu, satirlar = set(), []
    for ilce in a.ilce:
        sorgu = f"{a.sorgu} {ilce} İstanbul"
        token, sayfa = None, 0
        while sayfa < a.sayfa:
            try:
                data = ara(key, sorgu, token)
            except urllib.error.HTTPError as e:
                sys.exit(f"API hatası ({e.code}): {e.read().decode()[:500]}")
            for pl in data.get("places", []):
                if pl["id"] in goruldu:
                    continue
                goruldu.add(pl["id"])
                if pl.get("businessStatus") not in (None, "OPERATIONAL"):
                    continue
                lead, not_ = site_yok_mu(pl.get("websiteUri"))
                if not lead:
                    continue
                satirlar.append({
                    "isim": pl.get("displayName", {}).get("text", ""),
                    "ilce": ilce,
                    "adres": pl.get("formattedAddress", ""),
                    "telefon": pl.get("nationalPhoneNumber", ""),
                    "telefon_uluslararasi": pl.get("internationalPhoneNumber", ""),
                    "puan": pl.get("rating", ""),
                    "yorum_sayisi": pl.get("userRatingCount", ""),
                    "not": not_,
                    "harita": pl.get("googleMapsUri", ""),
                    "email": "",           # Elle / Instagram bio'dan doldurulur
                    "instagram": "",
                    "durum": "yeni",       # yeni -> demo_hazir -> gonderildi -> cevap -> teklif -> kazanildi/kaybedildi
                })
            token = data.get("nextPageToken")
            sayfa += 1
            if not token:
                break
            time.sleep(2)
        print(f"{ilce}: toplam lead {len(satirlar)}", file=sys.stderr)

    # Önce yorumu çok olanlar: aktif, para kazanan dükkanlar daha iyi müşteri.
    satirlar.sort(key=lambda r: -(r["yorum_sayisi"] or 0))
    os.makedirs(os.path.dirname(a.cikti) or ".", exist_ok=True)
    with open(a.cikti, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()) if satirlar else ["isim"])
        w.writeheader()
        w.writerows(satirlar)
    print(f"{len(satirlar)} lead yazıldı -> {a.cikti}")


if __name__ == "__main__":
    main()
