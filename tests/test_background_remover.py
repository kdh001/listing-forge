"""BackgroundNormalizer 테스트."""

from __future__ import annotations

from src.process.background_remover import BackgroundNormalizer


def test_white_image_skips_processing(config, white_bg_jpg, tmp_path):
  # _white_ratio ≥ min_white_ratio(0.92) 이면 rembg 없이 already_white로 스킵.
  norm = BackgroundNormalizer(config)
  dest = tmp_path / "out.jpg"
  report = norm.normalize_main_image(white_bg_jpg, dest)
  assert report["method"] == "already_white"
  assert report["ok"] is True
  assert dest.exists()


def test_gray_background_gets_composited(config, sample_jpg, tmp_path):
  norm = BackgroundNormalizer(config)
  dest = tmp_path / "out.jpg"
  # rembg 미설치 환경에서는 simple composite 폴백 — method는 rembg|copy_fallback 등.
  report = norm.normalize_main_image(sample_jpg, dest)
  assert dest.exists()
  assert report["method"] in ("rembg", "rembg_partial", "copy_fallback", "gemini_fallback", "already_white")
  ratio = norm._white_ratio(dest)
  assert ratio >= 0.5
