"""
건기식 리뷰 팩트체크 시스템 - 목업 데이터
루테인 제품 5종 + 리뷰 100개 + 분석 결과
"""

from datetime import datetime, timedelta
import random


# 루테인 제품 5종
PRODUCTS = [
    {
        "id": "p001",
        "name": "Lutein 20mg",
        "brand": "NOW Foods",
        "price": 14.99,
        "serving_size": "1 Softgel",
        "servings_per_container": 120,
        "ingredients": {
            "lutein": "20mg",
            "zeaxanthin": "4mg",
            "other": "Safflower Oil, Gelatin, Glycerin, Water, Natural Caramel Color"
        },
        "product_url": "https://www.nowfoods.com/products/supplements/lutein-20-mg-softgels"
    },
    {
        "id": "p002",
        "name": "Lutein with Lutemax 2020",
        "brand": "Doctor's Best",
        "price": 18.49,
        "serving_size": "1 Softgel",
        "servings_per_container": 60,
        "ingredients": {
            "lutein": "20mg",
            "zeaxanthin": "4mg",
            "meso_zeaxanthin": "4mg",
            "other": "Extra Virgin Olive Oil, Softgel (bovine gelatin, glycerin, purified water)"
        },
        "product_url": "https://www.doctorsbest.com/products/lutein-with-lutemax-2020"
    },
    {
        "id": "p003",
        "name": "Lutein 20mg",
        "brand": "Jarrow Formulas",
        "price": 16.99,
        "serving_size": "1 Softgel",
        "servings_per_container": 60,
        "ingredients": {
            "lutein": "20mg",
            "zeaxanthin": "1mg",
            "other": "Medium Chain Triglycerides, Soy Lecithin, Beeswax, Softgel (gelatin, glycerin, water)"
        },
        "product_url": "https://www.jarrow.com/products/lutein"
    },
    {
        "id": "p004",
        "name": "MacuGuard Ocular Support with Saffron",
        "brand": "Life Extension",
        "price": 22.50,
        "serving_size": "1 Softgel",
        "servings_per_container": 60,
        "ingredients": {
            "lutein": "20mg",
            "zeaxanthin": "4.5mg",
            "meso_zeaxanthin": "10mg",
            "saffron": "20mg",
            "other": "Sunflower Lecithin, Gelatin, Glycerin, Purified Water, Beeswax, Annatto Color"
        },
        "product_url": "https://www.lifeextension.com/vitamins-supplements/item02401/macuguard-ocular-support"
    },
    {
        "id": "p005",
        "name": "Lutein with Zeaxanthin 20mg",
        "brand": "California Gold Nutrition",
        "price": 12.00,
        "serving_size": "1 Softgel",
        "servings_per_container": 60,
        "ingredients": {
            "lutein": "20mg",
            "zeaxanthin": "1mg",
            "other": "Safflower Oil, Softgel Capsule (bovine gelatin, vegetable glycerin, purified water)"
        },
        "product_url": "https://www.iherb.com/pr/california-gold-nutrition-lutein-with-zeaxanthin"
    }
]


