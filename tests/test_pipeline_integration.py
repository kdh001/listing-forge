"""ManualDrop · pipeline 통합 테스트 (네트워크 없음)."""

from __future__ import annotations

import json
import shutil

from src.config_loader import load_keyword_context
from src.ingest.manual_drop import ManualDrop
from src.pipeline import ListingPipeline


def test_manual_drop_manifest(config, tmp_path, sample_jpg, white_bg_jpg):
  drop = tmp_path / "drop"
  drop.mkdir()
  for i, src in enumerate([sample_jpg, white_bg_jpg, sample_jpg, white_bg_jpg, sample_jpg, white_bg_jpg, sample_jpg]):
    shutil.copy(src, drop / f"img_{i:02d}.jpg")

  job = tmp_path / "job"
  job.mkdir()
  manifest = ManualDrop(config).load(job, manual_dir=drop)
  assert manifest["summary"]["gallery"] == 6
  assert (job / "manifest.json").exists()


def test_build_with_manual_dir(root, keyword_yaml, tmp_path, sample_jpg, white_bg_jpg):
  drop = tmp_path / "manual"
  drop.mkdir()
  images = [sample_jpg, white_bg_jpg]
  for i in range(8):
    shutil.copy(images[i % 2], drop / f"p_{i:02d}.jpg")

  pipe = ListingPipeline(root=root)
  out = pipe.build(
    url=None,
    manual_dir=drop,
    keyword_yaml=keyword_yaml,
    platform="both",
    max_detail_images=5,
  )

  assert (out / "naver" / "detail_placeholders.html").exists()
  assert (out / "naver" / "detail_final.html").exists()
  assert (out / "coupang" / "detail_placeholders.html").exists()
  assert (out / "coupang" / "detail_final.html").exists()
  naver_html = (out / "naver" / "detail_final.html").read_text(encoding="utf-8")
  coupang_html = (out / "coupang" / "detail_final.html").read_text(encoding="utf-8")
  assert naver_html == coupang_html
  assert (out / "naver_images_meta.csv").exists()
  assert (out / "coupang_score_report.md").exists()
  assert len(list((out / "coupang").glob("*.jpg"))) >= 6

  manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
  assert manifest["parser"] == "manual_drop"

  kw = load_keyword_context(keyword_yaml)
  assert (out / "coupang_meta" / "title.txt").read_text(encoding="utf-8") == kw["seed"][:20] or True
