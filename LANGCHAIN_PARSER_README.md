# LangChain Pydantic Output Parser 리뷰 분석 모듈

## 개요

이 모듈은 LangChain의 Pydantic Output Parser를 활용하여 건강기능식품 리뷰를 분석하고,
구조화된 객체(`ReviewValidationResult`)로 반환하는 기능을 제공합니다.

## 주요 기능

- ✅ **Pydantic 기반 구조화된 출력**: 리뷰 분석 결과를 타입이 명확한 객체로 반환
- 🔧 **두 가지 분석 모드**:
  - **규칙 기반**: 빠르고 무료, `validator.py`의 정규표현식 패턴 사용
  - **LLM 기반**: 더 정교하지만 비용 발생, LangChain + GPT 사용
- 📊 **13단계 광고 판별 체크리스트** 적용
- 🎯 **신뢰도 점수 자동 계산**
- 📄 **JSON 직렬화 지원**: `model_dump()`로 쉽게 JSON 변환

## 설치

```bash
pip install -r requirements.txt
```

필요한 패키지:
- `langchain-core>=0.3.0`
- `langchain-anthropic>=0.3.0`
- `pydantic>=2.0.0`
- `anthropic>=0.40.0` (이미 설치됨)

LLM 기반 분석을 사용하려면 Anthropic API 키가 필요합니다:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

또는 코드에서 직접 지정:

```python
result = parse_review_with_langchain(
    review_text=review,
    anthropic_api_key="your-api-key-here"
)
```

## 사용법

### 1. 기본 사용 (규칙 기반 - 추천)

```python
from core.langchain_parser import analyze_review

review_text = """
이 제품 정말 좋아요!!! 완전 대박입니다!!!
무료로 제공받아서 사용해봤는데 효과가 100% 만족이에요~
"""

# 규칙 기반 분석 (빠르고 무료)
result = analyze_review(
    review_text=review_text,
    length_score=60,
    repurchase_score=80,
    monthly_use_score=50
)

print(f"신뢰도 점수: {result.trust_score}")
print(f"광고 여부: {result.is_ad}")
print(f"감지된 항목 수: {result.detected_count}")

# 감지된 항목 확인
for item in result.detected_items:
    if item.detected:
        print(f"{item.item_number}. {item.item_name}")
```

### 2. LLM 기반 분석 (정교함)

```python
from core.langchain_parser import parse_review_hybrid

# LLM 기반 분석 (Anthropic API 키 필요)
result = parse_review_hybrid(
    review_text=review_text,
    use_llm=True,  # LLM 사용
    model_name="claude-3-5-sonnet-20241022",
    temperature=0
)
```

### 3. JSON으로 변환

```python
import json

result = analyze_review(review_text)

# Pydantic 모델을 dict로 변환
result_dict = result.model_dump()

# JSON 문자열로 변환
json_str = json.dumps(result_dict, ensure_ascii=False, indent=2)
print(json_str)
```

## 출력 구조

### ReviewValidationResult

```python
class ReviewValidationResult(BaseModel):
    trust_score: float          # 최종 신뢰도 점수 (0-100)
    base_score: float           # 감점 전 기본 점수
    penalty: int                # 감점 총합
    is_ad: bool                 # 광고 여부
    detected_count: int         # 감지된 항목 개수
    detected_items: List[AdCheckItem]  # 13개 항목 상세
    reasons: List[str]          # 감점 사유
    review_text: str            # 원본 리뷰
```

### AdCheckItem

```python
class AdCheckItem(BaseModel):
    item_number: int    # 항목 번호 (1-13)
    item_name: str      # 항목 이름
    detected: bool      # 감지 여부
```

## 예제 실행

```bash
python example_langchain_parser.py
```

## 13단계 광고 판별 체크리스트

1. ✓ 대가성 문구 존재
2. ✓ 감탄사 남발
3. ✓ 정돈된 문단 구조
4. ✓ 개인 경험 부재
5. ✓ 원료 특징 나열
6. ✓ 키워드 반복
7. ✓ 단점 회피
8. ✓ 찬사 위주 구성
9. ✓ 전문 용어 오남용
10. ✓ 비현실적 효과 강조
11. ✓ 타사 제품 비교
12. ✓ 홍보성 블로그 문체
13. ✓ 이모티콘 과다 사용

