"""Tier A Pillow 리사이즈 테스트."""

from __future__ import annotations

from PIL import Image

from src.process.image_tier_a import TierAProcessor


def test_resize_to_coupang_width(config, sample_jpg, tmp_path):
  proc = TierAProcessor(config)
  dest = tmp_path / "out.jpg"
  proc.process_to_jpg(sample_jpg, dest)
  with Image.open(dest) as img:
    assert img.width == config["output"]["coupang_target_width_px"]
    assert img.format == "JPEG"
