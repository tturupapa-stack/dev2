/* ==========================================
   iHerb 리뷰 20개 수집 → Supabase 저장 (통합본)
   - iHerb "본인 인증(길게 누르기)" 뜨면: 사람이 직접 통과 후 Enter
   - persistent profile로 세션(쿠키/스토리지) 유지
   - networkidle 타임아웃 회피: domcontentloaded + 핵심 요소 대기
   - API(XHR/Fetch JSON) 우선, 실패 시 DOM fallback
   ========================================== */

import 'dotenv/config'
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import crypto from 'crypto'
import fs from 'fs'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
)

const REVIEW_LIMIT = 20
const PROFILE_DIR = process.env.PW_PROFILE_DIR || './pw-profile'
const DEBUG = process.env.DEBUG === '1'
const HEADLESS = process.env.HEADLESS !== '0' // 기본 headless=true, HEADLESS=0이면 창 뜸

function assertValidUrl(url) {
  if (!url || typeof url !== 'string') throw new Error('❌ URL이 비었습니다')
  if (!url.startsWith('https://')) throw new Error('❌ URL은 반드시 https:// 로 시작해야 합니다')
  if (url.includes('](') || url.includes('[') || url.includes(')')) {
    throw new Error('❌ 마크다운([텍스트](URL)) 말고 URL만 넣어주세요.')
  }
}

function cleanText(s) {
  if (!s) return null
  const t = String(s).replace(/\s+/g, ' ').trim()
  return t.length ? t : null
}

function isJunkBody(body) {
  if (!body) return true
  const b = body.toLowerCase()
  const junk = [
    'based on',
    'ratings',
    'see customer reviews',
    'customer reviews',
    '평점',
    '고객 리뷰',
    '리뷰 보기',
  ]
  if (junk.some((p) => b.includes(p))) return true
  if (body.length < 30) return true
  return false
}

function hashReview(author, title, body) {
  return crypto
    .createHash('sha256')
    .update((author || '') + '|' + (title || '') + '|' + (body || ''))
    .digest('hex')
}

function waitForEnter() {
  return new Promise((resolve) => {
    process.stdin.resume()
    process.stdin.once('data', () => resolve())
  })
}

/** 인증 화면(길게 누르기)이 뜨면 사용자가 직접 통과하도록 안내하고 대기 */
async function handleHumanVerification(page) {
  const challenge = page.locator('text=본인 인증이 필요합니다')
  const button = page.locator('text=길게 누르기')

  const visible = await challenge.isVisible({ timeout: 2500 }).catch(() => false)
  if (!visible) return false

  console.log('⚠️ iHerb 본인 인증 화면이 떴습니다.')
  console.log('   → 열린 브라우저에서 "길게 누르기"를 직접 완료한 뒤, 이 터미널에서 Enter를 눌러주세요.')

  // headless면 사용자가 조작 불가 → headless 끄라고 안내
  if (HEADLESS) {
    console.log('   ※ 지금은 HEADLESS 모드라 인증이 불가능합니다.')
    console.log('   ※ 다음처럼 다시 실행하세요: HEADLESS=0 DEBUG=1 node scrape-iherb-playwright.mjs "<url>"')
    throw new Error('본인 인증 화면 감지됨 (HEADLESS=0으로 재실행 필요)')
  }

  // 사용자가 인증을 완료할 시간을 줌
  await waitForEnter()

  // 인증 통과 후 페이지가 바뀌거나 로딩되었는지 확인
  await page.waitForTimeout(1000)
  await page.waitForSelector('h1', { timeout: 60000 }).catch(() => {})
  const still = await button.isVisible({ timeout: 1500 }).catch(() => false)
  if (still) {
    console.log('⚠️ 아직 인증이 남아있는 것 같습니다. 다시 "길게 누르기" 후 Enter를 눌러주세요.')
    await waitForEnter()
  }
  return true
}

