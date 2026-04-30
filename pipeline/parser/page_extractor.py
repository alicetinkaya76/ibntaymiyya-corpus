"""Sayfa referansı (PageVxxPyyy) çıkarımı.

İki ayrı görev:
1. Logical line akışında PageVxxPyyy işaretlerini bulup ilişkili
   olduğu birim için `page_refs` listesi oluşturmak.
2. Verilen bir cilt-içi sayfa aralığında (örn. V07P005:V07P459) o
   sınırlara denk gelen logical line index'ini bulmak.

Not: PageVxxPyyy normalde sayfa SONUNU işaretler; "Bu satıra kadar
kitap V07P005'te bitiyor" anlamında. Bu yüzden bir birimin sayfa
aralığı = birimden ÖNCE biten son sayfa + 1, ile birim BİTTİĞİNDE
işaretlenen son sayfa.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .tokenizer import LogicalLine

_PAGE_REF_RE = re.compile(r"V(\d{2})P(\d{3,4})")


@dataclass(frozen=True)
class PageRef:
    """Bir sayfa referansının ham hâli."""

    code: str  # "V07P005"
    volume: int
    page: int
    line_no: int  # dosyada hangi satırda gözüktü


def parse_page_code(code: str) -> Optional[tuple[int, int]]:
    """`V07P005` gibi bir kodu (cilt, sayfa) çiftine çevirir."""
    m = _PAGE_REF_RE.match(code)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def find_page_refs(
    logical_lines: list[LogicalLine],
    start_idx: int = 0,
    end_idx: Optional[int] = None,
) -> list[PageRef]:
    """Verilen aralıktaki tüm sayfa referanslarını sırayla çıkarır."""
    if end_idx is None:
        end_idx = len(logical_lines)
    out: list[PageRef] = []
    for i in range(start_idx, end_idx):
        ln = logical_lines[i]
        if ln.kind == "page":
            code = ln.text.strip()
            parsed = parse_page_code(code)
            if parsed is None:
                continue
            v, p = parsed
            out.append(
                PageRef(
                    code=code,
                    volume=v,
                    page=p,
                    line_no=ln.line_no_start,
                )
            )
        else:
            # Inline `PageVxxPxxx` (satır içinde) de yakalayalım
            for m in _PAGE_REF_RE.finditer(ln.text):
                v = int(m.group(1))
                p = int(m.group(2))
                out.append(
                    PageRef(
                        code=f"V{v:02d}P{p:03d}",
                        volume=v,
                        page=p,
                        line_no=ln.line_no_start,
                    )
                )
    return out


def find_logical_line_for_page(
    logical_lines: list[LogicalLine],
    target_volume: int,
    target_page: int,
    search_start: int = 0,
    search_end: Optional[int] = None,
) -> int:
    """Hedef sayfaya işaret eden ilk logical line index'ini bulur.

    Eğer sayfa bulunamazsa -1 döner.
    """
    if search_end is None:
        search_end = len(logical_lines)
    for i in range(search_start, search_end):
        ln = logical_lines[i]
        if ln.kind != "page":
            continue
        parsed = parse_page_code(ln.text.strip())
        if parsed is None:
            continue
        v, p = parsed
        if v == target_volume and p == target_page:
            return i
    return -1


def page_codes_for_range(
    logical_lines: list[LogicalLine],
    start_idx: int,
    end_idx: int,
    expected_volume: Optional[int] = None,
) -> list[str]:
    """Verilen logical line aralığında geçen tüm sayfa kodlarını döner.

    Tekrar yoktur; sıralı, eşsiz liste. `expected_volume` verilirse
    sadece o cilte ait sayfalar alınır (Mecmû'da bazen `inline`
    olarak başka cildin sayfa kodu geçebilir).
    """
    refs = find_page_refs(logical_lines, start_idx, end_idx)
    seen: set[str] = set()
    out: list[str] = []
    for r in refs:
        if expected_volume is not None and r.volume != expected_volume:
            continue
        if r.code in seen:
            continue
        seen.add(r.code)
        out.append(r.code)
    return out


def normalize_page_code(code: str) -> str:
    """`V07P005` → standart 3-haneli sayfa: `V07P005`.

    Bazı OpenITI dump'larında 4 haneli sayfa olur (cilt 1000+ sayfa);
    bunlara dokunulmaz. Validasyon için kullanılır.
    """
    parsed = parse_page_code(code)
    if parsed is None:
        return code
    v, p = parsed
    if p < 1000:
        return f"V{v:02d}P{p:03d}"
    return f"V{v:02d}P{p:04d}"
