"""Section ve passage birim çıkarımı.

Bu modül diğer tüm parser modüllerini birleştirir; bir logical line
aralığı verildiğinde, o aralığa ait `Unit` listesini (section + passage)
inşa eder.

Ana fonksiyon: `extract_units(...)`.

Akış:
1. Logical line aralığı al.
2. `tree_builder.build_tree()` ile düz section listesi al.
3. Her section için:
   a. Section'ın gövdesini text olarak topla (paragraf paragraf, sayfa
      işaretlerini ayırarak).
   b. Manuscript folio işaretlerini metinden çıkar.
   c. Section uzun ise passage'lara böl (~500-700 kelime hedefli).
   d. Her passage/section için Kur'ân alıntılarını ve discourse
      marker'ları çıkar.
   e. Page refs'leri logical line aralığından topla.
   f. `Unit` Pydantic instance'ı oluştur.
4. Section'lar arası ve aynı section içindeki passage'lar arası
   `previous_unit_id` / `next_unit_id` zinciri kur.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .schema import (
    DiscourseMarker,
    EditorMeta,
    ExtractionMeta,
    QuranQuote,
    Unit,
    now_iso_utc,
)
from .tokenizer import LogicalLine, extract_manuscript_markers
from .tree_builder import StructNode
from .page_extractor import find_page_refs
from .quran_extractor import extract_quran_quotes
from .discourse_scanner import scan_discourse_markers
from .id_generator import section_id, passage_id


# Passage hedef boyutu (canonical_schema.md §4.2)
PASSAGE_TARGET_WORDS = 600
PASSAGE_MIN_WORDS = 80
PASSAGE_MAX_WORDS = 1200


# Q&A tespit örüntüleri (Mecmû fıkıh ciltlerinde yoğun, Iman'da seyrek)
_QUESTION_RE = re.compile(r"^(?:و?س[ُ]?ئ[ِ]?ل|سُئل)\b")
_ANSWER_RE = re.compile(r"^(?:فأجاب|أجاب)\b")


@dataclass
class SectionBody:
    """Bir section'ın gövde metni inşa edilmiş hâli."""

    text: str  # birleştirilmiş, normalize Arapça metin
    page_refs: list[str]  # bu section'da geçen sayfalar (sıralı, eşsiz)
    manuscript_markers: list[str]  # ms0001 vb. işaretler
    paragraph_offsets: list[tuple[int, int]]  # text içinde her paragrafın
    # [start, end) sınırları — passage bölmesinde paragraf sınırına saygı
    # için kullanılır
    line_range: tuple[int, int]  # ham dosyadaki [start_line, end_line]


def _build_section_body(
    logical_lines: list[LogicalLine],
    body_start_idx: int,
    body_end_idx: int,
) -> SectionBody:
    """Bir section'ın gövdesini logical line dilinden Arapça metne çevirir.

    Page satırları ATILIR (page_refs'e ayrı kaydedilir).
    Manuscript folio işaretleri çıkarılır (manuscript_markers'a kaydedilir).
    """
    paragraphs: list[str] = []
    paragraph_offsets: list[tuple[int, int]] = []
    page_refs: list[str] = []
    seen_pages: set[str] = set()
    all_markers: list[str] = []

    line_start = -1
    line_end = -1

    cursor = 0  # text içinde nerede olduğumuz
    for i in range(body_start_idx, body_end_idx):
        ln = logical_lines[i]
        if line_start == -1:
            line_start = ln.line_no_start
        line_end = ln.line_no_end

        if ln.kind == "page":
            # PageVxxPyyy satırı; page_refs'e ekle ama text'e ekleme
            code = ln.text.strip()
            if code not in seen_pages:
                seen_pages.add(code)
                page_refs.append(code)
            continue

        if ln.kind in ("blank", "meta", "meta_end", "other"):
            # boş ya da metadata; atla
            continue

        if ln.kind in ("volume", "kitab_cand", "struct"):
            # alt-bir başlık olabilir; gövdeye dahil etme — ama
            # tree_builder düz liste verdiği için bu durumda zaten
            # bu satırlar başka bir section'ın başlangıcı sayılır,
            # yani bu döngünün dışında olmalı. Yine de defansif:
            continue

        # prose veya devamlı satır
        text = ln.text
        # manuscript folio işaretlerini çıkar
        clean, markers = extract_manuscript_markers(text)
        all_markers.extend(markers)
        if not clean:
            continue
        # Inline PageVxxPyyy (satır içinde) varsa bunu da page_refs'e
        # ekle ve metinden çıkar
        for m in re.finditer(r"V\d{2}P\d{3,4}", clean):
            code = m.group(0)
            if code not in seen_pages:
                seen_pages.add(code)
                page_refs.append(code)
        clean = re.sub(r"V\d{2}P\d{3,4}", "", clean).strip()
        if not clean:
            continue
        clean = re.sub(r"\s+", " ", clean)

        para_start = cursor
        if paragraphs:
            # önceki paragrafa boşluk koy
            paragraphs.append(clean)
            cursor += 1 + len(clean)  # " " + clean
            paragraph_offsets.append(
                (para_start + 1, cursor)
            )  # boşluk dahil değil
        else:
            paragraphs.append(clean)
            cursor += len(clean)
            paragraph_offsets.append((para_start, cursor))

    full_text = " ".join(paragraphs)
    # Validasyon: cursor ile len(full_text) eşleşmeli
    # Aslında tek " ".join'de offset'ler birebir; manuel hesap doğru
    # olmayabilir. Yeniden hesaplayalım:
    paragraph_offsets = []
    pos = 0
    for idx, p in enumerate(paragraphs):
        if idx > 0:
            pos += 1  # ayraç boşluk
        paragraph_offsets.append((pos, pos + len(p)))
        pos += len(p)
    assert pos == len(full_text), f"offset hesabı hatalı: {pos} != {len(full_text)}"

    return SectionBody(
        text=full_text,
        page_refs=page_refs,
        manuscript_markers=all_markers,
        paragraph_offsets=paragraph_offsets,
        line_range=(line_start if line_start != -1 else 0,
                    line_end if line_end != -1 else 0),
    )


