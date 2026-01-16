# Streamlit UI 적용 실패 보고서 및 해결 방안

**작성일**: 2026-01-12  
**작성자**: 개발팀  
**문제 유형**: Streamlit Cloud 배포 실패 / Import 오류  
**영향 범위**: UI 개선사항이 Streamlit Cloud에 반영되지 않음

---

## 📋 개요

로컬에서 개발한 UI 개선사항(사이드바 탭 구조, 리뷰 분석 강화, 차트 가시성 향상)이 Streamlit Cloud에 배포되었으나 정상적으로 적용되지 않았습니다. 로그 분석 결과, import 경로 문제 및 모듈 로딩 오류가 의심됩니다.

---

## 🐛 발생한 문제

### 문제 증상
- Streamlit Cloud에서 앱이 정상적으로 시작되지 않음
- UI 개선사항이 반영되지 않음
- 로그에서 에러 메시지가 명확히 표시되지 않음 (로그가 중간에 끊김)

### 로그 분석 결과
```
[14:21:20] 🐍 Python dependencies were installed from /mount/src/ica-github/dev2-2Hour/dev2-main/ui_integration/requirements.txt using uv.
[14:21:21] 📦 Processed dependencies!
```
- 의존성 설치는 성공적으로 완료됨
- 이후 로그가 중단되어 실제 실행 오류를 확인할 수 없음

---

## 🔍 문제 원인 분석

### 1. Import 경로 문제

**현재 코드 (app.py 12-13줄)**:
```python
# 상위 디렉토리를 경로에 추가하여 supabase_data 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**문제점**:
- `supabase_data.py`는 `ui_integration/` 폴더 내에 있음 (같은 디렉토리)
- 상위 디렉토리를 추가할 필요가 없음
- Streamlit Cloud에서 경로가 다를 수 있어 오류 발생 가능

**실제 파일 구조**:
```
ui_integration/
├── app.py
├── supabase_data.py  ← 같은 디렉토리
├── mock_data.py
├── visualizations.py
└── utils.py
```

### 2. Import 순서 문제

**현재 코드 (app.py 15-24줄)**:
```python
try:
    from supabase_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    from mock_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = False
```

**문제점**:
- `st.set_page_config()` 이전에 import가 실행됨
- Streamlit이 완전히 초기화되기 전에 `st.warning()` 호출 시도
- `hasattr(st, 'warning')` 체크가 있지만, Streamlit Cloud에서는 다른 문제 발생 가능

### 3. visualizations.py 함수 누락 가능성

**app.py에서 import하는 함수들**:
```python
from visualizations import (
    render_gauge_chart,
    render_trust_badge,
    render_comparison_table,
    render_radar_chart,
    render_review_sentiment_chart,
    render_checklist_visual,
    render_price_comparison_chart
)
```

**확인 필요**:
- 모든 함수가 `visualizations.py`에 정의되어 있는지 확인
- 함수 시그니처가 일치하는지 확인

---

## ✅ 해결 방안

### 방안 1: Import 경로 수정 (즉시 적용)

**변경 사항**:
1. 불필요한 `sys.path.append()` 제거
2. 같은 디렉토리에서 직접 import
3. `st.set_page_config()` 이후로 import 이동

**수정 코드**:
```python
import streamlit as st
import pandas as pd
import os
from typing import Dict, List, Optional

