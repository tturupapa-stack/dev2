"""
Supabase 테이블 구조 조사 스크립트
현재 데이터베이스의 테이블과 컬럼 정보를 확인합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.supabase_client import get_supabase_service_client


def inspect_tables():
    """Supabase 테이블 구조 조사"""
    print("=" * 80)
    print("📊 Supabase 테이블 구조 조사")
    print("=" * 80)

    try:
        supabase = get_supabase_service_client()
        print("✅ Supabase 연결 성공\n")

        # 1. products 테이블 조사
        print("-" * 80)
        print("📦 products 테이블")
        print("-" * 80)

        try:
            products = supabase.table('products').select('*').limit(1).execute()

            if products.data:
                print(f"✅ 테이블 존재 확인")
                print(f"📊 데이터 개수 확인 중...")

                count_result = supabase.table('products').select('id', count='exact').execute()
                print(f"   총 레코드 수: {count_result.count}개\n")

                # 샘플 데이터로 컬럼 구조 확인
                if products.data:
                    print("📋 컬럼 구조 (샘플 데이터 기반):")
                    sample = products.data[0]
                    for key, value in sample.items():
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] if value else "NULL"
                        print(f"   - {key:20s} ({value_type:10s}): {value_preview}")

                    print("\n📝 샘플 데이터 (첫 번째 레코드):")
                    for key, value in sample.items():
                        print(f"   {key}: {value}")
            else:
                print("⚠️  테이블이 비어있습니다.")

        except Exception as e:
            print(f"❌ products 테이블 조회 실패: {e}")

        # 2. reviews 테이블 조사
        print("\n" + "-" * 80)
        print("💬 reviews 테이블")
        print("-" * 80)

        try:
            reviews = supabase.table('reviews').select('*').limit(1).execute()

            if reviews.data:
                print(f"✅ 테이블 존재 확인")
                print(f"📊 데이터 개수 확인 중...")

                count_result = supabase.table('reviews').select('id', count='exact').execute()
                print(f"   총 레코드 수: {count_result.count}개\n")

                # 샘플 데이터로 컬럼 구조 확인
                if reviews.data:
                    print("📋 컬럼 구조 (샘플 데이터 기반):")
                    sample = reviews.data[0]
                    for key, value in sample.items():
                        value_type = type(value).__name__
                        value_preview = str(value)[:50] if value else "NULL"
                        print(f"   - {key:20s} ({value_type:10s}): {value_preview}")

                    print("\n📝 샘플 데이터 (첫 번째 레코드):")
                    for key, value in sample.items():
                        print(f"   {key}: {value}")
            else:
                print("⚠️  테이블이 비어있습니다.")

        except Exception as e:
            print(f"❌ reviews 테이블 조회 실패: {e}")

        # 3. 테이블 관계 확인
        print("\n" + "-" * 80)
        print("🔗 테이블 관계 확인 (JOIN 테스트)")
        print("-" * 80)

        try:
            join_result = supabase.table('reviews')\
                .select('id, title, rating, products(id, brand, title)')\
                .limit(3)\
                .execute()

            if join_result.data:
                print(f"✅ 외래키 관계 확인 성공\n")
                print("📝 샘플 조인 결과 (3개):")
                for idx, review in enumerate(join_result.data, 1):
                    product = review.get('products', {})
                    print(f"\n   {idx}. 리뷰 ID: {review.get('id')}")
                    print(f"      리뷰 제목: {review.get('title', 'N/A')}")
                    print(f"      평점: {review.get('rating', 'N/A')}점")
                    print(f"      제품 브랜드: {product.get('brand', 'N/A')}")
                    print(f"      제품명: {product.get('title', 'N/A')[:40]}...")
            else:
                print("⚠️  조인 결과가 없습니다.")

        except Exception as e:
            print(f"❌ 조인 쿼리 실패: {e}")

        # 4. 통계 정보
        print("\n" + "-" * 80)
        print("📈 데이터 통계")
        print("-" * 80)

        try:
            # 제품 수
            products_count = supabase.table('products').select('id', count='exact').execute()
            print(f"총 제품 수: {products_count.count}개")

            # 리뷰 수
            reviews_count = supabase.table('reviews').select('id', count='exact').execute()
            print(f"총 리뷰 수: {reviews_count.count}개")

            # 브랜드별 제품 수
            if products_count.count > 0:
                products_list = supabase.table('products').select('brand').execute()
                brands = {}
                for p in products_list.data:
                    brand = p.get('brand', 'Unknown')
                    brands[brand] = brands.get(brand, 0) + 1

                print(f"\n브랜드별 제품 수:")
                for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {brand}: {count}개")

            # 평점별 리뷰 수
            if reviews_count.count > 0:
                print(f"\n평점별 리뷰 수:")
                for rating in range(1, 6):
                    rating_result = supabase.table('reviews')\
                        .select('id', count='exact')\
                        .eq('rating', rating)\
                        .execute()
                    print(f"  - {rating}점: {rating_result.count}개")

        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")

        print("\n" + "=" * 80)
        print("✅ 테이블 조사 완료")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Supabase 연결 실패: {e}")
        print("\n확인 사항:")
        print("1. .env 파일에 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 설정 확인")
        print("2. Supabase 프로젝트가 활성화되어 있는지 확인")
        print("3. 테이블이 생성되어 있는지 확인 (schema.sql 실행)")


if __name__ == "__main__":
    inspect_tables()
