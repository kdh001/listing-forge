"""공개 페이지 파싱 (알리 og:image · runParams imagePathList · alicdn URL)."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# alicdn 상품 이미지 URL 패턴 (갤러리·상세 후보)
_ALICDN_RE = re.compile(
  r"https?://(?:ae\d+\.)?alicdn\.com/kf/[A-Za-z0-9_./\-]+\.(?:jpg|jpeg|png|webp)",
  re.IGNORECASE,
)
# runParams DCData imagePathList JSON 배열
_IMAGE_PATH_LIST_RE = re.compile(r'"imagePathList"\s*:\s*(\[[^\]]+\])')


class PublicParser:
  """알리익스프레스 공개 HTML에서 제목·갤러리·상세 이미지 URL을 추출한다."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    self._session = requests.Session()
    self._session.headers.update({"User-Agent": "listing-forge/0.1"})

  def fetch(self, url: str, html: str | None = None) -> dict[str, Any]:
    """URL(또는 주입 HTML)에서 메타·이미지 URL 목록을 반환한다."""
    if html is None:
      resp = self._session.get(url, timeout=30)
      resp.raise_for_status()
      html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    og_title = soup.find("meta", property="og:title")
    title = og_title.get("content", "") if og_title else ""

    og_images: list[str] = []
    for tag in soup.find_all("meta", property="og:image"):
      content = tag.get("content")
      if content:
        og_images.append(_canonical_url(content))

    gallery_urls = self._extract_gallery_urls(html)
    if not gallery_urls and og_images:
      gallery_urls = og_images[: self.config.get("ingest", {}).get("max_gallery_images", 8)]

    all_alicdn = self._extract_alicdn_urls(html)
    gallery_set = set(gallery_urls)
    detail_candidates = [u for u in all_alicdn if u not in gallery_set]

    return {
      "source_url": url,
      "title": title,
      "gallery_urls": gallery_urls,
      "detail_urls": detail_candidates,
      "images_og": og_images,
      "parser": "public_parser",
    }

  def _extract_gallery_urls(self, html: str) -> list[str]:
    """runParams DCData imagePathList에서 메인 갤러리 URL 6장을 추출한다."""
    match = _IMAGE_PATH_LIST_RE.search(html)
    if not match:
      return []
    try:
      urls = json.loads(match.group(1))
    except json.JSONDecodeError:
      return []
    return [_canonical_url(u) for u in urls if isinstance(u, str)]

  def _extract_alicdn_urls(self, html: str) -> list[str]:
    """HTML 전체에서 alicdn 고해상도 URL을 중복 제거·정규화해 수집한다."""
    seen: set[str] = set()
    result: list[str] = []
    for raw in _ALICDN_RE.findall(html):
      url = _canonical_url(raw)
      if _is_junk_url(url):
        continue
      if url not in seen:
        seen.add(url)
        result.append(url)
    return result


def _canonical_url(url: str) -> str:
  """썸네일 suffix(_220x220 등)를 제거해 원본에 가까운 URL로 정규화한다."""
  url = url.split(".avif")[0]
  url = re.sub(r"_\d+x\d+[a-z0-9]*\.(jpg|jpeg|png|webp)_?$", r".\1", url, flags=re.IGNORECASE)
  url = re.sub(r"\.jpg_+$", ".jpg", url)
  if url.startswith("http://"):
    url = "https://" + url[7:]
  return url


def _is_junk_url(url: str) -> bool:
  """UI 아이콘·극소형 썸네일 URL을 junk로 분류한다."""
  lower = url.lower()
  junk_tokens = ("27x27", "48x48", "60x60", "80x80", "110x64", "154x64", "232x96", "1500x180")
  if any(t in lower for t in junk_tokens):
    return True
  path = urlparse(url).path
  if path.endswith(".png") and ("x" in path.split("/")[-1]):
    return True
  return False
