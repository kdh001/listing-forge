---
title: "listing-forge — Tasks"
slug: listing-forge
created: 2026-07-03
updated: 2026-07-03
source_prd: "./PRD.md"
---

# TASKS — listing-forge

## Phase 0 — kickoff · 이관

| ID | Task | DoD | 상태 |
|:---:|---|---|:---:|
| T-0 | repo 스캐폴드 + clip-lens reference 이관 | `reference/clip-lens-sample/` · templates · PRD/ARCH | ✅ |
| A-1~A-6 | ARCHITECTURE.md | Trade-off · Mermaid | ✅ 초안 |
| G-1~G-3 | git init · .gitignore · initial commit | | 📋 |

## Phase 1 — ingest + Tier A + placeholder HTML

| ID | Task | DoD | 상태 |
|:---:|---|---|:---:|
| T-1 | `PublicParser` (알리 og/runParams) | parity URL manifest 대비 URL 목록 | 📋 |
| T-2 | 이미지 다운로드 + gallery/detail 분류 | `source/` 폴더 구조 | 📋 |
| T-3 | Tier A Pillow 리사이즈 → JPG | coupang/ · 1720px | 📋 |
| T-4 | `naver_detail.j2` + placeholder HTML | reference HTML 구조 동일 | 📋 |
| T-5 | `build_listing.py ingest|build` CLI 스켈레톤 | `--url` `--keyword-yaml` | 📋 |

## Phase 2 — Gemini + 카피 + CSV

| ID | Task | DoD | 상태 |
|:---:|---|---|:---:|
| T-6 | Tier B Gemini (텍스트 많은 상세) | `prompts/image_tier_b.md` | 📋 |
| T-7 | Copywriter (한글 섹션) | scout 키워드·risk | 📋 |
| T-8 | `naver_images_meta.csv` 생성 | sample CSV 스키마 | 📋 |
| T-9 | `detail_final.html` (img 태그) | 로컬 미리보기 | 📋 |

## Phase 3 — Playwright · 1688 · E2E

| ID | Task | DoD | 상태 |
|:---:|---|---|:---:|
| T-10 | PlaywrightFetcher + manual_drop | hybrid 폴백 문서 | 📋 |
| T-11 | clip-lens parity E2E 1회 | 네이버에 실등록 가능 품질 | 📋 |

## Phase 4 — (보류)

| ID | Task | DoD | 상태 |
|:---:|---|---|:---:|
| T-12 | 로컬 웹 UI | URL + ZIP 업로드 | 📋 |
