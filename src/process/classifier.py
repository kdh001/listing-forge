"""gallery / detail / junk 분류 · Tier A/B 판정."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class ClassifiedImage:
  """분류·티어 결과를 담는 데이터 클래스."""

  path: Path
  category: str  # gallery | detail_page | junk
  tier: str  # A | B
  bytes: int
  url: str = ""


class ImageClassifier:
  """다운로드된 파일을 clip-lens 규칙(150KB 임계)으로 분류한다."""

  def __init__(self, config: dict[str, Any]) -> None:
    ingest = config.get("ingest", {})
    self.detail_min_bytes = int(ingest.get("detail_min_bytes", 150_000))
    self.thumbnail_max_bytes = int(ingest.get("thumbnail_max_bytes", 100_000))
    tier_cfg = config.get("image_tiers", {})
    self.text_ratio_tier_b = float(tier_cfg.get("text_area_ratio_tier_b", 0.05))

  def classify_file(
    self,
    path: Path,
    *,
    is_gallery: bool = False,
    url: str = "",
  ) -> ClassifiedImage:
    """단일 파일을 gallery/detail/junk로 분류하고 Tier A/B를 부여한다."""
    size = path.stat().st_size if path.exists() else 0
    if is_gallery:
      category = "gallery"
    elif size >= self.detail_min_bytes:
      category = "detail_page"
    elif size <= self.thumbnail_max_bytes:
      category = "junk"
    else:
      category = "detail_page"

    tier = "B" if category == "detail_page" and self._estimate_text_ratio(path) >= self.text_ratio_tier_b else "A"
    return ClassifiedImage(path=path, category=category, tier=tier, bytes=size, url=url)

  def classify_manifest(
    self,
    gallery_files: list[tuple[Path, str]],
    other_files: list[tuple[Path, str]],
  ) -> list[ClassifiedImage]:
    """갤러리·기타 파일 목록을 일괄 분류한다."""
    out: list[ClassifiedImage] = []
    for path, url in gallery_files:
      out.append(self.classify_file(path, is_gallery=True, url=url))
    for path, url in other_files:
      out.append(self.classify_file(path, is_gallery=False, url=url))
    return out

  def _estimate_text_ratio(self, path: Path) -> float:
    """고대비·채도 낮은 영역 비율로 텍스트 포함 추정(경량 휴리스틱)."""
    try:
      with Image.open(path) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        if w * h == 0:
          return 0.0
        step = max(1, (w * h) // 5000)
        pixels = list(rgb.getdata())
        text_like = 0
        sampled = 0
        for i in range(0, len(pixels), step):
          r, g, b = pixels[i]
          mx, mn = max(r, g, b), min(r, g, b)
          if mx - mn < 25 and 40 < mx < 220:
            text_like += 1
          sampled += 1
        return text_like / sampled if sampled else 0.0
    except OSError:
      return 0.0
