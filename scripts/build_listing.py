#!/usr/bin/env python3
"""listing-forge CLI — ingest / build (Phase 1 스켈레톤)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import ListingPipeline  # noqa: E402


def main() -> int:
  parser = argparse.ArgumentParser(description="listing-forge — 소싱 URL → 쿠팡/네이버 산출물")
  sub = parser.add_subparsers(dest="cmd", required=True)

  ingest = sub.add_parser("ingest", help="URL에서 이미지·메타만 수집")
  ingest.add_argument("--url", required=True)
  ingest.add_argument("--out", type=Path, default=None)

  build = sub.add_parser("build", help="전체 파이프라인")
  build.add_argument("--url", default=None, help="알리/1688 상품 URL")
  build.add_argument("--manual-dir", type=Path, default=None, help="수동 이미지 폴더")
  build.add_argument("--keyword-yaml", type=Path, required=True)
  build.add_argument("--platform", choices=["both", "coupang", "naver"], default="both")
  build.add_argument("--max-detail-images", type=int, default=15)

  args = parser.parse_args()
  pipe = ListingPipeline(root=ROOT)

  if args.cmd == "ingest":
    out = pipe.ingest(url=args.url, out_dir=args.out)
    print(f"ingest → {out}")
    return 0

  if args.cmd == "build":
    out = pipe.build(
      url=args.url,
      manual_dir=args.manual_dir,
      keyword_yaml=args.keyword_yaml,
      platform=args.platform,
      max_detail_images=args.max_detail_images,
    )
    print(f"build → {out}")
    return 0

  return 2


if __name__ == "__main__":
  raise SystemExit(main())
