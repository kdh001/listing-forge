"""Tier A — 제품컷 Pillow 리사이즈·JPG 변환 (텍스트 추가 없음)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image


class TierAProcessor:
  """제품컷을 쿠팡·네이버용 해상도로 리사이즈한다."""

  def __init__(self, config: dict[str, Any]) -> None:
    out = config.get("output", {})
    self.coupang_width = int(out.get("coupang_target_width_px", 1720))
    self.naver_width = int(out.get("naver_max_width_px", 860))
    self.jpeg_quality = int(out.get("jpeg_quality", 92))

  def process_to_jpg(self, src: Path, dest: Path, *, target_width: int | None = None) -> Path:
    """src 이미지를 target_width 기준으로 비율 유지 리사이즈 후 JPG 저장."""
    width = target_width or self.coupang_width
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
      rgb = img.convert("RGB")
      if rgb.width != width:
        ratio = width / rgb.width
        new_h = max(1, int(rgb.height * ratio))
        rgb = rgb.resize((width, new_h), Image.Resampling.LANCZOS)
      rgb.save(dest, format="JPEG", quality=self.jpeg_quality, optimize=True)
    return dest
