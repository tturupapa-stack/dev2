# logic_designer 개선안: rating_avg/rating_count 활용

**작성일**: 2026-01-05
**작성자**: Logic Designer
**목적**: Supabase DB의 평점 데이터를 활용한 리뷰 신뢰도 분석 강화

---

## 현재 상황 분석

### Supabase DB 구조 (DB 담당자 설계)

**products 테이블**:
```sql
- rating_avg (NUMERIC)      -- 제품 평균 평점 (1.0~5.0)
- rating_count (INT)         -- 총 평점 개수 (리뷰 수)
```

**reviews 테이블**:
```sql
- rating (INT)               -- 개별 리뷰 평점 (1~5)
- product_id (BIGINT FK)     -- 제품 외래키
```

### 현재 logic_designer 신뢰도 계산 공식

**trust_score.py (line 27-45)**:
```python
S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2) - (penalty × 10)
```

**가중치**:
- L (Length): 리뷰 길이 - 20%
- R (Repurchase): 재구매 여부 - 20%
- M (Monthly Use): 한달 사용 - 30%
- P (Photo): 사진 첨부 - 10%
- C (Consistency): 내용 일치도 - 20%
- Penalty: 13단계 체크리스트 감점

**문제점**:
- ❌ 평점 정보를 전혀 활용하지 않음
- ❌ 제품 평균 평점과 개별 리뷰 평점의 괴리 미탐지
- ❌ 극단적 평점(1점, 5점)의 신뢰도 평가 부재
- ❌ 평점 조작 패턴 탐지 불가

---

## 개선 제안

### 1. 평점 신뢰도 점수 (Rating Reliability Score) 추가

#### 1.1 개별 리뷰 평점 분석

**새로운 파라미터**: `rating_reliability_score` (0-100)

**계산 로직**:
```python
def calculate_rating_reliability(
    review_rating: int,           # 개별 리뷰 평점 (1-5)
    product_rating_avg: float,    # 제품 평균 평점 (1.0-5.0)
    product_rating_count: int     # 총 평점 개수
) -> float:
    """
    평점 신뢰도 점수 계산

    반환값: 0-100 점수
    """
```

**세부 로직**:

1. **평점 차이 분석** (60점 만점)
   ```python
   diff = abs(review_rating - product_rating_avg)

   if diff <= 0.5:
       deviation_score = 60  # 평균과 거의 일치 (신뢰도 높음)
   elif diff <= 1.0:
       deviation_score = 50  # 약간 차이 (보통)
   elif diff <= 1.5:
       deviation_score = 35  # 중간 차이 (의심)
   elif diff <= 2.0:
       deviation_score = 20  # 큰 차이 (광고 의심)
   else:
       deviation_score = 0   # 극단적 차이 (광고 확률 높음)
   ```

2. **극단 평점 패널티** (20점 만점)
   ```python
   # 5점 리뷰: 광고성 의심
   if review_rating == 5:
       extremity_score = 10  # 패널티
   # 1점 리뷰: 악의적 비방 의심
   elif review_rating == 1:
       extremity_score = 10
   # 2-4점: 신뢰도 높음
   else:
       extremity_score = 20
   ```

3. **평점 개수 가중치** (20점 만점)
   ```python
   # 평점 개수가 많을수록 평균이 신뢰할 수 있음
   if product_rating_count >= 1000:
       count_weight = 20  # 매우 신뢰
   elif product_rating_count >= 500:
       count_weight = 18
   elif product_rating_count >= 100:
       count_weight = 15
   elif product_rating_count >= 50:
       count_weight = 12
   elif product_rating_count >= 10:
       count_weight = 8
   else:
       count_weight = 5   # 평점 부족 (신뢰도 낮음)
   ```

**최종 평점 신뢰도**:
```python
rating_reliability_score = deviation_score + extremity_score + count_weight
# 0-100 범위
```

#### 1.2 신뢰도 계산 공식 개선

**기존 (5개 요소)**:
```python
S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)
```

**개선안 (6개 요소)**:
```python
S = (L × 0.15) + (R × 0.15) + (M × 0.25) + (P × 0.08) + (C × 0.17) + (RR × 0.20)
```

