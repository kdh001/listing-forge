"""Gemini API 클라이언트 — Tier B · 카피 (API 키 없으면 템플릿 폴백)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class GeminiClient:
  """google-generativeai 래퍼. 키 없으면 결정적 템플릿 폴백."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    gemini_cfg = config.get("gemini", {})
    self.text_model = gemini_cfg.get("text_model", "gemini-2.0-flash")
    self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    self._model = None
    if self.api_key:
      try:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.text_model)
      except Exception:  # noqa: BLE001
        self._model = None

  @property
  def available(self) -> bool:
    """Gemini API 사용 가능 여부."""
    return self._model is not None

  def generate_text(self, prompt: str) -> str:
    """텍스트 생성. 실패·키 없음 시 빈 문자열."""
    if not self._model:
      return ""
    try:
      resp = self._model.generate_content(prompt)
      return (resp.text or "").strip()
    except Exception:  # noqa: BLE001
      return ""

  def load_prompt(self, root: Path, name: str, **vars: str) -> str:
    """prompts/{name}.md 파일을 읽고 {{var}} 치환."""
    path = root / "prompts" / name
    if not path.exists():
      return ""
    text = path.read_text(encoding="utf-8")
    for key, val in vars.items():
      text = text.replace("{{" + key + "}}", val)
    return text
