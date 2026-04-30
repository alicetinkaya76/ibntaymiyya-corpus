"""CLI giriş noktası.

Kullanım:

    python -m pipeline.parser \\
        --input  data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1 \\
        --work-id MajmucFatawa \\
        --volume 7 \\
        --page-range V07P005:V07P459 \\
        --kitab "كتاب الإيمان" \\
        --output data/canonical/iman_v0.1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .openiti_parser import parse_file, units_to_json, PARSER_VERSION


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m pipeline.parser",
        description="OpenITI mARkdown → canonical JSON parser (İbn Teymiyye projesi)",
    )
    p.add_argument(
        "--input",
        required=True,
        help="OpenITI mARkdown dosyası yolu",
    )
    p.add_argument(
        "--work-id",
        required=True,
        choices=["MajmucFatawa", "Iman", "RisalaTadmuriyya"],
        help="Eserin kısa kimliği",
    )
    p.add_argument(
        "--volume",
        type=int,
        default=None,
        help="Sadece bu cildi izole et (Mecmû için 1-35)",
    )
    p.add_argument(
        "--page-range",
        type=str,
        default=None,
        help='"V07P005:V07P459" gibi sayfa aralığı',
    )
    p.add_argument(
        "--kitab",
        type=str,
        default=None,
        help="Çıkan birimlere yapıştırılacak kitâb başlığı (örn. كتاب الإيمان)",
    )
    p.add_argument(
        "--bab",
        type=str,
        default=None,
        help="Çıkan birimlere yapıştırılacak bâb başlığı",
    )
    p.add_argument(
        "--output",
        required=True,
        help="Çıktı JSON dosyası yolu",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="JSON çıktısını okunaklı (indented) yaz [varsayılan: True]",
    )
    p.add_argument(
        "--compact",
        dest="pretty",
        action="store_false",
        help="JSON çıktısını tek satırda yaz",
    )
    args = p.parse_args(argv)

    page_range_tuple = None
    if args.page_range:
        if ":" not in args.page_range:
            print(
                "[hata] --page-range 'V07P005:V07P459' biçiminde olmalı",
                file=sys.stderr,
            )
            return 2
        a, b = args.page_range.split(":", 1)
        page_range_tuple = (a.strip(), b.strip())

    print(f"[parser v{PARSER_VERSION}] {args.input} okunuyor...", file=sys.stderr)
    units = parse_file(
        args.input,
        work_id=args.work_id,
        volume=args.volume,
        page_range=page_range_tuple,
        kitab_label=args.kitab,
        bab_label=args.bab,
    )
    print(
        f"[parser] {len(units)} birim çıkarıldı "
        f"(section: {sum(1 for u in units if u.tier == 'section')}, "
        f"passage: {sum(1 for u in units if u.tier == 'passage')})",
        file=sys.stderr,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = units_to_json(units)
    indent = 2 if args.pretty else None
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=indent),
        encoding="utf-8",
    )
    print(f"[parser] {out_path} yazıldı.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
