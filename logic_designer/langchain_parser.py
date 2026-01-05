"""
LangChain Pydantic Output Parser를 활용한 리뷰 분석 모듈
ReviewValidator의 결과를 구조화된 객체로 반환
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class AdCheckItem(BaseModel):
    """광고 체크리스트 개별 항목"""
    item_number: int = Field(description="체크리스트 항목 번호 (1-13)")
    item_name: str = Field(description="항목 이름 (예: '대가성 문구 존재', '감탄사 남발' 등)")
    detected: bool = Field(description="해당 항목이 감지되었는지 여부")


class ReviewValidationResult(BaseModel):
    """리뷰 검증 결과"""
    trust_score: float = Field(
        description="최종 신뢰도 점수 (0-100). 높을수록 신뢰도가 높음"
    )
    base_score: float = Field(
        description="감점 적용 전 기본 신뢰도 점수 (0-100)"
    )
    penalty: int = Field(
        description="광고 패턴 감점 총합 (각 항목당 -10점)"
    )
    is_ad: bool = Field(
        description="광고 여부 판별 결과 (40점 미만 또는 감점 항목 3개 이상이면 True)"
    )
    detected_count: int = Field(
        description="감지된 광고 패턴 항목 개수"
    )
    detected_items: List[AdCheckItem] = Field(
        description="감지된 광고 패턴 항목 상세 정보"
    )
    reasons: List[str] = Field(
        description="광고로 판별된 사유 목록 (예: '1. 대가성 문구 존재')"
    )
    review_text: str = Field(
        description="분석된 원본 리뷰 텍스트"
    )


def parse_review_with_langchain(
    review_text: str,
    model_name: str = "gpt-4",
    temperature: float = 0,
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    openai_api_key: Optional[str] = None
) -> ReviewValidationResult:
    """
    LangChain Pydantic Output Parser를 사용하여 리뷰 텍스트를 분석하고
    구조화된 ReviewValidationResult 객체로 반환

    Args:
        review_text: 분석할 리뷰 텍스트
        model_name: 사용할 LLM 모델 이름 (기본값: "gpt-4")
        temperature: LLM temperature 설정 (기본값: 0)
        length_score: 리뷰 길이 점수 (0-100)
        repurchase_score: 재구매 여부 점수 (0-100)
        monthly_use_score: 한달 사용 여부 점수 (0-100)
        photo_score: 사진 첨부 점수 (0-100)
        consistency_score: 내용 일치도 점수 (0-100)
        openai_api_key: OpenAI API 키 (선택사항)

    Returns:
        ReviewValidationResult: 구조화된 리뷰 검증 결과 객체

    Example:
        >>> review = "이 제품 정말 좋아요!!! 완전 대박!!! 강추합니다!!!"
        >>> result = parse_review_with_langchain(
        ...     review_text=review,
        ...     length_score=60,
        ...     repurchase_score=80
        ... )
        >>> print(result.trust_score)
        >>> print(result.is_ad)
        >>> for item in result.detected_items:
        ...     print(f"{item.item_number}. {item.item_name}: {item.detected}")
    """
    # Pydantic Output Parser 초기화
    output_parser = PydanticOutputParser(pydantic_object=ReviewValidationResult)

    # Format instructions 생성
    format_instructions = output_parser.get_format_instructions()

    # Prompt Template 정의
    prompt_template = PromptTemplate(
        template="""당신은 건강기능식품 리뷰의 신뢰도를 평가하는 전문가입니다.

다음 리뷰 텍스트를 분석하여 13단계 광고 판별 체크리스트를 적용하고,
신뢰도 점수를 계산하여 구조화된 형태로 반환하세요.

## 13단계 광고 판별 체크리스트:
1. 대가성 문구 존재 (무상/무료 제공, 협찬, 받았어요 등)
2. 감탄사 남발 (!!!, ~~~, ♡♡♡, 완전/진짜/정말/너무 반복)
3. 정돈된 문단 구조 (번호매기기, 불릿 포인트 등)
4. 개인 경험 부재 (나는/저는/제가/직접 등의 표현 없음)
5. 원료 특징 나열 (성분, 함유량, mg/g 등 나열)
6. 키워드 반복 (특정 단어 5회 이상 반복)
7. 단점 회피 (부정적 의견이나 단점 언급 없음)
8. 찬사 위주 구성 (최고/강추/추천/만족 등 과도한 칭찬)
9. 전문 용어 오남용 (항산화/면역력/임상 등 전문용어 남발)
10. 비현실적 효과 강조 (100%/즉시/바로/하루만에 등)
11. 타사 제품 비교 (다른 제품보다 좋다는 비교)
12. 홍보성 블로그 문체 (~했답니다, ~해드립니다, ~추천드려요)
13. 이모티콘 과다 사용 (이모티콘 5개 이상 연속)

