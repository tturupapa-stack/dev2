import 'dotenv/config'
import axios from 'axios'
import * as cheerio from 'cheerio'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY // 서버 적재용
)

const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36'

async function fetchHtml(url) {
  const res = await axios.get(url, {
    headers: {
      'User-Agent': UA,
      'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
    },
    timeout: 30000,
  })
  return res.data
}

// iHerb 페이지 구조가 바뀔 수 있어 "최대한 안전한" 파싱만 합니다.
// (필요하면 네 프로젝트 데이터 포맷에 맞게 더 정교화 가능)
function parseProductAndReviews(html, url) {
  const $ = cheerio.load(html)

  // 제품 기본 정보 (가능한 것만)
  const title =
    $('h1').first().text().trim() ||
    $('meta[property="og:title"]').attr('content')?.trim() ||
    null

  const brand =
    $('[data-ga-label="brand"]').first().text().trim() ||
    $('a[href*="/brands/"]').first().text().trim() ||
    null

  const ratingAvgText =
    $('[data-testid*="rating"]').first().text().trim() ||
    $('[class*="rating"]').first().text().trim() ||
    null

  // 숫자만 대충 추출
  const ratingAvg = ratingAvgText ? Number((ratingAvgText.match(/[\d.]+/) || [])[0]) : null

  // 리뷰는 페이지에 따라 서버 렌더링이 아닐 수 있어요.
  // 일단 "페이지 안에 있는 리뷰 블록"을 최대한 긁어옵니다.
  const reviews = []

  const reviewBlocks = $('[data-testid*="review"], [class*="review"]').slice(0, 25)
  reviewBlocks.each((_, el) => {
    const block = $(el)

    const author =
      block.find('[class*="author"], [data-testid*="author"]').first().text().trim() || null
    const body =
      block.find('[class*="content"], [class*="text"], [data-testid*="content"]').first().text().trim() ||
      block.text().trim() ||
      null
    const ratingText =
      block.find('[class*="star"], [data-testid*="rating"]').first().text().trim() || null
    const rating = ratingText ? Number((ratingText.match(/\d+/) || [])[0]) : null

    if (body && body.length > 20) {
      // 리뷰 고유 ID가 명확치 않으니, (author+body 일부)로 간이 해시 키 만들기
      const source_review_id = Buffer.from((author || '') + '|' + body.slice(0, 80))
        .toString('base64')
        .replace(/=+$/g, '')

      reviews.push({
        source_review_id,
        author,
        rating,
        title: null,
        body,
        language: 'ko', // 대충 기본. 필요하면 감지 로직 추가
        helpful_count: null,
        review_date: null,
      })
    }
  })

  return {
    product: {
      source: 'iherb',
      source_product_id:
        $('meta[property="og:url"]').attr('content')?.split('/').pop()?.split('?')[0] ||
        url.split('/').pop()?.split('?')[0] ||
        url,
      url,
      title,
      brand,
      category: null,
      price: null,
      currency: 'USD',
      rating_avg: Number.isFinite(ratingAvg) ? ratingAvg : null,
      rating_count: null,
    },
    reviews: reviews.slice(0, 20),
  }
}

async function upsertToSupabase(parsed) {
  // 제품 업서트
  const { data: pRow, error: pErr } = await supabase
    .from('products')
    .upsert(parsed.product, { onConflict: 'source,source_product_id' })
    .select('id')
    .single()

  if (pErr) throw pErr
  const productId = pRow.id

  // 리뷰 upsert (product_id 주입)
 // source_review_id 기준으로 중복 제거
const uniqMap = new Map()

parsed.reviews.forEach((r) => {
  if (!uniqMap.has(r.source_review_id)) {
    uniqMap.set(r.source_review_id, r)
  }
})

const payload = Array.from(uniqMap.values()).map((r) => ({
  product_id: productId,
  source: 'iherb',
  ...r,
}))


  if (payload.length) {
    const { error: rErr } = await supabase
      .from('reviews')
      .upsert(payload, { onConflict: 'source,source_review_id' })
    if (rErr) throw rErr
  }

  return { productId, reviewCount: payload.length }
}

async function main() {
  const url = process.argv[2]
  if (!url) {
    console.error('Usage: node scrape-iherb-to-supabase.mjs "<iherb product url>"')
    process.exit(1)
  }

  console.log('Fetching:', url)
  const html = await fetchHtml(url)

  const parsed = parseProductAndReviews(html, url)
  console.log('Parsed product:', {
    title: parsed.product.title,
    brand: parsed.product.brand,
    rating_avg: parsed.product.rating_avg,
    reviews: parsed.reviews.length,
  })

  const result = await upsertToSupabase(parsed)
  console.log('✅ Saved to Supabase:', result)
}

main().catch((e) => {
  console.error('❌ Error:', e?.message || e)
  process.exit(1)
})
