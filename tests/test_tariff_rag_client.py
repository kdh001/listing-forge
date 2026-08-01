"""ecommerce-tariff-rag 소비자 단위 테스트 (HTTP/subprocess mock)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.integrations.tariff_rag_client import (
  TariffHint,
  TariffHintError,
  TariffRagClient,
  _to_hint,
  fetch_tariff_hint,
)

SAMPLE = {
  "schema_version": "tariff-hint-v1",
  "sku_text": "리튬 보조배터리",
  "status": "ok",
  "hs_candidates": [
    {"hs_code": "8507.60", "description": "리튬이온", "confidence": 0.8}
  ],
  "tariff_rate_pct": 8.0,
  "category_hint": "소형가전·액세서리",
  "sources": [
    {
      "chunk_id": "c1",
      "quote": "예시",
      "source_url": "https://www.customs.go.kr",
      "score": 0.9,
    }
  ],
  "disclaimer": "참고용 추정입니다. 실제 통관·세율·HS 확정은 관세사 확인이 필요합니다.",
  "official_lookup_urls": ["https://unipass.customs.go.kr"],
  "staleness_warnings": [],
  "answer_md": "참고",
}


def test_hint_http_ok() -> None:
  client = TariffRagClient(base_url="http://127.0.0.1:8787")
  mock_resp = MagicMock()
  mock_resp.raise_for_status = MagicMock()
  mock_resp.json.return_value = SAMPLE
  with patch("src.integrations.tariff_rag_client.requests.post", return_value=mock_resp) as post:
    hint = client.hint_http("리튬 보조배터리")
  post.assert_called_once()
  assert hint.usable_for_auto_fill is True
  assert hint.hs_candidates[0]["hs_code"] == "8507.60"
  assert "참고용" in hint.disclaimer


def test_rejects_empty_disclaimer() -> None:
  client = TariffRagClient()
  bad = {**SAMPLE, "disclaimer": ""}
  mock_resp = MagicMock()
  mock_resp.raise_for_status = MagicMock()
  mock_resp.json.return_value = bad
  with patch("src.integrations.tariff_rag_client.requests.post", return_value=mock_resp):
    with pytest.raises(TariffHintError, match="disclaimer"):
      client.hint_http("x")


def test_hint_subprocess_ok() -> None:
  client = TariffRagClient(cli_bin="tariff-rag")
  proc = MagicMock()
  proc.returncode = 0
  proc.stdout = json.dumps(SAMPLE, ensure_ascii=False)
  proc.stderr = ""
  with patch("src.integrations.tariff_rag_client.subprocess.run", return_value=proc) as run:
    hint = client.hint_subprocess("리튬 보조배터리")
  run.assert_called_once()
  assert hint.mode_used == "subprocess"
  assert hint.status == "ok"


def test_hint_json_file(tmp_path: Path) -> None:
  path = tmp_path / "hint.json"
  path.write_text(json.dumps(SAMPLE, ensure_ascii=False), encoding="utf-8")
  hint = TariffRagClient().hint_json_file(path)
  assert hint.mode_used == "json"
  assert hint.tariff_rate_pct == 8.0


def test_auto_falls_back_to_subprocess() -> None:
  client = TariffRagClient()
  fallback = _to_hint(SAMPLE, mode_used="subprocess")
  with patch.object(client, "hint_http", side_effect=TariffHintError("down")):
    with patch.object(client, "hint_subprocess", return_value=fallback):
      hint = client.hint("sku", mode="auto")
  assert hint.mode_used == "subprocess"
  assert isinstance(hint, TariffHint)


def test_fetch_tariff_hint_wrapper() -> None:
  expected = _to_hint(SAMPLE, mode_used="http")
  with patch.object(TariffRagClient, "hint", return_value=expected):
    hint = fetch_tariff_hint("x", mode="http")
  assert hint.sku_text == "리튬 보조배터리"


def test_low_confidence_not_usable() -> None:
  low = {**SAMPLE, "status": "low_confidence", "hs_candidates": []}
  hint = _to_hint(low, mode_used="http")
  assert hint.usable_for_auto_fill is False
