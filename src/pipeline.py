"""listing-forge pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ListingPipeline:
  root: Path

  def _load_config(self) -> dict[str, Any]:
    cfg_path = self.root / "config" / "listing.yaml"
    with open(cfg_path, encoding="utf-8") as f:
      return yaml.safe_load(f)

  def _job_dir(self, slug: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d")
    out = self.root / "output" / f"{slug}_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    return out

  def ingest(self, url: str, out_dir: Path | None = None) -> Path:
    """Phase 1: PublicParser 연결 예정."""
    from src.ingest.public_parser import PublicParser

    cfg = self._load_config()
    job = out_dir or self._job_dir("ingest")
    (job / "source").mkdir(parents=True, exist_ok=True)
    parser = PublicParser(cfg)
    meta = parser.fetch(url)
    manifest = job / "manifest.json"
    import json

    manifest.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return job

  def build(
    self,
    *,
    url: str | None,
    manual_dir: Path | None,
    keyword_yaml: Path,
    platform: str,
    max_detail_images: int,
  ) -> Path:
    """전체 빌드 — Phase 1+ 구현 예정."""
    with open(keyword_yaml, encoding="utf-8") as f:
      kw = yaml.safe_load(f)
    slug = str(kw.get("seed", "product")).replace(" ", "")[:32]
    job = self._job_dir(slug)
    (job / "DISCLAIMER.md").write_text(
      "# 면책\n\n중국 OEM 이미지·상표·KC 인증은 판매자 책임으로 확인하세요.\n",
      encoding="utf-8",
    )
    if url:
      self.ingest(url, out_dir=job)
    if manual_dir:
      # Phase 1: manual_drop
      pass
    # TODO: classifier, gemini, naver_html, coupang_jpeg
    readme = job / "README.txt"
    readme.write_text(
      f"platform={platform}\nkeyword_yaml={keyword_yaml}\nmax_detail={max_detail_images}\n",
      encoding="utf-8",
    )
    return job