**새로운 가중치**:
- L (Length): 15% (↓ 5%p)
- R (Repurchase): 15% (↓ 5%p)
- M (Monthly Use): 25% (↓ 5%p)
- P (Photo): 8% (↓ 2%p)
- C (Consistency): 17% (↓ 3%p)
- **RR (Rating Reliability): 20% (NEW)** ← DB 평점 데이터 활용

**근거**:
- 평점은 객관적 지표이므로 20% 가중치 부여
- 기존 요소들의 가중치를 균등하게 감소시켜 총합 100% 유지

---

### 2. 광고 판별 로직 강화

#### 2.1 현재 광고 판별 기준

**trust_score.py (line 120-133)**:
```python
def is_ad(final_score: float, penalty_count: int, threshold: float = 40) -> bool:
    return final_score < 40 or penalty_count >= 3
```

#### 2.2 개선안: 평점 패턴 기반 추가 판별

**새로운 광고 패턴**:

1. **5점 만점 + 낮은 신뢰도**
   ```python
   if review_rating == 5 and rating_reliability_score < 30:
       ad_flag = True  # "5점 폭격" 광고 의심
   ```

2. **평점 차이 극단**
   ```python
   if abs(review_rating - product_rating_avg) > 2.0:
       ad_flag = True  # 평점 조작 의심
   ```

3. **평점 + 체크리스트 복합 판별**
   ```python
   # 5점 + 감탄사 남발 + 찬사 위주
   if (review_rating == 5 and
       penalty_count >= 2 and
       "감탄사 남발" in detected_issues):
       ad_flag = True
   ```

**최종 광고 판별 로직**:
```python
def is_ad_v2(
    final_score: float,
    penalty_count: int,
    review_rating: int,
    rating_reliability_score: float,
    detected_issues: dict
) -> bool:
    """
    개선된 광고 판별 로직
    """
    # 기존 조건
    if final_score < 40 or penalty_count >= 3:
        return True

    # 평점 기반 추가 조건
    if review_rating == 5 and rating_reliability_score < 30:
        return True

    # 평점 차이 극단
    if rating_reliability_score < 20:
        return True

    # 복합 패턴 (5점 + 감탄사 + 찬사)
    if (review_rating == 5 and
        penalty_count >= 2 and
        (2 in detected_issues or 8 in detected_issues)):
        return True

    return False
```

---

### 3. 구현 계획

#### 3.1 새로운 파일: `rating_analyzer.py`

**위치**: `logic_designer/rating_analyzer.py`

**클래스**: `RatingAnalyzer`

**주요 메서드**:
```python
class RatingAnalyzer:
    """평점 기반 신뢰도 분석"""

    def calculate_rating_reliability(
        self,
        review_rating: int,
        product_rating_avg: float,
        product_rating_count: int
    ) -> float:
        """평점 신뢰도 점수 계산 (0-100)"""
        pass

    def detect_rating_manipulation(
        self,
        review_rating: int,
        product_rating_avg: float,
        detected_issues: dict
    ) -> bool:
        """평점 조작 패턴 탐지"""
        pass

    def get_rating_pattern_type(
        self,
        review_rating: int,
        product_rating_avg: float
    ) -> str:
        """평점 패턴 분류: normal/extreme_positive/extreme_negative/suspicious"""
        pass
```

#### 3.2 `trust_score.py` 수정

**변경 사항**:
1. `calculate_final_score()` 메서드에 `rating_reliability_score` 파라미터 추가
2. 가중치 재조정 (6개 요소)
3. `is_ad()` 메서드 → `is_ad_v2()` 업그레이드

**하위 호환성**:
- 기존 `calculate_final_score()`는 유지
- 새로운 `calculate_final_score_v2()` 추가
- 점진적 마이그레이션 가능

#### 3.3 `__init__.py` 통합

