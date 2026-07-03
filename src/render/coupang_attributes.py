"""쿠팡 Rec.Attr 상품속성 채우기."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


# 카테고리 프리셋별 필수 속성 (MVP: digital_accessory 기본)
REQUIRED_ATTRS = ["브랜드", "모델명", "제조국", "품목", "색상", "재질"]


class CoupangAttributeFiller:
  """keyword-scout listing.coupang_preset 기반 속성 CSV 생성."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config

  def fill(self, job_dir: Path, keyword_ctx: dict[str, Any], product_title: str) -> Path:
    """coupang_meta/attributes.csv 생성."""
    meta_dir = job_dir / "coupang_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    dest = meta_dir / "attributes.csv"
    listing = keyword_ctx.get("listing") or {}
    preset = listing.get("coupang_preset", "digital_accessory")
    seed = keyword_ctx.get("seed", "상품")

    rows = [
      {"속성명": "브랜드", "속성값": listing.get("brand_name", "기타")},
      {"속성명": "모델명", "속성값": seed[:30]},
      {"속성명": "제조국", "속성값": listing.get("origin_country", "중국(OEM)")},
      {"속성명": "품목", "속성값": product_title[:50] or seed},
      {"속성명": "색상", "속성값": listing.get("color", "상세페이지 참조")},
      {"속성명": "재질", "속성값": listing.get("material", "상세페이지 참조")},
      {"속성명": "프리셋", "속성값": preset},
    ]

    with open(dest, "w", encoding="utf-8-sig", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=["속성명", "속성값"])
      writer.writeheader()
      writer.writerows(rows)

    return dest

  def is_complete(self, path: Path) -> bool:
    """필수 속성이 모두 채워졌는지 확인."""
    if not path.exists():
      return False
    with open(path, encoding="utf-8-sig") as f:
      reader = csv.DictReader(f)
      filled = {row["속성명"]: row["속성값"] for row in reader if row.get("속성값")}
    return all(filled.get(a) for a in REQUIRED_ATTRS)
