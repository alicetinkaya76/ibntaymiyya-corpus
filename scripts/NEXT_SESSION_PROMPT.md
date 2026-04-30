# İbn Teymiyye Hesaplamalı Tutum Haritalama Sistemi · Faz 0 Hafta 1

> Bu prompt'u **yeni bir Claude oturumunun ilk mesajı** olarak yapıştır.
> Hangi modelle başlıyorsan başla, bu prompt sıfırdan tüm bağlamı kuruyor.

---

## 0 · Bağlam

Selçuk Üniversitesi'nden Dr. Ali Çetinkaya'yım. Bilgisayar Mühendisliği'nde Dr. Öğretim Üyesiyim; NLP/ML/dijital beşeri bilimler alanında çalışıyorum. Şu an Selçuk İlahiyat'tan Dr. Hüseyin Gökalp ile birlikte yeni bir hesaplamalı söylem analizi projesinin Faz 0 pilotunu başlatıyorum.

Önceki oturumda projenin tam strateji dökümanı hazırlandı (`IbnTaymiyye_Strateji_v1.docx`, 28 sayfa). Klasör iskeleti, korpus dump'ı ve git repo'su şu konumda kurulmuş durumda:

```
/Volumes/LaCie/ibntaymiyya/
├── data/raw/openiti/        # 124 OpenITI mARkdown dosyası, immutable
├── data/canonical/          # boş (bu oturumda doldurulacak)
├── pipeline/parser/         # boş (bu oturumda kod yazılacak)
├── annotate/streamlit/      # boş (bu oturumda iskelet)
├── docs/strategy/           # IbnTaymiyye_Strateji_v1.docx
└── ...
```

GitHub: `github.com/alicetinkaya76/ibntaymiyya-corpus`
Geliştirme makinesi: MacBook Pro M4 Max (48 GB RAM), Python 3.11+, Node 22+
Korpus konumu: `/Volumes/LaCie/ibntaymiyya/data/raw/openiti/` (LaCie harici disk)

## 1 · Projenin Çekirdek Tezi

Bu sistem bir tam metin arama motoru **değildir**. Klasik Arapça dini-polemik söylemde aynı pasaj birden fazla söylem-fonksiyonu taşır. On-kategorili tipoloji (F1-F10) proje boyunca bağlayıcıdır:

| Kod | Fonksiyon | Açıklama |
|-----|-----------|----------|
| F1 | Öz-tasdik | Yazarın kendi açık pozisyonu |
| F2 | Öz-tefrik | Kendisine atfedileni reddetme |
| F3 | Muhalif alıntısı | Bir karşıtın pozisyonunu aktarma |
| F4 | Çürütmek için kabul | Diyalektik لو سلَّمنا |
| F5 | Şartlı önerme | Eğer X ise Y |
| F6 | İcmâ iddiası | Kümülatif yetki çağrısı |
| F7 | Tafsîl | Anlam ayrımı (İbn Teymiyye imzası) |
| F8 | Tashîh | Muhalifin söylediğini düzeltme |
| F9 | Tarihsel anlatı | Nötr biyografik aktarım |
| F10 | Hipotetik | Düşünce deneyi |

Ayrıntı için: `docs/strategy/IbnTaymiyye_Strateji_v1.docx` Bölüm 3.2.

## 2 · Bağlayıcı Tasarım İlkeleri

1. **Orijinal Arapça merkezdedir.** Asıl pasajlar **çevrilmez**. Sadece taksonomi etiketleri, soru özetleri, biyografik metadata TR/EN'e çevrilir.
2. **Edisyon transparanlığı.** Her birim için OpenITI URI ve matbu sayfa referansı kayıtlıdır.
3. **Söylem konumu "haritala", asla "rehabilite" değil.** "Müdâfa", "vindicate" gibi kelimeler hiçbir yayında geçmez.
4. **Maktabah platformu yoktur**, sıfırdan inşa ediyoruz.
5. **Yerel-makine öncelikli.** Pipeline M4 Max'te koşacak şekilde tasarlanır; sunucuya bağımlılık minimum.
6. **Açık kaynak + açık veri.** Kod MIT, üretilen yapısal veri CC BY 4.0.
7. **`data/raw/openiti/` immutable'dır.** Asla düzenlenmez; tüm dönüşümler `data/canonical/` altında yapılır.

## 3 · OpenITI mARkdown Format Bilgisi

Korpus dosyalarındaki yapısal işaretleme:

```
#META#Header#End#                Metadata sınırı
### |                            cilt/kitab düzeyi
### ||                           bâb/kāide/bölüm
### |||                          alt-bölüm/fasıl
### ||||                         soru (سُئل / وسئل)
### |||||                        cevap (فأجاب)
PageVxxPxxx                      matbu sayfa referansı (örn. PageV07P123)
@QB@ ... @QE@                    Kur'ân alıntı sınırları
~~                               paragraf devam (line continuation)
```

