"""H2 manuel doğrulama için etiketleme şeması.

Hüseyin Hoca (ve gerekirse ikinci annotator) 26 stratified örneği
EXACT/EDITED/EXCERPT/OVERLAP/NOISE olarak işaretler. Bu modül:
    - Pydantic şeması ile etiket validasyonu
    - Atomic JSON save (kısmi kayıp yok)
    - Cohen κ ile iki annotator arası uyum hesabı
    - Annotation set yükleme (resume için)
sağlar.

Etiket sınıfları (5 sınıf):
    EXACT   - Birebir tekrar (kelimelik farklar olabilir, aynı pasaj)
    EDITED  - Albani edisyonu — kelime/sıra değişiklikleri ama aynı argüman
    EXCERPT - Hedef, kaynağın bir kısmı (özet veya alıntı)
    OVERLAP - Ortak konu/ortak ayet, ama farklı argüman
    NOISE   - Yanlış eşleşme — algoritma yanılmış

İlk üçü (EXACT/EDITED/EXCERPT) → "true positive" (gerçek tekrar)
OVERLAP → "borderline" (S4'te tartışılır)
NOISE → "false positive"

Threshold kalibrasyonu için S4'te kullanılır.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

from pydantic import BaseModel, Field, field_validator


class LabelKind(str, Enum):
    """5 sınıflı etiket. str-temelli enum → JSON'a doğrudan yazılır."""

    EXACT = "EXACT"
    EDITED = "EDITED"
    EXCERPT = "EXCERPT"
    OVERLAP = "OVERLAP"
    NOISE = "NOISE"

    @classmethod
    def is_true_positive(cls, label: "LabelKind") -> bool:
        """EXACT/EDITED/EXCERPT → True. OVERLAP/NOISE → False."""
        return label in {cls.EXACT, cls.EDITED, cls.EXCERPT}

    @classmethod
    def is_noise(cls, label: "LabelKind") -> bool:
        return label == cls.NOISE


