"""Üst-seviye cross-corpus eşleşme arama orchestration.

`find_pairs` adımları:
    1. Passage'ları seç (tier == "passage")
    2. min_words filtresi
    3. Kur'ân alıntılarını maskele (varsayılan)
    4. Normalize et
    5. TF-IDF veya shingle ile eşleştir
    6. Adjusted similarity ekle: sim × (1 - max(qd_s, qd_t))
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Sequence

from .normalize import normalize_arabic
from .quran_filter import quran_density, strip_quran_quotes
from .shingle import jaccard, shingle_set
from .tfidf_baseline import TFIDFCrossCorpusComparator


Method = Literal["tfidf_char", "tfidf_word", "shingle_jaccard"]


@dataclass
class CrossCorpusPair:
    """Bir kaynak passage ile hedef passage arasında bulunan eşleşme."""

    source_unit_id: str
    target_unit_id: str
    similarity: float
    method: str
    quran_density_source: float = 0.0
    quran_density_target: float = 0.0
    adjusted_similarity: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _prepare_text(unit: dict, *, mask_quran: bool) -> str:
    """Passage unit'inden karşılaştırılabilir metin üret. Sıra: strip → normalize."""
    text = unit.get("full_text_arabic", "")
    if mask_quran:
        text = strip_quran_quotes(text, unit.get("quran_quotes") or [])
    return normalize_arabic(text)


def _filter_passages(units: Sequence[dict]) -> list[dict]:
    return [u for u in units if u.get("tier") == "passage"]


def find_pairs(
    sources: Sequence[dict],
    targets: Sequence[dict],
    *,
    method: Method = "tfidf_char",
    threshold: float = 0.3,
    topk: int = 3,
    quran_aware: bool = True,
    min_words: int = 30,
) -> list[CrossCorpusPair]:
    """Kaynak ve hedef passage setleri arasında eşleşme arar."""
    sources = _filter_passages(sources)
    targets = _filter_passages(targets)

    sources = [u for u in sources if u.get("word_count", 0) >= min_words]
    targets = [u for u in targets if u.get("word_count", 0) >= min_words]

    if not sources or not targets:
        return []

    source_texts = [_prepare_text(u, mask_quran=quran_aware) for u in sources]
    target_texts = [_prepare_text(u, mask_quran=quran_aware) for u in targets]

    s_density = [
        quran_density(u.get("full_text_arabic", ""), u.get("quran_quotes") or [])
        for u in sources
    ]
    t_density = [
        quran_density(u.get("full_text_arabic", ""), u.get("quran_quotes") or [])
        for u in targets
    ]

    pairs: list[CrossCorpusPair] = []

    if method in ("tfidf_char", "tfidf_word"):
        analyzer = "char_wb" if method == "tfidf_char" else "word"
        ngram = (3, 5) if analyzer == "char_wb" else (1, 2)
        comparator = TFIDFCrossCorpusComparator(analyzer=analyzer, ngram_range=ngram)
        comparator.fit(source_texts, target_texts)
        matches = comparator.topk_pairs(k=topk, threshold=threshold)

        for m in matches:
            qd_s = s_density[m.source_idx]
            qd_t = t_density[m.target_idx]
            adjusted = m.similarity * (1.0 - max(qd_s, qd_t))
            pairs.append(
                CrossCorpusPair(
                    source_unit_id=sources[m.source_idx]["unit_id"],
                    target_unit_id=targets[m.target_idx]["unit_id"],
                    similarity=round(m.similarity, 4),
                    method=method,
                    quran_density_source=round(qd_s, 4),
                    quran_density_target=round(qd_t, 4),
                    adjusted_similarity=round(adjusted, 4),
                )
            )

    elif method == "shingle_jaccard":
        s_shingles = [shingle_set(t, n=5) for t in source_texts]
        t_shingles = [shingle_set(t, n=5) for t in target_texts]

        for i, s_shg in enumerate(s_shingles):
            if not s_shg:
                continue
            scored: list[tuple[int, float]] = []
            for j, t_shg in enumerate(t_shingles):
                if not t_shg:
                    continue
                sim = jaccard(s_shg, t_shg)
                if sim >= threshold:
                    scored.append((j, sim))
            scored.sort(key=lambda x: -x[1])
            scored = scored[:topk]

            for j, sim in scored:
                qd_s = s_density[i]
                qd_t = t_density[j]
                adjusted = sim * (1.0 - max(qd_s, qd_t))
                pairs.append(
                    CrossCorpusPair(
                        source_unit_id=sources[i]["unit_id"],
                        target_unit_id=targets[j]["unit_id"],
                        similarity=round(sim, 4),
                        method=method,
                        quran_density_source=round(qd_s, 4),
                        quran_density_target=round(qd_t, 4),
                        adjusted_similarity=round(adjusted, 4),
                    )
                )
    else:
        raise ValueError(f"Bilinmeyen method: {method}")

    return sorted(pairs, key=lambda p: -p.similarity)


def save_pairs(
    pairs: Sequence[CrossCorpusPair],
    path: str | Path,
    metadata: dict | None = None,
) -> None:
    """Çiftleri JSON'a yaz."""
    out = {"metadata": metadata or {}, "pairs": [p.to_dict() for p in pairs]}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_units(path: str | Path) -> list[dict]:
    """Kanonik JSON'u yükle."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