Korpus istatistikleri (önceki oturumdan, doğrulanmış):
- 124 ayrı eser
- 12.715.726 Arapça kelime
- 71.701.750 karakter (gövde)
- 16.426 yapısal başlık
- 6.069 fetva sorusu işareti
- En büyük 5 eser kelime sayısıyla: Mecmû'l-Fetâvâ (2.998.639), Resâil ve Fetâvâ (1.243.385), Fetâvâ Kübrâ (902.752), Der'ü Teâruz (672.745), Minhâcü's-Sünne (654.296)

## 4 · Faz 0 Pilot · Hedef Cilt

**Kitâbü'l-Îmân el-Kebîr** (Mecmû'l-Fetâvâ Cilt 7)

Sebep: Mürcie, Hâriciler, Cehmiyye karşı argümanları yoğun; F3-F4-F8 kategorileri zengin. Müşebbihelik tartışmasını içermediği için politik açıdan en güvenli pilottur. Orta uzunluktadır; 4 haftada uçtan uca koşulabilir.

OpenITI dosyası: `data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1`
İlgili cildin sınırı: `### |` ile başlayan ve içinde "كتاب الإيمان الكبير" (veya benzeri açılış başlığı) olan blok.

## 5 · Bu Oturumun (Hafta 1) Somut Hedefleri

Bu oturumda **dört çıktı** üretilmeli, sırasıyla:

### Hedef 1 · Canonical JSON Şeması Tasarımı

`docs/methodology/canonical_schema.md` dosyasında, her birim için ne saklayacağımızı netleştir:

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
  "question_text": "...",                 # Eğer varsa (سُئل bloğu)
  "answer_text": "...",                   # فأجاب bloğu
  "full_text_arabic": "...",
  "page_refs": ["V07P123", "V07P124"],
  "quran_quotes": [
    {"text": "...", "surah": null, "ayah": null, "char_offset": [120, 165]}
  ],
  "hadith_markers": [],                   # Ekleme: hadis sınırı tespiti sonra
  "char_count": 1842,
  "word_count": 287,
  "f1_to_f10_labels": null,               # Faz 4'te doldurulacak
  "topic_labels": null,                   # Faz 2'de doldurulacak
  "source_edition_note": "Şâmile bsk., İbn Kāsım derlemesi"
}
```

Şemayı kesinleştirmeden parser yazılmaz. Şema dosyası TR yorumlu ama field isimleri İngilizce.

### Hedef 2 · OpenITI mARkdown Parser Modülü

Yer: `pipeline/parser/openiti_parser.py`

Sorumlulukları:
- mARkdown dosyası okuma + metadata header ayrıştırma
- `### |`, `### ||`, `### |||`, `### ||||`, `### |||||` hiyerarşik ağaç çıkarımı
- Soru-cevap birim sınırlarını tespit (سُئل / فأجاب örüntüleri)
- `PageVxxPxxx` referanslarını çıkarma
- `@QB@ ... @QE@` Kur'ân alıntı sınırlarını çıkarma
- `~~` paragraf devamlarını birleştirme
- Stable `unit_id` üretimi

Test edilebilir olmalı; `tests/parser/test_openiti_parser.py` altında en az 5 birim testi.

CLI arayüzü:
```bash
python -m pipeline.parser \
  --input data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1 \
  --kitab "الإيمان الكبير" \
  --output data/canonical/iman_v0.1.json
```

### Hedef 3 · Kitâbü'l-Îmân Çıkarımı

Parser'ı Mecmû'l-Fetâvâ üzerinde koş; sadece Kitâbü'l-Îmân el-Kebîr cildine ait birimleri filtrele; `data/canonical/iman_v0.1.json` üret.

Sayım kontrolü: Önceki oturumda Mecmû'da 25 üst seviye Kitâb tespit edilmişti; bunlardan biri Kitâbü'l-Îmân el-Kebîr olmalı. Kitap içinde tahminen 200-400 birim çıkacak.

Yan-çıktı: `notebooks/01_iman_exploration.ipynb` — birim tipi dağılımı, ortalama uzunluk, soru/cevap oranı, sayfa aralığı görselleri.

### Hedef 4 · Streamlit Demo İskeleti

Yer: `annotate/streamlit/app.py`

Minimum işlevsellik:
- `data/canonical/iman_v0.1.json` dosyasını yükle
- Sol panelde birim listesi (id, kısa başlık, tip)
- Sağ panelde seçilen birimin Arapça gövdesi (sağdan-sola yazım, font: Amiri veya Noto Naskh Arabic)
- Sayfa referansları, soru metni, cevap metni ayrı bölümlerde
- (Bu oturumda) henüz F1-F10 etiketleme yok; sadece görüntüleme
- (Bu oturumda) henüz arama yok; sadece liste navigasyonu

