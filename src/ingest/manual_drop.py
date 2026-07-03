"""수동 ZIP/폴더 드롭 — hybrid 최종 폴백."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.process.classifier import ImageClassifier


class ManualDrop:
  """source/manual_drop/ 폴더의 이미지를 manifest 형식으로 로드한다."""

  SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    self.classifier = ImageClassifier(config)

  def load(self, job_dir: Path, manual_dir: Path | None = None) -> dict[str, Any]:
    """manual_dir(또는 job_dir/source/manual_drop)에서 이미지를 읽어 manifest 생성."""
    drop_dir = manual_dir or job_dir / "source" / "manual_drop"
    if not drop_dir.exists():
      raise FileNotFoundError(f"manual_drop 폴더 없음: {drop_dir}")

    source = job_dir / "source"
    gallery_dir = source / "01_gallery"
    detail_dir = source / "02_detail_page"
    gallery_dir.mkdir(parents=True, exist_ok=True)
    detail_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in drop_dir.iterdir() if p.suffix.lower() in self.SUPPORTED)
    if not files:
      raise ValueError(f"manual_drop에 이미지 없음: {drop_dir}")

    gallery_files: list[tuple[Path, str]] = []
    other_files: list[tuple[Path, str]] = []

    for i, src in enumerate(files):
      if i < 6:
        dest = gallery_dir / f"gallery_{i + 1:02d}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        gallery_files.append((dest, ""))
      else:
        dest = detail_dir / f"desc_{i + 1:02d}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        other_files.append((dest, ""))

    classified = self.classifier.classify_manifest(gallery_files, other_files)
    gallery, detail_page, junk = [], [], []

    for item in classified:
      entry = {"file": str(item.path.relative_to(job_dir)), "bytes": item.bytes, "tier": item.tier, "url": ""}
      if item.category == "gallery":
        gallery.append(entry)
      elif item.category == "detail_page":
        detail_page.append(entry)
      else:
        junk.append(entry)

    manifest = {
      "source_url": "manual_drop",
      "title": drop_dir.name,
      "parser": "manual_drop",
      "summary": {"gallery": len(gallery), "detail_page": len(detail_page), "related_thumbnails": len(junk)},
      "gallery": gallery,
      "detail_page": detail_page,
      "related_thumbnails": junk,
    }
    (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
