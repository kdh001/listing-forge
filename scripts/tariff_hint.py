#!/usr/bin/env python3
"""listing-forge → ecommerce-tariff-rag HS 힌트 CLI.

예시:
  # 사전: 다른 터미널에서 tariff-rag serve --port 8787
  python scripts/tariff_hint.py --sku "리튬 보조배터리 10000mAh"
  python scripts/tariff_hint.py --sku "..." --mode subprocess
  python scripts/tariff_hint.py --mode json --from-json path/to/hint.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Path(__file__).resolve().parents[1]: scripts/ 상위 = listing-forge 루트.
# sys.path.insert: pip install 없이 `python scripts/...`로 src.* import 가능하게 한다.
# CLI 진입점은 패키지 설치를 강제하지 않는 listing-forge 관례를 따른다.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.integrations.tariff_rag_client import (  # noqa: E402
  TariffHintError,
  fetch_tariff_hint,
)


def main() -> int:
  # argparse: sku/mode/출력 옵션을 선언한다.
  # --mode auto가 기본 — serve가 있으면 HTTP, 없으면 CLI 폴백.
  # 종료코드: 0 성공, 1 힌트 실패, 2 인자 오류.
  parser = argparse.ArgumentParser(
    description="listing-forge — ecommerce-tariff-rag HS 힌트 조회"
  )
  parser.add_argument("--sku", default="", help="상품명/SKU 텍스트")
  parser.add_argument(
    "--mode",
    choices=["auto", "http", "subprocess", "json"],
    default="auto",
  )
  parser.add_argument("--base-url", default=None, help="기본 http://127.0.0.1:8787")
  parser.add_argument("--from-json", type=Path, default=None, help="오프라인 hint JSON")
  parser.add_argument("--top-k", type=int, default=None)
  parser.add_argument("--alpha", type=float, default=None)
  parser.add_argument("--out", type=Path, default=None, help="응답 JSON 저장 경로")
  parser.add_argument(
    "--require-usable",
    action="store_true",
    help="자동 기입 가능(status=ok 등)이 아니면 exit 1",
  )
  args = parser.parse_args()

  if args.mode != "json" and not (args.sku or "").strip():
    parser.error("--sku 가 필요합니다 (mode=json 제외)")

  try:
    hint = fetch_tariff_hint(
      args.sku,
      mode=args.mode,
      base_url=args.base_url,
      json_path=args.from_json,
      top_k=args.top_k,
      alpha=args.alpha,
    )
  except TariffHintError as exc:
    print(f"[tariff-hint] ERROR: {exc}", file=sys.stderr)
    return 1

  # json.dumps: 한글 HS 설명을 깨지 않게 ensure_ascii=False.
  # indent=2로 사람이 읽고 listing-forge 산출물에 붙이기 쉽게 한다.
  # --out이 있으면 파일에도 동일 payload를 쓴다.
  text = json.dumps(hint.raw, ensure_ascii=False, indent=2)
  print(text)
  if args.out:
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text + "\n", encoding="utf-8")

  print(
    f"[tariff-hint] mode={hint.mode_used} status={hint.status} "
    f"usable={hint.usable_for_auto_fill}",
    file=sys.stderr,
  )
  print(f"[tariff-hint] disclaimer: {hint.disclaimer[:80]}…", file=sys.stderr)

  if args.require_usable and not hint.usable_for_auto_fill:
    print("[tariff-hint] 자동 기입 불가 — 수동 확인 필요", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
