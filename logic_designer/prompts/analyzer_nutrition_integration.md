# analyzer.py 영양성분 DB 통합 프롬프트

## 목적
식품의약품안전처 건강기능식품 영양성분 DB를 활용하여 `analyzer.py`의 AI 약사 분석 엔진이 더욱 정확하고 전문적인 분석을 제공하도록 개선합니다.

## 개선 방향

### 1. AI 프롬프트에 영양성분 정보 주입

**현재 문제점:**
- 리뷰 텍스트만으로 분석하여 제품의 실제 성분 정보를 모름
- 허위 주장과 실제 효능을 구분하지 못함
- 성분 함량 정보 없이 분석

**개선 방안:**

```python
def analyze(self, review_text: str, product_id: Optional[int] = None, model: str = "claude-sonnet-4-5-20250929") -> Dict:
    """
    리뷰를 약사 페르소나로 분석 (영양성분 DB 통합)
    
    Args:
        review_text: 분석할 리뷰 텍스트
        product_id: 제품 ID (제공 시 영양성분 정보 포함, 없어도 오류 없음)
        model: 사용할 Claude 모델
        
    Returns:
        Dict: 분석 결과
    """
    # 입력 검증: 리뷰가 너무 짧으면 오류 반환
    if len(review_text.strip()) < 10:
        raise ValueError("리뷰 텍스트가 너무 짧습니다 (최소 10자 이상)")
    
    # 1. 영양성분 정보 조회 (실패해도 계속 진행)
    nutrition_info = None
    if product_id:
        try:
            nutrition_info = self._get_nutrition_info(product_id)
            # nutrition_info가 None이어도 정상 (정보 없음)
        except Exception:
            # 예외 발생해도 분석은 계속 (기본 모드로 동작)
            nutrition_info = None
    
    # 2. AI 프롬프트 생성 (영양성분 정보가 있으면 포함, 없으면 기본 프롬프트)
    enhanced_prompt = self._build_enhanced_prompt(review_text, nutrition_info)
    
    # 3. AI 분석 수행 (영양성분 정보 유무와 관계없이)
    # ...
```

### 2. 강화된 시스템 프롬프트

```python
ENHANCED_SYSTEM_PROMPT = """당신은 15년 경력의 임상 약사입니다.

**역할 및 태도:**
- 전문적이고 객관적인 관점에서 리뷰를 분석합니다
- 보수적인 태도로 과장된 표현을 경계합니다
- 일반 사용자도 이해할 수 있도록 명확하게 설명합니다
- **제품의 실제 영양성분 정보를 기반으로 분석합니다**

**엄격한 제약 조건:**
1. 리뷰 원문에 명시된 내용만 분석하세요
2. 리뷰에 없는 성분이나 효능을 추측하거나 추가하지 마세요
3. 모호하거나 불확실한 정보는 '판단 불가'로 처리하세요
4. 의학적 진단이나 처방을 하지 마세요
5. **제공된 영양성분 정보와 리뷰 내용을 비교하여 일치 여부를 확인하세요**
6. **리뷰에서 언급된 성분이 실제 제품에 포함되어 있는지 검증하세요**
7. **리뷰의 효능 주장이 공식 효능 범위 내인지 확인하세요**

**영양성분 정보 활용:**
- 제품의 실제 함유 성분 목록을 참고하여 분석
- 성분별 공식 효능과 리뷰의 체감 효과를 비교
- 성분 함량 정보를 바탕으로 효과의 현실성 평가
- 허위 주장이나 과장된 표현을 식별

**필수 부인 공지:**
모든 분석 결과에 다음 문구를 포함해야 합니다:
"본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."

**출력 형식:**
반드시 다음 JSON 형식으로 응답하세요:
{
  "summary": "리뷰 한 줄 요약 (사용자 체감 중심, 30자 이내)",
  "efficacy": "효능 관련 내용 (원문 근거만, 공식 효능과 비교)",
  "side_effects": "부작용 관련 내용",
  "tip": "약사의 핵심 조언 (50자 이내, 영양성분 정보 기반)",
  "ingredient_validation": {
    "mentioned_ingredients": ["리뷰에서 언급된 성분 목록"],
    "valid_ingredients": ["실제 제품에 포함된 성분"],
    "invalid_claims": ["허위 주장 목록 (있는 경우)"]
  }
}

**주의사항:**
- summary, efficacy, side_effects, tip은 모두 문자열 타입입니다
- 리뷰에 해당 정보가 없으면 "정보 없음"으로 반환
- tip은 약사 관점에서 실질적이고 유용한 조언 제공
- ingredient_validation은 영양성분 정보가 제공된 경우에만 포함
"""
```

