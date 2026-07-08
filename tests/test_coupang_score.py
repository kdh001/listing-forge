"""CoupangScoreChecker 테스트."""

from __future__ import annotations

import json

from src.config_loader import load_keyword_context
from src.render.coupang_attributes import CoupangAttributeFiller
from src.render.coupang_tags import CoupangTagGenerator
from src.score.coupang_score import CoupangScoreChecker
from src.process.gemini_client import GeminiClient


def _setup_coupang_job(job, config, kw, sample_jpg):
  coupang = job / "coupang"
  coupang.mkdir(parents=True)
  for i in range(6):
    dest = coupang / f"{i + 1:02d}_{'main' if i == 0 else 'sub'}_test.jpg"
    dest.write_bytes(sample_jpg.read_bytes())
  CoupangAttributeFiller(config).fill(job, kw, "테스트상품")
  CoupangTagGenerator(config, GeminiClient(config)).generate(job, kw)
  (job / "coupang_meta" / "title.txt").write_text("3in1클립렌즈", encoding="utf-8")


def test_score_passes_with_full_artifacts(config, keyword_yaml, tmp_path, sample_jpg):
  kw = load_keyword_context(keyword_yaml)
  job = tmp_path / "job"
  job.mkdir()
  _setup_coupang_job(job, config, kw, sample_jpg)

  # CoupangScoreChecker.score: tags 20·이미지 6·속성 CSV → 75점 중 자동 채점 항목 검증.
  checker = CoupangScoreChecker(config)
  result = checker.score(job, kw)
  assert result["total"] >= 60
  assert result["breakdown"]["tags_count_20"]["ok"] is True
  assert result["breakdown"]["image_count_min"]["ok"] is True

  report_path = checker.write_report(job, result)
  assert report_path.exists()
  assert "쿠팡 상위노출" in report_path.read_text(encoding="utf-8")


def test_brand_bonus(config, keyword_yaml, tmp_path, sample_jpg):
  kw = load_keyword_context(keyword_yaml)
  kw["listing"]["brand_registered"] = True
  job = tmp_path / "job2"
  job.mkdir()
  _setup_coupang_job(job, config, kw, sample_jpg)
  result = CoupangScoreChecker(config).score(job, kw)
  assert result["breakdown"]["brand_registered_bonus"]["points"] == 20
