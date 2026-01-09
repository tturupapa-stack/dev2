# 건강기능식품 영양성분 정보 DB 구축 가이드

## 1. Supabase 테이블 생성

### 방법 1: 웹 콘솔 사용 (추천)

1. Supabase 대시보드 접속: https://supabase.com/dashboard
2. 프로젝트 선택
3. 왼쪽 메뉴에서 **SQL Editor** 클릭
4. `database/create_nutrition_info_table.sql` 파일 내용 복사 & 붙여넣기
5. **Run** 버튼 클릭

### 방법 2: CLI 사용

```bash
# SQL 파일 확인
cat database/create_nutrition_info_table.sql

# Supabase CLI로 실행 (설치 필요)
supabase db push
```

## 2. 데이터 업로드

테이블 생성 완료 후:

```bash
# 영양성분 정보 업로드 (약 4,380건)
node upload-nutrition-info.mjs
```

## 테이블 구조

**테이블명**: `nutrition_info`

**주요 컬럼**:
- `food_code` (TEXT, UNIQUE): 식품코드 (예: F102-054540000-0037)
- `food_name` (TEXT): 식품명
- `manufacturer_name` (TEXT): 제조사명
- 영양성분: energy_kcal, protein_g, fat_g, carbohydrate_g 등
- 비타민: vitamin_a_ug_rae, vitamin_c_mg, vitamin_d_ug 등
- 무기질: calcium_mg, iron_mg, sodium_mg 등

**인덱스**:
- food_code (고유)
- food_name
- manufacturer_name
- food_large_category_name
- representative_food_name

## 데이터 소스

- **파일**: `식품의약품안전처_건강기능식품영양성분정보_20251230.csv`
- **출처**: 식품의약품안전처
- **데이터 기준일**: 2025-12-30
- **총 레코드 수**: 약 4,380건

## 사용 예시

```javascript
// 제품명으로 검색
const { data } = await supabase
  .from('nutrition_info')
  .select('*')
  .ilike('food_name', '%루테인%')

// 제조사로 필터링
const { data } = await supabase
  .from('nutrition_info')
  .select('*')
  .eq('manufacturer_name', 'California Gold Nutrition')

// 비타민 D 함량 높은 순
const { data } = await supabase
  .from('nutrition_info')
  .select('food_name, vitamin_d_ug')
  .not('vitamin_d_ug', 'is', null)
  .order('vitamin_d_ug', { ascending: false })
  .limit(10)
```
