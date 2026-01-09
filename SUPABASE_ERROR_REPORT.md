# Supabase 연동 오류 보고서

**작성일**: 2026-01-09
**앱 URL**: https://ica-app-exygnp32igpx6sqravtn8t.streamlit.app/
**Supabase 프로젝트**: https://supabase.com/dashboard/project/bvowxbpqtfpkkxkzsumf

---

## 1. 문제 요약

Streamlit Cloud에 배포된 앱에서 Supabase 데이터가 표시되지 않음.

---

## 2. 원인 분석

### 2.1 로컬 환경 테스트 결과
| 항목 | 상태 | 비고 |
|------|------|------|
| Supabase 연결 | ✅ 성공 | REST API 정상 응답 |
| products 테이블 | ✅ 성공 | 5개 제품 확인 |
| reviews 테이블 | ✅ 성공 | 리뷰 데이터 확인 |

```
=== Supabase 연결 테스트 ===
URL: https://bvowxbpqtfpkkxkzsumf.supabase.co
--- products 테이블 ---
Status: 200
데이터 수: 5
  - ID: 14, Brand: iHerb (California Gold Nutrition)
  - ID: 15, Brand: Doctor's Best
  - ID: 16, Brand: Solaray
```

### 2.2 발견된 문제점

#### 문제 1: 모듈 로딩 시점 문제
```python
# 기존 코드 (문제)
SUPABASE_URL, SUPABASE_KEY = _get_config()  # 모듈 임포트 시 즉시 실행
```
- Streamlit Cloud에서 모듈이 임포트되는 시점에 `st.secrets`가 아직 준비되지 않았을 수 있음
- 설정값이 `None`으로 초기화되어 이후 API 호출 실패

#### 문제 2: 예외 처리 누락
```python
# 기존 코드 (문제)
except:
    pass  # 모든 에러를 무시 → 디버깅 불가
```

#### 문제 3: Secrets 설정 형식
Streamlit Cloud secrets는 TOML 형식이어야 함:
```toml
# 올바른 형식 (secrets.toml)
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2"
```

---

## 3. 수정 내용

### 3.1 Lazy Loading 도입
```python
# 수정된 코드
_config_cache = None

def _get_cached_config():
    global _config_cache
    if _config_cache is None:
        _config_cache = _get_config()
    return _config_cache
```
- 설정을 실제 사용 시점에 로드 (앱 실행 후)
- Streamlit의 `st.secrets`가 준비된 후에 접근

### 3.2 디버그 정보 추가
```python
if DEBUG:
    st.sidebar.write(f"Config source: {source}")
    st.sidebar.write(f"URL loaded: {'Yes' if supabase_url else 'No'}")
```
- 사이드바에 설정 상태 표시
- 문제 발생 시 원인 파악 용이

### 3.3 에러 메시지 개선
```python
if not supabase_url or not supabase_key:
    st.error("Supabase 연결 실패: secrets 설정을 확인하세요.")
    st.info("Settings > Secrets에서 SUPABASE_URL과 SUPABASE_ANON_KEY를 설정하세요.")
```

---

## 4. 확인 필요 사항

### 4.1 Streamlit Cloud Secrets 설정 확인

1. https://share.streamlit.io 접속
2. 앱 선택 → Settings → Secrets
3. 아래 내용이 **정확히** 입력되어 있는지 확인:

```toml
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2"
```

**주의사항**:
- 따옴표(`"`) 포함 필수
- 키 이름 대소문자 정확히 일치
- 공백이나 줄바꿈 없이 입력

### 4.2 앱 재시작

Secrets 수정 후 반드시 **Reboot app** 실행

---

## 5. 테스트 방법

앱 접속 후 사이드바에서 다음 정보 확인:
- `Config source: streamlit_secrets` → 정상
- `Config source: none` → Secrets 설정 오류

---

## 6. 관련 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| supabase_data.py | `/supabase_data.py` | Supabase API 연동 모듈 |
| app.py | `/app.py` | Streamlit 메인 앱 |
| requirements.txt | `/requirements.txt` | 패키지 의존성 |

---

## 7. 커밋 이력

| 커밋 | 설명 |
|------|------|
| `5c3707f` | fix: Improve Supabase config loading with debug info |
| `35c6322` | feat: Add app files to root for Streamlit Cloud deployment |
| `95a9396` | feat: Add Supabase integration for Streamlit Cloud |

---

## 8. 결론

로컬 환경에서는 Supabase 연결이 정상 작동하므로, **Streamlit Cloud의 Secrets 설정**을 다시 확인해야 합니다. 수정된 코드가 배포되면 사이드바에 디버그 정보가 표시되어 문제 원인을 파악할 수 있습니다.
