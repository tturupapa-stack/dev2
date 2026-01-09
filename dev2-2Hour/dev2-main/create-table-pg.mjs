import 'dotenv/config'
import pg from 'pg'
import fs from 'fs'

const { Client } = pg

async function createTableWithPg() {
  // Supabase 연결 문자열 확인
  const connectionString = process.env.DATABASE_URL || process.env.SUPABASE_DB_URL

  if (!connectionString) {
    console.log('⚠️ DATABASE_URL 환경변수가 설정되지 않았습니다.')
    console.log('\n=== 수동 설정 방법 ===')
    console.log('1. Supabase 대시보드 > Settings > Database')
    console.log('2. Connection string 복사 (URI)')
    console.log('3. .env 파일에 추가:')
    console.log('   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres')
    console.log('\n또는 Supabase 웹 콘솔에서 SQL Editor를 사용하세요:')
    console.log('cat database/create_nutrition_info_table.sql')
    return
  }

  console.log('📋 PostgreSQL 클라이언트로 테이블 생성 중...')

  const client = new Client({
    connectionString,
    ssl: {
      rejectUnauthorized: false
    }
  })

  try {
    await client.connect()
    console.log('✅ 데이터베이스 연결 성공')

    const sqlScript = fs.readFileSync('database/create_nutrition_info_table.sql', 'utf-8')

    console.log('🔨 SQL 실행 중...')
    await client.query(sqlScript)

    console.log('✅ nutrition_info 테이블 생성 완료!')
  } catch (error) {
    console.error('❌ 오류 발생:', error.message)
    throw error
  } finally {
    await client.end()
  }
}

createTableWithPg().catch((e) => {
  console.error('Error:', e.message)
  process.exit(1)
})