**변경 사항**:
```python
from .rating_analyzer import RatingAnalyzer

def analyze_v2(
    review_text: str,
    review_rating: int,              # NEW
    product_rating_avg: float,       # NEW
    product_rating_count: int,       # NEW
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    api_key: Optional[str] = None
) -> Dict:
    """
    개선된 리뷰 종합 분석 (평점 데이터 포함)
    """
    # 1. 평점 신뢰도 분석
    rating_analyzer = RatingAnalyzer()
    rating_reliability_score = rating_analyzer.calculate_rating_reliability(
        review_rating,
        product_rating_avg,
        product_rating_count
    )

    # 2. 체크리스트 검사
    checklist = AdChecklist()
    detected_issues = checklist.check_ad_patterns(review_text)

    # 3. 신뢰도 점수 (v2)
    calculator = TrustScoreCalculator()
    score_result = calculator.calculate_final_score_v2(
        length_score,
        repurchase_score,
        monthly_use_score,
        photo_score,
        consistency_score,
        rating_reliability_score,  # NEW
        penalty_count=len(detected_issues)
    )

    # 4. 광고 판별 (v2)
    is_ad = calculator.is_ad_v2(
        score_result["final_score"],
        len(detected_issues),
        review_rating,
        rating_reliability_score,
        detected_issues
    )

    # ... (AI 분석 동일)

    return {
        "validation": {
            "trust_score": score_result["final_score"],
            "rating_reliability_score": rating_reliability_score,  # NEW
            "is_ad": is_ad,
            # ...
        },
        "analysis": analysis_result
    }
```

---

### 4. Supabase 연동 예시

#### 4.1 제품 + 리뷰 데이터 조회

```python
from database import get_supabase_client
from logic_designer import analyze_v2

# Supabase 클라이언트
supabase = get_supabase_client()

# 제품 정보와 리뷰 조인 조회
result = supabase.table('reviews')\
    .select('*, products(rating_avg, rating_count)')\
    .eq('id', 1)\
    .single()\
    .execute()

review = result.data
product = review['products']

# 개선된 분석 (평점 데이터 포함)
analysis = analyze_v2(
    review_text=review['body'],
    review_rating=review['rating'],                    # 개별 리뷰 평점
    product_rating_avg=product['rating_avg'],          # 제품 평균 평점
    product_rating_count=product['rating_count'],      # 총 평점 개수
    # ... 기타 파라미터
)

print(f"신뢰도 점수: {analysis['validation']['trust_score']}")
print(f"평점 신뢰도: {analysis['validation']['rating_reliability_score']}")
print(f"광고 여부: {analysis['validation']['is_ad']}")
```

#### 4.2 배치 분석 (제품의 모든 리뷰)

```python
# 특정 제품의 모든 리뷰 분석
product_id = 1

# 제품 정보 조회
product = supabase.table('products')\
    .select('*')\
    .eq('id', product_id)\
    .single()\
    .execute().data

# 제품의 모든 리뷰 조회
reviews = supabase.table('reviews')\
    .select('*')\
    .eq('product_id', product_id)\
    .execute().data

# 각 리뷰 분석
results = []
for review in reviews:
    analysis = analyze_v2(
        review_text=review['body'],
        review_rating=review['rating'],
        product_rating_avg=product['rating_avg'],
        product_rating_count=product['rating_count']
    )

    results.append({
        'review_id': review['id'],
        'trust_score': analysis['validation']['trust_score'],
        'rating_reliability': analysis['validation']['rating_reliability_score'],
        'is_ad': analysis['validation']['is_ad']
    })

# 광고 리뷰 필터링
ad_reviews = [r for r in results if r['is_ad']]
print(f"광고 리뷰 수: {len(ad_reviews)} / {len(results)}")
```

---

### 5. 테스트 시나리오

#### 5.1 정상 리뷰 (높은 신뢰도)

**입력**:
```python
review_text = "한달 정도 먹어보니 눈이 덜 피곤합니다. 가격도 적당해요."
review_rating = 4
product_rating_avg = 4.5
product_rating_count = 1234
```

**예상 출력**:
```python
{
    "trust_score": 78.5,
    "rating_reliability_score": 85.0,  # 평점 차이 0.5 (신뢰)
    "is_ad": False
}
```

#### 5.2 광고 리뷰 (낮은 신뢰도)

**입력**:
```python
review_text = "최고의 루테인!!! 먹자마자 효과 대박!!! 강력 추천!!!"
review_rating = 5
product_rating_avg = 4.2
product_rating_count = 500
```

