"""Claude (4.7) baseline annotator — 26 H2 review pair için etiket kaydı.

Bu script, Hüseyin Hoca'nın atölyede yapacağı manuel etiketlemeye
**second-rater (LLM baseline)** olarak ekleniyor. Otorite Hüseyin
Hoca'da kalır — bu sadece Cohen κ ölçümü için karşılaştırma noktası.

Annotator: claude_4_7_baseline
Yöntem: Her pair'in tam metnini okuyarak (h2_pairs_for_review.md), bant
ve skor bilgisini İKİNCİL tutarak, sadece metin örtüşmesine bakarak
karar verme.

Bias farkındalığı: Skorlar görüldü, bu yüksek skorda EXACT/EDITED'a
doğru bias yaratabilir. Notlarda her etiketin gerekçesi belirtildi.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, ".")

from pipeline.crosscorpus.annotation_schema import (
    AnnotationSet, LabelKind, PairAnnotation,
    save_annotation_set,
)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# (source_id, target_id, label, notes_tr)
DECISIONS = [
    # ===== ÇOK YÜKSEK BANT (0.95+) =====
    ("MF-V07-S09-P021", "IMN-S00-P132", LabelKind.EDITED,
     "Albani giriş cümlesini ('قلت: لفظ المجمل والمطلق...') atmış, "
     "'ليست مما لا يفهم المراد به...' sonrası birebir aynı. Sonunda "
     "Albani daha geniş devam içeriği ekliyor."),
    ("MF-V07-S08-P005", "IMN-S00-P105", LabelKind.EDITED,
     "Kaynak 'فصل: ومما يسأل عنه...' fasıl başlığıyla açılıyor; hedef "
     "'والتحقيق أن النبي...' sonrasını birebir alıyor. Albani başlığı + "
     "ön argümanı çıkarmış."),
    ("MF-V07-S08-P007", "IMN-S00-P107", LabelKind.EDITED,
     "Hedef daha geniş bağlam içeriyor (754 vs 624 kelime); Albani önceki "
     "passage'la birleştirmiş gibi. Kaynaktaki cümle ('لأنه لا يستحق هذا "
     "الاسم...') hedefin ortasında birebir bulunabiliyor."),
    ("MF-V07-S09-P025", "IMN-S00-P136", LabelKind.EDITED,
     "Albani ilk cümleleri ('وسائر المرجئة...') atmış, 'والشافعي مع "
     "الصحابة...' sonrasını birebir alıyor. Sondaki içerik de Albani'de "
     "daha geniş."),
    ("MF-V07-S07-P008", "IMN-S00-P095", LabelKind.EDITED,
     "Kaynak hadisin yarısından kesilmiş ('قالها لذهب عنه...'); Albani "
     "hadisin tam başlangıcını ('وفي الصحيحين عن النبي...') ekleyip "
     "devamını birebir alıyor."),

    # ===== YÜKSEK BANT (0.80-0.95) =====
    ("MF-V07-S06-P004", "IMN-S00-P069", LabelKind.EDITED,
     "Albani Şâfiî'nin kaynağını (Atâ'dan rivayet) ek bir önsözle "
     "eklemiş; sonrasında 'وقال الشافعي رضي الله عنه في كتاب الأم...' "
     "kısmı birebir aynı."),
    ("MF-V07-S11-P007", "IMN-S00-P152", LabelKind.EDITED,
     "Kaynaktaki başlangıç bölümü (Halal nakli, ölüm hadisleri) hedefte "
     "yok; Albani kaynaktaki Ahmad-yaşlı diyaloğundan ('قال: ودخل عليه "
     "شيخ...') başlıyor."),
    ("MF-V07-S00-P011", "IMN-S00-P012", LabelKind.EXACT,
     "Birebir aynı pasaj. Albani sadece editöryel referansları ([آل عمران: "
     "103]) ve noktalama eklemiş — metin akışı hiç değişmemiş."),
    ("MF-V07-S09-P008", "IMN-S00-P118", LabelKind.OVERLAP,
     "Kaynak münafık/mü'min/küfür tanımları; hedef Hz. Peygamber'in "
     "şefaat duası ve cennet/cehennem dereceleri. Aynı geniş konu "
     "(iman-amel-küfür) ama tamamen farklı argümanlar."),
    ("MF-V07-S09-P026", "IMN-S00-P137", LabelKind.EXACT,
     "Birebir aynı pasaj. 'وهكذا كثير من الفلاسفة...' başlangıcından "
     "itibaren tüm metin aynı; Albani sadece [التوحيد] gibi bracket'lar "
     "eklemiş."),

    # ===== ORTA-YÜKSEK BANT (0.60-0.80) =====
    ("MF-V07-S00-P008", "IMN-S00-P009", LabelKind.OVERLAP,
     "Kaynak kalp katılığı + namaz; hedef Ammâr'ın namaz hadisi + "
     "haşyet. Ortak konu (namaz, iman, kalp) ama farklı pasajlar."),
    ("MF-V07-S06-P013", "IMN-S00-P079", LabelKind.OVERLAP,
     "Kaynak 'sekizinci yön: cahil mü'min'in tasdiki'; hedef 'Allah'ın "
     "kalplerine iman girmediği topluluk' tartışması. Aynı tema (iman "
     "seviyeleri) ama farklı argümanlar."),
    ("MF-V07-S09-P014", "IMN-S00-P124", LabelKind.OVERLAP,
     "İkisi de İslâm-İmân ayrımı tartışıyor; kaynak Ahmad'ın hadis "
     "yorumu, hedef Beyhakî/Eş'arî nakli. Farklı pasajlar."),
    ("MF-V07-S09-P009", "IMN-S00-P119", LabelKind.OVERLAP,
     "Kaynak küfür/nesep hadisleri; hedef fısk-iman ilişkisi. Yakın "
     "konu ama farklı argümanlar."),
    ("MF-V07-S09-P001", "IMN-S00-P111", LabelKind.OVERLAP,
     "Kaynak Ebû Tâlib el-Mekkî'nin imanın 7 erkânı; hedef İslâm-İmân "
     "tanım tartışması (Ebâdiyye/Mürcie). Farklı pasajlar."),
    ("MF-V07-S00-P003", "IMN-S00-P003", LabelKind.OVERLAP,
     "Kaynak 'kemâl-i vâcip vs müstahab' tartışması; hedef Yahudi/"
     "Hristiyan/Sâbiî mü'minler. Aynı geniş konu (iman tanımı) ama "
     "farklı argümanlar."),
    ("MF-V07-S07-P003", "IMN-S00-P090", LabelKind.OVERLAP,
     "Kaynak hadisten İslâm-İmân-Hicret-Cihâd hiyerarşisi; hedef ihlasla "
     "amelin sevabı. Bağlantılı ama farklı pasajlar."),
    ("MF-V07-S07-P004", "IMN-S00-P091", LabelKind.OVERLAP,
     "Kaynak 'kefarû ba'de imânihim' yorumu; hedef 'kefarû ba'de "
     "İslâmihim' yorumu (Tevbe 73-74). Yan yana ayetler, ardışık "
     "argümanlar — ama aynı pasaj değil."),
    ("MF-V07-S09-P015", "IMN-S00-P125", LabelKind.OVERLAP,
     "Kaynak Zühri'nin Sa'd hadisi yorumu, Ahmad'ın 'tevil' anlayışı; "
     "hedef Ahmad'a sorulan iman soruları (Salih b. Ahmad). Ortak "
     "kaynak (Ahmad) farklı pasajlar."),
    ("MF-V07-S00-P006", "IMN-S00-P007", LabelKind.OVERLAP,
     "Kaynak Yahudilerin Hz. Peygamber'i tanıması + 'akıl' lafzı; hedef "
     "korku-fıtrat tartışması. Ortak tema (ilim-amel) ama farklı "
     "argümanlar."),

    # ===== ORTA BANT (0.40-0.60) =====
    ("MF-V07-S00-P023", "IMN-S00-P025", LabelKind.EDITED,
     "ÖNEMLİ — düşük skora rağmen GERÇEK paralel. Hedefin ilk cümlesi "
     "('فتلك الشفاعة هي لأهل الإخلاص...') kaynağın yarıda kesilen "
     "sonuyla birebir aynı; argüman akışı kesintisiz devam ediyor. "
     "Albani kaynağın passage sınırını yeniden çizmiş, kaynak (152 "
     "kelime) çok kısa kaldığı için skor düşmüş. Threshold "
     "kalibrasyonu için değerli false-negative örneği."),
    ("MF-V07-S00-P022", "IMN-S00-P024", LabelKind.OVERLAP,
     "Kaynak müşrik Arapların yaratıcılığı kabul etmesi (yorum); hedef "
     "aynı konuda ayet listesi. Yüksek Kur'ân yoğunluğu (kaynak %58, "
     "hedef %53) — ortak ayet değil ortak metin gerek."),
    ("MF-V07-S01-P017", "IMN-S00-P043", LabelKind.OVERLAP,
     "Kaynak 'tasdik' lafzının Arapça dilsel kullanımı; hedef Kur'ân'ın "
     "Arapça oluşu. Yakın akrabalar (Arapça lafzı) ama farklı tezler."),
    ("MF-V07-S07-P002", "IMN-S00-P088", LabelKind.OVERLAP,
     "Kaynak Halid b. Ma'dân'dan İslâm hadisi; hedef Ubeyd b. Umeyr'den "
     "İslâm-İmân hadisi. İki ayrı hadis, aynı tematik alan."),
    ("MF-V07-S00-P021", "IMN-S00-P022", LabelKind.OVERLAP,
     "Kaynak taklid/şirk-i asgar tartışması; hedef ahbâr-rahbân rabb "
     "edinme (Tevbe 31). İkisi de tevhid konusunda ama farklı argümanlar."),

    # ===== DÜŞÜK BANT (0.30-0.40) =====
    ("MF-V07-S06-P020", "IMN-S00-P085", LabelKind.OVERLAP,
     "İkisi de Ahmad'dan nakil (iman/İslâm farkı); kaynak şehâdeteyn-"
     "namaz-zekât küfür rivayetleri, hedef 'أعتقها فإنها مؤمنة' hadisi "
     "ve Hammâd b. Zeyd ayrımı. Yakın ama farklı pasajlar — algoritma "
     "kelime ortaklığını (Ahmad, iman, İslâm) yakalamış."),
]


def main():
    if len(DECISIONS) != 26:
        print(f"HATA: 26 karar bekliyor, {len(DECISIONS)} bulundu")
        return 1

    aset = AnnotationSet(
        annotator="claude_4_7_baseline",
        session_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"),
        review_set_path="docs/cross_corpus/h2_pairs_for_review.md",
    )

    for src, tgt, label, notes in DECISIONS:
        aset.add_or_update(PairAnnotation(
            source_unit_id=src,
            target_unit_id=tgt,
            label=label,
            notes=notes,
            annotator="claude_4_7_baseline",
            annotated_at=now(),
        ))

    aset.completed = True
    path = save_annotation_set(aset, base_dir="data/annotations/h2_review")
    print(f"Kaydedildi: {path}")

    # Özet sınıf dağılımı
    from collections import Counter
    counts = Counter(a.label for a in aset.annotations)
    print(f"\nSınıf dağılımı:")
    for label in LabelKind:
        n = counts.get(label, 0)
        bar = "█" * n
        print(f"  {label.value:<8}: {n:>2}  {bar}")

    # Bant × etiket çapraz tablosu (manual olarak biliyoruz bantları)
    BANDS = {
        "Çok yüksek (≥0.95)": [0, 1, 2, 3, 4],
        "Yüksek (0.80–0.95)": [5, 6, 7, 8, 9],
        "Orta-yüksek (0.60–0.80)": list(range(10, 20)),
        "Orta (0.40–0.60)": list(range(20, 25)),
        "Düşük (0.30–0.40)": [25],
    }
    print(f"\nBant × etiket çapraz tablosu:")
    print(f"  {'Bant':<28} {'EXACT':>6} {'EDITED':>7} {'EXCERPT':>8} {'OVERLAP':>8} {'NOISE':>6}")
    for band_name, idxs in BANDS.items():
        c = Counter(DECISIONS[i][2] for i in idxs)
        print(f"  {band_name:<28} "
              f"{c.get(LabelKind.EXACT,0):>6} "
              f"{c.get(LabelKind.EDITED,0):>7} "
              f"{c.get(LabelKind.EXCERPT,0):>8} "
              f"{c.get(LabelKind.OVERLAP,0):>8} "
              f"{c.get(LabelKind.NOISE,0):>6}")

    # True positive / negative oranı
    tp = sum(1 for _, _, l, _ in DECISIONS if LabelKind.is_true_positive(l))
    fp = sum(1 for _, _, l, _ in DECISIONS if l == LabelKind.NOISE)
    borderline = sum(1 for _, _, l, _ in DECISIONS if l == LabelKind.OVERLAP)
    print(f"\n  True positive (EXACT/EDITED/EXCERPT): {tp}/26 = {100*tp/26:.1f}%")
    print(f"  Borderline (OVERLAP):                   {borderline}/26 = {100*borderline/26:.1f}%")
    print(f"  Algoritma yanılması (NOISE):            {fp}/26 = {100*fp/26:.1f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
