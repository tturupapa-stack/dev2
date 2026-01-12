"""
약사 인사이트 분석 모듈
15년 경력 임상 약사 페르소나 기반 AI 분석 엔진
"""

import os
import json
from typing import Dict, Optional
from anthropic import Anthropic
from .nutrition_utils import (
    get_nutrition_info_safe,
    extract_ingredients,
    is_valid_ingredient,
    get_official_efficacy
)


class PharmacistAnalyzer:
    """15년 경력 임상 약사 페르소나 기반 AI 분석기"""

    SYSTEM_PROMPT = """당신은 15년 경력의 임상 약사입니다.

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

    USER_PROMPT_TEMPLATE = """다음 건강기능식품 리뷰를 분석해주세요:

---
{review_text}
---

위 리뷰를 15년 경력 임상 약사 관점에서 분석하고, JSON 형식으로 출력해주세요.

**분석 시 주의사항:**
1. 리뷰 원문에 없는 내용은 절대 추가하지 마세요
2. 사용자가 느낀 주관적 체감을 객관적으로 정리하세요
3. 의학적 효능이 아닌 '사용자 체감 정보'임을 명확히 하세요
4. 부작용이 언급되지 않았으면 side_effects를 "정보 없음"으로 반환하세요

본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다.
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        약사 분석기 초기화

        Args:
            api_key: Anthropic API 키 (None인 경우 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API 키가 필요합니다. "
                "환경변수 ANTHROPIC_API_KEY를 설정하거나 api_key 매개변수를 전달하세요."
            )

        self.client = Anthropic(api_key=self.api_key)

    def analyze(
        self, 
        review_text: str, 
        product_id: Optional[int] = None,
        model: str = "claude-sonnet-4-5-20250929"
    ) -> Dict:
        """
        리뷰를 약사 페르소나로 분석 (영양성분 DB 통합)

        Args:
            review_text: 분석할 리뷰 텍스트
            product_id: 제품 ID (제공 시 영양성분 정보 포함, 없어도 오류 없음)
            model: 사용할 Claude 모델 (기본값: claude-sonnet-4-5-20250929)

        Returns:
            Dict: {
                "summary": "한 줄 요약",
                "efficacy": "효능 관련 내용",
                "side_effects": "부작용 관련 내용",
                "tip": "약사의 핵심 조언",
                "disclaimer": "부인 공지",
                "ingredient_validation": 성분 검증 결과 (선택적)
            }

        Raises:
            ValueError: 리뷰 텍스트가 10자 미만인 경우
            Exception: API 호출 실패 시
        """
        # 입력 검증: 리뷰가 너무 짧으면 오류 반환
        if len(review_text.strip()) < 10:
            raise ValueError("리뷰 텍스트가 너무 짧습니다 (최소 10자 이상)")
        
        # 1. 영양성분 정보 조회 (실패해도 계속 진행)
        nutrition_info = None
        if product_id:
            try:
                nutrition_info = get_nutrition_info_safe(product_id)
                # nutrition_info가 None이어도 정상 (정보 없음)
            except Exception:
                # 예외 발생해도 분석은 계속 (기본 모드로 동작)
                nutrition_info = None
        
        # 2. AI 프롬프트 생성 (영양성분 정보가 있으면 포함, 없으면 기본 프롬프트)
        user_prompt = self._build_enhanced_prompt(review_text, nutrition_info)

        try:
            # 3. Anthropic API 호출
            response = self.client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0.3,  # 일관성 있는 분석을 위해 낮은 temperature
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # 4. JSON 파싱
            content = response.content[0].text
            result = json.loads(content)

            # 5. 필수 필드 검증
            required_fields = ["summary", "efficacy", "side_effects", "tip"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"필수 필드 누락: {field}")

            # 6. 부인 공지 추가
            result["disclaimer"] = "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
            
            # 7. 영양성분 검증 결과 추가 (있는 경우)
            if nutrition_info:
                ingredient_validation = self._validate_ingredients(review_text, nutrition_info)
                result["ingredient_validation"] = ingredient_validation

            return result

        except json.JSONDecodeError as e:
            raise Exception(f"AI 응답 파싱 실패: {e}")
        except Exception as e:
            raise Exception(f"AI 분석 중 오류 발생: {e}")

    def _build_enhanced_prompt(
        self, 
        review_text: str, 
        nutrition_info: Optional[Dict] = None
    ) -> str:
        """
        영양성분 정보를 포함한 강화된 프롬프트 생성
        
        Args:
            review_text: 리뷰 텍스트
            nutrition_info: 영양성분 정보 (None이면 기본 프롬프트)
            
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

    def _format_nutrition_info(self, nutrition_info: Dict) -> str:
        """
        영양성분 정보를 AI 프롬프트에 적합한 형식으로 포맷팅
        
        Args:
            nutrition_info: 영양성분 정보
            
        Returns:
            str: 포맷팅된 영양성분 정보 문자열
        """
        formatted = []
        ingredients = nutrition_info.get('ingredients', [])
        
        if not ingredients:
            return "영양성분 정보 없음"
        
        for ingredient in ingredients:
            # 실제 스키마에 맞게 조정 필요
            name = ingredient.get('food_name', '') or \
                  ingredient.get('representative_food_name', '') or \
                  ingredient.get('ingredient_name', '')
            
            if name:
                formatted.append(f"- {name}")
        
        return "\n".join(formatted) if formatted else "영양성분 정보 없음"

    def _validate_ingredients(
        self, 
        review_text: str, 
        nutrition_info: Dict
    ) -> Dict:
        """
        리뷰에서 언급된 성분 검증
        
        Args:
            review_text: 리뷰 텍스트
            nutrition_info: 영양성분 정보
            
        Returns:
            Dict: 검증 결과
        """
        try:
            mentioned_ingredients = extract_ingredients(review_text)
            valid_ingredients = []
            invalid_ingredients = []
            
            for mentioned in mentioned_ingredients:
                if is_valid_ingredient(mentioned, nutrition_info):
                    valid_ingredients.append(mentioned)
                else:
                    invalid_ingredients.append(mentioned)
            
            return {
                "mentioned_ingredients": mentioned_ingredients,
                "valid_ingredients": valid_ingredients,
                "invalid_ingredients": invalid_ingredients,
                "has_invalid_claims": len(invalid_ingredients) > 0
            }
        except Exception:
            return {
                "mentioned_ingredients": [],
                "valid_ingredients": [],
                "invalid_ingredients": [],
                "has_invalid_claims": False
            }

    def analyze_safe(
        self, 
        review_text: str, 
        product_id: Optional[int] = None,
        model: str = "claude-sonnet-4-5-20250929"
    ) -> Dict:
        """
        안전한 분석 (오류 발생 시 기본값 반환, 영양성분 DB 통합)

        Args:
            review_text: 분석할 리뷰 텍스트
            product_id: 제품 ID (선택적)
            model: 사용할 Claude 모델

        Returns:
            Dict: 분석 결과 또는 오류 정보
        """
        try:
            return self.analyze(review_text, product_id, model)
        except ValueError as e:
            return {
                "error": "입력 오류",
                "message": str(e),
                "summary": "분석 불가",
                "efficacy": "정보 없음",
                "side_effects": "정보 없음",
                "tip": "리뷰 내용이 부족하여 분석할 수 없습니다.",
                "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
            }
        except Exception as e:
            return {
                "error": "분석 실패",
                "message": str(e),
                "summary": "분석 실패",
                "efficacy": "정보 없음",
                "side_effects": "정보 없음",
                "tip": "분석 중 오류가 발생했습니다.",
                "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
            }




