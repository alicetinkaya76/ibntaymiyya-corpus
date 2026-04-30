"""Kur'ân alıntısı çıkarımı.

OpenITI mARkdown'da Kur'ân alıntıları için iki konvansiyon vardır:

1. Resmi spec: `@QB@ ayet metni @QE@`
2. Yaygın yarı-spec: `{ayet metni}` süslü parantez içinde

İbn Teymiyye dump'ında her iki form da kullanılıyor. Bu modül her
ikisini de yakalar; çıkarılan alıntıları `QuranQuote` listesi olarak
döner. `char_offset` Python slicing ile alıntıyı tam veren yarı-açık
[start, end) aralığıdır.

NOT: Süslü parantez başka şeyler için de kullanılabilir (italik,
sözlük tanımı vb. — özellikle modern editörler). Bu modül süslü
parantezleri "Kur'ân adayı" olarak alır; gerçek Kur'ân olmadığını
kanıtlamak için Hafta 2'de Kur'ân ayet veritabanına (örn. Tanzil) karşı
doğrulama eklenecek.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


_QB_QE_RE = re.compile(r"@QB@\s*(.*?)\s*@QE@", flags=re.DOTALL)
# Süslü parantez: en yakın eşleşmeyi al; iç içe parantez nadir
_CURLY_RE = re.compile(r"\{([^{}]+)\}", flags=re.DOTALL)


@dataclass(frozen=True)
class ExtractedQuote:
    """Çıkarılan bir Kur'ân alıntısı (henüz Pydantic'e dönüşmemiş)."""

    text: str
    char_offset: tuple[int, int]
    style: str  # "qb_qe" veya "curly"


def extract_quran_quotes(text: str) -> list[ExtractedQuote]:
    """Verilen metinden tüm Kur'ân alıntılarını sırayla çıkarır.

    `char_offset`, `text` parametresine göre verilir; yarı-açık
    [start, end) aralığı, Python slicing ile alıntıyı (parantezler
    veya `@QB@..@QE@` dahil değil — sadece içeriği) verir.

    Örnek:
        >>> extract_quran_quotes("قال {الحمد لله} وانتهى")
        [ExtractedQuote(text="الحمد لله", char_offset=(5, 14), ...)]
    """
    out: list[ExtractedQuote] = []

    # 1) @QB@..@QE@ stilini tara
    for m in _QB_QE_RE.finditer(text):
        content = m.group(1)
        # offset: içeriğin başlangıç ve bitişi (parantezler değil)
        start = m.start(1)
        end = m.end(1)
        out.append(
            ExtractedQuote(
                text=content,
                char_offset=(start, end),
                style="qb_qe",
            )
        )

    # 2) Süslü parantez stilini tara — `@QB@..@QE@` ile çakışmadıysa
    #    (uygulamada @QB@/@QE@ + süslü parantez genelde farklı dosyalarda
    #    kullanılır; karışıkken çakışma kontrolü yapıyoruz)
    qb_qe_spans = [(q.char_offset[0], q.char_offset[1]) for q in out]

    def overlaps_qb_qe(s: int, e: int) -> bool:
        for qs, qe in qb_qe_spans:
            if not (e <= qs or s >= qe):
                return True
        return False

    for m in _CURLY_RE.finditer(text):
        content = m.group(1).strip()
        if not content:
            continue
        # offset: süslü parantezin İÇİ
        start = m.start(1)
        end = m.end(1)
        # Strip yapılınca offset'leri yeniden hesapla — strip kelime
        # bazında değil whitespace olduğundan dikkatli olmak lazım
        original_inner = m.group(1)
        leading_ws = len(original_inner) - len(original_inner.lstrip())
        trailing_ws = len(original_inner) - len(original_inner.rstrip())
        adj_start = start + leading_ws
        adj_end = end - trailing_ws
        if overlaps_qb_qe(adj_start, adj_end):
            continue
        out.append(
            ExtractedQuote(
                text=content,
                char_offset=(adj_start, adj_end),
                style="curly",
            )
        )

    # Sırala: char_offset.start'a göre
    out.sort(key=lambda q: q.char_offset[0])
    return out


# Görece güvenilir Kur'ân ayet işaretleri (manuel filtreleme için)
# Bir süslü parantez içeriği aşağıdakileri içeriyorsa Kur'ân olma
# olasılığı artar. Bu liste exhaustive değil; Hafta 2'de Tanzil
# karşılaştırmasıyla genişletilecek.
QURAN_HIGH_PRIORS = (
    "بسم الله الرحمن الرحيم",
    "الحمد لله رب العالمين",
    "إن الله",
    "والله",
    "يا أيها الذين آمنوا",
    "يا أيها الناس",
    "قل ",
    "قال تعالى",
)
