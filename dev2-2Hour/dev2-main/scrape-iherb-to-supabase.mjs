import 'dotenv/config'
import axios from 'axios'
import * as cheerio from 'cheerio'
import fs from 'fs'
import crypto from 'crypto'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
)

const REVIEW_LIMIT = 20

function cleanText(s) {
  if (!s) return null
  const t = String(s).replace(/\s+/g, ' ').trim()
  return t.length ? t : null
}

function hashReview(author, title, body) {
  return crypto
    .createHash('sha256')
    .update((author || '') + '|' + (title || '') + '|' + (body || ''))
    .digest('hex')
}

function looksLikeBlocked(html) {
  const h = html.toLowerCase()
  const signals = [
    'captcha',
    'verify',
    'robot',
    'unusual traffic',
    'challenge',
    'cloudflare',
    '본인 인증',
    '길게 누르기',
    '로봇',
    '인증이 필요',
  ]
  return signals.some((s) => h.includes(s))
}

async function fetchHtml(url) {
  const res = await axios.get(url, {
    timeout: 30000,
    headers: {
      // UA/언어만으로도 일부는 통과하지만, 지금처럼 인증 뜨면 대부분 실패합니다.
      'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36',
      'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
      Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    },
    maxRedirects: 5,
    validateStatus: (s) => s >= 200 && s < 400,
  })
  return String(res.data)
}

function parseProductAndReviews(html, url) {
  const $ = cheerio.load(html)

  const title = cleanText($('h1').first().text())
  const brand = cleanText($('a[href*="/brands/"]').first().text())

  // ✅ 리뷰 셀렉터는 iHerb가 자주 바뀌어서 “후보”를 여러 개 둡니다.
  // 단, axios로는 JS 렌더링된 리뷰가 없을 확률이 높아 0개가 정상일 수 있음.
  const reviewCandidates = []
  const selectors = [
    '[data-testid*="review"]',
    '[itemtype*="Review"]',
    '[class*="review"]',
  ]

  let nodes = null
  for (const sel of selectors) {
    const found = $(sel)
    if (found.length >= 3) {
      nodes = found
      break
    }
  }

  if (nodes) {
    nodes.each((_, el) => {
      const card = $(el)

      const author = cleanText(
        card.find('[itemprop="author"], [class*="author"], strong, a').first().text()
      )

      const body = cleanText(
        card
          .find('[itemprop="reviewBody"], [class*="reviewBody"], [class*="content"], [class*="text"], p')
          .first()
          .text()
      )

      const title2 = cleanText(
        card.find('[itemprop="name"], [class*="title"], h3, h4').first().text()
      )

      // 별점은 HTML에 없을 수 있음
      const ratingLabel = card.find('[aria-label*="별"], [aria-label*="out of 5"]').first().attr('aria-label')
      const rating = ratingLabel ? Number((ratingLabel.match(/\d+/) || [])[0]) : null

      if (body && body.length >= 30) {
        reviewCandidates.push({
          source_review_id: hashReview(author, title2, body),
          author: author || null,
          rating: Number.isFinite(rating) ? rating : null,
          title: title2 || null,
          body,
          language: 'ko',
          helpful_count: null,
          review_date: null,
        })
      }
    })
  }

  // 중복 제거 + limit
  const uniq = new Map()
  for (const r of reviewCandidates) {
    if (!uniq.has(r.source_review_id)) uniq.set(r.source_review_id, r)
  }

  return {
    product: {
      url,
      title,
      brand,
    },
    reviews: Array.from(uniq.values()).slice(0, REVIEW_LIMIT),
  }
}

async function saveToSupabase(url, product, reviews) {
  const source = 'iherb_axios'
  const source_product_id = url.split('/').pop()?.split('?')[0] || url

  const productPayload = {
    source,
    source_product_id,
    url,
    title: product.title || null,
    brand: product.brand || null,
    category: null,
    price: null,
    currency: 'KRW',
    rating_avg: null,
    rating_count: null,
  }

  const { data: productRow, error: productErr } = await supabase
    .from('products')
    .upsert(productPayload, { onConflict: 'source,source_product_id' })
    .select('id')
    .single()
  if (productErr) throw productErr

  const productId = productRow.id

  const payload = reviews.map((r) => ({ product_id: productId, source, ...r }))
  if (payload.length) {
    const { error: reviewErr } = await supabase
      .from('reviews')
      .upsert(payload, { onConflict: 'source,source_review_id' })
    if (reviewErr) throw reviewErr
  }

  console.log('✅ Saved:', { productId, reviewCount: payload.length })
}

async function run(url) {
  if (!url?.startsWith('https://')) throw new Error('URL은 https://로 시작해야 합니다.')

  console.log('Fetching:', url)
  const html = await fetchHtml(url)

  // 디버그 저장
  if (process.env.DEBUG === '1') {
    fs.writeFileSync('debug_axios.html', html, 'utf-8')
    console.log('🧪 Saved debug_axios.html')
  }

  // 차단 판별
  if (looksLikeBlocked(html)) {
    console.log('⛔ 차단/인증 페이지로 보입니다. (axios+cheerio로는 리뷰 수집이 어렵습니다)')
    console.log('   → A안(수동 입력) 또는 다른 소스(쿠팡/네이버/아마존) 전환을 추천합니다.')
    return
  }

  const { product, reviews } = parseProductAndReviews(html, url)

  console.log('Parsed product:', product)
  console.log('Parsed reviews:', reviews.length)

  await saveToSupabase(url, product, reviews)

  if (reviews.length === 0) {
    console.log('⚠️ 리뷰가 0개입니다. (JS 렌더링 리뷰라 HTML에 없을 가능성이 큽니다)')
  }
}

const url = process.argv[2]
run(url).catch((e) => {
  console.error('❌ Error:', e?.message || e)
  process.exit(1)
})
