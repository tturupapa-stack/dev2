"""
건기식 리뷰 신뢰도 검증 모듈
13단계 광고 판별 체크리스트와 신뢰도 공식을 구현
"""

import re
from typing import Dict, List, Tuple


class ReviewValidator:
    """리뷰 신뢰도 검증 클래스"""

    # 13단계 광고 판별 체크리스트 패턴
    AD_PATTERNS = {
        1: {
            "name": "대가성 문구 존재",
            "patterns": [
                r"무상.*제공", r"무료.*제공", r"받았어요", r"받아서",
                r"선물.*받", r"협찬", r"제공.*받"
            ]
        },
        2: {
            "name": "감탄사 남발",
            "patterns": [
                r"[!!!!]{3,}", r"[~~]{3,}", r"[♡♥❤️]{3,}",
                r"(완전|진짜|정말|너무).{0,10}(완전|진짜|정말|너무)"
            ]
        },
        3: {
            "name": "정돈된 문단 구조",
            "patterns": [
                r"^[0-9]\.", r"^-\s", r"^•\s",
                r"(\n[0-9]\.|◾|▪️|✓).{10,}"
            ]
        },
        4: {
            "name": "개인 경험 부재",
            "patterns": [
                r"^(?!.*(나는|저는|제가|내가|우리|직접|실제로)).*$"
            ]
        },
        5: {
            "name": "원료 특징 나열",
            "patterns": [
                r"(함유|성분|원료|추출물).{5,30}(함유|성분|원료|추출물)",
                r"(mg|g|mcg|IU).{0,20}(mg|g|mcg|IU)"
            ]
        },
        6: {
            "name": "키워드 반복",
            "patterns": []  # 동적 검사 필요
        },
        7: {
            "name": "단점 회피",
            "patterns": []  # 부정적 표현 부재 검사
        },
        8: {
            "name": "찬사 위주 구성",
            "patterns": [
                r"(최고|강추|추천|만족|좋아요|대박|훌륭).{0,20}(최고|강추|추천|만족|좋아요|대박|훌륭)"
            ]
        },
        9: {
            "name": "전문 용어 오남용",
            "patterns": [
                r"(항산화|면역력|대사|흡수율|생체이용률|임상).{5,40}(항산화|면역력|대사|흡수율|생체이용률|임상)"
            ]
        },
        10: {
            "name": "비현실적 효과 강조",
            "patterns": [
                r"(100%|완벽|즉시|바로|단|하루|일주일).{0,20}(효과|개선|변화|달라)",
                r"(기적|놀라운|엄청난|극적인).{0,10}(효과|변화)"
            ]
        },
        11: {
            "name": "타사 제품 비교",
            "patterns": [
                r"(다른|타사|기존|일반).{0,20}제품.{0,20}(비해|달리|차별|보다.{0,10}(좋|나은|우수|뛰어))",
                r"VS\s|vs\s|제품\s+(비교|대결)"
            ]
        },
        12: {
            "name": "홍보성 블로그 문체",
            "patterns": [
                r"~했답니다", r"~해드립니다", r"~하세요", r"~추천드려요",
                r"후기.*남겨요", r"리뷰.*남겨요"
            ]
        },
        13: {
            "name": "이모티콘 과다 사용",
            "patterns": [
                r"[😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚]{5,}"
            ]
        }
    }

    def __init__(self):
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

        S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)

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

    def check_ad_patterns(self, review_text: str) -> Dict[int, str]:
        """
        13단계 광고 판별 체크리스트 검사

        Args:
            review_text: 검사할 리뷰 텍스트

        Returns:
            Dict[int, str]: {항목번호: 항목명} 형태로 감점된 항목 반환
        """
        detected_issues = {}

        for item_num, item_data in self.AD_PATTERNS.items():
            name = item_data["name"]
            patterns = item_data["patterns"]

            # 특수 케이스 처리
            if item_num == 4:  # 개인 경험 부재
                if not self._has_personal_experience(review_text):
                    detected_issues[item_num] = name
                continue

            if item_num == 6:  # 키워드 반복
                if self._has_keyword_repetition(review_text):
                    detected_issues[item_num] = name
                continue

            if item_num == 7:  # 단점 회피
                if not self._has_negative_opinion(review_text):
                    detected_issues[item_num] = name
                continue

            # 정규표현식 패턴 매칭
            for pattern in patterns:
                if re.search(pattern, review_text, re.IGNORECASE | re.MULTILINE):
                    detected_issues[item_num] = name
                    break

        return detected_issues

    def _has_personal_experience(self, text: str) -> bool:
        """개인 경험 표현 존재 여부 검사"""
        personal_patterns = [
            r"나는", r"저는", r"제가", r"내가", r"우리",
            r"직접", r"실제로", r"먹어보니", r"사용해보니"
        ]
        for pattern in personal_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _has_keyword_repetition(self, text: str, threshold: int = 5) -> bool:
        """특정 키워드 과도한 반복 검사"""
        words = re.findall(r'\b\w+\b', text)
        if len(words) < 10:
            return False

        word_freq = {}
        for word in words:
            if len(word) >= 2:  # 2글자 이상 단어만
                word_freq[word] = word_freq.get(word, 0) + 1

        # 가장 많이 반복된 단어가 threshold 이상이면 True
        max_freq = max(word_freq.values()) if word_freq else 0
        return max_freq >= threshold

    def _has_negative_opinion(self, text: str) -> bool:
        """부정적 의견 또는 단점 언급 여부 검사"""
        negative_patterns = [
            r"단점", r"아쉬", r"불편", r"별로", r"그런데",
            r"하지만", r"다만", r"개선", r"부족", r"안.*좋"
        ]
        for pattern in negative_patterns:
            if re.search(pattern, text):
                return True
        return False

    def validate_review(
        self,
        review_text: str,
        length_score: float = 50,
        repurchase_score: float = 50,
        monthly_use_score: float = 50,
        photo_score: float = 0,
        consistency_score: float = 50
    ) -> Dict:
        """
        리뷰 종합 검증 수행

        Args:
            review_text: 검증할 리뷰 텍스트
            length_score: 길이 점수 (기본값: 50)
            repurchase_score: 재구매 점수 (기본값: 50)
            monthly_use_score: 한달 사용 점수 (기본값: 50)
            photo_score: 사진 점수 (기본값: 0)
            consistency_score: 일치도 점수 (기본값: 50)

        Returns:
            Dict: {
                "trust_score": 최종 신뢰도 점수,
                "is_ad": 광고 여부 (bool),
                "reasons": 감점된 항목 리스트 (List[str])
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

        # 광고 패턴 검사
        detected_issues = self.check_ad_patterns(review_text)

        # 감점 적용 (항목당 -10점)
        penalty = len(detected_issues) * 10
        final_score = max(0, base_score - penalty)

        # 광고 판별: 40점 미만 또는 감점 항목 3개 이상
        is_ad = final_score < 40 or len(detected_issues) >= 3

        # 감점 사유 리스트
        reasons = [f"{num}. {name}" for num, name in detected_issues.items()]

        return {
            "trust_score": final_score,
            "is_ad": is_ad,
            "reasons": reasons,
            "base_score": base_score,
            "penalty": penalty,
            "detected_count": len(detected_issues)
        }


# 편의 함수
def validate_review(review_text: str, **kwargs) -> Dict:
    """
    리뷰 검증 편의 함수

    Args:
        review_text: 검증할 리뷰 텍스트
        **kwargs: 선택적 점수 매개변수

    Returns:
        Dict: 검증 결과
    """
    validator = ReviewValidator()
    return validator.validate_review(review_text, **kwargs)
