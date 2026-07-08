"""PublicParser 단위 테스트."""

from __future__ import annotations

from src.ingest.public_parser import PublicParser


def test_extract_gallery_urls_parity(config, aliexpress_html, parity_manifest):
  # PublicParser.fetch(html=): 네트워크 없이 fixture HTML로 runParams·og:image 파싱 검증.
  parser = PublicParser(config)
  meta = parser.fetch("https://ko.aliexpress.com/item/1005009287952594.html", html=aliexpress_html)

  assert len(meta["gallery_urls"]) == parity_manifest["summary"]["gallery"]
  expected = [g["url"] for g in parity_manifest["gallery"]]
  assert meta["gallery_urls"] == expected


def test_title_from_og(config, aliexpress_html):
  # BeautifulSoup og:title — JS 렌더 없이 메타 태그에서 제목 추출 확인.
  parser = PublicParser(config)
  meta = parser.fetch("https://example.com/item/1.html", html=aliexpress_html)
  assert "3 in 1" in meta["title"]


def test_junk_urls_filtered(config, aliexpress_html):
  parser = PublicParser(config)
  meta = parser.fetch("https://example.com/item/1.html", html=aliexpress_html)
  for url in meta["detail_urls"]:
    assert "27x27" not in url
