"""Üst seviye OpenITI parser orchestration.

Diğer alt modülleri birleştirip tek bir `parse_file()` çağrısıyla
kanonik birim listesini üretir.

Kullanım:

    from pipeline.parser import parse_file

    units = parse_file(
        path="data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1",
        work_id="MajmucFatawa",
        volume=7,
        page_range=("V07P005", "V07P459"),
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .schema import EditorMeta, Unit
from .tokenizer import iter_logical_lines, read_raw_lines, merge_continuations
from .header_parser import MetadataHeader, detect_notation_style
from .tree_builder import build_tree, extract_volume_range
from .page_extractor import find_logical_line_for_page, parse_page_code
from .unit_extractor import extract_units


PARSER_VERSION = "0.1.0"


def parse_file(
    path: str | Path,
    *,
    work_id: str,
    volume: Optional[int] = None,
    page_range: Optional[tuple[str, str]] = None,
    kitab_label: Optional[str] = None,
    bab_label: Optional[str] = None,
    source_edition_note: Optional[str] = None,
) -> list[Unit]:
    """Bir OpenITI dosyasını parse edip kanonik birim listesi döner.

    Parameters
    ----------
    path
        OpenITI mARkdown dosyasının yolu.
    work_id
        Eserin kısa kimliği (`MajmucFatawa`, `Iman`, `RisalaTadmuriyya`).
    volume
        Çok-ciltli eserlerde sadece bu cildi izole et. Standalone
        risâlelerde `None`.
    page_range
        `(start_code, end_code)` örn. `("V07P005", "V07P459")`. Eğer
        verilirse, **bu sayfa aralığı içindeki birimler** çıkarılır
        (volume parametresinin ek-filtresi olarak çalışır).
    kitab_label
        Çıkan birimlere `kitab` alanı olarak yapıştırılacak metin.
        Örn. Mecmû V07'de `"كتاب الإيمان"`.
    bab_label
        Benzer şekilde, `bab` alanı.
    source_edition_note
        `editor_meta` ile eşleşen kısa Türkçe açıklama. Verilmezse
        otomatik üretilir.

    Returns
    -------
    list[Unit]
        Section ve passage tier'larında, sıralı kanonik birim listesi.
    """
    path = Path(path)
    raw_lines = read_raw_lines(path)
    logical = merge_continuations(raw_lines)

    # 1. Metadata header'ı çıkar
    header = MetadataHeader.from_raw_lines(raw_lines)

    # body başlangıç index'i
    body_start_idx = 0
    for i, ln in enumerate(logical):
        if ln.kind == "meta_end":
            body_start_idx = i + 1
            break

    # 2. Cilt aralığını izole et (varsa)
    vol_start_idx = body_start_idx
    vol_end_idx = len(logical)
    if volume is not None:
        try:
            vol_start_idx, vol_end_idx = extract_volume_range(logical, volume)
        except ValueError:
            # Cilt bulunamadıysa tüm gövdeye fall-back
            pass

    # 3. Sayfa aralığı (varsa) cilt sınırı içinde daralt
    page_start_idx = vol_start_idx
    page_end_idx = vol_end_idx
    if page_range is not None:
        sc, ec = page_range
        ps = parse_page_code(sc)
        pe = parse_page_code(ec)
        if ps is None or pe is None:
            raise ValueError(f"Geçersiz page_range: {page_range}")
        sv, sp = ps
        ev, ep = pe
        # Hedef sayfaları bul
        idx_start = find_logical_line_for_page(
            logical, sv, sp, vol_start_idx, vol_end_idx
        )
        idx_end = find_logical_line_for_page(
            logical, ev, ep, vol_start_idx, vol_end_idx
        )
        if idx_start != -1:
            page_start_idx = idx_start
        if idx_end != -1:
            # idx_end o sayfayı işaret eden satır; bir sonraki sayfaya
            # kadar olan içerik dahil edilmeli. Yani idx_end'in birkaç
            # satır sonrasına kadar git.
            page_end_idx = idx_end
            # Ek: end sayfası DAHİL edilmeli — bir sonraki sayfa kodu
            # gelene kadar tarayalım
            for j in range(idx_end + 1, vol_end_idx):
                ln = logical[j]
                if ln.kind == "page":
                    code_parsed = parse_page_code(ln.text.strip())
                    if code_parsed is not None and code_parsed != (ev, ep):
                        page_end_idx = j
                        break
            else:
                page_end_idx = vol_end_idx

    # 4. Düz section listesini inşa et (cilt+sayfa filtreli aralıkta)
    sections = build_tree(logical, body_start_idx=page_start_idx)
    # `build_tree` body_start_idx'ten dosya sonuna kadar tarar; bizim
    # asıl ilgilendiğimiz `page_end_idx`'e kadar olan kısım. Filtreleyelim.
    sections = [
        s
        for s in sections
        if s.body_start_idx <= page_end_idx and s.line_no <= logical[
            min(page_end_idx - 1, len(logical) - 1)
        ].line_no_start
    ]
    # Son section'ın body_end_idx'i page_end_idx'i aşmasın
    for s in sections:
        if s.body_end_idx > page_end_idx:
            s.body_end_idx = page_end_idx

    # 5. Editör metadata'sını oluştur
    sample_text = " ".join(
        l.text for l in logical[body_start_idx : body_start_idx + 100]
    )
    notation = detect_notation_style(header, sample_text)
    editor_meta = EditorMeta(
        editor_name=header.editor_name,
        publisher=header.publisher,
        publication_year=header.publication_year,
        notation_style=notation,  # type: ignore[arg-type]
    )
    if source_edition_note is None:
        parts = []
        if header.publisher:
            parts.append(header.publisher.split("،")[0])
        if header.publication_year:
            parts.append(header.publication_year)
        source_edition_note = "Şâmile bsk., " + (", ".join(parts) if parts else "edisyon bilgisi yok")

    # 6. Birimleri çıkar
    units = extract_units(
        work_id=work_id,
        openiti_uri=path.name,
        logical_lines=logical,
        sections=sections,
        editor_meta=editor_meta,
        source_edition_note=source_edition_note,
        parser_version=PARSER_VERSION,
        volume=volume,
        kitab_label=kitab_label,
        bab_label=bab_label,
    )
    return units


def units_to_json(units: list[Unit]) -> list[dict]:
    """Pydantic listesini ham dict listesine çevirir (JSON serialization)."""
    return [u.model_dump(mode="json") for u in units]
