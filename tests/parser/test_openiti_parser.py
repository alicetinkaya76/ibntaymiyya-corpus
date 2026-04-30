"""OpenITI parser test paketi.

7 test:
1. Metadata header parsing
2. Paragraf birleştirme (~~ devam işareti)
3. Tedmuriyye section hiyerarşisi
4. Mecmû cilt aralığı izolasyonu
5. Kitâb başlığı false-positive elenmesi
6. Sayfa kodu çıkarımı (Page öneki sıyrılır)
7. Kur'ân alıntı çıkarımı (iki stil)

Çalıştırma:
    cd ibntaymiyya/
    python -m pytest tests/parser/
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.parser.tokenizer import (
    read_raw_lines,
    merge_continuations,
    extract_manuscript_markers,
)
from pipeline.parser.header_parser import MetadataHeader, detect_notation_style
from pipeline.parser.tree_builder import (
    build_tree,
    extract_volume_range,
    _is_real_kitab_header,
)
from pipeline.parser.page_extractor import (
    parse_page_code,
    find_logical_line_for_page,
)
from pipeline.parser.quran_extractor import extract_quran_quotes
from pipeline.parser.id_generator import section_id, passage_id
from pipeline.parser import parse_file


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures"
RAW_DIR = REPO_ROOT / "data" / "raw" / "openiti"

MINI = FIXTURES / "mini_sample.txt"
TEDMURIYYE = RAW_DIR / "0728IbnTaymiyya.RisalaTadmuriyya.Shamela0022666-ara1"
IMAN_STD = RAW_DIR / "0728IbnTaymiyya.Iman.Shamela0007564-ara1"
MECMU = RAW_DIR / "0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1"


# ---------------------------------------------------------------------------
# Test 1 · Metadata header parsing
# ---------------------------------------------------------------------------


def test_metadata_header_parsing():
    """Tedmuriyye metadata bloğunun anahtar alanları doğru çıkarılmalı."""
    raw = read_raw_lines(TEDMURIYYE)
    header = MetadataHeader.from_raw_lines(raw)

    # Yazar İbn Teymiyye, vefatı 728h
    assert header.author_died_hijri == 728
    assert header.author_name and "ابن تيمية" in header.author_name
    # Kitap başlığı Risale Tedmuriyye'ye işaret etmeli
    assert header.book_title is not None
    # Header sonu BODY'den önce olmalı
    assert header.end_line_no > 0
    # Bilinen sentinel'ler atlanmalı (NODATA vb. raw_kv'de yer almamalı)
    assert "NODATA" not in header.raw_kv.values()


# ---------------------------------------------------------------------------
# Test 2 · Paragraf birleştirme (~~ continuation)
# ---------------------------------------------------------------------------


def test_paragraph_continuation_merging():
    """`~~` devam satırları, önceki paragrafa boşlukla birleşmeli."""
    raw = read_raw_lines(MINI)
    logical = merge_continuations(raw)

    # mini_sample.txt'de "هذا متن الباب الأول.\n~~وهذا تتمة..." iki fiziksel
    # satır var; tek mantıksal satıra birleşmeli
    found = False
    for ln in logical:
        if "متن الباب الأول" in ln.text:
            assert "تتمة الفقرة" in ln.text, (
                f"~~ devamı birleşmedi: {ln.text!r}"
            )
            assert ln.line_no_start != ln.line_no_end, (
                "Birleşmiş satırın range'i tek satır olmamalı"
            )
            found = True
            break
    assert found, "Beklenen prose satırı bulunamadı"


def test_manuscript_marker_extraction():
    """ms1234 gibi folio işaretleri metinden çıkarılıp listeye taşınmalı."""
    text = "هذا نص فيه ms1234 ثم ms5678 إشارة"
    clean, markers = extract_manuscript_markers(text)
    assert markers == ["ms1234", "ms5678"]
    assert "ms1234" not in clean and "ms5678" not in clean
    assert "هذا نص فيه" in clean and "إشارة" in clean


# ---------------------------------------------------------------------------
# Test 3 · Tedmuriyye section hiyerarşisi
# ---------------------------------------------------------------------------


def test_tedmuriyye_section_hierarchy():
    """Tedmuriyye en az 100 section üretmeli ve ilki khutba olmalı."""
    units = parse_file(TEDMURIYYE, work_id="RisalaTadmuriyya")
    sections = [u for u in units if u.tier == "section"]
    assert len(sections) >= 100, f"Tedmuriyye section sayısı düşük: {len(sections)}"
    # İlk birkaç section'ın başlığı al-Sa'awi'nin meşhur fihrist başlıklarına
    # uygun olmalı
    titles = [s.title or "" for s in sections[:5]]
    has_khutba = any("خطبة" in t or "موضوع" in t for t in titles)
    assert has_khutba, f"İlk 5 başlıkta khutba/mevzu beklenirdi: {titles}"


# ---------------------------------------------------------------------------
# Test 4 · Mecmû cilt aralığı izolasyonu
# ---------------------------------------------------------------------------


def test_mecmu_volume_range_extraction():
    """Cilt 7'nin logical aralığı, dosyanın yaklaşık ortasına denk gelmeli."""
    raw = read_raw_lines(MECMU)
    logical = merge_continuations(raw)
    start, end = extract_volume_range(logical, 7)
    # Cilt 7 mantıklı bir aralıkta olmalı
    assert 0 < start < end < len(logical)
    # Cilt 7'nin başlangıcında volume başlığı olmalı
    vol_line = logical[start]
    assert vol_line.kind == "volume"
    assert "السابع" in vol_line.text


