# validator.py 영양성분 DB 통합 프롬프트

## 목적
식품의약품안전처 건강기능식품 영양성분 DB를 활용하여 `validator.py`의 리뷰 검증 로직을 더욱 정확하고 포괄적으로 개선합니다.

## 개선 방향

### 1. 영양성분 기반 검증 강화

**현재 문제점:**
- `validate_review()`가 리뷰 텍스트와 기본 점수만으로 검증
- 제품의 실제 성분 정보를 활용하지 않음
- 허위 주장을 감지하지 못함

**개선 방안:**

```python
def validate_review(
    self,
    review_text: str,
    product_id: Optional[int] = None,
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50
) -> Dict:
    """
    리뷰 종합 검증 수행 (영양성분 DB 통합)
    
    Args:
        review_text: 검증할 리뷰 텍스트
        product_id: 제품 ID (제공 시 영양성분 검증 포함)
        length_score: 길이 점수 (기본값: 50)
        repurchase_score: 재구매 점수 (기본값: 50)
        monthly_use_score: 한달 사용 점수 (기본값: 50)
        photo_score: 사진 점수 (기본값: 0)
        consistency_score: 일치도 점수 (기본값: 50)
        
    Returns:
        Dict: {
            "trust_score": 최종 신뢰도 점수,
            "is_ad": 광고 여부 (bool),
            "reasons": 감점된 항목 리스트,
            "nutrition_validation": 영양성분 검증 결과 (있는 경우)
        }
    """
    # 1. 기본 점수 계산
    base_score = self.calculate_base_score(
        length_score,
        repurchase_score,
        monthly_use_score,
        photo_score,
        consistency_score
    )
    
    # 2. 광고 패턴 검사
    detected_issues = self.check_ad_patterns(review_text, product_id)
    
    # 3. 영양성분 검증 (product_id가 있는 경우)
    nutrition_validation = None
    if product_id:
        nutrition_validation = self._validate_nutrition_claims(
            review_text,
            product_id
        )
        
        # 영양성분 검증 결과를 감점 항목에 추가
        if nutrition_validation.get('has_invalid_claims'):
            detected_issues[14] = "허위 영양성분 주장"
    
    # 4. 감점 적용
    penalty = len(detected_issues) * 10
    final_score = max(0, base_score - penalty)
    
    # 5. 광고 판별
    is_ad = final_score < 40 or len(detected_issues) >= 3
    
    # 6. 감점 사유 리스트
    reasons = [f"{num}. {name}" for num, name in detected_issues.items()]
    
    result = {
        "trust_score": final_score,
        "is_ad": is_ad,
        "reasons": reasons,
        "base_score": base_score,
        "penalty": penalty,
        "detected_count": len(detected_issues)
    }
    
    # 영양성분 검증 결과 추가
    if nutrition_validation:
        result["nutrition_validation"] = nutrition_validation
    
    return result
```

### 2. 영양성분 주장 검증 함수

```python
def _validate_nutrition_claims(
    self,
    review_text: str,
    product_id: Optional[int] = None
) -> Dict:
    """
    리뷰의 영양성분 관련 주장 검증 (안전한 방식)
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID (None이면 검증 생략)
        
    Returns:
        Dict: 검증 결과 (오류 발생 시 안전한 기본값)
    """
    # 입력 검증
    if not review_text or len(review_text.strip()) < 3:
        return {
            "has_invalid_claims": False,
            "mentioned_ingredients": [],
            "valid_ingredients": [],
            "invalid_ingredients": [],
            "invalid_efficacy_claims": [],
            "message": "리뷰가 너무 짧음"
        }
    
    # product_id가 없으면 검증 생략
    if not product_id:
        return {
            "has_invalid_claims": False,
            "mentioned_ingredients": [],
            "valid_ingredients": [],
            "invalid_ingredients": [],
            "invalid_efficacy_claims": [],
            "message": "제품 ID 없음"
        }
    
    try:
        # 1. 영양성분 정보 조회 (오류 발생 시 기본값 반환)
        nutrition_info = self._get_nutrition_info(product_id)
        if not nutrition_info:
            return {
                "has_invalid_claims": False,
                "mentioned_ingredients": [],
                "valid_ingredients": [],
                "invalid_ingredients": [],
                "invalid_efficacy_claims": [],
                "message": "영양성분 정보 없음"
            }
    
    # 2. 리뷰에서 성분명 추출
    mentioned_ingredients = self._extract_ingredients(review_text)
    
    # 3. 실제 성분과 매칭
    valid_ingredients = []
    invalid_ingredients = []
    
    for mentioned in mentioned_ingredients:
        if self._is_valid_ingredient(mentioned, nutrition_info):
            valid_ingredients.append(mentioned)
        else:
            invalid_ingredients.append(mentioned)
    
    # 4. 효능 주장 검증
    invalid_efficacy_claims = self._validate_efficacy_claims(
        review_text,
        nutrition_info
    )
    
    return {
        "has_invalid_claims": len(invalid_ingredients) > 0 or len(invalid_efficacy_claims) > 0,
        "mentioned_ingredients": mentioned_ingredients,
        "valid_ingredients": valid_ingredients,
        "invalid_ingredients": invalid_ingredients,
        "invalid_efficacy_claims": invalid_efficacy_claims
    }
```

