"""쿠팡 JPG 네이밍·내보내기."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.process.image_tier_a import TierAProcessor


class CoupangExporter:
  """Tier A 갤러리 이미지를 coupang/ 폴더 JPG로 내보낸다."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    self.tier_a = TierAProcessor(config)

  def export_gallery(
    self,
    job_dir: Path,
    manifest: dict[str, Any],
    slug: str,
  ) -> list[Path]:
    """manifest gallery → coupang/01_main, 02_sub... JPG."""
    coupang_dir = job_dir / "coupang"
    coupang_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    gallery = manifest.get("gallery") or []

    for i, item in enumerate(gallery):
      src = job_dir / item["file"]
      if not src.exists():
        continue
      if i == 0:
        name = f"01_main_{slug}_대표.jpg"
      else:
        name = f"{i + 1:02d}_sub_{slug}_{i}.jpg"
      dest = coupang_dir / name
      # TierAProcessor.process_to_jpg: 1720px LANCZOS 리사이즈 — 쿠팡 대표/추가 JPG 규격.
      self.tier_a.process_to_jpg(src, dest)
      exported.append(dest)

    return exported

  def copy_additional_from_detail(
    self,
    job_dir: Path,
    manifest: dict[str, Any],
    slug: str,
    *,
    min_count: int = 5,
  ) -> list[Path]:
    """detail_page Tier A 이미지로 추가 이미지를 채운다."""
    coupang_dir = job_dir / "coupang"
    # Path.glob("*.jpg"): 기존 coupang JPG 개수로 min_additional(5)+대표1 장 충족 여부 판단.
    existing = sorted(coupang_dir.glob("*.jpg"))
    need = max(0, min_count + 1 - len(existing))
    if need <= 0:
      return existing

    tier_a_details = [
      item for item in (manifest.get("detail_page") or []) if item.get("tier") == "A"
    ]
    added: list[Path] = []
    seq = len(existing) + 1
    for item in tier_a_details:
      if len(added) >= need:
        break
      src = job_dir / item["file"]
      if not src.exists():
        continue
      dest = coupang_dir / f"{seq:02d}_sub_{slug}_detail{seq}.jpg"
      self.tier_a.process_to_jpg(src, dest)
      added.append(dest)
      seq += 1

    return sorted(coupang_dir.glob("*.jpg"))
