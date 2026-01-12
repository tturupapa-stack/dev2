# UI/UX 개발 가이드 - 초보 개발자를 위한 페이지 설명 및 개발일지

**작성일**: 2026-01-12  
**작성자**: 개발팀  
**대상**: 초보 UI/UX 개발 담당자  
**목적**: Streamlit 앱 페이지 구조 이해 및 UI 개발 안내

---

## 📋 개요

이 문서는 건기식 리뷰 팩트체크 시스템의 Streamlit UI 페이지를 이해하고, UI 개발을 진행하는 데 필요한 가이드를 제공합니다. 현재 페이지의 구조, 각 컴포넌트의 역할, 그리고 Supabase DB를 활용한 개선 방안을 포함합니다.

---

## 🎨 현재 페이지 구조 분석

### 전체 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│  🔍 건기식 리뷰 팩트체크                                │
│  루테인 제품 상위 3종 비교 분석                          │
├──────────────┬──────────────────────────────────────────┤
│              │  📦 제품 개요 (상위 3개)                  │
│  사이드바    │  [🥇] [🥈] [🥉]                          │
│              │                                           │
│  🔎 제품 검색│  📊 종합 비교표                            │
│  [검색창]    │  [비교 테이블]                            │
│              │                                           │
│  ℹ️ 신뢰도   │  📈 시각화 분석 (상위 3개)                │
│  등급 안내   │  ┌─────────────┬─────────────┐          │
│              │  │ 🕸️ 레이더    │ 💰 가격 비교│          │
│  📊 분석 기준│  │   차트       │   차트      │          │
│              │  └─────────────┴─────────────┘          │
│              │                                           │
│              │  📄 기타 제품                             │
│              │  [제품 목록]                              │
└──────────────┴──────────────────────────────────────────┘
```

---

## 📐 페이지 구성 요소 상세 설명

### 1. 사이드바 (Left Sidebar) - `st.sidebar`

사이드바는 사용자 입력과 정보 제공을 위한 고정 패널입니다.

#### 1.1 제품 검색 섹션

**위치**: 사이드바 상단  
**Streamlit 컴포넌트**: `st.text_input()`

```python
with st.sidebar:
    st.markdown("### 🔎 제품 검색")
    
    search_query_raw = st.text_input(
        "제품명 또는 브랜드 검색",
        placeholder="예: NOW Foods, Lutein...",
        key="search"
    )
```

**역할**:
- 사용자가 제품명이나 브랜드명을 입력하여 제품을 검색
- 입력된 검색어로 제품 목록 필터링
- `key="search"`로 위젯을 고유하게 식별

**개발 팁**:
- `placeholder`는 사용자에게 입력 예시를 보여줌
- `key`는 Streamlit이 위젯 상태를 추적하는 데 사용
- 검색어는 `sanitize_user_input()` 함수로 안전하게 처리

#### 1.2 신뢰도 등급 안내 섹션

**위치**: 사이드바 중간  
**Streamlit 컴포넌트**: `st.markdown()`

```python
st.markdown("### ℹ️ 신뢰도 등급 안내")
st.markdown("""
- **HIGH (70점 이상)**: 신뢰할 수 있는 제품
- **MEDIUM (50-70점)**: 보통 수준
- **LOW (50점 미만)**: 주의 필요
""")
```

**역할**:
- 신뢰도 점수 기준을 사용자에게 명확히 안내
- 각 등급의 의미를 설명하여 사용자 이해도 향상

**개발 팁**:
- Markdown 문법(`**굵게**`)을 사용하여 가독성 향상
- 이모지(ℹ️)로 시각적 구분
- `---`로 섹션 간 구분선 추가

#### 1.3 분석 기준 섹션

**위치**: 사이드바 하단  
**Streamlit 컴포넌트**: `st.markdown()`

```python
st.markdown("### 📊 분석 기준")
st.markdown("""
1. 인증 구매 비율
2. 재구매율
3. 장기 사용 비율
4. 평점 분포 적절성
5. 리뷰 길이
6. 시간 분포 자연성
7. 광고성 리뷰 탐지
8. 리뷰어 다양성
""")
```

**역할**:
- 제품 분석에 사용되는 8가지 기준을 명시
- 사용자가 분석 결과를 이해하는 데 도움

---

### 2. 메인 콘텐츠 영역 (Main Content Area)

메인 영역은 데이터 시각화와 분석 결과를 표시합니다.

#### 2.1 제품 개요 섹션 (상위 3개)

**위치**: 메인 영역 상단  
**Streamlit 컴포넌트**: `st.columns()`, `st.plotly_chart()`

```python
st.markdown('<div class="section-header">📦 제품 개요 (상위 3개)</div>', unsafe_allow_html=True)

