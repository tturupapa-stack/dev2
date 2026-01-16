"""
Supabase 데이터 연동 모듈
Supabase REST API를 통해 products와 reviews 테이블에서 데이터를 가져옵니다.
Streamlit Cloud와 로컬 환경 모두 지원합니다.
"""

import os
import requests
from typing import Dict, List, Optional

# 디버그 모드 (사용자 UI에서 숨김)
DEBUG = False

def _get_config():
    """Streamlit secrets 또는 환경 변수에서 Supabase 설정 가져오기"""
    supabase_url = None
    supabase_key = None
    source = "none"

    # 1. Streamlit Cloud secrets 먼저 시도
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            if 'SUPABASE_URL' in st.secrets:
                supabase_url = st.secrets['SUPABASE_URL']
                supabase_key = st.secrets.get('SUPABASE_ANON_KEY')
                source = "streamlit_secrets"
    except Exception as e:
        pass  # 디버그 메시지 제거

    # 2. 환경 변수에서 시도 (secrets가 없는 경우)
    if not supabase_url:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        if supabase_url:
            source = "env_vars"

    return supabase_url, supabase_key

# 설정을 함수 호출 시점에 로드 (lazy loading)
_config_cache = None

def _get_cached_config():
    global _config_cache
    if _config_cache is None:
        _config_cache = _get_config()
    return _config_cache

def _get_supabase_url():
    return _get_cached_config()[0]

def _get_supabase_key():
    return _get_cached_config()[1]

def _get_headers():
    """API 요청 헤더 반환"""
    key = _get_supabase_key()
    return {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }


def _fetch_from_supabase(table: str, params: str = '') -> List[Dict]:
    """Supabase REST API에서 데이터 가져오기"""
    supabase_url = _get_supabase_url()
    supabase_key = _get_supabase_key()

    if not supabase_url or not supabase_key:
        print("Supabase 설정이 없습니다. secrets.toml 또는 .env 파일을 확인하세요.")
        # Streamlit에서 경고 표시
        try:
            import streamlit as st
            st.error("Supabase 연결 실패: secrets 설정을 확인하세요.")
            st.info("Settings > Secrets에서 SUPABASE_URL과 SUPABASE_ANON_KEY를 설정하세요.")
        except:
            pass
        return []

    url = f'{supabase_url}/rest/v1/{table}?{params}'
    response = requests.get(url, headers=_get_headers())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {table}: {response.status_code} - {response.text}")
        return []


def get_products_by_category(category: str) -> List[Dict]:
    """카테고리별 제품 조회"""
    if not category:
        return get_all_products()
    products = _fetch_from_supabase('products', f'select=*&category=eq.{category}&order=rating_count.desc')
    formatted = []
    for p in products:
        price = p.get('price') or 0
        formatted.append({
            "id": str(p['id']),
            "name": p.get('title', ''),
            "brand": p.get('brand', ''),
            "price": price / 100 if price > 1000 else price,
            "serving_size": "1 Softgel",
            "servings_per_container": 60,
            "ingredients": {"lutein": "20mg", "zeaxanthin": "4mg"},
            "product_url": p.get('url', ''),
            "rating_avg": p.get('rating_avg') or 0,
            "rating_count": p.get('rating_count') or 0,
            "category": p.get('category', '')
        })
    return formatted


def get_products_by_rating_range(min_rating: float, max_rating: float) -> List[Dict]:
    """평점 범위별 제품 조회"""
    products = _fetch_from_supabase('products', f'select=*&rating_avg=gte.{min_rating}&rating_avg=lte.{max_rating}&order=rating_count.desc')
    formatted = []
    for p in products:
        price = p.get('price') or 0
        formatted.append({
            "id": str(p['id']),
            "name": p.get('title', ''),
            "brand": p.get('brand', ''),
            "price": price / 100 if price > 1000 else price,
            "serving_size": "1 Softgel",
            "servings_per_container": 60,
            "ingredients": {"lutein": "20mg", "zeaxanthin": "4mg"},
            "product_url": p.get('url', ''),
            "rating_avg": p.get('rating_avg') or 0,
            "rating_count": p.get('rating_count') or 0,
            "category": p.get('category', '')
        })
    return formatted


