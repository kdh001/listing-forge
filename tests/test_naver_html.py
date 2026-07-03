"""NaverShoppingSeoRules · DetailHtmlRenderer 테스트."""

from __future__ import annotations

from src.render.naver_html import DetailHtmlRenderer, NaverRenderer
from src.render.seo_rules import NaverShoppingSeoRules


def test_sanitize_title_removes_promo(config):
  seo = NaverShoppingSeoRules(config)
  title = seo.sanitize_title("무료배송 특가 1위 클립렌즈 클립렌즈")
  assert "무료배송" not in title
  assert "특가" not in title
  assert title.count("클립렌즈") == 1


def test_build_listing_title_includes_related(config):
  seo = NaverShoppingSeoRules(config)
  title = seo.build_listing_title("클립렌즈", ["휴대폰렌즈", "스마트폰"])
  assert "클립렌즈" in title
  assert len(title) <= seo.title_recommended_chars


def test_placeholder_contains_seo_checklist(root, config):
  renderer = DetailHtmlRenderer(root, config)
  slots = renderer.default_image_slots("3in1클립렌즈")
  html = renderer.render_placeholder(
    {
      "product_title": "3in1클립렌즈",
      "hook_line": "hook",
      "section_title": "title",
      "section_body": "body",
      "risk_disclaimer": "",
    },
    slots,
  )
  assert "dashed" in html
  assert "SEO" in html
  assert slots[0]["filename"] in html


def test_final_contains_img_and_alt(root, config):
  renderer = DetailHtmlRenderer(root, config)
  slots = renderer.default_image_slots("test")
  html = renderer.render_final(
    {"product_title": "클립렌즈", "hook_line": "h", "section_title": "s", "section_body": "b", "risk_disclaimer": ""},
    slots,
  )
  assert "<img" in html
  assert 'alt="클립렌즈' in html
  assert "../naver-store-images/" in html


def test_naver_renderer_alias(root, config):
  assert NaverRenderer is DetailHtmlRenderer
