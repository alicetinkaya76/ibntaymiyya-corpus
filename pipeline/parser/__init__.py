"""İbn Teymiyye Tutum Haritalama Sistemi · OpenITI parser.

Public API:

    from pipeline.parser import parse_file, units_to_json, Unit

    units = parse_file(
        "data/raw/openiti/0728IbnTaymiyya.MajmucFatawa.Shamela0007289-ara1",
        work_id="MajmucFatawa",
        volume=7,
        page_range=("V07P005", "V07P459"),
        kitab_label="كتاب الإيمان",
    )

    import json
    Path("data/canonical/iman_v0.1.json").write_text(
        json.dumps(units_to_json(units), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
"""

from .schema import (
    DiscourseMarker,
    EditorMeta,
    ExtractionMeta,
    FutureLinks,
    HadithMarker,
    QuranQuote,
    TopicLabels,
    Unit,
)
from .openiti_parser import parse_file, units_to_json, PARSER_VERSION

__all__ = [
    "parse_file",
    "units_to_json",
    "PARSER_VERSION",
    "Unit",
    "QuranQuote",
    "HadithMarker",
    "DiscourseMarker",
    "EditorMeta",
    "ExtractionMeta",
    "FutureLinks",
    "TopicLabels",
]

__version__ = "0.1.0"
