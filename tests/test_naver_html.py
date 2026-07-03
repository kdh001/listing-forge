"""NaverRenderer 테스트."""

from __future__ import annotations

from src.render.naver_html import NaverRenderer


def test_placeholder_contains_dashed_box(root):
  renderer = NaverRenderer(root)
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
  assert slots[0]["filename"] in html


def test_final_contains_img_tag(root):
  renderer = NaverRenderer(root)
  slots = renderer.default_image_slots("test")
  html = renderer.render_final(
    {"product_title": "t", "hook_line": "h", "section_title": "s", "section_body": "b", "risk_disclaimer": ""},
    slots,
  )
  assert "<img" in html