def _split_into_passages(body: SectionBody) -> list[tuple[int, int]]:
    """Section gövdesini passage'lara böler.

    Returns
    -------
    list[tuple[int, int]]
        Her passage için (start_offset, end_offset) yarı-açık aralık.
    """
    text = body.text
    word_count = len(text.split())
    if word_count <= PASSAGE_TARGET_WORDS + 200:
        # tek passage
        return [(0, len(text))]

    # Birden fazla passage; paragraf sınırlarına saygı duyarak böl
    passages: list[tuple[int, int]] = []
    current_start = 0
    current_words = 0

    for p_start, p_end in body.paragraph_offsets:
        p_text = text[p_start:p_end]
        p_words = len(p_text.split())

        if current_words == 0:
            current_start = p_start
        current_words += p_words

        if current_words >= PASSAGE_TARGET_WORDS:
            # Bu paragrafı dahil ederek bir passage kapat
            passages.append((current_start, p_end))
            current_words = 0

    # Geriye kalan
    if current_words > 0:
        last_para_end = body.paragraph_offsets[-1][1]
        if passages and current_words < PASSAGE_MIN_WORDS:
            # Çok küçük; önceki passage'a ekle
            prev_start, _ = passages[-1]
            passages[-1] = (prev_start, last_para_end)
        else:
            passages.append((current_start, last_para_end))

    return passages


def _classify_unit_type(
    title: Optional[str],
    text: str,
    has_question: bool,
    has_answer: bool,
) -> str:
    """Bir birimin `unit_type`'ını tahmin eder.

    Kaba heuristic; Hafta 2'de zenginleştirilebilir.
    """
    if has_question and has_answer:
        return "question_answer"
    # Mukaddime tespiti
    if title and ("خطبة" in title or "مقدمة" in title or "بسم الله" in text[:50]):
        return "preamble"
    # Reddiye tespiti
    if title:
        for kw in ("الرد على", "نقض", "الجواب على"):
            if kw in title:
                return "refutation"
    # Sonsöz/dua tespiti
    if "والحمد لله رب العالمين" in text[-100:] and len(text) < 500:
        return "colophon"
    return "exposition"


def _detect_qa(text: str) -> tuple[Optional[str], Optional[str]]:
    """Section gövdesinde Q&A var mı tespit eder; varsa soru ve cevap
    metinlerini ayrı döner.

    Bu BASİT bir tespit; karmaşık iç içe Q&A için Hafta 2 gerekir.
    Şu an yalnızca en üstte `سُئل ... فأجاب ...` örüntüsünü arıyoruz.
    """
    # سُئل arıyoruz: ya başta ya kısa boşluk sonrası
    snippet = text[:300]
    if not (re.search(r"\b(?:و?س[ُ]?ئ[ِ]?ل|سُئل)\b", snippet)):
        return None, None
    # فأجاب nerede?
    m = re.search(r"\b(?:فأجاب|أجاب)\b", text)
    if not m:
        return None, None
    q_text = text[: m.start()].strip()
    a_text = text[m.start() :].strip()
    return q_text, a_text


