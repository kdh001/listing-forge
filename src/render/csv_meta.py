"""네이버 naver_images_meta.csv 생성."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


class CsvMetaWriter:
  """templates/naver_images_meta.sample.csv 스키마 호환 CSV."""

  HEADERS = ["순번", "네이버업로드파일명", "바이트", "글자수", "사진설명", "카테고리태그", "검색키워드"]

  def write(self, dest: Path, rows: list[dict[str, Any]]) -> Path:
    """rows를 CSV로 저장한다."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8-sig", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=self.HEADERS)
      writer.writeheader()
      for row in rows:
        writer.writerow({h: row.get(h, "") for h in self.HEADERS})
    return dest

  def build_rows(
    self,
    image_slots: list[dict[str, str]],
    keyword_ctx: dict[str, Any],
    *,
    file_sizes: dict[str, int] | None = None,
  ) -> list[dict[str, Any]]:
    """이미지 슬롯 + 키워드로 CSV 행 목록 생성."""
    seed = keyword_ctx.get("seed", "상품")
    related = keyword_ctx.get("related") or []
    listing = keyword_ctx.get("listing") or {}
    category = listing.get("category_tag", "디지털/가전 > 기타")
    keywords = ", ".join([seed, *related[:6]])

    sizes = file_sizes or {}
    rows: list[dict[str, Any]] = []
    for slot in image_slots:
      fn = slot["filename"]
      desc = slot.get("caption", "")
      rows.append(
        {
          "순번": slot["seq"],
          "네이버업로드파일명": fn,
          "바이트": sizes.get(fn, 0),
          "글자수": len(desc),
          "사진설명": desc,
          "카테고리태그": category,
          "검색키워드": keywords,
        }
      )
    return rows
