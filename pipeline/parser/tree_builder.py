"""Hiyerarşik yapı çıkarımı.

OpenITI mARkdown spec'inde:
- `### |`   : en üst seviye (cilt/kitâb)
- `### ||`  : ikinci seviye (bâb/kāide)
- `### |||` : üçüncü seviye (fasıl)
- `### ||||`: dördüncü seviye (soru)
- `### |||||`: beşinci seviye (cevap)

ÖNEMLİ AMPİRİK BULGU (30 Nis 2026 sondajı):
İbn Teymiyye Mecmû dump'ında `### |` çoklu seviyede kullanılmış —
spec ihlali ya da dump anomalisi. Onun yerine GERÇEK hiyerarşi:

    `# الجزء ...`        → cilt sınırı (line-level header)
    `# كتاب ...`         → kitâb sınırı (line-level header)
    `### | ...`          → fasıl/section sınırı (mARkdown header)

Bu modül bu hibrit hiyerarşiyi inşa eder. False-positive
`# كتاب الله/كتاب الله مخالف...` cümlelerini ELER.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .tokenizer import LogicalLine


# False-positive filtre eşikleri
KITAB_HEADER_MAX_CHARS = 80  # gerçek kitâb başlığı kısa
KITAB_FALSE_POSITIVE_OPENERS = (
    "كتاب الله",  # "Allah'ın Kitabı"
    "كتاب اللَّه",
)


@dataclass
class StructNode:
    """Hiyerarşi ağacındaki bir düğüm.

    `kind`:
        - `volume`: cilt başlığı
        - `kitab` : kitâb başlığı
        - `section`: `### |` fasıl başlığı (veya implicit "preamble" section)
    """

    kind: str
    title: str  # başlık metni (Arapça)
    line_no: int  # 1-tabanlı dosya satırı
    pipes: int = 1  # struct'ta `|` sayısı, diğerlerinde 1
    parent: Optional["StructNode"] = None
    children: list["StructNode"] = field(default_factory=list)
    body_start_idx: int = -1  # logical line index nerede gövde başlıyor
    body_end_idx: int = -1  # gövde nerede bitiyor (exclusive)

    def __repr__(self) -> str:
        return f"StructNode({self.kind}: {self.title[:40]}... @line={self.line_no})"


def _is_real_kitab_header(text: str) -> bool:
    """`# كتاب ...` adayının gerçek kitâb başlığı olup olmadığını kestirir.

    Gerçek başlık: kısa, kalıplaşmış yapı (örn. `كتاب الإيمان`,
    `كتاب توحيد الألوهية`).

    False-positive: cümle başlangıcı (örn. `كتاب الله مخالف لسنة رسوله`).
    """
    if len(text) > KITAB_HEADER_MAX_CHARS:
        return False
    for fp in KITAB_FALSE_POSITIVE_OPENERS:
        if text.startswith(fp):
            return False
    return True


def build_tree(
    logical_lines: list[LogicalLine],
    body_start_idx: int = 0,
) -> list[StructNode]:
    """Mantıksal satırlardan düz section listesi inşa eder.

    Bu hafta hiyerarşik (nested) ağaç değil, **düz section listesi**
    döner. Her section bir `volume`, `kitab` veya `### |` başlığıyla
    açılır; bir sonraki struct/volume/kitab başlığına kadar süren
    gövdeyi kapsar.

    `body_start_idx`: ham metadata header bittikten sonraki ilk
    logical line index (0-tabanlı). Ondan önce tarama yapılmaz.

    KRİTİK: `body_start_idx` ile ilk struct/volume/kitab başlığı
    arasındaki gövde **implicit "preamble" section** olarak eklenir.
    Bu sayede başlıksız mukaddimeler (örn. Iman el-Kebîr'in V07P5-77
    arası 73 sayfası) kaybolmaz.

    Returns
    -------
    list[StructNode]
        Düz, sıralı StructNode listesi. Hiçbiri `parent` taşımaz
        (Faz 1'de gerçek nesting yapılacak).
    """
    nodes: list[StructNode] = []
    n = len(logical_lines)

    # Tüm yapısal aday düğümleri tek bir geçişte topla
    candidates: list[StructNode] = []
    for i in range(body_start_idx, n):
        ln = logical_lines[i]
        node: Optional[StructNode] = None

        if ln.kind == "volume":
            node = StructNode(
                kind="volume",
                title=ln.text.strip(),
                line_no=ln.line_no_start,
            )
        elif ln.kind == "kitab_cand":
            if _is_real_kitab_header(ln.text):
                node = StructNode(
                    kind="kitab",
                    title=ln.text.strip(),
                    line_no=ln.line_no_start,
                )
        elif ln.kind == "struct":
            m = re.match(r"^(\|+)\s*(.*)$", ln.text)
            if m:
                pipes = len(m.group(1))
                title = m.group(2).strip()
                node = StructNode(
                    kind="section",
                    title=title,
                    line_no=ln.line_no_start,
                    pipes=pipes,
                )

        if node is not None:
            node.body_start_idx = i + 1  # başlıktan sonraki satırdan başlar
            candidates.append((i, node))  # i de saklayalım — başlık satırı

    # İlk başlığa kadar gövdeyi implicit preamble section olarak ekle
    if candidates:
        first_header_i = candidates[0][0]
        if first_header_i > body_start_idx:
            # Bir gerçek metin var mı kontrol et
            has_content = any(
                logical_lines[j].kind in ("prose", "page")
                for j in range(body_start_idx, first_header_i)
            )
            if has_content:
                preamble = StructNode(
                    kind="section",
                    title="",  # başlıksız
                    line_no=logical_lines[body_start_idx].line_no_start,
                    pipes=1,
                )
                preamble.body_start_idx = body_start_idx
                preamble.body_end_idx = first_header_i
                nodes.append(preamble)

    # Aday düğümleri sırayla yerleştir
    for k, (start_i, node) in enumerate(candidates):
        if nodes:
            # Önceki node'un body_end_idx'i bu node'un başlık satırı
            if nodes[-1].body_end_idx == -1:
                nodes[-1].body_end_idx = start_i
        nodes.append(node)

    # Son node'un sonu = dosyanın (veya filtre aralığının) sonu
    if nodes and nodes[-1].body_end_idx == -1:
        nodes[-1].body_end_idx = n

    return nodes


def extract_volume_range(
    logical_lines: list[LogicalLine], target_volume: int
) -> tuple[int, int]:
    """Hedef cildin logical line aralığını döner.

    Mecmû'da cilt sınırları `# الجزء الأول`, `# الجزء الثاني` vb.
    şeklindedir. Arabic ordinal isimleri tanır.

    Returns
    -------
    (start_idx, end_idx) : exclusive end (yani Python slice gibi)
    """
    arabic_ordinals = {
        1: ["الأول", "الاول"],
        2: ["الثاني"],
        3: ["الثالث"],
        4: ["الرابع"],
        5: ["الخامس"],
        6: ["السادس"],
        7: ["السابع"],
        8: ["الثامن"],
        9: ["التاسع"],
        10: ["العاشر"],
        11: ["الحادي عشر"],
        12: ["الثاني عشر"],
        13: ["الثالث عشر"],
        14: ["الرابع عشر"],
        15: ["الخامس عشر"],
        16: ["السادس عشر"],
        17: ["السابع عشر"],
        18: ["الثامن عشر"],
        19: ["التاسع عشر"],
        20: ["العشرون", "العشرين"],
        21: ["الحادي والعشرون"],
        22: ["الثاني والعشرون"],
        23: ["الثالث والعشرون"],
        24: ["الرابع والعشرون"],
        25: ["الخامس والعشرون"],
        26: ["السادس والعشرون"],
        27: ["السابع والعشرون"],
        28: ["الثامن والعشرون"],
        29: ["التاسع والعشرون"],
        30: ["الثلاثون"],
        31: ["الحادي والثلاثون"],
        32: ["الثاني والثلاثون"],
        33: ["الثالث والثلاثون"],
        34: ["الرابع والثلاثون"],
        35: ["الخامس والثلاثون"],
    }
    if target_volume not in arabic_ordinals:
        raise ValueError(f"Cilt {target_volume} desteklenmiyor (1-35 arası)")
    target_words = arabic_ordinals[target_volume]
    next_words = arabic_ordinals.get(target_volume + 1, [])

    start_idx = -1
    end_idx = len(logical_lines)
    for i, ln in enumerate(logical_lines):
        if ln.kind != "volume":
            continue
        if start_idx == -1 and any(w in ln.text for w in target_words):
            # Ek kontrol: "الثاني" "الثاني والعشرون"da false-positive verir;
            # eşleştiğimiz kelimenin tam başlık olmasını isteyelim.
            # Basit yaklaşım: hedef kelimeyle TAM eşit, yoksa başka cilt kelimesi
            # daha uzun olarak eşliyor mu kontrol et.
            text = ln.text.strip()
            best_match = max(target_words, key=lambda w: len(w) if w in text else 0)
            # Daha uzun bir başka cilt eşleşmesi var mı?
            # (ör: "الثاني" → "الثاني عشر" da içerir)
            longer_others = [
                w
                for vol_n, words in arabic_ordinals.items()
                if vol_n != target_volume
                for w in words
                if w in text and len(w) > len(best_match)
            ]
            if longer_others:
                continue
            start_idx = i
            continue
        if start_idx != -1 and any(w in ln.text for w in next_words):
            text = ln.text.strip()
            # Aynı kontrol: false-positive eleme
            best_match_next = max(
                next_words, key=lambda w: len(w) if w in text else 0
            )
            longer_others = [
                w
                for vol_n, words in arabic_ordinals.items()
                if vol_n != target_volume + 1
                for w in words
                if w in text and len(w) > len(best_match_next)
            ]
            if longer_others:
                continue
            end_idx = i
            break

    if start_idx == -1:
        raise ValueError(f"Cilt {target_volume} dosyada bulunamadı")
    return start_idx, end_idx
