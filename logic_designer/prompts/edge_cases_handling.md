# 예외 상황 및 엣지 케이스 처리 가이드

## 목적
영양성분 DB 통합 시 발생할 수 있는 예외 상황과 엣지 케이스를 안전하게 처리하는 방법을 제시합니다.

## 핵심 원칙

### 1. Graceful Degradation (우아한 성능 저하)
- **영양성분 DB가 없어도 시스템이 정상 작동해야 함**
- DB 조회 실패 시 기본값 반환 (오류 발생 없음)
- 기존 기능은 항상 유지

### 2. 입력 검증 강화
- 리뷰가 없거나 너무 짧을 때의 처리
- 빈 값, None 값 처리
- 예상치 못한 데이터 형식 처리

## 예외 상황별 처리 방법

### 1. 영양성분 DB 관련 예외

#### 상황 1: 영양성분 DB 테이블이 없는 경우
```python
def _get_nutrition_info_safe(self, product_id: int) -> Optional[Dict]:
    """
    영양성분 정보 조회 (안전한 방식)
    
    Returns:
        Dict: 영양성분 정보 또는 None (오류/정보 없음)
    """
    try:
        from database.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # 테이블 존재 여부 확인 (선택적)
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .limit(1)\
            .execute()
        
        return {'ingredients': response.data} if response.data else None
        
    except Exception as e:
        # 모든 예외를 무시하고 None 반환
        # 로깅은 선택적 (프로덕션에서는 로깅 권장)
        # import logging
        # logging.debug(f"영양성분 정보 조회 실패 (product_id: {product_id}): {e}")
        return None
```

#### 상황 2: product_id가 None이거나 잘못된 경우
```python
def check_ad_patterns(self, review_text: str, product_id: Optional[int] = None) -> Dict[int, str]:
    """
    체크리스트 검사
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID (None이면 영양성분 검증 생략)
    """
    detected_issues = {}
    
    # 기존 13단계 검사 (항상 수행)
    # ...
    
    # product_id가 유효한 경우만 영양성분 검증
    if product_id and isinstance(product_id, int) and product_id > 0:
        try:
            # 영양성분 검증 수행
            # ...
        except Exception:
            # 오류 발생 시 무시하고 기존 결과만 반환
            pass
    
    return detected_issues
```

#### 상황 3: 영양성분 정보는 있지만 데이터가 불완전한 경우
```python
def _validate_ingredient_claims(self, review_text: str, product_id: Optional[int] = None) -> bool:
    """
    성분 주장 검증
    """
    if not product_id:
        return False
    
    nutrition_info = self._get_nutrition_info_safe(product_id)
    if not nutrition_info:
        return False
    
    # 데이터 검증
    ingredients = nutrition_info.get('ingredients', [])
    if not ingredients or len(ingredients) == 0:
        return False  # 성분 정보가 비어있으면 검증 불가
    
    # 검증 로직 수행
    # ...
```

### 2. 리뷰 텍스트 관련 예외

#### 상황 1: 리뷰가 None이거나 빈 문자열인 경우
```python
def check_ad_patterns(self, review_text: str, product_id: Optional[int] = None) -> Dict[int, str]:
    """
    체크리스트 검사
    """
    # 입력 검증
    if not review_text:
        return {}  # 빈 결과 반환 (오류 없이)
    
    if not isinstance(review_text, str):
        # 문자열이 아니면 문자열로 변환 시도
        try:
            review_text = str(review_text)
        except Exception:
            return {}  # 변환 실패 시 빈 결과 반환
    
    # 리뷰가 너무 짧은 경우 (3자 미만)
    if len(review_text.strip()) < 3:
        return {}  # 의미 있는 검사 불가
    
    # 정상 처리
    # ...
```

