# Pet Shop Web Sitesi İşi — İstanbul

**Fikir:** İstanbul'da web sitesi olmayan pet shopları bul → her birine kendi adıyla demo site hazırla →
demo linkini gönder → beğenenlere fiyat teklif et.

```
leads/      Bulunan dükkanlar (CSV — Excel/Google Sheets'te açılır, satış takibi de burada)
tools/      lead_finder.py (dükkan bulur) · generate_sites.py (demo site üretir)
site-template/  Demo site şablonu (mobil uyumlu, tek dosya)
sites/      Üretilmiş demo siteler (her dükkana bir klasör)
outreach/   Mesaj şablonları (WhatsApp / e-posta / takip / itiraz) + fiyatlandırma
```

## Adım adım

### 1. Web sitesi olmayan dükkanları bul
Google Cloud'da bir proje açıp **Places API (New)**'yi etkinleştirin, API anahtarı alın
(aylık ücretsiz kredi bu iş için genelde yeterli).

```bash
export GOOGLE_MAPS_API_KEY=...
python3 tools/lead_finder.py                          # İstanbul'un 39 ilçesi
python3 tools/lead_finder.py --ilce Kadıköy Üsküdar   # sadece bazı ilçeler
```
Sonuç: `leads/leads.csv` — sitesi olmayan veya sadece Instagram/Facebook linki olan, açık işletmeler;
yorum sayısı yüksek olan (yani aktif, kazanan) dükkanlar en üstte.

API anahtarı olmadan başlamak için: `leads/aday_listesi.csv` — internet rehberlerinden derlenmiş
6 aday. **Bilgiler eski olabilir; mesaj atmadan önce Google Haritalar'dan site/telefon kontrol edin.**

### 2. E-posta / Instagram bul
Places API e-posta vermez. Google Haritalar'daki Instagram linkinden veya bio'dan e-posta/WhatsApp'ı
CSV'deki `email` ve `instagram` sütunlarına ekleyin.

### 3. Demo siteleri üret
```bash
python3 tools/generate_sites.py leads/leads.csv
```
`sites/` klasörünü ücretsiz olarak **Netlify Drop** (app.netlify.com/drop — klasörü sürükle-bırak)
veya Cloudflare Pages'e yükleyin. Her dükkanın linki: `https://<siteniz>/<dukkan-klasoru>/`

### 4. Mesaj gönder
`outreach/mesaj_sablonlari.md` → günde 20–30 mesajı geçmeyin (WhatsApp hesabı spam'den kapanmasın),
her mesaj kişisel olsun. CSV'deki `durum` sütununu güncelleyin:
`yeni → demo_hazir → gonderildi → cevap → teklif → kazanildi / kaybedildi`

### 5. Teklif ver
`outreach/fiyatlandirma.md`. Satış olunca demo'ya dükkanın kendi fotoğraflarını ekleyin,
üstteki "örnek tasarımdır" bandını silin, alan adını bağlayın.

## ⚖️ Yasal not (Türkiye)
- 6563 sayılı Kanun: **esnaf ve tacirlere** ticari elektronik ileti ön onay olmadan gönderilebilir, ama
  her mesajda **ret (çıkış) imkânı** olmalı ve "istemiyorum" diyene bir daha yazılmamalı. Şablonlarda bu satır var.
- Toplu gönderim yaparsanız **İYS** (İleti Yönetim Sistemi) kaydı gerekebilir; büyümeden önce bir
  muhasebeci/avukata danışın.
- Dükkan bilgileri (isim, telefon, adres) herkese açık işletme bilgisidir; yine de KVKK kapsamında
  sadece bu teklif için kullanın, listeyi başkasıyla paylaşmayın/satmayın.
- Fatura kesmek için şahıs şirketi veya serbest meslek kaydı gerekir.
