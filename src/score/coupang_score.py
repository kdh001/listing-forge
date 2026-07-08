"""쿠팡 상위노출 점수 채점 — 75점 기준."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.render.coupang_attributes import CoupangAttributeFiller


class CoupangScoreChecker:
  """산출물 완성도를 점수화해 coupang_score_report.md 생성."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    rs = config.get("coupang", {}).get("ranking_score", {})
    self.threshold = int(rs.get("pass_threshold", 75))
    self.weights = rs.get("weights", {})
    self.min_additional = int(config.get("coupang", {}).get("min_additional_images", 5))

  def score(self, job_dir: Path, keyword_ctx: dict[str, Any]) -> dict[str, Any]:
    """항목별 점수 dict + total."""
    w = self.weights
    breakdown: dict[str, dict[str, Any]] = {}

    # OTA FILL — 수동 체크리스트
    breakdown["ota_fill_ad_ready"] = {
      "points": 0,
      "max": w.get("ota_fill_ad_ready", 20),
      "manual": True,
      "note": "Wing에서 OTA FILL 광고 노출 가능 여부를 수동 확인하세요.",
    }

    # Rec.Attr
    attr_path = job_dir / "coupang_meta" / "attributes.csv"
    attr_ok = CoupangAttributeFiller(self.config).is_complete(attr_path)
    breakdown["rec_attr_filled"] = {
      "points": w.get("rec_attr_filled", 20) if attr_ok else 0,
      "max": w.get("rec_attr_filled", 20),
      "ok": attr_ok,
    }

    # 태그 20개
    tags_path = job_dir / "coupang_meta" / "tags.json"
    tag_count = 0
    if tags_path.exists():
      # json.loads: tags.json 배열 길이 == 20 이면 tags_count_20 항목 20점 획득.
      tag_count = len(json.loads(tags_path.read_text(encoding="utf-8")))
    tags_ok = tag_count == 20
    breakdown["tags_count_20"] = {
      "points": w.get("tags_count_20", 20) if tags_ok else 0,
      "max": w.get("tags_count_20", 20),
      "count": tag_count,
      "ok": tags_ok,
    }

    # 이미지 수
    coupang_images = list((job_dir / "coupang").glob("*.jpg"))
    img_ok = len(coupang_images) >= 1 + self.min_additional
    breakdown["image_count_min"] = {
      "points": w.get("image_count_min", 20) if img_ok else 0,
      "max": w.get("image_count_min", 20),
      "count": len(coupang_images),
      "ok": img_ok,
    }

    # 브랜드 가산
    brand = (keyword_ctx.get("listing") or {}).get("brand_registered", False)
    breakdown["brand_registered_bonus"] = {
      "points": w.get("brand_registered_bonus", 20) if brand else 0,
      "max": w.get("brand_registered_bonus", 20),
      "ok": bool(brand),
    }

    auto_total = sum(b["points"] for b in breakdown.values() if not b.get("manual"))
    max_auto = sum(b["max"] for b in breakdown.values() if not b.get("manual"))
    total = auto_total  # OTA는 수동이라 자동 합계에 미포함

    result = {
      "total": total,
      "max_auto": max_auto,
      "threshold": self.threshold,
      "passed": total >= self.threshold,
      "breakdown": breakdown,
    }
    return result

  def write_report(self, job_dir: Path, result: dict[str, Any]) -> Path:
    """coupang_score_report.md 마크다운 리포트."""
    dest = job_dir / "coupang_score_report.md"
    lines = [
      "# 쿠팡 상위노출 점수 리포트",
      "",
      f"**자동 채점 합계: {result['total']} / {result['max_auto']}** (통과 기준: {result['threshold']}점)",
      "",
    ]
    if not result["passed"]:
      lines.extend(["> ⚠️ **경고**: 75점 미달 — 업로드 전 항목을 보완하세요.", ""])

    lines.append("| 항목 | 배점 | 획득 | 상태 |")
    lines.append("|---|---:|---:|---|")
    labels = {
      "ota_fill_ad_ready": "OTA FILL 광고 노출",
      "rec_attr_filled": "Rec.Attr 상품속성",
      "tags_count_20": "태그 20개",
      "image_count_min": "대표+추가이미지",
      "brand_registered_bonus": "브랜드 등록 가산",
    }
    for key, item in result["breakdown"].items():
      status = "수동 확인" if item.get("manual") else ("✅" if item.get("ok") else "❌")
      lines.append(f"| {labels.get(key, key)} | {item['max']} | {item['points']} | {status} |")

    lines.extend(["", "## 참고 (품질 가이드)", "- 20자 내외 상품명: `coupang_meta/title.txt`", "- 품질 높은 이미지: Tier A/B + 흰 배경 대표이미지", "- 메타태그: tags.json + naver_images_meta.csv"])
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest
