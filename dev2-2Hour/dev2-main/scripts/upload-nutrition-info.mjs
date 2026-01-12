import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import { parse } from 'csv-parse/sync'
import iconv from 'iconv-lite'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY
)

// 컬럼명 매핑 (CSV 한글 → DB 영문)
const COLUMN_MAPPING = {
  '식품코드': 'food_code',
  '식품명': 'food_name',
  '데이터구분코드': 'data_category_code',
  '데이터구분명': 'data_category_name',
  '식품기원코드': 'food_origin_code',
  '식품기원명': 'food_origin_name',
  '식품대분류코드': 'food_large_category_code',
  '식품대분류명': 'food_large_category_name',
  '대표식품코드': 'representative_food_code',
  '대표식품명': 'representative_food_name',
  '식품중분류코드': 'food_medium_category_code',
  '식품중분류명': 'food_medium_category_name',
  '식품소분류코드': 'food_small_category_code',
  '식품소분류명': 'food_small_category_name',
  '식품세분류코드': 'food_detail_category_code',
  '식품세분류명': 'food_detail_category_name',
  '유형명': 'type_name',
  '영양성분제공단위량': 'serving_unit',
  '에너지(kcal)': 'energy_kcal',
  '수분(g)': 'water_g',
  '단백질(g)': 'protein_g',
  '지방(g)': 'fat_g',
  '회분(g)': 'ash_g',
  '탄수화물(g)': 'carbohydrate_g',
  '당류(g)': 'sugar_g',
  '식이섬유(g)': 'dietary_fiber_g',
  '칼슘(mg)': 'calcium_mg',
  '철(mg)': 'iron_mg',
  '인(mg)': 'phosphorus_mg',
  '칼륨(mg)': 'potassium_mg',
  '나트륨(mg)': 'sodium_mg',
  '비타민 A(μg RAE)': 'vitamin_a_ug_rae',
  '레티놀(μg)': 'retinol_ug',
  '베타카로틴(μg)': 'beta_carotene_ug',
  '티아민(mg)': 'thiamine_mg',
  '리보플라빈(mg)': 'riboflavin_mg',
  '니아신(mg)': 'niacin_mg',
  '비타민 C(mg)': 'vitamin_c_mg',
  '비타민 D(μg)': 'vitamin_d_ug',
  '콜레스테롤(mg)': 'cholesterol_mg',
  '포화지방산(g)': 'saturated_fatty_acid_g',
  '트랜스지방산(g)': 'trans_fatty_acid_g',
  '출처코드': 'source_code',
  '출처명': 'source_name',
  '1회분량': 'serving_size',
  '1회분량중량/부피': 'serving_weight_volume',
  '1일섭취횟수': 'daily_intake_frequency',
  '섭취대상': 'intake_target',
  '식품중량/부피': 'food_weight_volume',
  '품목제조신고번호': 'product_report_number',
  '제조사명': 'manufacturer_name',
  '수입업체명': 'importer_name',
  '유통업체명': 'distributor_name',
  '수입여부': 'import_yn',
  '원산지국코드': 'origin_country_code',
  '원산지국명': 'origin_country_name',
  '데이터생성방법코드': 'data_creation_method_code',
  '데이터생성방법명': 'data_creation_method_name',
  '데이터생성일자': 'data_creation_date',
  '데이터기준일자': 'data_standard_date'
}

// 숫자 컬럼 목록
const NUMERIC_COLUMNS = [
  'energy_kcal', 'water_g', 'protein_g', 'fat_g', 'ash_g', 'carbohydrate_g',
  'sugar_g', 'dietary_fiber_g', 'calcium_mg', 'iron_mg', 'phosphorus_mg',
  'potassium_mg', 'sodium_mg', 'vitamin_a_ug_rae', 'retinol_ug',
  'beta_carotene_ug', 'thiamine_mg', 'riboflavin_mg', 'niacin_mg',
  'vitamin_c_mg', 'vitamin_d_ug', 'cholesterol_mg', 'saturated_fatty_acid_g',
  'trans_fatty_acid_g'
]

function parseNumeric(value) {
  if (!value || value.trim() === '') return null
  const num = parseFloat(value)
  return isFinite(num) ? num : null
}

function parseDate(dateStr) {
  if (!dateStr || dateStr.trim() === '') return null
  // YYYY-MM-DD 형식으로 변환
  try {
    const cleaned = dateStr.trim().replace(/\./g, '-')
    const date = new Date(cleaned)
    return isNaN(date.getTime()) ? null : cleaned
  } catch {
    return null
  }
}

async function uploadNutritionInfo(csvPath) {
  console.log(`📂 CSV 파일 읽는 중: ${csvPath}`)

  // UTF-8 인코딩으로 읽기
  const fileContent = fs.readFileSync(csvPath, 'utf-8')

  // BOM 제거
  const cleanedContent = fileContent.replace(/^\uFEFF/, '')

  const records = parse(cleanedContent, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
  })

  console.log(`📦 ${records.length}개의 데이터 발견`)

  if (records.length === 0) {
    console.log('⚠️ 업로드할 데이터가 없습니다')
    return
  }

  // 첫 번째 레코드 확인
  console.log('📋 CSV 컬럼명:', Object.keys(records[0]))
  console.log('📋 첫 번째 행 샘플:', records[0])

  // 데이터 변환
  const nutritionData = records.map((row) => {
    const mapped = {}

    // 컬럼명 매핑
    for (const [korKey, engKey] of Object.entries(COLUMN_MAPPING)) {
      const value = row[korKey]

      if (NUMERIC_COLUMNS.includes(engKey)) {
        mapped[engKey] = parseNumeric(value)
      } else if (engKey.includes('_date')) {
        mapped[engKey] = parseDate(value)
      } else {
        mapped[engKey] = value && value.trim() ? value.trim() : null
      }
    }

    return mapped
  })

  console.log('⬆️ Supabase에 업로드 중...')
  console.log(`샘플 데이터:`, nutritionData[0])

  // 배치 업로드 (1000개씩)
  const BATCH_SIZE = 1000
  let uploaded = 0

  for (let i = 0; i < nutritionData.length; i += BATCH_SIZE) {
    const batch = nutritionData.slice(i, i + BATCH_SIZE)

    const { data, error } = await supabase
      .from('nutrition_info')
      .upsert(batch, { onConflict: 'food_code' })

    if (error) {
      console.error(`❌ 배치 ${Math.floor(i / BATCH_SIZE) + 1} 업로드 중 오류:`, error)
      throw error
    }

    uploaded += batch.length
    console.log(`✅ ${uploaded}/${nutritionData.length} 업로드 완료 (${Math.round((uploaded / nutritionData.length) * 100)}%)`)
  }

  console.log(`✅ 총 ${nutritionData.length}개의 영양성분 정보가 성공적으로 업로드되었습니다!`)
}

async function run() {
  const csvPath = '식품의약품안전처_건강기능식품영양성분정보_20251230.csv'

  try {
    await uploadNutritionInfo(csvPath)
    console.log('✅ 모든 업로드 완료!')
  } catch (e) {
    console.error('❌ Error:', e?.message || e)
    process.exit(1)
  }
}

run()
