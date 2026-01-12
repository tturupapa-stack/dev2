import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
)

const data = JSON.parse(fs.readFileSync('./data/eye-vision-products.json', 'utf8'))

console.log('📡 Supabase 업로드 시작...')

// Products 데이터를 기존 스키마에 맞게 변환
const products = data.products.map(p => ({
  source: 'iherb',
  source_product_id: p.id,
  url: p.product_url,
  title: p.name,
  brand: p.brand,
  category: p.category,
  price: p.price,
  currency: p.currency,
  created_at: p.created_at
}))

console.log('\n📦 Products 업로드 중...')
const { data: prodResult, error: prodError } = await supabase
  .from('products')
  .upsert(products, { onConflict: 'source,source_product_id' })

if (prodError) {
  console.error('❌ Products 업로드 실패:', prodError.message)
} else {
  console.log('✅ Products 업로드 성공:', products.length, '건')
}

// 업로드된 products 조회
const { data: insertedProducts } = await supabase
  .from('products')
  .select('id, source_product_id, title')
  .eq('source', 'iherb')
  .eq('category', 'eye-vision')

console.log('📋 Eye Vision 제품:', insertedProducts?.length || 0, '건')
if (insertedProducts) {
  insertedProducts.forEach(p => console.log(`  - [${p.id}] ${p.title}`))
}

// product_nutrition 테이블에 업로드 시도
console.log('\n💊 Nutrition 업로드 중...')

// product_id 매핑
const productIdMap = {}
insertedProducts?.forEach(p => {
  productIdMap[p.source_product_id] = p.id
})

const nutritionData = data.nutrition_info.map(n => ({
  product_id: productIdMap[n.product_id] || null,
  source_product_id: n.product_id,
  nutrient_name: n.nutrient_name,
  amount: n.amount,
  daily_value: n.daily_value
}))

const { error: nutError } = await supabase
  .from('product_nutrition')
  .insert(nutritionData)

if (nutError) {
  if (nutError.message.includes('does not exist')) {
    console.log('⚠️ product_nutrition 테이블이 없습니다.')
    console.log('📝 Supabase SQL Editor에서 아래 SQL을 실행해주세요:\n')
    console.log(`CREATE TABLE product_nutrition (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT REFERENCES products(id),
  source_product_id TEXT,
  nutrient_name TEXT NOT NULL,
  amount TEXT,
  daily_value TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_product_nutrition_pid ON product_nutrition(product_id);`)
  } else {
    console.error('❌ Nutrition 업로드 실패:', nutError.message)
  }
} else {
  console.log('✅ Nutrition 업로드 성공:', nutritionData.length, '건')
}

console.log('\n🎉 완료!')
