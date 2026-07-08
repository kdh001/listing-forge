"""listing.yaml · keyword YAML 로드 유틸."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_listing_config(root: Path) -> dict[str, Any]:
  """config/listing.yaml 정본 설정을 읽는다."""
  path = root / "config" / "listing.yaml"
  # yaml.safe_load: YAML을 Python dict로 파싱한다. safe_load는 임의 객체 생성(!!python)을 막아 보안상 안전하다.
  # listing.yaml에는 ingest·coupang·naver_shopping_seo 등 파이프라인 전역 설정이 들어 있다.
  # encoding=utf-8로 한글 키워드·면책 문구를 깨짐 없이 읽는다.
  with open(path, encoding="utf-8") as f:
    return yaml.safe_load(f)


def load_keyword_context(keyword_yaml: Path) -> dict[str, Any]:
  """keyword-scout YAML 또는 listing 전용 YAML을 파이프라인 공통 형식으로 정규화한다."""
  # keyword-scout batch YAML(keywords 리스트)과 listing 전용 YAML(seed 직접) 두 형식을 모두 수용한다.
  # safe_load 실패 시 None이 올 수 있어 `or {}`로 빈 dict 폴백한다.
  with open(keyword_yaml, encoding="utf-8") as f:
    raw = yaml.safe_load(f) or {}

  # listing 전용 형식(seed 직접 지정)이면 그대로 사용
  if "seed" in raw:
    return _normalize_keyword_ctx(raw)

  # keyword-scout batch 형식(keywords 리스트)이면 첫 항목 query를 seed로 사용
  keywords = raw.get("keywords") or []
  if keywords:
    first = keywords[0]
    return _normalize_keyword_ctx(
      {
        "seed": first.get("query") or first.get("id") or "product",
        "related": [k.get("query", "") for k in keywords[1:6] if k.get("query")],
        "risk": first.get("tags") or [],
        "listing": raw.get("listing") or {},
      }
    )

  return _normalize_keyword_ctx({"seed": "product", "related": [], "risk": [], "listing": {}})


def _normalize_keyword_ctx(raw: dict[str, Any]) -> dict[str, Any]:
  """seed·related·risk·listing 필드를 일관된 dict로 만든다."""
  listing = raw.get("listing") or {}
  related = raw.get("related") or []
  if isinstance(related, str):
    related = [related]
  risk = raw.get("risk") or []
  if isinstance(risk, str):
    risk = [risk]
  return {
    "seed": str(raw.get("seed", "product")),
    "related": [str(r) for r in related],
    "risk": [str(r) for r in risk],
    "listing": listing,
  }
