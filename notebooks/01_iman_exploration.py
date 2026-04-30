# %% [markdown]
# # İbn Teymiyye · Iman el-Kebîr Pilot Keşfi
#
# **Hedef**: `data/canonical/iman_v0.1.json` üzerinde temel sağlık kontrolü.
# **Tarih**: 30 Nisan 2026 · **Faz**: 0 / Hafta 1
#
# Bu notebook **veri-görme** notebook'udur; F1-F10 sınıflandırması yapmaz.
# Sadece pilot çıktının yapısal sağlığını doğrular ve Hafta 2'ye yön verir.
#
# Kullanım:
# ```bash
# cd ibntaymiyya/
# jupyter nbconvert --to notebook --execute notebooks/01_iman_exploration.py
# # ya da VS Code'da .py dosyasını percent format olarak aç
# ```

# %%
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# %%
# Pilot JSON'ı yükle
DATA = Path(__file__).resolve().parent.parent / "data" / "canonical" / "iman_v0.1.json"
with DATA.open(encoding="utf-8") as f:
    units = json.load(f)

print(f"Toplam birim: {len(units)}")
sec = [u for u in units if u["tier"] == "section"]
pas = [u for u in units if u["tier"] == "passage"]
print(f"  Section: {len(sec)}")
print(f"  Passage: {len(pas)}")

# %% [markdown]
# ## 1 · Birim tipi (unit_type) dağılımı

# %%
type_counts = Counter(u["unit_type"] for u in units)
print(type_counts)

fig, ax = plt.subplots(figsize=(8, 4))
labels = list(type_counts.keys())
counts = list(type_counts.values())
ax.bar(labels, counts, color="#3a6a8c")
ax.set_title("Iman el-Kebîr (V07) · unit_type dağılımı")
ax.set_xlabel("unit_type")
ax.set_ylabel("Birim sayısı")
for i, c in enumerate(counts):
    ax.text(i, c + 1, str(c), ha="center")
plt.tight_layout()
plt.savefig("notebooks/figures/01_unit_type_distribution.png", dpi=120)
plt.show()

# %% [markdown]
# ## 2 · Passage kelime sayısı histogramı
#
# Hedef bant: 400-800 kelime (canonical_schema.md §4.2). Bunun dışına
# taşan birimler debug edilmeli.

# %%
passage_words = [u["word_count"] for u in pas]
fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(passage_words, bins=40, color="#7a8c3a", edgecolor="white")
ax.axvline(400, color="red", linestyle="--", alpha=0.6, label="alt hedef (400)")
ax.axvline(800, color="red", linestyle="--", alpha=0.6, label="üst hedef (800)")
ax.axvline(80, color="orange", linestyle=":", alpha=0.6, label="MIN (80)")
ax.axvline(1200, color="orange", linestyle=":", alpha=0.6, label="MAX (1200)")
ax.set_title("Passage kelime sayısı histogramı")
ax.set_xlabel("Kelime sayısı")
ax.set_ylabel("Passage sayısı")
ax.legend()
plt.tight_layout()
plt.savefig("notebooks/figures/02_passage_wordcount_hist.png", dpi=120)
plt.show()

# Aşma raporu
under_min = [u for u in pas if u["word_count"] < 80]
over_max = [u for u in pas if u["word_count"] > 1200]
print(f"MIN altı (<80 kel): {len(under_min)}")
print(f"MAX üstü (>1200 kel): {len(over_max)}")

# %% [markdown]
# ## 3 · V07 sayfa kapsama doğrulaması
#
# Beklenen aralık: V07P005-V07P459 (Iman el-Kebîr 455 sayfa).
# Kapsama tam olmalı; eksik sayfa varsa parser'da defekt vardır.

# %%
all_pages = set()
for u in units:
    for p in u.get("page_refs", []):
        all_pages.add(p)
v07 = sorted(p for p in all_pages if p.startswith("V07P"))
print(f"V07 kapsanan sayfa: {len(v07)}")
print(f"  En küçük: {v07[0]}")
print(f"  En büyük: {v07[-1]}")

# Beklenen aralık ile karşılaştır
expected = {f"V07P{i:03d}" for i in range(5, 460)}
covered = {p for p in v07}
missing = expected - covered
extra = covered - expected
print(f"Beklenen aralık (V07P005..V07P459): {len(expected)} sayfa")
print(f"Eksik sayfa: {len(missing)}")
if missing and len(missing) <= 20:
    print(f"  Eksikler: {sorted(missing)}")
print(f"Aralık dışı (ekstra): {len(extra)}")

# %% [markdown]
# ## 4 · Section uzunluk profili
#
# 12 section'ın kelime sayıları. Çok büyük section'lar (>10K) parser'ın
# `### |` başlığını seyrek bulduğu yerlerdir; bu beklenen ama dikkat
# edilmesi gereken bir durum.

