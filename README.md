# 건기식 리뷰 팩트체크 시스템

건강기능식품 리뷰의 신뢰도를 정량적으로 평가하고, AI 약사 페르소나를 통해 전문적인 분석을 제공하는 **Streamlit 웹 대시보드** 시스템입니다.

## 📖 프로젝트 소개

이 프로젝트는 iHerb 등 온라인 쇼핑몰에서 수집한 건강기능식품 리뷰를 분석하여:
- **8단계 체크리스트** 기반 신뢰도 검증
- **AI 약사 분석** (Claude AI 기반)
- **제품 비교 분석** (최대 3개 제품 동시 비교)
- **시각화 차트** (레이더 차트, 가격 비교, 세부 지표)

## 🚀 빠른 시작 (Quick Start)

### 1. 저장소 클론

```bash
git clone https://github.com/Siyeolryu/ica-github.git
cd ica-github/dev2-2Hour/dev2-main
```

### 2. 의존성 설치

```bash
# 프로젝트 루트 의존성
pip install -r requirements.txt

# UI 의존성
cd ui_integration
pip install -r requirements.txt
```

### 3. 환경 변수 설정

#### Streamlit 앱용 (권장)

`.streamlit/secrets.toml` 파일을 생성하세요:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"  # 선택사항
ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

**위치**: `ui_integration/.streamlit/secrets.toml`

**Supabase 키 확인 방법:**
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택 → Settings → API
3. **Project URL**: `SUPABASE_URL`에 입력
4. **anon/public key**: `SUPABASE_ANON_KEY`에 입력
5. **service_role key**: `SUPABASE_SERVICE_ROLE_KEY`에 입력 (관리자 권한)

#### Python 스크립트용 (선택사항)

프로젝트 루트에 `.env` 파일을 생성:

```env
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Streamlit 앱 실행

```bash
cd ui_integration
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.

## ✨ 주요 기능

### 1. 제품 선택 및 비교

- **브랜드 선택**: 사이드바에서 브랜드 선택
- **메인 제품 선택**: 선택한 브랜드의 제품 목록에서 메인 제품 선택
- **비교 제품 자동 추천**: 메인 제품 선택 시 다른 브랜드 제품 2개 자동 추천
- **비교 제품 수동 선택**: 대시보드에서 비교 제품 직접 선택 가능
- **실시간 차트 업데이트**: 비교 제품 선택 시 모든 차트 자동 업데이트

### 2. 리뷰 팩트체크 (8단계 체크리스트)

1. **인증 구매 비율**: 인증된 구매 리뷰 비율 (목표: 70% 이상)
2. **재구매율**: 재구매 의사가 있는 리뷰 비율
3. **장기 사용**: 1개월 이상 사용한 리뷰 비율
4. **평점 분포**: 평점 분포의 자연스러움 (100% 5점은 의심)
5. **리뷰 길이**: 충분한 길이의 리뷰 비율 (목표: 50% 이상)
6. **시간 분포**: 리뷰 작성 시간의 자연스러운 분포
7. **광고 탐지**: 광고성 문구 탐지 비율
8. **리뷰어 다양성**: 다양한 리뷰어의 참여 비율 (목표: 80% 이상)

### 3. 시각화 분석 차트

- **레이더 차트**: 신뢰도, 재구매율, 장기사용, 평점, 리뷰다양성 다차원 비교
- **가격 및 신뢰도 비교**: 3개 제품의 가격과 신뢰도 점수 막대 그래프
- **세부 지표 비교표**: 모든 지표를 테이블로 비교
- **리뷰 감정 분석**: 리뷰 감정 분포 차트
- **평점 분포**: 제품별 평점 분포 시각화

### 4. AI 약사 분석

- **페르소나**: 15년 경력 임상 약사
- **AI 모델**: Anthropic Claude Sonnet 4.5
- **출력 항목**:
  - 요약
  - 효능 분석
  - 부작용 정보
  - 복용 권장사항
  - 주의사항
  - 신뢰도 점수

### 5. 고급 필터링

- **가격 범위 필터**: 슬라이더로 가격 범위 설정
- **평점 범위 필터**: 1-5점 범위 설정
- **리뷰 수 범위 필터**: 최소/최대 리뷰 수 설정
- **제품명/브랜드 검색**: 실시간 검색 기능
- **필터 상태 표시**: 활성 필터 개수 및 내용 표시
- **필터 초기화**: 원클릭 필터 리셋

## 📁 프로젝트 구조

