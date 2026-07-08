"""쿠팡 태그 20개 생성."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.process.gemini_client import GeminiClient


class CoupangTagGenerator:
  """seed·related 기반 태그 20개를 생성한다."""

  TARGET_COUNT = 20

  def __init__(self, config: dict[str, Any], gemini: GeminiClient | None = None) -> None:
    self.config = config
    self.gemini = gemini

  def generate(self, job_dir: Path, keyword_ctx: dict[str, Any]) -> Path:
    """coupang_meta/tags.json 저장."""
    meta_dir = job_dir / "coupang_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    dest = meta_dir / "tags.json"

    seed = keyword_ctx.get("seed", "상품")
    related = list(keyword_ctx.get("related") or [])
    tags: list[str] = []

    for t in [seed, *related]:
      for part in str(t).replace(",", " ").split():
        part = part.strip()
        if part and part not in tags:
          tags.append(part)

    # seed 변형·연관어로 20개까지 확장
    suffixes = ["추천", "인기", "선물", "실용", "최신", "가성비", "프리미엄", "베스트", "필수", "신상"]
    i = 0
    while len(tags) < self.TARGET_COUNT and i < len(suffixes) * 3:
      candidate = f"{seed}{suffixes[i % len(suffixes)]}"
      if candidate not in tags:
        tags.append(candidate)
      i += 1

    if self.gemini and self.gemini.available and len(tags) < self.TARGET_COUNT:
      extra = self.gemini.generate_text(
        f"쿠팡 검색 태그 {self.TARGET_COUNT - len(tags)}개를 쉼표로 구분해줘. 키워드: {seed}"
      )
      for part in extra.replace("\n", ",").split(","):
        part = part.strip()
        if part and part not in tags:
          tags.append(part)
        if len(tags) >= self.TARGET_COUNT:
          break

    tags = tags[: self.TARGET_COUNT]
    while len(tags) < self.TARGET_COUNT:
      tags.append(f"{seed}{len(tags)}")

    # json.dumps: 쿠팡 Wing 업로드용 tags.json — 리스트 20개, ensure_ascii=False로 한글 태그 유지.
    dest.write_text(json.dumps(tags, ensure_ascii=False, indent=2), encoding="utf-8")
    return dest
