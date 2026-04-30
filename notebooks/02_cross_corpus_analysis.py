# %% [markdown]
# # 02 · Cross-Corpus H2 Analizi
#
# **Hipotez (H2):** Standalone Iman (Albani edisyonu), Mecmû V07'deki
# Iman el-Kebîr'in farklı bir editör tarafından düzenlenmiş halidir.
#
# **Yöntem:** TF-IDF char_wb (3,5) + cosine. Kur'ân alıntıları maskelenir.
#
# **Çalıştırma:** `python notebooks/02_cross_corpus_analysis.py`

# %%
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.crosscorpus import (
    TFIDFCrossCorpusComparator,
    find_pairs,
    normalize_arabic,
    quran_density,
    strip_quran_quotes,
)
from pipeline.crosscorpus.pair_extractor import load_units

DATA = ROOT / "data" / "canonical"
DERIVED = ROOT / "data" / "derived"
FIGS = ROOT / "notebooks" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

# %%
iman = load_units(DATA / "iman_v0.1.json")
iman_st = load_units(DATA / "iman_standalone_v0.1.json")
tdm = load_units(DATA / "tedmuriyye_v0.1.json")

print(f"Iman el-Kebîr (Mecmû V07):     {len(iman):>4} birim")
print(f"Standalone Iman (Albani):       {len(iman_st):>4} birim")
print(f"Risale Tedmuriyye:              {len(tdm):>4} birim")

# %% [markdown]
# ## Kur'ân-yoğunluk tarama

# %%
iman_pas = [u for u in iman if u["tier"] == "passage"]
iman_st_pas = [u for u in iman_st if u["tier"] == "passage"]

iman_density = [
    quran_density(u["full_text_arabic"], u.get("quran_quotes") or [])
    for u in iman_pas
]
iman_st_density = [
    quran_density(u["full_text_arabic"], u.get("quran_quotes") or [])
    for u in iman_st_pas
]

print("Kur'ân-yoğunluk istatistik:")
print(f"  Iman el-Kebîr:    medyan={np.median(iman_density):.3f}  ort={np.mean(iman_density):.3f}")
print(f"  Standalone Iman:  medyan={np.median(iman_st_density):.3f}  ort={np.mean(iman_st_density):.3f}")

