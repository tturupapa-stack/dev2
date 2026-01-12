"""
신뢰도 점수 계산 모듈
리뷰의 신뢰도를 수치화하여 평가합니다.
"""

from typing import Dict, Optional
from .nutrition_utils import (
    get_nutrition_info_safe,
    extract_ingredients,
    is_valid_ingredient
)


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
        consistency_score: float,
        nutrition_score: Optional[float] = None
    ) -> float:
        """
        신뢰도 기본 점수 계산

        공식 (영양성분 점수 없을 때):
        S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)

        공식 (영양성분 점수 있을 때):
        S = (L × 0.15) + (R × 0.15) + (M × 0.25) + (P × 0.1) + (C × 0.15) + (N × 0.2)

        Args:
            length_score (L): 리뷰 길이 점수 (0-100)
            repurchase_score (R): 재구매 여부 점수 (0-100)
            monthly_use_score (M): 한달 사용 여부 점수 (0-100)
            photo_score (P): 사진 첨부 점수 (0-100)
            consistency_score (C): 내용 일치도 점수 (0-100)
            nutrition_score (N): 영양성분 일치도 점수 (0-100, 선택적)

        Returns:
            float: 기본 신뢰도 점수 (0-100)
        """
        if nutrition_score is not None:
            # 영양성분 점수 포함 공식
            score = (
                length_score * 0.15 +
                repurchase_score * 0.15 +
                monthly_use_score * 0.25 +
                photo_score * 0.1 +
                consistency_score * 0.15 +
                nutrition_score * 0.2
            )
        else:
            # 기존 공식 (하위 호환성)
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
            nutrition_info = get_nutrition_info_safe(product_id)
            if not nutrition_info:
                return 50.0  # 정보 없으면 중간값 (오류 아님)
            
            # 2. 리뷰에서 성분명 추출
            mentioned_ingredients = extract_ingredients(review_text)
            
            # 3. 성분 언급이 없으면 중간값 반환
            if len(mentioned_ingredients) == 0:
                return 50.0
            
            # 4. 실제 성분과 매칭
            valid_count = 0
            invalid_count = 0
            
            for mentioned in mentioned_ingredients:
                if is_valid_ingredient(mentioned, nutrition_info):
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
        최종 신뢰도 점수 계산 (기본 점수 + 감점, 영양성분 일치도 포함)

        Args:
            length_score: 길이 점수 (기본값: 50)
            repurchase_score: 재구매 점수 (기본값: 50)
            monthly_use_score: 한달 사용 점수 (기본값: 50)
            photo_score: 사진 점수 (기본값: 0)
            consistency_score: 일치도 점수 (기본값: 50)
            penalty_count: 감점 항목 개수 (기본값: 0)
            penalty_per_item: 항목당 감점 점수 (기본값: 10)
            review_text: 리뷰 텍스트 (영양성분 점수 계산용, 선택적)
            product_id: 제품 ID (영양성분 정보 조회용, 선택적)
            use_nutrition_score: 영양성분 점수 사용 여부 (기본값: True)

        Returns:
            Dict: {
                "base_score": 기본 점수,
                "nutrition_score": 영양성분 일치도 점수,
                "penalty": 감점 점수,
                "final_score": 최종 점수,
                "raw_scores": 원시 점수 딕셔너리
            }
        """
        # 영양성분 일치도 점수 계산 (선택적)
        nutrition_score = 50.0  # 기본값 (중간값)
        if use_nutrition_score and review_text and product_id:
            try:
                nutrition_score = self.calculate_nutrition_consistency_score(
                    review_text,
                    product_id
                )
            except Exception:
                # 계산 실패 시 기본값 사용 (오류 없이)
                nutrition_score = 50.0
        
        # 기본 점수 계산 (영양성분 점수 포함 여부에 따라)
        if use_nutrition_score and review_text and product_id:
            base_score = self.calculate_base_score(
                length_score,
                repurchase_score,
                monthly_use_score,
                photo_score,
                consistency_score,
                nutrition_score
            )
        else:
            # 기존 방식 (하위 호환성)
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
