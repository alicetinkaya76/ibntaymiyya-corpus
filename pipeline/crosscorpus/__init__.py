"""Cross-corpus duplikasyon haritalama modülü.

Public API:
    Cross-corpus eşleşme:
        normalize_arabic, strip_quran_quotes, quran_density,
        TFIDFCrossCorpusComparator, shingle_set, jaccard,
        find_pairs, CrossCorpusPair

    Manuel doğrulama (S4):
        LabelKind, PairAnnotation, AnnotationSet,
        save_annotation_set, load_annotation_set, list_annotation_sets,
        cohen_kappa, confusion_matrix
"""

from .normalize import normalize_arabic
from .quran_filter import strip_quran_quotes, quran_density
from .tfidf_baseline import TFIDFCrossCorpusComparator
from .shingle import shingle_set, jaccard
from .pair_extractor import CrossCorpusPair, find_pairs
from .annotation_schema import (
    AnnotationSet,
    LabelKind,
    PairAnnotation,
    cohen_kappa,
    confusion_matrix,
    list_annotation_sets,
    load_annotation_set,
    save_annotation_set,
)

__all__ = [
    # Cross-corpus eşleşme
    "normalize_arabic",
    "strip_quran_quotes",
    "quran_density",
    "TFIDFCrossCorpusComparator",
    "shingle_set",
    "jaccard",
    "find_pairs",
    "CrossCorpusPair",
    # Manuel doğrulama
    "AnnotationSet",
    "LabelKind",
    "PairAnnotation",
    "cohen_kappa",
    "confusion_matrix",
    "list_annotation_sets",
    "load_annotation_set",
    "save_annotation_set",
]
