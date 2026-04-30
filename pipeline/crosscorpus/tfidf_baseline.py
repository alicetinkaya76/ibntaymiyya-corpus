"""TF-IDF + cosine benzerlik baseline'ı (cross-corpus).

char_wb (3-5) ana yaklaşım. Word-level paralel olarak da hesaplanır.
Char n-gram Arapça'da stemmer'sız çalışan en güvenilir yöntem;
الإيمان / إيمان / إيمانه gibi morfolojik varyantları otomatik yakalar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


Analyzer = Literal["char_wb", "word"]


@dataclass(frozen=True)
class Match:
    source_idx: int
    target_idx: int
    similarity: float


class TFIDFCrossCorpusComparator:
    """İki passage seti arasında TF-IDF + cosine benzerliği hesaplar.

    Tek modeli iki sete fit eder, böylece IDF ortak vocabulary üzerinden
    tutarlı olur.
    """

    def __init__(
        self,
        analyzer: Analyzer = "char_wb",
        ngram_range: tuple[int, int] = (3, 5),
        min_df: int = 2,
        max_df: float = 0.95,
        sublinear_tf: bool = True,
    ) -> None:
        self.analyzer = analyzer
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            analyzer=analyzer,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=sublinear_tf,
            lowercase=False,
        )
        self._sim_matrix: np.ndarray | None = None
        self._n_source: int = 0
        self._n_target: int = 0

    def fit(self, source_texts: Sequence[str], target_texts: Sequence[str]) -> None:
        if not source_texts or not target_texts:
            raise ValueError("source_texts ve target_texts boş olamaz")

        all_texts = list(source_texts) + list(target_texts)
        matrix = self.vectorizer.fit_transform(all_texts)

        n_s = len(source_texts)
        n_t = len(target_texts)
        source_vec = matrix[:n_s]
        target_vec = matrix[n_s:]

        self._sim_matrix = cosine_similarity(source_vec, target_vec)
        self._n_source = n_s
        self._n_target = n_t

    @property
    def similarity_matrix(self) -> np.ndarray:
        if self._sim_matrix is None:
            raise RuntimeError("Önce fit() çağrılmalı")
        return self._sim_matrix

    def topk_for_source(
        self, source_idx: int, k: int = 3, threshold: float = 0.0
    ) -> list[Match]:
        if self._sim_matrix is None:
            raise RuntimeError("Önce fit() çağrılmalı")

        row = self._sim_matrix[source_idx]
        if k >= len(row):
            top_idx = np.argsort(-row)
        else:
            top_idx = np.argpartition(-row, k)[:k]
            top_idx = top_idx[np.argsort(-row[top_idx])]

        return [
            Match(source_idx=source_idx, target_idx=int(j), similarity=float(row[j]))
            for j in top_idx
            if row[j] >= threshold
        ]

    def topk_pairs(self, k: int = 3, threshold: float = 0.0) -> list[Match]:
        if self._sim_matrix is None:
            raise RuntimeError("Önce fit() çağrılmalı")

        all_matches: list[Match] = []
        for i in range(self._n_source):
            all_matches.extend(self.topk_for_source(i, k=k, threshold=threshold))

        return sorted(all_matches, key=lambda m: -m.similarity)

    def all_pairs_above(self, threshold: float) -> list[Match]:
        if self._sim_matrix is None:
            raise RuntimeError("Önce fit() çağrılmalı")

        rows, cols = np.where(self._sim_matrix >= threshold)
        return sorted(
            [
                Match(
                    source_idx=int(r),
                    target_idx=int(c),
                    similarity=float(self._sim_matrix[r, c]),
                )
                for r, c in zip(rows, cols)
            ],
            key=lambda m: -m.similarity,
        )