#### 상황 2: 리뷰가 매우 짧은 경우 (3-10자)
```python
def check_ad_patterns(self, review_text: str, product_id: Optional[int] = None) -> Dict[int, str]:
    """
    체크리스트 검사
    """
    review_text = review_text.strip()
    
    # 매우 짧은 리뷰 처리
    if len(review_text) < 10:
        # 최소한의 검사만 수행
        detected_issues = {}
        
        # 1번: 대가성 문구만 체크 (짧은 리뷰에서도 가능)
        if re.search(r"무상.*제공|무료.*제공|받았어요|협찬", review_text):
            detected_issues[1] = "대가성 문구 존재"
        
        # 13번: 이모티콘 과다 사용 체크
        if re.search(r"[😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚]{5,}", review_text):
            detected_issues[13] = "이모티콘 과다 사용"
        
        # 영양성분 검증은 생략 (정보 부족)
        return detected_issues
    
    # 정상 길이 리뷰 처리
    # ...
```

#### 상황 3: 리뷰에 특수 문자나 인코딩 문제가 있는 경우
```python
def check_ad_patterns(self, review_text: str, product_id: Optional[int] = None) -> Dict[int, str]:
    """
    체크리스트 검사
    """
    try:
        # 인코딩 정규화
        if isinstance(review_text, bytes):
            review_text = review_text.decode('utf-8', errors='ignore')
        
        # 특수 문자 정리 (선택적)
        # review_text = review_text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 정상 처리
        # ...
    except UnicodeDecodeError:
        # 인코딩 오류 시 빈 결과 반환
        return {}
```

### 3. 점수 계산 관련 예외

#### 상황 1: 영양성분 점수 계산 실패 시
```python
def calculate_final_score(
    self,
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    penalty_count: int = 0,
    penalty_per_item: int = 10,
    review_text: Optional[str] = None,
    product_id: Optional[int] = None,
    use_nutrition_score: bool = True
) -> Dict:
    """
    최종 신뢰도 점수 계산
    """
    # 기본 점수 계산 (항상 수행)
    base_score = self.calculate_base_score(
        length_score,
        repurchase_score,
        monthly_use_score,
        photo_score,
        consistency_score
    )
    
    # 영양성분 점수 계산 (선택적)
    nutrition_score = 50.0  # 기본값 (중간값)
    if use_nutrition_score and review_text and product_id:
        try:
            nutrition_score = self.calculate_nutrition_consistency_score(
                review_text,
                product_id
            )
            # 영양성분 점수 통합
            base_score = (base_score * 0.8) + (nutrition_score * 0.2)
        except Exception:
            # 계산 실패 시 기본값 사용 (오류 없이)
            # base_score는 그대로 유지
            pass
    
    # 감점 적용
    penalty = penalty_count * penalty_per_item
    final_score = max(0, base_score - penalty)
    
    return {
        "base_score": base_score,
        "nutrition_score": nutrition_score,
        "penalty": penalty,
        "final_score": final_score,
        "raw_scores": {
            "L": length_score,
            "R": repurchase_score,
            "M": monthly_use_score,
            "P": photo_score,
            "C": consistency_score,
            "N": nutrition_score
        }
    }
```

### 4. AI 분석 관련 예외

#### 상황 1: 리뷰가 너무 짧아서 AI 분석 불가능한 경우
```python
def analyze(self, review_text: str, product_id: Optional[int] = None, model: str = "claude-sonnet-4-5-20250929") -> Dict:
    """
    AI 분석
    """
    # 입력 검증
    if len(review_text.strip()) < 10:
        return {
            "error": "REVIEW_TOO_SHORT",
            "message": "리뷰가 너무 짧습니다 (최소 10자 이상)",
            "summary": "분석 불가",
            "efficacy": "정보 없음",
            "side_effects": "정보 없음",
            "tip": "리뷰 내용이 부족하여 분석할 수 없습니다.",
            "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
        }
    
    # 정상 분석 수행
    # ...
```

