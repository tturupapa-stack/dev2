import 'dotenv/config'
import axios from 'axios'
import { createClient } from '@supabase/supabase-js'

const API_KEY = process.env.FOOD_SAFETY_API_KEY
const BASE_URL = 'https://api.data.go.kr/openapi/tn_pubr_public_health_functional_food_nutrition_info_api'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY
)

// 컬럼명 매핑 (API → DB)
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

const NUMERIC_COLUMNS = [
  'energy_kcal', 'water_g', 'protein_g', 'fat_g', 'ash_g', 'carbohydrate_g',
  'sugar_g', 'dietary_fiber_g', 'calcium_mg', 'iron_mg', 'phosphorus_mg',
  'potassium_mg', 'sodium_mg', 'vitamin_a_ug_rae', 'retinol_ug',
  'beta_carotene_ug', 'thiamine_mg', 'riboflavin_mg', 'niacin_mg',
  'vitamin_c_mg', 'vitamin_d_ug', 'cholesterol_mg', 'saturated_fatty_acid_g',
  'trans_fatty_acid_g'
]

function parseNumeric(value) {
  if (!value || value === '' || value === 'null') return null
  const num = parseFloat(value)
  return isFinite(num) ? num : null
}

function parseDate(dateStr) {
  if (!dateStr || dateStr.trim() === '') return null
  try {
    const cleaned = dateStr.trim().replace(/\./g, '-')
    const date = new Date(cleaned)
    return isNaN(date.getTime()) ? null : cleaned
  } catch {
    return null
  }
}

function transformData(apiData) {
  const mapped = {}

  for (const [korKey, engKey] of Object.entries(COLUMN_MAPPING)) {
    const value = apiData[korKey]

    if (NUMERIC_COLUMNS.includes(engKey)) {
      mapped[engKey] = parseNumeric(value)
    } else if (engKey.includes('_date')) {
      mapped[engKey] = parseDate(value)
    } else {
      mapped[engKey] = value && value.trim ? value.trim() : null
    }
  }

  return mapped
}

async function fetchFromAPI(pageNo = 1, numOfRows = 1000) {
  console.log(`📡 API 요청: 페이지 ${pageNo}, ${numOfRows}건`)

  try {
    const response = await axios.get(BASE_URL, {
      params: {
        serviceKey: API_KEY,
        pageNo,
        numOfRows,
        type: 'json'
      },
      timeout: 30000,
      maxRedirects: 5,
      headers: {
        'Accept': 'application/json'
      }
    })

    // 응답 구조 확인 (공공데이터포털 API 형식에 따라 조정 필요)
    const data = response.data.response?.body?.items || response.data.items || response.data

    if (!Array.isArray(data)) {
      console.error('⚠️ 예상치 못한 응답 형식:', JSON.stringify(response.data).substring(0, 200))
      return { items: [], totalCount: 0 }
    }

    const totalCount = response.data.response?.body?.totalCount || response.data.totalCount || data.length

    return { items: data, totalCount }

  } catch (error) {
    console.error('❌ API 요청 실패:', error.message)
    if (error.response) {
      console.error('응답 상태:', error.response.status)
      console.error('응답 데이터:', JSON.stringify(error.response.data).substring(0, 500))
    }
    throw error
  }
}

async function syncNutritionData() {
  console.log('🔄 식품의약품안전처 API 데이터 동기화 시작...')

  if (!API_KEY) {
    console.error('❌ FOOD_SAFETY_API_KEY 환경변수가 설정되지 않았습니다.')
    console.log('📋 .env 파일에 다음을 추가하세요:')
    console.log('FOOD_SAFETY_API_KEY=your_api_key_here')
    return
  }

  let totalSynced = 0
  let pageNo = 1
  const PAGE_SIZE = 1000

  try {
    // 첫 페이지 조회로 전체 건수 확인
    const { items: firstPage, totalCount } = await fetchFromAPI(pageNo, PAGE_SIZE)

    console.log(`📊 총 ${totalCount}건의 데이터 발견`)

    if (firstPage.length === 0) {
      console.log('⚠️ 조회된 데이터가 없습니다.')
      return
    }

    // 첫 페이지 처리
    const transformedData = firstPage.map(transformData)
    await uploadToSupabase(transformedData)
    totalSynced += transformedData.length
    console.log(`✅ ${totalSynced}/${totalCount} 동기화 완료 (${Math.round((totalSynced / totalCount) * 100)}%)`)

    // 나머지 페이지 처리
    const totalPages = Math.ceil(totalCount / PAGE_SIZE)

    for (pageNo = 2; pageNo <= totalPages; pageNo++) {
      const { items } = await fetchFromAPI(pageNo, PAGE_SIZE)

      if (items.length === 0) break

      const transformed = items.map(transformData)
      await uploadToSupabase(transformed)
      totalSynced += transformed.length

      console.log(`✅ ${totalSynced}/${totalCount} 동기화 완료 (${Math.round((totalSynced / totalCount) * 100)}%)`)

      // API 부하 방지를 위한 딜레이
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    console.log(`\n✅ 동기화 완료! 총 ${totalSynced}건 업데이트`)

  } catch (error) {
    console.error('\n💥 동기화 중 오류 발생:', error.message)
    console.error(`현재까지 ${totalSynced}건 동기화됨`)
    throw error
  }
}

async function uploadToSupabase(data) {
  const { error } = await supabase
    .from('nutrition_info')
    .upsert(data, { onConflict: 'food_code' })

  if (error) {
    console.error('❌ Supabase 업로드 오류:', error)
    throw error
  }
}

// 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  syncNutritionData().catch(e => {
    console.error('Error:', e.message)
    process.exit(1)
  })
}

export { fetchFromAPI, syncNutritionData, transformData }
