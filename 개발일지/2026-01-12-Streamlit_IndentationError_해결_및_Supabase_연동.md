# 개발일지: Streamlit IndentationError 해결 및 Supabase 연동 완료

**작성일**: 2026-01-12  
**작성자**: 개발팀  
**관련 이슈**: Streamlit Cloud 배포 시 IndentationError 발생, Supabase 연동 설정

---

## 📋 개요

Streamlit Cloud에 배포된 앱에서 `IndentationError`가 발생하여 앱 실행이 중단되었습니다. 또한 Supabase와 Streamlit 앱의 연동 설정을 완료했습니다.

---

## 🐛 발생한 문제

### 1. IndentationError 발생

**에러 메시지**:
```
File "/mount/src/ica-github/dev2-2Hour/dev2-main/ui_integration/app.py", line 139
    st.markdown("### 제품 검색")
IndentationError: expected an indented block after 'with' statement on line 138
```

**원인 분석**:
- 138번 라인의 `with` 문 다음에 들여쓰기가 누락되었거나 잘못되었습니다
- Python은 `with` 문 다음에 반드시 들여쓰기된 코드 블록이 필요합니다
- 빈 줄이나 들여쓰기가 없는 코드가 `with` 블록 다음에 오면 이 에러가 발생합니다

**영향**:
- Streamlit Cloud에서 앱이 실행되지 않음
- 사용자가 앱에 접근할 수 없음

---

## ✅ 해결 방법

### 1. 코드 구조 확인 및 수정

**문제가 있는 코드 패턴**:
```python
with st.sidebar:
    # 빈 줄이나 잘못된 들여쓰기
st.markdown("### 제품 검색")  # 들여쓰기 없음 - 에러 발생!
```

**수정된 코드**:
```python
with st.sidebar:
    st.markdown("### 🔎 제품 검색")  # 올바른 들여쓰기
    
    search_query = st.text_input(
        "제품명 또는 브랜드 검색",
        placeholder="예: NOW Foods, Lutein...",
        key="search"
    )
    
    st.markdown("---")
    
    st.markdown("### ℹ️ 신뢰도 등급 안내")
    # ... 나머지 코드
```

### 2. 들여쓰기 규칙 확인

Python에서 `with` 문 사용 시 주의사항:

1. **`with` 문 다음에는 반드시 들여쓰기된 코드가 있어야 함**
   ```python
   with st.sidebar:  # ✅ 올바름
       st.markdown("...")
   ```

2. **빈 `with` 블록은 허용되지 않음**
   ```python
   with st.sidebar:  # ❌ 에러 발생
   # 아무 코드도 없음
   ```

3. **들여쓰기는 일관되게 유지해야 함** (보통 4칸 또는 탭)
   ```python
   with st.sidebar:
       st.markdown("...")  # 4칸 들여쓰기
       st.text_input(...)  # 4칸 들여쓰기
   ```

### 3. 파일 검증 방법

배포 전에 다음을 확인:

```bash
# Python 문법 검사
python -m py_compile ui_integration/app.py

# 또는
python -m flake8 ui_integration/app.py --select=E
```

---

## 🔧 Supabase 연동 설정

### 1. 환경 변수 설정

**로컬 개발 환경** (`.env` 파일):
```env
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2
```

**Streamlit Cloud** (Secrets 설정):
```toml
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2"
```

### 2. 코드 수정 사항

**`ui_integration/app.py`**:
- Supabase 연동 시도 로직 추가
- 실패 시 자동으로 목업 데이터로 전환
- 연결 상태를 사이드바에 표시

**`ui_integration/supabase_data.py`**:
- Streamlit Secrets와 환경 변수 모두 지원
- REST API를 통한 데이터 가져오기 구현
- 에러 처리 및 폴백 로직 포함

### 3. 의존성 추가