cols = st.columns(3)  # 3개 컬럼 생성

for idx, data in enumerate(top3_products):
    with cols[idx]:  # 각 컬럼에 제품 정보 표시
        # 순위 배지
        rank_badge = rank_badges.get(idx, "")
        st.markdown(f'<div style="...">{rank_badge}</div>', unsafe_allow_html=True)
        
        # 제품 정보
        st.markdown(f"**{brand}**")
        st.markdown(f"<small>{name}</small>", unsafe_allow_html=True)
        
        # 신뢰도 게이지 차트
        fig_gauge = render_gauge_chart(trust_score, "신뢰도")
        st.plotly_chart(fig_gauge, key=f"gauge_{product.get('id', idx)}")
        
        # 신뢰도 배지
        badge_html = render_trust_badge(trust_level)
        st.markdown(badge_html, unsafe_allow_html=True)
```

**역할**:
- 상위 3개 제품을 가로로 나란히 표시
- 각 제품의 핵심 정보(브랜드, 이름, 가격, 신뢰도)를 카드 형태로 제공
- 순위 배지(🥇🥈🥉)로 시각적 구분

**개발 팁**:
- `st.columns(3)`로 3개 컬럼 생성
- `with cols[idx]:`로 각 컬럼에 내용 배치
- `st.plotly_chart()`로 인터랙티브 차트 표시
- `key` 파라미터로 각 차트를 고유하게 식별

#### 2.2 종합 비교표 섹션

**위치**: 메인 영역 중간  
**Streamlit 컴포넌트**: `st.dataframe()`

```python
st.markdown('<div class="section-header">📊 종합 비교표 (상위 3개)</div>', unsafe_allow_html=True)

comparison_df = render_comparison_table(top3_products)
st.dataframe(
    comparison_df,
    hide_index=True,
    height=250
)
```

**역할**:
- 상위 3개 제품의 주요 지표를 테이블로 비교
- 신뢰도, 광고 의심률, 재구매율, 한 달 사용 비율, 평균 평점 등 표시

**개발 팁**:
- `pandas.DataFrame`을 `st.dataframe()`으로 표시
- `hide_index=True`로 인덱스 숨김
- `height`로 테이블 높이 제한

#### 2.3 시각화 분석 섹션

**위치**: 메인 영역 중하단  
**Streamlit 컴포넌트**: `st.columns()`, `st.plotly_chart()`

##### 2.3.1 레이더 차트 (다차원 비교)

```python
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🕸️ 다차원 비교 (레이더 차트)")
    fig_radar = render_radar_chart(top3_products)
    st.plotly_chart(fig_radar, key="radar_main")
