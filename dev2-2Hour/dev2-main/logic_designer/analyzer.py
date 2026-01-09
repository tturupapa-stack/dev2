"""
약사 인사이트 분석 모듈
15년 경력 임상 약사 페르소나 기반 AI 분석 엔진
"""

import os
import json
from typing import Dict, Optional
from anthropic import Anthropic


class PharmacistAnalyzer:
    """15년 경력 임상 약사 페르소나 기반 AI 분석기"""

    SYSTEM_PROMPT = """당신은 15년 경력의 임상 약사입니다.

**역할 및 태도:**
- 전문적이고 객관적인 관점에서 리뷰를 분석합니다
- 보수적인 태도로 과장된 표현을 경계합니다
- 일반 사용자도 이해할 수 있도록 명확하게 설명합니다

**엄격한 제약 조건:**
1. 리뷰 원문에 명시된 내용만 분석하세요
2. 리뷰에 없는 성분이나 효능을 추측하거나 추가하지 마세요
3. 모호하거나 불확실한 정보는 '판단 불가'로 처리하세요
4. 의학적 진단이나 처방을 하지 마세요

**필수 부인 공지:**
모든 분석 결과에 다음 문구를 포함해야 합니다:
"본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."

**출력 형식:**
반드시 다음 JSON 형식으로 응답하세요:
{
  "summary": "리뷰 한 줄 요약 (사용자 체감 중심, 30자 이내)",
  "efficacy": "효능 관련 내용 (원문 근거만)",
  "side_effects": "부작용 관련 내용",
  "tip": "약사의 핵심 조언 (50자 이내)"
}

**주의사항:**
- summary, efficacy, side_effects, tip은 모두 문자열 타입입니다
- 리뷰에 해당 정보가 없으면 "정보 없음"으로 반환
- tip은 약사 관점에서 실질적이고 유용한 조언 제공
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

    def analyze(self, review_text: str, model: str = "claude-sonnet-4-5-20250929") -> Dict:
        """
        리뷰를 약사 페르소나로 분석

        Args:
            review_text: 분석할 리뷰 텍스트
            model: 사용할 Claude 모델 (기본값: claude-sonnet-4-5-20250929)

        Returns:
            Dict: {
                "summary": "한 줄 요약",
                "efficacy": "효능 관련 내용",
                "side_effects": "부작용 관련 내용",
                "tip": "약사의 핵심 조언",
                "disclaimer": "부인 공지"
            }

        Raises:
            ValueError: 리뷰 텍스트가 10자 미만인 경우
            Exception: API 호출 실패 시
        """
        # 입력 검증
        if len(review_text.strip()) < 10:
            raise ValueError("리뷰 텍스트가 너무 짧습니다 (최소 10자 이상)")

        try:
            # Anthropic API 호출
            response = self.client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0.3,  # 일관성 있는 분석을 위해 낮은 temperature
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": self.USER_PROMPT_TEMPLATE.format(
                            review_text=review_text
                        )
                    }
                ]
            )

            # JSON 파싱
            content = response.content[0].text
            result = json.loads(content)

            # 필수 필드 검증
            required_fields = ["summary", "efficacy", "side_effects", "tip"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"필수 필드 누락: {field}")

            # 부인 공지 추가
            result["disclaimer"] = "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."

            return result

        except json.JSONDecodeError as e:
            raise Exception(f"AI 응답 파싱 실패: {e}")
        except Exception as e:
            raise Exception(f"AI 분석 중 오류 발생: {e}")

    def analyze_safe(self, review_text: str, model: str = "claude-sonnet-4-5-20250929") -> Dict:
        """
        안전한 분석 (오류 발생 시 기본값 반환)

        Args:
            review_text: 분석할 리뷰 텍스트
            model: 사용할 Claude 모델

        Returns:
            Dict: 분석 결과 또는 오류 정보
        """
        try:
            return self.analyze(review_text, model)
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




