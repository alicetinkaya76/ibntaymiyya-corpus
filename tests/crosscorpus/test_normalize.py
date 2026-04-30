"""Arapça normalize fonksiyonu için testler."""

from pipeline.crosscorpus.normalize import normalize_arabic


def test_tashkeel_silinir():
    """Harekeli ve harekesiz aynı sonucu vermeli."""
    harekeli = "الْإِيمَانُ"
    harekesiz = "الإيمان"
    assert normalize_arabic(harekeli) == normalize_arabic(harekesiz)


def test_alif_varyantlari_birlesir():
    assert normalize_arabic("أحمد") == normalize_arabic("احمد")
    assert normalize_arabic("إيمان") == normalize_arabic("ايمان")
    assert normalize_arabic("آدم") == normalize_arabic("ادم")


def test_alif_maksura_yaya_donusur():
    """ى → ي."""
    assert normalize_arabic("على") == normalize_arabic("علي")


def test_idempotent():
    metin = "الْإِيمَانُ بِاللَّهِ"
    once = normalize_arabic(metin)
    iki_kez = normalize_arabic(once)
    assert once == iki_kez


def test_tatweel_silinir():
    assert normalize_arabic("اللـــه") == normalize_arabic("الله")


def test_noktalama_silinir():
    metin = "قال (الإمام) أحمد: \"الإيمان\" قول وعمل."
    sonuc = normalize_arabic(metin)
    assert "(" not in sonuc
    assert ")" not in sonuc
    assert ":" not in sonuc
    assert '"' not in sonuc
    assert "الايمان" in sonuc.split()


def test_whitespace_tekleştirilir():
    assert normalize_arabic("الإيمان    قول") == "الايمان قول"


def test_bos_metin_bos_doner():
    assert normalize_arabic("") == ""


def test_sadece_tashkeel_bos_doner():
    sadece_harekeler = "\u064e\u064f\u0650\u0651"
    assert normalize_arabic(sadece_harekeler) == ""