```

**역할**:
- 5개 차원(신뢰도, 가격점수, 함유량, 평균평점, 리뷰다양성)으로 제품 비교
- 각 제품을 다른 색상의 다각형으로 표시
- 한눈에 제품의 강점과 약점 파악 가능

**레이더 차트 구성 요소**:
- **축 (Axes)**: 5개 차원
  - 신뢰도: AI 분석 신뢰도 점수 (0-100)
  - 가격점수: 가성비 점수 (가격이 낮을수록 높음, 0-100)
  - 함유량: 루테인+제아잔틴 총 함유량 점수 (0-100)
  - 평균평점: 리뷰 평균 평점 (5점 → 100점 환산)
  - 리뷰다양성: 리뷰어 다양성 비율 (0-100)
- **범례**: 각 제품의 색상 매핑
- **스케일**: 0(중앙) ~ 100(외곽) 원형 그리드

**개발 팁**:
- `render_radar_chart()` 함수는 `visualizations.py`에 정의됨
- Plotly의 `go.Scatterpolar`을 사용하여 레이더 차트 생성
- `st.plotly_chart()`로 인터랙티브 차트 렌더링

##### 2.3.2 가격 비교 차트

```python
with col2:
    st.markdown("#### 💰 가격 비교")
    fig_price = render_price_comparison_chart(top3_products)
    st.plotly_chart(fig_price, key="price_main")
```

**역할**:
- 상위 3개 제품의 가격을 막대 차트로 비교
- 가격 정보를 시각적으로 비교하기 쉽게 표시

#### 2.4 기타 제품 섹션

**위치**: 메인 영역 하단  
**Streamlit 컴포넌트**: `st.expander()`

```python
if other_products:
    st.markdown('<div class="section-header">📄 기타 제품</div>', unsafe_allow_html=True)
    
    with st.expander("기타 제품 보기 (간략 정보)", expanded=False):
        for idx, data in enumerate(other_products):
            # 제품 간략 정보 표시
```

**역할**:
- 상위 3개 외 나머지 제품들을 접을 수 있는 섹션에 표시
- 공간 절약 및 사용자 선택적 정보 제공

**개발 팁**:
- `st.expander()`로 접을 수 있는 섹션 생성
- `expanded=False`로 기본적으로 접힌 상태
- 클릭 시 펼쳐져서 상세 정보 표시

---

## 🛠️ Streamlit 컴포넌트 사용 가이드

### 기본 컴포넌트

| 컴포넌트 | 용도 | 예시 |
|---------|------|------|
| `st.markdown()` | 텍스트/제목 표시 | `st.markdown("### 제목")` |
| `st.text_input()` | 텍스트 입력 필드 | `st.text_input("검색어")` |
| `st.columns()` | 가로 배치 | `col1, col2 = st.columns(2)` |
| `st.plotly_chart()` | Plotly 차트 표시 | `st.plotly_chart(fig)` |
| `st.dataframe()` | 데이터 테이블 표시 | `st.dataframe(df)` |
| `st.expander()` | 접을 수 있는 섹션 | `st.expander("제목")` |
| `st.sidebar` | 사이드바 영역 | `with st.sidebar:` |

### 레이아웃 구성 패턴

#### 패턴 1: 가로 배치 (3개 컬럼)
```python
cols = st.columns(3)
with cols[0]:
    st.write("첫 번째 컬럼")
with cols[1]:
    st.write("두 번째 컬럼")
with cols[2]:
    st.write("세 번째 컬럼")
```

#### 패턴 2: 가로 배치 (2개 컬럼)
```python
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1)
with col2:
    st.plotly_chart(fig2)
```

#### 패턴 3: 사이드바 사용
```python
with st.sidebar:
    st.markdown("### 사이드바 제목")
    user_input = st.text_input("입력")
```

---

## 💾 Supabase DB 연동 개선안

현재 앱은 `mock_data.py`를 사용하지만, Supabase DB와 연동하여 실제 데이터를 사용할 수 있습니다.

### 현재 상태

**데이터 소스**: `mock_data.py` (목업 데이터)
- 제품 5종
- 각 제품당 리뷰 20개 (총 100개)
- 고정된 분석 결과

### 개선안 1: 실시간 제품 검색 (Supabase 연동)

#### 현재 구현
```python
from mock_data import search_products

if search_query:
    filtered_products = search_products(search_query)
```

#### 개선안: Supabase에서 실시간 검색
```python
from supabase_data import search_products_from_db

