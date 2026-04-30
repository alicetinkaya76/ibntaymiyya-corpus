"""OpenITI metadata header parser.

Bir OpenITI dosyasının başında `######OpenITI#` ile açılan ve
`#META#Header#End#` ile kapanan metadata bloğu vardır. Bu blok
TAB-ayrılmış `#META# <key>\\t:: <value>` satırlarından oluşur.

Bu modül o bloğu structural olarak parse edip kanonik
`MetadataHeader` yapısı verir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .tokenizer import RawLine

# `#META# <key>\t:: <value>` veya bazen tek boşlukla
_META_LINE_RE = re.compile(r"^#META#\s+([^\t]+?)\s*::\s*(.*)$")


@dataclass
class MetadataHeader:
    """OpenITI metadata bloğunun yapılandırılmış hâli."""

    raw_kv: dict[str, str] = field(default_factory=dict)

    # Sık kullanılan alanlar (raw_kv'de de saklanır)
    author_name: Optional[str] = None
    author_died_hijri: Optional[int] = None
    book_title: Optional[str] = None
    book_subject: Optional[str] = None
    library_uri: Optional[str] = None  # örn. Shamela_0007289
    editor_name: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[str] = None  # ham string, "1416/1995م" gibi
    volume_count: Optional[str] = None

    # Header'ın bittiği satır numarası (1-tabanlı)
    end_line_no: int = 0

    @classmethod
    def from_raw_lines(cls, lines: list[RawLine]) -> "MetadataHeader":
        """Ham satır listesinden header'ı parse eder.

        `meta` ve `meta_end` tipli satırları işler; `meta_end` görüldüğünde
        durur ve o satırın numarasını `end_line_no` olarak kaydeder.
        """
        h = cls()
        for ln in lines:
            if ln.kind == "meta_end":
                h.end_line_no = ln.line_no
                break
            if ln.kind != "meta":
                # blank ya da başka bir satır olabilir; meta bölgesi içinde
                # sadece meta + blank tipleri görmek normaldir
                continue
            m = _META_LINE_RE.match(ln.raw)
            if not m:
                continue
            key = m.group(1).strip()
            val = m.group(2).strip()
            if val == "NODATA" or val == "NOTGIVEN" or val == "NOCODE":
                # OpenITI bilinmeyen değer için bu sentinel'leri kullanır
                continue
            h.raw_kv[key] = val

        # Sık kullanılan alanları doldur
        h.author_name = h.raw_kv.get("010.AuthorNAME")
        died = h.raw_kv.get("011.AuthorDIED")
        if died and died.isdigit():
            h.author_died_hijri = int(died)
        h.book_title = h.raw_kv.get("020.BookTITLE")
        h.book_subject = h.raw_kv.get("021.BookSUBJ")
        h.library_uri = h.raw_kv.get("030.LibURI")
        h.editor_name = h.raw_kv.get("040.EdEDITOR")
        h.publisher = h.raw_kv.get("043.EdPUBLISHER")
        # Yayın yılı bazen 045.EdYEAR'da, bazen 041.EdNUMBER'da geçer
        h.publication_year = h.raw_kv.get("045.EdYEAR") or h.raw_kv.get(
            "041.EdNUMBER"
        )
        h.volume_count = h.raw_kv.get("022.BookVOLS")
        return h


def detect_notation_style(
    header: MetadataHeader, sample_text: str
) -> str:
    """Editör notasyon stilini tespit eder.

    `sample_text` parametresi gövde metninden bir örnek (~1000 karakter)
    olabilir; karar editöre + örüntüye göre verilir:

    - Albani edisyonu → square_brackets (`[الإيمان]`)
    - İbn Kāsım derlemesi → double_quotes (`" الإيمان "`)
    - al-Sa'awi (Tedmuriyye) → qosa_curly (zengin başlık + farklı stil)

    Editör tanınmıyorsa ve örnekte de net işaret yoksa: `unknown`.
    """
    name = (header.editor_name or "").strip()
    if "الألباني" in name or "الالباني" in name:
        return "square_brackets"
    if "ابن قاسم" in name or "بن قاسم" in name:
        return "double_quotes"
    if "السعوي" in name:
        return "qosa_curly"
    # Heuristic: örnekte hangi tırnaklama daha sık?
    n_brackets = sample_text.count("[الإيمان]") + sample_text.count(
        "[الإسلام]"
    )
    n_quotes = sample_text.count('" الإيمان "') + sample_text.count(
        '" الإسلام "'
    )
    if n_brackets > n_quotes and n_brackets >= 2:
        return "square_brackets"
    if n_quotes > n_brackets and n_quotes >= 2:
        return "double_quotes"
    return "unknown"
