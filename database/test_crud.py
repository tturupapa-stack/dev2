"""
Supabase CRUD 테스트 스크립트
제품(products) 및 리뷰(reviews) 테이블에 대한 Create, Read, Update, Delete 테스트
"""

import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.supabase_client import get_supabase_service_client


class CRUDTester:
    """CRUD 작업 테스트 클래스"""

    def __init__(self):
        self.supabase = get_supabase_service_client()
        self.test_product_id = None
        self.test_review_id = None

    def test_create_product(self):
        """제품 생성(Create) 테스트"""
        print("\n" + "=" * 60)
        print("📝 CREATE 테스트 - 제품 생성")
        print("=" * 60)

        test_product = {
            "source": "iherb",
            "source_product_id": "TEST-12345",
            "url": "https://kr.iherb.com/pr/test-product/12345",
            "title": "Test Lutein Product",
            "brand": "Test Brand",
            "category": "루테인",
            "price": 19.99,
            "currency": "USD",
            "rating_avg": 4.5,
            "rating_count": 100
        }

        try:
            result = self.supabase.table('products').insert(test_product).execute()

            if result.data:
                self.test_product_id = result.data[0]['id']
                print(f"✅ 제품 생성 성공!")
                print(f"  - Product ID: {self.test_product_id}")
                print(f"  - Title: {result.data[0]['title']}")
                print(f"  - Brand: {result.data[0]['brand']}")
                return True
            else:
                print("❌ 제품 생성 실패")
                return False

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_read_products(self):
        """제품 조회(Read) 테스트"""
        print("\n" + "=" * 60)
        print("📖 READ 테스트 - 제품 조회")
        print("=" * 60)

        try:
            # 1. 전체 제품 조회
            result = self.supabase.table('products').select('*').execute()
            print(f"✅ 전체 제품 수: {len(result.data)}개")

            # 2. 특정 브랜드 조회
            result = self.supabase.table('products')\
                .select('*')\
                .eq('brand', 'Now Foods')\
                .execute()
            print(f"✅ Now Foods 제품 수: {len(result.data)}개")

            # 3. 가격 범위 조회
            result = self.supabase.table('products')\
                .select('*')\
                .gte('price', 15.0)\
                .lte('price', 20.0)\
                .execute()
            print(f"✅ 가격 $15-$20 제품 수: {len(result.data)}개")

            # 4. 정렬 및 제한
            result = self.supabase.table('products')\
                .select('id, brand, title, price')\
                .order('price', desc=True)\
                .limit(3)\
                .execute()
            print(f"\n✅ 가격 상위 3개 제품:")
            for idx, product in enumerate(result.data, 1):
                print(f"  {idx}. {product['brand']} - ${product['price']}")

            return True

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_update_product(self):
        """제품 수정(Update) 테스트"""
        print("\n" + "=" * 60)
        print("✏️  UPDATE 테스트 - 제품 수정")
        print("=" * 60)

        if not self.test_product_id:
            print("❌ 테스트용 제품이 없습니다. CREATE 테스트를 먼저 실행하세요.")
            return False

        try:
            # 가격 및 평점 업데이트
            update_data = {
                "price": 24.99,
                "rating_avg": 4.8,
                "rating_count": 150
            }

            result = self.supabase.table('products')\
                .update(update_data)\
                .eq('id', self.test_product_id)\
                .execute()

            if result.data:
                print(f"✅ 제품 수정 성공!")
                print(f"  - Product ID: {self.test_product_id}")
                print(f"  - 새 가격: ${result.data[0]['price']}")
                print(f"  - 새 평점: {result.data[0]['rating_avg']}")
                return True
            else:
                print("❌ 제품 수정 실패")
                return False

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_create_review(self):
        """리뷰 생성(Create) 테스트"""
        print("\n" + "=" * 60)
        print("📝 CREATE 테스트 - 리뷰 생성")
        print("=" * 60)

        if not self.test_product_id:
            # 기존 제품 중 하나 사용
            result = self.supabase.table('products').select('id').limit(1).execute()
            if result.data:
                self.test_product_id = result.data[0]['id']
            else:
                print("❌ 테스트용 제품이 없습니다.")
                return False

        test_review = {
            "product_id": self.test_product_id,
            "source": "iherb",
            "source_review_id": "TEST-REV-001",
            "author": "test_user",
            "rating": 5,
            "title": "테스트 리뷰입니다",
            "body": "이것은 CRUD 테스트를 위한 리뷰입니다.",
            "language": "ko",
            "review_date": datetime.now().strftime("%Y-%m-%d"),
            "helpful_count": 0
        }

        try:
            result = self.supabase.table('reviews').insert(test_review).execute()

            if result.data:
                self.test_review_id = result.data[0]['id']
                print(f"✅ 리뷰 생성 성공!")
                print(f"  - Review ID: {self.test_review_id}")
                print(f"  - Title: {result.data[0]['title']}")
                print(f"  - Rating: {result.data[0]['rating']}")
                return True
            else:
                print("❌ 리뷰 생성 실패")
                return False

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_read_reviews(self):
        """리뷰 조회(Read) 테스트"""
        print("\n" + "=" * 60)
        print("📖 READ 테스트 - 리뷰 조회")
        print("=" * 60)

        try:
            # 1. 전체 리뷰 수
            result = self.supabase.table('reviews').select('id', count='exact').execute()
            print(f"✅ 전체 리뷰 수: {result.count}개")

            # 2. 특정 제품의 리뷰
            result = self.supabase.table('reviews')\
                .select('*')\
                .eq('product_id', self.test_product_id)\
                .execute()
            print(f"✅ 테스트 제품 리뷰 수: {len(result.data)}개")

            # 3. 평점별 리뷰 수
            for rating in range(1, 6):
                result = self.supabase.table('reviews')\
                    .select('id', count='exact')\
                    .eq('rating', rating)\
                    .execute()
                print(f"✅ {rating}점 리뷰: {result.count}개")

            # 4. 최근 리뷰 5개
            result = self.supabase.table('reviews')\
                .select('id, title, rating, review_date')\
                .order('review_date', desc=True)\
                .limit(5)\
                .execute()
            print(f"\n✅ 최근 리뷰 5개:")
            for idx, review in enumerate(result.data, 1):
                print(f"  {idx}. [{review['rating']}★] {review['title']} ({review['review_date']})")

            return True

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_update_review(self):
        """리뷰 수정(Update) 테스트"""
        print("\n" + "=" * 60)
        print("✏️  UPDATE 테스트 - 리뷰 수정")
        print("=" * 60)

        if not self.test_review_id:
            print("❌ 테스트용 리뷰가 없습니다. CREATE 테스트를 먼저 실행하세요.")
            return False

        try:
            # helpful_count 증가
            update_data = {
                "helpful_count": 10,
                "body": "수정된 리뷰 내용입니다."
            }

            result = self.supabase.table('reviews')\
                .update(update_data)\
                .eq('id', self.test_review_id)\
                .execute()

            if result.data:
                print(f"✅ 리뷰 수정 성공!")
                print(f"  - Review ID: {self.test_review_id}")
                print(f"  - Helpful Count: {result.data[0]['helpful_count']}")
                return True
            else:
                print("❌ 리뷰 수정 실패")
                return False

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_delete_review(self):
        """리뷰 삭제(Delete) 테스트"""
        print("\n" + "=" * 60)
        print("🗑️  DELETE 테스트 - 리뷰 삭제")
        print("=" * 60)

        if not self.test_review_id:
            print("❌ 테스트용 리뷰가 없습니다.")
            return False

        try:
            result = self.supabase.table('reviews')\
                .delete()\
                .eq('id', self.test_review_id)\
                .execute()

            if result.data:
                print(f"✅ 리뷰 삭제 성공!")
                print(f"  - 삭제된 Review ID: {self.test_review_id}")
                self.test_review_id = None
                return True
            else:
                print("❌ 리뷰 삭제 실패")
                return False

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_delete_product(self):
        """제품 삭제(Delete) 테스트"""
        print("\n" + "=" * 60)
        print("🗑️  DELETE 테스트 - 제품 삭제")
        print("=" * 60)

        if not self.test_product_id:
            print("❌ 테스트용 제품이 없습니다.")
            return False

        try:
            result = self.supabase.table('products')\
                .delete()\
                .eq('id', self.test_product_id)\
                .execute()

            if result.data:
                print(f"✅ 제품 삭제 성공!")
                print(f"  - 삭제된 Product ID: {self.test_product_id}")
                print(f"  - CASCADE로 관련 리뷰도 자동 삭제됨")
                self.test_product_id = None
                return True
            else:
                print("❌ 제품 삭제 실패")
                return False

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def test_join_query(self):
        """조인 쿼리 테스트 (제품 + 리뷰)"""
        print("\n" + "=" * 60)
        print("🔗 JOIN 테스트 - 제품과 리뷰 조인")
        print("=" * 60)

        try:
            # 제품 정보와 함께 리뷰 조회
            result = self.supabase.table('reviews')\
                .select('*, products(brand, title)')\
                .limit(5)\
                .execute()

            print(f"✅ 조인 쿼리 성공! (샘플 5개)")
            for idx, review in enumerate(result.data, 1):
                product_info = review.get('products', {})
                print(f"  {idx}. [{review['rating']}★] {review['title']}")
                print(f"     제품: {product_info.get('brand', 'N/A')} - {product_info.get('title', 'N/A')[:40]}...")

            return True

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🧪 Supabase CRUD 테스트 시작")
    print("=" * 60)

    tester = CRUDTester()
    results = {}

    # 테스트 실행 순서
    tests = [
        ("제품 생성", tester.test_create_product),
        ("제품 조회", tester.test_read_products),
        ("제품 수정", tester.test_update_product),
        ("리뷰 생성", tester.test_create_review),
        ("리뷰 조회", tester.test_read_reviews),
        ("리뷰 수정", tester.test_update_review),
        ("조인 쿼리", tester.test_join_query),
        ("리뷰 삭제", tester.test_delete_review),
        ("제품 삭제", tester.test_delete_product),
    ]

    # 테스트 실행
    for test_name, test_func in tests:
        results[test_name] = test_func()

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)

    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print("\n" + "=" * 60)
    print(f"총 {success_count}/{total_count}개 테스트 통과")
    print("=" * 60)

    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
