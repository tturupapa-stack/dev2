"""
평점 기반 신뢰도 분석 모듈
Supabase DB의 rating_avg, rating_count를 활용한 리뷰 평점 신뢰도 평가
"""

from typing import Dict, Optional


class RatingAnalyzer:
    """평점 기반 신뢰도 분석 클래스"""

    def __init__(self):
        """평점 분석기 초기화"""
        pass

    def calculate_rating_reliability(
        self,
        review_rating: Optional[int],
        product_rating_avg: Optional[float],
        product_rating_count: Optional[int]
    ) -> float:
        """
        평점 신뢰도 점수 계산

        Args:
            review_rating: 개별 리뷰 평점 (1-5), None 가능
            product_rating_avg: 제품 평균 평점 (1.0-5.0), None 가능
            product_rating_count: 총 평점 개수, None 가능

        Returns:
            float: 평점 신뢰도 점수 (0-100)
        """
        # NULL 체크 - 데이터가 없으면 중립 점수 반환
        if (review_rating is None or
            product_rating_avg is None or
            product_rating_count is None):
            return 50.0  # 중립 점수

        # 1. 평점 차이 분석 (60점 만점)
        deviation_score = self._calculate_deviation_score(
            review_rating, product_rating_avg
        )

        # 2. 극단 평점 패널티 (20점 만점)
        extremity_score = self._calculate_extremity_score(review_rating)

        # 3. 평점 개수 가중치 (20점 만점)
        count_weight = self._calculate_count_weight(product_rating_count)

        # 4. 5점 리뷰 추가 패널티 (평균보다 높을 경우)
        five_star_penalty = 0
        if review_rating == 5 and product_rating_avg < 4.8:
            diff = 5 - product_rating_avg
            if diff > 1.0:
                five_star_penalty = 20  # 큰 차이는 강한 패널티
            elif diff > 0.5:
                five_star_penalty = 15  # 중간 차이
            else:
                five_star_penalty = 10  # 작은 차이

        # 최종 평점 신뢰도
        total_score = deviation_score + extremity_score + count_weight - five_star_penalty

        return round(max(0, total_score), 2)  # 0점 이상 유지

    def _calculate_deviation_score(
        self,
        review_rating: int,
        product_rating_avg: float
    ) -> float:
        """
        평점 차이 점수 계산 (0-60점)

        평균과 가까울수록 높은 점수
        """
        diff = abs(review_rating - product_rating_avg)

        if diff <= 0.5:
            return 60.0  # 평균과 거의 일치 (신뢰도 매우 높음)
        elif diff <= 1.0:
            return 50.0  # 약간 차이 (신뢰도 높음)
        elif diff <= 1.5:
            return 35.0  # 중간 차이 (보통)
        elif diff <= 2.0:
            return 20.0  # 큰 차이 (광고 의심)
        elif diff <= 2.5:
            return 10.0  # 매우 큰 차이 (광고 가능성 높음)
        else:
            return 0.0   # 극단적 차이 (광고 확률 매우 높음)

    def _calculate_extremity_score(self, review_rating: int) -> float:
        """
        극단 평점 점수 계산 (0-20점)

        2-4점: 정상 (20점)
        1점/5점: 극단 평점 (패널티)
        """
        if review_rating == 5:
            return 5.0   # 5점 만점: 광고성 의심 (강한 패널티)
        elif review_rating == 1:
            return 5.0   # 1점: 악의적 비방 의심 (강한 패널티)
        else:
            return 20.0  # 2-4점: 신뢰도 높음

    def _calculate_count_weight(self, product_rating_count: int) -> float:
        """
        평점 개수 가중치 계산 (0-20점)

        평점 개수가 많을수록 평균이 신뢰할 수 있음
        """
        if product_rating_count >= 1000:
            return 20.0  # 매우 많은 평점 (매우 신뢰)
        elif product_rating_count >= 500:
            return 18.0  # 많은 평점 (신뢰)
        elif product_rating_count >= 100:
            return 15.0  # 충분한 평점 (보통 신뢰)
        elif product_rating_count >= 50:
            return 12.0  # 적당한 평점
        elif product_rating_count >= 10:
            return 8.0   # 적은 평점 (신뢰도 낮음)
        else:
            return 5.0   # 매우 적은 평점 (신뢰도 매우 낮음)

    def detect_rating_manipulation(
        self,
        review_rating: Optional[int],
        product_rating_avg: Optional[float],
        rating_reliability_score: float,
        detected_issues: Dict[int, str]
    ) -> bool:
        """
        평점 조작 패턴 탐지

        Args:
            review_rating: 개별 리뷰 평점
            product_rating_avg: 제품 평균 평점
            rating_reliability_score: 평점 신뢰도 점수
            detected_issues: 13단계 체크리스트 감지 항목

        Returns:
            bool: True=조작 의심, False=정상
        """
        if review_rating is None or product_rating_avg is None:
            return False

        # 패턴 1: 5점 만점 + 낮은 평점 신뢰도
        if review_rating == 5 and rating_reliability_score < 30:
            return True  # "5점 폭격" 광고 의심

        # 패턴 2: 평점 차이 극단 (2.5점 이상)
        if abs(review_rating - product_rating_avg) > 2.5:
            return True  # 평점 조작 의심

        # 패턴 3: 5점 + 감탄사 남발 + 찬사 위주
        if (review_rating == 5 and
            len(detected_issues) >= 2 and
            (2 in detected_issues or 8 in detected_issues)):
            return True  # 광고성 리뷰 확률 높음

        # 패턴 4: 1점 + 극단적 부정
        if (review_rating == 1 and
            rating_reliability_score < 20):
            return True  # 악의적 비방 의심

        return False

    def get_rating_pattern_type(
        self,
        review_rating: Optional[int],
        product_rating_avg: Optional[float]
    ) -> str:
        """
        평점 패턴 분류

        Args:
            review_rating: 개별 리뷰 평점
            product_rating_avg: 제품 평균 평점

        Returns:
            str: 패턴 타입
                - 'normal': 정상 범위
                - 'extreme_positive': 극단 긍정 (5점)
                - 'extreme_negative': 극단 부정 (1점)
                - 'suspicious_high': 의심스러운 고평점
                - 'suspicious_low': 의심스러운 저평점
                - 'unknown': 데이터 부족
        """
        if review_rating is None or product_rating_avg is None:
            return 'unknown'

        diff = review_rating - product_rating_avg

        # 5점 리뷰
        if review_rating == 5:
            if diff > 1.5:
                return 'suspicious_high'  # 평균보다 훨씬 높음
            else:
                return 'extreme_positive'

        # 1점 리뷰
        elif review_rating == 1:
            if diff < -1.5:
                return 'suspicious_low'  # 평균보다 훨씬 낮음
            else:
                return 'extreme_negative'

        # 2-4점 리뷰 (정상 범위)
        else:
            if abs(diff) <= 1.0:
                return 'normal'
            elif diff > 1.0:
                return 'suspicious_high'
            else:
                return 'suspicious_low'

    def get_rating_insight(
        self,
        review_rating: Optional[int],
        product_rating_avg: Optional[float],
        product_rating_count: Optional[int],
        rating_reliability_score: float
    ) -> Dict[str, any]:
        """
        평점 분석 인사이트 생성

        Args:
            review_rating: 개별 리뷰 평점
            product_rating_avg: 제품 평균 평점
            product_rating_count: 총 평점 개수
            rating_reliability_score: 평점 신뢰도 점수

        Returns:
            Dict: 분석 인사이트
        """
        if review_rating is None or product_rating_avg is None:
            return {
                "pattern": "unknown",
                "reliability_level": "unknown",
                "message": "평점 데이터가 부족합니다.",
                "recommendation": "평점 정보가 없어 신뢰도를 판단하기 어렵습니다."
            }

        pattern = self.get_rating_pattern_type(review_rating, product_rating_avg)
        diff = abs(review_rating - product_rating_avg)

        # 신뢰도 레벨 결정
        if rating_reliability_score >= 70:
            reliability_level = "high"
            message = "평점이 제품 평균과 일치하며 신뢰도가 높습니다."
        elif rating_reliability_score >= 50:
            reliability_level = "medium"
            message = "평점이 제품 평균과 약간 차이가 있습니다."
        elif rating_reliability_score >= 30:
            reliability_level = "low"
            message = "평점이 제품 평균과 차이가 크며 신뢰도가 낮습니다."
        else:
            reliability_level = "very_low"
            message = "평점이 제품 평균과 크게 다르며 광고성 리뷰로 의심됩니다."

        # 권장 사항
        if pattern == 'suspicious_high':
            recommendation = "평균보다 높은 평점입니다. 광고성 리뷰일 가능성을 고려하세요."
        elif pattern == 'suspicious_low':
            recommendation = "평균보다 낮은 평점입니다. 악의적 리뷰일 가능성을 고려하세요."
        elif pattern == 'extreme_positive':
            recommendation = "5점 만점 리뷰입니다. 다른 리뷰와 함께 참고하세요."
        elif pattern == 'extreme_negative':
            recommendation = "1점 리뷰입니다. 개인적 경험일 수 있으므로 다른 리뷰도 확인하세요."
        else:
            recommendation = "신뢰할 수 있는 평점 범위입니다."

        return {
            "pattern": pattern,
            "reliability_level": reliability_level,
            "message": message,
            "recommendation": recommendation,
            "rating_diff": round(diff, 2),
            "rating_count": product_rating_count
        }


# 편의 함수
def analyze_rating(
    review_rating: Optional[int],
    product_rating_avg: Optional[float],
    product_rating_count: Optional[int]
) -> Dict:
    """
    평점 분석 편의 함수

    Args:
        review_rating: 개별 리뷰 평점
        product_rating_avg: 제품 평균 평점
        product_rating_count: 총 평점 개수

    Returns:
        Dict: {
            "rating_reliability_score": 평점 신뢰도 점수 (0-100),
            "pattern": 평점 패턴 타입,
            "insight": 분석 인사이트
        }
    """
    analyzer = RatingAnalyzer()

    reliability_score = analyzer.calculate_rating_reliability(
        review_rating,
        product_rating_avg,
        product_rating_count
    )

    pattern = analyzer.get_rating_pattern_type(
        review_rating,
        product_rating_avg
    )

    insight = analyzer.get_rating_insight(
        review_rating,
        product_rating_avg,
        product_rating_count,
        reliability_score
    )

    return {
        "rating_reliability_score": reliability_score,
        "pattern": pattern,
        "insight": insight
    }
