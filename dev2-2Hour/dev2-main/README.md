# 건기식 리뷰 팩트체크 엔진

건강기능식품 리뷰의 신뢰도를 정량적으로 평가하고, AI 약사 페르소나를 통해 전문적인 분석을 제공하는 시스템입니다.

## 주요 기능

### 1. 신뢰도 검증 엔진 (`core/validator.py`)
- **13단계 광고 판별 체크리스트** 기반 자동 검증
- **신뢰도 점수 계산**: `S = (L×0.2) + (R×0.2) + (M×0.3) + (P×0.1) + (C×0.2)`
- **감점 시스템**: 항목당 -10점, 40점 미만 또는 3개 이상 감점 시 광고 판별

### 2. AI 약사 분석 엔진 (`core/analyzer.py`)
- **페르소나**: 15년 경력 임상 약사
- **AI 모델**: Anthropic Claude Sonnet 4.5
- **출력**: JSON 형식 (요약, 효능, 부작용, 신뢰도, 조언)
- **할루시네이션 방지**: 리뷰 원문 근거만 추출

## 설치 방법

```bash
# 1. 저장소 클론
git clone https://github.com/tturupapa-stack/dev2.git
cd dev2

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
# .env 파일을 생성하고 다음 내용을 입력하세요
```

### 환경 변수 설정 (.env 파일)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Supabase 설정
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

**Supabase 키 확인 방법:**
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 선택 → Settings → API
3. **Project URL**: `SUPABASE_URL`에 입력
4. **anon/public key**: `SUPABASE_ANON_KEY`에 입력
5. **service_role key**: `SUPABASE_SERVICE_ROLE_KEY`에 입력 (관리자 권한)

## 사용 방법

### 기본 사용 예제

```python
from core import validate_review, analyze_review

# 1. 신뢰도 검증
review_text = "제품을 한 달 사용했는데 효과가 좋았습니다..."

result = validate_review(
    review_text=review_text,
    length_score=70,      # 리뷰 길이 점수 (0-100)
    repurchase_score=80,  # 재구매 의사 점수 (0-100)
    monthly_use_score=100, # 한달 사용 여부 (0-100)
    photo_score=50,       # 사진 첨부 점수 (0-100)
    consistency_score=85  # 내용 일치도 점수 (0-100)
)

print(f"신뢰도 점수: {result['trust_score']}")
print(f"광고 여부: {result['is_ad']}")
print(f"감점 사유: {result['reasons']}")

# 2. AI 약사 분석 (광고가 아닌 경우만)
if not result['is_ad']:
    ai_result = analyze_review(review_text)
    print(f"요약: {ai_result['Summary']}")
    print(f"효능: {ai_result['Efficacy']}")
    print(f"부작용: {ai_result['Side_effects']}")
    print(f"조언: {ai_result['Tip']}")
```

### 예제 실행

```bash
python example.py
```

## 프로젝트 구조

```
team_projects_logic_D/
├── core/                   # 핵심 모듈
│   ├── __init__.py
│   ├── validator.py        # 신뢰도 검증 엔진
│   └── analyzer.py         # AI 약사 분석 엔진
├── database/               # 데이터베이스 모듈
│   ├── __init__.py
│   ├── supabase_client.py  # Supabase 클라이언트
│   └── test_connection.py  # 연결 테스트 스크립트
├── logic_designer/         # 로직 설계 모듈
│   ├── __init__.py
│   ├── checklist.py        # 13단계 체크리스트
│   ├── trust_score.py      # 신뢰도 점수 계산
│   └── analyzer.py         # AI 분석 엔진
├── logs/                   # 개발 로그
│   ├── dev_log.md          # 개발일지
│   ├── prompt_log.md       # 프롬프트 설계 로그
│   └── output_review.md    # 결과값 검토
├── example.py              # 사용 예제
├── requirements.txt        # 의존성 패키지
├── .env                    # 환경 변수 (gitignore)
├── SPEC.md                 # 기획서
├── CLAUDE.md               # AI 작업 지침
└── README.md               # 프로젝트 문서
```

## 13단계 광고 판별 체크리스트

1. 대가성 문구 존재
2. 감탄사 남발
3. 정돈된 문단 구조
4. 개인 경험 부재
5. 원료 특징 나열
6. 키워드 반복
7. 단점 회피
8. 찬사 위주 구성
9. 전문 용어 오남용
10. 비현실적 효과 강조
11. 타사 제품 비교
12. 홍보성 블로그 문체
13. 이모티콘 과다 사용

## 신뢰도 점수 계산 공식

```
S = (L × 0.2) + (R × 0.2) + (M × 0.3) + (P × 0.1) + (C × 0.2)
```

- **L** (Length): 리뷰 길이 점수
- **R** (Repurchase): 재구매 의사 점수
- **M** (Monthly Use): 한달 이상 사용 여부 점수
- **P** (Photo): 사진 첨부 점수
- **C** (Consistency): 내용 일치도 점수

## AI 분석 출력 형식

```json
{
  "Summary": "리뷰 한 줄 요약",
  "Efficacy": ["효능1", "효능2"],
  "Side_effects": ["부작용1", "부작용2"],
  "Trust_score": 85,
  "Tip": "약사의 핵심 조언",
  "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
}
```

## 기술 스택

- **언어**: Python 3.8+
- **AI 모델**: Anthropic Claude Sonnet 4.5
- **데이터베이스**: Supabase (PostgreSQL)
- **주요 라이브러리**: anthropic, python-dotenv, supabase

## Supabase 데이터베이스 연동

### 연결 테스트

```bash
# Supabase 연결 테스트
python database/test_connection.py
```

### Python에서 사용하기

```python
from database import get_supabase_client, test_connection

# 연결 테스트
if test_connection():
    print("✅ Supabase 연결 성공!")
    
    # 클라이언트 사용
    supabase = get_supabase_client()
    
    # 데이터 조회 예제
    # response = supabase.table('your_table').select('*').execute()
```

### Supabase 프로젝트 정보

- **프로젝트 URL**: `https://bvowxbpqtfpkkxkzsumf.supabase.co`
- **GitHub 저장소**: [https://github.com/tturupapa-stack/dev2](https://github.com/tturupapa-stack/dev2)

## 주의 사항

1. **API 키 보안**
   - `.env` 파일은 절대 Git에 커밋하지 마세요
   - `.gitignore`에 `.env`가 포함되어 있는지 확인하세요
   - Supabase 서비스 역할 키는 서버 사이드에서만 사용하세요

2. **AI 분석 비용**
   - AI 분석은 비용이 발생하므로, 광고가 아닌 리뷰만 분석하세요
   - API 키 발급: https://console.anthropic.com/settings/keys

3. **의료 정보 주의**
   - 분석 결과는 참고용이며, 의학적 진단이 아닙니다
   - 모든 분석 결과에 부인 공지가 포함됩니다

## GitHub 저장소

- **저장소**: [https://github.com/tturupapa-stack/dev2](https://github.com/tturupapa-stack/dev2)

## 라이선스

이 프로젝트는 팀 프로젝트용으로 개발되었습니다.

## 기여자

- Logic Designer: 신뢰도 검증 엔진 및 AI 분석 로직 구현
