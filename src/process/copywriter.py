"""한글 상세 카피 · 쿠팡 20자 · 네이버 SEO 상품명 생성."""

from __future__ import annotations

from typing import Any

from src.process.gemini_client import GeminiClient
from src.render.seo_rules import NaverShoppingSeoRules


class Copywriter:
  """scout 키워드·risk·네이버 SEO를 반영한 카피·상품명을 생성한다."""

  def __init__(self, config: dict[str, Any], gemini: GeminiClient) -> None:
    self.config = config
    self.gemini = gemini
    self.seo = NaverShoppingSeoRules(config)
    title_max = config.get("coupang", {}).get("ranking_score", {}).get("title_max_chars", 20)
    self.title_max_chars = int(title_max)

  def build_context(self, keyword_ctx: dict[str, Any], product_title: str) -> dict[str, str]:
    """Jinja·CSV에 넣을 카피 dict."""
    seed = keyword_ctx.get("seed", "상품")
    related = keyword_ctx.get("related") or []
    related_str = ", ".join(related[:5]) if related else seed

    listing_title = self.seo.build_listing_title(seed, related)
    hook = self.seo.sanitize_hook(f"{seed}로 일상 촬영의 폭을 넓혀보세요.")
    section_title = f"왜 {seed}인가요?"
    section_body = (
      f"<strong>{seed}</strong>는 {related_str} 등 핵심 키워드에 최적화된 상품입니다.<br>"
      f"원본 상품명: {product_title[:80]}"
    )

    if self.gemini.available:
      prompt = (
        f"스마트스토어 상세페이지용 한글 카피 2문장을 작성해줘. "
        f"키워드: {seed}, 연관: {related_str}. "
        f"{self.seo.llm_copy_constraints()}"
      )
      extra = self.gemini.generate_text(prompt)
      if extra:
        section_body += f"<br><br>{extra}"

    risk_disclaimer = self._risk_disclaimer(keyword_ctx)

    return {
      "product_title": listing_title,
      "hook_line": hook,
      "section_title": section_title,
      "section_body": section_body,
      "risk_disclaimer": risk_disclaimer,
      "coupang_title": self.coupang_title(seed),
    }

  def coupang_title(self, seed: str) -> str:
    """쿠팡 상품명 — SEO 정규화 후 title_max_chars 이내."""
    title = self.seo.sanitize_title(seed.strip(), max_chars=self.title_max_chars)
    return title

  def _risk_disclaimer(self, keyword_ctx: dict[str, Any]) -> str:
    """risk 태그에 따른 면책 문구."""
    disclaimers = self.config.get("risk_disclaimers", {})
    risks = keyword_ctx.get("risk") or []
    parts: list[str] = []
    for tag in risks:
      if tag in disclaimers:
        parts.append(disclaimers[tag])
      if tag == "kc-medical":
        parts.append(disclaimers.get("kc-medical", ""))
    return " ".join(p for p in parts if p)
