import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY
)

async function createTable() {
  console.log('📋 Supabase에 nutrition_info 테이블 생성 중...')

  const sqlScript = fs.readFileSync('database/create_nutrition_info_table.sql', 'utf-8')

  // SQL을 문장 단위로 분리 (세미콜론 기준)
  const statements = sqlScript
    .split(';')
    .map((s) => s.trim())
    .filter((s) => s.length > 0 && !s.startsWith('--'))

  console.log(`📝 ${statements.length}개의 SQL 문장 실행 예정`)

  for (let i = 0; i < statements.length; i++) {
    const statement = statements[i]
    console.log(`\n[${i + 1}/${statements.length}] 실행 중...`)
    console.log(statement.substring(0, 100) + '...')

    try {
      const { data, error } = await supabase.rpc('exec_sql', {
        sql_query: statement
      })

      if (error) {
        // RPC가 없는 경우 직접 실행 시도
        if (error.message.includes('exec_sql')) {
          console.log('⚠️ RPC 함수가 없습니다. Supabase 웹 콘솔에서 SQL을 직접 실행해주세요:')
          console.log('\n=== SQL 스크립트 ===')
          console.log(sqlScript)
          console.log('\n=== 실행 방법 ===')
          console.log('1. Supabase 대시보드 접속')
          console.log('2. SQL Editor 메뉴 클릭')
          console.log('3. 위 SQL 스크립트 복사 & 붙여넣기')
          console.log('4. Run 버튼 클릭')
          console.log('\n또는 아래 명령어로 SQL 파일 확인:')
          console.log('cat database/create_nutrition_info_table.sql')
          return
        }
        throw error
      }

      console.log(`✅ 완료`)
    } catch (err) {
      console.error(`❌ 오류 발생:`, err.message)
      throw err
    }
  }

  console.log('\n✅ 테이블 생성 완료!')
}

createTable().catch((e) => {
  console.error('❌ Error:', e?.message || e)
  process.exit(1)
})
