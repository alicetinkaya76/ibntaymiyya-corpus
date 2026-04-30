# Canonical JSON Şeması · İbn Teymiyye Tutum Haritalama Sistemi

**Sürüm:** 0.1.0 · **Tarih:** 30 Nisan 2026 · **Faz:** 0 / Hafta 1

> Bu doküman, projenin *kanonik* veri biriminin alanlarını tanımlar. Bu şemaya
> yazılan her birim Faz 1-9 boyunca **stabil** kalacaktır; alan eklemek
> mümkündür ama **alan tipini değiştirmek veya kaldırmak**, geriye dönük
> uyumsuzluk doğurur ve ancak büyük sürüm artışıyla yapılır.

---

## 1 · Tasarım İlkeleri

1. **Asıl metin Arapça korunur, çevrilmez.** `full_text_arabic` orijinal Arap
   alfabesindedir; tüm alıntı/etiket metadata Türkçe veya İngilizce olabilir
   ama metnin kendisi asla.
2. **Edisyon transparanlığı.** Her birim, geldiği OpenITI URI'ı ve matbu
   sayfa referanslarını saklar; aynı eserin farklı baskıları arasında
   `editor_meta` ile ayrılır.
3. **Etiket katmanları opsiyoneldir.** F1-F10 ve topic etiketleri parser
   çıktısında `null` olarak başlar; Hafta 2-4'te dolar.
4. **İki seviyeli birim.** `tier="section"` insan navigasyonu; `tier="passage"`
   makine işleme (LLM, embedding) için. Aynı schema her iki seviyede de
   geçerli, ayırıcı `tier` alanıdır.
5. **Yatay bağlam korunur.** `previous_unit_id` / `next_unit_id` ile birimler
   bir zincir oluşturur; `parent_unit_id` ile dikey hiyerarşi.
6. **İzlenebilirlik.** Her birim hangi parser sürümüyle hangi ham satır
   aralığından çıkarıldığını `extraction_meta` altında saklar.

---

## 2 · Kanonik Birim Yapısı

Aşağıda her alanın **adı**, **tipi**, **zorunluluğu**, **anlamı** ve
**örnek değeri** sıralanır.