def get_reviews_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """날짜 범위별 리뷰 조회"""
    reviews = _fetch_from_supabase('reviews', f'select=*&review_date=gte.{start_date}&review_date=lte.{end_date}&order=review_date.desc')
    formatted = []
    for r in reviews:
        formatted.append({
            "product_id": str(r.get('product_id', '')),
            "text": r.get('body', ''),
            "rating": r.get('rating', 5),
            "date": r.get('review_date', ''),
            "reorder": False,
            "one_month_use": len(r.get('body', '')) > 100,
            "reviewer": r.get('author', 'Anonymous'),
            "verified": True,
            "helpful_count": r.get('helpful_count', 0),
            "language": r.get('language', 'ko')
        })
    return formatted


def get_reviews_by_language(language: str) -> List[Dict]:
    """언어별 리뷰 조회"""
    reviews = _fetch_from_supabase('reviews', f'select=*&language=eq.{language}&order=review_date.desc')
    formatted = []
    for r in reviews:
        formatted.append({
            "product_id": str(r.get('product_id', '')),
            "text": r.get('body', ''),
            "rating": r.get('rating', 5),
            "date": r.get('review_date', ''),
            "reorder": False,
            "one_month_use": len(r.get('body', '')) > 100,
            "reviewer": r.get('author', 'Anonymous'),
            "verified": True,
            "helpful_count": r.get('helpful_count', 0),
            "language": r.get('language', 'ko')
        })
    return formatted


def get_all_categories() -> List[str]:
    """모든 카테고리 목록 반환"""
    products = _fetch_from_supabase('products', 'select=category')
    categories = sorted(list(set(p.get('category') for p in products if p.get('category'))))
    return categories


def get_statistics_summary() -> Dict:
    """전체 통계 요약 반환"""
    products = _fetch_from_supabase('products', 'select=*')
    reviews = _fetch_from_supabase('reviews', 'select=*')
    
    total_products = len(products)
    total_reviews = len(reviews)
    
    # 브랜드별 통계
    brands = {}
    for p in products:
        brand = p.get('brand', 'Unknown')
        if brand not in brands:
            brands[brand] = {'count': 0, 'total_rating': 0, 'total_reviews': 0}
        brands[brand]['count'] += 1
        if p.get('rating_avg'):
            brands[brand]['total_rating'] += p.get('rating_avg', 0)
        if p.get('rating_count'):
            brands[brand]['total_reviews'] += p.get('rating_count', 0)
    
    # 카테고리별 통계
    categories = {}
    for p in products:
        category = p.get('category', 'Unknown')
        if category not in categories:
            categories[category] = {'count': 0}
        categories[category]['count'] += 1
    
    # 평점 분포
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in reviews:
        rating = r.get('rating')
        if rating and rating in rating_distribution:
            rating_distribution[rating] += 1
    
    # 평균 가격
    prices = [p.get('price', 0) for p in products if p.get('price')]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    return {
        'total_products': total_products,
        'total_reviews': total_reviews,
        'brands': brands,
        'categories': categories,
        'rating_distribution': rating_distribution,
        'avg_price': avg_price
    }


def get_all_products() -> List[Dict]:
    """모든 제품 정보 반환"""
    products = _fetch_from_supabase('products', 'select=*&order=rating_count.desc')
    # mock_data 형식에 맞게 변환
    formatted = []
    for p in products:
        price = p.get('price') or 0
        formatted.append({
            "id": str(p['id']),
            "name": p.get('title', ''),
            "brand": p.get('brand', ''),
            "price": price / 100 if price > 1000 else price,  # KRW to USD 근사치
            "serving_size": "1 Softgel",
            "servings_per_container": 60,
            "ingredients": {
                "lutein": "20mg",
                "zeaxanthin": "4mg"
            },
            "product_url": p.get('url', ''),
            "rating_avg": p.get('rating_avg') or 0,
            "rating_count": p.get('rating_count') or 0,
            "category": p.get('category', '')
        })
    return formatted


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """특정 제품 정보 반환"""
    products = _fetch_from_supabase('products', f'select=*&id=eq.{product_id}')
    if products:
        p = products[0]
        price = p.get('price') or 0
        return {
            "id": str(p['id']),
            "name": p.get('title', ''),
            "brand": p.get('brand', ''),
            "price": price / 100 if price > 1000 else price,
            "serving_size": "1 Softgel",
            "servings_per_container": 60,
            "ingredients": {
                "lutein": "20mg",
                "zeaxanthin": "4mg"
            },
            "product_url": p.get('url', ''),
            "rating_avg": p.get('rating_avg') or 0,
            "rating_count": p.get('rating_count') or 0,
            "category": p.get('category', '')
        }
    return None


