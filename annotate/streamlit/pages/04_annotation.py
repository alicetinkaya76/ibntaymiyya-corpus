"""Streamlit sayfa: H2 manuel doğrulama etiketleme aracı.

Hüseyin Hoca (ve istenirse ikinci annotator) 26 stratified örneği
EXACT/EDITED/EXCERPT/OVERLAP/NOISE olarak işaretler. Her etiket atomic
olarak diske kaydedilir; oturum kesilirse devam edilebilir.

Kullanım:
    1. Sidebar'dan "Yeni oturum başlat" → adını gir → session başlar.
    2. Veya "Devam et" → mevcut oturumlardan birini seç.
    3. Her pair'i sırayla incele, etiketle. "Kaydet ve sonraki" tuşu
       atomic save yapıp bir sonraki pair'e geçer.
    4. Tamamlanınca "Oturumu kapat" → completed=True işaretlenir.

Kayıt yeri: data/annotations/h2_review/{annotator_slug}_{session_id}.json

DİR / DEĞİLDİR:
- DİR: Single-rater veya double-rater (Cohen κ için) etiketleme aracı.
- DEĞİLDİR: Etiket sınıfı tasarım aracı (sınıflar sabit: 5 sınıf).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from pipeline.crosscorpus.annotation_schema import (  # noqa: E402
    AnnotationSet,
    LabelKind,
    PairAnnotation,
    list_annotation_sets,
    load_annotation_set,
    save_annotation_set,
)


DATA_CANONICAL = REPO_ROOT / "data" / "canonical"
DATA_DERIVED = REPO_ROOT / "data" / "derived"
ANNOTATIONS_DIR = REPO_ROOT / "data" / "annotations" / "h2_review"
DOCS_REVIEW_MD = REPO_ROOT / "docs" / "cross_corpus" / "h2_pairs_for_review.md"


st.set_page_config(
    page_title="Annotation · İbn Teymiyye H2",
    page_icon="✍️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Stil
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    .arabic-body {
        font-family: 'Amiri', 'Traditional Arabic', serif;
        font-size: 1.05rem;
        line-height: 1.85;
        direction: rtl;
        text-align: right;
        background: #fafaf6;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        border: 1px solid #e1ddc8;
        max-height: 380px;
        overflow-y: auto;
    }
    .source-body { border-left: 4px solid #3a6ea5; }
    .target-body { border-left: 4px solid #a55a3a; }
    .progress-pill {
        display: inline-block;
        background: #e6f0fa;
        padding: 3px 10px;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
    }
    .label-help {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: #666;
        background: #f5f5f0;
        padding: 8px 12px;
        border-radius: 4px;
        margin-top: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Veri yükleme
# ---------------------------------------------------------------------------


@st.cache_data
def load_units_dict(path: Path) -> dict:
    if not path.exists():
        return {}
    return {u["unit_id"]: u for u in json.loads(path.read_text(encoding="utf-8"))}


@st.cache_data
def load_review_pairs() -> list[dict]:
    """Stratified review setini al. h2_pairs_for_review.md Markdown'dan değil,
    güvenilirlik için tfidf_char JSON'dan yeniden hesaplar (random.seed(42)).
    """
    pairs_path = DATA_DERIVED / "cross_corpus_h2_tfidf_char_v0.1.json"
    if not pairs_path.exists():
        return []
    pairs = json.loads(pairs_path.read_text())["pairs"]

    # Top-1 per source
    top1 = {}
    for p in pairs:
        sid = p["source_unit_id"]
        if sid not in top1 or p["similarity"] > top1[sid]["similarity"]:
            top1[sid] = p
    top1_list = sorted(top1.values(), key=lambda p: -p["similarity"])

    # Stratified sampling — generate_h2_review_set.py ile aynı mantık
    import random
    random.seed(42)
    bands = [
        (0.95, 1.01, 5, "Çok yüksek (likely birebir)"),
        (0.80, 0.95, 5, "Yüksek (büyük ihtimal düzenlenmiş tekrar)"),
        (0.60, 0.80, 10, "Orta-yüksek (paragraf ortak, paraphrase olabilir)"),
        (0.40, 0.60, 5, "Orta (parça ortak, asıl iddia farklı olabilir)"),
        (0.30, 0.40, 5, "Düşük (gürültü mü gerçek mi?)"),
    ]
    selected = []
    for lo, hi, n, label in bands:
        candidates = [p for p in top1_list if lo <= p["similarity"] < hi]
        sampled = random.sample(candidates, min(n, len(candidates)))
        for p in sampled:
            p["band_label"] = label
        selected.extend(sampled)
    return selected


# ---------------------------------------------------------------------------
# Sayfa içeriği
# ---------------------------------------------------------------------------

st.title("✍️ H2 Manuel Doğrulama · Etiketleme Aracı")

iman = load_units_dict(DATA_CANONICAL / "iman_v0.1.json")
iman_st = load_units_dict(DATA_CANONICAL / "iman_standalone_v0.1.json")
review_pairs = load_review_pairs()

if not iman or not iman_st:
    st.error("Kanonik JSON'lar bulunamadı.")
    st.stop()

if not review_pairs:
    st.error(
        "Review seti üretilememedi. Önce şunu çalıştır:\n\n"
        "```bash\n"
        "python -m pipeline.crosscorpus --source data/canonical/iman_v0.1.json "
        "--target data/canonical/iman_standalone_v0.1.json "
        "--output data/derived/cross_corpus_h2_tfidf_char_v0.1.json "
        "--method tfidf_char --threshold 0.3 --topk 3\n"
        "```"
    )
    st.stop()


# ---------------------------------------------------------------------------
# Oturum yönetimi
# ---------------------------------------------------------------------------

st.sidebar.header("Oturum")

mode = st.sidebar.radio(
    "Mod",
    ["Yeni oturum", "Devam et", "Görüntüle (read-only)"],
)

aset: AnnotationSet | None = None

if mode == "Yeni oturum":
    annotator = st.sidebar.text_input(
        "Annotator adı", placeholder="Hüseyin Gökalp"
    )
    if st.sidebar.button("Başla", type="primary", disabled=not annotator.strip()):
        session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        aset = AnnotationSet(
            annotator=annotator.strip(),
            session_id=session_id,
            review_set_path="docs/cross_corpus/h2_pairs_for_review.md",
        )
        save_annotation_set(aset, base_dir=ANNOTATIONS_DIR)
        st.session_state["current_aset_path"] = str(
            ANNOTATIONS_DIR / f"_temp"
        )  # placeholder; gerçek path aşağıda atanır
        # Yeni oturumu yükle
        existing = list_annotation_sets(ANNOTATIONS_DIR)
        if existing:
            st.session_state["current_aset_path"] = str(existing[-1])
        st.rerun()

elif mode in ("Devam et", "Görüntüle (read-only)"):
    existing = list_annotation_sets(ANNOTATIONS_DIR)
    if not existing:
        st.sidebar.info("Henüz oturum yok. 'Yeni oturum' ile başlayın.")
        st.stop()
    chosen = st.sidebar.selectbox(
        "Oturum",
        options=existing,
        format_func=lambda p: p.name,
    )
    if chosen:
        st.session_state["current_aset_path"] = str(chosen)

# Aktif oturumu yükle
current_path = st.session_state.get("current_aset_path")
if not current_path or not Path(current_path).exists():
    st.info("Soldan bir oturum seçin veya 'Yeni oturum' ile başlayın.")
    st.stop()

aset = load_annotation_set(current_path)
read_only = (mode == "Görüntüle (read-only)")

# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

n_total = len(review_pairs)
done = sum(
    1 for p in review_pairs
    if aset.label_for(p["source_unit_id"], p["target_unit_id"]) is not None
)

st.markdown(
    f"<span class='progress-pill'><b>{aset.annotator}</b> · "
    f"{aset.session_id} · <b>{done}/{n_total}</b> tamamlandı"
    f"{' · 🔒 read-only' if read_only else ''}</span>",
    unsafe_allow_html=True,
)
st.progress(done / n_total if n_total else 0)

# ---------------------------------------------------------------------------
# Hangi pair'e bakacağız
# ---------------------------------------------------------------------------

# Default: ilk etiketlenmemiş, yoksa ilk pair
default_idx = next(
    (
        i for i, p in enumerate(review_pairs)
        if aset.label_for(p["source_unit_id"], p["target_unit_id"]) is None
    ),
    0,
)

st.sidebar.divider()
st.sidebar.subheader("Pair gezintisi")
selected_idx = st.sidebar.number_input(
    f"Pair # (1–{n_total})",
    min_value=1,
    max_value=n_total,
    value=default_idx + 1,
    step=1,
) - 1

current_pair = review_pairs[selected_idx]
src = iman.get(current_pair["source_unit_id"], {})
tgt = iman_st.get(current_pair["target_unit_id"], {})

# ---------------------------------------------------------------------------
# Pair gösterimi
# ---------------------------------------------------------------------------

st.divider()

st.subheader(
    f"{selected_idx + 1:02d}/{n_total} · "
    f"{current_pair['source_unit_id']} ↔ {current_pair['target_unit_id']}"
)
st.caption(
    f"**Bant:** {current_pair.get('band_label', '?')}  ·  "
    f"**Skor:** {current_pair['similarity']:.3f}  ·  "
    f"**Düzeltilmiş:** {current_pair['adjusted_similarity']:.3f}  ·  "
    f"**Kur'ân yoğunluğu:** kaynak={current_pair['quran_density_source']:.2f}, "
    f"hedef={current_pair['quran_density_target']:.2f}"
)

c1, c2 = st.columns(2)
with c1:
    page_s = (
        f"{src['page_refs'][0]}–{src['page_refs'][-1]}"
        if src.get("page_refs") else "?"
    )
    st.markdown(
        f"**📖 Kaynak (Mecmû V07 / İbn Kāsım)** · "
        f"{src.get('word_count', 0)} kelime · {page_s}"
    )
    st.markdown(
        f"<div class='arabic-body source-body'>{src.get('full_text_arabic', '')}</div>",
        unsafe_allow_html=True,
    )
with c2:
    page_t = (
        f"{tgt['page_refs'][0]}–{tgt['page_refs'][-1]}"
        if tgt.get("page_refs") else "?"
    )
    st.markdown(
        f"**🎯 Hedef (Standalone Iman / Albani)** · "
        f"{tgt.get('word_count', 0)} kelime · {page_t}"
    )
    st.markdown(
        f"<div class='arabic-body target-body'>{tgt.get('full_text_arabic', '')}</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Etiketleme formu
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Karar")

current_label = aset.label_for(
    current_pair["source_unit_id"], current_pair["target_unit_id"]
)
existing_notes = ""
if current_label is not None:
    for a in aset.annotations:
        if (
            a.source_unit_id == current_pair["source_unit_id"]
            and a.target_unit_id == current_pair["target_unit_id"]
        ):
            existing_notes = a.notes
            break

label_options = list(LabelKind)
label_idx = label_options.index(current_label) if current_label else 0

# Sınıf rehberi
LABEL_HELP = {
    LabelKind.EXACT: "Birebir tekrar (kelimelik farklar olabilir, ama aynı pasaj)",
    LabelKind.EDITED: "Albani edisyonu — kelime/sıra değişiklikleri ama aynı argüman",
    LabelKind.EXCERPT: "Hedef, kaynağın bir kısmı (özet veya alıntı)",
    LabelKind.OVERLAP: "Ortak konu/ortak ayet, ama farklı argüman",
    LabelKind.NOISE: "Yanlış eşleşme — algoritma yanılmış",
}

chosen_label = st.radio(
    "Etiket",
    options=label_options,
    index=label_idx,
    format_func=lambda l: l.value,
    horizontal=True,
    disabled=read_only,
    key=f"label_{selected_idx}",
)

st.markdown(
    f"<div class='label-help'>{LABEL_HELP[chosen_label]}</div>",
    unsafe_allow_html=True,
)

notes = st.text_area(
    "Notlar (opsiyonel)",
    value=existing_notes,
    placeholder="Bu pair hakkında neden bu kararı verdiğin, sayfa atıfları, vs.",
    height=80,
    disabled=read_only,
    key=f"notes_{selected_idx}",
)

# Kaydet butonları
if not read_only:
    col_save, col_save_next, col_skip = st.columns([1, 1, 1])
    with col_save:
        if st.button("💾 Kaydet"):
            ann = PairAnnotation(
                source_unit_id=current_pair["source_unit_id"],
                target_unit_id=current_pair["target_unit_id"],
                label=chosen_label,
                notes=notes,
                annotator=aset.annotator,
                annotated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            aset.add_or_update(ann)
            save_annotation_set(aset, base_dir=ANNOTATIONS_DIR)
            st.success(f"Kaydedildi: {chosen_label.value}")
            st.rerun()

    with col_save_next:
        if st.button("✅ Kaydet ve sonraki"):
            ann = PairAnnotation(
                source_unit_id=current_pair["source_unit_id"],
                target_unit_id=current_pair["target_unit_id"],
                label=chosen_label,
                notes=notes,
                annotator=aset.annotator,
                annotated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            aset.add_or_update(ann)
            save_annotation_set(aset, base_dir=ANNOTATIONS_DIR)
            if selected_idx + 1 < n_total:
                # session_state'i değiştirmek yerine sidebar'da güncellenecek
                pass
            st.success(f"Kaydedildi: {chosen_label.value}")
            # Sonraki için sidebar'daki number_input zaten default_idx'i tekrar hesaplayacak
            st.rerun()

    with col_skip:
        if st.button("⏭ Atla (kaydetmeden)"):
            st.info("Bu pair atlandı.")

# ---------------------------------------------------------------------------
# Tamamlama + indirme
# ---------------------------------------------------------------------------

st.divider()

if done == n_total and not read_only:
    if st.button("🎉 Oturumu kapat (completed=True)", type="primary"):
        aset.completed = True
        save_annotation_set(aset, base_dir=ANNOTATIONS_DIR)
        st.success("Oturum kapatıldı. Sonuçları başkalarıyla paylaşabilirsin.")
        st.rerun()

# JSON indirme
if aset.annotations:
    st.download_button(
        "📥 Bu oturumun JSON'unu indir",
        data=json.dumps(aset.model_dump(mode="json"), ensure_ascii=False, indent=2),
        file_name=Path(current_path).name,
        mime="application/json",
    )

st.caption(
    f"Diske son yazım: `{current_path}`. Atomic save uygulanır — "
    "etiketler crash olsa bile korunur."
)
