"""Stable `unit_id` üretici.

`unit_id` formatı (canonical_schema.md §2.1):

    <work_code>-<volume?>-S<section_idx>[-P<passage_idx>]

Eserlerin kısa kodları:
- MF  : Mecmû'l-Fetâvâ
- IMN : Standalone Iman (Albani edisyonu)
- TDM : Tedmuriyye

Volume ön eki sadece çok-ciltli eserlerde kullanılır (şu an yalnızca MF).

ID'ler ESER-İÇİNDE STABİL'dir: parser çalıştırılınca eşit girdi → eşit ID.
Section'ın dosyadaki sırası değişirse ID de değişir; bu nedenle yeni
section eklenmesi (Faz 1 enrichment'ı) NUMARALAMAYI ETKİLEMEMELİDİR.
Bu nedenle Faz 1'de section sırası DEĞİŞMEDEN sadece içerik metadata'sı
zenginleşir.
"""

from __future__ import annotations

WORK_CODES: dict[str, str] = {
    "MajmucFatawa": "MF",
    "Iman": "IMN",
    "RisalaTadmuriyya": "TDM",
}


def get_work_code(work_id: str) -> str:
    """Eser id'sinden kısa kod döner.

    Bilinmeyen `work_id` için `ValueError` fırlatır — yeni bir eser
    eklenirken bu eşleştirmenin açıkça yapılmasını zorunlu kılmak için.
    """
    if work_id not in WORK_CODES:
        raise ValueError(
            f"Bilinmeyen work_id={work_id!r}. id_generator.WORK_CODES sözlüğüne "
            f"yeni bir eşleştirme ekle."
        )
    return WORK_CODES[work_id]


def section_id(
    work_id: str,
    section_index: int,
    volume: int | None = None,
) -> str:
    """Section seviyesi unit_id'si üretir.

    >>> section_id("MajmucFatawa", 3, volume=7)
    'MF-V07-S03'
    >>> section_id("RisalaTadmuriyya", 5)
    'TDM-S05'
    """
    code = get_work_code(work_id)
    parts = [code]
    if volume is not None:
        parts.append(f"V{volume:02d}")
    parts.append(f"S{section_index:02d}")
    return "-".join(parts)


def passage_id(
    work_id: str,
    section_index: int,
    passage_index: int,
    volume: int | None = None,
) -> str:
    """Passage seviyesi unit_id'si üretir.

    >>> passage_id("MajmucFatawa", 3, 12, volume=7)
    'MF-V07-S03-P012'
    >>> passage_id("Iman", 0, 4)
    'IMN-S00-P004'
    """
    base = section_id(work_id, section_index, volume=volume)
    return f"{base}-P{passage_index:03d}"
