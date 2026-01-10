# trust_score.py 영양성분 DB 통합 프롬프트

## 목적
식품의약품안전처 건강기능식품 영양성분 DB를 활용하여 `trust_score.py`의 신뢰도 점수 계산을 더욱 정확하고 공정하게 개선합니다.

## 개선 방향

### 1. 영양성분 일치도 점수 추가

**현재 문제점:**
- `consistency_score`는 리뷰 내용의 일관성만 평가
- 제품의 실제 성분 정보와 리뷰 내용의 일치 여부를 반영하지 않음

**개선 방안:**

```python
def calculate_nutrition_consistency_score(
    self,
    review_text: str,
    product_id: Optional[int] = None
) -> float:
    """
    영양성분 일치도 점수 계산 (안전한 방식)
    
    리뷰에서 언급된 성분이 실제 제품에 포함되어 있는지,
    효능 주장이 공식 효능 범위 내인지 평가
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID (None이면 기본값 반환)
        
    Returns:
        float: 영양성분 일치도 점수 (0-100), 오류 시 50.0 반환
    """
    # 입력 검증
    if not review_text or len(review_text.strip()) < 3:
        return 50.0  # 리뷰가 너무 짧으면 중간값 반환
    
    if not product_id:
        return 50.0  # product_id 없으면 중간값 반환
    
    try:
        # 1. 영양성분 정보 조회 (오류 발생 시 기본값 반환)
        nutrition_info = self._get_nutrition_info_safe(product_id)
        if not nutrition_info:
            return 50.0  # 정보 없으면 중간값 (오류 아님)
        
        # 2. 리뷰에서 성분명 추출
        mentioned_ingredients = self._extract_ingredients(review_text)
        
        # 3. 성분 언급이 없으면 중간값 반환
        if len(mentioned_ingredients) == 0:
            return 50.0
        
        # 4. 실제 성분과 매칭
        valid_count = 0
        invalid_count = 0
        
        for mentioned in mentioned_ingredients:
            if self._is_valid_ingredient(mentioned, nutrition_info):
                valid_count += 1
            else:
                invalid_count += 1
        
        # 5. 점수 계산
        accuracy = valid_count / len(mentioned_ingredients)
        penalty = min(invalid_count * 20, 50)  # 최대 50점 감점
        score = (accuracy * 100) - penalty
        
        return max(0, min(100, score))
        
    except Exception:
        # 모든 예외를 무시하고 기본값 반환 (오류 없이)
        return 50.0

def _get_nutrition_info_safe(self, product_id: int) -> Optional[Dict]:
    """
    영양성분 정보 조회 (안전한 방식)
    
    Returns:
        Dict: 영양성분 정보 또는 None (오류/정보 없음)
    """
    try:
        from database.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .execute()
        return {'ingredients': response.data} if response.data else None
    except Exception:
        return None  # 오류 발생 시 None 반환 (오류 없이)
```

### 2. 신뢰도 점수 공식 확장

**기존 공식:**
```
S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)
```

**개선된 공식 (영양성분 일치도 포함):**
```
S = (L × 0.15) + (R × 0.15) + (M × 0.25) + (P × 0.1) + (C × 0.15) + (N × 0.2)

여기서:
- N: 영양성분 일치도 점수 (Nutrition Consistency Score)
- 기존 가중치를 약간 조정하여 N을 추가
```

