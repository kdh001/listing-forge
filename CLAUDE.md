# listing-forge — Agent rules

> PRD: `PRD.md` · PLAN: `PLAN.md` · TASKS: `TASKS.md` · scout: iCloud `archive/keyword-scout/`

## 원칙

1. **reference 우선** — 네이버 HTML·CSV·이미지 네이밍은 `reference/clip-lens-sample`·`templates/` 정본 따름
2. **hybrid ingest** — public 파싱 실패 시 Playwright → manual_drop; 단계 skip 금지
3. **Tier A/B** — 제품컷은 텍스트 추가 금지 · 설명컷만 Gemini 한글화
4. **scout risk** — `kc-medical` 등이면 자동 등록 초안 생성 금지, 경고만
5. **한국어 주석** — Python 한 줄마다
6. **쿠팡 대표이미지 흰 배경 필수** — 제품은 그대로 두고 배경만 순백 치환 (rembg → 실패 시 Gemini 폴백); 단계 skip 금지 (원칙 2와 동일)
7. **쿠팡 상위노출 75점 기준** — `coupang_score_report.md`로 자동 채점, 미달 시 **경고만** (등록 차단 금지, 원칙 4와 동일 톤)

## Git

kickoff G-1~G-6 · feature/T-n · push 전 PROGRESS (vault `scripts/project-progress/`)

## 로컬 실행 (예정)

```bash
python scripts/build_listing.py build \
  --url "https://ko.aliexpress.com/item/1005009287952594.html" \
  --keyword-yaml "/Users/kimdohun/Library/Mobile Documents/com~apple~CloudDocs/Desktop/project/archive/keyword-scout/keywords/seed.yaml" \
  --platform both
```

## Parity 테스트 URL

`config/listing.yaml` → `reference.clip_lens_sample.parity_test_url`

## 쿠팡 규칙 정본

`config/listing.yaml` → `coupang.main_image`(흰 배경) · `coupang.ranking_score`(75점 가중치)
