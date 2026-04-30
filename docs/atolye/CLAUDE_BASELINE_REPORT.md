# Claude 4.7 Baseline Annotator — H2 Review Set Etiketleri

**Annotator:** `claude_4_7_baseline`
**Tarih:** 30 Nisan 2026
**Yöntem:** Her pair'in tam metni (`docs/cross_corpus/h2_pairs_for_review.md`) okundu, sadece metin örtüşmesine bakılarak karar verildi. Skor ve bant bilgisi ikincil tutuldu (ama bias farkındalığıyla — bkz. *Sınırlamalar*).

---

## Özet sınıf dağılımı

```
EXACT   :  2  ██
EDITED  :  8  ████████
EXCERPT :  0  
OVERLAP : 16  ████████████████
NOISE   :  0  
```

| Kategori | Sayı | Oran |
|---|---|---|
| True positive (EXACT/EDITED/EXCERPT) | 10/26 | 38.5% |
| Borderline (OVERLAP) | 16/26 | 61.5% |
| Algoritma yanılması (NOISE) | 0/26 | 0.0% |

---

## Bant × etiket çapraz tablosu

| Bant | EXACT | EDITED | EXCERPT | OVERLAP | NOISE |
|---|---|---|---|---|---|
| Çok yüksek (≥0.95) | 0 | **5** | 0 | 0 | 0 |
| Yüksek (0.80–0.95) | 2 | 2 | 0 | 1 | 0 |
| Orta-yüksek (0.60–0.80) | 0 | 0 | 0 | **10** | 0 |
| Orta (0.40–0.60) | 0 | 1 | 0 | 4 | 0 |
| Düşük (0.30–0.40) | 0 | 0 | 0 | 1 | 0 |

---

## Bulgular (Hüseyin Hoca tahkimi öncesi gözlemler)

### 1. Çok yüksek bant (≥0.95) %100 isabetli

5/5 pair gerçek paralel pasaj — hepsi **EDITED** (Albani'nin editöryel müdahaleleri: fasıl başlıkları çıkarılmış, ön cümlecikler atılmış, ama metin gövdesi birebir kopya). **Hiç EXACT yok** — Albani her pasajda en azından küçük bir editöryel değişiklik yapmış.

### 2. Yüksek bant (0.80–0.95) çoğunlukla isabetli

5 pair: 2 EXACT (pair 8 ve 10 — birebir aynı, sadece referans bracket farkı), 2 EDITED, 1 OVERLAP. **Tek false positive: pair 9** (0.824) — algoritma kelime ortaklığını yakalamış ama farklı pasaj.

### 3. Orta-yüksek bant (0.60–0.80) %100 OVERLAP

10/10 pair OVERLAP. Bu bant **algoritmanın "false positive" zonu** — kaynak ve hedef metinler aynı geniş konuda (iman, İslâm, küfür, münafık, amel) ama farklı argümanlar/farklı pasajlar. Algoritma yüksek char n-gram örtüşmesinden yüksek skor veriyor ama metinler aynı pasaj değil.

### 4. **Pair 21 — değerli false negative örneği**

Pair 21 (`MF-V07-S00-P023 ↔ IMN-S00-P025`, skor **0.504**, orta bantta) **gerçek paralel** ve **EDITED** olarak işaretlendi.

Kaynak passage 152 kelime ile çok kısa, sonu yarıda kesilmiş ("وإذا كان كذلك ف..."). Hedef passage'ın ilk cümlesi ("فتلك الشفاعة هي لأهل الإخلاص...") kaynağın yarıda kesilen sonuyla **birebir aynı** — Albani kaynaktaki passage sınırını yeniden çizip iki Mecmû passage'ını tek pasaj olarak birleştirmiş.

**Bu pair'in önemi:** Algoritmanın yakalayamadığı türden bir paralel — kısa kaynak + uzun hedef → düşük TF-IDF skoru. Threshold kalibrasyonunda bu pair "false negative" olarak hesaba katılmalı; eğer threshold ≥ 0.80 alınırsa bu tür pair'ler kaçırılır.

### 5. Düşük bant (0.30–0.40) — algoritma sınırı

Pair 26 (skor 0.395) OVERLAP — ikisi de Ahmad'dan nakil ama farklı pasajlar. Algoritma ortak kelime kümesini (Ahmad, iman, İslâm) yakalamış ama gerçek paralel değil. Bu bant zaten zayıf, threshold seçiminde aşağı sınır olarak makul.

### 6. EXCERPT etiketi hiç kullanılmadı

26 pair'de **hiç EXCERPT yok**. Bu, Albani'nin Mecmû'dan "özet" yapmadığını gösteriyor — ya pasajları tam alıp düzenliyor (EDITED), ya da farklı pasajlardan paralel argümanlar üretiyor (OVERLAP). Bu paper için ilginç bir bulgu: **Albani edisyonu kısaltma değil yeniden düzenleme** (S3'te bulduğumuz "kelime hacmi neredeyse eşit" tespitiyle uyumlu).