### 3. 효능 주장 검증

```python
def _validate_efficacy_claims(
    self,
    review_text: str,
    nutrition_info: Dict
) -> List[str]:
    """
    리뷰의 효능 주장이 공식 효능 범위 내인지 검증
    
    Args:
        review_text: 리뷰 텍스트
        nutrition_info: 영양성분 정보
        
    Returns:
        List[str]: 허위 효능 주장 목록
    """
    invalid_claims = []
    
    # 1. 각 성분의 공식 효능 수집
    official_efficacies = set()
    for ingredient in nutrition_info.get('ingredients', []):
        efficacies = ingredient.get('official_efficacy', [])
        official_efficacies.update(efficacies)
    
    # 2. 리뷰에서 효능 주장 추출
    efficacy_patterns = [
        r'효과',
        r'개선',
        r'회복',
        r'치료',
        r'완치',
        r'예방',
        # ... 더 많은 패턴
    ]
    
    # 3. 과장된 주장 패턴
    exaggerated_patterns = [
        r'100%\s*효과',
        r'완전\s*회복',
        r'완치',
        r'기적',
        r'즉시\s*효과',
        # ... 더 많은 패턴
    ]
    
    # 4. 금지된 의학적 주장 감지
    prohibited_claims = []
    for pattern in exaggerated_patterns:
        matches = re.findall(pattern, review_text, re.IGNORECASE)
        prohibited_claims.extend(matches)
    
    return prohibited_claims
```

### 4. check_ad_patterns 확장

```python
def check_ad_patterns(
    self,
    review_text: str,
    product_id: Optional[int] = None
) -> Dict[int, str]:
    """
    13단계 광고 판별 체크리스트 검사 (영양성분 DB 통합)
    
    Args:
        review_text: 검사할 리뷰 텍스트
        product_id: 제품 ID (제공 시 영양성분 검증 포함)
        
    Returns:
        Dict[int, str]: {항목번호: 항목명} 형태로 감지된 항목 반환
    """
    detected_issues = {}
    
    # 기존 13단계 체크리스트 검사
    # ...
    
    # 영양성분 DB 기반 추가 검증 (product_id가 있는 경우)
    if product_id:
        # 5번: 원료 특징 나열 - 허위 성분 주장 검증
        nutrition_validation = self._validate_nutrition_claims(
            review_text,
            product_id
        )
        
        if nutrition_validation.get('has_invalid_claims'):
            # 허위 성분 주장이 있으면 5번 항목 강화
            if 5 not in detected_issues:
                detected_issues[5] = "원료 특징 나열"
            else:
                detected_issues[5] = "원료 특징 나열 (허위 성분 주장 포함)"
    
    return detected_issues
```

### 5. 영양성분 정보 조회

```python
def _get_nutrition_info(self, product_id: Optional[int] = None) -> Optional[Dict]:
    """
    제품의 영양성분 정보 조회 (안전한 방식)
    
    Args:
        product_id: 제품 ID (None이면 None 반환)
        
    Returns:
        Dict: 영양성분 정보 또는 None (오류/정보 없음)
    """
    # product_id가 없으면 None 반환 (오류 없이)
    if not product_id:
        return None
    
    try:
        from database.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .execute()
        
        if response.data:
            return {'ingredients': response.data}
        return None  # 정보 없음 (오류 아님)
    except Exception:
        # 모든 예외를 무시하고 None 반환 (오류 없이)
        return None

def _extract_ingredients(self, text: str) -> List[str]:
    """리뷰 텍스트에서 성분명 추출"""
    # checklist.py의 로직과 유사하게 구현
    # ...

def _is_valid_ingredient(
    self,
    mentioned_name: str,
    nutrition_info: Dict
) -> bool:
    """언급된 성분이 실제 제품에 포함되어 있는지 확인"""
    # checklist.py의 로직과 유사하게 구현
    # ...
```

