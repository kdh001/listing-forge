"""공개 페이지 파싱 (알리 og:image · JSON-LD)."""

from __future__ import annotations

from typing import Any

import requests
from bs4 import BeautifulSoup


class PublicParser:
  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config

  def fetch(self, url: str) -> dict[str, Any]:
    """URL에서 제목·이미지 URL 목록 추출 (MVP 스텁)."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "listing-forge/0.1"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    og_title = soup.find("meta", property="og:title")
    title = og_title.get("content", "") if og_title else ""
    images: list[str] = []
    for tag in soup.find_all("meta", property="og:image"):
      content = tag.get("content")
      if content:
        images.append(content)
    return {
      "source_url": url,
      "title": title,
      "images_og": images,
      "parser": "public_parser",
      "note": "Phase 1: runParams·갤러리 분류는 T-1에서 구현",
    }