### 3. 사용자 프롬프트 템플릿 강화

```python
def _build_enhanced_prompt(self, review_text: str, nutrition_info: Optional[Dict]) -> str:
    """
    영양성분 정보를 포함한 강화된 프롬프트 생성
    
    Args:
        review_text: 리뷰 텍스트
        nutrition_info: 영양성분 정보
        
    Returns:
        str: 강화된 프롬프트
    """
    base_prompt = """다음 건강기능식품 리뷰를 분석해주세요:

---
{review_text}
---

위 리뷰를 15년 경력 임상 약사 관점에서 분석하고, JSON 형식으로 출력해주세요.
"""
    
    if nutrition_info:
        nutrition_section = f"""

**제품 영양성분 정보:**
{self._format_nutrition_info(nutrition_info)}

**분석 시 주의사항:**
1. 리뷰에서 언급된 성분이 위 영양성분 목록에 실제로 포함되어 있는지 확인하세요
2. 리뷰의 효능 주장이 공식 효능 범위 내인지 검증하세요
3. 허위 주장이나 과장된 표현이 있으면 ingredient_validation에 명시하세요
4. 성분 함량 정보를 참고하여 효과의 현실성을 평가하세요
"""
        base_prompt += nutrition_section
    
    base_prompt += """
**분석 시 주의사항:**
1. 리뷰 원문에 없는 내용은 절대 추가하지 마세요
2. 사용자가 느낀 주관적 체감을 객관적으로 정리하세요
3. 의학적 효능이 아닌 '사용자 체감 정보'임을 명확히 하세요
4. 부작용이 언급되지 않았으면 side_effects를 "정보 없음"으로 반환하세요

본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다.
"""
    
    return base_prompt.format(review_text=review_text)
```

### 4. 영양성분 정보 조회 및 포맷팅

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
            return {
                'ingredients': response.data,
                'product_id': product_id
            }
        return None  # 정보 없음 (오류 아님)
    except Exception:
        # 모든 예외를 무시하고 None 반환 (기존 동작 유지, 오류 없음)
        return None

def _format_nutrition_info(self, nutrition_info: Dict) -> str:
    """
    영양성분 정보를 AI 프롬프트에 적합한 형식으로 포맷팅
    
    Args:
        nutrition_info: 영양성분 정보
        
    Returns:
        str: 포맷팅된 영양성분 정보 문자열
    """
    formatted = []
    for ingredient in nutrition_info.get('ingredients', []):
        name = ingredient.get('ingredient_name', '')
        amount = ingredient.get('amount', '')
        unit = ingredient.get('unit', '')
        efficacy = ingredient.get('official_efficacy', [])
        
        line = f"- {name}"
        if amount:
            line += f": {amount}{unit}"
        if efficacy:
            line += f" (공식 효능: {', '.join(efficacy)})"
        
        formatted.append(line)
    
    return '\n'.join(formatted) if formatted else "영양성분 정보 없음"
```

### 5. 분석 결과 검증 강화

```python
def analyze_safe(self, review_text: str, product_id: Optional[int] = None, model: str = "claude-sonnet-4-5-20250929") -> Dict:
    """
    안전한 분석 (오류 발생 시 기본값 반환, 영양성분 검증 포함)
    
    Args:
        review_text: 분석할 리뷰 텍스트
        product_id: 제품 ID
        model: 사용할 Claude 모델
        
    Returns:
        Dict: 분석 결과 또는 오류 정보
    """
    try:
        result = self.analyze(review_text, product_id, model)
        
        # 영양성분 검증 결과 추가 처리
        if 'ingredient_validation' in result:
            validation = result['ingredient_validation']
            if validation.get('invalid_claims'):
                # 허위 주장이 있는 경우 tip에 경고 추가
                result['tip'] = f"⚠️ 주의: {', '.join(validation['invalid_claims'])} - " + result.get('tip', '')
        
        return result
    except Exception as e:
        # 오류 처리 (기존과 동일)
        # ...
