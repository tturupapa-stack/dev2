"""
목업 데이터 생성 모듈
iHerb 루테인 제품 5종 + 제품당 리뷰 20개 (총 100개)
"""

from datetime import datetime, timedelta
import random

# =====================================================
# iHerb 루테인 제품 5종 목업 데이터
# =====================================================
MOCK_PRODUCTS = [
    {
        "source": "iherb",
        "source_product_id": "NOW-03212",
        "url": "https://kr.iherb.com/pr/now-foods-lutein-10-mg-120-softgels/3212",
        "title": "Lutein, 10 mg, 120 Softgels",
        "brand": "Now Foods",
        "category": "루테인",
        "price": 15.99,
        "currency": "USD",
        "rating_avg": 4.5,
        "rating_count": 2847
    },
    {
        "source": "iherb",
        "source_product_id": "JAR-00050",
        "url": "https://kr.iherb.com/pr/jarrow-formulas-lutein-20-mg-60-softgels/50",
        "title": "Lutein, 20 mg, 60 Softgels",
        "brand": "Jarrow Formulas",
        "category": "루테인",
        "price": 16.47,
        "currency": "USD",
        "rating_avg": 4.7,
        "rating_count": 1523
    },
    {
        "source": "iherb",
        "source_product_id": "DRB-00289",
        "url": "https://kr.iherb.com/pr/doctor-s-best-lutein-with-optilut-10-mg-120-veggie-caps/289",
        "title": "Lutein with OptiLut, 10 mg, 120 Veggie Caps",
        "brand": "Doctor's Best",
        "category": "루테인",
        "price": 14.24,
        "currency": "USD",
        "rating_avg": 4.6,
        "rating_count": 987
    },
    {
        "source": "iherb",
        "source_product_id": "SLF-00431",
        "url": "https://kr.iherb.com/pr/solgar-lutein-20-mg-60-softgels/431",
        "title": "Lutein, 20 mg, 60 Softgels",
        "brand": "Solgar",
        "category": "루테인",
        "price": 24.99,
        "currency": "USD",
        "rating_avg": 4.8,
        "rating_count": 1234
    },
    {
        "source": "iherb",
        "source_product_id": "LFS-01842",
        "url": "https://kr.iherb.com/pr/life-extension-macuguard-ocular-support-with-saffron-60-softgels/1842",
        "title": "MacuGuard Ocular Support with Saffron, 60 Softgels",
        "brand": "Life Extension",
        "category": "루테인",
        "price": 22.50,
        "currency": "USD",
        "rating_avg": 4.7,
        "rating_count": 892
    }
]


# =====================================================
# 리뷰 템플릿 (정상 리뷰 + 광고성 리뷰 혼합)
# =====================================================

# 정상 리뷰 템플릿 (60%)
NORMAL_REVIEW_TEMPLATES = [
    {
        "title": "눈 건강에 도움이 되는 것 같아요",
        "body": "한달 정도 먹어보니까 눈이 좀 덜 피곤한 것 같습니다. 컴퓨터 오래 보는 직업이라 구매했는데 괜찮네요.",
        "rating": 4
    },
    {
        "title": "재구매 했어요",
        "body": "두번째 구매입니다. 효과가 있는지는 모르겠지만 눈 건강을 위해 계속 먹으려고 합니다.",
        "rating": 4
    },
    {
        "title": "가격 대비 괜찮습니다",
        "body": "루테인 함량도 적당하고 가격도 합리적이어서 좋습니다. 캡슐 크기도 삼키기 편해요.",
        "rating": 5
    },
    {
        "title": "효과는 잘 모르겠어요",
        "body": "2주 정도 먹었는데 아직 눈에 띄는 변화는 없습니다. 좀 더 먹어봐야 알 것 같아요.",
        "rating": 3
    },
    {
        "title": "믿고 먹는 브랜드",
        "body": "이 브랜드 제품들을 여러개 먹고 있는데 품질이 좋은 것 같아서 만족합니다.",
        "rating": 5
    },
    {
        "title": "눈의 피로가 줄었어요",
        "body": "하루종일 모니터 보는 일을 하는데, 먹고나서 눈이 좀 덜 빡빡한 느낌이에요.",
        "rating": 4
    },
    {
        "title": "꾸준히 먹으려구요",
        "body": "눈 건강 관리 차원에서 구매했습니다. 장기적으로 먹어야 효과가 있을 것 같아요.",
        "rating": 4
    },
    {
        "title": "배송 빨랐어요",
        "body": "제품도 좋고 배송도 빨라서 만족합니다. 다음에도 여기서 구매할게요.",
        "rating": 5
    },
    {
        "title": "캡슐 크기가 좀 커요",
        "body": "효과는 괜찮은데 캡슐이 좀 커서 삼키기 힘들어요. 그래도 제품 자체는 좋습니다.",
        "rating": 3
    },
    {
        "title": "가성비 좋아요",
        "body": "이 가격에 이 정도 함량이면 괜찮은 것 같습니다. 만족하며 먹고 있어요.",
        "rating": 4
    },
    {
        "title": "부모님께 드렸어요",
        "body": "부모님 눈 건강 위해 구매했는데 잘 드시고 계세요. 좋은 제품인 것 같습니다.",
        "rating": 5
    },
    {
        "title": "무난한 제품",
        "body": "특별히 나쁜 점도 없고 좋은 점도 없는 무난한 제품입니다.",
        "rating": 3
    }
]