## 신뢰도 점수 계산 공식:
- 기본 점수 = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)
  * L (length_score): {length_score}
  * R (repurchase_score): {repurchase_score}
  * M (monthly_use_score): {monthly_use_score}
  * P (photo_score): {photo_score}
  * C (consistency_score): {consistency_score}

- 감점 = 감지된 항목 개수 × 10점
- 최종 점수 = max(0, 기본 점수 - 감점)
- 광고 판별: 최종 점수 < 40 또는 감점 항목 >= 3개

## 분석할 리뷰 텍스트:
{review_text}

{format_instructions}

위 리뷰를 분석하여 각 체크리스트 항목의 감지 여부를 판단하고,
신뢰도 점수를 계산한 후 지정된 JSON 형식으로 응답하세요.
""",
        input_variables=[
            "review_text",
            "length_score",
            "repurchase_score",
            "monthly_use_score",
            "photo_score",
            "consistency_score"
        ],
        partial_variables={"format_instructions": format_instructions}
    )

    # LLM 초기화
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        openai_api_key=openai_api_key
    )

    # Chain 생성 및 실행
    chain = prompt_template | llm | output_parser

    # 실행
    result = chain.invoke({
        "review_text": review_text,
        "length_score": length_score,
        "repurchase_score": repurchase_score,
        "monthly_use_score": monthly_use_score,
        "photo_score": photo_score,
        "consistency_score": consistency_score
    })

    return result


def parse_review_hybrid(
    review_text: str,
    use_llm: bool = False,
    **kwargs
) -> ReviewValidationResult:
    """
    하이브리드 방식으로 리뷰 분석
    - use_llm=False: validator.py의 규칙 기반 검증 사용 (빠름, 비용 없음)
    - use_llm=True: LangChain + LLM 사용 (느림, 비용 발생, 더 정교함)

    Args:
        review_text: 분석할 리뷰 텍스트
        use_llm: LLM 사용 여부 (기본값: False)
        **kwargs: parse_review_with_langchain()의 추가 매개변수

    Returns:
        ReviewValidationResult: 구조화된 리뷰 검증 결과 객체
    """
    if use_llm:
        return parse_review_with_langchain(review_text, **kwargs)
    else:
        # 규칙 기반 검증 사용
        from .validator import ReviewValidator

        validator = ReviewValidator()

        # kwargs에서 점수 파라미터 추출
        score_params = {
            k: v for k, v in kwargs.items()
            if k in ['length_score', 'repurchase_score', 'monthly_use_score',
                     'photo_score', 'consistency_score']
        }

        # 검증 수행
        validation_result = validator.validate_review(review_text, **score_params)

        # 감지된 항목 상세 정보 생성
        detected_issues = validator.check_ad_patterns(review_text)
        detected_items = []

        # 모든 13개 항목에 대해 AdCheckItem 생성
        for item_num in range(1, 14):
            item_data = validator.AD_PATTERNS[item_num]
            detected_items.append(
                AdCheckItem(
                    item_number=item_num,
                    item_name=item_data["name"],
                    detected=(item_num in detected_issues)
                )
            )

        # ReviewValidationResult 객체 생성
        result = ReviewValidationResult(
            trust_score=validation_result["trust_score"],
            base_score=validation_result["base_score"],
            penalty=validation_result["penalty"],
            is_ad=validation_result["is_ad"],
            detected_count=validation_result["detected_count"],
            detected_items=detected_items,
            reasons=validation_result["reasons"],
            review_text=review_text
        )

        return result


# 편의 함수
def analyze_review(review_text: str, **kwargs) -> ReviewValidationResult:
    """
    리뷰 분석 편의 함수 (기본적으로 규칙 기반 사용)

    Args:
        review_text: 분석할 리뷰 텍스트
        **kwargs: parse_review_hybrid()의 추가 매개변수

    Returns:
        ReviewValidationResult: 구조화된 리뷰 검증 결과 객체
    """
    return parse_review_hybrid(review_text, **kwargs)
