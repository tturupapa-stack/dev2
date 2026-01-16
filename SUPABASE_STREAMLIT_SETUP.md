# Supabase와 Streamlit 연동 설정 가이드

## 개요
이 문서는 Supabase 데이터베이스와 Streamlit 앱을 연동하는 방법을 설명합니다.

## 제공된 Supabase 설정

```
NEXT_PUBLIC_SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2
```

## 설정 방법

### 1. 로컬 개발 환경 설정

#### 방법 A: `.env` 파일 사용 (권장)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2
```

**참고**: Next.js에서는 `NEXT_PUBLIC_` 접두사를 사용하지만, Streamlit/Python에서는 접두사 없이 사용합니다.

#### 방법 B: Streamlit Secrets 사용

`.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 추가하세요:

```toml
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2"
```

### 2. Streamlit Cloud 배포 시 설정

Streamlit Cloud에 배포하는 경우:

1. Streamlit Cloud 대시보드에 로그인
2. 앱 설정 페이지로 이동
3. "Secrets" 섹션에서 다음을 추가:

```toml
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2"
```

## 앱 동작 방식

Streamlit 앱(`ui_integration/app.py`)은 다음 순서로 Supabase 설정을 찾습니다:

1. **Streamlit Secrets** (`.streamlit/secrets.toml` 또는 Streamlit Cloud Secrets)
2. **환경 변수** (`.env` 파일 또는 시스템 환경 변수)

설정을 찾지 못하면 자동으로 목업 데이터(`mock_data.py`)를 사용합니다.

## 파일 구조

```
ui_integration/
├── app.py                 # Streamlit 메인 앱 (Supabase 연동)
├── supabase_data.py      # Supabase 데이터 연동 모듈
├── mock_data.py          # 목업 데이터 (백업용)
└── requirements.txt      # 필요한 패키지 목록
```

## 테스트 방법

### 로컬에서 테스트

```bash
cd ui_integration
streamlit run app.py
```

### Supabase 연결 확인

앱 실행 시 사이드바에 다음 중 하나가 표시됩니다:
- ✅ **Supabase 연동 활성화**: Supabase에서 데이터를 가져오고 있습니다
- ⚠️ **목업 데이터 사용 중**: Supabase 연결 실패, 목업 데이터 사용

## 문제 해결

### 연결 실패 시

1. **환경 변수 확인**
   ```bash
   # Windows PowerShell
   $env:SUPABASE_URL
   $env:SUPABASE_ANON_KEY
   
   # Linux/Mac
   echo $SUPABASE_URL
   echo $SUPABASE_ANON_KEY
   ```

2. **`.env` 파일 위치 확인**
   - 프로젝트 루트 디렉토리에 있어야 합니다
   - `ui_integration/` 폴더가 아닌 상위 디렉토리에 위치

3. **Supabase 프로젝트 상태 확인**
   - Supabase 대시보드에서 프로젝트가 활성화되어 있는지 확인
   - API 키가 올바른지 확인

4. **네트워크 확인**
   - 방화벽이나 프록시 설정 확인
   - Supabase URL이 접근 가능한지 확인

### 데이터가 표시되지 않는 경우

1. Supabase 데이터베이스에 `products`와 `reviews` 테이블이 있는지 확인
2. 테이블에 데이터가 있는지 확인
3. RLS (Row Level Security) 정책이 올바르게 설정되어 있는지 확인

## 추가 리소스

- [Supabase 공식 문서](https://supabase.com/docs)
- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Supabase Python 클라이언트](https://github.com/supabase/supabase-py)
