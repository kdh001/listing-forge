"""쿠팡·네이버 공통 상세 HTML 렌더링 (Jinja2 + 네이버 SEO)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.render.seo_rules import NaverShoppingSeoRules


class DetailHtmlRenderer:
  """reference HTML 구조 + 네이버쇼핑 SEO 가이드를 Jinja2로 렌더링한다."""

  def __init__(self, root: Path, config: dict[str, Any] | None = None) -> None:
    self.root = root
    self.config = config or {}
    self.seo = NaverShoppingSeoRules(self.config)
    # Jinja2 Environment: templates/ 디렉터리에서 .j2 파일을 로드해 HTML 문자열을 생성한다.
    # FileSystemLoader: marketplace_detail.j2 등 템플릿 파일 경로 기준.
    # select_autoescape(["html","xml"]): XSS 방지용 자동 이스케이프 — |safe 필터 사용 구간은 예외.
    self.env = Environment(
      loader=FileSystemLoader(root / "templates"),
      autoescape=select_autoescape(["html", "xml"]),
    )
    html_cfg = self.config.get("marketplace_detail_html", {})
    self.template_name = html_cfg.get("template", "marketplace_detail.j2")
    store = html_cfg.get("image_store_dir", "naver-store-images")
    self.image_base = f"../{store}"

  def _base_ctx(self, ctx: dict[str, Any]) -> dict[str, Any]:
    """SEO 힌트·이미지 경로를 렌더 컨텍스트에 병합."""
    merged = {**self.seo.html_render_hints(), **ctx}
    merged["image_base"] = self.image_base
    return merged

  def render_placeholder(self, ctx: dict[str, Any], image_slots: list[dict[str, str]]) -> str:
    """점선 박스 placeholder HTML — SEO 체크리스트 포함."""
    tpl = self.env.get_template(self.template_name)
    # tpl.render: Jinja2 변수 치환 → 최종 HTML str. mode=placeholder면 점선 박스·체크리스트 출력.
    return tpl.render(mode="placeholder", image_slots=image_slots, **self._base_ctx(ctx))

  def render_final(self, ctx: dict[str, Any], image_slots: list[dict[str, str]]) -> str:
    """실제 img 태그 final HTML — alt·figure 시맨틱."""
    tpl = self.env.get_template(self.template_name)
    return tpl.render(mode="final", image_slots=image_slots, **self._base_ctx(ctx))

  @staticmethod
  def default_image_slots(seed: str) -> list[dict[str, str]]:
    """clip-lens 패턴 기반 기본 이미지 슬롯 목록."""
    slug = seed.replace(" ", "")[:16]
    roles = [
      ("01", "대표", f"01_대표_{slug}_스마트폰장착_휴대폰렌즈.jpg", "대표 이미지"),
      ("02", "패키지", f"02_패키지_{slug}_구성전경_휴대폰렌즈.jpg", "제품 패키지"),
      ("03", "구성", f"03_구성_{slug}_3가지렌즈_휴대폰렌즈.jpg", "구성 한눈에"),
    ]
    return [{"seq": r, "role": role, "filename": fn, "caption": cap} for r, role, fn, cap in roles]


# 하위 호환 별칭
NaverRenderer = DetailHtmlRenderer
