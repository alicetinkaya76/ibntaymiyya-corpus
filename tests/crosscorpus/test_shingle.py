"""Word-shingle + Jaccard testleri."""

from pipeline.crosscorpus.shingle import (
    jaccard,
    jaccard_overlap_coefficient,
    shingle_set,
)


def test_shingle_5_kelime():
    metin = "a b c d e f g"
    shg = shingle_set(metin, n=5)
    assert shg == {"a b c d e", "b c d e f", "c d e f g"}


def test_shingle_kisa_metin_bos_set():
    assert shingle_set("a b c", n=5) == set()


def test_shingle_idempotent_kelime_sirasi():
    metin = "الإيمان قول وعمل يزيد بالطاعة وينقص بالمعصية"
    a = shingle_set(metin, n=3)
    b = shingle_set(metin, n=3)
    assert a == b


def test_jaccard_aynı_set_bir():
    s = {"a", "b", "c"}
    assert jaccard(s, s) == 1.0


def test_jaccard_ayrik_set_sifir():
    a = {"a", "b"}
    b = {"c", "d"}
    assert jaccard(a, b) == 0.0


def test_jaccard_yari_yariya():
    a = {"a", "b"}
    b = {"b", "c"}
    assert abs(jaccard(a, b) - 1 / 3) < 1e-9


def test_jaccard_iki_bos_set_sifir():
    assert jaccard(set(), set()) == 0.0


def test_overlap_coefficient_tam_kapsayan_bir():
    a = {"a", "b"}
    b = {"a", "b", "c", "d"}
    assert jaccard_overlap_coefficient(a, b) == 1.0
    assert jaccard(a, b) == 0.5


def test_overlap_coefficient_alakasiz_sifir():
    a = {"a", "b"}
    b = {"c", "d"}
    assert jaccard_overlap_coefficient(a, b) == 0.0


def test_birebir_metin_jaccard_yuksek():
    a = shingle_set("الإيمان قول وعمل يزيد بالطاعة وينقص بالمعصية", n=3)
    b = shingle_set("الإيمان قول وعمل يزيد بالطاعة وينقص بالمعصية كلها", n=3)
    sim = jaccard(a, b)
    assert sim > 0.5
