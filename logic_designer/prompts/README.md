# 영양성분 DB 통합 프롬프트 가이드

## 개요

이 디렉토리에는 식품의약품안전처 건강기능식품 영양성분 DB를 `logic_designer` 모듈에 통합하기 위한 프롬프트 문서들이 포함되어 있습니다.

각 프롬프트는 특정 파일의 개선 방향과 구현 방법을 상세히 설명합니다.

## 파일 목록

### 1. checklist_nutrition_integration.md
**대상 파일**: `logic_designer/checklist.py`

**주요 내용**:
- 원료 특징 나열 검증 강화 (5번 항목)
- 전문 용어 오남용 검증 (9번 항목)
- 비현실적 효과 강조 검증 (10번 항목)
- 제품별 체크 기준 강화

**핵심 기능**:
- 허위 성분 주장 감지
- 허위 의학적 주장 감지
- 효과 시점 검증

### 2. analyzer_nutrition_integration.md
**대상 파일**: `logic_designer/analyzer.py`

**주요 내용**:
- AI 프롬프트에 영양성분 정보 주입
- 강화된 시스템 프롬프트
- 성분 검증 결과를 분석 결과에 포함
- 허위 주장 자동 감지 및 경고

**핵심 기능**:
- 영양성분 정보 기반 AI 분석
- 성분 검증 결과 제공
- 허위 주장 경고

### 3. trust_score_nutrition_integration.md
**대상 파일**: `logic_designer/trust_score.py`

**주요 내용**:
- 영양성분 일치도 점수 추가
- 신뢰도 점수 공식 확장
- 성분명 추출 및 매칭 로직
- 선택적 영양성분 점수 적용

**핵심 기능**:
- 영양성분 일치도 점수 계산
- 신뢰도 점수 공식에 통합
- 하위 호환성 유지

### 4. validator_nutrition_integration.md
**대상 파일**: `logic_designer/validator.py`

**주요 내용**:
- 영양성분 기반 검증 강화
- 영양성분 주장 검증 함수
- 효능 주장 검증
- check_ad_patterns 확장

**핵심 기능**:
- 허위 성분 주장 감지
- 과장된 효능 주장 감지
- 영양성분 검증 결과 제공

### 5. init_nutrition_integration.md
**대상 파일**: `logic_designer/__init__.py`

**주요 내용**:
- 통합 분석 함수에 product_id 추가
- 영양성분 검증 결과 조회
- 하위 호환성 유지

**핵심 기능**:
- 통합 분석 함수 개선
- 영양성분 검증 통합
- 기존 API 호환성 유지

### 6. edge_cases_handling.md
**대상**: 전체 프로젝트

**주요 내용**:
- 영양성분 DB 없을 때의 처리
- 리뷰가 적거나 없을 때의 처리
- 예외 상황별 대처 방안
- 프로젝트 전체 대처 전략

**핵심 기능**:
- Graceful Degradation (우아한 성능 저하)
- 입력 검증 강화
- 오류 없이 기본 모드로 동작

## 구현 순서

### Phase 1: 기반 구조 구축
1. **영양성분 DB 스키마 확인/구축**
   - `nutrition_info` 테이블 구조 확인
   - 필요한 경우 스키마 확장

2. **공통 유틸리티 함수 구현**
   - 영양성분 정보 조회 함수
   - 성분명 추출 함수
   - 성분명 매칭 함수

### Phase 2: 개별 모듈 개선
1. **trust_score.py** (우선순위: 높음)
   - 영양성분 일치도 점수 계산
   - 신뢰도 점수 공식 확장

2. **checklist.py** (우선순위: 높음)
   - 허위 성분 주장 감지
   - 허위 의학적 주장 감지

3. **validator.py** (우선순위: 중간)
   - 영양성분 검증 통합
   - 검증 결과 제공

4. **analyzer.py** (우선순위: 중간)
   - AI 프롬프트 강화
   - 성분 검증 결과 포함

5. **__init__.py** (우선순위: 낮음)
   - 통합 함수 개선
   - 전체 파이프라인 통합

