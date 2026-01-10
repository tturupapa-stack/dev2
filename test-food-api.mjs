import 'dotenv/config'
import axios from 'axios'

const API_KEY = process.env.FOOD_SAFETY_API_KEY || 'cd441dadd78626cd0ffa584f78556f198aaea45a9aadb26f2eb87d2f4323664f'
const BASE_URL = 'http://api.data.go.kr/openapi/tn_pubr_public_health_functional_food_nutrition_info_api'

async function testAPI() {
  console.log('📡 식품의약품안전처 API 테스트 중...')
  console.log(`🔑 API Key: ${API_KEY.substring(0, 20)}...`)

  try {
    // 샘플 코드처럼 URL 쿼리 스트링 직접 구성
    const queryParams = new URLSearchParams({
      serviceKey: API_KEY,
      pageNo: '1',
      numOfRows: '10',
      type: 'json'
    }).toString()

    const fullUrl = `${BASE_URL}?${queryParams}`

    console.log('\n📍 요청 URL:', fullUrl.substring(0, 150) + '...')

    const response = await axios.get(fullUrl, {
      timeout: 30000,
      headers: {
        'Accept': 'application/json'
      }
    })

    console.log('\n✅ API 응답 성공!')
    console.log('📊 응답 상태:', response.status)
    console.log('📦 응답 데이터 구조:', Object.keys(response.data))

    // 응답 데이터 샘플 출력
    if (response.data) {
      console.log('\n=== 응답 샘플 ===')
      console.log(JSON.stringify(response.data, null, 2).substring(0, 1000))
    }

    return response.data

  } catch (error) {
    console.error('\n❌ API 오류 발생:')
    if (error.response) {
      console.error('상태 코드:', error.response.status)
      console.error('응답 데이터:', error.response.data)
    } else if (error.request) {
      console.error('요청 오류:', error.message)
    } else {
      console.error('오류:', error.message)
    }
    throw error
  }
}

testAPI().catch(e => {
  console.error('\n💥 테스트 실패:', e.message)
  process.exit(1)
})
