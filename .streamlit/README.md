# Streamlit 설정 디렉토리

이 디렉토리는 Streamlit 앱의 설정 파일을 포함합니다.

## 파일 설명

### `secrets.toml`
- **민감한 정보 저장**: API 키, 데이터베이스 연결 정보 등
- **Git에 커밋되지 않음**: `.gitignore`에 포함되어 있음
- **로컬 개발용**: 로컬에서 Streamlit 앱을 실행할 때 사용

### `secrets.toml.example`
- **예시 파일**: secrets.toml의 템플릿
- **Git에 커밋됨**: 다른 개발자들이 참고할 수 있도록
- **실제 값 없음**: 실제 API 키는 포함하지 않음

### `config.toml`
- **앱 설정**: 테마, 서버 설정 등
- **Git에 커밋됨**: 공유 가능한 설정

## 설정 방법

### 1. secrets.toml 생성

```bash
# 예시 파일 복사
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

### 2. secrets.toml 편집

`.streamlit/secrets.toml` 파일을 열어 실제 API 키와 URL을 입력하세요:

```toml
# Supabase 설정
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-actual-anon-key"
SUPABASE_SERVICE_ROLE_KEY = "your-actual-service-role-key"

# Anthropic Claude API 설정
ANTHROPIC_API_KEY = "your-actual-api-key"
```

### 3. Supabase 키 확인 방법

1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택
3. **Settings** → **API** 메뉴
4. **Project URL**: `SUPABASE_URL`에 입력
5. **anon/public key**: `SUPABASE_ANON_KEY`에 입력
6. **service_role key**: `SUPABASE_SERVICE_ROLE_KEY`에 입력

### 4. Anthropic API 키 확인 방법

1. [Anthropic Console](https://console.anthropic.com/) 접속
2. **API Keys** 메뉴
3. 새 API 키 생성 또는 기존 키 복사

## 코드에서 사용 방법

```python
import streamlit as st

# 방법 1: 직접 접근
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_ANON_KEY"]
api_key = st.secrets["ANTHROPIC_API_KEY"]

# 방법 2: 안전한 접근 (키가 없을 경우 대비)
supabase_url = st.secrets.get("SUPABASE_URL", "default_value")
```

## Streamlit Cloud 배포 시

Streamlit Cloud에 배포할 때는 웹 대시보드에서 secrets를 설정합니다:

1. Streamlit Cloud 대시보드 접속
2. 앱 선택 → **Settings** → **Secrets**
3. TOML 형식으로 secrets 입력:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
ANTHROPIC_API_KEY = "your-api-key"
```

## 주의사항

- ⚠️ **secrets.toml은 절대 Git에 커밋하지 마세요**
- ✅ **secrets.toml.example은 Git에 커밋 가능**
- 🔒 **API 키는 절대 공유하지 마세요**