def _build_quran_quotes(text: str) -> list[QuranQuote]:
    """Metinden Kur'ân alıntılarını Pydantic listesine çevirir."""
    extracted = extract_quran_quotes(text)
    out: list[QuranQuote] = []
    for q in extracted:
        # offset'in metinle tutarlı olduğundan emin ol
        s, e = q.char_offset
        if text[s:e] != q.text:
            # whitespace kayması olabilir; düzelt
            # dikkat: schema validatorı sıkı; düzgün ayarlamalıyız
            # Olası kaynak: strip ile offset değişti; içeriği yeniden okuyalım
            # ama offset'i metinde bul.
            idx = text.find(q.text)
            if idx == -1:
                continue
            s = idx
            e = idx + len(q.text)
        out.append(QuranQuote(text=q.text, char_offset=(s, e)))
    return out


def _build_discourse_markers(text: str) -> list[DiscourseMarker]:
    """Metinden discourse marker'ları Pydantic listesine çevirir."""
    hits = scan_discourse_markers(text)
    out: list[DiscourseMarker] = []
    for h in hits:
        out.append(
            DiscourseMarker(
                pattern=h.pattern_text,
                char_offset=h.char_offset,
                candidate_label=h.candidate_label,
                confidence="surface_pattern",
            )
        )
    return out


