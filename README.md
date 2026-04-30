# İbn Teymiyye Külliyatı · Hesaplamalı Tutum Haritalama Sistemi

> Klasik Arapça dini-polemik söylemde söylem-fonksiyon temelli tutum sınıflandırması yapan,
> 124 eserlik OpenITI korpusu üzerinde çalışan, çok dilli kamusal araştırma platformu.

## Yürütücüler

- **Dr. Ali Çetinkaya** (PI, teknik liderlik) — Selçuk Üniversitesi Bilgisayar Mühendisliği
- **Dr. Hüseyin Gökalp** (Co-PI, içerik liderliği) — Selçuk Üniversitesi İlahiyat Fakültesi

## Çekirdek Tez

Bu sistem bir tam metin arama motoru değildir. Klasik Arapça söylemde aynı pasaj farklı
söylemsel işlevler taşır: öz-tasdik, öz-tefrik, muhalif alıntısı, diyalektik kabul, şartlı
önerme, icmâ iddiası, tafsîl, tashîh, tarihsel anlatı, hipotetik. Bu on söylem-fonksiyon
(F1-F10) tipolojisi üzerinden külliyat tasniflendirilir, tartışmalar haritalanır, görünür
çelişkiler çözümlenir ve İbn Teymiyye'nin kendi diliyle "bana atfedilen iddianın reddi"
pasajları sistematik olarak yüzeye çıkarılır.

Ayrıntılar için: `docs/strategy/IbnTaymiyye_Strateji_v1.docx`

## Korpus

- 124 ayrı eser (OpenITI 0700AH dump'ı)
- ~12,7 milyon Arapça kelime
- 6.069 fetva sorusu işareti
- 16.426 yapısal başlık

## Yığın

- **Veri:** SQLite + Python; immutable raw + canonical JSON
- **Lexical arama:** Meilisearch
- **Embedding:** BGE-M3 (multilingual)
- **Vektör DB:** Qdrant
- **Yerel LLM:** Ollama + Qwen 2.5 32B (4-bit)
- **API LLM (zor vakalar):** Anthropic Claude
- **Backend:** FastAPI + SQLAlchemy
- **KG:** Neo4j Community
- **Frontend:** Astro 5 (TR/AR/EN)
- **Anotasyon:** Custom Streamlit UI (Mücteba) + Doccano

## Klasör Yapısı

```
ibntaymiyya/
├── data/
│   ├── raw/openiti/        # 124 OpenITI dosyası (immutable)
│   ├── canonical/          # Parser çıktısı: birim-bazlı JSON
│   ├── derived/            # Embeddings, indexler
│   └── annotations/        # F1-F10 etiketleri, gold-set
├── pipeline/
│   ├── parser/             # mARkdown → JSON
│   ├── enrichment/         # LLM ile sınıflama
│   └── kg_builder/         # Triple çıkarımı, Neo4j
├── annotate/
│   ├── streamlit/          # Custom anotasyon UI
│   ├── doccano/            # Doccano config
│   └── guidelines/         # Anotasyon kılavuzları
├── api/                    # FastAPI backend
├── web/                    # Astro frontend
├── notebooks/              # Jupyter keşif
├── docs/
│   ├── strategy/           # Strateji dökümanı v1.0
│   ├── methodology/        # F1-F10 kılavuzu
│   └── papers/             # Yayın taslakları
├── tests/
├── sessions/               # Session tutanakları
└── scripts/                # Kurulum yardımcıları
```

## Faz 0 · Pilot (4 Hafta)

Hedef cilt: **Kitâbü'l-Îmân el-Kebîr** (Mecmû'l-Fetâvâ Cilt 7)

- **Hafta 1:** Parser + canonical JSON + Streamlit iskeleti
- **Hafta 2:** Taksonomi atölyesi + 50 birim gold annotation
- **Hafta 3:** BGE-M3 embeddings + Qdrant + F1-F10 prototip
- **Hafta 4:** Vizyon demosu + TÜBİTAK ön-veri raporu

## Lisans

- Kod: MIT (bkz. LICENSE)
- Üretilen yapısal veri: CC BY 4.0
- OpenITI ham veri: kendi lisansı geçerlidir (CC BY-NC-SA 4.0)

## Atıf

```
Çetinkaya, A. & Gökalp, H. (2026). İbn Teymiyye Külliyatı: Hesaplamalı
Tutum Haritalama Sistemi. v1.0 [Strateji dökümanı]. Selçuk Üniversitesi.
```

## İletişim

ali.cetinkaya@selcuk.edu.tr
