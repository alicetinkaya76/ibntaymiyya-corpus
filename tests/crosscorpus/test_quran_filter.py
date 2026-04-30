"""Kur'ân alıntı maskeleme + density testleri."""

from pipeline.crosscorpus.quran_filter import quran_density, strip_quran_quotes


def test_strip_tek_alinti():
    metin = "قال الله تعالى: قل هو الله أحد. وهذا دليل التوحيد."
    quotes = [{"text": "قل هو الله أحد", "char_offset": [16, 30]}]
    sonuc = strip_quran_quotes(metin, quotes)
    assert "قل هو الله أحد" not in sonuc
    assert "دليل التوحيد" in sonuc


def test_strip_birden_fazla_alinti():
    metin = "abc DEF ghi JKL mno"
    quotes = [
        {"text": "DEF", "char_offset": [4, 7]},
        {"text": "JKL", "char_offset": [12, 15]},
    ]
    sonuc = strip_quran_quotes(metin, quotes)
    assert "DEF" not in sonuc
    assert "JKL" not in sonuc
    assert "abc" in sonuc
    assert "ghi" in sonuc
    assert "mno" in sonuc


def test_strip_alinti_yoksa_metin_aynen_doner():
    metin = "Bu metin Kur'ân alıntısı içermez."
    sonuc = strip_quran_quotes(metin, [])
    assert sonuc == metin


def test_strip_cakisan_araliklar_birlesir():
    metin = "abcdefghij"
    quotes = [
        {"text": "cde", "char_offset": [2, 5]},
        {"text": "def", "char_offset": [3, 6]},
    ]
    sonuc = strip_quran_quotes(metin, quotes)
    assert "cdef" not in sonuc.replace(" ", "")
    assert "ab" in sonuc
    assert "ghij" in sonuc


def test_density_tum_metin_ayet():
    metin = "قل هو الله أحد"
    quotes = [{"text": metin, "char_offset": [0, len(metin)]}]
    assert quran_density(metin, quotes) == 1.0


def test_density_yari_yariya():
    metin = "abc" + "X" * 7
    quotes = [{"text": "abc", "char_offset": [0, 3]}]
    assert quran_density(metin, quotes) == 0.3


def test_density_alinti_yoksa_sifir():
    assert quran_density("hiç alıntı yok", []) == 0.0


def test_density_cakisan_araliklar_iki_kez_sayilmaz():
    metin = "abcdefghij"
    quotes = [
        {"text": "abcde", "char_offset": [0, 5]},
        {"text": "defgh", "char_offset": [3, 8]},
    ]
    assert quran_density(metin, quotes) == 0.8


def test_strip_pydantic_obje_kabul_edilir():
    class FakeQuote:
        char_offset = (4, 7)
        text = "DEF"

    metin = "abc DEF ghi"
    sonuc = strip_quran_quotes(metin, [FakeQuote()])
    assert "DEF" not in sonuc
