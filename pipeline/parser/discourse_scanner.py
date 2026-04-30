"""F1-F10 söylem-yüzey örüntüleri tarayıcısı.

Bu modül, strateji dökümanı Bölüm 3.2'de tanımlanan on söylem-fonksiyon
kategorisinin (F1-F10) Arapça yüzey örüntülerini metinde arar ve aday
etiketler verir. Buradaki etiketler **bağlayıcı değildir**; gerçek F1-F10
sınıflandırması Hafta 4'te LLM zero-shot + human gold annotator
sürecinden geçer.

Bu modülün çıktısı yalnızca:
1. F1-F10 sınıflandırıcısının fine-tuning aşamasında "yumuşak ön etiket"
   olarak kullanılmak için
2. Hüseyin Hoca'nın gold annotation aşamasında "şu pasaj F4 olabilir,
   bak" şeklinde dikkat çekici işaret olarak

NOT: Bu örüntüler güvenilir DEĞİLDİR. F4 (concession) örneği `لو سلمنا`
en güvenilir; F1 ve F8 ise neredeyse tamamen bağlam-bağımlıdır ve
yüzey örüntüden tahmin edilemez. Bu nedenle aşağıdaki listeler bilinen
yüksek-presisyonlu örüntülerle sınırlı tutulmuştur.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Her örüntü: (regex, hangi F kategorisi, kısa açıklama)
_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    # F2 · Öz-tefrik (self-distinction): yazarın kendisine atfedileni reddi
    (re.compile(r"كذبوا\s+عل[يى]"), "F2", "kuzhibu_'alayya"),
    (re.compile(r"افترى\s+عل[يى]"), "F2", "ifta'a_'alayya"),
    (re.compile(r"ن[ُُ]?س[ِِ]?ب\s+إل[يى]"), "F2", "nusiba_ilayya"),
    (re.compile(r"زعم(?:وا)?\s+أن[يى]"), "F2", "za'amu_anniy"),
    (re.compile(r"ما\s+ق[لُ]ت\s+(?:كذا|ذلك|هذا)"), "F2", "ma_qultu"),
    # F3 · Muhalif alıntısı (opponent quote)
    (re.compile(r"قالت\s+(?:ال)?جهمية"), "F3", "qaalat_jahmiyya"),
    (re.compile(r"قالت\s+(?:ال)?معتزلة"), "F3", "qaalat_mu'tazila"),
    (re.compile(r"قالت\s+(?:ال)?أشعرية"), "F3", "qaalat_ash'ariyya"),
    (re.compile(r"قالت\s+(?:ال)?فلاسفة"), "F3", "qaalat_falasifa"),
    (re.compile(r"قالت\s+طائفة"), "F3", "qaalat_ta'ifa"),
    (re.compile(r"قال\s+(?:ال)?قرامطة"), "F3", "qaala_qaramita"),
    # F4 · Çürütmek için kabul (concession)
    (re.compile(r"لو\s+سلَّ?منا"), "F4", "law_sallamna"),
    (re.compile(r"لو\s+ف[ُُ]ر[ِِ]ض"), "F4", "law_furida"),
    (re.compile(r"لو\s+قدر(?:نا)?"), "F4", "law_qaddarna"),
    (re.compile(r"على\s+تقدير\s+(?:صحة|ثبوت)"), "F4", "ala_taqdir"),
    # F5 · Şartlı önerme (conditional)
    # Not: `إذا` ve `إن` çok genel; sadece teolojik bağlamda anlamlı
    # kombinasyonları alıyoruz. Bu kategoriyi ileride güçlendireceğiz.
    (re.compile(r"إن\s+كان\s+المراد"), "F5", "in_kana_l-murad"),
    (re.compile(r"فإن\s+أردت(?:م)?\s+ب"), "F5", "fa-in_aradtum"),
    # F6 · İcmâ iddiası (consensus)
    (re.compile(r"اتفق\s+(?:ال)?مسلمون"), "F6", "ittafaqa_l-muslimun"),
    (re.compile(r"أجمع\s+(?:ال)?صحابة"), "F6", "ajma'a_l-sahaba"),
    (re.compile(r"أجمعت\s+الأمة"), "F6", "ajma'at_l-umma"),
    (re.compile(r"إجماع\s+(?:ال)?سلف"), "F6", "ijma'_l-salaf"),
    (re.compile(r"لا\s+خلاف\s+بين"), "F6", "la_khilafa_bayna"),
    # F7 · Tafsîl (anlam ayrımı) — İbn Teymiyye'nin imzası
    (re.compile(r"يحتمل\s+وجهين"), "F7", "yahtamil_wajhayn"),
    (re.compile(r"على\s+(?:ال)?وجهين"), "F7", "ala_l-wajhayn"),
    (re.compile(r"لفظ\s+مجمل"), "F7", "lafz_mujmal"),
    (re.compile(r"يطلق\s+على\s+معنيين"), "F7", "yutlaq_ala_ma'nayayn"),
    (re.compile(r"التفصيل\s+فيه"), "F7", "al-tafsilu_fihi"),
    (re.compile(r"فيه\s+تفصيل"), "F7", "fihi_tafsil"),
    # F8 · Tashîh (refinement)
    (re.compile(r"يعني\s+(?:بهذا|به|بذلك)"), "F8", "ya'ni_bihi"),
    (re.compile(r"الصواب\s+(?:فيه|أن)"), "F8", "al-sawabu_fihi"),
    (re.compile(r"إنما\s+ي(?:قصد|ريد)"), "F8", "innama_yaqsidu"),
    (re.compile(r"الأظهر"), "F8", "al-azhar"),
    # F10 · Hipotetik (thought experiment)
    (re.compile(r"فرض(?:نا)?\s+(?:أن|أنه)"), "F10", "faradna_anna"),
    (re.compile(r"قدر(?:نا)?\s+(?:أن|أنه)"), "F10", "qaddarna_anna"),
]


@dataclass(frozen=True)
class DiscourseHit:
    """Yüzey örüntü taramasından bir vuruş."""

    pattern_id: str
    pattern_text: str  # eşleşen orijinal Arapça metin
    char_offset: tuple[int, int]
    candidate_label: str  # F1..F10


def scan_discourse_markers(text: str) -> list[DiscourseHit]:
    """Verilen metinde yukarıdaki örüntüleri tarar.

    Aynı örüntü birden fazla kez geçerse her geçiş ayrı bir hit.
    Hit'ler char_offset.start'a göre sıralı döner.
    """
    hits: list[DiscourseHit] = []
    for pat, label, pat_id in _PATTERNS:
        for m in pat.finditer(text):
            hits.append(
                DiscourseHit(
                    pattern_id=pat_id,
                    pattern_text=m.group(0),
                    char_offset=(m.start(), m.end()),
                    candidate_label=label,
                )
            )
    hits.sort(key=lambda h: h.char_offset[0])
    return hits
