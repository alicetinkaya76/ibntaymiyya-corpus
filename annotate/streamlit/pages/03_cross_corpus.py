"""Streamlit sayfa: Cross-corpus paralel pasaj görüntüleyici.

Kullanım: `streamlit run annotate/streamlit/app.py`'den sonra
sidebar'daki "03 Cross Corpus" linkine tıkla.

Bir source passage seçilince, üç method'un (TF-IDF char/word, shingle)
top-3 candidate target'ını yan yana gösterir. Skor + adjusted similarity
+ Kur'ân density + sayfa referansları ile birlikte.

NEDİR / DEĞİLDİR:
- DİR: Cross-corpus eşleşmeleri keşfetmek için araştırma görüntüleyicisi.
- DEĞİLDİR: Etiketleme aracı (o `04_annotation.py`'de).
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_CANONICAL = REPO_ROOT / "data" / "canonical"
DATA_DERIVED = REPO_ROOT / "data" / "derived"

st.set_page_config(
    page_title="Cross-Corpus · İbn Teymiyye",
    page_icon="🔗",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Stil (RTL Arapça, vurgulamalar)
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    .arabic-body {
        font-family: 'Amiri', 'Traditional Arabic', serif;
        font-size: 1.15rem;
        line-height: 1.95;
        direction: rtl;
        text-align: right;
        background: #fafaf6;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        border: 1px solid #e1ddc8;
        max-height: 480px;
        overflow-y: auto;
    }
    .source-body { border-left: 4px solid #3a6ea5; }
    .target-body { border-left: 4px solid #a55a3a; }
    .meta-line {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .score-pill {
        display: inline-block;
        background: #e6f0fa;
        padding: 2px 9px;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        margin-right: 4px;
    }
    .score-high { background: #d4edda; }
    .score-mid  { background: #fff3cd; }
    .score-low  { background: #f8d7da; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Veri yükleme (cache'li)
# ---------------------------------------------------------------------------


@st.cache_data
def load_units(path: Path) -> dict:
    """unit_id → unit dict. Cache'li."""
    if not path.exists():
        return {}
    return {u["unit_id"]: u for u in json.loads(path.read_text(encoding="utf-8"))}


