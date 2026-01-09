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
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-5-20250929"
) -> Dict:
    """
    리뷰 종합 분석 통합 함수
    
    검증 로직과 AI 분석을 순차적으로 수행하여 최종 결과를 반환합니다.

    Args:
        review_text: 분석할 리뷰 텍스트
        length_score: 길이 점수 (기본값: 50)
        repurchase_score: 재구매 점수 (기본값: 50)
        monthly_use_score: 한달 사용 점수 (기본값: 50)
        photo_score: 사진 점수 (기본값: 0)
        consistency_score: 일치도 점수 (기본값: 50)
        api_key: Anthropic API 키 (선택)
        model: 사용할 Claude 모델 (기본값: claude-sonnet-4-5-20250929)

    Returns:
        Dict: {
            "validation": {
                "trust_score": 최종 신뢰도 점수,
                "is_ad": 광고 여부,
                "reasons": 감점 사유 리스트,
                "base_score": 기본 점수,
                "penalty": 감점 점수,
                "detected_count": 감지된 항목 개수
            },
            "analysis": {
                "summary": "리뷰 요약",
                "efficacy": "효능 관련 내용",
                "side_effects": "부작용 관련 내용",
                "tip": "약사의 핵심 조언",
                "disclaimer": "부인 공지"
            } 또는 None (광고인 경우)
        }
    """
    # 입력 검증
    if len(review_text.strip()) < 10:
        return {
            "error": "REVIEW_TOO_SHORT",
            "message": "리뷰가 너무 짧습니다 (최소 10자 이상)",
            "validation": None,
            "analysis": None
        }

    # 1단계: 광고 패턴 검사
    checklist = AdChecklist()
    detected_issues = checklist.check_ad_patterns(review_text)
    penalty_count = len(detected_issues)

    # 2단계: 신뢰도 점수 계산
    calculator = TrustScoreCalculator()
    score_result = calculator.calculate_final_score(
        length_score=length_score,
        repurchase_score=repurchase_score,
        monthly_use_score=monthly_use_score,
        photo_score=photo_score,
        consistency_score=consistency_score,
        penalty_count=penalty_count
    )

    # 3단계: 광고 여부 판별
    is_ad = calculator.is_ad(
        final_score=score_result["final_score"],
        penalty_count=penalty_count
    )

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

    # 4단계: 광고가 아닌 경우에만 AI 분석 수행
    analysis_result = None
    if not is_ad:
        try:
            analyzer = PharmacistAnalyzer(api_key=api_key)
            analysis_result = analyzer.analyze_safe(review_text, model)
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




