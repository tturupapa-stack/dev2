"""
Supabase 데이터베이스에 목업 데이터 삽입 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.supabase_client import get_supabase_service_client
from database.mock_data import MOCK_PRODUCTS, generate_mock_reviews


def clear_existing_data(supabase):
    """기존 데이터 삭제 (테스트용)"""
    print("\n🗑️  기존 데이터 삭제 중...")

    try:
        # 리뷰 먼저 삭제 (외래키 제약)
        supabase.table('reviews').delete().neq('id', 0).execute()
        print("  - reviews 테이블 데이터 삭제 완료")

        # 제품 삭제
        supabase.table('products').delete().neq('id', 0).execute()
        print("  - products 테이블 데이터 삭제 완료")

    except Exception as e:
        print(f"  ⚠️  데이터 삭제 중 오류 (무시 가능): {e}")


def seed_products(supabase):
    """제품 데이터 삽입"""
    print("\n📦 제품 데이터 삽입 중...")

    inserted_products = []

    for idx, product in enumerate(MOCK_PRODUCTS, 1):
        try:
            result = supabase.table('products').insert(product).execute()

            if result.data:
                product_data = result.data[0]
                inserted_products.append(product_data)
                print(f"  ✅ [{idx}/5] {product['brand']} - {product['title'][:40]}...")
            else:
                print(f"  ❌ [{idx}/5] 삽입 실패: {product['title']}")

        except Exception as e:
            print(f"  ❌ [{idx}/5] 오류 발생: {e}")

    return inserted_products


def seed_reviews(supabase, products):
    """리뷰 데이터 삽입"""
    print("\n💬 리뷰 데이터 삽입 중...")

    total_reviews = 0

    for idx, product in enumerate(products):
        product_id = product['id']
        product_title = product['title'][:30]

        # 제품별 20개 리뷰 생성
        reviews = generate_mock_reviews(product_id, idx)

        try:
            # 배치 삽입 (20개씩)
            result = supabase.table('reviews').insert(reviews).execute()

            if result.data:
                count = len(result.data)
                total_reviews += count
                print(f"  ✅ [{idx + 1}/5] {product_title}... - {count}개 리뷰 삽입")
            else:
                print(f"  ❌ [{idx + 1}/5] {product_title}... - 삽입 실패")

        except Exception as e:
            print(f"  ❌ [{idx + 1}/5] 오류 발생: {e}")

    return total_reviews


def verify_data(supabase):
    """데이터 삽입 확인"""
    print("\n🔍 데이터 검증 중...")

    try:
        # 제품 수 확인
        products_result = supabase.table('products').select('id', count='exact').execute()
        product_count = products_result.count

        # 리뷰 수 확인
        reviews_result = supabase.table('reviews').select('id', count='exact').execute()
        review_count = reviews_result.count

        print(f"  ✅ 총 제품 수: {product_count}개")
        print(f"  ✅ 총 리뷰 수: {review_count}개")

        # 제품별 리뷰 수 확인
        print("\n  📊 제품별 리뷰 수:")
        products = supabase.table('products').select('id, brand, title').execute()

        for product in products.data:
            reviews = supabase.table('reviews')\
                .select('id', count='exact')\
                .eq('product_id', product['id'])\
                .execute()

            print(f"    - {product['brand']}: {reviews.count}개")

        return True

    except Exception as e:
        print(f"  ❌ 검증 중 오류: {e}")
        return False


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 Supabase 목업 데이터 삽입 시작")
    print("=" * 60)

    try:
        # Supabase 서비스 클라이언트 (관리자 권한)
        supabase = get_supabase_service_client()
        print("✅ Supabase 연결 성공")

        # 1. 기존 데이터 삭제 (선택)
        response = input("\n⚠️  기존 데이터를 삭제하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            clear_existing_data(supabase)

        # 2. 제품 데이터 삽입
        products = seed_products(supabase)

        if not products:
            print("\n❌ 제품 데이터 삽입 실패")
            return

        # 3. 리뷰 데이터 삽입
        review_count = seed_reviews(supabase, products)

        # 4. 데이터 검증
        verify_data(supabase)

        print("\n" + "=" * 60)
        print("✅ 목업 데이터 삽입 완료!")
        print("=" * 60)
        print(f"  - 제품: {len(products)}개")
        print(f"  - 리뷰: {review_count}개")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