Çalıştırma:
```bash
streamlit run annotate/streamlit/app.py
```

Mücteba ile haftaya birlikte F1-F10 etiketleme widget'ı eklenecek.

## 6 · Bu Oturumda Yapılmayacaklar

Aşağıdakiler **bu oturumun kapsamı dışındadır**, sonraki haftalarda gelir:

- F1-F10 etiketleme arayüzü (Hafta 3)
- BGE-M3 embeddings ve Qdrant indeksi (Hafta 3)
- LLM zero-shot sınıflandırıcı (Hafta 2)
- Konu taksonomisi (Hafta 2 atölye)
- FastAPI backend (Faz 3)
- Astro frontend (Faz 8)
- Tüm 124 eserin parser'dan geçirilmesi (Faz 1)

Scope creep'ten kaçın. Sadece dört hedefe odaklan.

## 7 · Çalışma Tarzı Tercihleri

- Kapsamlı düşün, kaliteyi kısalık adına feda etme.
- Tek bir büyük dosya değil, modüler kod yaz.
- Her modülün kısa Türkçe docstring'i olsun.
- Test yazmadan parser'ı tamamlama.
- Önemli kararlar (örn. `unit_id` formatı, soru-cevap sınır kuralı) için önce şemayı/dokümantasyonu güncelle, sonra kodu yaz.
- Komutları çalıştırırken çıktıyı tam göster; özetleme.
- Hata varsa atlama, debug et.
- Türkçe konuş; teknik terimler İngilizce kalabilir.
- Session tutanağını oturum sonunda `sessions/2026-MM-DD-faz0-hafta1.md` olarak kaydet.

## 8 · Diğer Aktif Projelerimle İlişki

Bu projenin aşağıdaki projelerle bağlantı noktaları olacak (bu oturum için bilgi amaçlı, kod yok):

- **tabakat.io**: İbn Teymiyye'nin scholar düğümü oradan giriş kapısı olacak; ileride biyografi-eser bağlantısı.
- **İslamicAtlas.org**: İbn Teymiyye'nin Mardin/Şam/Mısır rotaları İslamicAtlas'a yansıyacak.
- **Halka**: Hoover veya El-Tobgui kitabı ileride Halka'da işlenecek; iddia ekstraksiyonu yardımcı veri sağlayabilir.

Bu üç bağlantıyı bu oturumda kurmuyoruz; sadece schema tasarımında "future_links" alanı bırakabilirsin.

## 9 · İletişim Tarzı

- "Hocam" diye hitap etme, "Ali" yeterli.
- Ben her şeyi onayladıktan sonra yaz; büyük dosya yazmadan önce kısa plan göster.
- Belirsizlik varsa sor, varsayım kurma.
- Anthropic Claude API anahtarı `.env`'de olacak; bu oturumda API çağrısı yok.

## 10 · Bu Oturumdan Beklenen Çıktılar Listesi

Sonunda bu dosyalar `data/canonical/` ve `pipeline/parser/` ve `annotate/streamlit/` altında olmalı:

- [ ] `docs/methodology/canonical_schema.md`
- [ ] `pipeline/parser/openiti_parser.py`
- [ ] `pipeline/parser/__main__.py` (CLI)
- [ ] `tests/parser/test_openiti_parser.py` (≥ 5 test)
- [ ] `data/canonical/iman_v0.1.json` (Kitâbü'l-Îmân birim havuzu)
- [ ] `notebooks/01_iman_exploration.ipynb`
- [ ] `annotate/streamlit/app.py` (demo iskeleti)
- [ ] `annotate/streamlit/requirements.txt` (Streamlit-spesifik deps)
- [ ] `sessions/2026-MM-DD-faz0-hafta1.md` (session tutanağı)
- [ ] Git commit'i: `feat: Faz 0 Hafta 1 · parser + Kitâbü'l-Îmân + Streamlit iskeleti`

---

## Başlangıç Komutu

Bu prompt'u okuduktan sonra ilk eylemin şunlar olsun:

1. `ls /Volumes/LaCie/ibntaymiyya/` ile klasör iskeletini doğrula.
2. `wc -l /Volumes/LaCie/ibntaymiyya/data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1` ile Mecmû dosyasını gör.
3. Dosyanın ilk 100 satırını incele; metadata header'ı ve ilk Kitâb sınırını anla.
4. **Sonra bana kısa bir plan göster:** "Önce schema'yı şu alanlarla yazacağım, sonra parser'ı şu modüllere ayıracağım, test'lerde şu örnekleri kullanacağım." Onayımı al, sonra kod yazmaya başla.

Hadi başlayalım.
