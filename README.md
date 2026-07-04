# listing-forge

알리/1688 소싱 URL → **쿠팡 JPG** + **네이버 스마트스토어 HTML** 자동 생성.

## 관련 프로젝트

| 프로젝트 | 역할 |
|----------|------|
| [keyword-scout](file:///Users/kimdohun/Library/Mobile%20Documents/com~apple~CloudDocs/Desktop/project/archive/keyword-scout/) | 키워드 CI/MOI/COS · `keywords/*.yaml` (iCloud 아카이브) |
| clip-lens-page | **이관됨** → `reference/clip-lens-sample/` (원본: iCloud archive) |

## 빠른 시작 (Phase 1 이후)

```bash
cd ~/Desktop/project/listing-forge
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # GEMINI_API_KEY

python scripts/build_listing.py build \
  --url "https://ko.aliexpress.com/item/1005009287952594.html" \
  --keyword-yaml "/Users/kimdohun/Library/Mobile Documents/com~apple~CloudDocs/Desktop/project/archive/keyword-scout/keywords/seed.yaml"
```

## 폴더

```
config/          listing.yaml (쿠팡 흰배경·점수제 가중치 포함)
reference/       clip-lens-sample (이관 레퍼런스)
templates/       naver HTML·CSV 샘플
prompts/         Gemini 프롬프트 (Tier A/B · 흰 배경 폴백)
src/
  ingest/        PublicParser · Playwright · manual_drop
  process/       classifier · gemini_client · background_remover · copywriter
  render/        naver_html · coupang_jpeg · coupang_attributes · coupang_tags · csv_meta
  score/         coupang_score (75점 채점)
scripts/         CLI
output/          산출물 (coupang/ · coupang_meta/ · coupang_score_report.md 포함)
```

## 쿠팡 요구사항 (신규)

- **대표이미지 흰 배경 필수** — 크롤링 원본이 흰 배경이 아니면 제품은 그대로 두고 배경만 순백으로 치환 (`src/process/background_remover.py`)
- **상위노출 점수제 (75점 이상 통과)** — 상품속성·태그20개·이미지수·브랜드가산 자동 채점, OTA FILL은 수동 체크리스트 (`src/score/coupang_score.py`, `config/listing.yaml → coupang`)

## 이관 (2026-07-03)

`clip-lens-page` 전체가 `reference/clip-lens-sample/`로 복사됨.  
이미지 바이너리는 git 제외 — 로컬 reference 폴더에 유지.
