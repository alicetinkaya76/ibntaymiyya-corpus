"""İbn Teymiyye Tutum Haritalama · Streamlit demo iskeleti.

Hafta 1 hedefi: Pilot JSON'ı (Iman el-Kebîr) sol panel + sağ panel
mizanpajıyla görselleştirmek.

NEDİR / DEĞİLDİR
- DEĞİLDİR: F1-F10 etiketleme aracı (Hafta 4'te eklenecek widget)
- DEĞİLDİR: arama / dizin (Hafta 3'te elastic/whoosh entegre edilecek)
- DİR: Kur'ân alıntıları, sayfa referansları, discourse marker
  vurgulamasıyla birlikte yapılandırılmış metin görüntüleyici.

Çalıştırma:
    cd ibntaymiyya/
    streamlit run annotate/streamlit/app.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import streamlit as st


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA = REPO_ROOT / "data" / "canonical" / "iman_v0.1.json"

st.set_page_config(
    page_title="İbn Teymiyye Tutum Haritalama (v0.1)",
    page_icon="📖",
    layout="wide",
)

# Amiri Arapça font + RTL CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');

    .arabic-body {
        font-family: 'Amiri', 'Traditional Arabic', serif;
        font-size: 1.4rem;
        line-height: 2.1;
        direction: rtl;
        text-align: right;
        background: #fafaf6;
        padding: 1.5rem 2rem;
        border-radius: 6px;
        border: 1px solid #e1ddc8;
    }
    .quran-quote {
        background: #fff7d6;
        padding: 0 4px;
        border-bottom: 1px dashed #c8a634;
    }
    .marker-F2 { background: #ffe0e0; }
    .marker-F3 { background: #ffe8d0; }
    .marker-F4 { background: #d8edd0; }
    .marker-F5 { background: #d8e8ff; }
    .marker-F6 { background: #e0d6f0; }
    .marker-F7 { background: #d0eaea; }
    .marker-F8 { background: #f8d8d8; }
    .marker-F10 { background: #f0e6c0; }

    .page-marker {
        display: inline-block;
        background: #5a6a7a;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        padding: 1px 5px;
        border-radius: 3px;
        margin: 0 4px;
        vertical-align: middle;
    }

    .section-card {
        background: #f4f0e8;
        border-left: 3px solid #6a8c7a;
        padding: 8px 12px;
        margin: 4px 0;
        font-family: 'Amiri', serif;
        font-size: 1rem;
        direction: rtl;
        text-align: right;
        cursor: pointer;
    }
    .section-card.selected {
        border-left-color: #c83a3a;
        background: #f6e8e0;
    }
    .meta-pill {
        display: inline-block;
        background: #e8e0c8;
        color: #5a4a2a;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 10px;
        margin-right: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Veri yükleme
# ---------------------------------------------------------------------------


@st.cache_data
def load_units(path: Path) -> list[dict]:
    """Kanonik JSON'ı yükler ve cache'e koyar."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def find_units_by_path(directory: Path) -> list[Path]:
    """data/canonical/ altındaki tüm pilot JSON'ları bulur."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


# ---------------------------------------------------------------------------
# Metin render etme
# ---------------------------------------------------------------------------


def render_arabic_body(unit: dict) -> str:
    """Bir birimin gövdesini HTML olarak işaretlemelerle render eder.

    İşaretlemeler:
    - Kur'ân alıntıları → `<span class="quran-quote">...</span>`
    - Discourse marker'lar → renkli arkaplan (F2-F10)
    - PageVxxPyyy referansları zaten metin dışına alınmış; sadece
      başlıkta gösterilir.
    """
    text = unit["full_text_arabic"]
    # Aşağıdaki algoritma char_offset üzerinden span'ları ekler.
    # Çakışmaları önlemek için tüm span'ları offset bazlı sıralar
    # ve metni soldan sağa parça parça birleştirir.

    spans = []
    for q in unit.get("quran_quotes", []):
        s, e = q["char_offset"]
        spans.append((s, e, "quran-quote", None))
    for m in unit.get("discourse_markers", []):
        s, e = m["char_offset"]
        cls = f"marker-{m['candidate_label']}"
        spans.append((s, e, cls, m["candidate_label"]))

    if not spans:
        # Sadece kaçış
        return _escape_html(text)

    spans.sort(key=lambda x: (x[0], -x[1]))

    out_parts: list[str] = []
    cursor = 0
    for s, e, cls, label in spans:
        if s < cursor:
            # çakışma: atla (basit yaklaşım; v0.2'de iç içe span'lar)
            continue
        # Önce arada kalan ham metin
        out_parts.append(_escape_html(text[cursor:s]))
        title_attr = f' title="{label}"' if label else ""
        out_parts.append(
            f'<span class="{cls}"{title_attr}>{_escape_html(text[s:e])}</span>'
        )
        cursor = e

    out_parts.append(_escape_html(text[cursor:]))
    return "".join(out_parts)


def _escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# UI · sol panel
# ---------------------------------------------------------------------------


def left_panel(units: list[dict]) -> Optional[str]:
    """Eser + section seçici. Seçilen section'ın unit_id'sini döner."""
    st.subheader("Eser ve Bölüm")

    # Eser işareti — pilot çıktıda tek eser olduğu için bilgi amaçlı
    work_id = units[0]["work_id"] if units else "(boş)"
    volume = units[0]["volume"] if units else None
    kitab = units[0]["kitab"] if units else None
    if kitab:
        st.markdown(f"**Eser:** {work_id}")
        st.markdown(f"**Cilt:** {volume}")
        st.markdown(f"**Kitâb:** <span dir='rtl'>{kitab}</span>", unsafe_allow_html=True)
        # Editör notu
        ed = units[0].get("editor_meta", {})
        if ed.get("editor_name"):
            st.markdown(
                f'<span class="meta-pill">Editör: '
                f'<span dir="rtl">{ed["editor_name"]}</span></span>',
                unsafe_allow_html=True,
            )
        if ed.get("notation_style"):
            st.markdown(
                f'<span class="meta-pill">Notasyon: '
                f'{ed["notation_style"]}</span>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("Section listesi")

    sections = [u for u in units if u["tier"] == "section"]
    if not sections:
        st.info("Hiç section bulunmadı.")
        return None

    # Radio yerine selectbox: çok section'lı eserlerde daha kullanışlı
    section_options = [
        f"{s['unit_id']}: "
        f"{(s['title'] or '(başlıksız preamble)')[:50]} "
        f"({s['word_count']:,} kel)"
        for s in sections
    ]
    selected_idx = st.selectbox(
        "Bir section seç:",
        range(len(sections)),
        format_func=lambda i: section_options[i],
        index=0,
    )
    return sections[selected_idx]["unit_id"]


# ---------------------------------------------------------------------------
# UI · sağ panel
# ---------------------------------------------------------------------------


def right_panel(units: list[dict], selected_unit_id: Optional[str]) -> None:
    """Seçilen section'ı + altındaki passage'ları göster."""
    if not selected_unit_id:
        st.info("Sol panelden bir section seç.")
        return

    sec = next((u for u in units if u["unit_id"] == selected_unit_id), None)
    if sec is None:
        st.error(f"Section bulunamadı: {selected_unit_id}")
        return

    st.subheader(f"📖 {sec['title'] or '(başlıksız preamble)'}")

    # Üst meta satırı
    cols = st.columns(5)
    cols[0].metric("unit_id", sec["unit_id"])
    cols[1].metric("Kelime", f"{sec['word_count']:,}")
    cols[2].metric("Karakter", f"{sec['char_count']:,}")
    cols[3].metric("Sayfa sayısı", len(sec.get("page_refs", [])))
    cols[4].metric("Kur'ân alıntısı", len(sec.get("quran_quotes", [])))

    # Sayfa aralığı
    pages = sec.get("page_refs", [])
    if pages:
        st.caption(f"Sayfa aralığı: {pages[0]} – {pages[-1]}")

    # Discourse marker özeti
    markers = sec.get("discourse_markers", [])
    if markers:
        from collections import Counter

        c = Counter(m["candidate_label"] for m in markers)
        marker_summary = " · ".join(f"{lbl}: {n}" for lbl, n in sorted(c.items()))
        st.caption(f"🔖 Aday F-etiketi yüzey örüntüleri: {marker_summary}")

    # Tab'lar: Section gövdesi vs Passage'lar
    tab1, tab2 = st.tabs(["Section Gövdesi", "Passage'lar"])

    with tab1:
        body_html = render_arabic_body(sec)
        st.markdown(
            f'<div class="arabic-body">{body_html}</div>',
            unsafe_allow_html=True,
        )

    with tab2:
        passages = [
            u
            for u in units
            if u["tier"] == "passage" and u["parent_unit_id"] == selected_unit_id
        ]
        st.write(f"Bu section altında **{len(passages)}** passage var.")
        for p in passages:
            with st.expander(
                f"{p['unit_id']} · {p['word_count']} kel · "
                f"{len(p.get('quran_quotes', []))} alıntı"
            ):
                p_html = render_arabic_body(p)
                st.markdown(
                    f'<div class="arabic-body">{p_html}</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    st.title("İbn Teymiyye Tutum Haritalama Sistemi · v0.1 demo")
    st.caption(
        "Faz 0 / Hafta 1 · pilot çıktı görselleştiricisi · "
        "F1-F10 etiketleri Hafta 4'te aktif olacak"
    )

    # Veri seçici (sol kenar çubuğu)
    canonical_dir = REPO_ROOT / "data" / "canonical"
    available = find_units_by_path(canonical_dir)
    if not available:
        st.error(
            f"Hiç kanonik JSON bulunamadı: {canonical_dir}\n\n"
            "Önce şu komutu çalıştırın:\n\n"
            "    python -m pipeline.parser \\\n"
            "        --input data/raw/openiti/0728IbnTaymiyya.MajmucFatawa... \\\n"
            "        --work-id MajmucFatawa --volume 7 --page-range V07P005:V07P459 \\\n"
            "        --kitab 'كتاب الإيمان' --output data/canonical/iman_v0.1.json"
        )
        return

    with st.sidebar:
        st.header("Veri kaynağı")
        chosen = st.selectbox(
            "JSON dosyası seç:",
            available,
            format_func=lambda p: p.name,
        )
        units = load_units(chosen)
        st.success(f"{len(units)} birim yüklendi.")

        st.divider()
        # Sol panel içeriği (eser+section)
        selected_unit_id = left_panel(units)

    # Sağ panel
    right_panel(units, selected_unit_id)


if __name__ == "__main__":
    main()
