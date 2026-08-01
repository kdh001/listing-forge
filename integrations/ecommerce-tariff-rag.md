# ecommerce-tariff-rag 연동 (HS 힌트 소비자)

listing-forge가 로컬 **ecommerce-tariff-rag**에서 품목 HS/관세율 **참고용 힌트**를 받는다.

## 면책

참고용 추정입니다. 실제 통관·세율·HS 확정은 관세사 및 관세청(UNI-PASS / CLIP) 확인이 필요합니다.
`disclaimer`가 비어 있거나 `status != ok`이면 자동 기입하지 마세요.

## 사전 준비 (tariff-rag)

```bash
cd ~/Desktop/project/ecommerce-tariff-rag
source .venv/bin/activate   # 또는 pip install -e ".[dev]"
tariff-rag reindex --provider hash
tariff-rag serve --port 8787
```

계약 정본: `ecommerce-tariff-rag/docs/integrations/listing-forge.md` (`tariff-hint-v1`).

## listing-forge에서 호출

```bash
cd ~/Desktop/project/listing-forge
source .venv/bin/activate

# .env
# TARIFF_RAG_BASE_URL=http://127.0.0.1:8787
# TARIFF_RAG_CLI=tariff-rag

python scripts/tariff_hint.py --sku "리튬 보조배터리 10000mAh"
python scripts/tariff_hint.py --sku "..." --mode subprocess
python scripts/tariff_hint.py --mode json --from-json /path/to/hint.json --out output/hint.json
```

### Python

```python
from src.integrations.tariff_rag_client import fetch_tariff_hint

hint = fetch_tariff_hint("리튬 보조배터리 10000mAh", mode="auto")
if hint.usable_for_auto_fill:
    hs = hint.hs_candidates[0]["hs_code"]
else:
    # UI/로그에 확인 필요 표시 — 세율 TBD 유지
    pass
print(hint.disclaimer)
```

### 모드

| mode | 동작 |
|------|------|
| `auto` (기본) | HTTP → subprocess → (json_path) |
| `http` | `POST {TARIFF_RAG_BASE_URL}/api/hint` |
| `subprocess` | `tariff-rag hint --sku ... --json` |
| `json` | 사전 저장 JSON 로드 (오프라인) |

## 구현 경로

| 파일 | 역할 |
|------|------|
| `src/integrations/tariff_rag_client.py` | 클라이언트 |
| `scripts/tariff_hint.py` | CLI |
| `tests/test_tariff_rag_client.py` | mock 테스트 |

## Won't

- KC/인증 RAG 혼입
- UNI-PASS 실시간 로그인
- 공개 SaaS / 세율 날조
