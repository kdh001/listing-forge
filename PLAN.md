# PLAN — listing-forge

> **PRD**: `PRD.md` · **Architecture**: `ARCHITECTURE.md` · **scout**: `../keyword-scout/`  
> **이관**: `clip-lens-page` → `reference/clip-lens-sample/` (2026-07-03)

## 0. 목표

알리/1688 URL + keyword-scout YAML → **쿠팡 JPG** + **네이버 HTML 2종** + CSV/manifest.

```
keyword-scout YAML → URL → hybrid ingest → Tier A/B → copy → render → output/
```

| Phase | 범위 | 상태 |
|:---:|---|:---:|
| **0** | kickoff · reference 이관 · 스캐폴드 | ✅ |
| **1** | PublicParser · Tier A · placeholder HTML | 📋 |
| **2** | Tier B Gemini · 한글 카피 · CSV | 📋 |
| **3** | Playwright · 1688 · scout E2E | 📋 |
| **4** | 로컬 웹 UI | 📋 |

## 1. reference/clip-lens-sample (이관 목록)

| 원본 (clip-lens-page) | 용도 |
|---|---|
| `naver-detail.html` | 네이버 placeholder 패턴 정본 → `templates/naver_detail.reference.html` |
| `naver-store-images/*.csv` | 파일명·SEO 샘플 → `templates/naver_images_meta.sample.csv` |
| `AI_UPSCALE_PROMPTS.md` | Gemini 프롬프트 → `prompts/image_tier_reference.md` |
| `aliexpress-images/manifest.json` | parity 테스트 기대값 |
| `aliexpress-images/README.md` | 갤러리/상세 분류 규칙 |
| `index.html` | 로컬 미리보기 참고 |

이미지 바이너리는 `.gitignore` — 로컬 `reference/clip-lens-sample/` 에 유지.

## 2. keyword-scout 연동

- `--keyword-yaml ../keyword-scout/keywords/seed.yaml`
- 읽기: `seed`, `related`, `risk`, (선택) `listing.category_tag`
- `integrations/keyword-scout.md` 참고

## 3. 산출물 레이아웃

```
output/{sku_id}_{YYYYMMDD}/
├── source/           # 원본 다운로드
├── coupang/          # 01_main_....jpg
├── naver/
│   ├── detail_placeholders.html
│   └── detail_final.html
├── naver-store-images/
├── naver_images_meta.csv
├── manifest.json
└── DISCLAIMER.md
```

## 4. Git (필수)

kickoff G-1~G-6 · 구현 feature/T-n · push 시 `PROGRESS.md` (vault project-progress 훅)

## 5. 다음 액션

- [ ] `scripts/build_listing.py` Phase 1 ingest 스텁 → parity URL
- [ ] Jinja `templates/naver_detail.j2` ← reference HTML 분해
- [ ] Tier A Pillow 리사이즈
