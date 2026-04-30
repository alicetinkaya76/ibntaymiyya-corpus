# H2 Manuel Doğrulama Atölye Paketi

**Tarih:** 30 Nisan 2026
**Atölye:** İbn Teymiyye Tutum Haritalama · H2 (Mecmû V07 ↔ Standalone Iman)
**Annotator:** Hüseyin Gökalp (Selçuk İlahiyat) — uzman, otorite
**Ölçüm:** Cohen κ (Hüseyin Gökalp ↔ Claude 4.7 baseline) — paper material

---

## İçerik

```
h2_review_template_v0.1.xlsx     ← Hüseyin Hoca'ya göndereceğin dosya
EMAIL_TASLAGI.txt                ← Email gövdesi (Türkçe)
build_review_xlsx.py             ← Üretici script (ihtiyaç olursa yeniden çalıştırılır)
README.md                        ← Bu dosya
```

---

## Excel dosyasının yapısı

| Sayfa | Görünür mü | Açıklama |
|---|---|---|
| 1. Talimatlar | ✅ | Protokol, 5 sınıf tanımı, örnekler, ipuçları |
| 2. Etiketleme | ✅ | 26 pair · Hüseyin Hoca'nın çalışacağı sayfa |
| 3. Claude_Baseline_GIZLI | 🔒 hidden | LLM ön-tahminleri · atölye sonrası açılır |
| 4. Özet | ✅ | Canlı ilerleme + sınıf dağılımı + bant×etiket çapraz tablo |

---

## Atölye akışı

### 1) Hüseyin Hoca'ya gönder

İki seçenek:

**A) Excel olarak yolla (basit):**
- `h2_review_template_v0.1.xlsx`'i email ekine koy
- `EMAIL_TASLAGI.txt`'in içeriğini email gövdesine yapıştır
- Hüseyin Hoca masaüstü Excel veya LibreOffice ile açar

**B) Google Sheets'e yükle (senkron çalışma için ideal):**
- drive.google.com'a `h2_review_template_v0.1.xlsx`'i yükle
- "Sağ tık → Aç → Google Sheets" ile aç (xlsx → Sheets dönüşümü)
- Sağ üstten "Paylaş" → Hüseyin Hoca'nın email'i (cetinkaya@gmail.com vs)
- "Düzenleyebilir" yetkisi ver
- Email taslağını göndereceğin emaile yapıştır + Sheets linki paylaş
- **Avantaj:** Aynı anda iki kişi açıkken sen ekran üzerinde anlık takip edebilirsin

### 2) Atölye sırasında

- Hüseyin Hoca 26 pair'i sırayla etiketler
- Sen yanında veya ekran paylaşımında oluyorsan, soruları anında yanıtlarsın
- Tartışmalı pair'leri "Notlar" kolonunda **TARTIŞMA** kelimesiyle işaretler
- "Özet" sayfası canlı güncellenir — kaç tamamlandı, hangi sınıftan kaç tane

### 3) Atölye sonu

- Hüseyin Hoca tamamlanmış xlsx'i sana gönderir (veya Sheets ise zaten paylaşımda)
- Bu dosyayı Claude'a gönder (zip ile veya Sheets linki)
- Claude şu işleri yapar:
  1. Hüseyin Hoca'nın etiketlerini Pydantic AnnotationSet JSON'una çevirir
  2. **Cohen κ** hesabı: `cohen_kappa(claude.annotations, huseyin.annotations)`
  3. **Confusion matrix**: hangi sınıflarda uyuşmadık raporu
  4. **Threshold kalibrasyonu**: Hüseyin etiketleri authority kabul edilip
     precision/recall eğrisi ve F1-optimal eşik
  5. **Tartışmalı pair'lerin tahkim listesi**: TARTIŞMA notu olanlar +
     Claude'la uyuşmayan pair'ler birlikte
  6. **Kanonik JSON güncelleme**: `is_repeat_or_excerpt_of` ve
     `cross_corpus_refs` alanları doldurulur

### 4) Tahkim oturumu (atölye sonu, opsiyonel)

- Claude_Baseline_GIZLI sayfası "Format → Sayfayı göster" ile açılır
- Tartışmalı + uyuşmayan pair'ler birlikte gözden geçirilir
- "Gold etiket" kararı verilir (Hüseyin Hoca authority)
- Bu gold etiketler paper'da rapor edilen final dataset

---

## Dosya yeniden üretilirse

Eğer xlsx'i yeniden üretmen gerekirse (örn. veri güncellenmiş, format değişikliği):

```bash
cd /Volumes/LaCie/ibntaymiyya/
cp scripts/build_review_xlsx.py scripts/   # zaten varsa atla
python scripts/build_review_xlsx.py
# Çıktı: docs/atolye/h2_review_template_v0.1.xlsx
```

26 pair seçimi `random.seed(42)` ile deterministic — her çalıştırmada aynı 26 pair üretilir.

---

## Alternatif: Streamlit?

Streamlit araç (zaten kurulu, çalışıyor) **paper showcase** için kalır.
Atölyeyi xlsx ile yapmanın avantajları:

- Hüseyin Hoca'nın doğal ortamı (Excel her akademisyenin günlük aleti)
- Kurulum sıfır (Streamlit için aynı wifi gerek)
- Senkron çalışma (Sheets'te iki kişi aynı anda)
- Veri taşınabilir (xlsx atölye sonrası arşivlenir)

Streamlit'in **avantajı:** Amiri font + RTL + skor pill renkler. Ama
Hüseyin Hoca'nın asıl iş yapacağı yer karar verme, görsel şıklık değil.

---

## Sonraki adım

1. Bu zip'i indir → unzip
2. xlsx'i Google Drive'a yükle (tavsiye edilen) veya email ekine koy
3. EMAIL_TASLAGI.txt'in içeriğini email gövdesine yapıştır
4. Hüseyin Hoca'ya gönder
5. Atölye günü ekran paylaşımında destekçi ol
6. Atölye sonu doldurulmuş xlsx'i Claude'a gönder

Atölye sonrası Claude'la S5'e başlanır:
- Cohen κ + confusion matrix
- Threshold kalibrasyonu
- Kanonik JSON in-place yazımı
- Final cross-corpus map
- (Eğer V03 ekstraksiyonu hazırsa) H1 testi
