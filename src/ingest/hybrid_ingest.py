"""hybrid ingest — public_parser → playwright → manual_drop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ingest.image_downloader import ImageDownloader
from src.ingest.public_parser import PublicParser
from src.process.classifier import ImageClassifier


class HybridIngest:
  """설정된 hybrid_order 순서로 수집을 시도한다."""

  def __init__(self, config: dict[str, Any]) -> None:
    self.config = config
    self.parser = PublicParser(config)
    self.downloader = ImageDownloader()
    self.classifier = ImageClassifier(config)

  def run(self, url: str, job_dir: Path, *, html: str | None = None) -> dict[str, Any]:
    """URL에서 이미지를 수집·다운로드·분류해 manifest dict를 반환한다."""
    # hybrid_order: config/listing.yaml ingest.hybrid_order — 실패 시 다음 단계로 폴백 (단계 skip 금지 원칙).
    order = self.config.get("ingest", {}).get("hybrid_order", ["public_parser"])
    last_error: Exception | None = None

    for step in order:
      try:
        if step == "public_parser":
          return self._run_public(url, job_dir, html=html)
        if step == "playwright":
          from src.ingest.playwright_fetcher import PlaywrightFetcher

          fetcher = PlaywrightFetcher(self.config)
          pw_html = fetcher.fetch_html(url)
          if pw_html:
            return self._run_public(url, job_dir, html=pw_html)
        if step == "manual_drop":
          from src.ingest.manual_drop import ManualDrop

          drop = ManualDrop(self.config)
          return drop.load(job_dir)
      except Exception as exc:  # noqa: BLE001 — hybrid 폴백
        last_error = exc
        continue

    raise RuntimeError(f"hybrid ingest 실패: {last_error}")

  def _run_public(self, url: str, job_dir: Path, *, html: str | None) -> dict[str, Any]:
    """PublicParser + 다운로드 + 분류."""
    meta = self.parser.fetch(url, html=html)
    source = job_dir / "source"
    gallery_dir = source / "01_gallery"
    detail_dir = source / "02_detail_page"
    junk_dir = source / "03_related_thumbnails"

    gallery_items: list[tuple[str, Path]] = []
    for i, gurl in enumerate(meta["gallery_urls"], start=1):
      ext = ".jpg" if ".jpg" in gurl.lower() else ".png"
      gallery_items.append((gurl, gallery_dir / f"gallery_{i:02d}{ext}"))

    detail_items: list[tuple[str, Path]] = []
    max_detail = int(self.config.get("ingest", {}).get("max_detail_images", 20))
    for i, durl in enumerate(meta["detail_urls"][: max_detail * 2], start=2):
      ext = ".png" if ".png" in durl.lower() else ".jpg"
      detail_items.append((durl, detail_dir / f"desc_{i:02d}{ext}"))

    # download_many: alicdn URL 목록을 순차 GET — 실패 URL은 ok=False로 manifest에 남긴다.
    dl_gallery = self.downloader.download_many(gallery_items)
    dl_detail = self.downloader.download_many(detail_items)

    gallery_files = [(Path(r["file"]), r["url"]) for r in dl_gallery if r.get("ok")]
    detail_files = [(Path(r["file"]), r["url"]) for r in dl_detail if r.get("ok")]

    # classify_manifest: 150KB 임계·Tier A/B 휴리스틱으로 gallery/detail/junk 분류.
    classified = self.classifier.classify_manifest(gallery_files, detail_files)
    junk: list[dict[str, Any]] = []
    gallery: list[dict[str, Any]] = []
    detail_page: list[dict[str, Any]] = []

    for item in classified:
      entry = {
        "file": str(item.path.relative_to(job_dir)),
        "bytes": item.bytes,
        "tier": item.tier,
        "url": item.url,
      }
      if item.category == "gallery":
        gallery.append(entry)
      elif item.category == "detail_page":
        detail_page.append(entry)
      else:
        junk_path = junk_dir / item.path.name
        junk_path.parent.mkdir(parents=True, exist_ok=True)
        if item.path.exists():
          # Path.rename: junk 분류 파일을 03_related_thumbnails/로 이동한다.
          item.path.rename(junk_path)
        entry["file"] = str(junk_path.relative_to(job_dir))
        junk.append(entry)

    manifest = {
      "source_url": url,
      "title": meta["title"],
      "parser": meta["parser"],
      "summary": {
        "gallery": len(gallery),
        "detail_page": len(detail_page),
        "related_thumbnails": len(junk),
      },
      "gallery": gallery,
      "detail_page": detail_page,
      "related_thumbnails": junk,
    }
    # json.dumps(ensure_ascii=False): 한글 title·경로를 유니코드 이스케이프 없이 manifest.json에 저장한다.
    (job_dir / "manifest.json").write_text(
      json.dumps(manifest, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    return manifest