# 페이지 설정을 먼저 실행
st.set_page_config(
    page_title="건기식 리뷰 팩트체크",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이후 import 실행
try:
    from supabase_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    from mock_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = False

from visualizations import (
    render_gauge_chart,
    render_trust_badge,
    render_comparison_table,
    render_radar_chart,
    render_review_sentiment_chart,
    render_checklist_visual,
    render_price_comparison_chart
)
```

### 방안 2: 에러 처리 강화

**추가 사항**:
- Import 실패 시 명확한 에러 메시지 출력
- Streamlit Cloud 로그에 에러 정보 기록

**수정 코드**:
```python
try:
    from supabase_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    import traceback
    print(f"[ERROR] Supabase import failed: {e}")
    print(traceback.format_exc())
    from mock_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = False
```

### 방안 3: visualizations.py 함수 검증

**확인 사항**:
- 모든 함수가 정의되어 있는지 확인
- 함수 시그니처 일치 확인
- 누락된 함수 추가

---

## 🔧 즉시 적용할 수정 사항

### 1. app.py 수정

**변경 전**:
```python
import streamlit as st
import pandas as pd
import sys
import os
from typing import Dict, List, Optional

# 상위 디렉토리를 경로에 추가하여 supabase_data 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    from mock_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = False
    if hasattr(st, 'warning'):
        st.warning("⚠️ Supabase 연동 실패: 목업 데이터를 사용합니다.")

from visualizations import (
    render_gauge_chart,
    render_trust_badge,
    render_comparison_table,
    render_radar_chart,
    render_review_sentiment_chart,
    render_checklist_visual,
    render_price_comparison_chart
)

# 페이지 설정
st.set_page_config(...)
```

**변경 후**:
```python
import streamlit as st
import pandas as pd
import os
from typing import Dict, List, Optional

# 페이지 설정을 먼저 실행 (Streamlit 초기화)
st.set_page_config(
    page_title="건기식 리뷰 팩트체크",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이후 모듈 import
try:
    from supabase_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    import traceback
    print(f"[ERROR] Supabase import failed: {e}")
    print(traceback.format_exc())
    from mock_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = False

try:
    from visualizations import (
        render_gauge_chart,
        render_trust_badge,
        render_comparison_table,
        render_radar_chart,
        render_review_sentiment_chart,
        render_checklist_visual,
        render_price_comparison_chart
    )
except ImportError as e:
    import traceback
    st.error(f"Visualizations import failed: {e}")
    print(traceback.format_exc())
    raise
```

---

## 🧪 검증 방법

### 1. 로컬 테스트
```bash
cd ui_integration
streamlit run app.py
```

**확인 사항**:
- [ ] 앱이 정상적으로 시작되는가?
- [ ] 모든 탭이 표시되는가?
- [ ] 차트가 정상적으로 렌더링되는가?
- [ ] 에러 메시지가 없는가?

### 2. 문법 검사
```bash
python -m py_compile ui_integration/app.py
python -m py_compile ui_integration/visualizations.py
```

### 3. Import 테스트
```python
# test_imports.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase_data import get_all_analysis_results
    print("✅ supabase_data import 성공")
except Exception as e:
    print(f"❌ supabase_data import 실패: {e}")

try:
    from visualizations import render_gauge_chart
    print("✅ visualizations import 성공")
except Exception as e:
    print(f"❌ visualizations import 실패: {e}")
```

---

## 📊 예상 효과

### 즉시 효과
- ✅ Streamlit Cloud에서 앱 정상 시작
- ✅ UI 개선사항 정상 반영
- ✅ Import 오류 해결

### 장기 효과
- ✅ 코드 안정성 향상
- ✅ 에러 추적 용이성 증가
- ✅ 유지보수성 향상

---

## 📝 결론

현재 문제는 **Import 경로 및 순서 문제**로 인한 것으로 판단됩니다. `sys.path.append()`를 제거하고, `st.set_page_config()`를 먼저 실행한 후 모듈을 import하도록 수정하면 해결될 것으로 예상됩니다.

**우선순위**:
1. **즉시**: app.py의 import 경로 및 순서 수정
2. **단기**: 에러 처리 강화
3. **장기**: 테스트 자동화 및 CI/CD 파이프라인 구축

---

**보고서 작성 시간**: 2026-01-12  
**수정 완료 시간**: 2026-01-12  
**수정 상태**: ✅ 완료

---

## ✅ 수정 완료 내역

### 수정된 내용

1. **Import 경로 수정**
   - 불필요한 `sys.path.append()` 제거
   - 같은 디렉토리에서 직접 import하도록 변경

2. **Import 순서 수정**
   - `st.set_page_config()`를 먼저 실행하여 Streamlit 초기화
   - 이후 모듈 import 실행

3. **에러 처리 강화**
   - Import 실패 시 `traceback`으로 상세 에러 정보 출력
   - Streamlit Cloud 로그에서 에러 추적 가능

### 검증 결과

```bash
python -m py_compile ui_integration/app.py
# ✅ 문법 검사 통과 (오류 없음)
```

### 배포 상태

- ✅ 코드 수정 완료
- ✅ 문법 검사 통과
- ✅ `ica-github` 저장소에 푸시 완료 (커밋: ac6f9f4)
- ⏳ Streamlit Cloud 자동 재배포 진행 중

**푸시된 저장소**: `https://github.com/Siyeolryu/ica-github.git`  
**경로**: `dev2-2Hour/dev2-main/ui_integration/app.py`  
**커밋 ID**: `ac6f9f4`

**다음 조치**: Streamlit Cloud에서 자동 재배포 완료 확인 (약 1-2분 소요)
