"""tariff_rag_client.py — ecommerce-tariff-rag HS 힌트 소비자.

우선순위: HTTP(/api/hint) → subprocess(tariff-rag hint) → 오프라인 JSON 로드.
응답에 disclaimer가 없으면 사용하지 않는다(날조·법적 단정 방지).
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# requests: listing-forge가 이미 쓰는 HTTP 클라이언트. httpx 의존성 추가 없이 통일.
# timeout을 짧게 잡아 serve가 꺼져 있으면 빠르게 subprocess 폴백으로 넘어간다.
# 실패 시 TariffHintError 또는 None(auto 모드) — 호출부가 status를 검사한다.
import requests

Mode = Literal["auto", "http", "subprocess", "json"]

DEFAULT_BASE_URL = "http://127.0.0.1:8787"
SCHEMA_VERSION = "tariff-hint-v1"


class TariffHintError(RuntimeError):
  """힌트 조회 실패 (네트워크·CLI·스키마)."""


@dataclass
class TariffHint:
  """tariff-hint-v1 응답을 listing-forge가 쓰기 쉽게 감싼다."""

  raw: dict[str, Any]
  mode_used: str
  sku_text: str = ""
  status: str = "low_confidence"
  hs_candidates: list[dict[str, Any]] = field(default_factory=list)
  tariff_rate_pct: float | None = None
  category_hint: str | None = None
  disclaimer: str = ""
  sources: list[dict[str, Any]] = field(default_factory=list)
  staleness_warnings: list[str] = field(default_factory=list)
  answer_md: str = ""

  @property
  def usable_for_auto_fill(self) -> bool:
    """status=ok 이고 disclaimer·sources가 있을 때만 자동 기입 후보."""
    return (
      self.status == "ok"
      and bool(self.disclaimer.strip())
      and len(self.sources) >= 1
      and len(self.hs_candidates) >= 1
    )


def _validate_hint(payload: dict[str, Any]) -> dict[str, Any]:
  """필수 필드·면책을 검증한다. 실패 시 TariffHintError."""
  if not isinstance(payload, dict):
    raise TariffHintError("힌트 응답이 JSON object가 아닙니다")
  disclaimer = str(payload.get("disclaimer") or "").strip()
  if not disclaimer:
    raise TariffHintError("disclaimer가 비어 있는 응답은 사용할 수 없습니다")
  schema = payload.get("schema_version") or SCHEMA_VERSION
  if schema != SCHEMA_VERSION:
    raise TariffHintError(f"unsupported schema_version={schema!r}")
  return payload


def _to_hint(payload: dict[str, Any], *, mode_used: str) -> TariffHint:
  """검증된 dict → TariffHint."""
  data = _validate_hint(payload)
  rate = data.get("tariff_rate_pct")
  return TariffHint(
    raw=data,
    mode_used=mode_used,
    sku_text=str(data.get("sku_text") or ""),
    status=str(data.get("status") or "low_confidence"),
    hs_candidates=list(data.get("hs_candidates") or []),
    tariff_rate_pct=float(rate) if rate is not None else None,
    category_hint=data.get("category_hint"),
    disclaimer=str(data.get("disclaimer") or ""),
    sources=list(data.get("sources") or []),
    staleness_warnings=list(data.get("staleness_warnings") or []),
    answer_md=str(data.get("answer_md") or ""),
  )


@dataclass
class TariffRagClient:
  """ecommerce-tariff-rag 로컬 서버/CLI 클라이언트."""

  base_url: str = field(
    default_factory=lambda: os.getenv("TARIFF_RAG_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
  )
  cli_bin: str = field(
    default_factory=lambda: os.getenv("TARIFF_RAG_CLI", "tariff-rag")
  )
  timeout_sec: float = 30.0

  def hint_http(self, sku: str, *, top_k: int | None = None, alpha: float | None = None) -> TariffHint:
    """POST {base}/api/hint → tariff-hint-v1."""
    url = f"{self.base_url}/api/hint"
    body: dict[str, Any] = {"sku": sku}
    if top_k is not None:
      body["top_k"] = top_k
    if alpha is not None:
      body["alpha"] = alpha
    try:
      # requests.post: 로컬 tariff-rag serve의 /api/hint JSON 계약을 호출한다.
      # subprocess보다 빠르고 파이프라인 임베드에 유리하다(서버가 떠 있을 때).
      # 연결 실패·4xx/5xx → RequestException / TariffHintError.
      resp = requests.post(url, json=body, timeout=self.timeout_sec)
      resp.raise_for_status()
      return _to_hint(resp.json(), mode_used="http")
    except requests.RequestException as exc:
      raise TariffHintError(f"HTTP hint 실패 ({url}): {exc}") from exc

  def hint_subprocess(
    self,
    sku: str,
    *,
    extra_args: list[str] | None = None,
  ) -> TariffHint:
    """`tariff-rag hint --sku ... --json` 서브프로세스."""
    cmd = [self.cli_bin, "hint", "--sku", sku, "--json"]
    if extra_args:
      cmd.extend(extra_args)
    try:
      # subprocess.run: PATH의 tariff-rag CLI를 호출한다.
      # serve 없이 동작하는 폴백 — listing-forge와 동일 머신에 패키지가 설치돼 있어야 한다.
      # check=False 후 returncode·stdout JSON을 검사한다.
      proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=self.timeout_sec,
        check=False,
      )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
      raise TariffHintError(f"subprocess hint 실패: {exc}") from exc
    if proc.returncode != 0:
      err = (proc.stderr or proc.stdout or "").strip()[:400]
      raise TariffHintError(f"tariff-rag exit={proc.returncode}: {err}")
    try:
      payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
      raise TariffHintError("subprocess stdout이 JSON이 아닙니다") from exc
    return _to_hint(payload, mode_used="subprocess")

  def hint_json_file(self, path: Path) -> TariffHint:
    """미리 저장한 hint JSON을 로드 (오프라인)."""
    if not path.is_file():
      raise TariffHintError(f"JSON 파일 없음: {path}")
    # json.loads: 오프라인 fixture·사전 export된 hint를 검증 후 반환한다.
    # 네트워크/CLI가 없을 때 계약만 맞춰 파이프라인을 돌리기 위함이다.
    # disclaimer 누락 시 _validate_hint가 거부한다.
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _to_hint(payload, mode_used="json")

  def hint(
    self,
    sku: str,
    *,
    mode: Mode = "auto",
    json_path: Path | None = None,
    top_k: int | None = None,
    alpha: float | None = None,
  ) -> TariffHint:
    """mode에 따라 HS 힌트를 가져온다. auto=http→subprocess→(json)."""
    sku = (sku or "").strip()
    if not sku and mode != "json":
      raise TariffHintError("sku가 비어 있습니다")

    if mode == "http":
      return self.hint_http(sku, top_k=top_k, alpha=alpha)
    if mode == "subprocess":
      return self.hint_subprocess(sku)
    if mode == "json":
      if json_path is None:
        raise TariffHintError("mode=json 이면 json_path가 필요합니다")
      return self.hint_json_file(json_path)

    # auto
    try:
      return self.hint_http(sku, top_k=top_k, alpha=alpha)
    except TariffHintError:
      pass
    try:
      return self.hint_subprocess(sku)
    except TariffHintError:
      pass
    if json_path is not None:
      return self.hint_json_file(json_path)
    raise TariffHintError(
      "auto 실패: HTTP·subprocess 모두 불가. "
      "tariff-rag serve 또는 `pip install -e` 후 CLI를 확인하세요."
    )


def fetch_tariff_hint(
  sku: str,
  *,
  mode: Mode = "auto",
  base_url: str | None = None,
  json_path: Path | None = None,
  top_k: int | None = None,
  alpha: float | None = None,
) -> TariffHint:
  """모듈 수준 편의 함수 — CLI·파이프라인에서 한 줄 호출."""
  client = TariffRagClient(base_url=base_url or os.getenv("TARIFF_RAG_BASE_URL", DEFAULT_BASE_URL))
  return client.hint(
    sku,
    mode=mode,
    json_path=json_path,
    top_k=top_k,
    alpha=alpha,
  )
