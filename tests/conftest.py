"""pytest 공통 fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def root() -> Path:
  return ROOT


@pytest.fixture
def config(root: Path) -> dict:
  with open(root / "config" / "listing.yaml", encoding="utf-8") as f:
    return yaml.safe_load(f)


@pytest.fixture
def keyword_yaml() -> Path:
  return FIXTURES / "keyword_clip_lens.yaml"


@pytest.fixture
def aliexpress_html() -> str:
  return (FIXTURES / "aliexpress_page.html").read_text(encoding="utf-8")


@pytest.fixture
def parity_manifest(root: Path) -> dict:
  path = root / "reference/clip-lens-sample/aliexpress-images/manifest.json"
  return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def sample_jpg(tmp_path: Path) -> Path:
  """테스트용 JPG — 중앙 빨간 사각형 + 회색 배경."""
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