#### 상황 2: 영양성분 정보가 없어도 AI 분석은 수행
```python
def analyze(self, review_text: str, product_id: Optional[int] = None, model: str = "claude-sonnet-4-5-20250929") -> Dict:
    """
    AI 분석 (영양성분 정보 없어도 수행)
    """
    # 영양성분 정보 조회 (실패해도 계속 진행)
    nutrition_info = None
    if product_id:
        try:
            nutrition_info = self._get_nutrition_info_safe(product_id)
        except Exception:
            # 오류 발생해도 분석은 계속
            nutrition_info = None
    
    # AI 프롬프트 생성 (영양성분 정보가 있으면 포함, 없으면 기본 프롬프트)
    prompt = self._build_enhanced_prompt(review_text, nutrition_info)
    
    # AI 분석 수행
    # ...
```

## 프로젝트 전체 대처 방안

### 1. 리뷰 데이터 부족 시나리오

#### 시나리오 A: 제품에 리뷰가 전혀 없는 경우
```python
# UI/API 레벨에서 처리
def get_product_analysis(product_id: int):
    """
    제품 분석 결과 조회
    """
    # 리뷰 개수 확인
    review_count = get_review_count(product_id)
    
    if review_count == 0:
        return {
            "status": "NO_REVIEWS",
            "message": "이 제품에는 아직 리뷰가 없습니다.",
            "suggestion": "리뷰가 충분히 모이면 분석을 제공할 수 있습니다.",
            "validation": None,
            "analysis": None
        }
    
    # 리뷰가 있는 경우 정상 처리
    # ...
```

#### 시나리오 B: 리뷰가 1-2개만 있는 경우
```python
def analyze_product_reviews(product_id: int, min_reviews: int = 3):
    """
    제품 리뷰 분석 (최소 리뷰 개수 요구)
    """
    reviews = get_reviews(product_id)
    
    if len(reviews) < min_reviews:
        return {
            "status": "INSUFFICIENT_REVIEWS",
            "message": f"리뷰가 {len(reviews)}개로 부족합니다 (최소 {min_reviews}개 필요).",
            "current_reviews": len(reviews),
            "required_reviews": min_reviews,
            "partial_analysis": analyze_available_reviews(reviews)  # 부분 분석 제공
        }
    
    # 충분한 리뷰가 있는 경우 정상 분석
    # ...
```

#### 시나리오 C: 리뷰는 많지만 모두 매우 짧은 경우
```python
def analyze_reviews(reviews: List[Dict]) -> Dict:
    """
    리뷰 분석 (리뷰 길이 고려)
    """
    # 리뷰 길이 분포 확인
    review_lengths = [len(r.get('body', '')) for r in reviews]
    avg_length = sum(review_lengths) / len(review_lengths) if review_lengths else 0
    
    if avg_length < 20:
        return {
            "status": "SHORT_REVIEWS",
            "message": "대부분의 리뷰가 매우 짧아 상세한 분석이 어렵습니다.",
            "average_length": avg_length,
            "recommendation": "더 긴 리뷰가 필요합니다.",
            "limited_analysis": perform_basic_analysis(reviews)  # 기본 분석만 제공
        }
    
    # 정상 분석 수행
    # ...
```

### 2. 영양성분 DB 부재 시나리오

#### 시나리오 A: nutrition_info 테이블이 아직 생성되지 않은 경우
```python
# 프로젝트 초기화 시 체크
def check_nutrition_db_availability() -> Dict:
    """
    영양성분 DB 사용 가능 여부 확인
    """
    try:
        from database.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # 테이블 존재 여부 확인
        response = supabase.table('nutrition_info')\
            .select('id')\
            .limit(1)\
            .execute()
        
        return {
            "available": True,
            "message": "영양성분 DB 사용 가능"
        }
    except Exception as e:
        return {
            "available": False,
            "message": "영양성분 DB 사용 불가 (기본 모드로 동작)",
            "error": str(e)
        }
```

