"""네이버 placeholder / final HTML 렌더링 (Jinja2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class NaverRenderer:
  """reference HTML 구조를 Jinja2로 렌더링한다."""

  def __init__(self, root: Path) -> None:
    self.root = root
    self.env = Environment(
      loader=FileSystemLoader(root / "templates"),
      autoescape=select_autoescape(["html", "xml"]),
    )

  def render_placeholder(self, ctx: dict[str, Any], image_slots: list[dict[str, str]]) -> str:
    """점선 박스 placeholder HTML을 생성한다."""
    tpl = self.env.get_template("naver_detail.j2")
    return tpl.render(mode="placeholder", image_slots=image_slots, **ctx)

  def render_final(self, ctx: dict[str, Any], image_slots: list[dict[str, str]]) -> str:
    """실제 img 태그가 들어간 final HTML을 생성한다."""
    tpl = self.env.get_template("naver_detail.j2")
    return tpl.render(mode="final", image_slots=image_slots, **ctx)

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