# 리뷰 생성 헬퍼 함수
def generate_reviews_for_product(product_id, product_name, count=20):
    """각 제품당 20개의 다양한 리뷰 생성"""

    # 리뷰 템플릿 (긍정/부정/중립, 광고성/진성)
    review_templates = {
        "positive_genuine": [
            "눈 건강을 위해 {}을 구매했습니다. 3개월 정도 복용 중인데 눈의 피로감이 확실히 줄어든 것 같아요. 장시간 컴퓨터 작업을 해도 예전보다 덜 뻑뻑합니다.",
            "꾸준히 먹고 있는데 효과가 있는 것 같습니다. 시력이 좋아진 건지는 모르겠지만 눈이 덜 피곤해요. 가격도 합리적이고 계속 구매할 예정입니다.",
            "의사 선생님 권유로 복용 시작했어요. 한 달 정도 먹었는데 눈 건조함이 개선되었습니다. 부작용은 없고 먹기 편해서 좋아요.",
            "루테인 제품 중에서 가성비가 좋은 것 같아요. 매일 아침 하나씩 먹고 있는데 눈 건강 유지에 도움이 되는 것 같습니다.",
            "예전보다 눈이 맑아진 느낌입니다. 황반변성 예방 목적으로 먹고 있는데 만족스럽습니다. 부모님께도 추천했어요."
        ],
        "positive_ad_like": [
            "정말 최고의 제품입니다! {}는 제 인생 영양제예요!! 모든 분들께 강력 추천합니다!!!",
            "대박 제품이에요!! 먹은 지 일주일만에 시력이 2.0으로 좋아졌어요! 믿기지 않으시겠지만 정말입니다!",
            "이 제품 안 먹으면 후회합니다! 100% 효과 보장! 전 세계 1위 브랜드! 지금 바로 구매하세요!",
            "와... 진짜 효과 대박이에요. 눈이 완전 새 눈이 된 느낌. 주변 사람들한테 다 추천했어요. 여러분도 꼭 사세요!"
        ],
        "neutral": [
            "{}을 구매해서 먹고 있습니다. 아직 효과는 잘 모르겠고 조금 더 먹어봐야 할 것 같아요.",
            "배송은 빨랐어요. 효과는 장기 복용해봐야 알 것 같습니다. 캡슐 크기는 적당합니다.",
            "한 달 정도 먹었는데 특별한 변화는 못 느끼겠어요. 그래도 눈 건강을 위해 계속 먹을 예정입니다.",
            "가격 대비 괜찮은 것 같아요. 효과는 개인차가 있을 듯합니다. 저는 아직 잘 모르겠어요."
        ],
        "negative": [
            "{} 먹고 속이 안 좋아졌어요. 저한테는 안 맞는 것 같습니다. 먹다가 중단했습니다.",
            "효과를 전혀 못 느끼겠어요. 3개월 먹었는데 변화가 없습니다. 돈 아깝네요.",
            "캡슐이 너무 커서 삼키기 힘들어요. 냄새도 좀 나고... 다른 제품 찾아볼 생각입니다.",
            "가격만 비싸고 효과는 없는 것 같아요. 차라리 눈 운동을 하는 게 나을 듯합니다."
        ]
    }

    reviewers = [
        "김철수", "이영희", "박민수", "정수연", "최현우",
        "강지혜", "윤서준", "임하은", "조준호", "한예진",
        "황민재", "서아린", "권도현", "송유나", "문지훈",
        "장서현", "백승기", "신다은", "홍준영", "노예슬"
    ]

    reviews = []
    base_date = datetime.now() - timedelta(days=365)

    for i in range(count):
        # 리뷰 타입 결정 (60% 긍정, 20% 중립, 15% 부정, 5% 광고성)
        rand = random.random()
        if rand < 0.60:
            review_type = "positive_genuine"
            rating = random.choice([4, 5])
            reorder = random.choice([True, True, False])
            one_month_use = random.choice([True, True, True, False])
        elif rand < 0.80:
            review_type = "neutral"
            rating = random.choice([3, 4])
            reorder = random.choice([True, False])
            one_month_use = random.choice([True, False])
        elif rand < 0.95:
            review_type = "negative"
            rating = random.choice([1, 2, 3])
            reorder = False
            one_month_use = random.choice([True, False])
        else:
            review_type = "positive_ad_like"
            rating = 5
            reorder = True
            one_month_use = False  # 광고성은 짧은 사용 기간

        template = random.choice(review_templates[review_type])
        review_text = template.format(product_name)

        review = {
            "product_id": product_id,
            "text": review_text,
            "rating": rating,
            "date": (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "reorder": reorder,
            "one_month_use": one_month_use,
            "reviewer": random.choice(reviewers),
            "verified": random.choice([True, True, True, False])  # 75% 인증 구매
        }

        reviews.append(review)

    return reviews


# 전체 리뷰 생성 (100개)
ALL_REVIEWS = []
for product in PRODUCTS:
    product_reviews = generate_reviews_for_product(product["id"], product["name"], 20)
    ALL_REVIEWS.extend(product_reviews)


# 체크리스트 결과 생성
def generate_checklist_results(reviews):
    """8단계 체크리스트 결과 생성"""
    total_reviews = len(reviews)
    verified_count = sum(1 for r in reviews if r["verified"])
    reorder_count = sum(1 for r in reviews if r["reorder"])
    one_month_count = sum(1 for r in reviews if r["one_month_use"])
    high_rating_count = sum(1 for r in reviews if r["rating"] >= 4)

    # 광고성 리뷰 탐지 (매우 긍정적이면서 짧은 사용기간)
    ad_suspected = sum(1 for r in reviews if r["rating"] == 5 and not r["one_month_use"] and len(r["text"]) < 100)

    return {
        "1_verified_purchase": {
            "passed": verified_count / total_reviews >= 0.7,
            "rate": verified_count / total_reviews,
            "description": f"인증 구매 비율: {verified_count}/{total_reviews}"
        },
        "2_reorder_rate": {
            "passed": reorder_count / total_reviews >= 0.3,
            "rate": reorder_count / total_reviews,
            "description": f"재구매율: {reorder_count}/{total_reviews}"
        },
        "3_long_term_use": {
            "passed": one_month_count / total_reviews >= 0.5,
            "rate": one_month_count / total_reviews,
            "description": f"한 달 이상 사용: {one_month_count}/{total_reviews}"
        },
        "4_rating_distribution": {
            "passed": 0.3 <= (high_rating_count / total_reviews) <= 0.9,
            "rate": high_rating_count / total_reviews,
            "description": f"고평점(4-5점) 비율: {high_rating_count}/{total_reviews}"
        },
        "5_review_length": {
            "passed": sum(len(r["text"]) for r in reviews) / total_reviews >= 50,
            "rate": sum(len(r["text"]) for r in reviews) / total_reviews / 100,
            "description": "평균 리뷰 길이 적절"
        },
        "6_time_distribution": {
            "passed": True,
            "rate": 0.85,
            "description": "리뷰 작성 시간 분포 자연스러움"
        },
        "7_ad_detection": {
            "passed": ad_suspected / total_reviews < 0.1,
            "rate": 1 - (ad_suspected / total_reviews),
            "description": f"광고 의심 리뷰: {ad_suspected}/{total_reviews}"
        },
        "8_reviewer_diversity": {
            "passed": len(set(r["reviewer"] for r in reviews)) >= total_reviews * 0.8,
            "rate": len(set(r["reviewer"] for r in reviews)) / total_reviews,
            "description": "리뷰어 다양성 양호"
        }
    }


# AI 약사 분석 결과 생성
def generate_ai_analysis(product, checklist):
    """AI 약사의 분석 결과 생성"""
    trust_score = sum(c["rate"] for c in checklist.values()) / len(checklist) * 100

    if trust_score >= 70:
        trust_level = "high"
        summary = f"{product['brand']} {product['name']}는 신뢰도 높은 제품입니다. 리뷰 분석 결과 인증 구매 비율이 높고, 재구매율도 양호하며, 광고성 리뷰 비율이 낮습니다."
    elif trust_score >= 50:
        trust_level = "medium"
        summary = f"{product['brand']} {product['name']}는 중간 수준의 신뢰도를 보입니다. 일부 지표에서 개선이 필요하지만 전반적으로 무난한 제품입니다."
    else:
        trust_level = "low"
        summary = f"{product['brand']} {product['name']}는 신뢰도가 낮은 편입니다. 광고성 리뷰 비율이 높거나 검증된 구매 비율이 낮습니다."

    return {
        "trust_score": round(trust_score, 1),
        "trust_level": trust_level,
        "summary": summary,
        "efficacy": f"루테인 {product['ingredients']['lutein']} 함유. 눈 건강 유지 및 황반색소 밀도 개선에 도움을 줄 수 있습니다. 제아잔틴 {product['ingredients'].get('zeaxanthin', '0mg')} 추가 함유로 시너지 효과 기대.",
        "side_effects": "일반적으로 안전하나, 드물게 소화불량이나 알레르기 반응이 나타날 수 있습니다. 과량 섭취 시 피부가 노랗게 변할 수 있으니 권장량을 준수하세요.",
        "recommendations": "하루 1회, 식사와 함께 복용하면 흡수율이 높아집니다. 최소 3개월 이상 꾸준히 복용해야 효과를 체감할 수 있습니다.",
        "warnings": "임신부, 수유부는 복용 전 의사와 상담하세요. 다른 눈 건강 보조제와 중복 복용 시 과량 섭취에 주의하세요."
    }


# 전체 분석 결과 생성
ANALYSIS_RESULTS = {}
for product in PRODUCTS:
    product_reviews = [r for r in ALL_REVIEWS if r["product_id"] == product["id"]]
    checklist = generate_checklist_results(product_reviews)
    ai_analysis = generate_ai_analysis(product, checklist)

    ANALYSIS_RESULTS[product["id"]] = {
        "product": product,
        "reviews": product_reviews,
        "checklist_results": checklist,
        "ai_result": ai_analysis
    }


# 데이터 접근 함수
def get_all_products():
    """모든 제품 정보 반환"""
    return PRODUCTS


def get_product_by_id(product_id):
    """특정 제품 정보 반환"""
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def get_reviews_by_product(product_id):
    """특정 제품의 리뷰 반환"""
    return [r for r in ALL_REVIEWS if r["product_id"] == product_id]


def get_analysis_result(product_id):
    """특정 제품의 분석 결과 반환"""
    return ANALYSIS_RESULTS.get(product_id)


def get_all_analysis_results():
    """모든 제품의 분석 결과 반환"""
    return ANALYSIS_RESULTS


def search_products(query):
    """제품 검색 (이름, 브랜드)"""
    query = query.lower()
    return [p for p in PRODUCTS if query in p["name"].lower() or query in p["brand"].lower()]


if __name__ == "__main__":
    # 테스트 출력
    print("=" * 60)
    print("루테인 제품 목업 데이터 생성 완료")
    print("=" * 60)
    print(f"\n총 제품 수: {len(PRODUCTS)}")
    print(f"총 리뷰 수: {len(ALL_REVIEWS)}")
    print(f"\n제품 목록:")
    for p in PRODUCTS:
        analysis = ANALYSIS_RESULTS[p["id"]]
        print(f"  - {p['brand']} {p['name']}")
        print(f"    신뢰도: {analysis['ai_result']['trust_score']:.1f} ({analysis['ai_result']['trust_level'].upper()})")
        print(f"    리뷰 수: {len(analysis['reviews'])}")
