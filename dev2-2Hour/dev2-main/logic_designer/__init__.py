"""
건기식 리뷰 팩트체크 로직 설계 모듈
검증 로직과 AI 분석을 통합한 파이프라인
"""

from typing import Dict, Optional
from .checklist import AdChecklist, check_ad_patterns
from .trust_score import TrustScoreCalculator, calculate_trust_score
from .analyzer import PharmacistAnalyzer


def analyze(
    review_text: str,
    product_id: Optional[int] = None,
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-5-20250929",
    use_nutrition_validation: bool = True
) -> Dict:
    """
    리뷰 종합 분석 통합 함수 (영양성분 DB 통합, 안전한 방식)
    
    검증 로직과 AI 분석을 순차적으로 수행하여 최종 결과를 반환합니다.
    영양성분 DB 정보를 활용하여 더욱 정확한 검증과 분석을 수행합니다.
    
    중요: 영양성분 DB가 없어도 오류 없이 동작합니다.
    리뷰가 짧거나 없어도 적절히 처리합니다.

    Args:
        review_text: 분석할 리뷰 텍스트
        product_id: 제품 ID (선택적, 영양성분 검증용)
        length_score: 길이 점수 (기본값: 50)
        repurchase_score: 재구매 점수 (기본값: 50)
        monthly_use_score: 한달 사용 점수 (기본값: 50)
        photo_score: 사진 점수 (기본값: 0)
        consistency_score: 일치도 점수 (기본값: 50)
        api_key: Anthropic API 키 (선택)
        model: 사용할 Claude 모델 (기본값: claude-sonnet-4-5-20250929)
        use_nutrition_validation: 영양성분 검증 사용 여부 (기본값: True)

    Returns:
        Dict: {
            "validation": {
                "trust_score": 최종 신뢰도 점수,
                "is_ad": 광고 여부,
                "reasons": 감점 사유 리스트,
                "base_score": 기본 점수,
                "nutrition_score": 영양성분 일치도 점수 (선택적),
                "penalty": 감점 점수,
                "detected_count": 감지된 항목 개수
            },
            "analysis": {
                "summary": "리뷰 요약",
                "efficacy": "효능 관련 내용",
                "side_effects": "부작용 관련 내용",
                "tip": "약사의 핵심 조언",
                "disclaimer": "부인 공지",
                "ingredient_validation": 성분 검증 결과 (선택적)
            } 또는 None (광고인 경우)
        }
    """
    # 입력 검증: 리뷰가 너무 짧으면 오류 반환
    if len(review_text.strip()) < 10:
        return {
            "error": "REVIEW_TOO_SHORT",
            "message": "리뷰가 너무 짧습니다 (최소 10자 이상)",
            "validation": None,
            "analysis": None
        }

    # 1단계: 광고 패턴 검사 (영양성분 DB 통합)
    try:
        checklist = AdChecklist()
        detected_issues = checklist.check_ad_patterns(review_text, product_id)
        penalty_count = len(detected_issues)
    except Exception:
        # 체크리스트 검사 실패 시 기본값 사용
        detected_issues = {}
        penalty_count = 0

    # 2단계: 신뢰도 점수 계산 (영양성분 일치도 포함)
    try:
        calculator = TrustScoreCalculator()
        score_result = calculator.calculate_final_score(
            length_score=length_score,
            repurchase_score=repurchase_score,
            monthly_use_score=monthly_use_score,
            photo_score=photo_score,
            consistency_score=consistency_score,
            penalty_count=penalty_count,
            review_text=review_text if use_nutrition_validation else None,
            product_id=product_id if use_nutrition_validation else None,
            use_nutrition_score=use_nutrition_validation
        )
    except Exception:
        # 점수 계산 실패 시 기본값 사용
        score_result = {
            "base_score": 50.0,
            "nutrition_score": 50.0,
            "penalty": penalty_count * 10,
            "final_score": max(0, 50.0 - (penalty_count * 10)),
            "raw_scores": {
                "L": length_score,
                "R": repurchase_score,
                "M": monthly_use_score,
                "P": photo_score,
                "C": consistency_score,
                "N": 50.0
            }
        }

    # 3단계: 광고 여부 판별
    try:
        is_ad = calculator.is_ad(
            final_score=score_result["final_score"],
            penalty_count=penalty_count
        )
    except Exception:
        # 광고 판별 실패 시 기본값 사용
        is_ad = score_result["final_score"] < 40 or penalty_count >= 3

    # 감점 사유 리스트 생성
    reasons = [f"{num}. {name}" for num, name in detected_issues.items()]

    validation_result = {
        "trust_score": score_result["final_score"],
        "is_ad": is_ad,
        "reasons": reasons,
        "base_score": score_result["base_score"],
        "penalty": score_result["penalty"],
        "detected_count": penalty_count,
        "raw_scores": score_result["raw_scores"]
    }
    
    # 영양성분 점수 추가 (있는 경우)
    if "nutrition_score" in score_result:
        validation_result["nutrition_score"] = score_result["nutrition_score"]

    # 4단계: 광고가 아닌 경우에만 AI 분석 수행 (영양성분 정보 포함)
    analysis_result = None
    if not is_ad:
        try:
            analyzer = PharmacistAnalyzer(api_key=api_key)
            analysis_result = analyzer.analyze_safe(
                review_text, 
                product_id=product_id if use_nutrition_validation else None,
                model=model
            )
        except Exception as e:
            analysis_result = {
                "error": "ANALYSIS_ERROR",
                "message": str(e),
                "summary": "분석 실패",
                "efficacy": "정보 없음",
                "side_effects": "정보 없음",
                "tip": "분석 중 오류가 발생했습니다.",
                "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
            }
    else:
        # 광고인 경우 분석 생략
        analysis_result = {
            "error": "AD_REVIEW",
            "message": "광고 리뷰는 분석하지 않습니다.",
            "summary": "광고 리뷰",
            "efficacy": "정보 없음",
            "side_effects": "정보 없음",
            "tip": "이 리뷰는 광고로 판별되어 분석하지 않습니다.",
            "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
        }

    return {
        "validation": validation_result,
        "analysis": analysis_result
    }


__all__ = [
    "analyze",
    "AdChecklist",
    "check_ad_patterns",
    "TrustScoreCalculator",
    "calculate_trust_score",
    "PharmacistAnalyzer"
]