def test_mecmu_volume_does_not_match_substring():
    """`الثاني` (cilt 2) `الثاني عشر` (cilt 12) ile karıştırılmamalı."""
    raw = read_raw_lines(MECMU)
    logical = merge_continuations(raw)
    start_2, end_2 = extract_volume_range(logical, 2)
    start_12, end_12 = extract_volume_range(logical, 12)
    # İki aralık çakışmamalı
    assert end_2 <= start_12, (
        f"Cilt 2 [{start_2},{end_2}) ile Cilt 12 [{start_12},{end_12}) çakıştı"
    )


# ---------------------------------------------------------------------------
# Test 5 · Kitâb başlığı false-positive elemesi
# ---------------------------------------------------------------------------


def test_kitab_header_false_positive_filter():
    """`# كتاب الله مخالف...` gibi cümleler kitâb başlığı sayılmamalı."""
    # Gerçek başlık
    assert _is_real_kitab_header("كتاب الإيمان")
    assert _is_real_kitab_header("كتاب توحيد الألوهية")
    # False-positive: cümle başlangıcı
    assert not _is_real_kitab_header(
        "كتاب الله مخالف لسنة رسوله صلى الله عليه وسلم في زعم هؤلاء"
    )
    assert not _is_real_kitab_header("كتاب الله المنزل وسنة رسوله")
    # Çok uzun cümle
    assert not _is_real_kitab_header(
        "كتاب " + ("الإيمان " * 30)  # 30 kez tekrar = çok uzun
    )


# ---------------------------------------------------------------------------
# Test 6 · Sayfa kodu çıkarımı (Page öneki sıyrılır)
# ---------------------------------------------------------------------------


def test_page_code_strips_page_prefix():
    """`# PageV07P005` parse edildiğinde kanonik kod `V07P005` olmalı."""
    raw = read_raw_lines(MINI)
    logical = merge_continuations(raw)
    page_lines = [ln for ln in logical if ln.kind == "page"]
    assert len(page_lines) >= 1
    for ln in page_lines:
        # text "Page" öneki içermemeli
        assert not ln.text.startswith("Page"), (
            f"Page öneki sıyrılmamış: {ln.text!r}"
        )
        # Kanonik forma uymalı
        parsed = parse_page_code(ln.text.strip())
        assert parsed is not None, f"Sayfa kodu parse edilemedi: {ln.text!r}"


def test_find_logical_line_for_page():
    """V07P005'in logical line index'i bulunmalı."""
    raw = read_raw_lines(MECMU)
    logical = merge_continuations(raw)
    idx = find_logical_line_for_page(logical, 7, 5)
    assert idx >= 0
    assert logical[idx].kind == "page"
    parsed = parse_page_code(logical[idx].text.strip())
    assert parsed == (7, 5)


# ---------------------------------------------------------------------------
# Test 7 · Kur'ân alıntı çıkarımı
# ---------------------------------------------------------------------------


