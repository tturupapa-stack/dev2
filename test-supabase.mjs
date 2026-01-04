import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing env:', { supabaseUrl, hasKey: !!supabaseKey })
  process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

const run = async () => {
  const { data, error } = await supabase.from('test_table').select('*')
  if (error) console.error('❌ Supabase error:', error)
  else console.log('✅ Supabase connected:', data)
}

run()
