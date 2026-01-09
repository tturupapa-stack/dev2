# 📡 데이터 입출력 인터페이스 정의

두 에이전트가 소통할 데이터 형식을 미리 약속합니다.

## 데이터 흐름 (Pipeline)

```
[원본 리뷰 데이터] 
    ↓
[검증 로직 에이전트] → trust_score, is_ad, deduction_reasons
    ↓
[약사 인사이트 에이전트] → JSON 분석 결과
    ↓
[최종 출력]
```

## 1. 검증 로직 에이전트 출력 형식

### 입력
- `review_text`: str - 원본 리뷰 텍스트
- `review_metadata`: dict - 리뷰 메타데이터 (선택적)

### 출력
```python
{
    "trust_score": float,  # 신뢰도 점수 (0-100)
    "is_ad": bool,         # 광고 여부
    "deduction_reasons": list[str],  # 감점 사유 리스트
    "checklist_results": dict,  # 13단계 체크리스트 결과
    "raw_scores": {       # 원시 점수 (디버깅용)
        "L": float,  # Length 관련 점수
        "R": float,  # Review quality 점수
        "M": float,  # Metadata 점수
        "P": float,  # Pattern 점수
        "C": float   # Content 점수
    }
}
```

## 2. 약사 인사이트 에이전트 입출력 형식

### 입력
- `review_text`: str - 원본 리뷰 텍스트
- `trust_score`: float - 검증 에이전트로부터 받은 신뢰도 점수
- `is_ad`: bool - 광고 여부 (True인 경우 분석 생략 가능)

### 출력
```python
{
    "summary": str,        # 리뷰 요약 (사용자 체감 중심)
    "efficacy": str,       # 효능 관련 내용 (원문 근거만)
    "side_effects": str,  # 부작용 관련 내용
    "tip": str,           # 약사 관점의 조언
    "confidence": str      # 분석 신뢰도 ("high" | "medium" | "low")
}
```

## 3. 통합 파이프라인 출력 형식

최종적으로 두 에이전트의 결과를 통합한 형식:

```python
{
    "review_id": str,
    "validation": {
        "trust_score": float,
        "is_ad": bool,
        "deduction_reasons": list[str]
    },
    "analysis": {
        "summary": str,
        "efficacy": str,
        "side_effects": str,
        "tip": str,
        "confidence": str
    },
    "timestamp": str  # ISO 8601 형식
}
```

## 4. 에러 처리

### 검증 로직 에이전트 에러
- 리뷰 텍스트가 10자 미만인 경우: `{"error": "REVIEW_TOO_SHORT", "message": "리뷰가 너무 짧습니다."}`
- 필수 메타데이터 누락: `{"error": "MISSING_METADATA", "message": "필수 메타데이터가 없습니다."}`

### 약사 인사이트 에이전트 에러
- 광고로 판별된 경우: `{"error": "AD_REVIEW", "message": "광고 리뷰는 분석하지 않습니다."}`
- LLM API 호출 실패: `{"error": "API_ERROR", "message": "AI 분석 서비스 오류가 발생했습니다."}`

## 5. 데이터 검증 규칙

### 검증 로직 에이전트
- `trust_score`는 0 이상 100 이하의 실수여야 함
- `is_ad`가 True인 경우 `trust_score`는 70 미만이어야 함
- `deduction_reasons`는 빈 리스트일 수 있음

### 약사 인사이트 에이전트
- 모든 필드(str 타입)는 최소 1자 이상이어야 함
- `confidence`는 반드시 "high", "medium", "low" 중 하나여야 함
- JSON 파싱 가능한 형식이어야 함

