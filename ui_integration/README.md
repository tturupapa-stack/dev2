# 건기식 리뷰 팩트체크 시스템 - Streamlit UI

루테인 제품 5종에 대한 리뷰 분석 및 비교 대시보드

## 프로젝트 구조

```
ui_integration/
├── app.py                  # [Main] Tab 기반 동적 대시보드 로직
├── visualizations.py       # [Chart] Plotly 기반 고해상도 시각화 컴포넌트
├── mock_data.py            # [Data] 제품 및 리뷰 분석 데이터 세트
├── requirements.txt        # [Env] 프로젝트 의존성 관리
└── README.md               # [Doc] 프로젝트 명세서
```

## 설치 방법

### 1. 가상환경 생성 (권장)

```bash
cd ui_integration
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

브라우저에서 자동으로 http://localhost:8501 이 열립니다.

## 기능 소개

### 1. 제품 개요 (5개 제품 카드)
- 제품명, 브랜드, 가격
- 신뢰도 게이지 차트
- 신뢰도 등급 배지 (HIGH/MEDIUM/LOW)

### 2. 종합 비교표
- 신뢰도 점수
- 광고 의심률
- 재구매율
- 한 달 사용 비율
- 평균 평점

### 3. 시각화 분석
- **레이더 차트**: 5개 제품의 다차원 비교
- **가격 비교 차트**: 브랜드별 가격 시각화

### 4. AI 약사 인사이트
각 제품별 상세 분석:
- 요약
- 효능 분석
- 부작용 정보
- 복용 권장사항
- 주의사항
- 8단계 체크리스트 결과

### 5. 리뷰 상세 보기
- 제품별 리뷰 목록 (20개씩)
- 광고 의심 리뷰 하이라이트
- 평점 필터링
- 평점 분포 차트
- 인증구매/재구매/1개월+ 배지

## 데이터 구조

### 제품 정보 (5종)
- NOW Foods Lutein 20mg
- Doctor's Best Lutein with Lutemax 2020
- Jarrow Formulas Lutein 20mg
- Life Extension MacuGuard Ocular Support
- California Gold Nutrition Lutein with Zeaxanthin

### 리뷰 정보 (각 제품당 20개, 총 100개)
- 텍스트, 평점, 작성일
- 재구매 여부, 한 달 사용 여부
- 리뷰어, 인증 구매 여부
- 다양한 리뷰 타입 (긍정/부정/중립/광고성)

### 분석 결과
- 신뢰도 점수 (0-100)
- 신뢰도 등급 (HIGH/MEDIUM/LOW)
- 8단계 체크리스트 결과
- AI 약사 분석 (요약, 효능, 부작용, 권장사항, 주의사항)

## 기술 스택

- **Streamlit**: 웹 UI 프레임워크
- **Plotly**: 인터랙티브 차트
- **Pandas**: 데이터 처리

## 신뢰도 분석 기준 (8단계 체크리스트)

1. 인증 구매 비율 (70% 이상)
2. 재구매율 (30% 이상)
3. 장기 사용 비율 (50% 이상)
4. 평점 분포 적절성 (30-90% 고평점)
5. 리뷰 길이 (평균 50자 이상)
6. 시간 분포 자연성
7. 광고성 리뷰 탐지 (10% 미만)
8. 리뷰어 다양성 (80% 이상)

## 주요 특징

- 실시간 제품 검색 기능
- 반응형 레이아웃 (가로/세로 레이아웃 자동 조정)
- 인터랙티브 차트 (확대/축소/호버 정보)
- 광고성 리뷰 자동 탐지 및 하이라이트
- 다양한 필터링 옵션

## 향후 개선 사항

- [ ] 데이터베이스 연동 (PostgreSQL)
- [ ] 실시간 크롤링 기능
- [ ] 더 많은 제품 카테고리 추가
- [ ] 사용자 로그인 및 즐겨찾기 기능
- [ ] PDF 리포트 내보내기
- [ ] 제품 비교 기능 강화
