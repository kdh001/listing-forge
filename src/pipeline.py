"""listing-forge pipeline — ingest → process → render → score."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config_loader import load_keyword_context
from src.ingest.hybrid_ingest import HybridIngest
from src.ingest.manual_drop import ManualDrop
from src.process.background_remover import BackgroundNormalizer
from src.process.copywriter import Copywriter
from src.process.gemini_client import GeminiClient
from src.process.image_tier_a import TierAProcessor
from src.render.coupang_attributes import CoupangAttributeFiller
from src.render.coupang_jpeg import CoupangExporter
from src.render.coupang_tags import CoupangTagGenerator
from src.render.csv_meta import CsvMetaWriter
from src.render.naver_html import DetailHtmlRenderer
from src.score.coupang_score import CoupangScoreChecker


@dataclass
class ListingPipeline:
  """URL + keyword YAML → 쿠팡/네이버 산출물 파이프라인."""

  root: Path

  def _load_config(self) -> dict[str, Any]:
    from src.config_loader import load_listing_config

    return load_listing_config(self.root)

  def _job_dir(self, slug: str) -> Path:
    # datetime.now().strftime: output/{slug}_{YYYYMMDD}/ 일별 job 폴더 — 재실행 시 날짜로 구분.
    stamp = datetime.now().strftime("%Y%m%d")
    safe = "".join(c for c in slug if c.isalnum() or c in "-_")[:32] or "product"
    out = self.root / "output" / f"{safe}_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    return out

  def ingest(self, url: str, out_dir: Path | None = None, *, html: str | None = None) -> Path:
    """hybrid ingest → manifest.json."""
    cfg = self._load_config()
    job = out_dir or self._job_dir("ingest")
    job.mkdir(parents=True, exist_ok=True)
    # HybridIngest.run: public_parser → playwright → manual_drop 순 폴백으로 manifest.json 생성.
    HybridIngest(cfg).run(url, job, html=html)
    return job

  def build(
    self,
    *,
    url: str | None,
    manual_dir: Path | None,
    keyword_yaml: Path,
    platform: str,
    max_detail_images: int,
    html: str | None = None,
  ) -> Path:
    """전체 빌드 파이프라인."""
    cfg = self._load_config()
    if max_detail_images:
      cfg.setdefault("ingest", {})["max_detail_images"] = max_detail_images

    # load_keyword_context: keyword-scout YAML → seed/related/risk/listing 정규 dict.
    kw_ctx = load_keyword_context(keyword_yaml)
    slug = kw_ctx["seed"].replace(" ", "")[:32]
    job = self._job_dir(slug)

    disclaimers = cfg.get("risk_disclaimers", {})
    risk_lines = [disclaimers[t] for t in kw_ctx.get("risk", []) if t in disclaimers]
    if any("kc-medical" in str(r) for r in kw_ctx.get("risk", [])):
      risk_lines.append(disclaimers.get("kc-medical", ""))
    disclaimer_body = "# 면책\n\n중국 OEM 이미지·상표·KC 인증은 판매자 책임으로 확인하세요.\n"
    if risk_lines:
      disclaimer_body += "\n".join(f"- {l}" for l in risk_lines if l) + "\n"
    (job / "DISCLAIMER.md").write_text(disclaimer_body, encoding="utf-8")

    manifest: dict[str, Any] | None = None
    if url:
      self.ingest(url, out_dir=job, html=html)
      # json.loads: hybrid ingest가 쓴 manifest.json을 파이프라인 후속 단계에 전달한다.
      manifest = json.loads((job / "manifest.json").read_text(encoding="utf-8"))
    elif manual_dir:
      manifest = ManualDrop(cfg).load(job, manual_dir=manual_dir)
    else:
      raise ValueError("--url 또는 --manual-dir 중 하나는 필수입니다.")

    gemini = GeminiClient(cfg)
    copywriter = Copywriter(cfg, gemini)
    copy_ctx = copywriter.build_context(kw_ctx, manifest.get("title", ""))

    if platform in ("both", "naver"):
      self._build_naver(job, kw_ctx, copy_ctx, manifest, cfg)

    if platform in ("both", "coupang"):
      self._build_coupang(job, kw_ctx, copy_ctx, manifest, cfg, gemini)

    # _build_detail_html: 쿠팡·네이버 동일 detail_placeholders/final HTML (Jinja2 + SEO).
    self._build_detail_html(job, copy_ctx, kw_ctx, cfg, platform)

    (job / "README.txt").write_text(
      f"platform={platform}\nkeyword_yaml={keyword_yaml}\nseed={kw_ctx['seed']}\n",
      encoding="utf-8",
    )
    return job

  def _build_naver(
    self,
    job: Path,
    kw_ctx: dict[str, Any],
    copy_ctx: dict[str, str],
    manifest: dict[str, Any],
    cfg: dict[str, Any],
  ) -> None:
    """네이버 store-images·CSV (HTML은 _build_detail_html)."""
    naver_dir = job / "naver"
    store_dir = job / "naver-store-images"
    naver_dir.mkdir(parents=True, exist_ok=True)
    store_dir.mkdir(parents=True, exist_ok=True)

    slots = DetailHtmlRenderer.default_image_slots(kw_ctx["seed"])
    tier_a = TierAProcessor(cfg)

    file_sizes: dict[str, int] = {}
    gallery = manifest.get("gallery") or []
    for i, slot in enumerate(slots):
      if i < len(gallery):
        src = job / gallery[i]["file"]
        dest = store_dir / slot["filename"]
        if src.exists():
          # TierAProcessor: 네이버 860px JPG — naver-store-images/ + CSV 바이트 컬럼.
          tier_a.process_to_jpg(src, dest, target_width=int(cfg.get("output", {}).get("naver_max_width_px", 860)))
          file_sizes[slot["filename"]] = dest.stat().st_size

    CsvMetaWriter().write(
      job / "naver_images_meta.csv",
      CsvMetaWriter().build_rows(slots, kw_ctx, file_sizes=file_sizes),
    )

  def _build_detail_html(
    self,
    job: Path,
    copy_ctx: dict[str, str],
    kw_ctx: dict[str, Any],
    cfg: dict[str, Any],
    platform: str,
  ) -> None:
    """쿠팡·네이버 동일 상세 HTML — SEO 가이드 반영."""
    html_cfg = cfg.get("marketplace_detail_html", {})
    output_dirs: list[str] = list(html_cfg.get("output_dirs") or ["naver", "coupang"])

    if platform == "naver":
      targets = ["naver"]
    elif platform == "coupang":
      targets = ["coupang"]
    else:
      targets = output_dirs

    renderer = DetailHtmlRenderer(self.root, cfg)
    slots = renderer.default_image_slots(kw_ctx["seed"])
    render_ctx = {**copy_ctx, "risk_disclaimer": copy_ctx.get("risk_disclaimer", "")}

    placeholder = renderer.render_placeholder(render_ctx, slots)
    final = renderer.render_final(render_ctx, slots)

    for dirname in targets:
      out_dir = job / dirname
      out_dir.mkdir(parents=True, exist_ok=True)
      out_dir.joinpath("detail_placeholders.html").write_text(placeholder, encoding="utf-8")
      out_dir.joinpath("detail_final.html").write_text(final, encoding="utf-8")

  def _build_coupang(
    self,
    job: Path,
    kw_ctx: dict[str, Any],
    copy_ctx: dict[str, str],
    manifest: dict[str, Any],
    cfg: dict[str, Any],
    gemini: GeminiClient,
  ) -> None:
    """쿠팡 JPG·메타·흰배경·점수."""
    slug = kw_ctx["seed"].replace(" ", "")[:16]
    exporter = CoupangExporter(cfg)
    exporter.export_gallery(job, manifest, slug)
    min_add = int(cfg.get("coupang", {}).get("min_additional_images", 5))
    exporter.copy_additional_from_detail(job, manifest, slug, min_count=min_add)

    coupang_dir = job / "coupang"
    main_images = sorted(coupang_dir.glob("01_main*.jpg"))
    if main_images:
      normalizer = BackgroundNormalizer(cfg, gemini)
      main = main_images[0]
      tmp = main.with_suffix(".norm.jpg")
      report = normalizer.normalize_main_image(main, tmp)
      if tmp.exists():
        # shutil.move: 정규화된 JPG를 01_main_*.jpg 위치로 원자적 교체.
        shutil.move(str(tmp), str(main))
      normalizer.write_report(job, [report])

    meta_dir = job / "coupang_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "title.txt").write_text(copy_ctx.get("coupang_title", kw_ctx["seed"]), encoding="utf-8")

    CoupangAttributeFiller(cfg).fill(job, kw_ctx, manifest.get("title", ""))
    CoupangTagGenerator(cfg, gemini).generate(job, kw_ctx)

    checker = CoupangScoreChecker(cfg)
    result = checker.score(job, kw_ctx)
    checker.write_report(job, result)