#### 시나리오 B: 제품별로 영양성분 정보가 없는 경우
```python
def analyze_with_fallback(review_text: str, product_id: Optional[int] = None) -> Dict:
    """
    분석 수행 (영양성분 정보 없어도 동작)
    """
    # 1. 영양성분 정보 확인
    has_nutrition_info = False
    if product_id:
        nutrition_info = get_nutrition_info_safe(product_id)
        has_nutrition_info = nutrition_info is not None
    
    # 2. 분석 수행 (영양성분 정보 유무와 관계없이)
    result = analyze(
        review_text,
        product_id=product_id if has_nutrition_info else None,
        use_nutrition_validation=has_nutrition_info
    )
    
    # 3. 결과에 메타데이터 추가
    result["metadata"] = {
        "nutrition_info_available": has_nutrition_info,
        "analysis_mode": "enhanced" if has_nutrition_info else "basic"
    }
    
    return result
```

### 3. 통합 대처 전략

```python
# logic_designer/__init__.py에 추가
def analyze_with_safety_checks(
    review_text: str,
    product_id: Optional[int] = None,
    **kwargs
) -> Dict:
    """
    안전한 분석 (모든 예외 상황 처리)
    """
    # 1. 입력 검증
    if not review_text or len(review_text.strip()) < 3:
        return {
            "error": "INVALID_INPUT",
            "message": "리뷰가 너무 짧거나 비어있습니다.",
            "validation": None,
            "analysis": None
        }
    
    # 2. 영양성분 DB 사용 가능 여부 확인
    use_nutrition = False
    if product_id:
        try:
            nutrition_info = get_nutrition_info_safe(product_id)
            use_nutrition = nutrition_info is not None
        except Exception:
            use_nutrition = False
    
    # 3. 분석 수행
    try:
        result = analyze(
            review_text,
            product_id=product_id if use_nutrition else None,
            use_nutrition_validation=use_nutrition,
            **kwargs
        )
        
        # 4. 메타데이터 추가
        result["metadata"] = {
            "nutrition_validation_used": use_nutrition,
            "review_length": len(review_text),
            "has_product_id": product_id is not None
        }
        
        return result
        
    except Exception as e:
        # 최종 오류 처리
        return {
            "error": "ANALYSIS_ERROR",
            "message": f"분석 중 오류 발생: {str(e)}",
            "validation": None,
            "analysis": None
        }
```

## 구현 체크리스트

### 필수 구현 항목
- [ ] 모든 DB 조회 함수에 try-except 추가
- [ ] 모든 함수에 입력 검증 추가 (None, 빈 문자열 체크)
- [ ] 영양성분 정보 없을 때 기본값 반환
- [ ] 리뷰가 짧을 때 적절한 처리
- [ ] 오류 발생 시 로깅 (선택적)

### 권장 구현 항목
- [ ] 영양성분 DB 사용 가능 여부 체크 함수
- [ ] 리뷰 데이터 품질 평가 함수
- [ ] 부분 분석 제공 기능
- [ ] 메타데이터 추가 (분석 모드 표시)

## 테스트 시나리오

### 테스트 1: 영양성분 DB 없음
```python
# nutrition_info 테이블이 없는 경우
result = analyze("리뷰 텍스트", product_id=1)
# 기대: 오류 없이 기본 모드로 동작
assert result["metadata"]["nutrition_validation_used"] == False
```

### 테스트 2: 리뷰 없음
```python
# 빈 리뷰
result = analyze("", product_id=1)
# 기대: 적절한 오류 메시지 반환
assert result["error"] == "INVALID_INPUT"
```

### 테스트 3: 매우 짧은 리뷰
```python
# 3자 미만 리뷰
result = analyze("좋아요", product_id=1)
# 기대: 최소한의 검사만 수행
assert len(result["validation"]["reasons"]) <= 2
```

### 테스트 4: product_id 없음
```python
# product_id 없이 분석
result = analyze("리뷰 텍스트")
# 기대: 기본 모드로 정상 동작
assert result["validation"] is not None
```

## 참고 자료

- 각 프롬프트 파일의 "구현 요구사항" 섹션
- README.md의 "공통 구현 패턴" 섹션
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/
