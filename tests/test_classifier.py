"""ImageClassifier 단위 테스트."""

from __future__ import annotations

from src.process.classifier import ImageClassifier


def test_gallery_always_gallery(config, sample_jpg):
  # classify_file(is_gallery=True): 갤러리 슬롯은 bytes·텍스트 비율과 무관하게 gallery+A 고정.
  clf = ImageClassifier(config)
  item = clf.classify_file(sample_jpg, is_gallery=True)
  assert item.category == "gallery"
  assert item.tier == "A"


def test_large_file_is_detail(config, tmp_path):
  clf = ImageClassifier(config)
  # 150KB 이상 더미 파일 — detail_min_bytes(150000) 임계로 detail_page 분류.
  big = tmp_path / "big.bin"
  big.write_bytes(b"\x00" * 160_000)
  item = clf.classify_file(big, is_gallery=False)
  assert item.category == "detail_page"


def test_small_file_is_junk(config, tmp_path):
  clf = ImageClassifier(config)
  # thumbnail_max_bytes(100000) 미만 → junk (related_thumbnails 폴더 대상).
  small = tmp_path / "tiny.bin"
  small.write_bytes(b"\x00" * 500)
  item = clf.classify_file(small, is_gallery=False)
  assert item.category == "junk"