def test_quran_quote_curly_style():
    """`{...}` süslü parantez içi alıntılar yakalanmalı."""
    text = "قال {الحمد لله رب العالمين} وانتهى الكلام"
    quotes = extract_quran_quotes(text)
    assert len(quotes) == 1
    q = quotes[0]
    assert q.text == "الحمد لله رب العالمين"
    s, e = q.char_offset
    assert text[s:e] == q.text
    assert q.style == "curly"


def test_quran_quote_qb_qe_style():
    """`@QB@..@QE@` stilindeki alıntılar yakalanmalı."""
    text = "@QB@ يا أيها الذين آمنوا @QE@ ثم استمر"
    quotes = extract_quran_quotes(text)
    assert len(quotes) == 1
    assert quotes[0].text == "يا أيها الذين آمنوا"
    assert quotes[0].style == "qb_qe"


def test_quran_quote_no_double_count():
    """`@QB@..@QE@` ve `{...}` çakışırsa sadece `qb_qe` sayılmalı."""
    # Gerçek dosyalarda nadir ama mümkün
    text = "@QB@ {الحمد لله} @QE@ devam"
    quotes = extract_quran_quotes(text)
    # qb_qe + curly aynı yerde olduğunda sadece qb_qe kalmalı
    assert len(quotes) == 1
    assert quotes[0].style == "qb_qe"


# ---------------------------------------------------------------------------
# Bonus testler · ID üretici ve schema invariantları
# ---------------------------------------------------------------------------


def test_id_generator_format():
    assert section_id("MajmucFatawa", 3, volume=7) == "MF-V07-S03"
    assert passage_id("MajmucFatawa", 3, 12, volume=7) == "MF-V07-S03-P012"
    assert section_id("RisalaTadmuriyya", 5) == "TDM-S05"
    assert passage_id("Iman", 0, 4) == "IMN-S00-P004"


def test_id_generator_unknown_work_raises():
    with pytest.raises(ValueError):
        section_id("UnknownWork", 0)


def test_notation_style_detection():
    """Editör adına göre notasyon stili tespit edilmeli."""
    # Albani edisyonu — square_brackets
    h = MetadataHeader()
    h.editor_name = "محمد ناصر الدين الألباني"
    assert detect_notation_style(h, "") == "square_brackets"
    # İbn Kāsım — double_quotes
    h.editor_name = "عبد الرحمن بن محمد بن قاسم"
    assert detect_notation_style(h, "") == "double_quotes"
    # Bilinmeyen + örnek metinde işaret yok
    h.editor_name = "محقق غير معروف"
    assert detect_notation_style(h, "نص عادي") == "unknown"


def test_pilot_iman_kabir_coverage():
    """Pilot çıktının V07P005-V07P459 sayfa kapsamı tam olmalı."""
    units = parse_file(
        MECMU,
        work_id="MajmucFatawa",
        volume=7,
        page_range=("V07P005", "V07P459"),
        kitab_label="كتاب الإيمان",
    )
    assert len(units) > 100, f"Pilot için en az 100 birim bekleniyordu: {len(units)}"
    # Sayfa kapsama
    all_pages: set[str] = set()
    for u in units:
        for p in u.page_refs:
            all_pages.add(p)
    v07_pages = sorted(p for p in all_pages if p.startswith("V07P"))
    assert v07_pages[0] == "V07P005", f"İlk sayfa V07P005 olmalıydı: {v07_pages[0]}"
    # En az 400 sayfa kapsanmalı (V07P5-459 arası ~455 sayfa)
    assert len(v07_pages) >= 400, f"Sayfa kapsama düşük: {len(v07_pages)}"


def test_pilot_unit_id_format_validation():
    """Tüm birimlerin unit_id'si kanonik regex'e uymalı."""
    import re

    units = parse_file(
        MECMU,
        work_id="MajmucFatawa",
        volume=7,
        page_range=("V07P005", "V07P459"),
        kitab_label="كتاب الإيمان",
    )
    pat = re.compile(r"^MF-V07-S\d{2,3}(-P\d{3,4})?$")
    for u in units:
        assert pat.match(u.unit_id), f"unit_id formata uymuyor: {u.unit_id}"