## 신뢰도 점수 계산 공식

```
기본 점수 = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)
```

- **L** (length_score): 리뷰 길이 점수 (0-100)
- **R** (repurchase_score): 재구매 여부 점수 (0-100)
- **M** (monthly_use_score): 한달 사용 여부 점수 (0-100)
- **P** (photo_score): 사진 첨부 점수 (0-100)
- **C** (consistency_score): 내용 일치도 점수 (0-100)

```
감점 = 감지된 항목 개수 × 10점
최종 점수 = max(0, 기본 점수 - 감점)
```

**광고 판별 기준**:
- 최종 점수 < 40점, 또는
- 감점 항목 >= 3개

## API 함수

### `analyze_review(review_text, **kwargs)`

리뷰 분석 편의 함수 (기본적으로 규칙 기반 사용)

**매개변수**:
- `review_text` (str): 분석할 리뷰 텍스트
- `use_llm` (bool): LLM 사용 여부 (기본값: False)
- `length_score` (float): 길이 점수 (기본값: 50)
- `repurchase_score` (float): 재구매 점수 (기본값: 50)
- `monthly_use_score` (float): 한달 사용 점수 (기본값: 50)
- `photo_score` (float): 사진 점수 (기본값: 0)
- `consistency_score` (float): 일치도 점수 (기본값: 50)

**반환값**: `ReviewValidationResult`

### `parse_review_hybrid(review_text, use_llm=False, **kwargs)`

하이브리드 방식 리뷰 분석

**매개변수**: `analyze_review()`와 동일 + LLM 관련 매개변수
- `model_name` (str): Claude 모델 이름 (기본값: "claude-3-5-sonnet-20241022")
- `temperature` (float): LLM temperature (기본값: 0)
- `anthropic_api_key` (str): Anthropic API 키

**반환값**: `ReviewValidationResult`

### `parse_review_with_langchain(review_text, **kwargs)`

LLM 기반 리뷰 분석 (항상 LangChain 사용)

**매개변수**: `parse_review_hybrid()`와 동일

**반환값**: `ReviewValidationResult`

## 규칙 기반 vs LLM 기반 비교

| 특성 | 규칙 기반 | LLM 기반 |
|------|-----------|----------|
| **속도** | ⚡ 매우 빠름 (< 0.1초) | 🐢 느림 (2-5초) |
| **비용** | 💰 무료 | 💸 유료 (API 호출당 과금) |
| **정확도** | 📊 일관성 높음 | 🎯 더 정교하고 맥락 이해 |
| **API 키** | ❌ 불필요 | ✅ 필요 (Anthropic) |
| **사용 모델** | 정규표현식 패턴 매칭 | Claude 3.5 Sonnet |
| **추천 용도** | 대량 처리, 실시간 분석 | 정밀 분석, 애매한 케이스 |

## Context7 MCP 사용 시 주의사항

이 모듈은 Context7 MCP의 최신 LangChain 코드베이스 정보를 바탕으로 작성되었습니다.
만약 Context7 MCP 서버가 설정되어 있다면, 다음과 같이 최신 LangChain 문서를 조회할 수 있습니다:

```bash
# Context7 MCP 설정 예시
# .claude/mcp.json 또는 MCP 설정 파일에 추가
```

현재 구현은 2024-2025년 최신 LangChain API 기준으로 작성되었습니다.

## 파일 구조

```
core/
  ├── validator.py          # 원본 규칙 기반 검증 모듈
  └── langchain_parser.py   # 🆕 LangChain Pydantic Parser 모듈

example_langchain_parser.py # 사용 예제
requirements.txt            # 의존성 패키지
```

## 라이선스

이 프로젝트의 라이선스를 따릅니다.

## 참고 자료

- [LangChain PydanticOutputParser 공식 문서](https://python.langchain.com/api_reference/core/output_parsers/langchain_core.output_parsers.pydantic.PydanticOutputParser.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Control LLM output with LangChain's structured and Pydantic output parsers](https://atamel.dev/posts/2024/12-09_control_llm_output_langchain_structured_pydantic/)
