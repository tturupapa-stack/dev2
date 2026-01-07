# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

건기식(건강기능식품) 리뷰 팩트체크 시스템 프로토타입. iHerb 루테인 제품 5종의 리뷰 100개(제품당 20개)를 Supabase에 저장하고, 8단계 체크리스트 + Claude AI 분석으로 광고성 리뷰를 판별하며, Streamlit 대시보드로 결과를 시각화합니다.

## Tech Stack

- **Database**: Supabase (PostgreSQL)
- **AI Analysis**: Claude API (Anthropic) - NOT OpenAI
- **UI**: Streamlit + Plotly
- **Scraping**: Selenium + BeautifulSoup (one-time data collection)

## Project Structure

```
docs/                    # 기획 문서 및 가이드
data_manager/            # 팀원 A: 데이터 수집/정제/Supabase 업로드
logic_designer/          # 팀원 B: 8단계 체크리스트, 신뢰도 계산, AI 분석
ui_integration/          # 팀원 C: Streamlit UI, 시각화
```

## Commands

```bash
# 환경 설정
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 데이터 업로드 (1회성)
python data_manager/db_uploader.py

# Streamlit 앱 실행
streamlit run ui_integration/app.py
```

## Environment Variables

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
ANTHROPIC_API_KEY=your-anthropic-api-key  # NOT OpenAI
```

## Database Schema

**products**: id, name, brand, price, serving_size, servings_per_container, ingredients (JSONB), other_ingredients (TEXT[]), warnings (TEXT[]), product_url, created_at

**reviews**: id, product_id (FK), text, rating (1-5), date, reorder (bool), one_month_use (bool), reviewer, verified (bool), created_at

## Module Interface

팀원 B → 팀원 C 분석 결과 형식:
```python
{
    'trust_score': float,        # 0-100
    'trust_level': str,          # 'high' | 'medium' | 'low'
    'checklist_results': Dict,
    'ai_result': {
        'summary': str,
        'efficacy': List[str],
        'side_effects': List[str],
        'recommendations': str,
        'warnings': List[str]
    }
}
```

## Trust Score Formula

- 체크리스트 점수: 40%
- 재구매율: 30%
- 한달 사용 비율: 20%
- 평점 신뢰도: 10%

## Development Workflow

### 개발일지 작성 규칙

**IMPORTANT**: 모든 작업 완료 후 반드시 개발일지를 작성할 것

- **위치**: `개발일지/YYYY-MM-DD-작업_제목.md`
- **작성 시점**: 의미 있는 작업(기능 추가, 버그 수정, 리팩토링 등) 완료 시
- **필수 포함 내용**:
  - 작업 개요
  - 주요 작업 내용 (파일별 변경사항)
  - 기술 스택 및 새로 추가된 의존성
  - 트러블슈팅 (발생한 문제와 해결 방법)
  - 업로드/배포 결과
  - 배운 점
  - 다음 단계

- **작성 형식**: Markdown, 코드 블록과 스크린샷 포함
- **명명 규칙**: `YYYY-MM-DD-간결한_작업_설명.md`

## Available Skills

- **supervisor-report**: 복잡한 작업을 frontend-developer, backend-developer, test-runner, code-reviewer, doc-writer 에이전트에게 위임하고 결과를 검증
- **musinsa-inspired-design**: 무신사 스타일 디자인 시스템 (Bold Minimalism, Editorial Layout)