**예상 출력**:
```python
{
    "trust_score": 25.0,
    "rating_reliability_score": 35.0,  # 5점 + 극단 평점 패널티
    "is_ad": True  # 신뢰도 낮음 + 5점 폭격 패턴
}
```

#### 5.3 평점 조작 의심

**입력**:
```python
review_text = "좋아요"
review_rating = 1  # 악의적 1점
product_rating_avg = 4.7
product_rating_count = 2000
```

**예상 출력**:
```python
{
    "trust_score": 15.0,
    "rating_reliability_score": 10.0,  # 평점 차이 3.7 (극단)
    "is_ad": True  # 평점 조작 의심
}
```

---

### 6. 예상 효과

#### 6.1 정량적 효과

| 지표 | 현재 | 개선 후 | 향상 |
|------|------|---------|------|
| 광고 탐지율 | 75% | **90%** | +15%p |
| 오탐률 (정상→광고) | 15% | **8%** | -7%p |
| 평점 조작 탐지 | 0% | **85%** | +85%p |
| 신뢰도 점수 정확도 | 70% | **88%** | +18%p |

#### 6.2 정성적 효과

- ✅ **객관적 지표 반영**: 평점은 사용자가 조작하기 어려운 객관 지표
- ✅ **DB 활용도 증가**: Supabase의 rating_avg, rating_count 필드 활용
- ✅ **팀원 간 협업 강화**: DB 담당자 설계와 Logic Designer 로직 통합
- ✅ **확장성 향상**: 추후 평점 트렌드 분석, 시계열 분석 가능

---

### 7. 구현 우선순위

#### Phase 1: 기본 구현 (1-2일)
- [ ] `rating_analyzer.py` 파일 생성
- [ ] `calculate_rating_reliability()` 메서드 구현
- [ ] 단위 테스트 작성

#### Phase 2: 통합 (1일)
- [ ] `trust_score.py` 수정 (`calculate_final_score_v2()` 추가)
- [ ] `is_ad_v2()` 메서드 구현
- [ ] `__init__.py`에 `analyze_v2()` 통합

#### Phase 3: 테스트 (1일)
- [ ] 목업 데이터로 테스트
- [ ] Supabase 연동 테스트
- [ ] 성능 비교 (기존 vs 개선)

#### Phase 4: 문서화 (0.5일)
- [ ] README 업데이트
- [ ] 사용 예제 추가
- [ ] 팀원 C에게 UI 연동 가이드 제공

---

### 8. 리스크 및 대응

#### 리스크 1: rating_avg, rating_count가 NULL인 경우

**대응책**:
```python
if product_rating_avg is None or product_rating_count is None:
    # 기본값 사용 또는 평점 신뢰도 점수를 50점으로 설정
    rating_reliability_score = 50
else:
    rating_reliability_score = calculate_rating_reliability(...)
```

#### 리스크 2: 하위 호환성 문제

**대응책**:
- 기존 `analyze()` 함수 유지
- 새로운 `analyze_v2()` 함수 추가
- 점진적 마이그레이션 권장

#### 리스크 3: 평점 데이터 부족 (신규 제품)

**대응책**:
```python
if product_rating_count < 10:
    # 평점 신뢰도 가중치 낮춤
    rating_weight = 0.05  # 20% → 5%
    other_weights_boost = 0.15 / 5  # 나머지에 재분배
```

---

### 9. 다음 단계

1. **개선안 검토** - 팀원 피드백 수렴
2. **프로토타입 구현** - `rating_analyzer.py` 작성
3. **테스트** - 목업 데이터 + Supabase 실제 데이터
4. **성능 비교** - 기존 vs 개선안 정확도 측정
5. **배포** - UI 팀(팀원 C)과 연동

---

## 참고 자료

**관련 파일**:
- `logic_designer/trust_score.py` - 현재 신뢰도 계산 로직
- `logic_designer/checklist.py` - 13단계 체크리스트
- `database/schema.sql` - Supabase 스키마 정의

**참고 문서**:
- `개발일지/2026-01-05-Supabase_실제_테이블_구조_파악.md`
- `database/README.md`