**또는 선택적 적용:**
```python
def calculate_final_score(
    self,
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    penalty_count: int = 0,
    penalty_per_item: int = 10,
    review_text: Optional[str] = None,
    product_id: Optional[int] = None,
    use_nutrition_score: bool = True
) -> Dict:
    """
    최종 신뢰도 점수 계산 (영양성분 일치도 포함)
    
    Args:
        ... (기존 매개변수)
        review_text: 리뷰 텍스트 (영양성분 점수 계산용)
        product_id: 제품 ID (영양성분 정보 조회용)
        use_nutrition_score: 영양성분 점수 사용 여부
        
    Returns:
        Dict: 계산 결과
    """
    # 기본 점수 계산
    base_score = self.calculate_base_score(
        length_score,
        repurchase_score,
        monthly_use_score,
        photo_score,
        consistency_score
    )
    
    # 영양성분 일치도 점수 추가 (선택적)
    nutrition_score = 50.0  # 기본값
    if use_nutrition_score and review_text and product_id:
        nutrition_score = self.calculate_nutrition_consistency_score(
            review_text,
            product_id
        )
        
        # 가중 평균으로 통합
        # 기존 점수 80% + 영양성분 점수 20%
        base_score = (base_score * 0.8) + (nutrition_score * 0.2)
    
    # 감점 적용
    penalty = penalty_count * penalty_per_item
    final_score = max(0, base_score - penalty)
    
    return {
        "base_score": base_score,
        "nutrition_score": nutrition_score,
        "penalty": penalty,
        "final_score": final_score,
        "raw_scores": {
            "L": length_score,
            "R": repurchase_score,
            "M": monthly_use_score,
            "P": photo_score,
            "C": consistency_score,
            "N": nutrition_score
        }
    }
```

### 3. 성분명 추출 및 매칭 로직

```python
def _extract_ingredients(self, text: str) -> List[str]:
    """
    리뷰 텍스트에서 성분명 추출
    
    Args:
        text: 리뷰 텍스트
        
    Returns:
        List[str]: 추출된 성분명 목록
    """
    # 1. 일반적인 건강기능식품 성분명 패턴
    common_ingredients = [
        r'비타민\s*[A-Z]?\d*',
        r'루테인',
        r'제아잔틴',
        r'오메가\s*3',
        r'프로바이오틱스',
        r'코엔자임\s*Q10',
        r'글루코사민',
        r'콜라겐',
        r'히알루론산',
        # ... 더 많은 패턴
    ]
    
    extracted = []
    for pattern in common_ingredients:
        matches = re.findall(pattern, text, re.IGNORECASE)
        extracted.extend(matches)
    
    # 2. 중복 제거 및 정규화
    normalized = [self._normalize_ingredient_name(name) for name in extracted]
    return list(set(normalized))

def _normalize_ingredient_name(self, name: str) -> str:
    """
    성분명 정규화 (공백 제거, 대소문자 통일 등)
    
    Args:
        name: 원본 성분명
        
    Returns:
        str: 정규화된 성분명
    """
    # 공백 제거, 소문자 변환
    normalized = re.sub(r'\s+', '', name.lower())
    return normalized

def _is_valid_ingredient(
    self,
    mentioned_name: str,
    nutrition_info: Dict
) -> bool:
    """
    언급된 성분이 실제 제품에 포함되어 있는지 확인
    
    Args:
        mentioned_name: 리뷰에서 언급된 성분명
        product_id: 제품 ID
        
    Returns:
        bool: 유효한 성분이면 True
    """
    mentioned_normalized = self._normalize_ingredient_name(mentioned_name)
    
    for ingredient in nutrition_info.get('ingredients', []):
        # 공식명 확인
        official_name = self._normalize_ingredient_name(
            ingredient.get('ingredient_name', '')
        )
        if mentioned_normalized in official_name or official_name in mentioned_normalized:
            return True
        
        # 별칭 확인
        aliases = ingredient.get('ingredient_aliases', [])
        for alias in aliases:
            alias_normalized = self._normalize_ingredient_name(alias)
            if mentioned_normalized in alias_normalized or alias_normalized in mentioned_normalized:
                return True
    
    return False
```

### 4. 영양성분 정보 조회

```python
def _get_nutrition_info(self, product_id: int) -> Optional[Dict]:
    """
    제품의 영양성분 정보 조회
    
    Args:
        product_id: 제품 ID
        
    Returns:
        Dict: 영양성분 정보 또는 None
    """
    try:
        from database.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .execute()
        
        if response.data:
            return {'ingredients': response.data}
        return None
    except Exception as e:
        # 오류 발생 시 None 반환
        return None
```

