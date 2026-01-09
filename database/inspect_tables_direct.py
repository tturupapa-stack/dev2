"""
Supabase REST API를 직접 호출하여 테이블 구조 조사
supabase 패키지 없이 requests만으로 동작
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

    # 환경 변수 가져오기
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("❌ .env 파일에 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY를 설정하세요.")
        return

    # REST API 엔드포인트
    rest_api_url = f"{supabase_url}/rest/v1"

    # 헤더 설정
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }

    print("=" * 80)
    print("📊 Supabase 테이블 구조 조사 (REST API)")
    print("=" * 80)
    print(f"Supabase URL: {supabase_url}")
    print(f"API Key: {service_key[:20]}...")
    print()

    # 1. products 테이블 조사
    print("-" * 80)
    print("📦 products 테이블")
    print("-" * 80)

    try:
        # 데이터 개수 확인
        count_response = requests.get(
            f"{rest_api_url}/products",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "id", "limit": 0}
        )

        if count_response.status_code == 200:
            total_count = count_response.headers.get("Content-Range", "0-0/0").split("/")[1]
            print(f"✅ 테이블 존재 확인")
            print(f"📊 총 레코드 수: {total_count}개\n")

            # 샘플 데이터 1개 조회
            sample_response = requests.get(
                f"{rest_api_url}/products",
                headers=headers,
                params={"limit": 1}
            )

            if sample_response.status_code == 200:
                data = sample_response.json()

                if data:
                    print("📋 컬럼 구조 (샘플 데이터 기반):")
                    sample = data[0]

                    for key, value in sample.items():
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] if value else "NULL"
                        print(f"   - {key:20s} ({value_type:10s}): {value_preview}")

                    print("\n📝 샘플 데이터 (첫 번째 레코드):")
                    print(json.dumps(sample, indent=2, ensure_ascii=False))
                else:
                    print("⚠️  테이블이 비어있습니다.")
        else:
            print(f"❌ 테이블 조회 실패 (HTTP {count_response.status_code})")
            print(f"   응답: {count_response.text}")

    except Exception as e:
        print(f"❌ products 테이블 조회 중 오류: {e}")

    # 2. reviews 테이블 조사
    print("\n" + "-" * 80)
    print("💬 reviews 테이블")
    print("-" * 80)

    try:
        # 데이터 개수 확인
        count_response = requests.get(
            f"{rest_api_url}/reviews",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "id", "limit": 0}
        )

        if count_response.status_code == 200:
            total_count = count_response.headers.get("Content-Range", "0-0/0").split("/")[1]
            print(f"✅ 테이블 존재 확인")
            print(f"📊 총 레코드 수: {total_count}개\n")

            # 샘플 데이터 1개 조회
            sample_response = requests.get(
                f"{rest_api_url}/reviews",
                headers=headers,
                params={"limit": 1}
            )

            if sample_response.status_code == 200:
                data = sample_response.json()

                if data:
                    print("📋 컬럼 구조 (샘플 데이터 기반):")
                    sample = data[0]

                    for key, value in sample.items():
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] if value else "NULL"
                        print(f"   - {key:20s} ({value_type:10s}): {value_preview}")

                    print("\n📝 샘플 데이터 (첫 번째 레코드):")
                    print(json.dumps(sample, indent=2, ensure_ascii=False))
                else:
                    print("⚠️  테이블이 비어있습니다.")
        else:
            print(f"❌ 테이블 조회 실패 (HTTP {count_response.status_code})")
            print(f"   응답: {count_response.text}")

    except Exception as e:
        print(f"❌ reviews 테이블 조회 중 오류: {e}")

    # 3. 통계 정보
    print("\n" + "-" * 80)
    print("📈 데이터 통계")
    print("-" * 80)

    try:
        # 제품 수
        products_response = requests.get(
            f"{rest_api_url}/products",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "id", "limit": 0}
        )

        if products_response.status_code == 200:
            products_count = products_response.headers.get("Content-Range", "0-0/0").split("/")[1]
            print(f"총 제품 수: {products_count}개")

        # 리뷰 수
        reviews_response = requests.get(
            f"{rest_api_url}/reviews",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "id", "limit": 0}
        )

        if reviews_response.status_code == 200:
            reviews_count = reviews_response.headers.get("Content-Range", "0-0/0").split("/")[1]
            print(f"총 리뷰 수: {reviews_count}개")

        # 브랜드별 제품 수
        if int(products_count) > 0:
            brands_response = requests.get(
                f"{rest_api_url}/products",
                headers=headers,
                params={"select": "brand"}
            )

            if brands_response.status_code == 200:
                products_data = brands_response.json()
                brands = {}
                for p in products_data:
                    brand = p.get('brand', 'Unknown')
                    brands[brand] = brands.get(brand, 0) + 1

                print(f"\n브랜드별 제품 수:")
                for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {brand}: {count}개")

        # 평점별 리뷰 수
        if int(reviews_count) > 0:
            print(f"\n평점별 리뷰 수:")
            for rating in range(1, 6):
                rating_response = requests.get(
                    f"{rest_api_url}/reviews",
                    headers={**headers, "Prefer": "count=exact"},
                    params={"select": "id", "rating": f"eq.{rating}", "limit": 0}
                )

                if rating_response.status_code == 200:
                    rating_count = rating_response.headers.get("Content-Range", "0-0/0").split("/")[1]
                    print(f"  - {rating}점: {rating_count}개")

    except Exception as e:
        print(f"❌ 통계 조회 중 오류: {e}")

    # 4. 조인 쿼리 테스트 (외래키 관계 확인)
    print("\n" + "-" * 80)
    print("🔗 테이블 관계 확인 (JOIN 테스트)")
    print("-" * 80)

    try:
        join_response = requests.get(
            f"{rest_api_url}/reviews",
            headers=headers,
            params={
                "select": "id,title,rating,products(id,brand,title)",
                "limit": 3
            }
        )

        if join_response.status_code == 200:
            join_data = join_response.json()

            if join_data:
                print(f"✅ 외래키 관계 확인 성공\n")
                print("📝 샘플 조인 결과 (3개):")

                for idx, review in enumerate(join_data, 1):
                    product = review.get('products', {})
                    print(f"\n   {idx}. 리뷰 ID: {review.get('id')}")
                    print(f"      리뷰 제목: {review.get('title', 'N/A')}")
                    print(f"      평점: {review.get('rating', 'N/A')}점")
                    print(f"      제품 브랜드: {product.get('brand', 'N/A')}")
                    print(f"      제품명: {product.get('title', 'N/A')[:40]}...")
            else:
                print("⚠️  조인 결과가 없습니다.")
        else:
            print(f"❌ 조인 쿼리 실패 (HTTP {join_response.status_code})")
            print(f"   응답: {join_response.text}")

    except Exception as e:
        print(f"❌ 조인 쿼리 중 오류: {e}")

    print("\n" + "=" * 80)
    print("✅ 테이블 조사 완료")
    print("=" * 80)


if __name__ == "__main__":
    inspect_supabase_tables()
