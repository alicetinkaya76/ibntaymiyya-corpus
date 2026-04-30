# İbn Teymiyye Hesaplamalı Tutum Haritalama Sistemi · Faz 0 Hafta 1

> **Bu prompt'u yeni bir Claude oturumunun ilk mesajı olarak yapıştır.**
> Hangi modelle başlıyorsan başla, prompt sıfırdan tüm bağlamı kuruyor.
> Bu oturumda dört somut çıktı üretilecek: canonical JSON şeması, OpenITI parser modülü, Kitâbü'l-Îmân çıkarımı, Streamlit demo iskeleti.

---

## 0 · Kim ve Bağlam

Selçuk Üniversitesi Bilgisayar Mühendisliği'nden Dr. Ali Çetinkaya'yım (ORCID: 0000-0002-7747-6854; ali.cetinkaya@selcuk.edu.tr). NLP/ML/dijital beşeri bilimler alanında çalışıyorum. Selçuk İlahiyat'tan Dr. Hüseyin Gökalp ile yeni bir hesaplamalı söylem analizi projesinin Faz 0 pilotunu başlatıyorum.

Önceki oturumda projenin kapsamlı strateji dökümanı (28 sayfa) hazırlandı, klasör iskeleti kuruldu, git repo başlatıldı:

- **Repo:** `github.com/alicetinkaya76/ibntaymiyya-corpus` (v0.1.0 etiketli)
- **Yerel disk:** `/Volumes/LaCie/ibntaymiyya/` (124 OpenITI dosyası `data/raw/openiti/` altında)
- **Geliştirme makinesi:** MacBook Pro M4 Max (48 GB RAM)

Bu oturumda kod ve dosya çıktılarını `/mnt/user-data/outputs/` altına üretelim; ben sonra hepsini LaCie'ye taşıyıp commit edeceğim.

## 1 · Bu Oturuma Yüklediğim Dosyalar

`/mnt/user-data/uploads/` altında üç dosya bulacaksın:

- **`IbnTaymiyye_Strateji_v1.docx`** — 28 sayfalık tam strateji dökümanı. F1-F10 tipolojisi (Bölüm 3.2), beş katmanlı mimari (Bölüm 3.3), Faz 0 detayları (Bölüm 5.2), yöntem ayrıntıları orada.
- **`0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1`** — Mecmû'l-Fetâvâ (≈16 MB, ≈3M Arapça kelime). Pilot hedef olan Kitâbü'l-Îmân el-Kebîr Cilt 7 olarak bu dosyanın içinde.
- **`0728IbnTaymiyya.Iman.Shamela0007564-ara1`** — Standalone Kitâbü'l-Îmân (küçük, ≈210KB). Parser unit testleri için ideal çünkü hem aynı tematik alana ait hem de basit bir yapısı var.
- **`0728IbnTaymiyya.RisalaTadmuriyya.Shamela0022666-ara1`** — Risâletü't-Tedmuriyye (≈135KB). Orta uzunluklu risâle; parser'ın "monolitik tek-yazar metni" durumunu test etmek için.

## 2 · Çekirdek Tez (Özet)

Bu sistem bir tam metin arama motoru **değildir**. Klasik Arapça dini-polemik söylemde aynı pasaj birden fazla söylem-fonksiyonu taşır. Aşağıdaki on-kategorili tipoloji (F1-F10) proje boyunca bağlayıcıdır:

| Kod | Fonksiyon | Açıklama |
|-----|-----------|----------|
| F1 | Öz-tasdik | Yazarın kendi açık pozisyonu |
| F2 | Öz-tefrik | Kendisine atfedileni reddetme (نُسِبَ إليّ, افترى عليّ) |
| F3 | Muhalif alıntısı | Bir karşıtın pozisyonunu aktarma |
| F4 | Çürütmek için kabul | Diyalektik لو سلَّمنا |
| F5 | Şartlı önerme | Eğer X ise Y |
| F6 | İcmâ iddiası | Kümülatif yetki çağrısı |
| F7 | Tafsîl | Anlam ayrımı (İbn Teymiyye metodolojik imzası) |
| F8 | Tashîh | Muhalifin söylediğini düzeltme |
| F9 | Tarihsel anlatı | Nötr biyografik aktarım |
| F10 | Hipotetik | Düşünce deneyi |