## 구현 요구사항

### 1. 의존성 추가

```python
# validator.py 상단에 추가
import re
from typing import Dict, List, Optional
from database.supabase_client import get_supabase_client
```

### 2. 기존 함수 시그니처 유지

- `validate_review()`에 `product_id` 선택적 매개변수 추가
- `product_id`가 없으면 기존 방식으로 동작
- 하위 호환성 유지

## 테스트 시나리오

### 시나리오 1: 허위 성분 주장 감지
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴)
리뷰: "오메가3와 코엔자임Q10이 함유되어 있어서 심혈관 건강에 좋아요"

기대 결과:
- detected_issues에 14번 항목 추가: "허위 영양성분 주장"
- nutrition_validation.invalid_ingredients: ["오메가3", "코엔자임Q10"]
- trust_score 감소
```

### 시나리오 2: 과장된 효능 주장 감지
```
제품: 루테인 제품 (공식 효능: "눈 건강 유지")
리뷰: "시력이 100% 회복되고 백내장도 완치되었어요!"

기대 결과:
- nutrition_validation.invalid_efficacy_claims: ["100% 효과", "완치"]
- detected_issues에 10번 항목 강화
- trust_score 감소
```

### 시나리오 3: 정확한 성분 언급
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴)
리뷰: "루테인과 제아잔틴을 먹고 눈 건강이 좋아졌어요"

기대 결과:
- nutrition_validation.has_invalid_claims: False
- nutrition_validation.valid_ingredients: ["루테인", "제아잔틴"]
- trust_score 유지 또는 증가
```

## 우선순위

1. **높음**: `validate_review()`에 `product_id` 매개변수 추가
2. **높음**: 영양성분 주장 검증 함수 구현
3. **중간**: 효능 주장 검증 로직 구현
4. **낮음**: 성분별 가중치 적용

## 참고 자료

- 식품의약품안전처 건강기능식품 정보
- 건강기능식품 공전: 금지된 표시·광고 문구
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/

---

## 구현 완료 요약 (2026-01-08)

### ✅ 구현된 기능

1. **`check_ad_patterns()` 메서드 확장**
   - `product_id` 매개변수 추가 완료
   - 입력 검증 추가 (리뷰 3자 미만 시 빈 결과 반환)
   - 영양성분 DB 기반 추가 검증 로직 통합

2. **`_validate_ingredient_claims()` 메서드 구현**
   - 리뷰에서 언급된 성분이 실제 제품에 포함되어 있는지 검증
   - `nutrition_utils.py`의 함수들을 활용
   - 허위 성분 주장 감지

3. **`_validate_efficacy_claims()` 메서드 구현**
   - 리뷰의 효능 주장이 공식 효능 범위 내인지 검증
   - 과장된 효능 주장 패턴 감지
   - 허위 효능 주장 감지

4. **`_validate_nutrition_claims()` 메서드 구현**
   - 종합 영양성분 검증 결과 반환
   - 언급된 성분, 유효한 성분, 허위 주장 목록 제공
   - 안전한 예외 처리 포함

5. **`validate_review()` 메서드 확장**
   - `product_id` 매개변수 추가
   - 영양성분 검증 결과를 검증 결과에 포함
   - `nutrition_validation` 필드 추가

### 📝 구현 세부사항

- **공통 유틸리티 활용**: `nutrition_utils.py`의 함수들을 import하여 사용
- **안전한 예외 처리**: 모든 DB 조회 및 검증 함수에 try-except 추가
- **하위 호환성 유지**: `product_id`가 None이면 기존 방식으로 동작

### 🔄 변경된 파일

- `logic_designer/validator.py`: 4개 검증 메서드 추가, `validate_review()` 확장
- `logic_designer/nutrition_utils.py`: 공통 유틸리티 함수 모듈 (신규 생성)

### ⚠️ 주의사항

- 영양성분 검증 결과는 `nutrition_validation` 필드에 포함
- 허위 주장이 있으면 14번 항목으로 추가 감점
- 효능 주장 검증은 향후 더 정교한 로직으로 개선 가능
