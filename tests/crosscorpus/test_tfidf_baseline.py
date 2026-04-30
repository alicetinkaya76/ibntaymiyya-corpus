"""TF-IDF cross-corpus comparator için testler."""

import pytest

from pipeline.crosscorpus.tfidf_baseline import TFIDFCrossCorpusComparator


SOURCE_TEXTS = [
    "الإيمان قول وعمل يزيد بالطاعة وينقص بالمعصية وهذا قول السلف",
    "الكفر كفران كفر أكبر يخرج من الملة وكفر دون كفر لا يخرج",
    "البحث في الفلسفة الإسلامية يحتاج إلى دراية بالكلام والمنطق",
]

TARGET_TEXTS = [
    "الإيمان قول وعمل يزيد بالطاعة وينقص بالمعصية وهذا قول السلف الصالح",
    "كلام مختلف تماما عن الجملة الأخرى لا علاقة بينهما أبدا",
    "الكفر نوعان كفر أكبر يخرج صاحبه من الملة وكفر أصغر دون كفر لا يخرج",
]


def test_birebir_pasaj_yuksek_benzerlik():
    c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    sim = c.similarity_matrix[0, 0]
    assert sim > 0.7


def test_alakasiz_pasaj_dusuk_benzerlik():
    c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    sim = c.similarity_matrix[0, 1]
    assert sim < 0.3


def test_paraphrased_pasaj_orta_benzerlik():
    c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    sim = c.similarity_matrix[1, 2]
    assert 0.3 < sim < 0.95


def test_topk_skoruna_gore_sirali():
    c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    matches = c.topk_for_source(0, k=3)
    similarities = [m.similarity for m in matches]
    assert similarities == sorted(similarities, reverse=True)


def test_threshold_filtreleme():
    c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    matches = c.topk_for_source(0, k=10, threshold=0.5)
    assert all(m.similarity >= 0.5 for m in matches)


def test_word_analyzer_calisir():
    c = TFIDFCrossCorpusComparator(analyzer="word", ngram_range=(1, 2), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    assert c.similarity_matrix.shape == (3, 3)


def test_fit_sirasiz_hata():
    c = TFIDFCrossCorpusComparator()
    with pytest.raises(RuntimeError):
        _ = c.similarity_matrix


def test_bos_input_hata():
    c = TFIDFCrossCorpusComparator()
    with pytest.raises(ValueError):
        c.fit([], TARGET_TEXTS)
    with pytest.raises(ValueError):
        c.fit(SOURCE_TEXTS, [])


def test_all_pairs_above_threshold_sirali():
    c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    c.fit(SOURCE_TEXTS, TARGET_TEXTS)
    pairs = c.all_pairs_above(0.0)
    similarities = [p.similarity for p in pairs]
    assert similarities == sorted(similarities, reverse=True)
