"""
제품별 체크 기준 사용 예시
"""

from .product_criteria import ProductCheckCriteria, DefaultProductCriteria
from .checklist import AdChecklist


def example_basic_usage():
    """기본 사용 예시"""
    print("=== 기본 사용 예시 ===\n")
    
    # 1. 제품 기준 생성
    criteria = ProductCheckCriteria(
        product_name="비타민C 1000mg",
        nutrition_category="비타민",
        positive_keywords=["면역력", "감기예방", "항산화", "피부건강"],
        negative_expressions=["알레르기", "위장불편", "메스꺼움"],
        ad_suspicious_expressions=["100% 효과", "즉시 개선", "완벽한"]
    )
    
    # 2. 체크리스트에 기준 적용
    checklist = AdChecklist(criteria=criteria)
    
    # 3. 리뷰 검사
    review_text = """
    이 비타민C는 정말 좋아요! 면역력이 올라가서 감기예방에 도움이 됩니다.
    항산화 효과도 있고 피부건강에도 좋아요. 100% 효과를 보장합니다!
    """
    
    detected = checklist.check_ad_patterns(review_text)
    print(f"감지된 항목: {detected}")
    
    # 4. 상세 요약
    summary = checklist.get_check_summary(review_text)
    print(f"\n긍정적 키워드 발견: {summary['positive_keywords_found']}")
    print(f"부정적 표현 발견: {summary['negative_expressions_found']}")
    print(f"사용된 기준: {summary['criteria_used']}")


def example_predefined_criteria():
    """사전 정의된 기준 사용 예시"""
    print("\n=== 사전 정의된 기준 사용 예시 ===\n")
    
    # 비타민C 기준 사용
    criteria = DefaultProductCriteria.create_vitamin_c_criteria()
    checklist = AdChecklist(criteria=criteria)
    
    review_text = """
    비타민C를 먹고 나서 면역력이 좋아진 것 같아요.
    감기예방에도 도움이 되고 항산화 효과도 있어서 만족합니다.
    다만 위장불편함이 조금 있어서 아쉽네요.
    """
    
    summary = checklist.get_check_summary(review_text)
    print(f"제품명: {criteria.product_name}")
    print(f"영양구분: {criteria.nutrition_category}")
    print(f"긍정적 키워드 발견: {summary['positive_keywords_found']}")
    print(f"부정적 표현 발견: {summary['negative_expressions_found']}")
    print(f"감지된 광고 항목: {summary['detected_issues']}")


def example_dynamic_criteria():
    """동적 기준 생성 예시"""
    print("\n=== 동적 기준 생성 예시 ===\n")
    
    # 일반 기준으로 시작
    criteria = DefaultProductCriteria.create_generic_criteria(
        product_name="오메가3",
        nutrition_category="지방산"
    )
    
    # 키워드 추가
    criteria.add_positive_keyword("뇌건강")
    criteria.add_positive_keyword("심혈관")
    criteria.add_negative_expression("비린내")
    criteria.add_ad_suspicious_expression("완벽한 뇌건강")
    
    print(f"제품명: {criteria.product_name}")
    print(f"영양구분: {criteria.nutrition_category}")
    print(f"긍정적 키워드: {criteria.positive_keywords}")
    print(f"부정적 표현: {criteria.negative_expressions}")
    print(f"광고의심 표현: {criteria.ad_suspicious_expressions}")


def example_multiple_products():
    """여러 제품 비교 예시"""
    print("\n=== 여러 제품 비교 예시 ===\n")
    
    reviews = [
        {
            "product": "비타민C",
            "text": "면역력 향상에 좋아요! 감기예방 효과가 있어서 만족합니다."
        },
        {
            "product": "프로바이오틱스",
            "text": "장건강에 도움이 되고 소화가 잘 됩니다. 변비개선에도 효과가 있어요."
        },
        {
            "product": "오메가3",
            "text": "뇌건강과 심혈관 건강에 좋습니다. 다만 비린내가 조금 있어요."
        }
    ]
    
    criteria_map = {
        "비타민C": DefaultProductCriteria.create_vitamin_c_criteria(),
        "프로바이오틱스": DefaultProductCriteria.create_probiotics_criteria(),
        "오메가3": DefaultProductCriteria.create_omega3_criteria()
    }
    
    for review in reviews:
        product_name = review["product"]
        criteria = criteria_map[product_name]
        checklist = AdChecklist(criteria=criteria)
        
        summary = checklist.get_check_summary(review["text"])
        
        print(f"\n[{product_name}]")
        print(f"  긍정적 키워드: {summary['positive_keywords_found']}")
        print(f"  부정적 표현: {summary['negative_expressions_found']}")
        print(f"  감지된 항목 수: {len(summary['detected_issues'])}")


if __name__ == "__main__":
    example_basic_usage()
    example_predefined_criteria()
    example_dynamic_criteria()
    example_multiple_products()

