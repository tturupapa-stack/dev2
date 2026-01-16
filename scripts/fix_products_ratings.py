"""
Products 테이블의 rating_avg와 rating_count를 실제 리뷰 데이터로 업데이트하는 스크립트
⚠️ 발견된 문제: products.rating_avg와 rating_count가 NULL이거나 0
✅ 해결: 실제 reviews 테이블 데이터를 집계하여 업데이트
"""
import sys
import io
import os
import requests
from datetime import datetime

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 프로젝트 루트를 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Supabase 설정 (SERVICE_ROLE_KEY 사용 - 관리자 권한)
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_KEY = "sb_secret_7colYDry0-0E76v-yrpzFA_ab48cpbo"  # SERVICE_ROLE_KEY

def fetch_all_products():
    """모든 제품 조회"""
    url = f"{SUPABASE_URL}/rest/v1/products"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    params = {"select": "id,brand,title"}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 제품 조회 실패: {response.status_code}")
        return []

def fetch_reviews_for_product(product_id):
    """특정 제품의 모든 리뷰 조회"""
    url = f"{SUPABASE_URL}/rest/v1/reviews"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    params = {
        "select": "rating",
        "product_id": f"eq.{product_id}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def update_product_ratings(product_id, rating_avg, rating_count):
    """제품의 rating_avg와 rating_count 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/products"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    params = {"id": f"eq.{product_id}"}
    
    data = {
        "rating_avg": rating_avg,
        "rating_count": rating_count
    }
    
    response = requests.patch(url, headers=headers, params=params, json=data)
    return response.status_code == 200

def main():
    print("=" * 70)
    print("Products 테이블 Rating 정보 자동 업데이트")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. 모든 제품 조회
    print("\n📦 제품 목록 조회 중...")
    products = fetch_all_products()
    print(f"✅ 총 {len(products)}개 제품 발견")
    
    # 2. 각 제품의 리뷰 집계 및 업데이트
    updated_count = 0
    no_review_count = 0
    
    for i, product in enumerate(products, 1):
        product_id = product['id']
        product_name = f"{product.get('brand', 'N/A')} - {product.get('title', 'N/A')[:40]}"
        
        # 제품의 리뷰 조회
        reviews = fetch_reviews_for_product(product_id)
        
        if reviews:
            # 평균 평점 계산
            ratings = [r['rating'] for r in reviews if r.get('rating') is not None]
            if ratings:
                rating_avg = sum(ratings) / len(ratings)
                rating_count = len(ratings)
                
                # 업데이트
                success = update_product_ratings(product_id, rating_avg, rating_count)
                
                if success:
                    print(f"[{i}/{len(products)}] ✅ {product_name}")
                    print(f"          평점: {rating_avg:.2f} / 리뷰 수: {rating_count}개")
                    updated_count += 1
                else:
                    print(f"[{i}/{len(products)}] ❌ 업데이트 실패: {product_name}")
            else:
                print(f"[{i}/{len(products)}] ⚠️  리뷰는 있지만 평점 없음: {product_name}")
                no_review_count += 1
        else:
            # 리뷰가 없는 경우 0으로 업데이트
            success = update_product_ratings(product_id, 0, 0)
            if success:
                print(f"[{i}/{len(products)}] ⭕ 리뷰 없음 (0으로 설정): {product_name}")
                no_review_count += 1
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("업데이트 완료 요약")
    print("=" * 70)
    print(f"✅ 업데이트 성공: {updated_count}개")
    print(f"⭕ 리뷰 없음: {no_review_count}개")
    print(f"📊 전체: {len(products)}개")
    print("=" * 70)
    
    print("\n✨ 이제 UI에서 제품 평점과 리뷰 수가 정확하게 표시됩니다!")

if __name__ == "__main__":
    main()
