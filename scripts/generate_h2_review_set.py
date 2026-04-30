"""H2 sonuçlarından Hüseyin Hoca için stratified örnek üretir.

Skor bantlarından eşit sayıda örnek alır, her örnek için kaynak ve hedef
pasajların gövdelerini yan yana yazar.
"""

import json
import random
from pathlib import Path

random.seed(42)


def load_canonical(path: str) -> dict:
    return {u["unit_id"]: u for u in json.loads(Path(path).read_text())}


def truncate(text: str, n: int = 800) -> str:
    if len(text) <= n:
        return text
    return text[:n] + " […]"


def main():
    pairs = json.loads(
        Path("data/derived/cross_corpus_h2_tfidf_char_v0.1.json").read_text()
    )["pairs"]
    iman = load_canonical("data/canonical/iman_v0.1.json")
    iman_st = load_canonical("data/canonical/iman_standalone_v0.1.json")

    top1 = {}
    for p in pairs:
        sid = p["source_unit_id"]
        if sid not in top1 or p["similarity"] > top1[sid]["similarity"]:
            top1[sid] = p
    top1_list = sorted(top1.values(), key=lambda p: -p["similarity"])

    bands = [
        (0.95, 1.01, 5, "Çok yüksek (likely birebir)"),
        (0.80, 0.95, 5, "Yüksek (büyük ihtimal düzenlenmiş tekrar)"),
        (0.60, 0.80, 10, "Orta-yüksek (paragraf ortak, paraphrase olabilir)"),
        (0.40, 0.60, 5, "Orta (parça ortak, asıl iddia farklı olabilir)"),
        (0.30, 0.40, 5, "Düşük (gürültü mü gerçek mi?)"),
    ]

    selected = []
    for lo, hi, n, label in bands:
        candidates = [p for p in top1_list if lo <= p["similarity"] < hi]
        sampled = random.sample(candidates, min(n, len(candidates)))
        for p in sampled:
            p["band_label"] = label
        selected.extend(sampled)

    out = ["# H2 Cross-Corpus — Manuel Doğrulama Seti\n"]
    out.append("**Oluşturma:** otomatik · `scripts/generate_h2_review_set.py`\n")
    out.append("**Kaynak:** `data/derived/cross_corpus_h2_tfidf_char_v0.1.json`\n")
    out.append("**Yöntem:** TF-IDF char_wb (3,5) + cosine, Kur'ân ayetleri maskeli, top-1 per source\n")
    out.append("**Stratified sampling:** 5 skor bandından (5+5+10+5+5)\n\n")
    out.append("## Doğrulama protokolü\n")
    out.append(
        "Hüseyin Hoca: her çift için aşağıdaki sınıflardan birini seç:\n"
        "- **EXACT**: Birebir tekrar (kelimelik farklar olabilir, ama aynı pasaj)\n"
        "- **EDITED**: Albani edisyonu — kelime/sıra değişiklikleri ama aynı argüman\n"
        "- **EXCERPT**: Hedef, kaynağın bir kısmı (özet veya alıntı)\n"
        "- **OVERLAP**: Ortak konu/ortak ayet, ama farklı argüman\n"
        "- **NOISE**: Yanlış eşleşme — algoritma yanılmış\n\n"
        "Sonuç eşik kalibrasyonu için kullanılacak (S4'te).\n\n"
    )
    out.append("---\n\n")

    for i, p in enumerate(selected, 1):
        src = iman[p["source_unit_id"]]
        tgt = iman_st[p["target_unit_id"]]
        out.append(
            f"## {i:02d}. {p['source_unit_id']} ↔ {p['target_unit_id']}\n\n"
            f"**Bant:** {p['band_label']}  \n"
            f"**Skor:** {p['similarity']:.3f}  ·  "
            f"**Düzeltilmiş:** {p['adjusted_similarity']:.3f}  \n"
            f"**Kur'ân yoğunluğu:** kaynak={p['quran_density_source']:.2f}, "
            f"hedef={p['quran_density_target']:.2f}  \n"
            f"**Kelime sayısı:** kaynak={src['word_count']}, hedef={tgt['word_count']}  \n"
            f"**Sayfalar:** kaynak={src['page_refs'][0] if src['page_refs'] else '?'}"
            f"–{src['page_refs'][-1] if src['page_refs'] else '?'} · "
            f"hedef={tgt['page_refs'][0] if tgt['page_refs'] else '?'}"
            f"–{tgt['page_refs'][-1] if tgt['page_refs'] else '?'}\n\n"
            f"### Kaynak (Mecmû V07 / İbn Kāsım)\n\n"
            f"```\n{truncate(src['full_text_arabic'])}\n```\n\n"
            f"### Hedef (Standalone Iman / Albani)\n\n"
            f"```\n{truncate(tgt['full_text_arabic'])}\n```\n\n"
            f"### Karar (Hüseyin Hoca için)\n\n"
            f"- [ ] EXACT  - [ ] EDITED  - [ ] EXCERPT  - [ ] OVERLAP  - [ ] NOISE\n"
            f"- **Notlar:**\n\n"
            f"---\n\n"
        )

    out_path = Path("docs/cross_corpus/h2_pairs_for_review.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(out), encoding="utf-8")
    print(f"Yazıldı: {out_path}")
    print(f"Toplam çift: {len(selected)}")
    for lo, hi, _, label in bands:
        in_band = sum(1 for p in selected if lo <= p["similarity"] < hi)
        print(f"  Bant [{lo:.2f}, {hi:.2f}) — {label}: {in_band} çift")


if __name__ == "__main__":
    main()
