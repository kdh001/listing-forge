"""Playwright 폴백 — public 파싱 실패 시 브라우저 HTML 수집."""

from __future__ import annotations

import os
from typing import Any


class PlaywrightFetcher:
  """Playwright로 상품 페이지 HTML을 가져온다 (선택·폴백)."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    self.user_data_dir = os.environ.get("PLAYWRIGHT_USER_DATA_DIR", "./playwright/.auth")

  def fetch_html(self, url: str) -> str | None:
    """페이지 HTML 반환. Playwright 미설치·실패 시 None."""
    try:
      from playwright.sync_api import sync_playwright
    except ImportError:
      return None

    try:
      with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        html = page.content()
        browser.close()
        return html
    except Exception:  # noqa: BLE001
      return None

  def is_available(self) -> bool:
    """Playwright import 가능 여부."""
    try:
      import playwright  # noqa: F401

      return True
    except ImportError:
      return False
