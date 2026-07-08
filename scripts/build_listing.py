#!/usr/bin/env python3
"""listing-forge CLI — ingest / build (Phase 1 스켈레톤)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Path(__file__).resolve().parents[1]: scripts/의 상위 = 프로젝트 루트(listing-forge).
# sys.path.insert: `from src.pipeline` import 시 src 패키지를 찾을 수 있게 PYTHONPATH를 런타임에 추가한다.
# CLI는 패키지 설치(pip install -e .) 없이도 `python scripts/build_listing.py`로 바로 실행 가능해야 한다.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import ListingPipeline  # noqa: E402


def main() -> int:
  # argparse.ArgumentParser: ingest/build 서브커맨드 CLI를 선언적으로 정의한다.
  # add_subparsers(dest="cmd"): 첫 번째 인자로 하위 명령(ingest|build)을 분기한다.
  # parse_args(): sys.argv를 파싱해 Namespace 객체로 반환 — 미지정 required 인자 시 SystemExit(2).
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
  # ListingPipeline: ingest→process→render→score 오케스트레이션 진입점.
  # root=ROOT로 config/listing.yaml·templates/ 경로 기준을 프로젝트 루트에 고정한다.
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
  # SystemExit(main()): 종료 코드(0=성공)를 셸에 반환한다. raise로 호출해 finally 블록도 정상 실행된다.
  raise SystemExit(main())