# %%
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(iman_density, bins=20, color="#3a6ea5")
ax[0].set_title("Iman el-Kebîr · Kur'ân yoğunluğu")
ax[0].set_xlabel("density (0–1)")
ax[0].set_ylabel("passage")
ax[1].hist(iman_st_density, bins=20, color="#a53a3a")
ax[1].set_title("Standalone Iman · Kur'ân yoğunluğu")
ax[1].set_xlabel("density (0–1)")
plt.tight_layout()
plt.savefig(FIGS / "02_quran_density.png", dpi=120, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## H2 testi · TF-IDF char_wb (3,5) baseline

# %%
pairs = find_pairs(
    iman, iman_st,
    method="tfidf_char", threshold=0.3, topk=3, quran_aware=True,
)
print(f"Toplam pair: {len(pairs)}")
print(f"En yüksek: {pairs[0].similarity:.3f}  En düşük: {pairs[-1].similarity:.3f}")

# %%
similarities = [p.similarity for p in pairs]
adjusted = [p.adjusted_similarity for p in pairs]

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(similarities, bins=20, color="#3a6ea5")
ax[0].axvline(0.5, color="grey", ls="--", lw=0.7, label="threshold önerisi")
ax[0].set_xlabel("similarity")
ax[0].set_ylabel("pair sayısı")
ax[0].set_title("Ham TF-IDF char skoru")
ax[0].legend()
ax[1].hist(adjusted, bins=20, color="#a55a3a")
ax[1].axvline(0.5, color="grey", ls="--", lw=0.7)
ax[1].set_xlabel("adjusted similarity")
ax[1].set_title("Kur'ân-yoğunluk düzeltilmiş skor")
plt.tight_layout()
plt.savefig(FIGS / "02_similarity_histogram.png", dpi=120, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Coverage matrisi (heatmap)

# %%
src_texts = [normalize_arabic(strip_quran_quotes(u["full_text_arabic"], u.get("quran_quotes") or [])) for u in iman_pas]
tgt_texts = [normalize_arabic(strip_quran_quotes(u["full_text_arabic"], u.get("quran_quotes") or [])) for u in iman_st_pas]

c = TFIDFCrossCorpusComparator(analyzer="char_wb", ngram_range=(3, 5), min_df=2)
c.fit(src_texts, tgt_texts)
sim_mat = c.similarity_matrix

fig, ax = plt.subplots(figsize=(10, 9))
im = ax.imshow(sim_mat, aspect="auto", cmap="viridis", vmin=0, vmax=1)
ax.set_xlabel("Standalone Iman passage idx")
ax.set_ylabel("Iman el-Kebîr passage idx")
ax.set_title("H2 · TF-IDF char_wb cosine matrisi")
plt.colorbar(im, ax=ax, label="similarity")
plt.tight_layout()
plt.savefig(FIGS / "02_similarity_heatmap.png", dpi=120, bbox_inches="tight")
plt.show()

# %% [markdown]
# **Beklenen pattern:** Albani Mecmû V07'yi sıraya göre işlediyse, diagonal görünür.

# %% [markdown]
# ## Üç method top-1 uyumu

# %%
methods = {}
for name, kwargs in [
    ("tfidf_char", {"method": "tfidf_char", "threshold": 0.3}),
    ("tfidf_word", {"method": "tfidf_word", "threshold": 0.3}),
    ("shingle", {"method": "shingle_jaccard", "threshold": 0.1}),
]:
    p = find_pairs(iman, iman_st, topk=1, quran_aware=True, **kwargs)
    methods[name] = {x.source_unit_id: x.target_unit_id for x in p}

common = set(methods["tfidf_char"]) & set(methods["tfidf_word"]) & set(methods["shingle"])
n = len(common)
agree_cw = sum(1 for s in common if methods["tfidf_char"][s] == methods["tfidf_word"][s])
agree_cs = sum(1 for s in common if methods["tfidf_char"][s] == methods["shingle"][s])
agree_all = sum(1 for s in common if methods["tfidf_char"][s] == methods["tfidf_word"][s] == methods["shingle"][s])
print(f"Üç method'da da top-1 olan source: {n}")
print(f"  char ≡ word:    {agree_cw}/{n}  ({100*agree_cw/n:.1f}%)")
print(f"  char ≡ shingle: {agree_cs}/{n}  ({100*agree_cs/n:.1f}%)")
print(f"  üçü birden:     {agree_all}/{n}  ({100*agree_all/n:.1f}%)")

# %% [markdown]
# ## Coverage özeti

# %%
top1_per_source = {}
for p in pairs:
    sid = p.source_unit_id
    if sid not in top1_per_source or p.similarity > top1_per_source[sid].similarity:
        top1_per_source[sid] = p

n_passage_src = len(iman_pas)
covered_03 = sum(1 for p in top1_per_source.values() if p.similarity >= 0.3)
covered_05 = sum(1 for p in top1_per_source.values() if p.similarity >= 0.5)
covered_07 = sum(1 for p in top1_per_source.values() if p.similarity >= 0.7)
covered_09 = sum(1 for p in top1_per_source.values() if p.similarity >= 0.9)
adj_05 = sum(1 for p in top1_per_source.values() if p.adjusted_similarity >= 0.5)

print("Mecmû V07 Iman el-Kebîr passage coverage:")
print(f"  Toplam passage:                    {n_passage_src}")
print(f"  En az 1 match (skor ≥ 0.3):        {covered_03} ({100*covered_03/n_passage_src:.1f}%)")
print(f"  Skor ≥ 0.5:                         {covered_05} ({100*covered_05/n_passage_src:.1f}%)")
print(f"  Skor ≥ 0.7 (yüksek güven):          {covered_07} ({100*covered_07/n_passage_src:.1f}%)")
print(f"  Skor ≥ 0.9 (likely birebir):        {covered_09} ({100*covered_09/n_passage_src:.1f}%)")
print(f"  Adjusted ≥ 0.5 (Kur'ân-bağımsız):   {adj_05} ({100*adj_05/n_passage_src:.1f}%)")

# %%
print(f"\nÇalıştırma tamamlandı.\nFigürler: {FIGS}")
