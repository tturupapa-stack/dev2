import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'

const supabaseUrl = 'https://bvowxbpqtfpkkxkzsumf.supabase.co'
const supabaseKey = process.env.SUPABASE_KEY || 'sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2'
const supabase = createClient(supabaseUrl, supabaseKey)

// 출력 디렉토리
const OUTPUT_DIR = './data'
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true })
}

async function exportTable(tableName) {
    console.log(`\n=== ${tableName} 테이블 데이터 추출 ===`)

    try {
        const { data, error } = await supabase
            .from(tableName)
            .select('*')

        if (error) {
            console.log(`[FAIL] Error: ${error.message}`)
            return []
        }

        console.log(`Total ${data.length} records found`)

        if (data && data.length > 0) {
            // JSON 저장
            const jsonPath = path.join(OUTPUT_DIR, `${tableName}.json`)
            fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2), 'utf-8')
            console.log(`[OK] JSON saved: ${jsonPath}`)

            // CSV 저장
            const csvPath = path.join(OUTPUT_DIR, `${tableName}.csv`)
            const headers = Object.keys(data[0])
            const csvContent = [
                headers.join(','),
                ...data.map(row => headers.map(h => {
                    const val = row[h]
                    if (val === null || val === undefined) return ''
                    if (typeof val === 'object') return `"${JSON.stringify(val).replace(/"/g, '""')}"`
                    if (typeof val === 'string' && (val.includes(',') || val.includes('"') || val.includes('\n'))) {
                        return `"${val.replace(/"/g, '""')}"`
                    }
                    return val
                }).join(','))
            ].join('\n')
            fs.writeFileSync(csvPath, '\ufeff' + csvContent, 'utf-8')
            console.log(`[OK] CSV saved: ${csvPath}`)

            // 샘플 출력
            console.log(`\n--- Sample Data ---`)
            data.slice(0, 2).forEach((row, i) => {
                const sample = Object.entries(row).slice(0, 3).map(([k, v]) => {
                    const str = String(v)
                    return `${k}: ${str.length > 30 ? str.slice(0, 30) + '...' : str}`
                }).join(', ')
                console.log(`  ${i + 1}. ${sample}`)
            })
        }

        return data
    } catch (e) {
        console.log(`[ERROR] ${e.message}`)
        return []
    }
}

async function checkTables() {
    console.log('\n=== 테이블 확인 ===')

    const tables = ['products', 'reviews', 'nutrition_info', 'checklist_results', 'analysis_results']
    const available = []

    for (const table of tables) {
        try {
            const { data, error } = await supabase
                .from(table)
                .select('*')
                .limit(1)

            if (!error && data) {
                console.log(`[OK] ${table}: accessible`)
                available.push(table)
            } else {
                console.log(`[FAIL] ${table}: ${error?.message || 'no data'}`)
            }
        } catch (e) {
            console.log(`[FAIL] ${table}: ${e.message}`)
        }
    }

    return available
}

async function main() {
    console.log('='.repeat(50))
    console.log('Supabase Data Export')
    console.log(`Time: ${new Date().toLocaleString('ko-KR')}`)
    console.log('='.repeat(50))

    // 테이블 확인
    const availableTables = await checkTables()

    // 데이터 추출
    const allData = {}
    for (const table of availableTables) {
        allData[table] = await exportTable(table)
    }

    // 요약
    console.log('\n' + '='.repeat(50))
    console.log('Export Summary')
    console.log('='.repeat(50))
    for (const [table, data] of Object.entries(allData)) {
        console.log(`${table}: ${data.length} records`)
    }
    console.log(`Output: ${path.resolve(OUTPUT_DIR)}`)
    console.log('='.repeat(50))
}

main().catch(console.error)