@st.cache_data
def load_pairs(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["pairs"]


def score_class(sim: float) -> str:
    if sim >= 0.7:
        return "score-high"
    if sim >= 0.4:
        return "score-mid"
    return "score-low"


# ---------------------------------------------------------------------------
# Sayfa içeriği
# ---------------------------------------------------------------------------

st.title("🔗 Cross-Corpus · Paralel Pasaj Görüntüleyici")

st.caption(
    "Bir kaynak passage seçin; sağda üç method'un top eşleşmelerini "
    "yan yana karşılaştırın. Bu sayfa **etiketleme aracı değildir** — "
    "etiketleme için sidebar'dan `04 Annotation` sayfasına geçin."
)

# Hangi karşılaştırmayı göstereceğimizi seç
comparison = st.sidebar.radio(
    "Karşılaştırma",
    options=["H2: Iman ↔ Standalone Iman"],
    help="S4'te H1 (Tedmuriyye ↔ V03) eklenecek.",
)

if comparison.startswith("H2"):
    SOURCES = load_units(DATA_CANONICAL / "iman_v0.1.json")
    TARGETS = load_units(DATA_CANONICAL / "iman_standalone_v0.1.json")
    SOURCE_LABEL = "Mecmû V07 Iman el-Kebîr"
    TARGET_LABEL = "Standalone Iman (Albani)"
    pairs_char = load_pairs(DATA_DERIVED / "cross_corpus_h2_tfidf_char_v0.1.json")
    pairs_word = load_pairs(DATA_DERIVED / "cross_corpus_h2_tfidf_word_v0.1.json")
    pairs_shingle = load_pairs(DATA_DERIVED / "cross_corpus_h2_shingle_v0.1.json")
else:
    st.error("Bilinmeyen karşılaştırma.")
    st.stop()

if not SOURCES or not TARGETS:
    st.error(
        "Kanonik veri bulunamadı. `data/canonical/`'da gerekli JSON'ları "
        "doğrula."
    )
    st.stop()

if not pairs_char:
    st.warning(
        "Türetilmiş veri bulunamadı. Önce şunu çalıştır:\n\n"
        "```bash\n"
        "python -m pipeline.crosscorpus --source data/canonical/iman_v0.1.json "
        "--target data/canonical/iman_standalone_v0.1.json "
        "--output data/derived/cross_corpus_h2_tfidf_char_v0.1.json "
        "--method tfidf_char --threshold 0.3 --topk 3\n```"
    )
    st.stop()

# Source passage'larını filtrele (sadece tier=passage)
source_passages = sorted(
    [u for u in SOURCES.values() if u.get("tier") == "passage"],
    key=lambda u: u["unit_id"],
)

# Sidebar: source seçici
st.sidebar.header(f"Kaynak — {SOURCE_LABEL}")
unit_options = [u["unit_id"] for u in source_passages]

# Default: en yüksek skorlu pair'in source'u
if pairs_char:
    default_src = pairs_char[0]["source_unit_id"]
    default_idx = unit_options.index(default_src) if default_src in unit_options else 0
else:
    default_idx = 0

selected_src_id = st.sidebar.selectbox(
    "Source passage",
    options=unit_options,
    index=default_idx,
    help="Karşılaştırılacak kaynak passage'ı seç.",
)

src_unit = SOURCES.get(selected_src_id)
if not src_unit:
    st.error(f"Source unit bulunamadı: {selected_src_id}")
    st.stop()

# Bu source için her method'tan top-3 al
def top_n_for(pairs: list[dict], src_id: str, n: int = 3) -> list[dict]:
    matches = [p for p in pairs if p["source_unit_id"] == src_id]
    matches.sort(key=lambda p: -p["similarity"])
    return matches[:n]


top_char = top_n_for(pairs_char, selected_src_id, 3)
top_word = top_n_for(pairs_word, selected_src_id, 3)
top_shg = top_n_for(pairs_shingle, selected_src_id, 3)

# ---------------------------------------------------------------------------
# Sol: kaynak passage
# ---------------------------------------------------------------------------

col_src, col_tgt = st.columns([1, 1])

with col_src:
    st.subheader(f"📖 {SOURCE_LABEL}")
    page_str = (
        f"{src_unit['page_refs'][0]}–{src_unit['page_refs'][-1]}"
        if src_unit.get("page_refs") else "?"
    )
    st.markdown(
        f"<div class='meta-line'><b>{src_unit['unit_id']}</b> · "
        f"{src_unit.get('unit_type', '?')} · "
        f"{src_unit.get('word_count', 0)} kelime · {page_str}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='arabic-body source-body'>{src_unit.get('full_text_arabic', '')}</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Sağ: top eşleşmeler tab'larıyla
# ---------------------------------------------------------------------------

with col_tgt:
    st.subheader(f"🎯 {TARGET_LABEL} — top eşleşmeler")

    if not top_char:
        st.info("Bu source için eşik üstünde eşleşme yok.")
    else:
        # Üç method tab'ı
        tabs = st.tabs(["TF-IDF char_wb (3,5)", "TF-IDF word (1,2)", "Shingle Jaccard"])

        for tab, top, label in zip(tabs, [top_char, top_word, top_shg], ["char", "word", "shingle"]):
            with tab:
                if not top:
                    st.info(f"Bu method için eşleşme yok ({label}).")
                    continue
                # En iyi 3'ü göster
                rank_options = [
                    f"#{i+1}  {p['target_unit_id']}  ·  {p['similarity']:.3f}"
                    for i, p in enumerate(top)
                ]
                chosen_rank = st.radio(
                    f"Rank ({label})",
                    options=range(len(top)),
                    format_func=lambda i, t=top: rank_options[i],
                    horizontal=True,
                    key=f"rank_{label}",
                )
                p = top[chosen_rank]
                tgt_unit = TARGETS.get(p["target_unit_id"], {})
                tgt_page_str = (
                    f"{tgt_unit['page_refs'][0]}–{tgt_unit['page_refs'][-1]}"
                    if tgt_unit.get("page_refs") else "?"
                )

                # Skor pill'leri
                cls = score_class(p["similarity"])
                st.markdown(
                    f"<span class='score-pill {cls}'>skor {p['similarity']:.3f}</span> "
                    f"<span class='score-pill'>düz. {p['adjusted_similarity']:.3f}</span> "
                    f"<span class='score-pill'>QD-S {p['quran_density_source']:.2f}</span> "
                    f"<span class='score-pill'>QD-T {p['quran_density_target']:.2f}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='meta-line'><b>{p['target_unit_id']}</b> · "
                    f"{tgt_unit.get('unit_type', '?')} · "
                    f"{tgt_unit.get('word_count', 0)} kelime · {tgt_page_str}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='arabic-body target-body'>"
                    f"{tgt_unit.get('full_text_arabic', '')}</div>",
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------------------------
# Alt: özet + linkler
# ---------------------------------------------------------------------------

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(
        "Source coverage (skor ≥ 0.5)",
        f"{sum(1 for p in pairs_char if p['similarity'] >= 0.5 and p['source_unit_id'] == selected_src_id)}",
        help="Bu source'un ≥0.5 skorlu match sayısı (top-3 dahil)",
    )
with c2:
    if top_char:
        st.metric(
            "En iyi adjusted",
            f"{top_char[0]['adjusted_similarity']:.3f}",
            help="Kur'ân-yoğunluğa göre düzeltilmiş skor",
        )
with c3:
    st.metric("Kelime sayısı", src_unit.get("word_count", 0))

st.caption(
    "💡 Etiketleme yapmak için sidebar'dan **04 Annotation** sayfasına geç. "
    "Bu sayfa sadece keşif amaçlıdır."
)
