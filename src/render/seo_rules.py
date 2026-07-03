"""네이버쇼핑 상품검색 SEO 가이드 — 상품명·상세 HTML 생성 규칙.

출처: join.shopping.naver.com FAQ catgCd=H00015 (상품검색SEO 가이드)
      shopping_product_info_provide_guide (네이버 쇼핑검색 SEO & 상품정보 제공 가이드)
"""

from __future__ import annotations

import re
from typing import Any


# 상품명·훅 문구에 넣으면 안 되는 판매/홍보 키워드 (어뷰징·신뢰도 감점)
_BANNED_PROMO_RE = re.compile(
  r"무료배송|당일발송|빠른배송|특가|할인|세일|최저가|1위|인기|가성비|"
  r"긴급|한정|품절|이벤트|사은품|무이자|적립|쿠폰|MD추천|정품|공식|"
  r"주문폭주|재입고|선착순|저렴|추천|떙처리|초특가|기획|시즌오프",
  re.IGNORECASE,
)

# 허용 특수문자: ( ) - · [ ] / & + , ~ .  — 그 외 제거
_ALLOWED_SPECIAL = set("()-·[]/&+,~.")

# 금지 특수문자 패턴 (★ ▶ ◀ 등)
_FORBIDDEN_SPECIAL_RE = re.compile(r"[★☆▶◀◆◇●○■□※♥♡]")


class NaverShoppingSeoRules:
  """네이버쇼핑 SEO 가이드 기반 상품명·카피 정규화."""

  def __init__(self, config: dict[str, Any]) -> None:
    seo = config.get("naver_shopping_seo", {})
    self.title_recommended_chars = int(seo.get("title_recommended_chars", 50))
    self.title_max_chars = int(seo.get("title_max_chars", 100))
    self.detail_max_width_px = int(seo.get("detail_max_width_px", 860))
    self.image_min_px = int(seo.get("image_min_px", 500))
    self.image_format = seo.get("image_format", "JPG")
    self.banned_promo_words: list[str] = seo.get("banned_promo_words") or []

  def sanitize_title(self, text: str, *, max_chars: int | None = None) -> str:
    """상품명 SEO — 중복·홍보·특수문자 제거, 길이 제한."""
    limit = max_chars if max_chars is not None else self.title_max_chars
    cleaned = text.strip()
    cleaned = _FORBIDDEN_SPECIAL_RE.sub("", cleaned)
    cleaned = _BANNED_PROMO_RE.sub("", cleaned)
    for word in self.banned_promo_words:
      cleaned = cleaned.replace(word, "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = self._dedupe_words(cleaned)
    cleaned = self._strip_disallowed_chars(cleaned)
    if len(cleaned) > limit:
      cleaned = cleaned[:limit].rstrip()
    return cleaned or "상품"

  def build_listing_title(self, seed: str, related: list[str] | None = None) -> str:
    """적합도 TIP — seed + 연관 키워드 1~2개, 대표 옵션 포함 권장."""
    parts = [seed.strip()]
    if related:
      for kw in related[:2]:
        kw = kw.strip()
        if kw and kw not in seed and kw not in parts:
          parts.append(kw)
    raw = " ".join(parts)
    return self.sanitize_title(raw, max_chars=self.title_recommended_chars)

  def sanitize_hook(self, text: str) -> str:
    """훅 문구 — 홍보·배송·할인 문구 제거."""
    cleaned = _BANNED_PROMO_RE.sub("", text)
    cleaned = _FORBIDDEN_SPECIAL_RE.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or text[:40]

  def llm_copy_constraints(self) -> str:
    """Gemini 등 LLM 프롬프트에 붙일 SEO 제약 문구."""
    return (
      "네이버쇼핑 SEO 가이드 준수: "
      "무료배송·할인·특가·1위·정품 등 홍보 문구 금지, "
      "키워드 중복·나열 금지, 과장·의료효능 금지, "
      "브랜드·모델·대표 옵션(색상/용량) 중심으로 간결하게."
    )

  def html_render_hints(self) -> dict[str, Any]:
    """Jinja 템플릿에 주입할 SEO·이미지 가이드."""
    return {
      "max_width_px": self.detail_max_width_px,
      "image_min_px": self.image_min_px,
      "image_format": self.image_format,
      "seo_checklist": self.checklist_for_upload(),
    }

  def checklist_for_upload(self) -> list[str]:
    """업로드 전 수동 확인용 체크리스트 (placeholder HTML에 표시)."""
    return [
      "상품명: 브랜드·모델·대표 옵션 포함, 홍보/할인/배송 문구 없음",
      "상품명: 동의어·유의어 중복 기재 금지 (50자 내외 권장)",
      "카테고리·속성·태그: keyword-scout seed/related와 일치",
      "이미지: 500px 이상 JPG, 선명·흰/단색 배경 대표컷 1장 이상",
      "이미지: 워터마크·과도한 텍스트 오버레이 없음 (Tier A 제품컷)",
      "상세 HTML: 이벤트·할인 정보는 상품명/본문이 아닌 이벤트 필드에",
      "검색 랭킹: 적합도(연관도)·인기도·신뢰도 — 어뷰징·재등록 금지",
    ]

  @staticmethod
  def _dedupe_words(text: str) -> str:
    """동일 단어 반복 제거 (어뷰징 방지)."""
    seen: set[str] = set()
    out: list[str] = []
    for word in text.split():
      key = word.lower()
      if key not in seen:
        seen.add(key)
        out.append(word)
    return " ".join(out)

  @staticmethod
  def _strip_disallowed_chars(text: str) -> str:
    """허용 목록 외 특수문자 제거."""
    buf: list[str] = []
    for ch in text:
      if ch.isalnum() or ch.isspace() or ch in _ALLOWED_SPECIAL or ("\uac00" <= ch <= "\ud7a3"):
        buf.append(ch)
    return "".join(buf)
