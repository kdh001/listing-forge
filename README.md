# listing-forge

알리/1688 소싱 URL → **쿠팡 JPG** + **네이버 스마트스토어 HTML** 자동 생성.

## 관련 프로젝트

| 프로젝트 | 역할 |
|----------|------|
| [keyword-scout](../keyword-scout/) | 키워드 CI/MOI/COS · `keywords/*.yaml` |
| [clip-lens-page](../clip-lens-page/) | **이관됨** → `reference/clip-lens-sample/` |

## 빠른 시작 (Phase 1 이후)

```bash
cd ~/Desktop/project/listing-forge
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # GEMINI_API_KEY

python scripts/build_listing.py build \
  --url "https://ko.aliexpress.com/item/1005009287952594.html" \
  --keyword-yaml ../keyword-scout/keywords/seed.yaml
```

## 폴더

```
config/          listing.yaml
reference/       clip-lens-sample (이관 레퍼런스)
templates/       naver HTML·CSV 샘플
prompts/         Gemini 프롬프트
src/             파이프라인 (구현 중)
scripts/         CLI
output/          산출물
```

## 이관 (2026-07-03)

`clip-lens-page` 전체가 `reference/clip-lens-sample/`로 복사됨.  
이미지 바이너리는 git 제외 — 로컬 reference 폴더에 유지.
