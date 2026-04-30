"""Annotation şeması ve Cohen κ için testler."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from pipeline.crosscorpus.annotation_schema import (
    AnnotationSet,
    LabelKind,
    PairAnnotation,
    cohen_kappa,
    confusion_matrix,
    list_annotation_sets,
    load_annotation_set,
    save_annotation_set,
)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ann(src, tgt, label, annotator="huseyin"):
    return PairAnnotation(
        source_unit_id=src,
        target_unit_id=tgt,
        label=label,
        annotator=annotator,
        annotated_at=_now(),
    )


# ---------------------------------------------------------------------------
# Şema validasyonu
# ---------------------------------------------------------------------------


def test_label_kind_enum_5_sinif():
    """LabelKind 5 sınıftan oluşmalı: EXACT/EDITED/EXCERPT/OVERLAP/NOISE."""
    assert {k.value for k in LabelKind} == {
        "EXACT", "EDITED", "EXCERPT", "OVERLAP", "NOISE"
    }


def test_label_kind_true_positive_dogru():
    """EXACT/EDITED/EXCERPT → True; OVERLAP/NOISE → False."""
    assert LabelKind.is_true_positive(LabelKind.EXACT) is True
    assert LabelKind.is_true_positive(LabelKind.EDITED) is True
    assert LabelKind.is_true_positive(LabelKind.EXCERPT) is True
    assert LabelKind.is_true_positive(LabelKind.OVERLAP) is False
    assert LabelKind.is_true_positive(LabelKind.NOISE) is False


def test_pair_annotation_bos_annotator_hata():
    """annotator boşsa ValidationError."""
    with pytest.raises(Exception):  # pydantic ValidationError
        PairAnnotation(
            source_unit_id="MF-V07-S00-P000",
            target_unit_id="IMN-S00-P000",
            label=LabelKind.EXACT,
            annotator="   ",
            annotated_at=_now(),
        )


# ---------------------------------------------------------------------------
# AnnotationSet ekle/güncelle/ara
# ---------------------------------------------------------------------------


def test_annotation_set_add_or_update_yeni():
    """Yeni pair eklenince listeye eklenir."""
    aset = AnnotationSet(annotator="huseyin", session_id="s1")
    aset.add_or_update(_ann("MF-A", "IMN-A", LabelKind.EXACT))
    assert len(aset.annotations) == 1
    assert aset.label_for("MF-A", "IMN-A") == LabelKind.EXACT


def test_annotation_set_add_or_update_uzerine_yazar():
    """Aynı pair tekrar eklenince üzerine yazılmalı, listeye eklenmemeli."""
    aset = AnnotationSet(annotator="huseyin", session_id="s1")
    aset.add_or_update(_ann("MF-A", "IMN-A", LabelKind.EXACT))
    aset.add_or_update(_ann("MF-A", "IMN-A", LabelKind.EDITED))
    assert len(aset.annotations) == 1  # sadece 1, güncellenmiş
    assert aset.label_for("MF-A", "IMN-A") == LabelKind.EDITED


def test_annotation_set_label_for_eksik_etiket_none():
    """Etiketlenmemiş pair için label_for None döner."""
    aset = AnnotationSet(annotator="huseyin", session_id="s1")
    assert aset.label_for("X", "Y") is None


# ---------------------------------------------------------------------------
# Atomic save / load roundtrip
# ---------------------------------------------------------------------------


def test_save_load_roundtrip(tmp_path):
    """Kaydedilen AnnotationSet aynen geri yüklenmeli."""
    aset = AnnotationSet(annotator="Hüseyin Gökalp", session_id="20260430T1700")
    aset.add_or_update(_ann("MF-V07-S00-P001", "IMN-S00-P010", LabelKind.EXACT))
    aset.add_or_update(_ann("MF-V07-S00-P002", "IMN-S00-P011", LabelKind.NOISE))

    path = save_annotation_set(aset, base_dir=tmp_path)
    assert path.exists()

    # Türkçe karakter slug — "huseyin_gokalp" olmalı
    assert "huseyin_gokalp" in path.name
    assert "20260430T1700" in path.name

    # JSON unicode'u koruyor olmalı
    raw = path.read_text(encoding="utf-8")
    assert "Hüseyin Gökalp" in raw

    loaded = load_annotation_set(path)
    assert loaded.annotator == "Hüseyin Gökalp"
    assert len(loaded.annotations) == 2
    assert loaded.label_for("MF-V07-S00-P001", "IMN-S00-P010") == LabelKind.EXACT


def test_save_atomic_temp_file_birakmaz(tmp_path):
    """Save sonrasında .tmp dosya kalmamalı."""
    aset = AnnotationSet(annotator="ali", session_id="s1")
    aset.add_or_update(_ann("MF-A", "IMN-A", LabelKind.EDITED))
    save_annotation_set(aset, base_dir=tmp_path)

    tmp_files = list(tmp_path.glob("*.tmp"))
    hidden_tmps = list(tmp_path.glob(".*.tmp"))
    assert tmp_files == []
    assert hidden_tmps == []


def test_list_annotation_sets_bos_dizin(tmp_path):
    assert list_annotation_sets(tmp_path) == []


def test_list_annotation_sets_var_olan_dosyalari_dondurur(tmp_path):
    aset1 = AnnotationSet(annotator="huseyin", session_id="s1")
    aset1.add_or_update(_ann("a", "b", LabelKind.EXACT))
    save_annotation_set(aset1, base_dir=tmp_path)

    aset2 = AnnotationSet(annotator="ali", session_id="s2")
    aset2.add_or_update(_ann("a", "b", LabelKind.EDITED))
    save_annotation_set(aset2, base_dir=tmp_path)

    files = list_annotation_sets(tmp_path)
    assert len(files) == 2


# ---------------------------------------------------------------------------
# Cohen κ
# ---------------------------------------------------------------------------


def test_cohen_kappa_tam_uyum_bir():
    """İki annotator tüm pair'lerde aynı etiketi verirse κ=1.0."""
    a = [
        _ann("p1", "q1", LabelKind.EXACT, "A"),
        _ann("p2", "q2", LabelKind.EDITED, "A"),
        _ann("p3", "q3", LabelKind.NOISE, "A"),
    ]
    b = [
        _ann("p1", "q1", LabelKind.EXACT, "B"),
        _ann("p2", "q2", LabelKind.EDITED, "B"),
        _ann("p3", "q3", LabelKind.NOISE, "B"),
    ]
    assert cohen_kappa(a, b) == 1.0