```
team_projects_logic_D/
├── ui_integration/         # Streamlit 웹 대시보드 ⭐ 메인 기능
│   ├── app.py              # 메인 Streamlit 앱
│   ├── supabase_data.py    # Supabase 데이터 조회
│   ├── visualizations.py   # 차트 및 시각화 컴포넌트
│   ├── utils.py            # 유틸리티 함수
│   ├── requirements.txt    # UI 의존성
│   └── .streamlit/         # Streamlit 설정
│       ├── secrets.toml    # 환경 변수 (Git에 커밋하지 않음)
│       └── config.toml     # Streamlit 설정
├── core/                   # 핵심 모듈
│   ├── validator.py        # 신뢰도 검증 엔진
│   ├── analyzer.py         # AI 약사 분석 엔진
│   └── langchain_parser.py # LangChain 파서
├── database/               # 데이터베이스 모듈
│   ├── supabase_client.py  # Supabase 클라이언트
│   ├── schema.sql          # DB 스키마
│   └── test_crud.py        # CRUD 테스트
├── logic_designer/         # 로직 설계 모듈
│   ├── checklist.py        # 8단계 체크리스트
│   ├── trust_score.py      # 신뢰도 점수 계산
│   └── rating_analyzer.py  # 평점 분석
├── data_manager/           # 데이터 수집 및 업로드
│   └── db_uploader.py      # Supabase 업로드 스크립트
├── scripts/                 # 유틸리티 스크립트
│   ├── fix_products_ratings.py    # 제품 평점 업데이트
│   └── export_supabase_data.py    # 데이터 내보내기
├── 개발일지/               # 개발 로그
├── docs/                   # 프로젝트 문서
├── requirements.txt        # 프로젝트 의존성
├── SPEC.md                 # 기획서
├── CLAUDE.md               # AI 작업 지침
└── README.md               # 프로젝트 문서 (이 파일)
```

## 💻 사용 예제

### Streamlit 앱 사용 (권장)

```bash
cd ui_integration
streamlit run app.py
```

**웹 브라우저에서:**
1. 사이드바에서 브랜드 선택
2. 메인 제품 선택
3. 비교 제품 2개 자동 추천 또는 수동 선택
4. 리뷰 팩트체크 결과 및 차트 확인

### Python API 사용

```python
from ui_integration.supabase_data import (
    get_all_products,
    get_reviews_by_product,
    generate_checklist_results,
    generate_ai_analysis
)

# 제품 목록 조회
products = get_all_products()
print(f"총 {len(products)}개 제품")

# 특정 제품의 리뷰 조회
reviews = get_reviews_by_product(product_id=1)
print(f"리뷰 {len(reviews)}개")

# 8단계 체크리스트 생성
checklist = generate_checklist_results(reviews)
print(f"신뢰도 점수: {sum(item.get('rate', 0) for item in checklist.values()) / len(checklist) * 100:.1f}%")

# AI 약사 분석
ai_result = generate_ai_analysis(products[0], checklist)
print(f"요약: {ai_result.get('summary', 'N/A')}")
```

## 🗄️ 데이터베이스 스키마

### products 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `id` | INTEGER | 제품 ID (Primary Key) |
| `name` | TEXT | 제품명 |
| `brand` | TEXT | 브랜드명 |
| `price` | DECIMAL | 가격 (USD) |
| `rating_avg` | DECIMAL | 평균 평점 (1-5) |
| `rating_count` | INTEGER | 리뷰 수 |
| `category` | TEXT | 카테고리 |
| `product_url` | TEXT | 제품 링크 |
| `created_at` | TIMESTAMP | 생성일시 |

### reviews 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `id` | INTEGER | 리뷰 ID (Primary Key) |
| `product_id` | INTEGER | 제품 ID (Foreign Key) |
| `text` | TEXT | 리뷰 내용 |
| `rating` | INTEGER | 평점 (1-5) |
| `reviewer` | TEXT | 리뷰어 이름 |
| `verified` | BOOLEAN | 인증 구매 여부 |
| `reorder` | BOOLEAN | 재구매 의사 |
| `one_month_use` | BOOLEAN | 1개월 이상 사용 여부 |
| `date` | DATE | 리뷰 작성일 |
| `created_at` | TIMESTAMP | 생성일시 |

## 📊 신뢰도 점수 계산

8단계 체크리스트의 각 항목을 평가하여 종합 신뢰도 점수를 계산합니다:

```
종합 신뢰도 = (각 항목 통과율의 평균) × 100
```

각 항목은 통과/미흡 기준이 있으며, 통과율에 따라 신뢰도 점수가 결정됩니다.

## 🔧 트러블슈팅

### Supabase 연결 실패

**증상**: `ConnectionError` 또는 `401 Unauthorized`

**해결 방법**:
1. `.streamlit/secrets.toml` 파일 확인
2. `SUPABASE_URL`과 `SUPABASE_ANON_KEY`가 올바른지 확인
3. Supabase Dashboard에서 API 키 재확인
4. Supabase 프로젝트가 활성화되어 있는지 확인

### Streamlit 앱이 실행되지 않음

**증상**: `ModuleNotFoundError` 또는 `ImportError`

**해결 방법**:
```bash
# ui_integration 폴더로 이동
cd ui_integration

# 의존성 재설치
pip install -r requirements.txt

# Streamlit 재설치
pip install --upgrade streamlit
```

