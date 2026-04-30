"""Arapça metin normalizasyonu — TF-IDF ve shingle öncesi temizlik.

Stemming değildir; karakter seviyesi normalizasyondur.

Uygulanan dönüşümler:
    1. Tashkeel (harekeler) silinir
    2. Alif varyantları birleştirilir: أ إ آ ٱ → ا
    3. Yâ varyantları birleştirilir: ى → ي
    4. Tâ marbūta ve hamza varyantları KORUNUR (anlam ayırıcı)
    5. Tatweel silinir: ـ
    6. Whitespace tek boşluğa indirgenir
    7. ASCII + Arapça noktalama silinir

Reddedilen alternatif: stemmer (kalibrasyon hatası kaynağı).
"""

from __future__ import annotations

import re
import unicodedata


_TASHKEEL = "".join([
    "\u064b", "\u064c", "\u064d", "\u064e", "\u064f", "\u0650",
    "\u0651", "\u0652", "\u0653", "\u0654", "\u0655", "\u0656",
    "\u0657", "\u0658", "\u0670",
])
_TASHKEEL_RE = re.compile(f"[{_TASHKEEL}]")
_TATWEEL = "\u0640"

_ALIF_VARIANTS = {
    "\u0622": "\u0627", "\u0623": "\u0627",
    "\u0625": "\u0627", "\u0671": "\u0627",
}
_YA_VARIANTS = {"\u0649": "\u064a"}
_CHAR_MAP = {**_ALIF_VARIANTS, **_YA_VARIANTS}

_PUNCT_RE = re.compile(
    r"[\(\)\[\]\{\}\.\,\;\:\?\!\"\'\-\—\–\…\«\»\/\\\|\<\>\=\+\*\&\^\%\$\#\@\~\`"
    r"\u060c\u061b\u061f\u066a\u066c\u066d\ufd3e\ufd3f]"
)
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_arabic(text: str) -> str:
    """Klasik Arapça metni karşılaştırma için normalize eder.

    Idempotent: normalize_arabic(normalize_arabic(x)) == normalize_arabic(x).
    """
    text = unicodedata.normalize("NFKC", text)
    text = _TASHKEEL_RE.sub("", text)
    text = text.replace(_TATWEEL, "")
    text = "".join(_CHAR_MAP.get(c, c) for c in text)
    text = _PUNCT_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text
