"""
Supabase 테이블 구조 상세 조사 (개선 버전)
"""

import os
import sys
import json
from dotenv import load_dotenv
import requests

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 환경 변수 로드
load_dotenv()

def inspect_supabase_tables():
    """Supabase 테이블 구조 및 데이터 조사"""

    # 환경 변수
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("❌ .env 파일에 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY를 설정하세요.")
        return

    rest_api_url = f"{supabase_url}/rest/v1"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }

    print("=" * 80)
    print("📊 Supabase 테이블 상세 조사")
    print("=" * 80)
    print(f"URL: {supabase_url}\n")

    # 1. products 테이블
    print("-" * 80)
    print("📦 products 테이블")
    print("-" * 80)

    try:
        # 전체 데이터 조회
        response = requests.get(
            f"{rest_api_url}/products",
            headers={**headers, "Prefer": "count=exact"}
        )

        print(f"HTTP 상태 코드: {response.status_code}")

        if response.status_code in [200, 206]:
            data = response.json()
            total = response.headers.get("Content-Range", "*/0").split("/")[1]

            print(f"✅ 총 레코드 수: {total}개\n")

            if data:
                print("📋 컬럼 목록:")
                columns = list(data[0].keys())
                for idx, col in enumerate(columns, 1):
                    print(f"   {idx:2d}. {col}")

                print(f"\n📝 샘플 데이터 (최대 3개):")
                for idx, item in enumerate(data[:3], 1):
                    print(f"\n   [{idx}] ID: {item.get('id')}")
                    print(f"       브랜드: {item.get('brand', 'N/A')}")
                    print(f"       제품명: {item.get('title', 'N/A')}")
                    print(f"       가격: ${item.get('price', 'N/A')} {item.get('currency', 'USD')}")
                    print(f"       평점: {item.get('rating_avg', 'N/A')} ({item.get('rating_count', 0)}개)")
            else:
                print("⚠️  데이터가 없습니다.")
        else:
            print(f"❌ 조회 실패: {response.text}")

    except Exception as e:
        print(f"❌ 오류: {e}")

    # 2. reviews 테이블
    print("\n" + "-" * 80)
    print("💬 reviews 테이블")
    print("-" * 80)

    try:
        response = requests.get(
            f"{rest_api_url}/reviews",
            headers={**headers, "Prefer": "count=exact"}
        )

        print(f"HTTP 상태 코드: {response.status_code}")

        if response.status_code in [200, 206]:
            data = response.json()
            total = response.headers.get("Content-Range", "*/0").split("/")[1]

            print(f"✅ 총 레코드 수: {total}개\n")

            if data:
                print("📋 컬럼 목록:")
                columns = list(data[0].keys())
                for idx, col in enumerate(columns, 1):
                    print(f"   {idx:2d}. {col}")

                print(f"\n📝 샘플 데이터 (최대 3개):")
                for idx, item in enumerate(data[:3], 1):
                    print(f"\n   [{idx}] ID: {item.get('id')}")
                    print(f"       제품 ID: {item.get('product_id', 'N/A')}")
                    print(f"       제목: {item.get('title', 'N/A')}")
                    print(f"       평점: {item.get('rating', 'N/A')}점")
                    print(f"       작성자: {item.get('author', 'N/A')}")
                    print(f"       작성일: {item.get('review_date', 'N/A')}")
                    body = item.get('body', '')
                    if body:
                        print(f"       내용: {body[:60]}...")
            else:
                print("⚠️  데이터가 없습니다.")
        else:
            print(f"❌ 조회 실패: {response.text}")

    except Exception as e:
        print(f"❌ 오류: {e}")

    # 3. 통계
    print("\n" + "-" * 80)
    print("📈 통계 정보")
    print("-" * 80)

    try:
        # 제품 통계
        products_resp = requests.get(
            f"{rest_api_url}/products",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "brand"}
        )

        if products_resp.status_code in [200, 206]:
            products_data = products_resp.json()
            total_products = products_resp.headers.get("Content-Range", "*/0").split("/")[1]

            print(f"총 제품 수: {total_products}개")

            # 브랜드별 집계
            if products_data:
                brands = {}
                for p in products_data:
                    brand = p.get('brand', 'Unknown')
                    brands[brand] = brands.get(brand, 0) + 1

                print("\n브랜드별 제품 수:")
                for brand, count in sorted(brands.items()):
                    print(f"  - {brand}: {count}개")

        # 리뷰 통계
        reviews_resp = requests.get(
            f"{rest_api_url}/reviews",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "rating"}
        )

        if reviews_resp.status_code in [200, 206]:
            reviews_data = reviews_resp.json()
            total_reviews = reviews_resp.headers.get("Content-Range", "*/0").split("/")[1]

            print(f"\n총 리뷰 수: {total_reviews}개")

            # 평점별 집계
            if reviews_data:
                ratings = {}
                for r in reviews_data:
                    rating = r.get('rating')
                    if rating is not None:
                        ratings[rating] = ratings.get(rating, 0) + 1

                print("\n평점별 리뷰 수:")
                for rating in sorted(ratings.keys()):
                    print(f"  - {rating}점: {ratings[rating]}개")

    except Exception as e:
        print(f"❌ 통계 오류: {e}")

    # 4. 제품별 리뷰 수
    print("\n" + "-" * 80)
    print("🔗 제품-리뷰 관계")
    print("-" * 80)

    try:
        # 제품과 리뷰 조인
        response = requests.get(
            f"{rest_api_url}/products",
            headers=headers,
            params={"select": "id,brand,title"}
        )

        if response.status_code in [200, 206]:
            products = response.json()

            print("제품별 리뷰 수:\n")
            for product in products:
                product_id = product['id']

                # 해당 제품의 리뷰 수 조회
                reviews_resp = requests.get(
                    f"{rest_api_url}/reviews",
                    headers={**headers, "Prefer": "count=exact"},
                    params={"product_id": f"eq.{product_id}", "select": "id", "limit": 0}
                )

                if reviews_resp.status_code in [200, 206]:
                    review_count = reviews_resp.headers.get("Content-Range", "*/0").split("/")[1]
                    print(f"  [{product_id}] {product['brand']} - {review_count}개 리뷰")
                    print(f"       {product['title'][:50]}...")

    except Exception as e:
        print(f"❌ 관계 조회 오류: {e}")

    print("\n" + "=" * 80)
    print("✅ 조사 완료")
    print("=" * 80)


if __name__ == "__main__":
    inspect_supabase_tables()
