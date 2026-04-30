"""Kur'ân alıntılarını passage gövdesinden çıkarma + density metric.

İki strateji birlikte:
    1. Pre-process (strip_quran_quotes): TF-IDF / shingle öncesi
       ayet aralıklarını metinden siler.
    2. Post-process (quran_density): Pasajın ayet-yoğunluk oranı,
       adjusted_similarity = sim × (1 - max(qd_s, qd_t)) hesaplaması için.

Sıra kritik: önce STRIP, sonra NORMALIZE (offset'ler kayar).
"""

from __future__ import annotations

from typing import Sequence


def strip_quran_quotes(
    text: str,
    quran_quotes: Sequence[dict] | Sequence[object],
) -> str:
    """Passage gövdesinden Kur'ân alıntı aralıklarını çıkarır.

    Çakışan aralıkları interval-merge ile birleştirir, sondan başa kesim
    yapar (önceki indeksler etkilenmez).
    """
    if not quran_quotes:
        return text

    intervals: list[tuple[int, int]] = []
    for q in quran_quotes:
        offset = q.get("char_offset") if isinstance(q, dict) else getattr(q, "char_offset", None)
        if offset is None:
            continue
        s, e = int(offset[0]), int(offset[1])
        if s < 0 or e <= s:
            continue
        intervals.append((s, e))

    if not intervals:
        return text

    intervals.sort()
    merged: list[tuple[int, int]] = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))

    result_chars = list(text)
    for s, e in reversed(merged):
        result_chars[s:e] = " "

    result = "".join(result_chars)
    while "  " in result:
        result = result.replace("  ", " ")
    return result.strip()


def quran_density(
    text: str,
    quran_quotes: Sequence[dict] | Sequence[object],
) -> float:
    """Pasajın Kur'ân-yoğunluğu (0.0 = ayet yok, 1.0 = tamamı ayet).

    Karakter bazlı: toplam Kur'ân karakter / toplam karakter.
    Çakışan aralıklar tek sayılır.
    """
    if not quran_quotes or not text:
        return 0.0

    intervals: list[tuple[int, int]] = []
    for q in quran_quotes:
        offset = q.get("char_offset") if isinstance(q, dict) else getattr(q, "char_offset", None)
        if offset is None:
            continue
        s, e = int(offset[0]), int(offset[1])
        if s < 0 or e <= s:
            continue
        intervals.append((s, e))

    if not intervals:
        return 0.0

    intervals.sort()
    merged: list[tuple[int, int]] = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))

    quran_chars = sum(e - s for s, e in merged)
    total_chars = len(text)
    if total_chars == 0:
        return 0.0
    return min(1.0, quran_chars / total_chars)