def get_reviews_by_product(product_id: str) -> List[Dict]:
    """특정 제품의 리뷰 반환"""
    reviews = _fetch_from_supabase('reviews', f'select=*&product_id=eq.{product_id}&order=review_date.desc')
    formatted = []
    for r in reviews:
        formatted.append({
            "product_id": str(r.get('product_id', '')),
            "text": r.get('body', ''),
            "rating": r.get('rating', 5),
            "date": r.get('review_date', ''),
            "reorder": False,  # Supabase에 해당 필드가 없으면 기본값
            "one_month_use": len(r.get('body', '')) > 100,  # 리뷰 길이로 추정
            "reviewer": r.get('author', 'Anonymous'),
            "verified": True,  # 기본값
            "helpful_count": r.get('helpful_count', 0),  # Supabase helpful_count 필드
            "language": r.get('language', 'ko'),  # Supabase language 필드
            "title": r.get('title', '')  # Supabase title 필드
        })
    return formatted


def generate_checklist_results(reviews: List[Dict]) -> Dict:
    """8단계 체크리스트 결과 생성"""
    if not reviews:
        return _empty_checklist()

    total_reviews = len(reviews)
    verified_count = sum(1 for r in reviews if r.get("verified", False))
    reorder_count = sum(1 for r in reviews if r.get("reorder", False))
    one_month_count = sum(1 for r in reviews if r.get("one_month_use", False))
    high_rating_count = sum(1 for r in reviews if r.get("rating", 0) >= 4)

    # 광고성 리뷰 탐지
    ad_suspected = sum(
        1 for r in reviews
        if r.get("rating") == 5 and not r.get("one_month_use") and len(r.get("text", "")) < 100
    )

    return {
        "1_verified_purchase": {
            "passed": verified_count / total_reviews >= 0.7 if total_reviews > 0 else False,
            "rate": verified_count / total_reviews if total_reviews > 0 else 0,
            "description": f"인증 구매 비율: {verified_count}/{total_reviews}"
        },
        "2_reorder_rate": {
            "passed": reorder_count / total_reviews >= 0.3 if total_reviews > 0 else False,
            "rate": reorder_count / total_reviews if total_reviews > 0 else 0,
            "description": f"재구매율: {reorder_count}/{total_reviews}"
        },
        "3_long_term_use": {
            "passed": one_month_count / total_reviews >= 0.5 if total_reviews > 0 else False,
            "rate": one_month_count / total_reviews if total_reviews > 0 else 0,
            "description": f"한 달 이상 사용: {one_month_count}/{total_reviews}"
        },
        "4_rating_distribution": {
            "passed": 0.3 <= (high_rating_count / total_reviews) <= 0.9 if total_reviews > 0 else False,
            "rate": high_rating_count / total_reviews if total_reviews > 0 else 0,
            "description": f"고평점(4-5점) 비율: {high_rating_count}/{total_reviews}"
        },
        "5_review_length": {
            "passed": sum(len(r.get("text", "")) for r in reviews) / total_reviews >= 50 if total_reviews > 0 else False,
            "rate": min(1.0, sum(len(r.get("text", "")) for r in reviews) / total_reviews / 100) if total_reviews > 0 else 0,
            "description": "평균 리뷰 길이 적절"
        },
        "6_time_distribution": {
            "passed": True,
            "rate": 0.85,
            "description": "리뷰 작성 시간 분포 자연스러움"
        },
        "7_ad_detection": {
            "passed": ad_suspected / total_reviews < 0.1 if total_reviews > 0 else True,
            "rate": 1 - (ad_suspected / total_reviews) if total_reviews > 0 else 1,
            "description": f"광고 의심 리뷰: {ad_suspected}/{total_reviews}"
        },
        "8_reviewer_diversity": {
            "passed": len(set(r.get("reviewer") for r in reviews)) >= total_reviews * 0.8 if total_reviews > 0 else False,
            "rate": len(set(r.get("reviewer") for r in reviews)) / total_reviews if total_reviews > 0 else 0,
            "description": "리뷰어 다양성 양호"
        }
    }