if search_query:
    # Supabase에서 제품 검색
    filtered_products = search_products_from_db(search_query)
    # 검색 결과가 없으면 목업 데이터로 폴백
    if not filtered_products:
        filtered_products = search_products(search_query)  # 폴백
```

**개선 효과**:
- ✅ 실제 DB 데이터로 검색
- ✅ 새로운 제품 추가 시 자동 반영
- ✅ 검색 성능 향상 (인덱스 활용)

**구현 방법**:
1. `supabase_data.py`에 `search_products_from_db()` 함수 추가
2. Supabase의 `products` 테이블에서 `ilike` 쿼리 사용
3. 검색 결과를 기존 데이터 형식으로 변환

**예시 코드**:
```python
def search_products_from_db(search_query: str) -> List[Dict]:
    """Supabase에서 제품 검색"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    
    url = f'{SUPABASE_URL}/rest/v1/products'
    params = f'name.ilike.%{search_query}%,brand.ilike.%{search_query}%'
    
    response = requests.get(url, headers=_get_headers(), params=params)
    if response.status_code == 200:
        return response.json()
    return []
```

---

### 개선안 2: 동적 필터링 옵션 (Supabase 활용)

#### 현재 구현
- 사이드바에 검색창만 있음
- 필터링 옵션 없음

#### 개선안: 다중 필터 추가
```python
with st.sidebar:
    st.markdown("### 🔎 제품 검색")
    search_query = st.text_input("제품명 또는 브랜드 검색", ...)
    
    st.markdown("---")
    
    # 🆕 신규 추가: 브랜드 필터
    st.markdown("### 🏷️ 브랜드 필터")
    brands = get_all_brands_from_db()  # Supabase에서 브랜드 목록 가져오기
    selected_brands = st.multiselect(
        "브랜드 선택",
        options=brands,
        default=brands,  # 기본값: 전체 선택
        key="brand_filter"
    )
    
    # 🆕 신규 추가: 신뢰도 등급 필터
    st.markdown("### ⭐ 신뢰도 등급 필터")
    trust_levels = st.multiselect(
        "등급 선택",
        options=["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"],
        key="trust_filter"
    )
    
    # 🆕 신규 추가: 가격 범위 필터
    st.markdown("### 💰 가격 범위")
    price_range = st.slider(
        "가격 범위 ($)",
        min_value=0,
        max_value=100,
        value=(0, 100),
        key="price_range"
    )
```

**개선 효과**:
- ✅ 사용자가 원하는 조건으로 제품 필터링
- ✅ Supabase 쿼리로 효율적인 필터링
- ✅ 사용자 경험 향상

**구현 방법**:
1. `supabase_data.py`에 필터링 함수 추가
2. Supabase 쿼리에 필터 조건 추가
3. UI에 `st.multiselect`, `st.slider` 등 추가

**예시 코드**:
```python
def get_all_brands_from_db() -> List[str]:
    """Supabase에서 모든 브랜드 목록 가져오기"""
    url = f'{SUPABASE_URL}/rest/v1/products'
    params = 'select=brand&order=brand'
    
    response = requests.get(url, headers=_get_headers(), params=params)
    if response.status_code == 200:
        brands = [item['brand'] for item in response.json()]
        return sorted(list(set(brands)))  # 중복 제거 및 정렬
    return []

def filter_products_from_db(
    brands: List[str] = None,
    trust_levels: List[str] = None,
    price_min: float = None,
    price_max: float = None
) -> List[Dict]:
    """Supabase에서 필터링된 제품 가져오기"""
    # Supabase 쿼리 구성
    params = []
    
    if brands:
        brand_filter = ','.join([f'brand.eq.{b}' for b in brands])
        params.append(brand_filter)
    
    if price_min is not None:
        params.append(f'price.gte.{price_min}')
    
    if price_max is not None:
        params.append(f'price.lte.{price_max}')
    
    query_string = '&'.join(params)
    url = f'{SUPABASE_URL}/rest/v1/products?{query_string}'
    
    response = requests.get(url, headers=_get_headers())
    if response.status_code == 200:
        products = response.json()
        
        # 신뢰도 등급 필터링 (클라이언트 사이드)
        if trust_levels:
            # 분석 결과와 조인하여 필터링
            filtered = []
            for product in products:
                analysis = get_analysis_for_product(product['id'])
                if analysis and analysis.get('trust_level') in trust_levels:
                    filtered.append(product)
            return filtered
        
        return products
    return []
```

---

### 개선안 3: 실시간 통계 대시보드

#### 현재 구현
- 고정된 상위 3개 제품만 표시
- 통계 정보 없음

#### 개선안: 실시간 통계 추가
```python
# 사이드바에 통계 섹션 추가
with st.sidebar:
    st.markdown("---")
    
    # 🆕 신규 추가: 실시간 통계
    st.markdown("### 📊 전체 통계")
    
    # Supabase에서 통계 가져오기
    stats = get_statistics_from_db()
    
    st.metric("전체 제품 수", stats['total_products'])
    st.metric("평균 신뢰도", f"{stats['avg_trust_score']:.1f}점")
    st.metric("HIGH 등급 제품", f"{stats['high_count']}개")
    
    # 통계 차트 (작은 파이 차트)
    fig_stats = render_statistics_pie_chart(stats)
    st.plotly_chart(fig_stats, use_container_width=True)
```

**개선 효과**:
- ✅ 전체 데이터베이스 현황 파악
- ✅ 사용자에게 컨텍스트 제공
- ✅ 데이터 기반 의사결정 지원

**구현 방법**:
1. `supabase_data.py`에 통계 조회 함수 추가
2. Supabase 집계 쿼리 사용 (`count`, `avg` 등)
3. 작은 차트로 시각화

**예시 코드**:
```python
def get_statistics_from_db() -> Dict:
    """Supabase에서 전체 통계 가져오기"""
    # 제품 수
    products_count = _fetch_count('products')
    
    # 평균 신뢰도 (분석 결과에서)
    # 주의: 실제로는 analysis_results 테이블이 필요하거나
    # products 테이블에 trust_score 컬럼이 있어야 함
    
    return {
        'total_products': products_count,
        'avg_trust_score': 65.5,  # 예시 값
        'high_count': 2,  # 예시 값
        'medium_count': 2,
        'low_count': 1
    }
```

---

### 개선안 4: 제품 상세 페이지/모달

#### 현재 구현
- 제품 목록만 표시
- 상세 정보는 확장 패널에만 표시

#### 개선안: 클릭 가능한 제품 카드
```python
# 제품 카드를 클릭 가능하게 만들기
for idx, data in enumerate(top3_products):
    with cols[idx]:
        # 🆕 제품 카드를 클릭 가능한 버튼으로
        if st.button(f"상세 보기", key=f"detail_{idx}"):
            st.session_state['selected_product_id'] = data['product']['id']
            st.rerun()  # 페이지 새로고침
        
        # 제품 기본 정보 표시
        # ...

# 선택된 제품이 있으면 상세 모달 표시
if 'selected_product_id' in st.session_state:
    product_id = st.session_state['selected_product_id']
    
    # 🆕 Supabase에서 상세 정보 가져오기
    product_detail = get_product_detail_from_db(product_id)
    
    # 모달 또는 새 섹션으로 상세 정보 표시
    with st.expander(f"📋 {product_detail['name']} 상세 정보", expanded=True):
        # 제품 상세 정보
        st.markdown(f"**브랜드**: {product_detail['brand']}")
        st.markdown(f"**가격**: ${product_detail['price']:.2f}")
        
        # 🆕 Supabase에서 리뷰 가져오기
        reviews = get_reviews_for_product_from_db(product_id)
        st.markdown(f"**리뷰 수**: {len(reviews)}개")
        
        # 성분 정보
        if 'ingredients' in product_detail:
            st.markdown("**주요 성분**:")
            for ing in product_detail['ingredients']:
                st.markdown(f"- {ing['name']}: {ing['amount']}")
```

**개선 효과**:
- ✅ 사용자가 원하는 제품만 상세히 확인
- ✅ 페이지 공간 효율적 사용
- ✅ 인터랙티브한 사용자 경험

---

### 개선안 5: 실시간 리뷰 업데이트

#### 현재 구현
- 고정된 리뷰 데이터만 표시
- 새 리뷰 추가 시 수동 업데이트 필요

#### 개선안: 최신 리뷰 자동 표시
```python
# 리뷰 섹션에 최신 리뷰 옵션 추가
with col_filter1:
    highlight_ads = st.checkbox("광고 의심 리뷰 하이라이트", value=True)
    
    # 🆕 신규 추가: 최신 리뷰만 보기
    show_recent_only = st.checkbox("최근 7일 리뷰만 보기", value=False)

# 리뷰 필터링
if show_recent_only:
    # 🆕 Supabase에서 최근 7일 리뷰만 가져오기
    from datetime import datetime, timedelta
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    recent_reviews = get_reviews_from_db(
        product_id=selected_data['product']['id'],
        date_from=seven_days_ago
    )
    filtered_reviews = recent_reviews
else:
    filtered_reviews = [r for r in reviews if r["rating"] in rating_filter]
```

**개선 효과**:
- ✅ 최신 리뷰 트렌드 파악
- ✅ 시간에 따른 리뷰 변화 추적
- ✅ 사용자에게 최신 정보 제공

---

### 개선안 6: 사용자 피드백 수집

#### 개선안: 피드백 버튼 추가
```python
# 각 제품 분석 결과 옆에 피드백 버튼
for idx, data in enumerate(top3_products):
    with cols[idx]:
        # ... 제품 정보 표시 ...
        
        # 🆕 신규 추가: 피드백 수집
        st.markdown("---")
        st.markdown("**이 분석이 도움이 되었나요?**")
        
        col_fb1, col_fb2 = st.columns(2)
        with col_fb1:
            if st.button("👍 도움됨", key=f"helpful_{idx}"):
                # Supabase에 피드백 저장
                save_feedback_to_db(
                    product_id=data['product']['id'],
                    feedback_type='helpful',
                    user_ip=st.session_state.get('user_ip', 'unknown')
                )
                st.success("피드백 감사합니다!")
        
        with col_fb2:
            if st.button("👎 도움 안됨", key=f"not_helpful_{idx}"):
                save_feedback_to_db(
                    product_id=data['product']['id'],
                    feedback_type='not_helpful',
                    user_ip=st.session_state.get('user_ip', 'unknown')
                )
                st.info("개선하겠습니다!")
```

**개선 효과**:
- ✅ 사용자 만족도 측정
- ✅ 서비스 개선 데이터 수집
- ✅ 사용자 참여도 향상

**구현 방법**:
1. Supabase에 `user_feedback` 테이블 생성
2. 피드백 저장 함수 구현
3. UI에 피드백 버튼 추가

**테이블 스키마 예시**:
```sql
CREATE TABLE user_feedback (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    feedback_type TEXT,  -- 'helpful', 'not_helpful'
    user_ip TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🎯 UI 개발 체크리스트

### 기본 UI 구성

- [ ] 사이드바 레이아웃 구성
  - [ ] 제품 검색 입력 필드
  - [ ] 신뢰도 등급 안내 텍스트
  - [ ] 분석 기준 리스트
- [ ] 메인 영역 레이아웃 구성
  - [ ] 제품 개요 섹션 (3개 컬럼)
  - [ ] 종합 비교표 섹션
  - [ ] 시각화 분석 섹션 (2개 컬럼)
  - [ ] 기타 제품 섹션

### 시각화 구현

- [ ] 게이지 차트 구현
  - [ ] 신뢰도 점수 표시
  - [ ] 색상 구분 (HIGH/MEDIUM/LOW)
- [ ] 레이더 차트 구현
  - [ ] 5개 차원 축 구성
  - [ ] 3개 제품 데이터 시리즈
  - [ ] 범례 표시
- [ ] 가격 비교 차트 구현
  - [ ] 막대 차트 또는 선 차트
  - [ ] 제품별 색상 구분

### 데이터 연동

- [ ] Mock 데이터 로드 확인
- [ ] Supabase 연동 준비 (선택)
  - [ ] 환경 변수 설정
  - [ ] `supabase_data.py` 모듈 활용
  - [ ] 폴백 로직 구현

### 사용자 경험

- [ ] 검색 기능 동작 확인
- [ ] 필터링 기능 동작 확인
- [ ] 차트 인터랙션 확인
- [ ] 반응형 레이아웃 확인

---

## 📚 학습 자료 및 참고 문서

### Streamlit 공식 문서
- [Streamlit Components](https://docs.streamlit.io/library/api-reference)
- [Layouts and Containers](https://docs.streamlit.io/library/api-reference/layout)
- [Charts and Graphs](https://docs.streamlit.io/library/api-reference/charts)

### Plotly 문서
- [Plotly Python](https://plotly.com/python/)
- [Radar Chart (Polar Chart)](https://plotly.com/python/radar-chart/)

### Supabase 연동
- [Supabase REST API](https://supabase.com/docs/reference/javascript/introduction)
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/secrets-management)

---

## 🚀 다음 단계 개발 가이드

### 단계 1: 기본 UI 복제
1. `app.py` 파일을 열고 각 섹션을 하나씩 이해
2. 각 Streamlit 컴포넌트의 역할 파악
3. CSS 스타일 적용 방법 학습

### 단계 2: 시각화 커스터마이징
1. `visualizations.py` 파일 분석
2. 레이더 차트 색상/스타일 변경
3. 새로운 차트 타입 추가 (예: 히트맵, 트리맵)

### 단계 3: Supabase 연동
1. `supabase_data.py` 모듈 이해
2. 간단한 쿼리부터 시작 (예: 제품 목록 가져오기)
3. 점진적으로 복잡한 쿼리 구현

### 단계 4: 고급 기능 추가
1. 사용자 피드백 수집
2. 실시간 통계 대시보드
3. 제품 상세 페이지

---

## 💡 개발 팁

### 1. 디버깅 방법
```python
# Streamlit에서 디버깅
st.write("디버그 정보:", variable)  # 변수 값 확인
st.json(data)  # JSON 데이터 구조 확인
```

### 2. 성능 최적화
```python
# 데이터 캐싱 사용
@st.cache_data
def load_heavy_data():
    # 무거운 데이터 로드
    return data
```

### 3. 에러 처리
```python
try:
    # 위험한 코드
    result = risky_operation()
except Exception as e:
    st.error(f"오류 발생: {str(e)}")
    # 폴백 로직
    result = fallback_data
```

### 4. 사용자 입력 검증
```python
# 항상 사용자 입력을 검증하고 이스케이프
from utils import sanitize_user_input

user_input = st.text_input("입력")
safe_input = sanitize_user_input(user_input)  # XSS 방지
```

---

## 📝 결론

이 가이드는 초보 UI/UX 개발자가 Streamlit 앱의 구조를 이해하고, 단계적으로 UI를 개발할 수 있도록 돕기 위해 작성되었습니다.

**핵심 포인트**:
1. **사이드바**: 사용자 입력 및 정보 제공
2. **메인 영역**: 데이터 시각화 및 분석 결과
3. **Supabase 연동**: 실시간 데이터 활용으로 앱 기능 강화

**다음 작업**:
- [ ] 현재 UI 구조 완전히 이해
- [ ] 각 컴포넌트를 하나씩 구현해보기
- [ ] Supabase 연동 개선안 중 우선순위 정하기
- [ ] 팀원들과 협의하여 개선안 구체화

**질문이나 도움이 필요하면 언제든 팀원들에게 물어보세요!** 🚀

---

**작성 완료 시간**: 2026-01-12  
**다음 업데이트**: UI 개선 진행 시