```

## 구현 요구사항

### 1. 영양성분 DB 스키마 (analyzer.py용)

```sql
-- nutrition_info 테이블
CREATE TABLE nutrition_info (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    ingredient_name TEXT NOT NULL,
    ingredient_aliases JSONB,
    amount NUMERIC,
    unit TEXT,
    official_efficacy TEXT[],           -- 공식 효능 목록
    daily_value_percentage NUMERIC,      -- 일일 권장량 대비 비율
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. 의존성 추가

```python
# analyzer.py 상단에 추가
from typing import Dict, Optional
from database.supabase_client import get_supabase_client
```

## 테스트 시나리오

### 시나리오 1: 정상 성분 언급
```
제품: 루테인 제품 (실제 성분: 루테인 10mg, 제아잔틴 2mg)
리뷰: "루테인을 먹고 눈이 덜 피로해졌어요"

기대 결과:
- ingredient_validation.valid_ingredients: ["루테인"]
- invalid_claims: [] (없음)
- tip: "루테인은 눈 건강 유지에 도움을 줄 수 있습니다..."
```

### 시나리오 2: 허위 성분 주장
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴만 포함)
리뷰: "오메가3와 코엔자임Q10이 함유되어 있어서 심혈관 건강에 좋아요"

기대 결과:
- ingredient_validation.invalid_claims: ["오메가3", "코엔자임Q10"]
- tip: "⚠️ 주의: 실제 제품에는 오메가3와 코엔자임Q10이 포함되어 있지 않습니다..."
```

### 시나리오 3: 과장된 효능 주장
```
제품: 루테인 제품 (공식 효능: "눈 건강 유지")
리뷰: "시력이 100% 회복되고 백내장도 완치되었어요!"

기대 결과:
- ingredient_validation.invalid_claims: ["시력 100% 회복", "백내장 완치"]
- tip: "⚠️ 주의: 루테인의 공식 효능은 '눈 건강 유지'이며, 시력 회복이나 백내장 완치는 인정되지 않습니다..."
```

## 우선순위

1. **높음**: AI 프롬프트에 영양성분 정보 주입
2. **높음**: 성분 검증 결과를 분석 결과에 포함
3. **중간**: 허위 주장 자동 감지 및 경고
4. **낮음**: 성분 함량 기반 효과 현실성 평가

## 참고 자료

- 식품의약품안전처 건강기능식품 정보
- 건강기능식품 공전: 성분별 공식 효능
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/

---

## 구현 완료 요약 (2026-01-08)

### ✅ 구현된 기능

1. **`analyze()` 메서드 확장**
   - `product_id` 매개변수 추가 완료
   - 영양성분 정보 조회 로직 추가 (실패해도 계속 진행)
   - 강화된 프롬프트 생성 로직 통합

2. **시스템 프롬프트 강화**
   - 영양성분 정보 활용 지침 추가 완료
   - 성분 검증 및 효능 검증 요구사항 추가
   - 출력 형식에 `ingredient_validation` 필드 명시

3. **`_build_enhanced_prompt()` 메서드 구현**
   - 영양성분 정보가 있으면 프롬프트에 포함
   - 없으면 기본 프롬프트 사용
   - 영양성분 정보 포맷팅 로직 포함

4. **`_format_nutrition_info()` 메서드 구현**
   - 영양성분 정보를 AI 프롬프트에 적합한 형식으로 변환
   - 실제 DB 스키마에 맞게 `food_name`, `representative_food_name` 필드 사용

5. **`_validate_ingredients()` 메서드 구현**
   - 리뷰에서 언급된 성분 검증
   - `nutrition_utils.py`의 함수 활용
   - 검증 결과를 분석 결과에 포함

6. **`analyze_safe()` 메서드 확장**
   - `product_id` 매개변수 추가
   - 영양성분 검증 결과 포함

### 📝 구현 세부사항

- **공통 유틸리티 활용**: `nutrition_utils.py`의 함수들을 import하여 사용
- **안전한 예외 처리**: 영양성분 정보 조회 실패 시 None 반환, 분석은 계속 진행
- **하위 호환성 유지**: `product_id`가 None이면 기본 프롬프트 사용

### 🔄 변경된 파일

- `logic_designer/analyzer.py`: 4개 메서드 추가/수정, 시스템 프롬프트 강화
- `logic_designer/nutrition_utils.py`: 공통 유틸리티 함수 모듈 (신규 생성)

### ⚠️ 주의사항

- AI 응답에 `ingredient_validation` 필드가 포함되도록 시스템 프롬프트에 명시
- 실제 DB 스키마에 맞게 영양성분 정보 포맷팅 로직 조정 필요
