"""find_pairs orchestration için entegrasyon testleri (gerçek kanonik JSON)."""

import json
from pathlib import Path

import pytest

from pipeline.crosscorpus.pair_extractor import (
    CrossCorpusPair,
    find_pairs,
    load_units,
    save_pairs,
)

DATA = Path(__file__).resolve().parents[2] / "data" / "canonical"
IMAN = DATA / "iman_v0.1.json"
IMAN_STANDALONE = DATA / "iman_standalone_v0.1.json"


@pytest.fixture(scope="module")
def iman_units():
    if not IMAN.exists():
        pytest.skip(f"Kanonik veri yok: {IMAN}")
    return load_units(IMAN)


@pytest.fixture(scope="module")
def iman_standalone_units():
    if not IMAN_STANDALONE.exists():
        pytest.skip(f"Kanonik veri yok: {IMAN_STANDALONE}")
    return load_units(IMAN_STANDALONE)


def test_iman_vs_standalone_eslemis_pasaj_var(iman_units, iman_standalone_units):
    pairs = find_pairs(
        iman_units, iman_standalone_units,
        method="tfidf_char", threshold=0.5, topk=1, quran_aware=True,
    )
    assert len(pairs) > 0


def test_pair_alanlari_dolu(iman_units, iman_standalone_units):
    pairs = find_pairs(
        iman_units, iman_standalone_units,
        method="tfidf_char", threshold=0.4, topk=1,
    )
    if not pairs:
        pytest.skip("Eşleşme bulunamadı")
    p = pairs[0]
    assert p.source_unit_id.startswith("MF-V07-")
    assert p.target_unit_id.startswith("IMN-")
    assert 0.0 <= p.similarity <= 1.0
    assert 0.0 <= p.adjusted_similarity <= 1.0
    assert p.adjusted_similarity <= p.similarity
    assert 0.0 <= p.quran_density_source <= 1.0
    assert 0.0 <= p.quran_density_target <= 1.0


def test_method_secimi_calisir(iman_units, iman_standalone_units):
    for method in ["tfidf_char", "tfidf_word", "shingle_jaccard"]:
        pairs = find_pairs(
            iman_units, iman_standalone_units,
            method=method, threshold=0.05, topk=1,
        )
        assert len(pairs) > 0, f"{method} hiç pair üretmedi"


def test_save_load_roundtrip(tmp_path):
    pairs = [
        CrossCorpusPair(
            source_unit_id="MF-V07-S00-P000",
            target_unit_id="IMN-S00-P010",
            similarity=0.85,
            method="tfidf_char",
            quran_density_source=0.2,
            quran_density_target=0.15,
            adjusted_similarity=0.68,
        )
    ]
    out = tmp_path / "test_pairs.json"
    save_pairs(pairs, out, metadata={"test": True})
    data = json.loads(out.read_text())
    assert data["metadata"]["test"] is True
    assert len(data["pairs"]) == 1
    assert data["pairs"][0]["similarity"] == 0.85


def test_kisa_passage_atilir(iman_units, iman_standalone_units):
    pairs_loose = find_pairs(
        iman_units, iman_standalone_units,
        method="tfidf_char", threshold=0.0, topk=1, min_words=30,
    )
    pairs_strict = find_pairs(
        iman_units, iman_standalone_units,
        method="tfidf_char", threshold=0.0, topk=1, min_words=500,
    )
    assert len(pairs_strict) <= len(pairs_loose)
