"""CLI: ``python -m pipeline.crosscorpus``."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from .pair_extractor import find_pairs, load_units, save_pairs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-corpus duplikasyon eşleşmesi tarayıcı"
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--method",
        choices=["tfidf_char", "tfidf_word", "shingle_jaccard"],
        default="tfidf_char",
    )
    parser.add_argument("--threshold", type=float, default=0.3)
    parser.add_argument("--topk", type=int, default=3)
    parser.add_argument("--no-quran-aware", action="store_true")
    parser.add_argument("--min-words", type=int, default=30)

    args = parser.parse_args(argv)

    print(f"Kaynak: {args.source}")
    sources = load_units(args.source)
    print(f"  → {len(sources)} birim")

    print(f"Hedef: {args.target}")
    targets = load_units(args.target)
    print(f"  → {len(targets)} birim")

    print(
        f"method={args.method} threshold={args.threshold} "
        f"topk={args.topk} quran_aware={not args.no_quran_aware}"
    )
    pairs = find_pairs(
        sources, targets,
        method=args.method,
        threshold=args.threshold,
        topk=args.topk,
        quran_aware=not args.no_quran_aware,
        min_words=args.min_words,
    )

    metadata = {
        "source_file": str(args.source),
        "target_file": str(args.target),
        "method": args.method,
        "threshold": args.threshold,
        "topk": args.topk,
        "quran_aware": not args.no_quran_aware,
        "min_words": args.min_words,
        "n_source": len(sources),
        "n_target": len(targets),
        "n_pairs": len(pairs),
        "extracted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    print(f"Bulunan çift: {len(pairs)}")
    if pairs:
        print(f"Skor: min={pairs[-1].similarity:.3f} max={pairs[0].similarity:.3f}")

    save_pairs(pairs, args.output, metadata=metadata)
    print(f"Yazıldı: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
