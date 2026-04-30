"""OpenITI mARkdown tokenizer.

Sorumluluklar:
- Ham dosyayı satır satır okumak (1-tabanlı satır numaralarını
  korumak için).
- `~~` paragraf devam işaretlerini bir önceki satıra birleştirmek.
- `# ` satır başı paragraf işaretlerini ayırt etmek (içerik mi yoksa
  PageVxxPyyy / kitâb başlığı / cilt başlığı mı).

Önemli OpenITI mARkdown gözlemi (üç İbn Teymiyye dosyasında doğrulandı):
- `# PageVxxPyyy` BAĞIMSIZ SATIR olarak çıkıyor (mARkdown spec'i bunu
  inline da desteklese de, Şâmile dump'larında satır başı standart).
- `# الجزء ...` cilt başlığı, `# كتاب ...` kitâb başlığı — Mecmû'da
  yapısal sınırlar bunlar (resmi mARkdown spec'inde olmasa bile).
- `~~` ile başlayan satırlar bir önceki içeriğin paragraf devamıdır.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


# Regex'ler; modül seviyesinde compile (performans)
# `# PageV07P005` → kanonik formatta `V07P005` (Page öneki sıyrılır).
_PAGE_LINE_RE = re.compile(r"^# Page(V\d{2}P\d{3,4})\s*$")
_VOLUME_HEADER_RE = re.compile(r"^# الجزء (.+?)\s*$")
_KITAB_HEADER_RE = re.compile(r"^# (كتاب\s+.+?)\s*$")
_STRUCT_HEADER_RE = re.compile(r"^### (\|+)\s*(.*?)\s*$")
_CONT_LINE_RE = re.compile(r"^~~(.*)$")
_PROSE_LINE_RE = re.compile(r"^# (.+)$")
_MS_FOLIO_RE = re.compile(r"\bms\d{3,4}\b")  # ms0001, ms1901 vb.

# Mecmû'da false-positive: "# كتاب الله ..." cümle başlangıçları kitâb başlığı değil.
# Heuristic: gerçek kitâb başlığı çok kısa (< 50 karakter) ve hemen ardından
# konu içeriği gelir. unit_extractor false-positive filtresini uygular;
# burada sadece adayı işaretliyoruz.


@dataclass(frozen=True)
class RawLine:
    """Ham dosyadan tek bir mantıksal satır."""

    line_no: int  # 1-tabanlı orijinal satır numarası
    raw: str  # orijinal hâli, sondaki \n çıkarılmış
    kind: str  # bkz. tokenize() docstring


@dataclass(frozen=True)
class LogicalLine:
    """Paragraf birleştirme sonrası mantıksal satır.

    `~~` ile devam eden fiziksel satırlar tek mantıksal satıra
    birleştirilir. `source_line_range` orijinal dosyadaki [start, end]
    kapsayıcı satır aralığını verir.
    """

    line_no_start: int
    line_no_end: int
    text: str  # birleştirilmiş içerik (ön ekler çıkarılmış)
    kind: str
    raw_first: str  # ilk fiziksel satırın ham hâli (debug için)


def _classify(raw: str) -> str:
    """Bir ham satırın tipini sınıflandırır.

    Olası tipler:
    - `meta`         : `#META# ...` veya `######OpenITI#`
    - `meta_end`     : `#META#Header#End#`
    - `page`         : `# PageVxxPyyy`
    - `volume`       : `# الجزء ...`
    - `kitab_cand`   : `# كتاب ...` (false-positive olabilir)
    - `struct`       : `### |` veya `### ||` veya `### |||`
    - `cont`         : `~~...` paragraf devamı
    - `prose`        : `# ...` (yukarıdakiler dışında)
    - `blank`        : boş satır
    - `other`        : başka bir şey (ham veri ihlali)
    """
    s = raw.rstrip("\n").rstrip("\r")
    if s == "":
        return "blank"
    if s.startswith("######"):
        return "meta"
    if s == "#META#Header#End#":
        return "meta_end"
    if s.startswith("#META#"):
        return "meta"
    if _PAGE_LINE_RE.match(s):
        return "page"
    if _VOLUME_HEADER_RE.match(s):
        return "volume"
    if _KITAB_HEADER_RE.match(s):
        return "kitab_cand"
    if _STRUCT_HEADER_RE.match(s):
        return "struct"
    if _CONT_LINE_RE.match(s):
        return "cont"
    if _PROSE_LINE_RE.match(s):
        return "prose"
    return "other"


def read_raw_lines(path: Path | str) -> list[RawLine]:
    """Ham dosyayı satır satır okur, her satıra tip atar.

    1-tabanlı satır numarasını korur. Bu numaralar
    `source_line_range` izlenebilirlik kayıtlarında kullanılır.
    """
    p = Path(path)
    lines: list[RawLine] = []
    with p.open("r", encoding="utf-8", errors="strict") as f:
        for i, raw in enumerate(f, start=1):
            s = raw.rstrip("\n").rstrip("\r")
            kind = _classify(s)
            lines.append(RawLine(line_no=i, raw=s, kind=kind))
    return lines


def merge_continuations(lines: list[RawLine]) -> list[LogicalLine]:
    """`~~` paragraf devamlarını önceki satıra birleştirir.

    Bir paragraf şöyle başlar: `# Bu uzun cümle...` ve sonra ardışık
    olarak `~~devamı...` `~~daha devamı...` gelirse bunlar tek mantıksal
    satıra birleştirilir.

    `~~` lar arasındaki boşluklar tek bir boşluğa indirilir; baştaki
    `# ` veya `~~` işaretçileri çıkarılır; ham metin korunur.
    """
    result: list[LogicalLine] = []
    i = 0
    n = len(lines)
    while i < n:
        cur = lines[i]
        if cur.kind == "cont":
            # `~~` ile başlayan satır ama öncesinde uygun bir şey yoksa
            # bunu kendi başına bir prose satırı gibi alalım (ham veri
            # bozuk olabilir).
            text = _CONT_LINE_RE.match(cur.raw).group(1).strip()
            result.append(
                LogicalLine(
                    line_no_start=cur.line_no,
                    line_no_end=cur.line_no,
                    text=text,
                    kind="prose",  # tek başına prose gibi davran
                    raw_first=cur.raw,
                )
            )
            i += 1
            continue

        if cur.kind in ("prose", "kitab_cand", "volume", "struct", "page"):
            # Olası birleşim aday başlangıç. `~~` devamlarını topla.
            start_no = cur.line_no
            end_no = cur.line_no
            # İlgili tipe göre içeriği çıkar
            if cur.kind == "prose":
                content = _PROSE_LINE_RE.match(cur.raw).group(1)
            elif cur.kind == "kitab_cand":
                content = _KITAB_HEADER_RE.match(cur.raw).group(1)
            elif cur.kind == "volume":
                content = _VOLUME_HEADER_RE.match(cur.raw).group(1)
            elif cur.kind == "struct":
                m = _STRUCT_HEADER_RE.match(cur.raw)
                pipes = m.group(1)
                title = m.group(2)
                content = f"{pipes} {title}"  # geçici saklayıcı, tree_builder
                # bunu yeniden parse edecek
            else:  # page
                content = _PAGE_LINE_RE.match(cur.raw).group(1)

            # `~~` devamlarını ekle
            j = i + 1
            chunks = [content.strip()]
            while j < n and lines[j].kind == "cont":
                cont_text = _CONT_LINE_RE.match(lines[j].raw).group(1).strip()
                chunks.append(cont_text)
                end_no = lines[j].line_no
                j += 1

            merged_text = " ".join(c for c in chunks if c)
            # birden fazla ardışık boşluk → tek
            merged_text = re.sub(r"\s+", " ", merged_text).strip()

            result.append(
                LogicalLine(
                    line_no_start=start_no,
                    line_no_end=end_no,
                    text=merged_text,
                    kind=cur.kind,
                    raw_first=cur.raw,
                )
            )
            i = j
            continue

        # meta, meta_end, blank, other
        result.append(
            LogicalLine(
                line_no_start=cur.line_no,
                line_no_end=cur.line_no,
                text=cur.raw,
                kind=cur.kind,
                raw_first=cur.raw,
            )
        )
        i += 1

    return result


def extract_manuscript_markers(text: str) -> tuple[str, list[str]]:
    """Metinden manuscript folio işaretlerini (ms0001, ms1901 vb.) çıkarır.

    Returns
    -------
    (clean_text, markers)
        clean_text: işaretler çıkarılmış metin
        markers: bulunan işaretlerin listesi (sıra ve tekrarla birlikte)
    """
    markers = _MS_FOLIO_RE.findall(text)
    clean = _MS_FOLIO_RE.sub("", text)
    # işaret çıkarıldıktan sonra çift boşluk kalabilir
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean, markers


def iter_logical_lines(path: Path | str) -> Iterator[LogicalLine]:
    """Bir dosyayı okuyup birleştirilmiş mantıksal satırlarını verir."""
    raw_lines = read_raw_lines(path)
    yield from merge_continuations(raw_lines)