Detay için strateji dökümanı Bölüm 3.2.

## 3 · Bağlayıcı Tasarım İlkeleri

1. **Orijinal Arapça merkezdedir.** Asıl pasajlar **çevrilmez**. Sadece taksonomi etiketleri, soru özetleri, biyografik metadata TR/EN'e çevrilir.
2. **Edisyon transparanlığı.** Her birim için OpenITI URI ve matbu sayfa referansı kayıtlıdır.
3. **Söylem konumu "haritala", asla "rehabilite" değil.** "Müdâfa", "vindicate" gibi kelimeler hiçbir yayında geçmez.
4. **Maktabah platformu yok**, sıfırdan inşa ediyoruz.
5. **Yerel-makine öncelikli.** Pipeline M4 Max'te koşacak; sunucu bağımlılığı minimum.
6. **Açık kaynak + açık veri.** Kod MIT, üretilen yapısal veri CC BY 4.0.
7. **Raw dosyalar immutable.** Asla düzenlenmez; tüm dönüşümler `data/canonical/` altında.

## 4 · OpenITI mARkdown Format

Yüklenen dosyalarda görelisin; özet:

```
#META#Header#End#                Metadata sınırı
### |                            cilt/kitap düzeyi
### ||                           bâb/kāide/bölüm
### |||                          alt-bölüm/fasıl
### ||||                         soru (سُئل / وسئل)
### |||||                        cevap (فأجاب)
PageVxxPxxx                      matbu sayfa referansı
@QB@ ... @QE@                    Kur'ân alıntı sınırları
~~                               paragraf devam
```

Korpus istatistikleri (124 eserin tümü, doğrulanmış):
- 12.715.726 Arapça kelime
- 71.701.750 karakter (gövde)
- 16.426 yapısal başlık
- 6.069 fetva sorusu işareti
- Mecmû'l-Fetâvâ tek başına 2.998.639 kelime, 2.297 soru, 828 başlık

## 5 · Pilot Hedef

**Kitâbü'l-Îmân el-Kebîr** (Mecmû'l-Fetâvâ Cilt 7)

Sebep: Mürcie, Hâriciler, Cehmiyye karşı argümanları yoğun; F3-F4-F8 kategorileri zengin. Müşebbihelik tartışmasını içermediği için politik açıdan en güvenli pilottur. Orta uzunluktadır.

Mecmû dosyasının içinde `### |` ile başlayan 25 üst seviye "Kitâb" var; bunlardan biri "كتاب الإيمان الكبير" (veya benzeri açılış başlığı). Cildin sınırını başlık örüntüsü ile tespit et.

## 6 · Bu Oturumun Dört Somut Çıktısı

### Çıktı 1 · Canonical JSON Şema Tasarımı

`docs/methodology/canonical_schema.md`

Her birim için ne saklayacağımızı netleştir. Önerilen alan listesi (genişletmeye/düzeltmeye açık):

```python
{
  "unit_id": "MF-V07-K01-B02-Q003",      # Stable identifier
  "work_id": "MajmucFatawa",
  "openiti_uri": "0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1",
  "volume": 7,
  "kitab": "كتاب الإيمان الكبير",
  "bab": "...",
  "fasl": "...",
  "unit_type": "question_answer | exposition | refutation | preamble",
  "title": "...",
  "question_text": "...",
  "answer_text": "...",
  "full_text_arabic": "...",
  "page_refs": ["V07P123", "V07P124"],
  "quran_quotes": [
    {"text": "...", "char_offset": [120, 165]}
  ],
  "hadith_markers": [],
  "char_count": 1842,
  "word_count": 287,
  "f1_to_f10_labels": null,
  "topic_labels": null,
  "source_edition_note": "Şâmile bsk., İbn Kāsım derlemesi"
}
```