/** JSON 트리에서 리뷰로 보이는 객체들 추출 */
function extractReviewObjects(root) {
  const out = []
  const visit = (node) => {
    if (!node) return
    if (Array.isArray(node)) return node.forEach(visit)
    if (typeof node !== 'object') return

    const keys = Object.keys(node)
    const lowerKeys = keys.map((k) => k.toLowerCase())
    const hasTextKey = lowerKeys.some((k) =>
      ['reviewtext', 'review_text', 'text', 'body', 'content', 'comment'].includes(k)
    ) || lowerKeys.some((k) => k.includes('review') && k.includes('text'))

    const hasRatingKey = lowerKeys.some((k) => ['rating', 'stars', 'score'].includes(k))
    const hasAuthorKey = lowerKeys.some((k) =>
      ['author', 'username', 'user', 'displayname', 'name'].includes(k)
    )

    if (hasTextKey && (hasRatingKey || hasAuthorKey)) out.push(node)
    keys.forEach((k) => visit(node[k]))
  }
  visit(root)
  return out
}

function normalizeApiReview(obj) {
  const get = (...cands) => {
    for (const c of cands) {
      if (obj[c] != null) return obj[c]
      const found = Object.keys(obj).find((k) => k.toLowerCase() === String(c).toLowerCase())
      if (found) return obj[found]
    }
    return null
  }

  const body = cleanText(get('reviewText', 'review_text', 'text', 'body', 'content', 'comment'))
  const title = cleanText(get('title', 'headline', 'summary'))

  const ratingRaw = get('rating', 'stars', 'score')
  const rating = ratingRaw != null ? Number(String(ratingRaw).match(/\d+/)?.[0]) : null

  let author = get('author', 'userName', 'username', 'displayName', 'name')
  if (author && typeof author === 'object') {
    author = author.name || author.displayName || author.username || null
  }
  author = cleanText(author)

  const helpfulRaw = get('helpful', 'helpfulCount', 'helpful_count', 'upvotes')
  const helpful_count = helpfulRaw != null ? Number(String(helpfulRaw).match(/\d+/)?.[0]) : null

  const dateRaw = get('date', 'createdAt', 'created_at', 'reviewDate', 'review_date')
  const review_date = dateRaw ? String(dateRaw).slice(0, 10) : null

  if (!body || isJunkBody(body)) return null

  return {
    source_review_id: hashReview(author, title, body),
    author,
    rating,
    title,
    body,
    language: 'ko',
    helpful_count,
    review_date,
  }
}

async function parseReviewsFromDom(page) {
  // ✅ iHerb의 실제 리뷰 카드 찾기 (ugc-review-item, dt-review-item 등)
  const candidates = [
    'ugc-review-item',
    '[class*="ugc-review"]',
    '[class*="dt-review"]',
    '[class*="review-item"]',
    '[data-testid*="review"]',
    '[class*="review"]',
    '[itemtype*="Review"]',
    'article',
  ]

  let cards = null
  for (const sel of candidates) {
    const loc = page.locator(sel)
    const cnt = await loc.count().catch(() => 0)
    console.log(`  Checking selector "${sel}": found ${cnt} elements`)
    if (cnt >= 3) {
      cards = loc
      console.log(`  ✓ Using selector: ${sel}`)
      break
    }
  }
  if (!cards) cards = page.locator('article')

  const count = await cards.count()
  const list = []

  console.log(`  Parsing ${count} potential review cards...`)

  for (let i = 0; i < count && list.length < REVIEW_LIMIT * 3; i++) {
    const c = cards.nth(i)

    const author = cleanText(
      await c.locator('[itemprop="author"], [class*="author"], [class*="user"], [class*="name"], strong, a')
        .first().textContent().catch(() => null)
    )

    let body = cleanText(
      await c.locator(
        '[itemprop="reviewBody"], [data-testid*="reviewBody"], [class*="reviewBody"], [class*="review-text"], [class*="content"], [class*="text"], p'
      ).first().textContent().catch(() => null)
    )

    if (!body || isJunkBody(body)) {
      const full = cleanText(await c.textContent().catch(() => null))
      if (full && full.length > 80 && !isJunkBody(full)) body = full
    }

    const title = cleanText(
      await c.locator('[itemprop="name"], [class*="title"], [class*="headline"], h3, h4, h5')
        .first().textContent().catch(() => null)
    )

    const ratingLabel = await c.locator('[aria-label*="별"], [aria-label*="out of 5"], [aria-label*="stars"]')
      .first().getAttribute('aria-label').catch(() => null)
    const rating = ratingLabel ? Number((ratingLabel.match(/\d+/) || [])[0]) : null

    if (!body || isJunkBody(body)) continue

    list.push({
      source_review_id: hashReview(author, title, body),
      author: author || null,
      rating,
      title: title || null,
      body,
      language: 'ko',
      helpful_count: null,
      review_date: null,
    })
  }

  console.log(`  Extracted ${list.length} reviews from DOM`)

  const uniq = new Map()
  for (const r of list) if (!uniq.has(r.source_review_id)) uniq.set(r.source_review_id, r)
  return Array.from(uniq.values()).slice(0, REVIEW_LIMIT)
}