class PairAnnotation(BaseModel):
    """Tek bir pair için bir annotator'ın kararı."""

    source_unit_id: str
    target_unit_id: str
    label: LabelKind
    notes: str = ""
    annotator: str
    annotated_at: str  # ISO 8601 UTC

    @field_validator("annotator")
    @classmethod
    def _validate_annotator(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("annotator boş olamaz")
        if len(v) > 100:
            raise ValueError("annotator 100 karakterden uzun olamaz")
        return v

    @field_validator("source_unit_id", "target_unit_id")
    @classmethod
    def _validate_unit_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("unit_id boş olamaz")
        return v


class AnnotationSet(BaseModel):
    """Bir annotator'ın bir oturumda tamamladığı tüm etiketler.

    Disk'te JSON olarak tutulur:
        data/annotations/h2_review/{annotator}_{session_id}.json
    """

    annotator: str
    session_id: str  # genellikle ISO timestamp
    annotations: list[PairAnnotation] = Field(default_factory=list)
    review_set_path: str = ""  # hangi review setine karşılık geldiği
    completed: bool = False  # tüm pair'ler etiketlenmiş mi
    created_at: str = ""  # ISO 8601 UTC
    updated_at: str = ""

    def add_or_update(self, annotation: PairAnnotation) -> None:
        """Aynı pair için bir etiket varsa üzerine yaz; yoksa ekle.

        Eşitlik: (source_unit_id, target_unit_id) ikilisi.
        """
        key = (annotation.source_unit_id, annotation.target_unit_id)
        for i, existing in enumerate(self.annotations):
            if (existing.source_unit_id, existing.target_unit_id) == key:
                self.annotations[i] = annotation
                self.updated_at = _now_iso()
                return
        self.annotations.append(annotation)
        self.updated_at = _now_iso()

    def label_for(self, source_id: str, target_id: str) -> Optional[LabelKind]:
        """Bu pair zaten etiketlenmişse etiketini döner; yoksa None."""
        for a in self.annotations:
            if a.source_unit_id == source_id and a.target_unit_id == target_id:
                return a.label
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_annotation_set(
    aset: AnnotationSet,
    base_dir: str | Path = "data/annotations/h2_review",
) -> Path:
    """AnnotationSet'i atomic olarak diske yaz.

    Atomicity: önce tmpfile'a yaz, sonra os.replace ile rename. Bu
    yarı-yazılmış dosya bırakmaz; etiketleme sırasında crash olsa bile
    önceki kaydedilmiş hâl kaybolmaz.

    Dosya adı: {annotator}_{session_id}.json (annotator slugified)
    """
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    slug = _slugify(aset.annotator)
    filename = f"{slug}_{aset.session_id}.json"
    target = base / filename

    if not aset.created_at:
        aset.created_at = _now_iso()
    aset.updated_at = _now_iso()

    payload = aset.model_dump(mode="json")
    text = json.dumps(payload, ensure_ascii=False, indent=2)

    # Atomic write: tmp + rename
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{filename}.", suffix=".tmp", dir=str(base)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_path, target)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    return target


def load_annotation_set(path: str | Path) -> AnnotationSet:
    """Daha önce kaydedilmiş AnnotationSet'i diskten yükler."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return AnnotationSet.model_validate(data)


def list_annotation_sets(
    base_dir: str | Path = "data/annotations/h2_review",
) -> list[Path]:
    """Bir dizindeki tüm annotation set JSON dosyalarını döner."""
    base = Path(base_dir)
    if not base.exists():
        return []
    return sorted(base.glob("*.json"))


def _slugify(name: str) -> str:
    """Annotator adını dosya-güvenli slug'a dönüştür.

    "Hüseyin Gökalp" → "huseyin_gokalp"
    Türkçe karakterleri ASCII'ye approximate map'liyoruz.
    """
    tr_map = str.maketrans("ÇĞİıÖŞÜçğöşü", "CGIiOSUcgosu")
    s = name.translate(tr_map).lower()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("_")
    slug = "".join(out).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or "anon"


# ---------------------------------------------------------------------------
# Inter-rater agreement (Cohen's κ)
# ---------------------------------------------------------------------------


def cohen_kappa(
    annotations_a: Sequence[PairAnnotation],
    annotations_b: Sequence[PairAnnotation],
) -> float:
    """İki annotator arasındaki Cohen κ değeri.

    κ = (Po - Pe) / (1 - Pe)
        Po: gözlenen uyum oranı
        Pe: rastgele beklenen uyum oranı

    Yorumlama (Landis & Koch 1977):
        < 0.00  : kötü uyum
        0.01-0.20: hafif (slight)
        0.21-0.40: makul (fair)
        0.41-0.60: orta (moderate)
        0.61-0.80: önemli (substantial)
        0.81-1.00: neredeyse mükemmel

    Args:
        annotations_a: Birinci annotator'ın PairAnnotation listesi
        annotations_b: İkinci annotator'ın PairAnnotation listesi

    Returns:
        Cohen κ değeri. Eğer ortak pair yoksa veya tüm uyumsa 1.0.

    Hesap sadece **ortak pair'ler** üzerinden yapılır (her iki annotator
    da etiketlemiş olanlar). Eksik etiketleme normalize edilmez.
    """
    # (source, target) → label dict
    map_a = {(a.source_unit_id, a.target_unit_id): a.label for a in annotations_a}
    map_b = {(a.source_unit_id, a.target_unit_id): a.label for a in annotations_b}

    common_keys = set(map_a) & set(map_b)
    n = len(common_keys)
    if n == 0:
        return 0.0

    # Po: aynı etiket sayısı / toplam
    agree = sum(1 for k in common_keys if map_a[k] == map_b[k])
    po = agree / n

    # Pe: Her sınıfın iki annotator'da bağımsız frekansı çarpılır, toplanır
    labels = list(LabelKind)
    pe = 0.0
    for label in labels:
        p_a = sum(1 for k in common_keys if map_a[k] == label) / n
        p_b = sum(1 for k in common_keys if map_b[k] == label) / n
        pe += p_a * p_b

    if pe == 1.0:
        # Mükemmel uyum + tek sınıf → κ tanımsız; 1.0 döndür (tüm uyumlar)
        return 1.0 if po == 1.0 else 0.0

    return (po - pe) / (1.0 - pe)


def confusion_matrix(
    annotations_a: Sequence[PairAnnotation],
    annotations_b: Sequence[PairAnnotation],
) -> dict[tuple[LabelKind, LabelKind], int]:
    """A vs B confusion matrix (sözlük: (a_label, b_label) → count).

    Nerede uyuşamadıklarını anlamak için kullanılır.
    """
    map_a = {(a.source_unit_id, a.target_unit_id): a.label for a in annotations_a}
    map_b = {(a.source_unit_id, a.target_unit_id): a.label for a in annotations_b}

    matrix: dict[tuple[LabelKind, LabelKind], int] = {}
    for k in set(map_a) & set(map_b):
        key = (map_a[k], map_b[k])
        matrix[key] = matrix.get(key, 0) + 1
    return matrix
