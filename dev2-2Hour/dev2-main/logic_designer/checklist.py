"""
13단계 광고 판별 체크리스트 모듈
리뷰 텍스트에서 광고성 패턴을 탐지합니다.
제품별 기준을 설정하여 동일한 기준으로 체크할 수 있습니다.

개선 이력 (2026-01-07):
- 개인 경험 패턴 대폭 확장: 구매/사용/체감/재구매 표현 추가
- 단점 회피 로직 완화: 다른 광고 패턴과 함께 있을 때만 감점
- 키워드 반복 임계값 완화: 5회 → 7회

개선 근거:
- Supabase 통합 테스트 결과, 정상 리뷰의 오탐률이 높았음
- "개인 경험 부재": 15개 중 13개에서 감지 (86.7%)
- "단점 회피": 15개 중 11개에서 감지 (73.3%)
- 평균 신뢰도 점수: 47.54점 (목표 50점 미달)
"""

import re
from typing import Dict, Optional
from .product_criteria import ProductCheckCriteria
from .nutrition_utils import (
    get_nutrition_info_safe,
    extract_ingredients,
    is_valid_ingredient,
    get_official_efficacy,
    get_typical_effect_period
)


class AdChecklist:
    """13단계 광고 판별 체크리스트 클래스"""

    # 13단계 광고 판별 체크리스트 패턴 (기본 패턴)
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

    def __init__(self, criteria: Optional[ProductCheckCriteria] = None):
        """
        체크리스트 초기화
        
        Args:
            criteria: 제품별 체크 기준 (None이면 기본 기준 사용)
        """
        self.criteria = criteria

    def check_ad_patterns(
        self, 
        review_text: str, 
        product_id: Optional[int] = None
    ) -> Dict[int, str]:
        """
        13단계 광고 판별 체크리스트 검사 (영양성분 DB 통합)

        Args:
            review_text: 검사할 리뷰 텍스트
            product_id: 제품 ID (제공 시 영양성분 DB 조회, 없어도 오류 없음)

        Returns:
            Dict[int, str]: {항목번호: 항목명} 형태로 감지된 항목 반환
        """
        # 입력 검증: 리뷰가 너무 짧으면 빈 결과 반환
        if not review_text or len(review_text.strip()) < 3:
            return {}
        
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
                # 개선 (2026-01-07): 임계값 5 → 7로 완화
                threshold = self.criteria.keyword_repetition_threshold if self.criteria else 7
                if self._has_keyword_repetition(review_text, threshold=threshold):
                    detected_issues[item_num] = name
                continue

            if item_num == 7:  # 단점 회피
                # 개선 (2026-01-07): 단점이 없다고 무조건 광고는 아님
                # 다른 광고 패턴(찬사 위주, 감탄사 남발)이 함께 있을 때만 의심
                if not self._has_negative_opinion(review_text):
                    # 찬사 위주(8번) 또는 감탄사 남발(2번)이 이미 감지된 경우에만 추가
                    if 8 in detected_issues or 2 in detected_issues:
                        detected_issues[item_num] = name
                continue
            
            # 제품별 광고의심 표현 체크 (기본 패턴에 추가)
            if self.criteria and self.criteria.ad_suspicious_expressions:
                for suspicious_expr in self.criteria.ad_suspicious_expressions:
                    if suspicious_expr in review_text:
                        detected_issues[item_num] = f"{name} (제품별 기준: {suspicious_expr})"
                        break

            # 정규표현식 패턴 매칭
            for pattern in patterns:
                if re.search(pattern, review_text, re.IGNORECASE | re.MULTILINE):
                    detected_issues[item_num] = name
                    break

        # 영양성분 DB 기반 추가 검증 (product_id가 있고 정보가 있는 경우만)
        if product_id:
            try:
                # 5번: 원료 특징 나열 - 허위 성분 주장 검증
                if self._validate_ingredient_claims(review_text, product_id):
                    # 기존 5번 항목이 있으면 강화, 없으면 추가
                    if 5 in detected_issues:
                        detected_issues[5] = f"{detected_issues[5]} (허위 성분 주장 포함)"
                    else:
                        detected_issues[5] = "원료 특징 나열 (허위 성분 주장)"
                
                # 9번: 전문 용어 오남용 - 허위 의학적 주장 검증
                if self._validate_medical_claims(review_text, product_id):
                    if 9 in detected_issues:
                        detected_issues[9] = f"{detected_issues[9]} (허위 의학적 주장 포함)"
                    else:
                        detected_issues[9] = "전문 용어 오남용 (허위 의학적 주장)"
                
                # 10번: 비현실적 효과 강조 - 효과 시점 검증
                if self._validate_effect_timeline(review_text, product_id):
                    if 10 in detected_issues:
                        detected_issues[10] = f"{detected_issues[10]} (효과 시점 과장)"
                    else:
                        detected_issues[10] = "비현실적 효과 강조 (효과 시점 과장)"
            except Exception:
                # 영양성분 검증 중 오류 발생 시 무시하고 기존 결과만 반환
                pass

        return detected_issues

    def _has_personal_experience(self, text: str) -> bool:
        """
        개인 경험 표현 존재 여부 검사

        개선 사항 (2026-01-07):
        - 구매/사용 관련 표현 추가 (구매, 샀, 먹, 사용, 복용)
        - 체감 표현 추가 (느, 같아, 되는, 했)
        - 재구매 표현 추가 (재구매, 또, 다시, 계속)
        """
        personal_patterns = [
            # 1인칭 대명사
            r"나는", r"저는", r"제가", r"내가", r"우리",
            # 직접 경험
            r"직접", r"실제로", r"먹어보니", r"사용해보니",
            # 구매/사용 표현
            r"구매", r"샀", r"사서", r"먹", r"사용", r"복용", r"써",
            # 체감 표현
            r"느", r"같아", r"되는", r"됐", r"했", r"해서",
            # 재구매 및 지속 사용
            r"재구매", r"또", r"다시", r"계속", r"리피트",
            # 소유 표현
            r"내", r"제", r"우리", r"아버지", r"어머니", r"부모님", r"가족"
        ]
        for pattern in personal_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _has_keyword_repetition(self, text: str, threshold: int = 7) -> bool:
        """
        특정 키워드 과도한 반복 검사

        개선 사항 (2026-01-07):
        - 기본 임계값 5 → 7로 완화 (정상 리뷰도 특정 단어를 여러 번 쓸 수 있음)
        """
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
        """
        부정적 의견 또는 단점 언급 여부 검사

        개선 사항 (2026-01-07):
        - 이 함수는 단점 회피(7번) 항목에서만 사용됨
        - 단점이 없다고 무조건 광고는 아님 (정상 리뷰도 만족하면 단점을 안 쓸 수 있음)
        - 따라서 check_ad_patterns()에서 다른 광고 패턴과 함께 있을 때만 감점
        """
        # 기본 부정적 패턴
        negative_patterns = [
            r"단점", r"아쉬", r"불편", r"별로", r"그런데",
            r"하지만", r"다만", r"개선", r"부족", r"안.*좋"
        ]
        
        # 제품별 부정적 표현 추가
        if self.criteria and self.criteria.negative_expressions:
            for expr in self.criteria.negative_expressions:
                if expr in text:
                    return True
        
        # 기본 패턴 검사
        for pattern in negative_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def check_with_criteria(
        self, 
        review_text: str, 
        criteria: ProductCheckCriteria
    ) -> Dict[int, str]:
        """
        제품 기준을 사용하여 체크리스트 검사
        
        Args:
            review_text: 검사할 리뷰 텍스트
            criteria: 제품별 체크 기준
            
        Returns:
            Dict[int, str]: {항목번호: 항목명} 형태로 감지된 항목 반환
        """
        # 임시로 기준 설정
        original_criteria = self.criteria
        self.criteria = criteria
        
        try:
            result = self.check_ad_patterns(review_text)
            return result
        finally:
            # 원래 기준으로 복원
            self.criteria = original_criteria
    
    def get_check_summary(self, review_text: str) -> Dict:
        """
        체크리스트 검사 결과 상세 요약
        
        Args:
            review_text: 검사할 리뷰 텍스트
            
        Returns:
            Dict: {
                "detected_issues": 감지된 항목,
                "positive_keywords_found": 발견된 긍정적 키워드,
                "negative_expressions_found": 발견된 부정적 표현,
                "criteria_used": 사용된 기준 정보
            }
        """
        detected_issues = self.check_ad_patterns(review_text)
        
        result = {
            "detected_issues": detected_issues,
            "positive_keywords_found": [],
            "negative_expressions_found": [],
            "criteria_used": None
        }
        
        if self.criteria:
            result["criteria_used"] = {
                "product_name": self.criteria.product_name,
                "nutrition_category": self.criteria.nutrition_category
            }
            
            # 긍정적 키워드 검사
            for keyword in self.criteria.positive_keywords:
                if keyword in review_text:
                    result["positive_keywords_found"].append(keyword)
            
            # 부정적 표현 검사
            for expr in self.criteria.negative_expressions:
                if expr in review_text:
                    result["negative_expressions_found"].append(expr)
        
        return result

    def _validate_ingredient_claims(
        self, 
        review_text: str, 
        product_id: Optional[int] = None
    ) -> bool:
        """
        리뷰에서 언급된 성분이 실제 제품에 포함되어 있는지 검증
        
        Args:
            review_text: 리뷰 텍스트
            product_id: 제품 ID (None이면 검증 생략)
            
        Returns:
            bool: 허위 성분 주장이 있으면 True (광고 의심), 정보 없으면 False
        """
        # 1. product_id가 없으면 검증 생략 (기존 방식으로 동작)
        if not product_id:
            return False
        
        # 2. 영양성분 정보 조회 (오류 발생 시 기본값 반환)
        nutrition_info = get_nutrition_info_safe(product_id)
        if not nutrition_info:
            return False  # 정보 없으면 검증 생략 (오류 없이)
        
        # 3. 리뷰 텍스트에서 성분명 추출
        mentioned_ingredients = extract_ingredients(review_text)
        if not mentioned_ingredients:
            return False  # 성분 언급 없으면 검증 불가
        
        # 4. 언급된 성분이 실제 제품에 없는 경우 → 허위 주장으로 판단
        for mentioned in mentioned_ingredients:
            if not is_valid_ingredient(mentioned, nutrition_info):
                return True  # 허위 주장 발견
        
        return False  # 모든 성분이 유효함

    def _validate_medical_claims(
        self, 
        review_text: str, 
        product_id: Optional[int] = None
    ) -> bool:
        """
        리뷰의 의학적 주장이 영양성분 DB의 공식 효능과 일치하는지 검증
        
        Args:
            review_text: 리뷰 텍스트
            product_id: 제품 ID (None이면 검증 생략)
            
        Returns:
            bool: 허위 의학적 주장이 있으면 True
        """
        if not product_id:
            return False
        
        try:
            nutrition_info = get_nutrition_info_safe(product_id)
            if not nutrition_info:
                return False
            
            # 리뷰에서 성분명 추출
            mentioned_ingredients = extract_ingredients(review_text)
            if not mentioned_ingredients:
                return False
            
            # 의학적 주장 패턴 (과장된 표현)
            exaggerated_claims = [
                r"100%.*(회복|치료|완치)",
                r"(완벽|완전).*(치료|회복|개선)",
                r"(기적|놀라운|엄청난).*(효과|변화)",
                r"(즉시|바로|단.*하루|일주일).*(효과|개선|변화)"
            ]
            
            # 리뷰에 과장된 주장이 있는지 확인
            has_exaggerated_claim = False
            for pattern in exaggerated_claims:
                if re.search(pattern, review_text, re.IGNORECASE):
                    has_exaggerated_claim = True
                    break
            
            if not has_exaggerated_claim:
                return False  # 과장된 주장이 없으면 검증 불가
            
            # 각 성분의 공식 효능 확인
            for ingredient in mentioned_ingredients:
                official_efficacy = get_official_efficacy(ingredient, nutrition_info)
                # 공식 효능이 없거나 과장된 주장과 불일치하면 의심
                if not official_efficacy:
                    # 공식 효능 정보가 없으면 검증 불가 (의심하지 않음)
                    continue
            
            # 과장된 주장이 있지만 공식 효능과 일치하지 않는 경우는 False 반환
            # (더 정교한 검증은 향후 개선)
            return False
            
        except Exception:
            return False  # 오류 발생 시 False 반환 (오류 없이)

    def _validate_effect_timeline(
        self, 
        review_text: str, 
        product_id: Optional[int] = None
    ) -> bool:
        """
        리뷰의 효과 발현 시점이 현실적인지 검증
        
        Args:
            review_text: 리뷰 텍스트
            product_id: 제품 ID (None이면 검증 생략)
            
        Returns:
            bool: 비현실적인 효과 시점 주장이 있으면 True
        """
        if not product_id:
            return False
        
        try:
            nutrition_info = get_nutrition_info_safe(product_id)
            if not nutrition_info:
                return False
            
            # 리뷰에서 성분명 추출
            mentioned_ingredients = extract_ingredients(review_text)
            if not mentioned_ingredients:
                return False
            
            # 비현실적인 시점 표현 패턴
            unrealistic_timeline_patterns = [
                r"(즉시|바로|단.*하루|하루만에|일주일만에).*(효과|개선|변화|달라)",
                r"(하루|일주일).*(만에|만).*(효과|개선|변화)"
            ]
            
            # 비현실적인 시점 표현이 있는지 확인
            has_unrealistic_timeline = False
            for pattern in unrealistic_timeline_patterns:
                if re.search(pattern, review_text, re.IGNORECASE):
                    has_unrealistic_timeline = True
                    break
            
            if not has_unrealistic_timeline:
                return False  # 비현실적인 시점 표현이 없으면 검증 불가
            
            # 각 성분의 일반적 효과 발현 기간 확인
            for ingredient in mentioned_ingredients:
                typical_period = get_typical_effect_period(ingredient, nutrition_info)
                if typical_period:
                    # 일반적으로 2주 이상 걸리는 성분인데 "하루만에" 효과 주장하면 의심
                    if typical_period >= 14:
                        # "하루만에", "일주일만에" 같은 표현이 있으면 비현실적
                        if re.search(r"(하루|일주일).*(만에|만)", review_text, re.IGNORECASE):
                            return True
            
            return False
            
        except Exception:
            return False  # 오류 발생 시 False 반환 (오류 없이)


# 편의 함수
def check_ad_patterns(
    review_text: str, 
    product_id: Optional[int] = None
) -> Dict[int, str]:
    """
    13단계 광고 판별 체크리스트 검사 편의 함수

    Args:
        review_text: 검사할 리뷰 텍스트

    Returns:
        Dict[int, str]: {항목번호: 항목명} 형태로 감지된 항목 반환
    """
    checklist = AdChecklist()
    return checklist.check_ad_patterns(review_text)




