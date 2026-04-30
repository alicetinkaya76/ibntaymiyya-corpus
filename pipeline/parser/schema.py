"""Kanonik veri yapıları.

`docs/methodology/canonical_schema.md` ile tutarlı olmak ZORUNDA.
Doküman ile kod arasında uyumsuzluk olursa kod düzeltilir, doküman
güncellenir (asla tersi değil).

Bu modül parser'ın çıkardığı tüm tipleri Pydantic ile tanımlar.
`Unit` ana sınıftır; section ve passage aynı sınıfı paylaşır,
ayırıcı `tier` alanıdır.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# Validasyon regex'leri (canonical_schema.md §5)
UNIT_ID_RE = re.compile(r"^(MF|IMN|TDM)(-V\d{1,2})?-S\d{2,3}(-P\d{3,4})?$")
PAGE_REF_RE = re.compile(r"^V\d{2}P\d{3,4}$")
F_LABEL_RE = re.compile(r"^F([1-9]|10)$")


class QuranQuote(BaseModel):
    """Birim içindeki bir Kur'ân alıntısı."""

    text: str = Field(..., description="Alıntının orijinal Arapça metni")
    char_offset: tuple[int, int] = Field(
        ..., description="full_text_arabic içinde [start, end] yarı-açık aralık"
    )


class HadithMarker(BaseModel):
    """Hadis alıntı işareti. Hafta 2'de zenginleşecek."""

    text: str
    char_offset: tuple[int, int]
    source_book: Optional[str] = None  # "Bukhari", "Muslim", vb.
    isnad_present: Optional[bool] = None


class DiscourseMarker(BaseModel):
    """F1-F10 yüzey örüntü taraması sonucu."""

    pattern: str = Field(..., description="Eşleşen orijinal Arapça örüntü")
    char_offset: tuple[int, int]
    candidate_label: str = Field(..., description="F1..F10")
    confidence: Literal["surface_pattern", "llm_zero_shot", "human_gold"] = (
        "surface_pattern"
    )

    @field_validator("candidate_label")
    @classmethod
    def _validate_label(cls, v: str) -> str:
        if not F_LABEL_RE.match(v):
            raise ValueError(f"candidate_label F1..F10 olmalı, alındı: {v}")
        return v


class EditorMeta(BaseModel):
    """Baskının editöryel metadata'sı."""

    editor_name: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[str] = None
    notation_style: Literal[
        "double_quotes", "square_brackets", "qosa_curly", "unknown"
    ] = "unknown"


class ExtractionMeta(BaseModel):
    """Birimin nasıl çıkarıldığının izlenebilirlik kaydı."""

    parser_version: str
    extracted_at: str  # ISO 8601 UTC
    source_line_range: tuple[int, int] = Field(
        ..., description="Ham OpenITI dosyasındaki [start_line, end_line], 1-tabanlı"
    )


class FutureLinks(BaseModel):
    """Diğer projelere ileride eklenecek bağlantılar için yer."""

    tabakat_io: Optional[str] = None
    islamicatlas: Optional[str] = None
    halka_book_ref: Optional[str] = None


class TopicLabels(BaseModel):
    """Üç seviyeli taksonomi etiketleri (Faz 2'de doldurulur)."""

    top: Optional[str] = None
    mid: Optional[str] = None
    leaf: Optional[str] = None


