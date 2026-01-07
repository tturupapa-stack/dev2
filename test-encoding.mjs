import fs from 'fs'
import iconv from 'iconv-lite'

const encodings = ['utf-8', 'euc-kr', 'cp949', 'utf-16le', 'utf-16be']

console.log('=== products_rows.csv 첫 줄 테스트 ===')
for (const encoding of encodings) {
  try {
    const buffer = fs.readFileSync('products_rows.csv')
    const text = iconv.decode(buffer, encoding)
    const firstLine = text.split('\n')[1] // 헤더 제외
    console.log(`\n${encoding}:`)
    console.log(firstLine.substring(0, 200))
  } catch (e) {
    console.log(`\n${encoding}: ERROR - ${e.message}`)
  }
}