async function run(url) {
  assertValidUrl(url)

  // ✅ persistent context: 세션(쿠키/스토리지) 유지
  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: HEADLESS,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
    locale: 'ko-KR',
  })

  const page = await context.newPage()
  page.setDefaultNavigationTimeout(120000)
  page.setDefaultTimeout(60000)

  // 로딩 빠르게: 이미지/폰트/미디어 차단
  await page.route('**/*', (route) => {
    const type = route.request().resourceType()
    if (type === 'image' || type === 'media' || type === 'font') return route.abort()
    route.continue()
  })

  // ✅ API 리뷰 응답 수집 버퍼
  const apiReviews = []
  const apiUrls = [] // 디버그용

  page.on('request', (req) => {
    const u = req.url()
    const lowerU = u.toLowerCase()
    // 디버그: 리뷰 관련 모든 요청 기록
    if (DEBUG && (lowerU.includes('review') || lowerU.includes('ugc') || lowerU.includes('graphql') || lowerU.includes('api'))) {
      console.log(`📤 REQUEST: ${req.method()} ${u}`)
    }
  })

  page.on('response', async (res) => {
    try {
      const rt = res.request().resourceType()
      const u = res.url()
      const lowerU = u.toLowerCase()

      // 디버그: 모든 XHR/Fetch 응답 기록
      if (DEBUG && (rt === 'xhr' || rt === 'fetch')) {
        console.log(`📥 RESPONSE: ${res.status()} ${u}`)
      }

      if (rt !== 'xhr' && rt !== 'fetch') return

      const ct = (await res.headers())['content-type'] || ''
      if (!ct.includes('application/json')) return

      // 디버그: 모든 JSON API 호출 기록
      if (DEBUG && (lowerU.includes('review') || lowerU.includes('ugc') || lowerU.includes('rating') || lowerU.includes('graphql'))) {
        apiUrls.push(u)
        console.log(`🌐 JSON API Call: ${u}`)
      }

      if (!lowerU.includes('review') && !lowerU.includes('ugc') && !lowerU.includes('rating') && !lowerU.includes('graphql')) return

      const json = await res.json().catch(() => null)
      if (!json) return

      if (DEBUG) {
        console.log(`📦 JSON Response from ${u}:`, JSON.stringify(json).slice(0, 300))
      }

      const candidates = extractReviewObjects(json)
      for (const c of candidates) {
        const norm = normalizeApiReview(c)
        if (norm) {
          apiReviews.push(norm)
          if (DEBUG) console.log(`✓ Captured review: ${norm.body?.slice(0, 50)}...`)
        }
      }
    } catch (err) {
      if (DEBUG) console.error('Error processing response:', err.message)
    }
  })

  console.log('🔗 Opening:', url)

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 })
  await handleHumanVerification(page) // ← 인증 뜨면 여기서 멈춰서 사용자 조작 기다림

  await page.waitForSelector('h1', { timeout: 60000 })
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {})

  if (DEBUG) {
    await page.screenshot({ path: 'debug_iherb.png', fullPage: true }).catch(() => {})
    fs.writeFileSync('debug_iherb.html', (await page.content().catch(() => '')) || '', 'utf-8')
    console.log('🧪 DEBUG saved: debug_iherb.png / debug_iherb.html')
  }

  // 제품 정보
  const title = cleanText(await page.locator('h1').first().textContent().catch(() => null))
  const brand = cleanText(await page.locator('a[href*="/brands/"]').first().textContent().catch(() => null))

  // ✅ 리뷰 섹션으로 스크롤 (Web Component 로딩 트리거)
  console.log('⏳ Scrolling to reviews section...')
  const reviewsSection = page.locator('#product-reviews, ugc-pdp-review')
  if (await reviewsSection.count()) {
    await reviewsSection.first().scrollIntoViewIfNeeded().catch(() => {})
    await page.waitForTimeout(2000)
  }

  // ✅ Web Component가 hydrate되길 기다림
  await page.waitForSelector('ugc-review-list.hydrated', { timeout: 10000 }).catch(() => {})
  await page.waitForTimeout(3000)

  // ✅ iHerb UGC API 직접 호출 시도
  const numericProductId = url.split('/').pop()?.split('?')[0].match(/\d+$/)?.[0]
  if (numericProductId) {
    console.log(`📡 Attempting direct API call for product ${numericProductId}...`)
    try {
      const ugcUrl = `https://ugc.iherb.com/api/review/product/${numericProductId}?page=1&pageSize=20&sort=MostHelpful&locale=ko-KR`

      // Use page.request (Playwright's request context) to bypass CORS
      const apiResponse = await page.request.get(ugcUrl, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      })

      if (apiResponse.ok()) {
        const ugcResponse = await apiResponse.json()

        if (DEBUG) {
          console.log(`📦 UGC API Response:`, JSON.stringify(ugcResponse).slice(0, 500))
        }

        if (ugcResponse?.reviews || ugcResponse?.data?.reviews) {
          const reviewData = ugcResponse.reviews || ugcResponse.data?.reviews || []
          for (const r of reviewData.slice(0, REVIEW_LIMIT)) {
            const norm = normalizeApiReview(r)
            if (norm) apiReviews.push(norm)
          }
          console.log(`✓ Fetched ${apiReviews.length} reviews from direct API`)
        }
      } else {
        console.log(`⚠️ API returned status: ${apiResponse.status()}`)
      }
    } catch (e) {
      console.log(`⚠️ Direct API call failed: ${e.message}`)
    }
  }

  // 스크롤 + 더보기로 로딩 유도
  console.log('⏳ Loading reviews (scroll/click loop)...')
  for (let i = 0; i < 10; i++) {
    await page.mouse.wheel(0, 1400).catch(() => {})
    await page.waitForTimeout(900)

    const moreBtn = page.locator('button:has-text("더 보기"), button:has-text("Load More"), button:has-text("더보기"), button:has-text("Show More")')
    if (await moreBtn.count()) {
      await moreBtn.first().click().catch(() => {})
      await page.waitForTimeout(1300)
    }
    console.log(`...loop ${i + 1}/10`)
  }

  await page.waitForTimeout(3000)

  // ✅ 1) API 리뷰 우선
  let reviews = []
  if (apiReviews.length) {
    const uniq = new Map()
    for (const r of apiReviews) if (!uniq.has(r.source_review_id)) uniq.set(r.source_review_id, r)
    reviews = Array.from(uniq.values()).slice(0, REVIEW_LIMIT)
    console.log(`🧠 API reviews captured: ${reviews.length}`)
  }

  // ✅ 2) DOM fallback
  if (reviews.length < 5) {
    const dom = await parseReviewsFromDom(page)
    reviews = dom
    console.log(`🧩 DOM reviews parsed: ${reviews.length}`)
  }

  console.log(`📝 Final reviews: ${reviews.length}`)

  // (선택) 세션 상태 저장(프로필로도 유지되지만 백업용)
  await context.storageState({ path: 'storageState.json' }).catch(() => {})

  await context.close()

  // products upsert
  const source_product_id = url.split('/').pop()?.split('?')[0] || url
  const productPayload = {
    source: 'iherb',
    source_product_id,
    url,
    title: title || null,
    brand: brand || null,
    category: null,
    price: null,
    currency: 'USD',
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

  const reviewPayload = reviews.map((r) => ({
    product_id: productId,
    source: 'iherb',
    ...r,
  }))

  if (reviewPayload.length) {
    const { error: reviewErr } = await supabase
      .from('reviews')
      .upsert(reviewPayload, { onConflict: 'source,source_review_id' })
    if (reviewErr) throw reviewErr
  }

  console.log('✅ Saved to Supabase:', { productId, reviewCount: reviewPayload.length })
}

const url = process.argv[2]
run(url).catch((err) => {
  console.error('❌ Error:', err?.message || err)
  process.exit(1)
})