# %%
sec_df = pd.DataFrame(
    [
        {
            "unit_id": s["unit_id"],
            "title": (s["title"] or "(başlıksız)")[:60],
            "word_count": s["word_count"],
            "page_start": s["page_refs"][0] if s["page_refs"] else "-",
            "page_end": s["page_refs"][-1] if s["page_refs"] else "-",
            "n_passages": sum(1 for u in pas if u["parent_unit_id"] == s["unit_id"]),
        }
        for s in sec
    ]
)
print(sec_df.to_string(index=False))

# %% [markdown]
# ## 5 · Söylem-yüzey örüntü (F1-F10) ön sayımı
#
# Hatırlatma: bu sayımlar **bağlayıcı değildir**. Yüzey örüntü taraması
# yalnızca Hafta 4'teki LLM zero-shot + human gold annotator için
# yumuşak ön etiket üretir.

# %%
label_counts = Counter()
for u in units:
    if u["tier"] == "passage":
        # passage'larda sayalım, section'larda da olduğu için çift sayma olmasın
        for m in u.get("discourse_markers", []):
            label_counts[m["candidate_label"]] += 1

print("Passage seviyesi F-marker dağılımı:")
for lbl in sorted(label_counts):
    print(f"  {lbl}: {label_counts[lbl]}")

fig, ax = plt.subplots(figsize=(8, 4))
labels = sorted(label_counts.keys())
counts = [label_counts[l] for l in labels]
ax.bar(labels, counts, color="#8c3a4a")
ax.set_title("Iman el-Kebîr · F-marker yüzey örüntü dağılımı (passage seviyesi)")
ax.set_xlabel("Aday F-etiketi")
ax.set_ylabel("Vuruş sayısı")
for i, c in enumerate(counts):
    ax.text(i, c + 0.5, str(c), ha="center")
plt.tight_layout()
plt.savefig("notebooks/figures/03_f_marker_distribution.png", dpi=120)
plt.show()

# %% [markdown]
# ## 6 · En uzun ve en kısa 5 passage
#
# Uç durumlar parser'ın doğru çalıştığının kanıtı: çok kısa olanlar
# muhtemelen kısa hadis aktarımı veya colophon; çok uzun olanlar
# tek paragraflık uzun argüman bloklarıdır.

# %%
sorted_pas = sorted(pas, key=lambda u: u["word_count"])
print("\nEN KISA 5 PASSAGE")
for u in sorted_pas[:5]:
    print(f"  {u['unit_id']}: {u['word_count']} kel | {u['full_text_arabic'][:80]}...")

print("\nEN UZUN 5 PASSAGE")
for u in sorted_pas[-5:]:
    print(f"  {u['unit_id']}: {u['word_count']} kel | {u['full_text_arabic'][:80]}...")

# %% [markdown]
# ## 7 · Kur'ân alıntı yoğunluğu
#
# Bir argümanın Kur'ân-yoğunluğu, Faz 4'te F1-F10 sınıflandırmasında
# özellik olarak kullanılabilir.

# %%
quran_per_passage = [len(u.get("quran_quotes", [])) for u in pas]
print(f"Toplam passage'da Kur'ân alıntı sayısı: {sum(quran_per_passage)}")
print(f"Ortalama / passage: {sum(quran_per_passage)/len(quran_per_passage):.2f}")
print(f"Max alıntılı passage: {max(quran_per_passage)} alıntı")

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(
    quran_per_passage,
    bins=range(0, max(quran_per_passage) + 2),
    color="#3a8c5a",
    edgecolor="white",
    align="left",
)
ax.set_title("Passage başına Kur'ân alıntı sayısı")
ax.set_xlabel("Alıntı sayısı")
ax.set_ylabel("Passage sayısı")
plt.tight_layout()
plt.savefig("notebooks/figures/04_quran_quote_density.png", dpi=120)
plt.show()

# %% [markdown]
# ## Özet ve Hafta 2 yön levhası
#
# - **Sayfa kapsamı tam**: V07P005-V07P459 hepsi var.
# - **Birim kompozisyonu sağlıklı**: 12 section + 150 passage.
# - **Passage uzunlukları hedef bantta**: çoğu 400-800 kelime arasında;
#   uçlar bilinçli paragraf-saygısı kararından kaynaklı.
# - **F-marker dağılımı zengin**: F4 (concession) ve F10 (hipotetik) yüksek;
#   F1 ve F2'nin yüzeyde nadir olması beklenen — bunlar bağlam-bağımlı,
#   LLM gerektirir.
# - **Kur'ân alıntıları yakalandı**: süslü parantez stili dominant;
#   Albani gibi modern editörler `@QB@..@QE@` kullanmıyor.
#
# Hafta 2'de:
# 1. Tedmuriyye + Standalone Iman parse'larını da kanonik JSON'a yaz.
# 2. Cross-corpus duplikasyon tespiti (Tedmuriyye = Mecmû V03'ün bir
#    bölümü mü?).
# 3. Hadis isnâd işaretleyicisini `hadith_markers` alanına doldur.
# 4. F1-F10 etiket setini Hüseyin Hoca ile kalibre et — pilot 30 passage
#    üzerinden gold annotation.