def test_cohen_kappa_rastgele_dusuk():
    """Düşük uyum durumunda κ < 0.5 olmalı.

    Burada A hep EXACT, B hep NOISE → po=0, κ negatif veya 0.
    """
    a = [_ann(f"p{i}", f"q{i}", LabelKind.EXACT, "A") for i in range(5)]
    b = [_ann(f"p{i}", f"q{i}", LabelKind.NOISE, "B") for i in range(5)]
    k = cohen_kappa(a, b)
    assert k < 0.5


def test_confusion_matrix_dogru_sayim():
    """A ve B'nin aynı verdiği etiketler ile farklı verdiği etiketler ayrı sayılmalı."""
    a = [
        _ann("p1", "q1", LabelKind.EXACT, "A"),
        _ann("p2", "q2", LabelKind.EXACT, "A"),
        _ann("p3", "q3", LabelKind.EDITED, "A"),
    ]
    b = [
        _ann("p1", "q1", LabelKind.EXACT, "B"),
        _ann("p2", "q2", LabelKind.EDITED, "B"),
        _ann("p3", "q3", LabelKind.EDITED, "B"),
    ]
    cm = confusion_matrix(a, b)
    assert cm[(LabelKind.EXACT, LabelKind.EXACT)] == 1
    assert cm[(LabelKind.EXACT, LabelKind.EDITED)] == 1
    assert cm[(LabelKind.EDITED, LabelKind.EDITED)] == 1