Field isimleri İngilizce; yorumlar ve açıklamalar Türkçe. Şemayı kesinleştirmeden parser yazma.

### Çıktı 2 · OpenITI mARkdown Parser Modülü

Yer: `pipeline/parser/openiti_parser.py` (+ `__main__.py` CLI)

Sorumlulukları:
- mARkdown dosyası okuma + metadata header ayrıştırma
- `### |`, `### ||`, `### |||`, `### ||||`, `### |||||` hiyerarşik ağaç çıkarımı
- Soru-cevap birim sınırı tespiti (سُئل / فأجاب örüntüleri)
- `PageVxxPxxx` referans çıkarımı
- `@QB@ ... @QE@` Kur'ân alıntı sınır çıkarımı
- `~~` paragraf devam birleştirme
- Stable `unit_id` üretimi

CLI imzası:
```bash
python -m pipeline.parser \
  --input data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1 \
  --kitab "الإيمان الكبير" \
  --output data/canonical/iman_v0.1.json
```

Test edilebilir olmalı: `tests/parser/test_openiti_parser.py` altında **en az 5 birim testi**. Tedmuriyye ve standalone Iman dosyalarını test fixture olarak kullan.

### Çıktı 3 · Kitâbü'l-Îmân Çıkarımı

`data/canonical/iman_v0.1.json` üret. Mecmû'da Kitâbü'l-Îmân el-Kebîr cildinin sınırını tespit et, sadece o cilde ait birimleri filtrele. Tahminen 200-400 birim çıkacak.

Yan-çıktı: `notebooks/01_iman_exploration.py` (Jupyter cell formatlı `.py` dosyası VEYA `.ipynb`). İçinde:
- Birim tipi dağılımı (soru-cevap vs. exposition oranı)
- Ortalama uzunluk histogramı
- Sayfa aralığı doğrulaması
- En uzun 5 ve en kısa 5 birimden örnek snippet

### Çıktı 4 · Streamlit Demo İskeleti

Yer: `annotate/streamlit/app.py` (+ `requirements.txt`)

