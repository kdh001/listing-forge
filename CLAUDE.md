# listing-forge — Agent rules

> PRD: `PRD.md` · PLAN: `PLAN.md` · TASKS: `TASKS.md` · scout: `../keyword-scout/`

## 원칙

1. **reference 우선** — 네이버 HTML·CSV·이미지 네이밍은 `reference/clip-lens-sample`·`templates/` 정본 따름
2. **hybrid ingest** — public 파싱 실패 시 Playwright → manual_drop; 단계 skip 금지
3. **Tier A/B** — 제품컷은 텍스트 추가 금지 · 설명컷만 Gemini 한글화
4. **scout risk** — `kc-medical` 등이면 자동 등록 초안 생성 금지, 경고만
5. **한국어 주석** — Python 한 줄마다

## Git

kickoff G-1~G-6 · feature/T-n · push 전 PROGRESS (vault `scripts/project-progress/`)

## 로컬 실행 (예정)

```bash
python scripts/build_listing.py build \
  --url "https://ko.aliexpress.com/item/1005009287952594.html" \
  --keyword-yaml ../keyword-scout/keywords/seed.yaml \
  --platform both
```

## Parity 테스트 URL

`config/listing.yaml` → `reference.clip_lens_sample.parity_test_url`