### 7. NOISE etiketi hiç kullanılmadı

Algoritma 26 pair'in hiçbirinde "tamamen alakasız" eşleşme üretmemiş. En zayıf pair (pair 26) bile aynı tematik alanda. Bu, TF-IDF char_wb baseline'ının **konu-düzeyinde** çok güvenilir olduğunu gösteriyor — sadece pasaj-düzeyi paralelliği ayırt etmekte zorlanıyor.

---

## Threshold kalibrasyonu önerisi (Claude baseline'a göre)

| Strateji | Threshold | TP | FP (OVERLAP) | FN | Notu |
|---|---|---|---|---|---|
| **Yüksek precision** | ≥ 0.85 | 9 | 1 | 1 | Pair 21 kaçar |
| **F1-optimal** | ≥ 0.80 | 9 | 1 | 1 | Aynı |
| **Recall-priority** | ≥ 0.40 | 10 | 15 | 0 | Pair 21 yakalanır ama OVERLAP'lar gelir |
| **Sadece confidence-1** | ≥ 0.95 | 5 | 0 | 5 | Çok temkinli |

**Tavsiye:** Yüksek precision threshold (≥0.85) + manual review of "borderline" zone (0.50–0.85). Pair 21 gibi düşük-skorlu gerçek paraleller için **adjusted similarity** veya **alternatif metric** (örn. shingle Jaccard skor + Mecmû passage'ı kısa+yarı-kesik kontrolü) gerekli.

---

## Sınırlamalar (Hüseyin Hoca tahkimi için kritik)

1. **Skor görüldü, bias riski:** Yüksek skorlu pair'lerde EXACT/EDITED'a doğru çekim olabilir. Notlardaki gerekçelerime bakıp Hüseyin Hoca tahkim edebilir. Özellikle pair 9 (0.824) için OVERLAP kararım — yüksek skoru gözardı edip sadece metne bakarak verildi, doğru olmayabilir.

2. **Tek-rater uyum sorunu:** Bu çıktı Cohen κ için **second-rater baseline** olarak tasarlandı. Hüseyin Hoca'nın etiketleri otoritedir; benim etiketim makine taban değeri.

3. **OVERLAP/EDITED sınırı:** Bazı pair'ler için (özellikle pair 18 — Tevbe 73-74 ardışık ayetleri) OVERLAP/EDITED kararı zor. Hüseyin Hoca farklı yorumlayabilir.

4. **EXCERPT'in hiç kullanılmaması olağandışı:** 26 pair'de hiç "özet" çıkmadı. Hüseyin Hoca bazı orta-yüksek bant pair'lerde EXCERPT yorumlayabilir (özellikle pair 12 — kaynak passage'ın kısa, hedef passage'ın uzun olduğu durumlar).

---

## Cohen κ kullanımı (S5'te)

Hüseyin Hoca'nın etiketleri `data/annotations/h2_review/huseyin_gokalp_*.json`'a kaydedildiğinde:

```python
from pipeline.crosscorpus import (
    load_annotation_set, cohen_kappa, confusion_matrix, list_annotation_sets
)

sets = list_annotation_sets("data/annotations/h2_review")
claude = load_annotation_set([s for s in sets if "claude" in s.name][0])
huseyin = load_annotation_set([s for s in sets if "huseyin" in s.name][0])

k = cohen_kappa(claude.annotations, huseyin.annotations)
print(f"Cohen κ (Claude ↔ Hüseyin Gökalp) = {k:.3f}")

# Hangi pair'lerde uyuşmadık
cm = confusion_matrix(claude.annotations, huseyin.annotations)
for (label_c, label_h), n in sorted(cm.items(), key=lambda x: -x[1]):
    if label_c != label_h:
        print(f"  Claude: {label_c.value:<7} → Hüseyin: {label_h.value:<7} : {n} pair")
```

**Beklentim:** κ ∈ [0.4, 0.7] (orta-substantial). Yüksek bantta uyum yüksek olur (5'te 5), orta-yüksek bantta Hüseyin Hoca bazı OVERLAP'ları farklı yorumlayabilir.

---

## Paper material için bulgular

1. **LLM-as-second-rater feasibility:** Claude 4.7 26 pair'i ~5-10 dakikada okuyup tutarlı etiketler üretti (notes alanında her etiketin metin-temelli gerekçesi var).

2. **Algoritmanın topology'si net:**
   - ≥0.95: %100 isabet (5/5 EDITED)
   - 0.80–0.95: %80 isabet (4/5 TP, 1 OVERLAP)
   - 0.60–0.80: %0 isabet (10/10 OVERLAP — false positive zone)
   - 0.40–0.60: bir gerçek pair var (pair 21 — false negative zone)
   - 0.30–0.40: OVERLAP

3. **Albani edisyonunun karakteri:** EXCERPT etiketi hiç çıkmadı, EDITED hakim → Albani **kısaltma yapmıyor, editöryel müdahale yapıyor** (bkz. S3'teki "%3 kelime hacim farkı" bulgusu).
