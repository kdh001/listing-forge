"""Copywriter · CoupangTagGenerator 테스트."""

from __future__ import annotations

import json

from src.config_loader import load_keyword_context
from src.process.copywriter import Copywriter
from src.process.gemini_client import GeminiClient
from src.render.coupang_tags import CoupangTagGenerator


def test_coupang_title_max_20_chars(config, keyword_yaml):
  kw = load_keyword_context(keyword_yaml)
  cw = Copywriter(config, GeminiClient(config))
  title = cw.coupang_title("아주아주아주긴상품명테스트용키워드")
  assert len(title) <= 20


def test_tags_count_20(config, keyword_yaml, tmp_path):
  kw = load_keyword_context(keyword_yaml)
  job = tmp_path / "job"
  job.mkdir()
  gen = CoupangTagGenerator(config, GeminiClient(config))
  path = gen.generate(job, kw)
  tags = json.loads(path.read_text(encoding="utf-8"))
  assert len(tags) == 20