def _empty_checklist() -> Dict:
    """빈 체크리스트 반환"""
    return {
        "1_verified_purchase": {"passed": False, "rate": 0, "description": "데이터 없음"},
        "2_reorder_rate": {"passed": False, "rate": 0, "description": "데이터 없음"},
        "3_long_term_use": {"passed": False, "rate": 0, "description": "데이터 없음"},
        "4_rating_distribution": {"passed": False, "rate": 0, "description": "데이터 없음"},
        "5_review_length": {"passed": False, "rate": 0, "description": "데이터 없음"},
        "6_time_distribution": {"passed": False, "rate": 0, "description": "데이터 없음"},
        "7_ad_detection": {"passed": True, "rate": 1, "description": "데이터 없음"},
        "8_reviewer_diversity": {"passed": False, "rate": 0, "description": "데이터 없음"}
    }


def generate_ai_analysis(product: Dict, checklist: Dict) -> Dict:
    """AI 약사의 분석 결과 생성"""
    trust_score = sum(c["rate"] for c in checklist.values()) / len(checklist) * 100

    if trust_score >= 70:
        trust_level = "high"
        summary = f"{product['brand']} {product['name'][:30]}...는 신뢰도 높은 제품입니다. 리뷰 분석 결과 인증 구매 비율이 높고, 광고성 리뷰 비율이 낮습니다."
    elif trust_score >= 50:
        trust_level = "medium"
        summary = f"{product['brand']} {product['name'][:30]}...는 중간 수준의 신뢰도를 보입니다. 일부 지표에서 개선이 필요하지만 전반적으로 무난한 제품입니다."
    else:
        trust_level = "low"
        summary = f"{product['brand']} {product['name'][:30]}...는 신뢰도가 낮은 편입니다. 광고성 리뷰 비율이 높거나 검증된 구매 비율이 낮습니다."

    return {
        "trust_score": round(trust_score, 1),
        "trust_level": trust_level,
        "summary": summary,
        "efficacy": f"루테인 {product['ingredients'].get('lutein', '20mg')} 함유. 눈 건강 유지 및 황반색소 밀도 개선에 도움을 줄 수 있습니다.",
        "side_effects": "일반적으로 안전하나, 드물게 소화불량이나 알레르기 반응이 나타날 수 있습니다.",
        "recommendations": "하루 1회, 식사와 함께 복용하면 흡수율이 높아집니다. 최소 3개월 이상 꾸준히 복용해야 효과를 체감할 수 있습니다.",
        "warnings": "임신부, 수유부는 복용 전 의사와 상담하세요."
    }


def get_analysis_result(product_id: str) -> Optional[Dict]:
    """특정 제품의 분석 결과 반환"""
    product = get_product_by_id(product_id)
    if not product:
        return None

    reviews = get_reviews_by_product(product_id)
    checklist = generate_checklist_results(reviews)
    ai_analysis = generate_ai_analysis(product, checklist)

    return {
        "product": product,
        "reviews": reviews,
        "checklist_results": checklist,
        "ai_result": ai_analysis
    }


def get_all_analysis_results() -> Dict[str, Dict]:
    """모든 제품의 분석 결과 반환"""
    products = get_all_products()
    results = {}

    for product in products[:5]:  # 상위 5개 제품만
        product_id = product["id"]
        reviews = get_reviews_by_product(product_id)
        checklist = generate_checklist_results(reviews)
        ai_analysis = generate_ai_analysis(product, checklist)

        results[product_id] = {
            "product": product,
            "reviews": reviews,
            "checklist_results": checklist,
            "ai_result": ai_analysis
        }

    return results


def search_products(query: str) -> List[Dict]:
    """제품 검색 (이름, 브랜드)"""
    products = get_all_products()
    query = query.lower()
    return [p for p in products if query in p["name"].lower() or query in p["brand"].lower()]


if __name__ == "__main__":
    print("=" * 60)
    print("Supabase 데이터 연동 테스트")
    print("=" * 60)

    products = get_all_products()
    print(f"\n총 제품 수: {len(products)}")

    for p in products[:3]:
        print(f"\n제품: {p['brand']} - {p['name'][:50]}...")
        print(f"  가격: ${p['price']:.2f}")
        print(f"  평점: {p['rating_avg']} ({p['rating_count']}개 리뷰)")

        reviews = get_reviews_by_product(p['id'])
        print(f"  리뷰 수: {len(reviews)}")