# 광고성 리뷰 템플릿 (40%)
AD_REVIEW_TEMPLATES = [
    {
        "title": "최고의 루테인! 강력 추천합니다!!!",
        "body": "와 진짜 대박이에요!!! 먹자마자 바로 효과 느꼈어요!! 시력이 1.0에서 1.5로 올랐어요!!! 주변 사람들한테 다 추천했습니다!! 이거 아니면 안 먹어요!! 최고최고!!",
        "rating": 5
    },
    {
        "title": "눈 건강의 혁명! 믿을 수 없는 효과!",
        "body": "단 3일만에 눈이 확 좋아졌습니다! 안경을 벗을 수 있게 되었어요! 의사 선생님도 깜짝 놀라셨어요! 이 제품은 정말 기적입니다! 모든 분들께 강력 추천합니다!",
        "rating": 5
    },
    {
        "title": "완벽한 제품!!! 100점 만점에 100점!!!",
        "body": "이런 제품은 처음이에요! 너무너무 좋아요! 효과도 빠르고 가격도 저렴하고! 배송도 빠르고! 포장도 완벽하고! 정말 최고의 제품입니다! 재구매 1000번 할거에요!!!",
        "rating": 5
    },
    {
        "title": "의사가 추천한 그 제품!",
        "body": "안과 의사 친구가 추천해서 샀는데 역시 의사들이 먹는 제품은 다르네요! 효과 장난 아닙니다! 눈이 정말 맑아지고 시력도 좋아졌어요!",
        "rating": 5
    },
    {
        "title": "이거 아니면 안 사요",
        "body": "다른 루테인 다 버리고 이거만 먹어요. 다른 건 효과 없어요. 이 제품만이 진리입니다. 모든 분들 이거 드세요.",
        "rating": 5
    },
    {
        "title": "가족 모두 먹고 있어요!!!",
        "body": "너무 좋아서 온 가족이 다 먹고 있어요! 할머니부터 조카까지! 다들 효과 좋다고 난리에요! 이제 우리집 필수품이 되었습니다!",
        "rating": 5
    },
    {
        "title": "후회 안하실거에요! 당장 구매하세요!",
        "body": "고민하지 마시고 바로 구매하세요! 진짜 후회 안해요! 저는 10통 구매했어요! 지인들한테 나눠주려구요! 최고의 선택이었습니다!",
        "rating": 5
    },
    {
        "title": "눈 건강의 답은 이것!",
        "body": "여러 루테인 먹어봤지만 이것만한게 없어요. 효과 확실하고 가격도 저렴해요. 여러분도 빨리 드세요!",
        "rating": 5
    }
]


def generate_mock_reviews(product_id: int, product_index: int) -> list:
    """
    제품별 20개 리뷰 생성 (정상:광고성 = 12:8)

    Args:
        product_id: 제품 ID (DB에서 생성된 ID)
        product_index: 제품 인덱스 (0-4)

    Returns:
        list: 20개의 리뷰 데이터
    """
    reviews = []

    # 정상 리뷰 12개
    for i in range(12):
        template = random.choice(NORMAL_REVIEW_TEMPLATES)
        review_date = datetime.now() - timedelta(days=random.randint(1, 365))

        reviews.append({
            "product_id": product_id,
            "source": "iherb",
            "source_review_id": f"NORM-{product_index}-{i:03d}",
            "author": f"user{random.randint(1000, 9999)}",
            "rating": template["rating"],
            "title": template["title"],
            "body": template["body"],
            "language": "ko",
            "review_date": review_date.strftime("%Y-%m-%d"),
            "helpful_count": random.randint(0, 50)
        })

    # 광고성 리뷰 8개
    for i in range(8):
        template = random.choice(AD_REVIEW_TEMPLATES)
        review_date = datetime.now() - timedelta(days=random.randint(1, 90))  # 광고성은 최근

        reviews.append({
            "product_id": product_id,
            "source": "iherb",
            "source_review_id": f"AD-{product_index}-{i:03d}",
            "author": f"ad_user{random.randint(1000, 9999)}",
            "rating": 5,  # 광고성 리뷰는 대부분 5점
            "title": template["title"],
            "body": template["body"],
            "language": "ko",
            "review_date": review_date.strftime("%Y-%m-%d"),
            "helpful_count": random.randint(0, 5)  # 광고성은 helpful 적음
        })

    # 날짜순 정렬
    reviews.sort(key=lambda x: x["review_date"], reverse=True)

    return reviews


def get_all_mock_data():
    """
    모든 목업 데이터 반환 (제품 5개 + 리뷰 100개)

    Returns:
        dict: {"products": [...], "reviews": [...]}
    """
    all_reviews = []

    # 각 제품별 리뷰 생성 (product_id는 1부터 시작한다고 가정)
    for idx, product in enumerate(MOCK_PRODUCTS):
        product_id = idx + 1  # DB에서 자동 생성되는 ID 예상
        reviews = generate_mock_reviews(product_id, idx)
        all_reviews.extend(reviews)

    return {
        "products": MOCK_PRODUCTS,
        "reviews": all_reviews
    }


if __name__ == "__main__":
    # 테스트: 목업 데이터 출력
    data = get_all_mock_data()
    print(f"총 제품 수: {len(data['products'])}")
    print(f"총 리뷰 수: {len(data['reviews'])}")
    print(f"\n첫 번째 제품:")
    print(data['products'][0])
    print(f"\n첫 번째 리뷰:")
    print(data['reviews'][0])
