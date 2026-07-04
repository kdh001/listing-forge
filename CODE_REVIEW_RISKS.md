# Code Review 위험사항 — listing-forge

> 검토일: 2026-07-03 | 브랜치: main

## 🔴 Important

| Location | Finding | Reasoning |
|----------|---------|-----------|
| `templates/naver_detail.j2:33` | `section_body \| safe` HTML 이스케이프 없음 | Gemini/스크래핑 텍스트 XSS 삽입 가능 |
| `src/ingest/public_parser.py:32-35` | URL 검증 없이 HTTP GET (SSRF) | alicdn 외 호스트·사설 IP 접근 가능 |

## 🟡 Nit

| Location | Finding |
|----------|---------|
| `src/process/gemini_client.py:25-26` | Gemini 실패 broad except로 삼킴 |
| `src/config_loader.py:28-31` | batch YAML 첫 키워드만 사용 (silent misconfig) |

## 다음 진행 사항

- [ ] **P0** `\| safe` 제거, bleach/html.escape 적용
- [ ] **P0** ingest URL http(s)+허용 도메인 allowlist, private IP 차단
- [ ] **P1** Gemini 실패 시 로깅 + strict 모드 옵션
- [ ] **P2** 다키워드 배치 문서화 또는 루프 지원
