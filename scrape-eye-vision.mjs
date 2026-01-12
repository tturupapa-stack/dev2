/* ==========================================
   iHerb Eye Vision 카테고리 상위 5개 제품 스크래핑
   - Playwright 사용
   - products + nutrition_info 데이터 생성
   ========================================== */

import 'dotenv/config'
import { chromium } from 'playwright'
import readline from 'readline'

const CATEGORY_URL = 'https://kr.iherb.com/c/eye-vision'
const PRODUCT_LIMIT = 5
const PROFILE_DIR = process.env.PW_PROFILE_DIR || './pw-profile'

function waitForEnter(message = '계속하려면 Enter를 누르세요...') {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    rl.question(`\n⏳ ${message}\n`, () => {
      rl.close()
      resolve()
    })
  })
}

async function scrapeProducts() {
  console.log('🚀 Playwright 시작 (persistent profile)...')

  // Persistent context 사용 - 쿠키/세션 유지
  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false, // 봇 감지 우회를 위해 headless=false
    locale: 'ko-KR',
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  })

  const page = await context.newPage()

  try {
    console.log(`📡 카테고리 페이지 접속: ${CATEGORY_URL}`)
    await page.goto(CATEGORY_URL, { waitUntil: 'domcontentloaded', timeout: 60000 })

    // 봇 감지 확인 및 수동 인증 대기
    await page.waitForTimeout(2000)
    const title = await page.title()
    if (title.includes('기다리') || title.includes('wait') || title.includes('Checking')) {
      console.log('🔒 봇 감지 발생! 브라우저에서 인증을 완료해주세요.')
      await waitForEnter('인증 완료 후 Enter를 누르세요...')
    }

    // 페이지 로드 대기
    await page.waitForTimeout(3000)

    console.log('📋 제품 목록 수집 중...')

    // 제품 링크 수집
    const productLinks = await page.$$eval(
      '.product-cell-container a.absolute-link-wrapper, .product a[href*="/pr/"]',
      (links, limit) => {
        const urls = []
        for (const link of links) {
          const href = link.href
          if (href && href.includes('/pr/') && !urls.includes(href)) {
            urls.push(href)
          }
          if (urls.length >= limit) break
        }
        return urls
      },
      PRODUCT_LIMIT
    )

    console.log(`✅ ${productLinks.length}개 제품 링크 수집 완료`)

    const products = []
    const nutritionInfos = []

    // 각 제품 페이지에서 상세 정보 수집
    for (let i = 0; i < productLinks.length; i++) {
      const url = productLinks[i]
      console.log(`\n📦 [${i + 1}/${productLinks.length}] 제품 정보 수집: ${url}`)

      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
        await page.waitForTimeout(2000)

        // 봇 감지 확인
        let pageTitle = await page.title()
        if (pageTitle.includes('기다리') || pageTitle.includes('wait')) {
          console.log('  🔒 봇 감지! 브라우저에서 인증 완료 후 Enter...')
          await waitForEnter()
          await page.waitForTimeout(2000)
          pageTitle = await page.title()
        }

        // 제품 ID 추출
        const productId = url.match(/\/(\d+)$/)?.[1] || `prod_${i + 1}`

        console.log(`  📄 페이지: ${pageTitle.substring(0, 50)}...`)

        // 제품 기본 정보 - 다양한 셀렉터 시도
        const name = await page.$eval(
          '#name, h1#product-title, h1[itemprop="name"], [class*="product-name"], [class*="product-title"], h1',
          el => el.textContent.trim()
        ).catch(() => pageTitle.split('|')[0]?.trim() || '')

        const brand = await page.$eval(
          'a[href*="/m/"] span, [class*="brand"], [itemprop="brand"] span, [class*="manufacturer"]',
          el => el.textContent.trim()
        ).catch(() => '')

        const priceText = await page.$eval(
          '[class*="price"] bdi, [class*="price-inner"], .product-price, [data-price]',
          el => el.textContent.trim()
        ).catch(() => '0')

        const price = parseFloat(priceText.replace(/[^\d.]/g, '')) || 0

        // 서빙 정보 - 제품 상세에서 추출
        const servingSize = await page.$eval(
          '[class*="serving"], [class*="Serving"]',
          el => el.textContent.trim()
        ).catch(() => '')

        // 성분 정보
        const ingredients = await page.$eval(
          '[class*="supplement"], [class*="ingredient"], [class*="Ingredient"]',
          el => el.textContent.trim().substring(0, 1000)
        ).catch(() => '')

        const product = {
          id: productId,
          name: name,
          brand: brand,
          price: price,
          currency: 'KRW',
          serving_size: servingSize,
          product_url: url,
          ingredients: ingredients,
          category: 'eye-vision',
          created_at: new Date().toISOString()
        }

        products.push(product)
        console.log(`  ✅ 제품: ${product.name || 'N/A'} (${product.brand || 'N/A'}) - ₩${product.price}`)

        // 영양 성분 정보 수집 (Supplement Facts)
        const nutritionData = await page.$$eval(
          '.supplement-facts-table tr, table.supplement-facts tr, .facts-table tr',
          rows => {
            const data = []
            for (const row of rows) {
              const cells = row.querySelectorAll('td, th')
              if (cells.length >= 2) {
                const nutrient = cells[0]?.textContent?.trim() || ''
                const amount = cells[1]?.textContent?.trim() || ''
                const dv = cells[2]?.textContent?.trim() || ''
                if (nutrient && !nutrient.includes('Serving') && !nutrient.includes('서빙')) {
                  data.push({ nutrient, amount, dv })
                }
              }
            }
            return data
          }
        ).catch(() => [])

        for (const item of nutritionData) {
          nutritionInfos.push({
            product_id: productId,
            nutrient_name: item.nutrient,
            amount: item.amount,
            daily_value: item.dv || null,
            created_at: new Date().toISOString()
          })
        }

        console.log(`  📊 영양성분: ${nutritionData.length}건`)

        // 잠시 대기 (서버 부하 방지)
        await page.waitForTimeout(2000)

      } catch (err) {
        console.error(`  ❌ 제품 정보 수집 실패: ${err.message}`)
      }
    }

    console.log('\n' + '='.repeat(50))
    console.log('📊 수집 결과')
    console.log('='.repeat(50))
    console.log(`\n✅ products: ${products.length}건`)
    console.log(`✅ nutrition_info: ${nutritionInfos.length}건`)

    return { products, nutritionInfos }

  } catch (error) {
    console.error('❌ 스크래핑 실패:', error.message)
    throw error
  } finally {
    await context.close()
  }
}

// 실행
console.log('='.repeat(50))
console.log('🔍 iHerb Eye Vision 제품 스크래핑')
console.log('='.repeat(50))

scrapeProducts()
  .then(({ products, nutritionInfos }) => {
    console.log('\n\n📦 PRODUCTS DATA:')
    console.log(JSON.stringify(products, null, 2))

    console.log('\n\n💊 NUTRITION INFO DATA:')
    console.log(JSON.stringify(nutritionInfos, null, 2))
  })
  .catch(err => {
    console.error('💥 실패:', err.message)
    process.exit(1)
  })
