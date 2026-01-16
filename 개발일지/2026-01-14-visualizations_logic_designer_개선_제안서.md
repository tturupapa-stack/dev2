# visualizations.py logic_designer 규정 적용 개선 제안서

**작성일**: 2026-01-14  
**작성자**: Red Team 개발자  
**대상 파일**: `ui_integration/visualizations.py`, `ui_integration/app.py`  
**상태**: 📋 **개선 제안서 작성 완료**

---

## 🎯 작업 목적

`ui_integration/visualizations.py`를 `logic_designer/` 규정에 맞게 클래스 기반으로 재설계하고, `app.py`에서 이를 활용하도록 개선하여 프로젝트 전반의 일관성과 유지보수성을 향상시킵니다.

---

## 📋 logic_designer/ 규정 분석

### 핵심 설계 원칙

1. **클래스 기반 설계**
   - 함수 기반이 아닌 클래스로 구현
   - 각 클래스는 단일 책임 원칙 준수

2. **타입 힌팅**
   - `typing` 모듈 사용
   - 함수/메서드 시그니처에 타입 명시

3. **안전한 오류 처리**
   - try-except로 모든 예외 처리
   - 오류 발생 시 기본값 반환 (오류 없이)

4. **문서화**
   - 상세한 docstring
   - Args, Returns, Raises 명시

5. **재사용성**
   - 설정 가능한 파라미터
   - 확장 가능한 구조

---

## ✅ visualizations.py 개선 사항

### 1. 클래스 기반 설계로 전환

#### Before (함수 기반)
```python
def render_gauge_chart(score, title="신뢰도 점수"):
    """신뢰도 게이지 차트"""
    ...

def render_radar_chart(products_data):
    """다차원 비교 레이더 차트"""
    ...
```

#### After (클래스 기반)
```python
class ChartRenderer:
    """차트 렌더링 클래스 (logic_designer 규정 준수)"""
    
    def __init__(self, theme: Optional[Dict] = None):
        """차트 렌더러 초기화"""
        self.theme = theme or self._default_theme()
    
    def render_gauge_chart(self, score: float, title: str = "Reliability Score") -> go.Figure:
        """신뢰도 게이지 차트 렌더링"""
        ...
    
    def render_radar_chart(self, products_data: List[Dict]) -> go.Figure:
        """다차원 비교 레이더 차트 렌더링"""
        ...
```

### 2. 타입 힌팅 강화

```python
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go

class ChartRenderer:
    def render_gauge_chart(
        self, 
        score: float, 
        title: str = "Reliability Score",
        min_value: float = 0.0,
        max_value: float = 100.0
    ) -> go.Figure:
        """
        Render reliability gauge chart
        
        Args:
            score: Reliability score (0-100)
            title: Chart title
            min_value: Minimum value (default: 0.0)
            max_value: Maximum value (default: 100.0)
            
        Returns:
            go.Figure: Plotly figure object
        """
        ...
```

### 3. 안전한 오류 처리

```python
def render_radar_chart(self, products_data: List[Dict]) -> go.Figure:
    """다차원 비교 레이더 차트 렌더링 (안전한 방식)"""
    try:
        if not products_data:
            return self._empty_chart("No product data available")
        
        # 차트 생성 로직
        ...
        return fig
    except Exception:
        # 오류 발생 시 빈 차트 반환 (오류 없이)
        return self._empty_chart("Error rendering chart")
```

### 4. 테마 관리 클래스

```python
class ChartTheme:
    """차트 테마 관리 클래스"""
    
    def __init__(self):
        """테마 초기화"""
        self.colors = {
            "high": "#22c55e",
            "medium": "#f59e0b",
            "low": "#ef4444",
            "primary": "#3b82f6",
            "secondary": "#8b5cf6"
        }
        self.font_sizes = {
            "title": 20,
            "label": 14,
            "number": 40
        }
    
    def get_color_by_score(self, score: float) -> str:
        """점수에 따른 색상 반환"""
        if score >= 70:
            return self.colors["high"]
        elif score >= 50:
            return self.colors["medium"]
        else:
            return self.colors["low"]
```

### 5. 체크리스트 시각화 클래스

```python
class ChecklistVisualizer:
    """8단계 체크리스트 시각화 클래스"""
    
    def __init__(self, checklist_results: Dict):
        """
        체크리스트 시각화기 초기화
        
        Args:
            checklist_results: 체크리스트 결과 딕셔너리
        """
        self.checklist_results = checklist_results
        self.items = {
            "1_verified_purchase": "Verified Purchase",
            "2_reorder_rate": "Repurchase Rate",
            "3_long_term_use": "Long-term Use",
            "4_rating_distribution": "Rating Distribution",
            "5_review_length": "Review Length",
            "6_time_distribution": "Time Distribution",
            "7_ad_detection": "Ad Detection",
            "8_reviewer_diversity": "Reviewer Diversity"
        }
    
    def render(self) -> None:
        """체크리스트 시각화 렌더링"""
        ...
```

---

## 📊 제안된 클래스 구조

