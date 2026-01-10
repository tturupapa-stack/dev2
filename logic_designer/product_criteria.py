"""
제품별 체크 기준 설정 모듈
각 제품에 맞는 체크리스트 기준을 정의합니다.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ProductCheckCriteria:
    """
    제품별 체크 기준 클래스
    동일한 기준으로 제품을 체크하기 위한 설정값들을 담습니다.
    """
    
    # 필수 필드
    product_name: str  # 제품명
    nutrition_category: str  # 영양구분 (예: "비타민", "미네랄", "프로바이오틱스" 등)
    
    # 키워드 및 표현 설정
    positive_keywords: List[str] = field(default_factory=list)  # 긍정적 키워드
    negative_expressions: List[str] = field(default_factory=list)  # 부정적 표현
    ad_suspicious_expressions: List[str] = field(default_factory=list)  # 광고의심 표현
    
    # 추가 설정 (선택적)
    product_specific_patterns: Dict[str, List[str]] = field(default_factory=dict)  # 제품별 특수 패턴
    keyword_repetition_threshold: int = 5  # 키워드 반복 임계값
    min_review_length: int = 10  # 최소 리뷰 길이
    
    # 메타데이터
    description: Optional[str] = None  # 기준 설명
    created_at: Optional[str] = None  # 생성 시간
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not self.product_name:
            raise ValueError("제품명은 필수입니다.")
        if not self.nutrition_category:
            raise ValueError("영양구분은 필수입니다.")
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "product_name": self.product_name,
            "nutrition_category": self.nutrition_category,
            "positive_keywords": self.positive_keywords,
            "negative_expressions": self.negative_expressions,
            "ad_suspicious_expressions": self.ad_suspicious_expressions,
            "product_specific_patterns": self.product_specific_patterns,
            "keyword_repetition_threshold": self.keyword_repetition_threshold,
            "min_review_length": self.min_review_length,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ProductCheckCriteria":
        """딕셔너리에서 생성"""
        return cls(
            product_name=data.get("product_name", ""),
            nutrition_category=data.get("nutrition_category", ""),
            positive_keywords=data.get("positive_keywords", []),
            negative_expressions=data.get("negative_expressions", []),
            ad_suspicious_expressions=data.get("ad_suspicious_expressions", []),
            product_specific_patterns=data.get("product_specific_patterns", {}),
            keyword_repetition_threshold=data.get("keyword_repetition_threshold", 5),
            min_review_length=data.get("min_review_length", 10),
            description=data.get("description"),
            created_at=data.get("created_at")
        )
    
    def add_positive_keyword(self, keyword: str):
        """긍정적 키워드 추가"""
        if keyword and keyword not in self.positive_keywords:
            self.positive_keywords.append(keyword)
    
    def add_negative_expression(self, expression: str):
        """부정적 표현 추가"""
        if expression and expression not in self.negative_expressions:
            self.negative_expressions.append(expression)
    
    def add_ad_suspicious_expression(self, expression: str):
        """광고의심 표현 추가"""
        if expression and expression not in self.ad_suspicious_expressions:
            self.ad_suspicious_expressions.append(expression)
    
    def add_specific_pattern(self, pattern_name: str, patterns: List[str]):
        """제품별 특수 패턴 추가"""
        self.product_specific_patterns[pattern_name] = patterns


# 사전 정의된 제품 기준 예시
class DefaultProductCriteria:
    """기본 제품 기준 팩토리"""
    
    @staticmethod
    def create_vitamin_c_criteria() -> ProductCheckCriteria:
        """비타민C 제품 기준"""
        return ProductCheckCriteria(
            product_name="비타민C",
            nutrition_category="비타민",
            positive_keywords=[
                "면역력", "감기예방", "항산화", "콜라겐", "피부건강",
                "에너지", "활력", "회복"
            ],
            negative_expressions=[
                "알레르기", "위장불편", "메스꺼움", "설사", "복통",
                "부작용", "불편함", "아쉬움"
            ],
            ad_suspicious_expressions=[
                "100% 효과", "즉시 개선", "완벽한", "기적",
                "단 하루만에", "일주일 만에 완전히"
            ],
            description="비타민C 제품 체크 기준"
        )
    
    @staticmethod
    def create_probiotics_criteria() -> ProductCheckCriteria:
        """프로바이오틱스 제품 기준"""
        return ProductCheckCriteria(
            product_name="프로바이오틱스",
            nutrition_category="프로바이오틱스",
            positive_keywords=[
                "장건강", "소화", "변비개선", "면역력", "균형",
                "활력", "편안함"
            ],
            negative_expressions=[
                "복통", "가스", "팽만감", "설사", "불편",
                "효과없음", "변화없음"
            ],
            ad_suspicious_expressions=[
                "완벽한 장건강", "즉시 효과", "100% 개선",
                "기적의 변화"
            ],
            description="프로바이오틱스 제품 체크 기준"
        )
    
    @staticmethod
    def create_omega3_criteria() -> ProductCheckCriteria:
        """오메가3 제품 기준"""
        return ProductCheckCriteria(
            product_name="오메가3",
            nutrition_category="지방산",
            positive_keywords=[
                "뇌건강", "심혈관", "콜레스테롤", "관절", "항염",
                "집중력", "기억력"
            ],
            negative_expressions=[
                "비린내", "트림", "소화불량", "불편", "아쉬움"
            ],
            ad_suspicious_expressions=[
                "완벽한 뇌건강", "즉시 효과", "100% 개선"
            ],
            description="오메가3 제품 체크 기준"
        )
    
    @staticmethod
    def create_generic_criteria(
        product_name: str,
        nutrition_category: str
    ) -> ProductCheckCriteria:
        """일반 제품 기준 생성"""
        return ProductCheckCriteria(
            product_name=product_name,
            nutrition_category=nutrition_category,
            positive_keywords=[],
            negative_expressions=[],
            ad_suspicious_expressions=[],
            description=f"{product_name} 제품 체크 기준"
        )




