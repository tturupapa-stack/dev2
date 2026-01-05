"""
신뢰도 점수 계산 모듈
리뷰의 신뢰도를 수치화하여 평가합니다.
"""

from typing import Dict


class TrustScoreCalculator:
    """신뢰도 점수 계산 클래스"""

    def __init__(self):
        """신뢰도 점수 계산기 초기화"""
        pass

    def calculate_base_score(
        self,
        length_score: float,
        repurchase_score: float,
        monthly_use_score: float,
        photo_score: float,
        consistency_score: float
    ) -> float:
        """
        신뢰도 기본 점수 계산

        공식: S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)

        Args:
            length_score (L): 리뷰 길이 점수 (0-100)
            repurchase_score (R): 재구매 여부 점수 (0-100)
            monthly_use_score (M): 한달 사용 여부 점수 (0-100)
            photo_score (P): 사진 첨부 점수 (0-100)
            consistency_score (C): 내용 일치도 점수 (0-100)

        Returns:
            float: 기본 신뢰도 점수 (0-100)
        """
        score = (
            length_score * 0.2 +
            repurchase_score * 0.2 +
            monthly_use_score * 0.3 +
            photo_score * 0.1 +
            consistency_score * 0.2
        )
        return round(score, 2)

    def apply_penalty(self, base_score: float, penalty_count: int, penalty_per_item: int = 10) -> float:
        """
        감점 적용

        Args:
            base_score: 기본 점수
            penalty_count: 감점 항목 개수
            penalty_per_item: 항목당 감점 점수 (기본값: 10)

        Returns:
            float: 감점 적용 후 최종 점수 (0 이상)
        """
        penalty = penalty_count * penalty_per_item
        final_score = max(0, base_score - penalty)
        return round(final_score, 2)

    def calculate_final_score(
        self,
        length_score: float = 50,
        repurchase_score: float = 50,
        monthly_use_score: float = 50,
        photo_score: float = 0,
        consistency_score: float = 50,
        penalty_count: int = 0,
        penalty_per_item: int = 10
    ) -> Dict:
        """
        최종 신뢰도 점수 계산 (기본 점수 + 감점)

        Args:
            length_score: 길이 점수 (기본값: 50)
            repurchase_score: 재구매 점수 (기본값: 50)
            monthly_use_score: 한달 사용 점수 (기본값: 50)
            photo_score: 사진 점수 (기본값: 0)
            consistency_score: 일치도 점수 (기본값: 50)
            penalty_count: 감점 항목 개수 (기본값: 0)
            penalty_per_item: 항목당 감점 점수 (기본값: 10)

        Returns:
            Dict: {
                "base_score": 기본 점수,
                "penalty": 감점 점수,
                "final_score": 최종 점수,
                "raw_scores": 원시 점수 딕셔너리
            }
        """
        # 기본 점수 계산
        base_score = self.calculate_base_score(
            length_score,
            repurchase_score,
            monthly_use_score,
            photo_score,
            consistency_score
        )

        # 감점 적용
        penalty = penalty_count * penalty_per_item
        final_score = self.apply_penalty(base_score, penalty_count, penalty_per_item)

        return {
            "base_score": base_score,
            "penalty": penalty,
            "final_score": final_score,
            "raw_scores": {
                "L": length_score,
                "R": repurchase_score,
                "M": monthly_use_score,
                "P": photo_score,
                "C": consistency_score
            }
        }

    def is_ad(self, final_score: float, penalty_count: int, threshold: float = 40) -> bool:
        """
        광고 여부 판별

        Args:
            final_score: 최종 신뢰도 점수
            penalty_count: 감점 항목 개수
            threshold: 광고 판별 임계값 (기본값: 40)

        Returns:
            bool: 광고 여부 (True: 광고, False: 일반 리뷰)
        """
        # 40점 미만 또는 감점 항목 3개 이상이면 광고로 판별
        return final_score < threshold or penalty_count >= 3


# 편의 함수
def calculate_trust_score(
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    penalty_count: int = 0
) -> Dict:
    """
    신뢰도 점수 계산 편의 함수

    Args:
        length_score: 길이 점수 (기본값: 50)
        repurchase_score: 재구매 점수 (기본값: 50)
        monthly_use_score: 한달 사용 점수 (기본값: 50)
        photo_score: 사진 점수 (기본값: 0)
        consistency_score: 일치도 점수 (기본값: 50)
        penalty_count: 감점 항목 개수 (기본값: 0)

    Returns:
        Dict: 신뢰도 점수 계산 결과
    """
    calculator = TrustScoreCalculator()
    return calculator.calculate_final_score(
        length_score,
        repurchase_score,
        monthly_use_score,
        photo_score,
        consistency_score,
        penalty_count
    )