**`ui_integration/requirements.txt`**:
```
streamlit>=1.31.0
plotly>=5.18.0
pandas>=2.1.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 📝 변경 사항 요약

### 수정된 파일

1. **`ui_integration/app.py`**
   - Supabase 연동 로직 추가
   - 에러 처리 개선
   - 들여쓰기 검증

2. **`ui_integration/supabase_data.py`** (신규 생성)
   - Supabase 데이터 연동 모듈
   - Streamlit Cloud 호환성 확보

3. **`.streamlit/secrets.toml.example`**
   - Supabase 설정 예시 추가

4. **`ui_integration/requirements.txt`**
   - `requests`, `python-dotenv` 패키지 추가

5. **`SUPABASE_STREAMLIT_SETUP.md`** (신규 생성)
   - Supabase 연동 설정 가이드 문서

---

## 🧪 테스트 결과

### 로컬 테스트
```bash
cd ui_integration
streamlit run app.py
```

**결과**:
- ✅ Supabase 연결 성공 시: "✅ Supabase 연동 활성화" 표시
- ✅ Supabase 연결 실패 시: 자동으로 목업 데이터 사용, "⚠️ 목업 데이터 사용 중" 표시
- ✅ 앱 정상 실행 확인

### 배포 전 체크리스트

- [x] Python 문법 검사 통과
- [x] 들여쓰기 일관성 확인
- [x] Supabase 연결 테스트
- [x] 에러 처리 로직 검증
- [x] 환경 변수 설정 확인

---

## 🚀 배포 가이드

### Streamlit Cloud 배포 시

1. **Secrets 설정**:
   - Streamlit Cloud 대시보드 → Settings → Secrets
   - 위의 `secrets.toml` 내용 추가

2. **배포 확인**:
   - 배포 후 앱 로드 확인
   - 사이드바에서 Supabase 연결 상태 확인
   - 데이터 로드 테스트

3. **문제 발생 시**:
   - Streamlit Cloud 로그 확인
   - Secrets 설정 재확인
   - 환경 변수 이름 확인 (대소문자 구분)

---

## 📚 참고 자료

### Python 들여쓰기 가이드
- [PEP 8 - Style Guide](https://pep8.org/#indentation)
- Python은 들여쓰기로 코드 블록을 구분합니다
- 일반적으로 4칸 공백을 사용합니다

### Supabase 연동 문서
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

### 에러 해결 팁
- IDE에서 들여쓰기 표시 기능 활성화
- 코드 포맷터 사용 (Black, autopep8)
- 배포 전 로컬에서 문법 검사 실행

---

## 🔍 향후 개선 사항

1. **코드 품질 관리**
   - CI/CD 파이프라인에 문법 검사 추가
   - 자동 코드 포맷팅 적용
   - 린터 설정 강화

2. **에러 모니터링**
   - Streamlit Cloud 로그 모니터링
   - 에러 알림 시스템 구축
   - 사용자 피드백 수집

3. **문서화**
   - API 문서 보완
   - 배포 가이드 상세화
   - 트러블슈팅 가이드 작성

---

## ✅ 완료 체크리스트

- [x] IndentationError 원인 분석
- [x] 코드 수정 및 검증
- [x] Supabase 연동 설정 완료
- [x] 환경 변수 설정 가이드 작성
- [x] 로컬 테스트 완료
- [x] 개발일지 작성
- [ ] Streamlit Cloud 재배포 및 검증

---

## 📌 결론

IndentationError는 Python의 기본 문법 규칙을 준수하지 않아 발생한 문제였습니다. `with` 문 다음에는 반드시 들여쓰기된 코드 블록이 필요하며, 이를 준수함으로써 문제를 해결했습니다.

또한 Supabase와 Streamlit의 연동을 완료하여 실제 데이터베이스에서 데이터를 가져올 수 있도록 설정했습니다. 연결 실패 시 자동으로 목업 데이터를 사용하는 폴백 메커니즘을 구현하여 안정성을 높였습니다.

**다음 단계**: Streamlit Cloud에 재배포하여 실제 환경에서 동작을 확인하겠습니다.
