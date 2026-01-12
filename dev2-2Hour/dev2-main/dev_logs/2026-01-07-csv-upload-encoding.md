# Development Log: CSV Data Upload and Korean Encoding Handling

## Work Overview
Implementation of functionality to upload iHerb product and review data from CSV files to Supabase DB

## Main Work Content

### 1. CSV Data Upload Script Creation
- **Purpose**: Upload products_rows.csv and reviews_rows.csv to Supabase
- **Implementation File**: `upload-products-csv.mjs`
- **Features**:
  - CSV file parsing and upsert to Supabase tables
  - Product ID mapping: Automatic conversion of CSV's source_product_id to actual DB id
  - Automatic duplicate review removal
  - Unique ID generation: `{source_product_id}-{review_id}` format

### 2. Korean Encoding Issue Resolution
#### Problem
- CSV file read as UTF-8 and uploaded to Supabase, but Korean characters were corrupted
- Example: "루테인" → ""

#### Cause Analysis
```bash
file -bi products_rows.csv
# Result: text/csv; charset=iso-8859-1
```
- CSV file was saved in **EUC-KR/CP949** encoding
- Node.js default file reading assumes UTF-8

#### Solution
1. **Encoding Test Script Creation** (`test-encoding.mjs`)
   - Tested reading file with multiple encodings (utf-8, euc-kr, cp949, utf-16le, utf-16be)
   - Confirmed EUC-KR/CP949 is the correct encoding

2. **iconv-lite Package Addition**
   ```bash
   npm install iconv-lite
   ```

3. **Upload Script Modification**
   ```javascript
   // Before
   const fileContent = fs.readFileSync(csvPath, 'utf-8')

   // After
   const buffer = fs.readFileSync(csvPath)
   const fileContent = iconv.decode(buffer, 'euc-kr')
   ```

### 3. Python Backup Uploader Creation
- **File**: `data_manager/db_uploader.py`
- **Purpose**: Backup script to enable CSV upload in Python environment
- **Status**: Completed (available for future use)

## Upload Results

### Products Table
- **Total 5 products uploaded successfully**
  1. California Gold Nutrition - Lutein (iHerb)
  2. Doctor's Best - Lutemax 2020
  3. Solaray - L-Lysine Monolaurin
  4. Natural Factors - Lutein with Zeaxanthin
  5. Sports Research - Lutein + Zeaxanthin

### Reviews Table
- **Total 50 reviews uploaded successfully**
- 10 duplicate reviews automatically removed

## Technology Stack & Dependencies Added

### Newly Added Packages
```json
{
  "csv-parse": "^6.1.0",     // CSV parsing
  "iconv-lite": "^0.7.1"      // Encoding conversion
}
```

### Technologies Used
- **JavaScript/Node.js**: Main upload script
- **Supabase JavaScript Client**: DB connection
- **iconv-lite**: EUC-KR → UTF-8 conversion
- **csv-parse**: CSV file parsing

## File Structure

```
data_manager/
  └── db_uploader.py           # Python-based uploader (backup)

upload-products-csv.mjs        # Main CSV upload script
test-encoding.mjs              # Encoding test utility
products_rows.csv              # Product data (5 items)
reviews_rows.csv               # Review data (60 items)
```

## Git Commit History

```
commit dc13561
feat: Add CSV data upload tool - Korean handling with EUC-KR encoding support

- Added products_rows.csv, reviews_rows.csv
- upload-products-csv.mjs: Supabase upload script
- data_manager/db_uploader.py: Python uploader
- test-encoding.mjs: Encoding test utility
- Added iconv-lite, csv-parse dependencies
```

## Troubleshooting

### Issue 1: product_id null Error
**Problem**: `product_id` null constraint violation when uploading to reviews table
```
null value in column "product_id" violates not-null constraint
```

**Cause**: CSV's `product_id` column contained source_product_id (string)

**Solution**:
1. Query source_product_id → id mapping from products table
2. Create mapping table for automatic conversion

### Issue 2: Duplicate Review Error
**Problem**: `ON CONFLICT DO UPDATE command cannot affect row a second time`

**Cause**: CSV had duplicate source_review_id across multiple products (1, 2, 3...)

**Solution**:
1. Generate unique ID: `{source_product_id}-{review_id}`
2. Add automatic duplicate removal logic

### Issue 3: Korean Character Corruption
**Problem**: All Korean characters stored in Supabase were corrupted

**Cause**: CSV file was EUC-KR encoding but read as UTF-8

**Solution**: Use iconv-lite to convert EUC-KR → UTF-8 before upload

## Next Steps

1. Query and display uploaded data in Streamlit app
2. Apply fact-check logic to actual DB data
3. Add functionality to save AI analysis results to reviews table

## Lessons Learned

1. **Importance of Encoding**:
   - Must check file encoding when handling Korean data
   - Can check file encoding with `file -bi` command
   - Windows environment may default to EUC-KR/CP949

2. **CSV Data Preprocessing**:
   - Need automatic duplicate removal logic
   - Use mapping table for data with foreign key relationships

3. **Supabase upsert**:
   - Use `onConflict` option for duplicate handling
   - Must check constraints (NOT NULL, UNIQUE, etc.)

## References
- [iconv-lite Documentation](https://www.npmjs.com/package/iconv-lite)
- [csv-parse Documentation](https://www.npmjs.com/package/csv-parse)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