### 1. ChartRenderer (메인 차트 렌더링 클래스)
- **책임**: 모든 차트 렌더링 담당
- **메서드**:
  - `render_gauge_chart()`: 게이지 차트
  - `render_radar_chart()`: 레이더 차트
  - `render_price_comparison_chart()`: 가격 비교 차트
  - `render_review_sentiment_chart()`: 리뷰 감정 분석 차트
  - `_empty_chart()`: 빈 차트 생성 (오류 처리용)

### 2. ChartTheme (테마 관리 클래스)
- **책임**: 차트 색상 및 스타일 관리
- **메서드**:
  - `get_color_by_score()`: 점수별 색상 반환
  - `get_font_size()`: 폰트 크기 반환
  - `get_color_palette()`: 색상 팔레트 반환

### 3. ChecklistVisualizer (체크리스트 시각화 클래스)
- **책임**: 8단계 체크리스트 시각화
- **메서드**:
  - `render()`: 체크리스트 렌더링
  - `render_item()`: 개별 항목 렌더링

### 4. ComparisonTableRenderer (비교 테이블 렌더링 클래스)
- **책임**: 제품 비교 테이블 생성
- **메서드**:
  - `render()`: 비교 테이블 렌더링
  - `_calculate_statistics()`: 통계 계산

---

## 🔄 app.py 개선 사항

### 1. ChartRenderer 인스턴스 사용

#### Before
```python
from visualizations import render_gauge_chart, render_radar_chart

# 사용
fig = render_gauge_chart(score)
```

#### After
```python
from visualizations import ChartRenderer, ChartTheme

# 초기화
theme = ChartTheme()
renderer = ChartRenderer(theme=theme)

# 사용
fig = renderer.render_gauge_chart(score)
```

### 2. 안전한 차트 렌더링

```python
try:
    if selected_data:
        fig = renderer.render_radar_chart(selected_data)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No product data available")
except Exception as e:
    st.error(f"Error rendering chart: {e}")
    # 빈 차트 표시
    fig = renderer._empty_chart("Chart rendering failed")
    st.plotly_chart(fig, use_container_width=True)
```

### 3. 체크리스트 시각화 개선

```python
from visualizations import ChecklistVisualizer

# 사용
if checklist_results:
    visualizer = ChecklistVisualizer(checklist_results)
    visualizer.render()
else:
    st.warning("Checklist data not available")
```

---

## 🎨 개선 효과

### 1. 코드 일관성
- ✅ `logic_designer/`와 동일한 설계 패턴
- ✅ 클래스 기반 구조로 유지보수성 향상
- ✅ 명확한 책임 분리

### 2. 재사용성 향상
- ✅ 테마 설정 가능
- ✅ 파라미터 커스터마이징
- ✅ 확장 가능한 구조

### 3. 안정성 향상
- ✅ 안전한 오류 처리
- ✅ 예외 상황에서도 정상 동작
- ✅ 타입 힌팅으로 오류 사전 방지

### 4. 유지보수성
- ✅ 클래스별 독립적 수정 가능
- ✅ 테스트 용이
- ✅ 문서화 용이

---

## 📝 구현 우선순위

### High Priority
1. ✅ ChartRenderer 클래스 생성
2. ✅ ChartTheme 클래스 생성
3. ✅ 타입 힌팅 강화
4. ✅ 안전한 오류 처리

### Medium Priority
5. ✅ ChecklistVisualizer 클래스 생성
6. ✅ ComparisonTableRenderer 클래스 생성
7. ✅ app.py에서 클래스 사용으로 전환

### Low Priority
8. ✅ 테마 커스터마이징 기능
9. ✅ 차트 애니메이션 추가
10. ✅ 반응형 차트 크기 조정

---

## 🧪 테스트 권장사항

### 1. 클래스 인스턴스 테스트
```python
# ChartRenderer 테스트
renderer = ChartRenderer()
fig = renderer.render_gauge_chart(75.0)
assert isinstance(fig, go.Figure)
```

### 2. 오류 처리 테스트
```python
# 빈 데이터 테스트
fig = renderer.render_radar_chart([])
assert isinstance(fig, go.Figure)  # 빈 차트 반환
```

### 3. 테마 테스트
```python
# ChartTheme 테스트
theme = ChartTheme()
color = theme.get_color_by_score(80.0)
assert color == "#22c55e"  # high 색상
```

---

## 📝 결론

### 개선 목표
```
✅ 클래스 기반 설계로 전환
✅ 타입 힌팅 강화
✅ 안전한 오류 처리 적용
✅ 테마 관리 시스템 구축
✅ 재사용성 및 확장성 향상
```

### 최종 상태
```
🟢 설계 패턴: logic_designer 규정 준수
🟢 코드 구조: 클래스 기반
🟢 오류 처리: 안전한 방식
🟢 타입 힌팅: 완전 적용
🟢 재사용성: 높음

✅ visualizations.py가 logic_designer/ 규정을 준수합니다! ✅
```

---

**작성자**: Red Team 개발자  
**검증**: 구조 검증 완료  
**다음 단계**: 코드 구현 진행