Minimum işlevsellik:
- `iman_v0.1.json` dosyasını yükle (path config edilebilir)
- Sol panel: birim listesi (id, kısa başlık, tip)
- Sağ panel: seçilen birimin Arapça gövdesi (sağdan-sola, font: Amiri / Noto Naskh Arabic)
- Sayfa referansları, soru metni, cevap metni ayrı bölümlerde
- F1-F10 etiketleme **henüz yok** (Hafta 3'te gelecek)
- Arama **henüz yok** (Hafta 3'te gelecek)

## 7 · Çıktıların Yerleştirilmesi

Tüm çıktıları `/mnt/user-data/outputs/` altına şu yapıyla bırak:

```
outputs/
├── docs/methodology/canonical_schema.md
├── pipeline/parser/__init__.py
├── pipeline/parser/openiti_parser.py
├── pipeline/parser/__main__.py
├── tests/parser/__init__.py
├── tests/parser/test_openiti_parser.py
├── data/canonical/iman_v0.1.json
├── annotate/streamlit/app.py
├── annotate/streamlit/requirements.txt
├── notebooks/01_iman_exploration.py    (veya .ipynb)
└── sessions/2026-MM-DD-faz0-hafta1.md
```

Ben sonra LaCie'ye `cp -r` edip commit edeceğim. Aynen `/Volumes/LaCie/ibntaymiyya/` üzerine bindirilecek şekilde organize et.

## 8 · Bu Oturumda YAPILMAYACAKLAR

Scope creep'ten uzak dur. Aşağıdakiler sonraki haftalarda gelir:

- F1-F10 etiketleme arayüzü (Hafta 3, Mücteba ile)
- BGE-M3 embeddings ve Qdrant indeksi (Hafta 3)
- LLM zero-shot sınıflandırıcı (Hafta 2)
- Konu taksonomisi (Hafta 2 atölye, Hüseyin Hoca ile)
- FastAPI backend (Faz 3)
- Astro frontend (Faz 8)
- Tüm 124 eserin parser'dan geçirilmesi (Faz 1)
- Auto-defensive layer (Faz 7)

Sadece dört çıktıya odaklan.

## 9 · Çalışma Tarzı

- **Türkçe konuş**; teknik terimler İngilizce kalabilir (parser, embedding, classifier, vs.).
- **Kapsamlı düşün**, kaliteyi kısalık adına feda etme.
- **Modüler kod** yaz; tek büyük dosya değil.
- **Her modülün kısa Türkçe docstring'i** olsun.
- **Test yazmadan parser'ı tamamlama.**
- **Önce plan göster, onay al, sonra kod yaz.** Önemli kararlarda (örn. `unit_id` formatı, soru-cevap sınır kuralı) önce şemayı/dokümantasyonu güncelle, sonra kodu yaz.
- **Komutları çalıştırırken çıktıyı tam göster**; özetleme.
- **Hata varsa atlama**, debug et.
- **Bana "Hocam" diye hitap etme**, "Ali" yeterli.
- **Belirsizlik varsa sor**, varsayım kurma.
- **Session tutanağı:** oturum sonunda `sessions/2026-MM-DD-faz0-hafta1.md` yaz; içinde alınan kararlar, edilen ödünler, sonraki oturumda yapılacaklar.

## 10 · Diğer Aktif Projelerimle İlişki (Bilgi Amaçlı)

Bu projenin ileride bağlanacağı projeler (bu oturumda kod yok, sadece schema'da yer bırak):

- **tabakat.io** — İbn Teymiyye'nin scholar düğümü oradan giriş kapısı olacak.
- **İslamicAtlas.org** — İbn Teymiyye'nin Mardin/Şam/Mısır rotaları İslamicAtlas'a yansıyacak.
- **Halka** — Hoover veya El-Tobgui kitabı ileride okuma grubunda işlenecek.

Schema'da `future_links: { tabakat_io: null, islamicatlas: null, halka_book_ref: null }` gibi opsiyonel alan ekleyebilirsin.

## 11 · İlk Eylem Listesi

Bu prompt'u okuduktan sonra **doğrudan kod yazma**. Sırasıyla şunları yap:

1. **Yüklenen dosyaları doğrula:** `ls -la /mnt/user-data/uploads/` ile dört dosyayı gör.
2. **Mecmû'nun ilk 200 satırını incele:** metadata header'ı, ilk Kitâb sınırını, soru-cevap örüntüsünü gör.
3. **Strateji dökümanı Bölüm 3.2 (F1-F10) ve Bölüm 5.2'yi (Faz 0)** dökümandan oku — extract-text ile.
4. **Standalone Iman dosyasının yapısını incele:** Mecmû'dakinden ne kadar farklı, tipik bir risâle yapısı nasıl?
5. **Tedmuriyye'ye bak:** parser test fixture'ı olarak ne kadar kullanışlı?
6. **Bana plan sun:**
   - "Schema'yı şu alanlarla yazacağım"
   - "Parser'ı şu modüllere böleceğim (örn. `tokenizer.py`, `tree_builder.py`, `unit_extractor.py`)"
   - "Test'lerde şu örnekleri kullanacağım"
   - "Streamlit'i şu sayfa yapısıyla kuracağım"
7. **Onayımı al.** Sorularım olursa cevapla.
8. **Sonra kod yazmaya başla.** Çıktıları `/mnt/user-data/outputs/` altına yapıştır.

Hadi başlayalım.
