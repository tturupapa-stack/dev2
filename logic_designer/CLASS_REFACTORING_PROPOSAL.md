# 제품별 체크 기준 클래스 설계 (구현 완료)

## 구현 목적

**제품별로 다른 체크 기준을 설정하여 동일한 기준으로 리뷰를 체크할 수 있도록 함**

예를 들어:
- 제품명: "비타민C"
- 영양구분: "비타민"
- 긍정적 키워드: ["면역력", "감기예방", "항산화"]
- 부정적 표현: ["알레르기", "위장불편", "메스꺼움"]
- 광고의심 표현: ["100% 효과", "즉시 개선", "완벽한"]

## 현재 구조의 문제점

1. **제품별 차별화 불가**: 모든 제품에 동일한 기준만 적용됨
2. **확장성 부족**: 제품 특성에 맞는 키워드나 표현을 추가하기 어려움
3. **유지보수 어려움**: 제품별 기준을 코드에 하드코딩해야 함

## 구현된 클래스 구조

### 1. `ProductCheckCriteria` (제품별 체크 기준)
**책임**: 제품별 체크 기준을 정의하고 관리

**주요 필드:**
- `product_name`: 제품명
- `nutrition_category`: 영양구분 (비타민, 미네랄, 프로바이오틱스 등)
- `positive_keywords`: 긍정적 키워드 리스트
- `negative_expressions`: 부정적 표현 리스트
- `ad_suspicious_expressions`: 광고의심 표현 리스트
- `product_specific_patterns`: 제품별 특수 패턴
- `keyword_repetition_threshold`: 키워드 반복 임계값

**주요 메서드:**
- `add_positive_keyword()`: 긍정적 키워드 추가
- `add_negative_expression()`: 부정적 표현 추가
- `add_ad_suspicious_expression()`: 광고의심 표현 추가
- `to_dict()` / `from_dict()`: 직렬화/역직렬화

### 2. `DefaultProductCriteria` (기본 기준 팩토리)
**책임**: 사전 정의된 제품 기준 제공

**제공하는 기준:**
- `create_vitamin_c_criteria()`: 비타민C 제품 기준
- `create_probiotics_criteria()`: 프로바이오틱스 제품 기준
- `create_omega3_criteria()`: 오메가3 제품 기준
- `create_generic_criteria()`: 일반 제품 기준 생성

### 3. `AdChecklist` (체크리스트 - 수정됨)
**책임**: 제품 기준을 받아서 체크리스트 검사 수행

**주요 변경사항:**
- `__init__(criteria: Optional[ProductCheckCriteria])`: 제품 기준을 받을 수 있음
- `check_with_criteria()`: 특정 기준으로 체크
- `get_check_summary()`: 상세 검사 결과 요약 (긍정/부정 키워드 포함)

**기존 API 호환성:**
- `check_ad_patterns()` 메서드는 그대로 유지 (기준 없이도 사용 가능)

## 클래스 간 의존성 다이어그램

```
AdChecklist
    └── ProductCheckCriteria
            ├── product_name
            ├── nutrition_category
            ├── positive_keywords
            ├── negative_expressions
            └── ad_suspicious_expressions

DefaultProductCriteria (팩토리)
    └── ProductCheckCriteria 생성
```

## 사용 예시

### 기본 사용법

```python
from logic_designer.product_criteria import ProductCheckCriteria
from logic_designer.checklist import AdChecklist

# 1. 제품 기준 생성
criteria = ProductCheckCriteria(
    product_name="비타민C 1000mg",
    nutrition_category="비타민",
    positive_keywords=["면역력", "감기예방", "항산화"],
    negative_expressions=["알레르기", "위장불편"],
    ad_suspicious_expressions=["100% 효과", "즉시 개선"]
)

# 2. 체크리스트에 기준 적용
checklist = AdChecklist(criteria=criteria)

# 3. 리뷰 검사
review_text = "이 비타민C는 면역력 향상에 좋아요!"
detected = checklist.check_ad_patterns(review_text)

# 4. 상세 요약
summary = checklist.get_check_summary(review_text)
print(f"긍정적 키워드: {summary['positive_keywords_found']}")
print(f"부정적 표현: {summary['negative_expressions_found']}")
```

### 사전 정의된 기준 사용

```python
from logic_designer.product_criteria import DefaultProductCriteria
from logic_designer.checklist import AdChecklist

# 비타민C 기준 사용
criteria = DefaultProductCriteria.create_vitamin_c_criteria()
checklist = AdChecklist(criteria=criteria)

# 리뷰 검사
result = checklist.check_ad_patterns(review_text)
```

### 동적 기준 생성

```python
# 일반 기준으로 시작
criteria = DefaultProductCriteria.create_generic_criteria(
    product_name="오메가3",
    nutrition_category="지방산"
)

# 키워드 추가
criteria.add_positive_keyword("뇌건강")
criteria.add_negative_expression("비린내")
criteria.add_ad_suspicious_expression("완벽한 뇌건강")
```

## 구현 완료 상태

✅ **완료된 작업:**
1. `ProductCheckCriteria` 클래스 구현 (`product_criteria.py`)
2. `DefaultProductCriteria` 팩토리 클래스 구현
3. `AdChecklist` 클래스 수정 (제품 기준 지원)
4. 사용 예시 파일 작성 (`example_product_criteria.py`)

## 장점

1. **제품별 차별화**: 각 제품에 맞는 키워드와 표현으로 체크 가능
2. **유연한 설정**: 제품 특성에 맞게 키워드 추가/수정 가능
3. **재사용성**: 사전 정의된 기준을 쉽게 사용 가능
4. **확장성**: 새로운 제품 기준 추가가 쉬움
5. **기존 호환성**: 기준 없이도 기존 방식으로 사용 가능

## 파일 구조

```
logic_designer/
├── product_criteria.py          # 제품별 체크 기준 클래스
├── checklist.py                 # 체크리스트 (수정됨)
└── example_product_criteria.py  # 사용 예시
```

## 다음 단계 (선택사항)

1. 데이터베이스에 제품 기준 저장 기능 추가
2. 제품 기준 관리 UI 추가
3. 제품별 기준 자동 생성 기능 (제품 정보 기반)
4. 기준별 통계 및 분석 기능

