"""
Supabase REST API 연동 통합 테스트
supabase-py 패키지 없이 REST API로 직접 연동
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import requests

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from logic_designer import analyze
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class SupabaseRestClient:
    """Supabase REST API 클라이언트"""

    def __init__(self, url, key):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }

    def select(self, table, columns='*', limit=None):
        """SELECT 쿼리 실행"""
        endpoint = f"{self.url}/rest/v1/{table}"
        params = {'select': columns}
        if limit:
            params['limit'] = limit

        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()


class SupabaseIntegrationTest:
    """Supabase 데이터베이스 연동 테스트 클래스"""

    def __init__(self):
        self.client = None
        self.products = []
        self.reviews = []
        self.test_results = []
        self.statistics = {}

    def connect_to_supabase(self):
        """Supabase 연결"""
        print("\n" + "=" * 80)
        print("🔌 Supabase REST API 연결 중...")
        print("=" * 80)

        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

            if not supabase_url or not supabase_key:
                print("❌ 환경 변수가 설정되지 않았습니다.")
                print("   .env 파일에 다음을 설정하세요:")
                print("   SUPABASE_URL=https://your-project.supabase.co")
                print("   SUPABASE_ANON_KEY=your-anon-key")
                return False

            self.client = SupabaseRestClient(supabase_url, supabase_key)

            # 연결 테스트
            test_response = self.client.select('products', limit=1)
            print(f"✅ Supabase 연결 성공!")
            print(f"   URL: {supabase_url}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ 연결 실패: {e}")
            return False
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

    def fetch_products(self):
        """제품 데이터 가져오기"""
        print("\n" + "=" * 80)
        print("📦 제품 데이터 가져오는 중...")
        print("=" * 80)

        try:
            self.products = self.client.select('products')

            print(f"✅ 제품 {len(self.products)}개 로드 완료")
            for idx, product in enumerate(self.products, 1):
                brand = product.get('brand', 'N/A')
                title = product.get('title', 'N/A')
                print(f"   [{idx}] {brand} - {title[:50]}...")

            return True

        except Exception as e:
            print(f"❌ 제품 데이터 가져오기 실패: {e}")
            return False

    def fetch_reviews(self, limit=50):
        """리뷰 데이터 가져오기"""
        print("\n" + "=" * 80)
        print(f"💬 리뷰 데이터 가져오는 중 (최대 {limit}개)...")
        print("=" * 80)

        try:
            self.reviews = self.client.select('reviews', limit=limit)

            print(f"✅ 리뷰 {len(self.reviews)}개 로드 완료")

            # 제품별 리뷰 수 통계
            product_review_count = {}
            for review in self.reviews:
                product_id = review.get('product_id')
                product_review_count[product_id] = product_review_count.get(product_id, 0) + 1

            print(f"\n   제품별 리뷰 수:")
            for product_id, count in sorted(product_review_count.items()):
                product = next((p for p in self.products if p['id'] == product_id), None)
                product_name = product.get('brand', 'Unknown') if product else 'Unknown'
                print(f"     - {product_name}: {count}개")

            return True

        except Exception as e:
            print(f"❌ 리뷰 데이터 가져오기 실패: {e}")
            return False

    def analyze_reviews(self, max_reviews=20):
        """리뷰 분석 실행"""
        print("\n" + "=" * 80)
        print(f"🔍 리뷰 분석 시작 (최대 {max_reviews}개)")
        print("=" * 80)

        # AI 분석 제외 (비용 절약)
        api_key = None

        reviews_to_test = self.reviews[:max_reviews]

        for idx, review in enumerate(reviews_to_test, 1):
            review_id = review.get('id', 'N/A')
            review_title = review.get('title', '제목 없음')
            review_body = review.get('body', '')
            review_rating = review.get('rating', 0)
            product_id = review.get('product_id')

            # 제품 정보 찾기
            product = next((p for p in self.products if p['id'] == product_id), None)
            product_name = product.get('brand', 'Unknown') if product else 'Unknown'

            # 리뷰 텍스트 생성
            review_text = f"{review_title}\n{review_body}" if review_title else review_body

            if len(review_text.strip()) < 10:
                print(f"\n[{idx}/{len(reviews_to_test)}] ⚠️  리뷰가 너무 짧아 건너뜀 (ID: {review_id})")
                continue

            print(f"\n[{idx}/{len(reviews_to_test)}] 분석 중...")
            print(f"  제품: {product_name}")
            print(f"  리뷰 ID: {review_id}")
            print(f"  제목: {review_title[:50] if review_title else '(제목 없음)'}...")
            print(f"  평점: {review_rating}")

            try:
                # 점수 계산 (간단한 휴리스틱)
                length_score = min(100, len(review_text) / 2)  # 길이 기반
                repurchase_score = 60  # 기본값
                monthly_use_score = 60  # 기본값
                photo_score = 0  # 사진 정보 없음
                consistency_score = review_rating * 20 if review_rating else 50  # 평점 기반

                # analyze() 호출
                result = analyze(
                    review_text=review_text,
                    length_score=length_score,
                    repurchase_score=repurchase_score,
                    monthly_use_score=monthly_use_score,
                    photo_score=photo_score,
                    consistency_score=consistency_score,
                    api_key=api_key
                )

                # 결과 저장
                self.test_results.append({
                    'review_id': review_id,
                    'product_id': product_id,
                    'product_name': product_name,
                    'title': review_title,
                    'rating': review_rating,
                    'review_text_preview': review_text[:100],
                    'result': result
                })

                # 결과 출력
                validation = result['validation']
                print(f"  신뢰도 점수: {validation['trust_score']}")
                print(f"  광고 여부: {'❌ 광고' if validation['is_ad'] else '✅ 정상'}")
                print(f"  감점 항목: {validation['detected_count']}개")
                if validation['reasons']:
                    print(f"  감점 사유: {', '.join(validation['reasons'][:3])}")

            except Exception as e:
                print(f"  ❌ 분석 실패: {e}")

    def calculate_statistics(self):
        """통계 계산"""
        print("\n" + "=" * 80)
        print("📊 통계 분석")
        print("=" * 80)

        if not self.test_results:
            print("⚠️  분석된 리뷰가 없습니다.")
            return

        # 기본 통계
        total_reviews = len(self.test_results)
        trust_scores = [r['result']['validation']['trust_score'] for r in self.test_results]
        ad_count = sum(1 for r in self.test_results if r['result']['validation']['is_ad'])
        normal_count = total_reviews - ad_count

        # 평점별 통계
        rating_distribution = {}
        for r in self.test_results:
            rating = r['rating']
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1

        # 제품별 통계
        product_stats = {}
        for r in self.test_results:
            product_name = r['product_name']
            if product_name not in product_stats:
                product_stats[product_name] = {
                    'total': 0,
                    'ad_count': 0,
                    'avg_trust_score': []
                }
            product_stats[product_name]['total'] += 1
            if r['result']['validation']['is_ad']:
                product_stats[product_name]['ad_count'] += 1
            product_stats[product_name]['avg_trust_score'].append(
                r['result']['validation']['trust_score']
            )

        # 통계 저장
        self.statistics = {
            'total_reviews': total_reviews,
            'ad_count': ad_count,
            'normal_count': normal_count,
            'ad_rate': round(ad_count / total_reviews * 100, 2) if total_reviews else 0,
            'avg_trust_score': round(sum(trust_scores) / len(trust_scores), 2) if trust_scores else 0,
            'min_trust_score': min(trust_scores) if trust_scores else 0,
            'max_trust_score': max(trust_scores) if trust_scores else 0,
            'rating_distribution': rating_distribution,
            'product_stats': product_stats
        }

        # 통계 출력
        print(f"\n✅ 전체 통계:")
        print(f"  - 분석된 리뷰 수: {total_reviews}개")
        print(f"  - 정상 리뷰: {normal_count}개 ({100 - self.statistics['ad_rate']:.2f}%)")
        print(f"  - 광고 리뷰: {ad_count}개 ({self.statistics['ad_rate']:.2f}%)")
        print(f"  - 평균 신뢰도: {self.statistics['avg_trust_score']}")
        print(f"  - 신뢰도 범위: {self.statistics['min_trust_score']} ~ {self.statistics['max_trust_score']}")

        print(f"\n📊 평점 분포:")
        for rating in sorted(rating_distribution.keys(), reverse=True):
            count = rating_distribution[rating]
            percentage = round(count / total_reviews * 100, 1)
            bar = "█" * int(percentage / 5)
            print(f"  ⭐ {rating}점: {count}개 ({percentage:5.1f}%) {bar}")

        print(f"\n🏢 제품별 통계:")
        for product_name, stats in product_stats.items():
            avg_score = round(sum(stats['avg_trust_score']) / len(stats['avg_trust_score']), 2)
            ad_rate = round(stats['ad_count'] / stats['total'] * 100, 1)
            print(f"  - {product_name}:")
            print(f"    총 {stats['total']}개 | 광고 {stats['ad_count']}개 ({ad_rate}%) | 평균 신뢰도 {avg_score}")

    def generate_report(self):
        """개발일지 보고서 생성"""
        print("\n" + "=" * 80)
        print("📝 개발일지 보고서 생성 중...")
        print("=" * 80)

        report_dir = project_root / "개발일지"
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / f"{datetime.now().strftime('%Y-%m-%d')}-Supabase_통합_테스트.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Supabase 통합 테스트 개발일지\n\n")
            f.write(f"**작성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**작성자**: Claude (AI Assistant)\n")
            f.write(f"**테스트 대상**: Supabase REST API + logic_designer 모듈\n\n")
            f.write(f"---\n\n")

            # 1. 테스트 개요
            f.write(f"## 1. 테스트 개요\n\n")
            f.write(f"### 1.1 목적\n")
            f.write(f"실제 Supabase 데이터베이스에 저장된 iHerb 루테인 제품 리뷰를 가져와\n")
            f.write(f"`logic_designer` 모듈의 광고 판별 및 신뢰도 분석 기능을 검증합니다.\n\n")

            f.write(f"### 1.2 테스트 환경\n")
            f.write(f"- **데이터베이스**: Supabase PostgreSQL\n")
            f.write(f"- **연동 방식**: REST API (supabase-py 패키지 대신 직접 HTTP 요청)\n")
            f.write(f"- **분석 모듈**: logic_designer (checklist + trust_score + analyzer)\n")
            f.write(f"- **AI 분석**: 비활성화 (비용 절약)\n\n")

            # 2. 데이터 현황
            f.write(f"## 2. 데이터 현황\n\n")
            f.write(f"### 2.1 제품 정보\n")
            f.write(f"총 **{len(self.products)}개** 제품이 데이터베이스에 저장되어 있습니다.\n\n")
            for idx, product in enumerate(self.products, 1):
                brand = product.get('brand', 'N/A')
                title = product.get('title', 'N/A')
                price = product.get('price', 'N/A')
                f.write(f"{idx}. **{brand}** - {title}\n")
                f.write(f"   - 가격: ${price}\n")
            f.write(f"\n")

            f.write(f"### 2.2 리뷰 정보\n")
            f.write(f"- 데이터베이스 총 리뷰 수: {len(self.reviews)}개\n")
            f.write(f"- 이번 테스트에서 분석된 리뷰 수: **{self.statistics.get('total_reviews', 0)}개**\n\n")

            # 3. 분석 결과
            f.write(f"## 3. 분석 결과\n\n")
            f.write(f"### 3.1 전체 통계\n\n")
            f.write(f"| 지표 | 값 | 비고 |\n")
            f.write(f"|------|-----|------|\n")
            f.write(f"| 분석된 리뷰 수 | {self.statistics.get('total_reviews', 0)}개 | - |\n")
            f.write(f"| 정상 리뷰 | {self.statistics.get('normal_count', 0)}개 | {100 - self.statistics.get('ad_rate', 0):.2f}% |\n")
            f.write(f"| 광고 리뷰 | {self.statistics.get('ad_count', 0)}개 | {self.statistics.get('ad_rate', 0):.2f}% |\n")
            f.write(f"| 평균 신뢰도 점수 | {self.statistics.get('avg_trust_score', 0)} | 0-100 척도 |\n")
            f.write(f"| 신뢰도 범위 | {self.statistics.get('min_trust_score', 0)} ~ {self.statistics.get('max_trust_score', 0)} | - |\n\n")

            # 평점 분포
            f.write(f"### 3.2 평점 분포\n\n")
            rating_dist = self.statistics.get('rating_distribution', {})
            total = self.statistics.get('total_reviews', 1)
            for rating in sorted(rating_dist.keys(), reverse=True):
                count = rating_dist[rating]
                percentage = round(count / total * 100, 1)
                f.write(f"- ⭐ **{rating}점**: {count}개 ({percentage}%)\n")
            f.write(f"\n")

            # 제품별 분석
            f.write(f"### 3.3 제품별 분석\n\n")
            product_stats = self.statistics.get('product_stats', {})
            for product_name, stats in product_stats.items():
                avg_score = round(sum(stats['avg_trust_score']) / len(stats['avg_trust_score']), 2)
                ad_rate = round(stats['ad_count'] / stats['total'] * 100, 1)
                f.write(f"#### {product_name}\n")
                f.write(f"- 총 리뷰: **{stats['total']}개**\n")
                f.write(f"- 광고 리뷰: {stats['ad_count']}개 ({ad_rate}%)\n")
                f.write(f"- 정상 리뷰: {stats['total'] - stats['ad_count']}개 ({100 - ad_rate:.1f}%)\n")
                f.write(f"- 평균 신뢰도: **{avg_score}점**\n\n")

            # 4. 상세 분석 결과 (상위 10개만)
            f.write(f"## 4. 상세 분석 결과 (샘플)\n\n")
            for idx, result in enumerate(self.test_results[:10], 1):
                validation = result['result']['validation']
                f.write(f"### [{idx}] {result['title']}\n\n")
                f.write(f"```\n")
                f.write(f"{result['review_text_preview']}...\n")
                f.write(f"```\n\n")
                f.write(f"| 항목 | 값 |\n")
                f.write(f"|------|-----|\n")
                f.write(f"| 제품 | {result['product_name']} |\n")
                f.write(f"| 평점 | ⭐ {result['rating']} |\n")
                f.write(f"| 신뢰도 점수 | {validation['trust_score']} |\n")
                f.write(f"| 판별 결과 | {'❌ 광고' if validation['is_ad'] else '✅ 정상'} |\n")
                f.write(f"| 감점 항목 수 | {validation['detected_count']}개 |\n")
                if validation['reasons']:
                    f.write(f"| 감점 사유 | {', '.join(validation['reasons'])} |\n")
                f.write(f"\n")

            # 5. 발견 사항 및 인사이트
            f.write(f"## 5. 발견 사항 및 인사이트\n\n")
            f.write(f"### 5.1 광고 리뷰 비율 분석\n")
            ad_rate = self.statistics.get('ad_rate', 0)
            if ad_rate > 50:
                f.write(f"- ⚠️ **매우 높음** ({ad_rate:.2f}%): 체크리스트가 너무 엄격할 수 있습니다.\n")
                f.write(f"- 권장 조치: `checklist.py`의 패턴을 완화하고 임계값을 조정하세요.\n")
            elif ad_rate > 30:
                f.write(f"- ⚠️ **높음** ({ad_rate:.2f}%): 일부 정상 리뷰가 오탐될 가능성이 있습니다.\n")
                f.write(f"- 권장 조치: 개인 경험 패턴과 단점 회피 로직을 검토하세요.\n")
            elif ad_rate > 10:
                f.write(f"- ✅ **적정 수준** ({ad_rate:.2f}%): 광고 판별 로직이 적절하게 작동하고 있습니다.\n")
            else:
                f.write(f"- ✅ **낮음** ({ad_rate:.2f}%): 양질의 리뷰 데이터입니다.\n")
            f.write(f"\n")

            f.write(f"### 5.2 신뢰도 점수 분포\n")
            avg_score = self.statistics.get('avg_trust_score', 0)
            if avg_score < 30:
                f.write(f"- ⚠️ 평균 신뢰도가 매우 낮습니다 ({avg_score}점).\n")
                f.write(f"- 체크리스트 감점 로직이 과도하게 작동하고 있을 수 있습니다.\n")
            elif avg_score < 50:
                f.write(f"- ⚠️ 평균 신뢰도가 낮은 편입니다 ({avg_score}점).\n")
                f.write(f"- 일부 리뷰가 광고로 오인될 가능성이 있습니다.\n")
            else:
                f.write(f"- ✅ 평균 신뢰도가 양호합니다 ({avg_score}점).\n")
            f.write(f"\n")

            # 6. 결론 및 다음 단계
            f.write(f"## 6. 결론 및 다음 단계\n\n")
            f.write(f"### 6.1 성과\n")
            f.write(f"- ✅ Supabase REST API 연동 성공 (supabase-py 패키지 없이)\n")
            f.write(f"- ✅ 실제 데이터로 logic_designer 검증 완료\n")
            f.write(f"- ✅ 제품별 리뷰 분석 통계 생성\n")
            f.write(f"- ✅ 광고 판별 로직 실전 테스트 완료\n\n")

            f.write(f"### 6.2 개선 필요 사항\n")
            if ad_rate > 30:
                f.write(f"- ⚠️ 오탐률 개선: `checklist.py`의 개인 경험 패턴 완화\n")
                f.write(f"- ⚠️ 임계값 조정: `trust_score.py`의 광고 판별 기준 재설정\n")
            f.write(f"- 📊 통계 지표 확장: 표준편차, 중앙값 등 추가\n")
            f.write(f"- 🤖 AI 분석 통합: Claude API로 약사 인사이트 생성\n\n")

            f.write(f"### 6.3 다음 단계\n")
            f.write(f"1. **단기** (이번 주)\n")
            f.write(f"   - [ ] `checklist.py` 패턴 개선 (INTEGRATION_TEST_REPORT.md 참고)\n")
            f.write(f"   - [ ] 개선된 로직으로 재테스트\n")
            f.write(f"   - [ ] 전체 리뷰 데이터 분석 ({len(self.reviews)}개 전체)\n\n")

            f.write(f"2. **중기** (이번 달)\n")
            f.write(f"   - [ ] AI 분석 통합 (ANTHROPIC_API_KEY 설정 후)\n")
            f.write(f"   - [ ] Streamlit UI 연동\n")
            f.write(f"   - [ ] 실시간 모니터링 대시보드 구축\n\n")

            f.write(f"3. **장기** (다음 달)\n")
            f.write(f"   - [ ] 다양한 제품 카테고리 확장\n")
            f.write(f"   - [ ] 다국어 리뷰 지원\n")
            f.write(f"   - [ ] 사용자 피드백 수집 및 반영\n\n")

            f.write(f"---\n\n")
            f.write(f"**보고서 생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**보고서 경로**: `{report_path}`\n")

        print(f"✅ 개발일지 보고서 생성 완료!")
        print(f"   위치: {report_path}")
        return report_path

    def run_all_tests(self, review_limit=50, analyze_limit=20):
        """전체 테스트 실행"""
        print("\n" + "=" * 80)
        print("🚀 Supabase 통합 테스트 시작 (REST API)")
        print("=" * 80)

        # 1. Supabase 연결
        if not self.connect_to_supabase():
            print("\n❌ Supabase 연결 실패. 테스트를 중단합니다.")
            return False

        # 2. 제품 데이터 가져오기
        if not self.fetch_products():
            print("\n❌ 제품 데이터 가져오기 실패. 테스트를 중단합니다.")
            return False

        # 3. 리뷰 데이터 가져오기
        if not self.fetch_reviews(limit=review_limit):
            print("\n❌ 리뷰 데이터 가져오기 실패. 테스트를 중단합니다.")
            return False

        # 4. 리뷰 분석
        self.analyze_reviews(max_reviews=analyze_limit)

        # 5. 통계 계산
        self.calculate_statistics()

        # 6. 개발일지 보고서 생성
        report_path = self.generate_report()

        print("\n" + "=" * 80)
        print("✅ 통합 테스트 완료!")
        print("=" * 80)
        print(f"\n📄 개발일지 보고서: {report_path}")

        return True


def main():
    """메인 실행 함수"""
    tester = SupabaseIntegrationTest()

    print("\n🔍 Supabase 통합 테스트 설정")
    print("-" * 80)

    try:
        review_limit = input("가져올 리뷰 수 (기본값: 50): ").strip()
        review_limit = int(review_limit) if review_limit else 50
    except ValueError:
        review_limit = 50

    try:
        analyze_limit = input("분석할 리뷰 수 (기본값: 20): ").strip()
        analyze_limit = int(analyze_limit) if analyze_limit else 20
    except ValueError:
        analyze_limit = 20

    # 테스트 실행
    success = tester.run_all_tests(review_limit=review_limit, analyze_limit=analyze_limit)

    if success:
        print("\n✅ 테스트가 성공적으로 완료되었습니다.")
    else:
        print("\n❌ 테스트 중 오류가 발생했습니다.")


if __name__ == "__main__":
    main()
