"""
rating_analyzer.py 테스트 스크립트
"""

import sys
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from logic_designer.rating_analyzer import RatingAnalyzer, analyze_rating


def test_case_1_normal_review():
    """테스트 케이스 1: 정상 리뷰 (평균과 일치)"""
    print("=" * 80)
    print("테스트 1: 정상 리뷰 (평균과 일치)")
    print("=" * 80)

    analyzer = RatingAnalyzer()

    review_rating = 4
    product_rating_avg = 4.5
    product_rating_count = 1234

    result = analyze_rating(review_rating, product_rating_avg, product_rating_count)

    print(f"리뷰 평점: {review_rating}점")
    print(f"제품 평균: {product_rating_avg}점")
    print(f"평점 개수: {product_rating_count}개")
    print(f"\n평점 신뢰도 점수: {result['rating_reliability_score']}/100")
    print(f"평점 패턴: {result['pattern']}")
    print(f"신뢰도 레벨: {result['insight']['reliability_level']}")
    print(f"메시지: {result['insight']['message']}")
    print(f"권장 사항: {result['insight']['recommendation']}")

    assert result['rating_reliability_score'] >= 70, "정상 리뷰는 70점 이상이어야 함"
    print("\n✅ 테스트 통과!")


def test_case_2_ad_review():
    """테스트 케이스 2: 광고 리뷰 (5점 만점 + 평균과 큰 차이)"""
    print("\n" + "=" * 80)
    print("테스트 2: 광고 리뷰 (5점 만점, 평균 3.5)")
    print("=" * 80)

    # 더 극단적인 광고 리뷰: 5점인데 평균은 3.5
    review_rating = 5
    product_rating_avg = 3.5
    product_rating_count = 500

    result = analyze_rating(review_rating, product_rating_avg, product_rating_count)

    print(f"리뷰 평점: {review_rating}점")
    print(f"제품 평균: {product_rating_avg}점")
    print(f"평점 개수: {product_rating_count}개")
    print(f"\n평점 신뢰도 점수: {result['rating_reliability_score']}/100")
    print(f"평점 패턴: {result['pattern']}")
    print(f"신뢰도 레벨: {result['insight']['reliability_level']}")
    print(f"메시지: {result['insight']['message']}")
    print(f"권장 사항: {result['insight']['recommendation']}")

    assert result['rating_reliability_score'] < 50, f"광고 리뷰는 50점 미만이어야 함 (실제: {result['rating_reliability_score']})"
    assert result['pattern'] in ['extreme_positive', 'suspicious_high'], "5점은 극단 패턴"
    print("\n✅ 테스트 통과!")


def test_case_3_malicious_review():
    """테스트 케이스 3: 악의적 리뷰 (1점 + 평균과 큰 차이)"""
    print("\n" + "=" * 80)
    print("테스트 3: 악의적 리뷰 (1점)")
    print("=" * 80)

    review_rating = 1
    product_rating_avg = 4.7
    product_rating_count = 2000

    result = analyze_rating(review_rating, product_rating_avg, product_rating_count)

    print(f"리뷰 평점: {review_rating}점")
    print(f"제품 평균: {product_rating_avg}점")
    print(f"평점 개수: {product_rating_count}개")
    print(f"\n평점 신뢰도 점수: {result['rating_reliability_score']}/100")
    print(f"평점 패턴: {result['pattern']}")
    print(f"신뢰도 레벨: {result['insight']['reliability_level']}")
    print(f"메시지: {result['insight']['message']}")
    print(f"권장 사항: {result['insight']['recommendation']}")

    assert result['rating_reliability_score'] < 30, "악의적 리뷰는 30점 미만이어야 함"
    assert 'suspicious' in result['pattern'] or 'extreme' in result['pattern'], "1점은 극단 패턴"
    print("\n✅ 테스트 통과!")


def test_case_4_manipulation_detection():
    """테스트 케이스 4: 평점 조작 탐지"""
    print("\n" + "=" * 80)
    print("테스트 4: 평점 조작 탐지")
    print("=" * 80)

    analyzer = RatingAnalyzer()

    # 시나리오 1: 5점 + 낮은 신뢰도
    review_rating = 5
    product_rating_avg = 3.5
    rating_reliability_score = 25
    detected_issues = {2: "감탄사 남발", 8: "찬사 위주 구성"}

    is_manipulation = analyzer.detect_rating_manipulation(
        review_rating,
        product_rating_avg,
        rating_reliability_score,
        detected_issues
    )

    print(f"리뷰 평점: {review_rating}점")
    print(f"제품 평균: {product_rating_avg}점")
    print(f"평점 신뢰도: {rating_reliability_score}")
    print(f"감지된 이슈: {detected_issues}")
    print(f"\n평점 조작 여부: {is_manipulation}")

    assert is_manipulation, "5점 + 낮은 신뢰도 + 감탄사는 조작으로 판별되어야 함"
    print("\n✅ 테스트 통과!")


def test_case_5_null_handling():
    """테스트 케이스 5: NULL 값 처리"""
    print("\n" + "=" * 80)
    print("테스트 5: NULL 값 처리")
    print("=" * 80)

    # NULL 값
    result = analyze_rating(None, None, None)

    print(f"리뷰 평점: None")
    print(f"제품 평균: None")
    print(f"평점 개수: None")
    print(f"\n평점 신뢰도 점수: {result['rating_reliability_score']}/100")
    print(f"평점 패턴: {result['pattern']}")
    print(f"메시지: {result['insight']['message']}")

    assert result['rating_reliability_score'] == 50.0, "NULL은 중립 점수 50점"
    assert result['pattern'] == 'unknown', "NULL은 unknown 패턴"
    print("\n✅ 테스트 통과!")


def test_case_6_edge_cases():
    """테스트 케이스 6: 경계값 테스트"""
    print("\n" + "=" * 80)
    print("테스트 6: 경계값 테스트")
    print("=" * 80)

    analyzer = RatingAnalyzer()

    # 6-1: 평점 개수 매우 적음
    print("\n[6-1] 평점 개수 5개 (매우 적음)")
    result = analyze_rating(4, 4.5, 5)
    print(f"  평점 신뢰도: {result['rating_reliability_score']}/100")
    print(f"  (평점 개수가 적어도 평점 일치도가 높으면 70점 이상 가능)")
    assert result['rating_reliability_score'] < 100, "최대 100점 미만"

    # 6-2: 평점 개수 매우 많음
    print("\n[6-2] 평점 개수 5000개 (매우 많음)")
    result = analyze_rating(4, 4.5, 5000)
    print(f"  평점 신뢰도: {result['rating_reliability_score']}/100")
    assert result['rating_reliability_score'] >= 80, "평점 개수 많으면 신뢰도 높아야 함"

    # 6-3: 평점 완전 일치
    print("\n[6-3] 평점 완전 일치 (4 vs 4.0)")
    result = analyze_rating(4, 4.0, 1000)
    print(f"  평점 신뢰도: {result['rating_reliability_score']}/100")
    assert result['rating_reliability_score'] >= 90, "완전 일치는 매우 높은 신뢰도"

    print("\n✅ 모든 경계값 테스트 통과!")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 80)
    print("🧪 rating_analyzer.py 테스트 시작")
    print("=" * 80)

    try:
        test_case_1_normal_review()
        test_case_2_ad_review()
        test_case_3_malicious_review()
        test_case_4_manipulation_detection()
        test_case_5_null_handling()
        test_case_6_edge_cases()

        print("\n" + "=" * 80)
        print("✅ 모든 테스트 통과!")
        print("=" * 80)

    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return False

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