## 구현 요구사항

### 1. 의존성 추가

```python
# trust_score.py 상단에 추가
import re
from typing import Dict, List, Optional
from database.supabase_client import get_supabase_client
```

### 2. 기존 함수 시그니처 유지

기존 코드와의 호환성을 위해:
- `calculate_final_score()`에 선택적 매개변수 추가
- `product_id`가 없으면 기존 방식으로 동작
- 기본값 설정으로 하위 호환성 유지

## 테스트 시나리오

### 시나리오 1: 정확한 성분 언급
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴)
리뷰: "루테인과 제아잔틴을 먹고 눈 건강이 좋아졌어요"

기대 결과:
- nutrition_score: 100점 (모든 언급된 성분이 실제 제품에 포함)
- final_score: 기존 점수보다 높아짐
```

### 시나리오 2: 허위 성분 주장
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴만)
리뷰: "오메가3와 코엔자임Q10이 함유되어 있어서 좋아요"

기대 결과:
- nutrition_score: 0점 (언급된 성분 중 실제 제품에 없는 성분 존재)
- final_score: 기존 점수보다 낮아짐
```

### 시나리오 3: 부분 일치
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴)
리뷰: "루테인을 먹고 있어요. 오메가3도 좋다고 해서..."

기대 결과:
- nutrition_score: 50점 (루테인은 정확, 오메가3는 허위)
- final_score: 중간 수준
```

## 우선순위

1. **높음**: 영양성분 일치도 점수 계산 함수 구현
2. **높음**: `calculate_final_score()`에 영양성분 점수 통합
3. **중간**: 성분명 추출 및 매칭 로직 구현
4. **낮음**: 성분별 가중치 적용 (주요 성분 vs 보조 성분)

## 참고 자료

- 식품의약품안전처 건강기능식품 정보
- 건강기능식품 공전: 성분명 표준화 규정
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/

---

## 구현 완료 요약 (2026-01-08)

### ✅ 구현된 기능

1. **`calculate_nutrition_consistency_score()` 메서드 구현**
   - 리뷰에서 언급된 성분이 실제 제품에 포함되어 있는지 평가
   - `nutrition_utils.py`의 함수들을 활용하여 구현
   - 오류 발생 시 50.0 반환 (중간값)

2. **`calculate_base_score()` 메서드 확장**
   - `nutrition_score` 선택적 매개변수 추가
   - 영양성분 점수가 있으면 확장 공식 사용 (가중치 조정)
   - 없으면 기존 공식 사용 (하위 호환성)

3. **`calculate_final_score()` 메서드 확장**
   - `review_text`, `product_id`, `use_nutrition_score` 매개변수 추가
   - 영양성분 일치도 점수 계산 및 통합
   - 반환값에 `nutrition_score` 필드 추가

### 📝 구현 세부사항

- **점수 계산 공식**: 
  - 영양성분 점수 있을 때: `S = (L × 0.15) + (R × 0.15) + (M × 0.25) + (P × 0.1) + (C × 0.15) + (N × 0.2)`
  - 영양성분 점수 없을 때: 기존 공식 유지
- **공통 유틸리티 활용**: `nutrition_utils.py`의 함수들을 import하여 사용
- **안전한 예외 처리**: 모든 단계에 try-except 추가, 오류 시 기본값 반환

### 🔄 변경된 파일

- `logic_designer/trust_score.py`: 2개 메서드 추가/수정, 점수 공식 확장
- `logic_designer/nutrition_utils.py`: 공통 유틸리티 함수 모듈 (신규 생성)

### ⚠️ 주의사항

- 영양성분 점수는 선택적 적용 (기본값 50.0)
- `use_nutrition_score=False`로 설정하면 기존 방식으로 동작
- `product_id`가 None이면 영양성분 점수 계산 생략