def extract_units(
    *,
    work_id: str,
    openiti_uri: str,
    logical_lines: list[LogicalLine],
    sections: list[StructNode],
    editor_meta: EditorMeta,
    source_edition_note: str,
    parser_version: str,
    volume: Optional[int] = None,
    kitab_label: Optional[str] = None,
    bab_label: Optional[str] = None,
) -> list[Unit]:
    """Verilen section listesinden tam birim listesi üretir.

    `sections` `tree_builder.build_tree()` çıktısı; her section'ın
    `body_start_idx` ve `body_end_idx`'i logical_lines üzerinde
    geçerli olmalı.

    Returns
    -------
    list[Unit]
        Hem section hem passage tier'larında, sıralı.
    """
    extracted_at = now_iso_utc()

    # Önce sadece "section" kindindeki StructNode'ları al;
    # `volume` ve `kitab` türündekiler section değil, üst-yapı işaretçisi.
    section_nodes = [s for s in sections if s.kind == "section"]
    # Eğer hiç section yoksa, tüm gövdeyi tek bir implicit section yap
    if not section_nodes:
        if logical_lines:
            section_nodes = [
                StructNode(
                    kind="section",
                    title="",  # başlıksız
                    line_no=logical_lines[0].line_no_start,
                    pipes=1,
                    body_start_idx=0,
                    body_end_idx=len(logical_lines),
                )
            ]

    units: list[Unit] = []

    # Section ve passage list'leri ayrı tut, sonra unite et
    section_units: list[Unit] = []
    passage_units: list[Unit] = []

    # Sıralı section_index sayacı; boş gövdeli section atlanırsa
    # sayaç ARTMAZ — böylece numaralama 0,1,2,...,n sıralı kalır.
    s_idx_counter = 0

    for snode in section_nodes:
        body = _build_section_body(
            logical_lines, snode.body_start_idx, snode.body_end_idx
        )
        if not body.text.strip():
            # Boş section; atla, sayaç artmaz
            continue

        s_idx = s_idx_counter
        s_idx_counter += 1

        sec_id = section_id(work_id, s_idx, volume=volume)
        title = snode.title or None
        q_text, a_text = _detect_qa(body.text)
        unit_type = _classify_unit_type(
            title=title,
            text=body.text,
            has_question=q_text is not None,
            has_answer=a_text is not None,
        )

        section_unit = Unit(
            unit_id=sec_id,
            tier="section",
            work_id=work_id,
            openiti_uri=openiti_uri,
            volume=volume,
            kitab=kitab_label,
            bab=bab_label,
            fasl=title,
            unit_type=unit_type,
            title=title,
            question_text=q_text,
            answer_text=a_text,
            full_text_arabic=body.text,
            char_count=len(body.text),
            word_count=len(body.text.split()),
            page_refs=body.page_refs,
            quran_quotes=_build_quran_quotes(body.text),
            hadith_markers=[],
            manuscript_markers=body.manuscript_markers,
            discourse_markers=_build_discourse_markers(body.text),
            f1_to_f10_labels=None,
            topic_labels=None,
            parent_unit_id=None,
            section_index=s_idx,
            passage_index=None,
            previous_unit_id=None,  # section zinciri sonra
            next_unit_id=None,
            editor_meta=editor_meta,
            source_edition_note=source_edition_note,
            is_repeat_or_excerpt_of=None,
            cross_corpus_refs=[],
            extraction_meta=ExtractionMeta(
                parser_version=parser_version,
                extracted_at=extracted_at,
                source_line_range=body.line_range,
            ),
        )
        section_units.append(section_unit)

        # Passage'ları üret
        passage_spans = _split_into_passages(body)
        for p_idx, (p_start, p_end) in enumerate(passage_spans):
            p_text = body.text[p_start:p_end].strip()
            if not p_text:
                continue
            pid = passage_id(work_id, s_idx, p_idx, volume=volume)

            # Passage page_refs'i: section page_refs'inin bir alt kümesi
            # (passage bu offset aralığındaki sayfaları kapsar). Hassasiyet
            # için şimdilik tüm section page_refs'i atıyoruz; passage
            # bazlı sayfa hesabı v0.2'de.
            passage_pages = body.page_refs

            passage_quran = []
            for q in _build_quran_quotes(body.text):
                qs, qe = q.char_offset
                if qs >= p_start and qe <= p_end:
                    # passage offset'ine kaydır
                    passage_quran.append(
                        QuranQuote(
                            text=q.text,
                            char_offset=(qs - p_start, qe - p_start),
                        )
                    )

            passage_disc = []
            for d in _build_discourse_markers(body.text):
                ds, de = d.char_offset
                if ds >= p_start and de <= p_end:
                    passage_disc.append(
                        DiscourseMarker(
                            pattern=d.pattern,
                            char_offset=(ds - p_start, de - p_start),
                            candidate_label=d.candidate_label,
                            confidence=d.confidence,
                        )
                    )

            p_q_text, p_a_text = _detect_qa(p_text)
            p_unit_type = _classify_unit_type(
                title=None,
                text=p_text,
                has_question=p_q_text is not None,
                has_answer=p_a_text is not None,
            )

            passage_unit = Unit(
                unit_id=pid,
                tier="passage",
                work_id=work_id,
                openiti_uri=openiti_uri,
                volume=volume,
                kitab=kitab_label,
                bab=bab_label,
                fasl=title,
                unit_type=p_unit_type,
                title=None,
                question_text=p_q_text,
                answer_text=p_a_text,
                full_text_arabic=p_text,
                char_count=len(p_text),
                word_count=len(p_text.split()),
                page_refs=passage_pages,
                quran_quotes=passage_quran,
                hadith_markers=[],
                manuscript_markers=[],  # section-seviyesinde tutuyoruz
                discourse_markers=passage_disc,
                f1_to_f10_labels=None,
                topic_labels=None,
                parent_unit_id=sec_id,
                section_index=s_idx,
                passage_index=p_idx,
                previous_unit_id=None,
                next_unit_id=None,
                editor_meta=editor_meta,
                source_edition_note=source_edition_note,
                is_repeat_or_excerpt_of=None,
                cross_corpus_refs=[],
                extraction_meta=ExtractionMeta(
                    parser_version=parser_version,
                    extracted_at=extracted_at,
                    source_line_range=body.line_range,
                ),
            )
            passage_units.append(passage_unit)

    # Section zinciri kur
    for i, u in enumerate(section_units):
        prev = section_units[i - 1].unit_id if i > 0 else None
        nxt = section_units[i + 1].unit_id if i < len(section_units) - 1 else None
        # Pydantic immutable değil; setattr ile değiştir
        u_dict = u.model_dump()
        u_dict["previous_unit_id"] = prev
        u_dict["next_unit_id"] = nxt
        section_units[i] = Unit.model_validate(u_dict)

    # Passage zinciri kur (section içinde)
    by_section: dict[int, list[Unit]] = {}
    for u in passage_units:
        by_section.setdefault(u.section_index, []).append(u)
    new_passage_units: list[Unit] = []
    for s_idx, plist in by_section.items():
        plist.sort(key=lambda x: x.passage_index or 0)
        for i, u in enumerate(plist):
            prev = plist[i - 1].unit_id if i > 0 else None
            nxt = plist[i + 1].unit_id if i < len(plist) - 1 else None
            u_dict = u.model_dump()
            u_dict["previous_unit_id"] = prev
            u_dict["next_unit_id"] = nxt
            new_passage_units.append(Unit.model_validate(u_dict))

    # Section'ları ve passage'ları sırayla unite et
    units = []
    for s_idx, sunit in enumerate(section_units):
        units.append(sunit)
        units.extend(
            [u for u in new_passage_units if u.section_index == s_idx]
        )
    return units