### 2.1 · Kimlik ve Köken

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `unit_id` | str | ✓ | Stabil tanımlayıcı: `<work>-<volume>-S<section>-P<passage>` |
| `tier` | str | ✓ | `section` veya `passage` |
| `work_id` | str | ✓ | Eserin kısa kodu: `MajmucFatawa`, `Iman`, `RisalaTadmuriyya` |
| `openiti_uri` | str | ✓ | OpenITI dosya URI'sı tam haliyle |
| `volume` | int? | opt | Mecmû gibi çok ciltli eserlerde cilt no; standalone risâlede `null` |
| `kitab` | str? | opt | Mecmû'da Kitâb başlığı (örn. `كتاب الإيمان`) |
| `bab` | str? | opt | Bâb başlığı (Mecmû'da çoğunlukla `null`) |
| `fasl` | str? | opt | Fasıl/bölüm başlığı (`### \|` sınırlı) |
| `unit_type` | str | ✓ | `question_answer` \| `exposition` \| `refutation` \| `preamble` \| `colophon` |

**`unit_id` formatı kuralları:**

```
<work_code>-<volume?>-S<section_idx>[-P<passage_idx>]

work_code:    MF (Mecmû'l-Fetâvâ) | IMN (Iman standalone) | TDM (Tedmuriyye)
volume:       Sadece Mecmû için: V07, V08, ... (3 haneli değil, tek-iki sayı)
section_idx:  S00, S01, ... 2 haneli, eserdeki section sırası
passage_idx:  P000, P001, ... 3 haneli, section içindeki passage sırası
```

**Örnekler:**

- `MF-V07-S03` → Mecmû Cilt 7, 3. section (insan-okur seviyesi)
- `MF-V07-S03-P012` → aynı section'ın 12. passage'ı (LLM seviyesi)
- `IMN-S00-P004` → Standalone Iman'ın tek section'ının 4. passage'ı
- `TDM-S05` → Tedmuriyye'nin 5. section'ı

### 2.2 · İçerik

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `title` | str? | opt | Section başlığı (passage için ekseriya boş) |
| `question_text` | str? | opt | `سُئل` ile başlayan soru kısmı, varsa |
| `answer_text` | str? | opt | `فأجاب` sonrası cevap kısmı, varsa |
| `full_text_arabic` | str | ✓ | Birimin tam Arapça gövdesi, normalize edilmiş |
| `char_count` | int | ✓ | `full_text_arabic` karakter sayısı |
| `word_count` | int | ✓ | Boşluk-bölünmüş kelime sayısı |

**`full_text_arabic` normalizasyon kuralları:**

- `~~` paragraf devam işareti ile ayrılan satırlar, ortasındaki boşluk
  tek `\n` olacak şekilde **birleştirilir**.
- `# ` satır başı paragraf işaretleyicisi **çıkarılır**.
- `# PageVxxPyyy` satırları çıkarılır (`page_refs`'e taşınır).
- Manuscript folio işaretleri (örn. `ms1901`) metnin içinden çıkarılır
  (`manuscript_markers`'a taşınır).
- Arapça diakritikler (harekelerin tümü) **korunur**.
- Birden fazla ardışık boşluk tek boşluğa indirilir.

### 2.3 · Sayfa, Alıntı ve Referanslar

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `page_refs` | list[str] | ✓ | Birimin yayıldığı sayfalar: `["V07P012","V07P013"]` |
| `quran_quotes` | list[dict] | ✓ | Kur'ân alıntıları: `[{"text":"...","char_offset":[s,e]}]` |
| `hadith_markers` | list[dict] | ✓ | Hadis alıntı işaretleri (Hafta 2'de doldurulur, şimdi `[]`) |
| `manuscript_markers` | list[str] | ✓ | Folio işaretleri: `["ms1901","ms1902"]` |

**`quran_quotes` formatı:**

- `text`: alıntının kendisi, süslü parantez içeriği veya `@QB@..@QE@` arası
- `char_offset`: `full_text_arabic` içindeki **start, end** karakter ofseti.
  Yarı-açık aralık değil, *kapsayıcı* aralık değil — Python slicing ile
  `full_text_arabic[start:end]` çağrısı alıntıyı verir.

### 2.4 · Söylem-Yüzey Örüntüleri

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `discourse_markers` | list[dict] | ✓ | F1-F10 yüzey örüntü tarama sonuçları |

Her giriş:

```json
{
  "pattern": "لو سلَّمنا",
  "char_offset": [340, 350],
  "candidate_label": "F4",
  "confidence": "surface_pattern"
}
```

`candidate_label` **bağlayıcı değildir**; gerçek F1-F10 etiketi Hafta 4'te
LLM ve human annotator zincirinden geçer. `surface_pattern` confidence,
sadece kelime tabanlı ilk teşhis anlamına gelir.

### 2.5 · Etiket Katmanları (Hafta 2-4'te dolacak)

| Alan | Tip | Zorunlu | Şu an |
|---|---|---|---|
| `f1_to_f10_labels` | list[str]? | opt | `null` (Hafta 4) |
| `topic_labels` | dict? | opt | `null`; doldurulduğunda `{"top": "akaid", "mid": "iman", "leaf": "iman_amel"}` |

### 2.6 · Hiyerarşi ve Navigasyon

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `parent_unit_id` | str? | opt | passage için ait olduğu section'ın id'si; section için `null` |
| `section_index` | int | ✓ | section sırası (0-tabanlı) |
| `passage_index` | int? | opt | passage için section içindeki sıra; section için `null` |
| `previous_unit_id` | str? | opt | Yatay önceki birim |
| `next_unit_id` | str? | opt | Yatay sonraki birim |

### 2.7 · Editör ve Baskı Bilgisi

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `editor_meta` | dict | ✓ | Baskının editör/yayıncı bilgisi |
| `source_edition_note` | str | ✓ | Kısa Türkçe edisyon notu |

`editor_meta` örneği:

```json
{
  "editor_name": "عبد الرحمن بن محمد بن قاسم",
  "publisher":   "مجمع الملك فهد لطباعة المصحف الشريف",
  "publication_year": "1416/1995",
  "notation_style": "double_quotes"
}
```

`notation_style` değerleri: `double_quotes` (İbn Kāsım), `square_brackets`
(Albani), `qosa_curly` (al-Sa'awi), `unknown`. Bu alan Faz 1 duplikasyon
tespitinde paralel baskıları eşleştirmek için kullanılır.

### 2.8 · Cross-Corpus ve İzlenebilirlik

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `is_repeat_or_excerpt_of` | str? | opt | Eğer bu birim başka bir birimin tekrarı/alıntısıysa, o birimin `unit_id`'si (Faz 1'de doldurulur) |
| `cross_corpus_refs` | list[str] | ✓ | Bilinen paralel pasajların id'leri (örn. Tedmuriyye = Mecmû V03 P1-128) |
| `extraction_meta` | dict | ✓ | Parser sürümü, çıkarım tarihi, ham satır aralığı |

`extraction_meta` örneği:

```json
{
  "parser_version": "0.1.0",
  "extracted_at":   "2026-04-30T12:34:56Z",
  "source_line_range": [48346, 48512]
}
```

### 2.9 · Gelecek Bağlantıları

| Alan | Tip | Zorunlu | Anlam |
|---|---|---|---|
| `future_links` | dict | ✓ | İleride bağlanacak diğer projelere yer |

Şimdiki şekli:

```json
{
  "tabakat_io": null,
  "islamicatlas": null,
  "halka_book_ref": null
}
```

Bu alanlar bu hafta doldurulmuyor; sadece şema rezervasyonu.

---

## 3 · Tam Şema Örneği (passage seviyesi)

```json
{
  "unit_id": "MF-V07-S03-P012",
  "tier": "passage",
  "work_id": "MajmucFatawa",
  "openiti_uri": "0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1",
  "volume": 7,
  "kitab": "كتاب الإيمان",
  "bab": null,
  "fasl": "في قول السلف الإيمان قول وعمل",
  "unit_type": "exposition",

  "title": null,
  "question_text": null,
  "answer_text": null,
  "full_text_arabic": "وإذا تأملت قول السلف...",
  "char_count": 1842,
  "word_count": 287,

  "page_refs": ["V07P017", "V07P018"],
  "quran_quotes": [
    {"text": "{إنما المؤمنون الذين آمنوا بالله ورسوله}", "char_offset": [120, 165]}
  ],
  "hadith_markers": [],
  "manuscript_markers": ["ms1901"],

  "discourse_markers": [
    {"pattern": "قالت طائفة", "char_offset": [42, 53], "candidate_label": "F3", "confidence": "surface_pattern"}
  ],

  "f1_to_f10_labels": null,
  "topic_labels": null,

  "parent_unit_id": "MF-V07-S03",
  "section_index": 3,
  "passage_index": 12,
  "previous_unit_id": "MF-V07-S03-P011",
  "next_unit_id": "MF-V07-S03-P013",

  "editor_meta": {
    "editor_name": "عبد الرحمن بن محمد بن قاسم",
    "publisher": "مجمع الملك فهد لطباعة المصحف الشريف",
    "publication_year": "1416/1995",
    "notation_style": "double_quotes"
  },
  "source_edition_note": "Şâmile bsk., İbn Kāsım derlemesi, Medine 1995",

  "is_repeat_or_excerpt_of": null,
  "cross_corpus_refs": [],
  "extraction_meta": {
    "parser_version": "0.1.0",
    "extracted_at": "2026-04-30T12:34:56Z",
    "source_line_range": [48720, 48745]
  },

  "future_links": {
    "tabakat_io": null,
    "islamicatlas": null,
    "halka_book_ref": null
  }
}
```

---

## 4 · Birim Tanımı: Section vs Passage

### 4.1 · Section (Tier 1 — insan-okur birimi)

Bir section, **`### |` ile sınırlı tematik blok**tur. Mecmû'da editör İbn
Kāsım'ın koyduğu fasıl başlıkları, Tedmuriyye'de al-Sa'awi'nin başlıkları
section sınırlarıdır. Standalone Iman gibi başlıksız metinler, **tek bir
section** olarak ele alınır.

**Section'lar Streamlit panelde, başlık kartı + sayfa aralığı + kelime
sayısı şeklinde sıralanır.**

### 4.2 · Passage (Tier 2 — makine işleme birimi)

Bir passage, **section içinde 400-800 kelime hedefli** alt birimdir.
Sınırlama kuralı:

1. Section uzunluğu ≤ 800 kelime ise: tek passage = section.
2. Section uzunluğu > 800 kelime ise: passage'lar **paragraf sınırlarına
   saygı duyarak** ~500-700 kelime hedefiyle bölünür.
3. Passage sınırı asla bir paragrafın ortasından geçmez.
4. Bir passage, en az 80 kelime; en fazla 1200 kelime.

**Passage'lar F1-F10 sınıflandırmasına LLM tarafından beslenecek olan
gerçek atom birimlerdir.**

### 4.3 · Neden iki seviye?

Iman el-Kebîr 12.000+ satır, ~120.000 kelime. Section-bazlı (17 birim)
analiz çok kaba (her section'da onlarca farklı F1-F10 etiketi karışık);
paragraf-bazlı (~3.000 paragraf) analiz çok dağınık (bağlam kaybolur).
**~500-700 kelime sweet spot'tur**: argument component classification
literatüründe (Stab & Gurevych 2014, Habernal & Gurevych 2017) konsensüs
budur.

---

## 5 · Validasyon Kuralları

Parser çıkışında her birim için aşağıdaki invariantlar **otomatik test
edilir**:

1. `unit_id` regex `^(MF|IMN|TDM)(-V\d{1,2})?-S\d{2,3}(-P\d{3,4})?$` eşleşir.
2. `tier == "passage"` ise `parent_unit_id` zorunlu, formatı
   `<work>-<volume?>-S<section_idx>` olmalı.
3. `char_count == len(full_text_arabic)`.
4. `word_count == len(full_text_arabic.split())`.
5. `quran_quotes[i].char_offset` `[s, e]` ile `full_text_arabic[s:e]` karşılaştırması
   `quran_quotes[i].text` ile **eşleşmeli** (whitespace farkına izin
   verilmez).
6. `page_refs` regex `^V\d{2}P\d{3,4}$` eşleşir.
7. `discourse_markers[i].candidate_label` ∈ `{F1..F10}`.
8. `editor_meta.notation_style` ∈ `{double_quotes, square_brackets, qosa_curly, unknown}`.

---

## 6 · Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|---|---|---|
| 0.1.0 | 30 Nis 2026 | İlk sürüm (Faz 0 / Hafta 1) |

İleride (Hafta 2+) eklenmesi düşünülenler — *bu sürümde yok*:

- `topic_labels` (Faz 2 atölyesinde finalize edilecek 3-seviyeli taksonomi)
- `f1_to_f10_labels` ve `f1_to_f10_confidence` (Faz 4 sınıflandırıcı çıktısı)
- `embedding_vector` (Faz 3, BGE-M3)
- `inter_annotator_agreement` (gold pasajlar için Cohen's kappa)

---

*Bu doküman canonical schema spesifikasyonunun referans noktasıdır. Parser
bu şemaya yazılı `Unit` Pydantic dataclass'ını implementasyonun tek
gerçeği olarak kabul eder; bu doküman ile kod arasında uyumsuzluk olursa
**kod düzeltilir, bu doküman güncellenir** (asla tersi değil).*
