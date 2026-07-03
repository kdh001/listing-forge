"""이미지 URL → 로컬 파일 다운로드."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class ImageDownloader:
  """HTTP로 이미지를 받아 source/ 하위 폴더에 저장한다."""

  def __init__(self) -> None:
    self._session = requests.Session()
    self._session.headers.update({"User-Agent": "listing-forge/0.1"})

  def download(self, url: str, dest: Path) -> dict[str, Any]:
    """단일 URL을 dest 경로에 저장하고 bytes·상태를 반환한다."""
    dest.parent.mkdir(parents=True, exist_ok=True)
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
