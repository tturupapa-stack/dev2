"""
개선된 checklist.py 테스트
개선 전후 비교 테스트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'database'))

from mock_data import NORMAL_REVIEW_TEMPLATES, AD_REVIEW_TEMPLATES
from logic_designer import analyze


def test_improvements():
    """개선된 로직 테스트"""
    print("\n" + "=" * 80)
    print("🔍 개선된 checklist.py 테스트")
    print("=" * 80)

    # 테스트 케이스
    test_cases = [
        {
            "title": "정상 리뷰 1 (재구매 표현)",
            "text": "재구매 했어요\n두번째 구매입니다. 효과가 있는지는 모르겠지만 눈 건강을 위해 계속 먹으려고 합니다.",
            "expected": "정상"
        },
        {
            "title": "정상 리뷰 2 (사용 표현)",
            "text": "눈의 피로가 줄었어요\n하루종일 모니터 보는 일을 하는데, 먹고나서 눈이 좀 덜 빡빡한 느낌이에요.",
            "expected": "정상"
        },
        {
            "title": "정상 리뷰 3 (구매 표현)",
            "text": "가격 대비 괜찮습니다\n루테인 함량도 적당하고 가격도 합리적이어서 좋습니다. 캡슐 크기도 삼키기 편해요.",
            "expected": "정상"
        },
        {
            "title": "광고 리뷰 1 (감탄사 남발)",
            "text": "최고의 루테인! 강력 추천합니다!!!\n와 진짜 대박이에요!!! 먹자마자 바로 효과 느꼈어요!!",
            "expected": "광고"
        },
        {
            "title": "광고 리뷰 2 (비현실적 효과)",
            "text": "눈 건강의 혁명!\n단 3일만에 눈이 확 좋아졌습니다! 안경을 벗을 수 있게 되었어요!",
            "expected": "광고"
        }
    ]

    results = {
        "total": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "details": []
    }

    for idx, case in enumerate(test_cases, 1):
        print(f"\n[{idx}/{len(test_cases)}] {case['title']}")
        print(f"  기대 결과: {case['expected']}")

        try:
            result = analyze(
                review_text=case['text'],
                length_score=70,
                repurchase_score=60,
                monthly_use_score=60,
                photo_score=0,
                consistency_score=70,
                api_key=None
            )

            validation = result['validation']
            is_ad = validation['is_ad']
            actual_result = "광고" if is_ad else "정상"

            print(f"  실제 결과: {actual_result}")
            print(f"  신뢰도 점수: {validation['trust_score']}")
            print(f"  감점 항목: {validation['detected_count']}개")
            if validation['reasons']:
                print(f"  감점 사유: {', '.join(validation['reasons'][:3])}")

            # 결과 비교
            is_correct = (case['expected'] == actual_result)
            if is_correct:
                print(f"  ✅ 정답!")
                results['correct'] += 1
            else:
                print(f"  ❌ 오답!")
                results['incorrect'] += 1

            results['details'].append({
                'case': case['title'],
                'expected': case['expected'],
                'actual': actual_result,
                'correct': is_correct,
                'trust_score': validation['trust_score'],
                'penalty_count': validation['detected_count']
            })

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            results['incorrect'] += 1

    # 통계 출력
    print("\n" + "=" * 80)
    print("📊 테스트 결과")
    print("=" * 80)
    print(f"  - 총 테스트: {results['total']}개")
    print(f"  - 정답: {results['correct']}개")
    print(f"  - 오답: {results['incorrect']}개")
    print(f"  - 정확도: {results['correct'] / results['total'] * 100:.1f}%")

    print("\n📋 상세 결과:")
    for detail in results['details']:
        status = "✅" if detail['correct'] else "❌"
        print(f"  {status} {detail['case']}: {detail['expected']} → {detail['actual']} (신뢰도: {detail['trust_score']})")

    return results


def compare_with_mock_data():
    """목업 데이터로 개선 전후 비교"""
    print("\n" + "=" * 80)
    print("🔄 목업 데이터 테스트 (정상 리뷰 샘플)")
    print("=" * 80)

    # 정상 리뷰 5개만 테스트
    sample_reviews = NORMAL_REVIEW_TEMPLATES[:5]

    stats = {
        "total": len(sample_reviews),
        "detected_as_normal": 0,
        "detected_as_ad": 0,
        "avg_trust_score": 0,
        "avg_penalty_count": 0
    }

    trust_scores = []
    penalty_counts = []

    for idx, template in enumerate(sample_reviews, 1):
        review_text = f"{template['title']}\n{template['body']}"

        result = analyze(
            review_text=review_text,
            length_score=70,
            repurchase_score=60,
            monthly_use_score=60,
            photo_score=0,
            consistency_score=70,
            api_key=None
        )

        validation = result['validation']
        is_ad = validation['is_ad']

        if is_ad:
            stats['detected_as_ad'] += 1
        else:
            stats['detected_as_normal'] += 1

        trust_scores.append(validation['trust_score'])
        penalty_counts.append(validation['detected_count'])

        print(f"\n[{idx}/{len(sample_reviews)}] {template['title'][:30]}...")
        print(f"  판별: {'❌ 광고' if is_ad else '✅ 정상'}")
        print(f"  신뢰도: {validation['trust_score']}")
        print(f"  감점: {validation['detected_count']}개")

    stats['avg_trust_score'] = sum(trust_scores) / len(trust_scores)
    stats['avg_penalty_count'] = sum(penalty_counts) / len(penalty_counts)

    print("\n" + "=" * 80)
    print("📊 목업 데이터 테스트 통계")
    print("=" * 80)
    print(f"  - 총 리뷰: {stats['total']}개")
    print(f"  - 정상 판별: {stats['detected_as_normal']}개 ({stats['detected_as_normal'] / stats['total'] * 100:.1f}%)")
    print(f"  - 광고 판별: {stats['detected_as_ad']}개 ({stats['detected_as_ad'] / stats['total'] * 100:.1f}%)")
    print(f"  - 평균 신뢰도: {stats['avg_trust_score']:.2f}")
    print(f"  - 평균 감점 항목: {stats['avg_penalty_count']:.2f}개")

    print("\n💡 개선 목표:")
    print(f"  - 오탐률(정상→광고): {'✅ 개선' if stats['detected_as_ad'] < 2 else '⚠️ 추가 개선 필요'}")
    print(f"  - 평균 신뢰도: {'✅ 목표 달성' if stats['avg_trust_score'] >= 50 else '⚠️ 추가 개선 필요'}")

    return stats


def main():
    """메인 실행"""
    print("\n" + "=" * 80)
    print("🚀 checklist.py 개선 검증 테스트")
    print("=" * 80)
    print("\n개선 사항:")
    print("  1. 개인 경험 패턴 확장: 구매, 먹, 사용, 복용, 재구매 등")
    print("  2. 단점 회피 완화: 다른 광고 패턴과 함께 있을 때만 감점")
    print("  3. 키워드 반복 임계값: 5 → 7로 완화")

    # 1. 개선 사항 테스트
    test_results = test_improvements()

    # 2. 목업 데이터 테스트
    mock_results = compare_with_mock_data()

    # 3. 최종 평가
    print("\n" + "=" * 80)
    print("✅ 최종 평가")
    print("=" * 80)

    if test_results['correct'] >= 4:
        print("  ✅ 개선 로직이 정상적으로 작동합니다.")
    else:
        print("  ⚠️ 추가 조정이 필요할 수 있습니다.")

    if mock_results['avg_trust_score'] >= 50:
        print("  ✅ 평균 신뢰도 목표 달성!")
    else:
        print(f"  ⚠️ 평균 신뢰도 {mock_results['avg_trust_score']:.2f} (목표: 50 이상)")

    if mock_results['detected_as_ad'] / mock_results['total'] <= 0.2:
        print("  ✅ 정상 리뷰 오탐률 개선 성공!")
    else:
        print(f"  ⚠️ 오탐률 {mock_results['detected_as_ad'] / mock_results['total'] * 100:.1f}% (목표: 20% 이하)")


if __name__ == "__main__":
    main()
