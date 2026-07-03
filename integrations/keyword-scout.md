# keyword-scout 연동

## 경로

기본: `../keyword-scout` (`config/listing.yaml` · `KEYWORD_SCOUT_ROOT`)

## CLI

```bash
python scripts/build_listing.py build \
  --url "https://..." \
  --keyword-yaml ../keyword-scout/keywords/맥세이프선풍기.yaml
```

## YAML에서 읽는 필드

| 필드 | 용도 |
|------|------|
| `seed` | H1·파일명 slug·CSV 검색키워드 |
| `related` | 상세 본문 SEO |
| `risk` | `kc-medical` / `fad` → disclaimer 블록 |
| `listing.category_tag` | (선택) CSV 카테고리 |
| `listing.scout_report` | (선택) 각주용 리포트 경로 |
| `listing.brand_registered` | (선택) `true`면 쿠팡 상위노출 점수 **가산점 20점** 적용 |

## keyword-scout 확장 (제안)

```yaml
# keywords/_template.yaml 에 추가
listing:
  category_tag: "디지털/가전 > ..."
  coupang_preset: digital_accessory
  brand_registered: false   # 브랜드 등록 완료 시 true → 점수 +20
```

scout 코드 변경 없이 listing-forge만 읽어도 동작함 (`seed`·`risk`만으로 MVP).
