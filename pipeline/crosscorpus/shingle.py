"""N-gram word-shingle + Jaccard benzerliği — kesin metric.

Word-shingle (n=5) tercihi: "ifade benzerliği"nin doğru granülaritesi —
"birebir tekrar" tespiti için altın standart.
"""

from __future__ import annotations


def shingle_set(text: str, n: int = 5) -> set[str]:
    """Metni n-kelime shingle setine dönüştürür."""
    words = text.split()
    if len(words) < n:
        return set()
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    """|A ∩ B| / |A ∪ B|. Boş setler için 0.0."""
    if not a and not b:
        return 0.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def jaccard_overlap_coefficient(a: set[str], b: set[str]) -> float:
    """|A ∩ B| / min(|A|, |B|). Asimetrik (alt-küme) durumlarda Jaccard'dan
    daha bilgilendirici."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))