### 차트가 표시되지 않음

**증상**: 비교 제품 선택 시 차트가 업데이트되지 않음

**해결 방법**:
1. 브라우저 새로고침 (F5)
2. 비교 제품을 다시 선택
3. Streamlit 앱 재시작

### 제품 데이터가 표시되지 않음

**증상**: 제품 목록이 비어있거나 평점이 0으로 표시됨

**해결 방법**:
```bash
# 제품 평점 업데이트 스크립트 실행
python scripts/fix_products_ratings.py
```

## ⚡ 성능 및 제한사항

### 성능 지표

- 제품 30개 로드: < 2초
- 리뷰 510개 조회: < 3초
- AI 분석 생성: < 5초
- 차트 렌더링: < 1초

### 제한사항

- 최대 비교 제품: 2개
- AI 분석은 광고가 아닌 리뷰만 대상
- Supabase 무료 플랜 제한 적용
- 현재 제품 수: 30개 (카테고리: sleep, eye-vision, 면역 강화, 항산화제)

## 🆕 최신 기능 (2026-01-14 업데이트)

### 비교 제품 분석
- 메인 제품 선택 시 비교 제품 2개 자동 추천
- 다른 브랜드 우선 추천 알고리즘
- 비교 제품 선택 시 차트 자동 업데이트

### 고급 필터링
- 가격 범위 필터
- 평점 범위 필터 (1-5점)
- 리뷰 수 범위 필터
- 제품명/브랜드 검색

### 시각화 개선
- 레이더 차트 (다차원 비교)
- 가격 및 신뢰도 비교 차트
- 세부 지표 비교표
- 리뷰 감정 분석 차트

### UI/UX 개선
- 필터 상태 표시 및 피드백
- 필터 히스토리 및 되돌리기 기능
- 성능 최적화 (데이터 캐싱)
- 필터 검증 및 오류 처리

## 🛠️ 기술 스택

- **언어**: Python 3.8+
- **웹 프레임워크**: Streamlit 1.31.0+
- **AI 모델**: Anthropic Claude Sonnet 4.5
- **데이터베이스**: Supabase (PostgreSQL)
- **시각화**: Plotly 5.18.0+
- **데이터 처리**: Pandas 2.1.0+
- **주요 라이브러리**: 
  - `anthropic`: Claude AI API
  - `supabase`: Supabase 클라이언트
  - `python-dotenv`: 환경 변수 관리
  - `langchain-core`: LangChain 통합

## 📦 버전 정보

- **현재 버전**: v1.0.0
- **최종 업데이트**: 2026-01-14
- **Python 버전**: 3.8+
- **Streamlit 버전**: 1.31.0+

## 🔐 보안 주의사항

1. **API 키 보안**
   - `.streamlit/secrets.toml` 파일은 절대 Git에 커밋하지 마세요
   - `.gitignore`에 `.streamlit/secrets.toml`이 포함되어 있는지 확인하세요
   - Supabase 서비스 역할 키는 서버 사이드에서만 사용하세요

2. **AI 분석 비용**
   - AI 분석은 비용이 발생하므로, 광고가 아닌 리뷰만 분석하세요
   - API 키 발급: https://console.anthropic.com/settings/keys

3. **의료 정보 주의**
   - 분석 결과는 참고용이며, 의학적 진단이 아닙니다
   - 모든 분석 결과에 부인 공지가 포함됩니다

## 📚 관련 문서

- [프로젝트 기획서](SPEC.md)
- [AI 작업 지침](CLAUDE.md)
- [UI 통합 가이드](ui_integration/README.md)
- [데이터베이스 스키마](database/schema.sql)

## 🤝 기여하기

프로젝트에 기여하고 싶으신가요?

1. Fork 저장소
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

### 코딩 스타일
- Python: PEP 8 준수
- 커밋 메시지: Conventional Commits 형식
- 문서: Markdown 형식

## 📄 라이선스

이 프로젝트는 팀 프로젝트용으로 개발되었습니다.  
상업적 사용 시 문의 바랍니다.

## 🌐 GitHub 저장소

- **메인 저장소**: [https://github.com/Siyeolryu/ica-github](https://github.com/Siyeolryu/ica-github)
- **프로젝트 경로**: `/dev2-2Hour/dev2-main`
- **UI 통합**: [ui_integration 폴더](https://github.com/Siyeolryu/ica-github/tree/main/dev2-2Hour/dev2-main/ui_integration)

## 👥 기여자

- **Logic Designer**: 신뢰도 검증 엔진 및 AI 분석 로직 구현
- **UI Developer**: Streamlit 웹 대시보드 및 시각화 구현
- **Data Manager**: 데이터 수집 및 Supabase 구축

---

**문의**: 프로젝트 관련 문의사항은 GitHub Issues를 통해 남겨주세요.
