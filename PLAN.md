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
| **2.5** | **쿠팡 흰 배경 정규화 · 상위노출 점수제** | 📋 |
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
├── source/                       # 원본 다운로드
├── coupang/
│   ├── 01_main_....jpg           # 대표이미지 — 흰 배경 필수
│   ├── 02_sub_....jpg ~ 06+      # 추가이미지 — 최소 5개
│   └── bg_normalize_report.json  # 배경 처리 로그
├── coupang_meta/
│   ├── attributes.csv            # Rec.Attr 상품속성
│   ├── tags.json                 # 태그 20개
│   └── title.txt                 # 20자 내외 상품명
├── coupang_score_report.md       # 상위노출 점수 체크리스트 (75점 기준)
├── naver/
│   ├── detail_placeholders.html
│   └── detail_final.html
├── naver-store-images/
├── naver_images_meta.csv
├── manifest.json
└── DISCLAIMER.md
```

## 3.1 쿠팡 흰 배경 정규화 (Phase 2.5)

- 대표이미지(coupang 01_main)만 필수 대상. 추가이미지는 선택.
- 1차: `rembg`(U²-Net 로컬 세그멘테이션)로 제품 누끼 → 순백(`#FFFFFF`) 캔버스에 합성
- 검증: 이미지 테두리 픽셀 샘플링 → 흰색 비율이 `config/listing.yaml`의 `min_white_ratio` 미달이면 실패 판정
- 폴백: Gemini 이미지 편집 (`prompts/image_white_bg.md`) — "제품은 그대로 유지, 배경만 흰색으로"
- 원칙 2(hybrid ingest)와 동일하게 **단계 skip 금지** — rembg 실패를 조용히 무시하지 않고 반드시 Gemini 폴백 또는 실패 로그 남김

## 3.2 쿠팡 상위노출 점수제 (Phase 2.5)

- 기준: `config/listing.yaml` → `coupang.ranking_score` (통과 75점)
- 자동 채점 4항목(속성·태그20·이미지수·브랜드가산) + 체크리스트 1항목(OTA FILL, 수동 확인)
- 산출: `coupang_score_report.md` — 항목별 점수·합계·75점 미달 시 경고 배너
- scout risk 원칙(§CLAUDE.md 4)과 동일하게 **경고만 하고 등록 자체를 막지 않음**

## 4. Git (필수)

kickoff G-1~G-6 · 구현 feature/T-n · push 시 `PROGRESS.md` (vault project-progress 훅)

## 5. 다음 액션

- [ ] `scripts/build_listing.py` Phase 1 ingest 스텁 → parity URL
- [ ] Jinja `templates/naver_detail.j2` ← reference HTML 분해
- [ ] Tier A Pillow 리사이즈
- [ ] `BackgroundNormalizer` rembg 도입 · 흰 배경 판정 임계값 튜닝
- [ ] `CoupangScoreChecker` 75점 채점 로직 · 리포트 템플릿
