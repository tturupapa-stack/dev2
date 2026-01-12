# 1주차 팀원 가이드 (데이터 수집/DB 구축)

## 당신이 만들 것
iHerb에서 **루테인 제품 5종**의 **제품 정보 + 리뷰 20개씩**을 수집하여 **Supabase에 저장**하는 프로그램

---

## 프로토타입 특징

| 항목 | 값 |
|------|-----|
| 제품 카테고리 | 루테인 |
| 제품 수 | 5개 |
| 제품당 리뷰 수 | 20개 |
| 총 리뷰 수 | 100개 |
| 데이터 출처 | iHerb |
| 저장소 | Supabase (PostgreSQL) |
| 작업 성격 | **1회성 데이터 구축** |

---

## Claude Code에 이렇게 요청하세요

### 1단계: 프로젝트 시작
```
data_manager라는 폴더를 만들고,
iHerb에서 루테인 제품 정보와 리뷰를 수집해서 Supabase에 저장하는 프로그램을 만들어줘.

이건 프로토타입이라 1회성으로 데이터를 수집하고 DB에 저장하면 돼.
실시간 스크래핑이 아니야.

총 5개 제품, 각 제품당 20개 리뷰 = 100개 리뷰를 저장해야 해.
```

### 2단계: Supabase 테이블 생성
```
Supabase에 두 개 테이블을 만들어줘:

1. products 테이블:
   - id (UUID, 자동생성)
   - name (제품명)
   - brand (브랜드)
   - price (가격)
   - serving_size (1회 섭취량)
   - servings_per_container (총 섭취 횟수)
   - ingredients (성분 정보, JSONB)
   - other_ingredients (기타 원료, TEXT[])
   - warnings (주의사항, TEXT[])
   - product_url (제품 URL)
   - image_url (이미지 URL)
   - created_at (생성일시)

2. reviews 테이블:
   - id (UUID, 자동생성)
   - product_id (products 테이블 참조)
   - text (리뷰 본문)
   - rating (평점 1-5)
   - date (작성일)
   - reorder (재구매 여부)
   - one_month_use (한달사용 여부)
   - reviewer (리뷰어 이름)
   - verified (구매 인증 여부)
   - created_at (생성일시)

SQL 코드 만들어줘.
```

### 3단계: Supabase 클라이언트 구현
```
supabase_client.py 파일을 만들어줘.

환경변수에서 SUPABASE_URL, SUPABASE_KEY를 읽어서 연결해.
python-dotenv 사용해줘.

필요한 함수:
- insert_product(product_data) : 제품 저장
- insert_reviews(reviews_list) : 리뷰 일괄 저장
- get_all_products() : 전체 제품 조회
- get_reviews_by_product(product_id) : 제품별 리뷰 조회
- search_products(keyword) : 제품 검색
```

### 4단계: 데이터 수집 (선택)
```
iHerb에서 루테인 제품 5개를 선정하고 리뷰를 수집해줘.

방법 1: Selenium으로 크롤링 (자동)
방법 2: 수동으로 JSON 파일에 데이터 정리 (수동)

어느 방법이든 최종적으로 Supabase에 저장되면 돼.
```

### 5단계: 데이터 업로드
```
db_uploader.py 파일을 만들어줘.

upload_all_data() 함수가 있어야 해.
이 함수를 실행하면:
1. 5개 제품 정보를 products 테이블에 저장
2. 각 제품당 20개 리뷰를 reviews 테이블에 저장
3. 총 100개 리뷰가 저장되면 완료

실행 방법: python -m data_manager.db_uploader
```

### 6단계: 테스트
```
데이터가 잘 저장됐는지 확인해줘.

1. products 테이블에 5개 제품이 있는지
2. reviews 테이블에 100개 리뷰가 있는지
3. 각 제품당 20개 리뷰가 연결되어 있는지

확인 코드 만들어줘.
```

---

## 하지 마세요 (금지사항)

| 하지 마세요 | 이유 |
|-------------|------|
| "분석 기능도 추가해줘" | 분석은 2주차 담당입니다 |
| "신뢰도 점수 계산해줘" | 분석은 2주차 담당입니다 |
| "UI 화면 만들어줘" | UI는 3주차 담당입니다 |
| "네이버 쇼핑도 크롤링해줘" | 프로토타입은 iHerb만 사용합니다 |
| "실시간 스크래핑 기능" | 프로토타입은 사전 저장 데이터 사용 |

---

## 여기까지만 하세요 (작업 범위)

**Supabase 설정:**
- [x] Supabase 프로젝트 생성
- [x] products 테이블 생성
- [x] reviews 테이블 생성
- [x] 환경 변수 설정 (.env)

**데이터 수집:**
- [x] 루테인 제품 5종 선정
- [x] 각 제품 정보 수집 (크롤링 or 수동)
- [x] 각 제품 리뷰 20개 수집

**데이터 저장:**
- [x] products 테이블에 5개 제품 저장
- [x] reviews 테이블에 100개 리뷰 저장
- [x] 데이터 무결성 검증

---

## 환경 변수 설정

프로젝트 폴더에 `.env` 파일을 만들고:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

Supabase 대시보드에서:
1. Project Settings → API
2. Project URL 복사 → SUPABASE_URL
3. anon public 키 복사 → SUPABASE_KEY

---

## 완료 체크리스트

작업이 끝나면 이것만 확인해주세요:

```
Claude에게 이렇게 물어보세요:

"Supabase 데이터 확인해줘.

1. products 테이블에 몇 개 제품 있어?
2. reviews 테이블에 몇 개 리뷰 있어?
3. 각 제품마다 리뷰가 몇 개씩 연결되어 있어?

쿼리 결과 보여줘."
```

예상 결과:
- products: 5개
- reviews: 100개
- 제품당 리뷰: 각 20개

---

## 문제가 생기면

```
"에러가 나는데 고쳐줘" 라고 하면 Claude가 알아서 고칩니다.

Supabase 연결 문제:
→ "SUPABASE_URL이랑 SUPABASE_KEY 환경변수 확인해줘"

크롤링 문제:
→ "크롤링 대신 수동으로 JSON 파일 만들어서 업로드하자"
```

---

## 폴더 구조 (완성 예시)

```
data_manager/
├── __init__.py              ← 패키지 초기화
├── supabase_client.py       ← Supabase 연결 및 CRUD
├── scraper.py               ← iHerb 크롤러 (선택)
├── data_cleaner.py          ← 데이터 정제
├── db_uploader.py           ← 데이터 업로드 스크립트
└── config.py                ← 설정

data/
└── raw_products.json        ← 수동 수집 시 사용
```

---

## 다음 단계

데이터 저장이 완료되면:
1. SUPABASE_URL, SUPABASE_KEY를 팀원 B, C에게 공유
2. 2주차 팀원이 이 데이터를 분석
3. 3주차 팀원이 UI에서 조회
