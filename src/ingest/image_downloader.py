"""이미지 URL → 로컬 파일 다운로드."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class ImageDownloader:
  """HTTP로 이미지를 받아 source/ 하위 폴더에 저장한다."""

  def __init__(self) -> None:
    # requests.Session: TCP 연결·쿠키를 재사용해 alicdn 다중 이미지 다운로드 시 성능을 높인다.
    # User-Agent 헤더: 봇 차단을 완화하기 위해 식별 가능한 클라이언트명을 명시한다.
    self._session = requests.Session()
    self._session.headers.update({"User-Agent": "listing-forge/0.1"})

  def download(self, url: str, dest: Path) -> dict[str, Any]:
    """단일 URL을 dest 경로에 저장하고 bytes·상태를 반환한다."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    # session.get: GET 요청으로 이미지 바이너리를 받는다. timeout=60은 대용량 상세컷 대비.
    # raise_for_status(): 404·403 등 HTTP 오류 시 RequestException을 발생시켜 호출자가 ok=False로 기록할 수 있다.
    # resp.content: bytes 그대로 dest에 저장 — PIL 디코딩은 classifier/tier_a 단계에서 수행한다.
    resp = self._session.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return {"url": url, "file": str(dest), "bytes": len(resp.content), "ok": True}

  def download_many(self, items: list[tuple[str, Path]]) -> list[dict[str, Any]]:
    """(url, dest) 목록을 순차 다운로드한다."""
    results: list[dict[str, Any]] = []
    for url, dest in items:
      try:
        results.append(self.download(url, dest))
      except requests.RequestException as exc:
        results.append({"url": url, "file": str(dest), "bytes": 0, "ok": False, "error": str(exc)})
    return results
