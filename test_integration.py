"""
통합 테스트: database (data_manager) + logic_designer
mock_data를 사용하여 logic_designer의 분석 기능을 테스트합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'database'))

# 직접 import (database.__init__ 문제 우회)
from mock_data import NORMAL_REVIEW_TEMPLATES, AD_REVIEW_TEMPLATES

from logic_designer import analyze
from logic_designer.checklist import AdChecklist
from logic_designer.trust_score import TrustScoreCalculator


class IntegrationTestRunner:
    """통합 테스트 실행 클래스"""

    def __init__(self):
        self.results = {
            "normal_reviews": [],
            "ad_reviews": [],
            "statistics": {}
        }

    def test_normal_reviews(self):
        """정상 리뷰 테스트"""
        print("\n" + "=" * 80)
        print("📝 정상 리뷰 테스트 시작")
        print("=" * 80)

        for idx, template in enumerate(NORMAL_REVIEW_TEMPLATES, 1):
            review_text = f"{template['title']}\n{template['body']}"

            try:
                # analyze() 함수로 분석 (AI 분석 제외)
                result = analyze(
                    review_text=review_text,
                    length_score=70,  # 정상 리뷰는 적당한 길이
                    repurchase_score=60,
                    monthly_use_score=60,
                    photo_score=0,
                    consistency_score=70,
                    api_key=None  # AI 분석 생략 (비용 절약)
                )

                self.results["normal_reviews"].append({
                    "index": idx,
                    "title": template['title'],
                    "result": result
                })

                validation = result['validation']
                print(f"\n[{idx}/{len(NORMAL_REVIEW_TEMPLATES)}] {template['title'][:40]}")
                print(f"  - 신뢰도 점수: {validation['trust_score']}")
                print(f"  - 광고 여부: {'❌ 광고' if validation['is_ad'] else '✅ 정상'}")
                print(f"  - 감점 항목: {validation['detected_count']}개")
                if validation['reasons']:
                    print(f"  - 감점 사유: {', '.join(validation['reasons'][:3])}")

            except Exception as e:
                print(f"\n[{idx}] ❌ 오류 발생: {e}")

    def test_ad_reviews(self):
        """광고성 리뷰 테스트"""
        print("\n" + "=" * 80)
        print("🚨 광고성 리뷰 테스트 시작")
        print("=" * 80)

        for idx, template in enumerate(AD_REVIEW_TEMPLATES, 1):
            review_text = f"{template['title']}\n{template['body']}"

            try:
                # analyze() 함수로 분석
                result = analyze(
                    review_text=review_text,
                    length_score=80,  # 광고성 리뷰는 길이가 길 수 있음
                    repurchase_score=50,
                    monthly_use_score=40,  # 광고는 한달 사용 언급 적음
                    photo_score=20,
                    consistency_score=40,
                    api_key=None  # AI 분석 생략
                )

                self.results["ad_reviews"].append({
                    "index": idx,
                    "title": template['title'],
                    "result": result
                })

                validation = result['validation']
                print(f"\n[{idx}/{len(AD_REVIEW_TEMPLATES)}] {template['title'][:40]}")
                print(f"  - 신뢰도 점수: {validation['trust_score']}")
                print(f"  - 광고 여부: {'✅ 광고 탐지' if validation['is_ad'] else '❌ 미탐지'}")
                print(f"  - 감점 항목: {validation['detected_count']}개")
                if validation['reasons']:
                    print(f"  - 감점 사유: {', '.join(validation['reasons'][:3])}")

            except Exception as e:
                print(f"\n[{idx}] ❌ 오류 발생: {e}")

    def calculate_statistics(self):
        """통계 계산"""
        print("\n" + "=" * 80)
        print("📊 통계 분석")
        print("=" * 80)

        # 정상 리뷰 통계
        normal_trust_scores = [r['result']['validation']['trust_score']
                               for r in self.results['normal_reviews']]
        normal_ad_count = sum(1 for r in self.results['normal_reviews']
                              if r['result']['validation']['is_ad'])
        normal_penalty_counts = [r['result']['validation']['detected_count']
                                 for r in self.results['normal_reviews']]

        # 광고성 리뷰 통계
        ad_trust_scores = [r['result']['validation']['trust_score']
                           for r in self.results['ad_reviews']]
        ad_detected_count = sum(1 for r in self.results['ad_reviews']
                                if r['result']['validation']['is_ad'])
        ad_penalty_counts = [r['result']['validation']['detected_count']
                             for r in self.results['ad_reviews']]

        # 통계 저장
        self.results['statistics'] = {
            "normal_reviews": {
                "count": len(normal_trust_scores),
                "avg_trust_score": round(sum(normal_trust_scores) / len(normal_trust_scores), 2) if normal_trust_scores else 0,
                "min_trust_score": min(normal_trust_scores) if normal_trust_scores else 0,
                "max_trust_score": max(normal_trust_scores) if normal_trust_scores else 0,
                "false_positive_rate": round(normal_ad_count / len(self.results['normal_reviews']) * 100, 2) if self.results['normal_reviews'] else 0,
                "avg_penalty_count": round(sum(normal_penalty_counts) / len(normal_penalty_counts), 2) if normal_penalty_counts else 0
            },
            "ad_reviews": {
                "count": len(ad_trust_scores),
                "avg_trust_score": round(sum(ad_trust_scores) / len(ad_trust_scores), 2) if ad_trust_scores else 0,
                "min_trust_score": min(ad_trust_scores) if ad_trust_scores else 0,
                "max_trust_score": max(ad_trust_scores) if ad_trust_scores else 0,
                "detection_rate": round(ad_detected_count / len(self.results['ad_reviews']) * 100, 2) if self.results['ad_reviews'] else 0,
                "avg_penalty_count": round(sum(ad_penalty_counts) / len(ad_penalty_counts), 2) if ad_penalty_counts else 0
            }
        }

        # 통계 출력
        print("\n✅ 정상 리뷰 분석 결과:")
        print(f"  - 총 리뷰 수: {self.results['statistics']['normal_reviews']['count']}개")
        print(f"  - 평균 신뢰도 점수: {self.results['statistics']['normal_reviews']['avg_trust_score']}")
        print(f"  - 신뢰도 범위: {self.results['statistics']['normal_reviews']['min_trust_score']} ~ {self.results['statistics']['normal_reviews']['max_trust_score']}")
        print(f"  - 오탐률 (False Positive): {self.results['statistics']['normal_reviews']['false_positive_rate']}%")
        print(f"  - 평균 감점 항목: {self.results['statistics']['normal_reviews']['avg_penalty_count']}개")

        print("\n🚨 광고성 리뷰 분석 결과:")
        print(f"  - 총 리뷰 수: {self.results['statistics']['ad_reviews']['count']}개")
        print(f"  - 평균 신뢰도 점수: {self.results['statistics']['ad_reviews']['avg_trust_score']}")
        print(f"  - 신뢰도 범위: {self.results['statistics']['ad_reviews']['min_trust_score']} ~ {self.results['statistics']['ad_reviews']['max_trust_score']}")
        print(f"  - 탐지율 (Detection Rate): {self.results['statistics']['ad_reviews']['detection_rate']}%")
        print(f"  - 평균 감점 항목: {self.results['statistics']['ad_reviews']['avg_penalty_count']}개")

        # 전체 정확도
        total_reviews = len(self.results['normal_reviews']) + len(self.results['ad_reviews'])
        correct_predictions = (len(self.results['normal_reviews']) - normal_ad_count) + ad_detected_count
        accuracy = round(correct_predictions / total_reviews * 100, 2) if total_reviews else 0

        print(f"\n🎯 전체 정확도: {accuracy}% ({correct_predictions}/{total_reviews})")

    def test_with_ai_analysis(self):
        """AI 분석 샘플 테스트 (선택적)"""
        print("\n" + "=" * 80)
        print("🤖 AI 분석 샘플 테스트 (선택)")
        print("=" * 80)

        # ANTHROPIC_API_KEY 확인
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "sk-ant-your-api-key-here":
            print("  ⚠️  ANTHROPIC_API_KEY가 설정되지 않아 AI 분석을 건너뜁니다.")
            print("  💡 AI 분석을 테스트하려면 .env 파일에 유효한 API 키를 설정하세요.")
            return

        # 정상 리뷰 1개만 샘플 테스트
        sample_review = NORMAL_REVIEW_TEMPLATES[0]
        review_text = f"{sample_review['title']}\n{sample_review['body']}"

        print(f"\n샘플 리뷰: {sample_review['title']}")
        print(f"내용: {sample_review['body'][:60]}...")

        try:
            result = analyze(
                review_text=review_text,
                length_score=70,
                repurchase_score=60,
                monthly_use_score=60,
                photo_score=0,
                consistency_score=70,
                api_key=api_key
            )

            if result['analysis'] and 'summary' in result['analysis']:
                print("\n✅ AI 분석 결과:")
                print(f"  - 요약: {result['analysis']['summary']}")
                print(f"  - 효능: {result['analysis']['efficacy']}")
                print(f"  - 부작용: {result['analysis']['side_effects']}")
                print(f"  - 약사 조언: {result['analysis']['tip']}")
            else:
                print("\n  ⚠️  AI 분석 결과가 없습니다.")

        except Exception as e:
            print(f"\n  ❌ AI 분석 오류: {e}")

    def run_all_tests(self, include_ai: bool = False):
        """모든 테스트 실행"""
        print("\n" + "=" * 80)
        print("🚀 통합 테스트 시작: database (data_manager) + logic_designer")
        print("=" * 80)

        # 1. 정상 리뷰 테스트
        self.test_normal_reviews()

        # 2. 광고성 리뷰 테스트
        self.test_ad_reviews()

        # 3. 통계 계산
        self.calculate_statistics()

        # 4. AI 분석 샘플 테스트 (선택)
        if include_ai:
            self.test_with_ai_analysis()

        print("\n" + "=" * 80)
        print("✅ 통합 테스트 완료!")
        print("=" * 80)


def main():
    """메인 실행 함수"""
    runner = IntegrationTestRunner()

    # AI 분석 포함 여부 확인
    print("\n🤖 AI 분석을 포함하시겠습니까?")
    print("   (API 비용이 발생할 수 있습니다. 1개 샘플만 테스트합니다.)")
    response = input("   AI 분석 포함 (y/N): ")

    include_ai = response.lower() == 'y'

    # 모든 테스트 실행
    runner.run_all_tests(include_ai=include_ai)


if __name__ == "__main__":
    main()
