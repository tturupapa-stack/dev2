-- 건강기능식품 영양성분 정보 테이블 생성
-- 식품의약품안전처 데이터

CREATE TABLE IF NOT EXISTS nutrition_info (
  id BIGSERIAL PRIMARY KEY,

  -- 식품 기본 정보
  food_code TEXT UNIQUE NOT NULL,  -- 식품코드 (PK 대용)
  food_name TEXT,                  -- 식품명
  data_category_code TEXT,         -- 데이터구분코드
  data_category_name TEXT,         -- 데이터구분명
  food_origin_code TEXT,           -- 식품기원코드
  food_origin_name TEXT,           -- 식품기원명

  -- 식품 분류
  food_large_category_code TEXT,   -- 식품대분류코드
  food_large_category_name TEXT,   -- 식품대분류명
  representative_food_code TEXT,   -- 대표식품코드
  representative_food_name TEXT,   -- 대표식품명
  food_medium_category_code TEXT,  -- 식품중분류코드
  food_medium_category_name TEXT,  -- 식품중분류명
  food_small_category_code TEXT,   -- 식품소분류코드
  food_small_category_name TEXT,   -- 식품소분류명
  food_detail_category_code TEXT,  -- 식품세분류코드
  food_detail_category_name TEXT,  -- 식품세분류명
  type_name TEXT,                  -- 유형명

  -- 영양성분 제공 정보
  serving_unit TEXT,               -- 영양성분제공단위량

  -- 기본 영양성분 (숫자형)
  energy_kcal NUMERIC,             -- 에너지(kcal)
  water_g NUMERIC,                 -- 수분(g)
  protein_g NUMERIC,               -- 단백질(g)
  fat_g NUMERIC,                   -- 지방(g)
  ash_g NUMERIC,                   -- 회분(g)
  carbohydrate_g NUMERIC,          -- 탄수화물(g)
  sugar_g NUMERIC,                 -- 당류(g)
  dietary_fiber_g NUMERIC,         -- 식이섬유(g)

  -- 무기질 (mg)
  calcium_mg NUMERIC,              -- 칼슘(mg)
  iron_mg NUMERIC,                 -- 철(mg)
  phosphorus_mg NUMERIC,           -- 인(mg)
  potassium_mg NUMERIC,            -- 칼륨(mg)
  sodium_mg NUMERIC,               -- 나트륨(mg)

  -- 비타민
  vitamin_a_ug_rae NUMERIC,        -- 비타민 A(μg RAE)
  retinol_ug NUMERIC,              -- 레티놀(μg)
  beta_carotene_ug NUMERIC,        -- 베타카로틴(μg)
  thiamine_mg NUMERIC,             -- 티아민(mg)
  riboflavin_mg NUMERIC,           -- 리보플라빈(mg)
  niacin_mg NUMERIC,               -- 니아신(mg)
  vitamin_c_mg NUMERIC,            -- 비타민 C(mg)
  vitamin_d_ug NUMERIC,            -- 비타민 D(μg)

  -- 지방 관련
  cholesterol_mg NUMERIC,          -- 콜레스테롤(mg)
  saturated_fatty_acid_g NUMERIC,  -- 포화지방산(g)
  trans_fatty_acid_g NUMERIC,      -- 트랜스지방산(g)

  -- 출처 정보
  source_code TEXT,                -- 출처코드
  source_name TEXT,                -- 출처명

  -- 섭취 정보
  serving_size TEXT,               -- 1회분량
  serving_weight_volume TEXT,      -- 1회분량중량/부피
  daily_intake_frequency TEXT,     -- 1일섭취횟수
  intake_target TEXT,              -- 섭취대상
  food_weight_volume TEXT,         -- 식품중량/부피

  -- 제조/유통 정보
  product_report_number TEXT,      -- 품목제조신고번호
  manufacturer_name TEXT,          -- 제조사명
  importer_name TEXT,              -- 수입업체명
  distributor_name TEXT,           -- 유통업체명
  import_yn TEXT,                  -- 수입여부
  origin_country_code TEXT,        -- 원산지국코드
  origin_country_name TEXT,        -- 원산지국명

  -- 데이터 메타정보
  data_creation_method_code TEXT,  -- 데이터생성방법코드
  data_creation_method_name TEXT,  -- 데이터생성방법명
  data_creation_date DATE,         -- 데이터생성일자
  data_standard_date DATE,         -- 데이터기준일자

  -- 시스템 타임스탬프
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_nutrition_info_food_code ON nutrition_info(food_code);
CREATE INDEX IF NOT EXISTS idx_nutrition_info_food_name ON nutrition_info(food_name);
CREATE INDEX IF NOT EXISTS idx_nutrition_info_manufacturer ON nutrition_info(manufacturer_name);
CREATE INDEX IF NOT EXISTS idx_nutrition_info_large_category ON nutrition_info(food_large_category_name);
CREATE INDEX IF NOT EXISTS idx_nutrition_info_representative_food ON nutrition_info(representative_food_name);

-- 업데이트 시각 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_nutrition_info_updated_at BEFORE UPDATE
ON nutrition_info FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 테이블 코멘트
COMMENT ON TABLE nutrition_info IS '식품의약품안전처 건강기능식품 영양성분 정보';
COMMENT ON COLUMN nutrition_info.food_code IS '식품 고유 코드 (예: F102-054540000-0037)';
COMMENT ON COLUMN nutrition_info.food_name IS '제품명';
COMMENT ON COLUMN nutrition_info.energy_kcal IS '100g당 열량(kcal)';
