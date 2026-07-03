---
title: "listing-forge"
slug: listing-forge
status: active
created: 2026-07-03
updated: 2026-07-03
git_remote: ""
project_root: "~/Desktop/project/listing-forge/"
kickoff_mode: full
related:
  - "../keyword-scout/PRD.md"
  - "./reference/clip-lens-sample/"
tags: [prd, projects, ecommerce, sourcing]
---

# PRD — listing-forge

> **한 줄**: keyword-scout로 고른 키워드·SKU에 대해 알리/1688 URL → **쿠팡 JPG** + **네이버 HTML 2종** 자동 생성.  
> **레퍼런스 이관**: `clip-lens-page` → `reference/clip-lens-sample/` (2026-07-03)

## 1. 문제·타겟

| | 내용 |
|---|---|
| **타겟** | 본인 — 쿠팡·네이버 스마트스토어 병행 소싱 |
| **Pain** | 키워드는 keyword-scout, **상세 이미지·한글화·HTML**은 clip-lens-page 수동(2~4h/SKU) |
| **현재 대안** | 수동 다운로드 · Canva · 에디터 직접 편집 |

## 2. 목표·성공 기준

| 유형 | 정의 |
|---|---|
| **North Star** | URL 1개 → 30분 내 업로드 가능 산출물 폴더 |
| **MVP** | 하이브리드 수집 · Tier A/B 이미지 · placeholder HTML · coupang JPG · CSV 메타 |
| **Parity** | `reference/clip-lens-sample` 알리 URL과 동등 품질 E2E 1회 |
| **Out of scope** | Wing/스마트스토어 API 자동 등록 · KC 단정 · 가격 동기화 |

## 3. 사용자 스토리

```mermaid
flowchart LR
  KS[keyword-scout] --> U[URL 붙여넣기]
  U --> LF[listing-forge CLI]
  LF --> C[coupang/*.jpg]
  LF --> N[naver/*.html]
  LF --> M[manifest + CSV]
```

1. keyword-scout → 키워드 YAML 확정  
2. 1688/알리 URL 복사  
3. `python scripts/build_listing.py build --url ... --keyword-yaml ...`  
4. 쿠팡 JPG 업로드 · 네이버 placeholder HTML 붙여넣기  

## 4. 기능 Must / Won't

### Must

| ID | 기능 |
|:---:|---|
| F1 | 하이브리드 수집 (public → Playwright → manual_drop) |
| F2 | 이미지 gallery/detail/junk 분류 |
| F3 | Tier A 업스케일 · Tier B Gemini 한글화 |
| F4 | 한글 상세 카피 (scout 키워드·risk 반영) |
| F5 | 네이버 `detail_placeholders.html` + `detail_final.html` |
| F6 | 쿠팡 JPG + `naver_images_meta.csv` |
| F7 | keyword-scout `--keyword-yaml` 연동 |
| F8 | `manifest.json` + disclaimer |

### Won't (v1)

- 마켓 API 자동 등록  
- 1688 로그인 필수 전제  

### Later

- 로컬 웹 UI · 배치 · scout HTTP 연동  

## 5. 비기능

| 항목 | 요구 |
|---|---|
| API | Gemini 호출 상한 `max_tier_b_images` |
| 법무 | `DISCLAIMER.md` · risk 태그 경고 |
| 봇 | Playwright 실패 시 manual_drop 문서화 |

## 6. 아키텍처

> 정본: `./ARCHITECTURE.md`

## 7. Git · kickoff

| 단계 | 상태 |
|:---:|---|
| G-1~G-3 | kickoff 시 |
| A-1~A-6 | `ARCHITECTURE.md` |

## 8. 다음 액션

- [ ] Phase 1: PublicParser + Tier A + placeholder HTML  
- [ ] clip-lens parity URL E2E  
- [ ] Tier B Gemini + 카피 생성  
