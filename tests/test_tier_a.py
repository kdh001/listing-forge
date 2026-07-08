"""Tier A Pillow 리사이즈 테스트."""

from __future__ import annotations

from PIL import Image

from src.process.image_tier_a import TierAProcessor


def test_resize_to_coupang_width(config, sample_jpg, tmp_path):
  proc = TierAProcessor(config)
  dest = tmp_path / "out.jpg"
  proc.process_to_jpg(sample_jpg, dest)
  # Image.open: Tier A 출력 JPG width가 config coupang_target_width_px(1720)와 일치하는지 검증.
  with Image.open(dest) as img:
    assert img.width == config["output"]["coupang_target_width_px"]
    assert img.format == "JPEG"
