import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY // 서버 적재용
)

const run = async () => {
  // 1) 제품 업서트
  const product = {
    source: 'iherb',
    source_product_id: 'iherb_12345',
    url: 'https://www.iherb.com/...',
    title: 'Vitamin C 1000mg',
    brand: 'NOW Foods',
    category: 'Supplements',
    price: 9.99,
    currency: 'USD',
    rating_avg: 4.7,
    rating_count: 1234
  }

  const { data: pRows, error: pErr } = await supabase
    .from('products')
    .upsert(product, { onConflict: 'source,source_product_id' })
    .select('id')
    .single()

  if (pErr) throw pErr
  const productId = pRows.id

  // 2) 리뷰 삽입
  const reviews = [
    {
      product_id: productId,
      source: 'iherb',
      source_review_id: 'r1',
      author: 'kim',
      rating: 5,
      title: '좋아요',
      body: '배송 빠르고 효과 좋습니다',
      language: 'ko',
      helpful_count: 3
    }
  ]

  const { error: rErr } = await supabase
    .from('reviews')
    .upsert(reviews, { onConflict: 'source,source_review_id' })

  if (rErr) throw rErr

  console.log('✅ inserted product_id:', productId)
}

run().catch((e) => {
  console.error('❌', e)
  process.exit(1)
})