class Unit(BaseModel):
    """Kanonik birim — section veya passage.

    Aynı sınıf her iki seviye için kullanılır; ayırıcı `tier` alanıdır.
    """

    # 2.1 · Kimlik ve köken
    unit_id: str
    tier: Literal["section", "passage"]
    work_id: str
    openiti_uri: str
    volume: Optional[int] = None
    kitab: Optional[str] = None
    bab: Optional[str] = None
    fasl: Optional[str] = None
    unit_type: Literal[
        "question_answer", "exposition", "refutation", "preamble", "colophon"
    ]

    # 2.2 · İçerik
    title: Optional[str] = None
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    full_text_arabic: str
    char_count: int
    word_count: int

    # 2.3 · Sayfa, alıntı, referans
    page_refs: list[str] = Field(default_factory=list)
    quran_quotes: list[QuranQuote] = Field(default_factory=list)
    hadith_markers: list[HadithMarker] = Field(default_factory=list)
    manuscript_markers: list[str] = Field(default_factory=list)

    # 2.4 · Söylem-yüzey örüntüleri
    discourse_markers: list[DiscourseMarker] = Field(default_factory=list)

    # 2.5 · Etiket katmanları (Hafta 2-4'te dolar)
    f1_to_f10_labels: Optional[list[str]] = None
    topic_labels: Optional[TopicLabels] = None

    # 2.6 · Hiyerarşi ve navigasyon
    parent_unit_id: Optional[str] = None
    section_index: int
    passage_index: Optional[int] = None
    previous_unit_id: Optional[str] = None
    next_unit_id: Optional[str] = None

    # 2.7 · Editör ve baskı bilgisi
    editor_meta: EditorMeta
    source_edition_note: str

    # 2.8 · Cross-corpus ve izlenebilirlik
    is_repeat_or_excerpt_of: Optional[str] = None
    cross_corpus_refs: list[str] = Field(default_factory=list)
    extraction_meta: ExtractionMeta

    # 2.9 · Gelecek bağlantıları
    future_links: FutureLinks = Field(default_factory=FutureLinks)

    # ---- Validatörler (canonical_schema.md §5 invariantları) ----

    @field_validator("unit_id")
    @classmethod
    def _validate_unit_id(cls, v: str) -> str:
        if not UNIT_ID_RE.match(v):
            raise ValueError(f"unit_id formatına uymuyor: {v}")
        return v

    @field_validator("page_refs")
    @classmethod
    def _validate_page_refs(cls, v: list[str]) -> list[str]:
        for ref in v:
            if not PAGE_REF_RE.match(ref):
                raise ValueError(f"page_ref formatına uymuyor: {ref}")
        return v

    @model_validator(mode="after")
    def _validate_consistency(self) -> "Unit":
        # Invariant 3: char_count == len(full_text_arabic)
        if self.char_count != len(self.full_text_arabic):
            raise ValueError(
                f"char_count={self.char_count} ile len(full_text_arabic)="
                f"{len(self.full_text_arabic)} eşleşmiyor"
            )
        # Invariant 4: word_count == len(full_text_arabic.split())
        actual_word_count = len(self.full_text_arabic.split())
        if self.word_count != actual_word_count:
            raise ValueError(
                f"word_count={self.word_count} ile gerçek={actual_word_count} eşleşmiyor"
            )
        # Invariant 2: passage'ın parent_unit_id'si zorunlu
        if self.tier == "passage" and self.parent_unit_id is None:
            raise ValueError("passage tier'ında parent_unit_id zorunlu")
        if self.tier == "section" and self.parent_unit_id is not None:
            raise ValueError(
                f"section tier'ında parent_unit_id None olmalı, alındı: "
                f"{self.parent_unit_id}"
            )
        # Invariant 5: Kur'ân alıntı offset'leri tutarlı
        for q in self.quran_quotes:
            s, e = q.char_offset
            slice_text = self.full_text_arabic[s:e]
            if slice_text != q.text:
                # whitespace toleransı yok — ama bu birim canonical olduğu için
                # zaten normalize edilmiş, sıkı olmamız gerek
                raise ValueError(
                    f"Kur'ân alıntı offset {q.char_offset} ile metin eşleşmiyor.\n"
                    f"  Beklenen: {q.text!r}\n"
                    f"  Bulunan:  {slice_text!r}"
                )
        return self


def now_iso_utc() -> str:
    """Mevcut anı ISO 8601 UTC formatında döner."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
