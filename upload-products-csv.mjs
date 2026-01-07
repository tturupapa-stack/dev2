import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import { parse } from 'csv-parse/sync'
import iconv from 'iconv-lite'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY
)

async function uploadProductsFromCSV(csvPath) {
  console.log(`📂 CSV 파일 읽는 중: ${csvPath}`)

  // EUC-KR/CP949 인코딩으로 읽기
  const buffer = fs.readFileSync(csvPath)
  const fileContent = iconv.decode(buffer, 'euc-kr')
  const records = parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
  })

  console.log(`📦 ${records.length}개의 제품 발견`)

  if (records.length === 0) {
    console.log('⚠️ 업로드할 제품이 없습니다')
    return
  }

  const products = records.map((row) => ({
    source: row.source || null,
    source_product_id: row.source_product_id || null,
    url: row.url || null,
    title: row.title || null,
    brand: row.brand || null,
    category: row.category || null,
    price: row.price && row.price.trim() ? parseInt(row.price) : null,
    currency: row.currency || null,
    rating_avg: row.rating_avg && row.rating_avg.trim() ? parseFloat(row.rating_avg) : null,
    rating_count: row.rating_count && row.rating_count.trim() ? parseInt(row.rating_count) : null,
  }))

  console.log('⬆️ Supabase에 업로드 중...')

  const { data, error } = await supabase
    .from('products')
    .upsert(products, { onConflict: 'source,source_product_id' })

  if (error) {
    console.error('❌ 업로드 중 오류 발생:', error)
    throw error
  }

  console.log(`✅ ${products.length}개의 제품이 성공적으로 업로드되었습니다!`)
  console.log('📊 업로드된 제품:')
  products.forEach((p) => {
    console.log(`  - ${p.brand}: ${p.title?.substring(0, 50)}...`)
  })
}

async function uploadReviewsFromCSV(csvPath) {
  console.log(`📂 CSV 파일 읽는 중: ${csvPath}`)

  // EUC-KR/CP949 인코딩으로 읽기
  const buffer = fs.readFileSync(csvPath)
  const fileContent = iconv.decode(buffer, 'euc-kr')
  const records = parse(fileContent, {
    columns: true,
    skip_empty_lines: true,
  })

  console.log(`📝 ${records.length}개의 리뷰 발견`)

  if (records.length === 0) {
    console.log('⚠️ 업로드할 리뷰가 없습니다')
    return
  }

  // 1. products 테이블에서 source_product_id -> id 매핑 가져오기
  console.log('🔍 제품 ID 매핑 조회 중...')
  const { data: products, error: productsError } = await supabase
    .from('products')
    .select('id, source, source_product_id')

  if (productsError) {
    console.error('❌ 제품 조회 중 오류:', productsError)
    throw productsError
  }

  // source_product_id -> id 매핑 생성
  const productIdMap = new Map()
  products.forEach((p) => {
    const key = `${p.source}:${p.source_product_id}`
    productIdMap.set(key, p.id)
  })

  console.log(`✅ ${productIdMap.size}개의 제품 매핑 완료`)

  // 2. CSV의 product_id(source_product_id)를 실제 id로 변환
  const reviews = []
  const skipped = []

  for (const row of records) {
    const sourceProductId = row.product_id?.trim()
    const source = row.source?.trim() || 'iHerb'
    const key = `${source}:${sourceProductId}`
    const actualProductId = productIdMap.get(key)

    if (!actualProductId) {
      skipped.push({ source, sourceProductId })
      continue
    }

    // source_review_id를 고유하게 만들기 위해 source_product_id 포함
    const originalReviewId = row.source_review_id?.trim() || '0'
    const uniqueReviewId = `${sourceProductId}-${originalReviewId}`

    reviews.push({
      product_id: actualProductId,
      source: source,
      source_review_id: uniqueReviewId,
      author: row.author || null,
      rating: row.rating && row.rating.trim() ? parseInt(row.rating) : null,
      title: row.title || null,
      body: row.body || null,
      language: row.language || null,
      helpful_count: row.helpful_count && row.helpful_count.trim() ? parseInt(row.helpful_count) : null,
      review_date: row.review_date || null,
    })
  }

  if (skipped.length > 0) {
    console.log(`⚠️ 제품을 찾을 수 없어 ${skipped.length}개 리뷰를 건너뜁니다:`)
    skipped.forEach((s) => console.log(`  - ${s.source}:${s.sourceProductId}`))
  }

  if (reviews.length === 0) {
    console.log('⚠️ 업로드할 리뷰가 없습니다')
    return
  }

  // 중복 제거: source + source_review_id 기준으로 마지막 항목만 유지
  const uniqueReviews = []
  const seen = new Set()

  for (const review of reviews) {
    const key = `${review.source}:${review.source_review_id}`
    if (!seen.has(key)) {
      seen.add(key)
      uniqueReviews.push(review)
    }
  }

  if (reviews.length !== uniqueReviews.length) {
    console.log(`⚠️ ${reviews.length - uniqueReviews.length}개의 중복된 리뷰를 제거했습니다`)
  }

  console.log(`⬆️ ${uniqueReviews.length}개 리뷰를 Supabase에 업로드 중...`)

  const { data, error } = await supabase
    .from('reviews')
    .upsert(uniqueReviews, { onConflict: 'source,source_review_id' })

  if (error) {
    console.error('❌ 업로드 중 오류 발생:', error)
    throw error
  }

  console.log(`✅ ${uniqueReviews.length}개의 리뷰가 성공적으로 업로드되었습니다!`)
}

const mode = process.argv[2] || 'products'

try {
  if (mode === 'products' || mode === 'all') {
    await uploadProductsFromCSV('products_rows.csv')
  }

  if (mode === 'reviews' || mode === 'all') {
    await uploadReviewsFromCSV('reviews_rows.csv')
  }

  console.log('✅ 모든 업로드 완료!')
} catch (e) {
  console.error('❌ Error:', e?.message || e)
  process.exit(1)
}