### Phase 3: 테스트 및 검증
1. 단위 테스트 작성
2. 통합 테스트 수행
3. 실제 데이터 검증

## 영양성분 DB 스키마 가정

```sql
-- nutrition_info 테이블
CREATE TABLE nutrition_info (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    ingredient_name TEXT NOT NULL,           -- 성분명 (공식명)
    ingredient_aliases JSONB,                -- 동의어/별칭 배열
    amount NUMERIC,                          -- 함량
    unit TEXT,                               -- 단위 (mg, g, mcg 등)
    official_efficacy TEXT[],                -- 공식 효능 목록
    prohibited_claims TEXT[],                 -- 금지된 주장 목록
    typical_effect_period_days INT,          -- 일반적 효과 발현 기간 (일)
    daily_value_percentage NUMERIC,          -- 일일 권장량 대비 비율
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_nutrition_info_product_id ON nutrition_info(product_id);
CREATE INDEX idx_nutrition_info_ingredient_name ON nutrition_info(ingredient_name);
```

## 공통 구현 패턴

### 1. 영양성분 정보 조회

```python
from database.supabase_client import get_supabase_client

def get_nutrition_info(product_id: int) -> Optional[Dict]:
    """제품의 영양성분 정보 조회"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .execute()
        return {'ingredients': response.data} if response.data else None
    except Exception:
        return None
```

### 2. 성분명 추출

```python
import re

def extract_ingredients(text: str) -> List[str]:
    """리뷰 텍스트에서 성분명 추출"""
    patterns = [
        r'비타민\s*[A-Z]?\d*',
        r'루테인',
        r'제아잔틴',
        r'오메가\s*3',
        # ... 더 많은 패턴
    ]
    extracted = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        extracted.extend(matches)
    return list(set(extracted))
```

### 3. 성분명 매칭

```python
def is_valid_ingredient(mentioned_name: str, nutrition_info: Dict) -> bool:
    """언급된 성분이 실제 제품에 포함되어 있는지 확인"""
    mentioned_normalized = normalize_ingredient_name(mentioned_name)
    
    for ingredient in nutrition_info.get('ingredients', []):
        official_name = normalize_ingredient_name(ingredient.get('ingredient_name', ''))
        if mentioned_normalized in official_name or official_name in mentioned_normalized:
            return True
        
        aliases = ingredient.get('ingredient_aliases', [])
        for alias in aliases:
            if mentioned_normalized in normalize_ingredient_name(alias):
                return True
    
    return False
```

## 테스트 체크리스트

- [ ] 영양성분 정보 조회 기능 테스트
- [ ] 성분명 추출 기능 테스트
- [ ] 성분명 매칭 기능 테스트
- [ ] 허위 성분 주장 감지 테스트
- [ ] 허위 효능 주장 감지 테스트
- [ ] 영양성분 일치도 점수 계산 테스트
- [ ] 통합 분석 함수 테스트
- [ ] 하위 호환성 테스트 (product_id 없이 사용)

## 참고 자료

- 식품의약품안전처 건강기능식품 정보: https://www.foodsafetykorea.go.kr/
- 건강기능식품 공전
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/
- Supabase 프로젝트: https://supabase.com/dashboard/project/bvowxbpqtfpkkxkzsumf

## 예외 상황 처리

### 중요: 모든 구현 시 필수 사항

1. **영양성분 DB가 없어도 오류 없이 동작**
   - 모든 DB 조회 함수는 try-except로 감싸기
   - 오류 발생 시 None 또는 기본값 반환
   - 기존 기능은 항상 유지

2. **리뷰가 적거나 없을 때의 처리**
   - 리뷰가 None이거나 빈 문자열: 빈 결과 반환
   - 리뷰가 3자 미만: 최소한의 검사만 수행
   - 리뷰가 10자 미만: 기본 분석만 제공

자세한 내용은 **edge_cases_handling.md** 참고

## 문의

구현 중 문제가 발생하거나 추가 설명이 필요한 경우, 각 프롬프트 파일의 상세 내용을 참고하세요.
