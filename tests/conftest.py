"""pytest 공통 fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

# Path(__file__).parents[1]: tests/ → 프로젝트 루트. sys.path.insert로 src 패키지 import 가능하게 한다.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def root() -> Path:
  """프로젝트 루트 경로 — config/templates/reference 접근용."""
  return ROOT


@pytest.fixture
def config(root: Path) -> dict:
  """config/listing.yaml — pytest-safe_load로 실제 운영 설정과 동일한 dict 제공."""
  with open(root / "config" / "listing.yaml", encoding="utf-8") as f:
    return yaml.safe_load(f)


@pytest.fixture
def keyword_yaml() -> Path:
  """tests/fixtures/keyword_clip_lens.yaml — scout 형식 키워드 샘플."""
  return FIXTURES / "keyword_clip_lens.yaml"


@pytest.fixture
def aliexpress_html() -> str:
  """저장된 알리 HTML fixture — 네트워크 없이 PublicParser parity 테스트."""
  return (FIXTURES / "aliexpress_page.html").read_text(encoding="utf-8")


@pytest.fixture
def parity_manifest(root: Path) -> dict:
  """clip-lens-sample manifest.json — gallery URL 기대값 정본."""
  path = root / "reference/clip-lens-sample/aliexpress-images/manifest.json"
  return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def sample_jpg(tmp_path: Path) -> Path:
  """테스트용 JPG — 중앙 빨간 사각형 + 회색 배경."""
  # pytest tmp_path: 테스트별 격리 temp 디렉터리. Pillow Image.new로 Tier A/배경 제거 입력 생성.
  img = Image.new("RGB", (400, 400), color=(180, 180, 180))
  for x in range(120, 280):
    for y in range(120, 280):
      img.putpixel((x, y), (200, 50, 50))
  path = tmp_path / "sample.jpg"
  img.save(path, format="JPEG")
  return path


@pytest.fixture
def white_bg_jpg(tmp_path: Path) -> Path:
  """흰 배경 제품컷 테스트용."""
  img = Image.new("RGB", (400, 400), color=(255, 255, 255))
  for x in range(150, 250):
    for y in range(150, 250):
      img.putpixel((x, y), (30, 30, 30))
  path = tmp_path / "white_product.jpg"
  img.save(path, format="JPEG")
  return path
