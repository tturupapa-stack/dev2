# Development Log: Ministry of Food and Drug Safety Health Functional Food Nutrition Database Setup

## Work Overview
Uploaded 4,380 records of Ministry of Food and Drug Safety health functional food nutrition information to Supabase nutrition_info table

## Work Background
- Need nutrition component reference data for health functional food review fact-checking
- Plan to implement product nutrition component verification functionality using official MFDS data

## Main Work Content

### 1. CSV File Analysis
**Files**:
- `products_master.csv`: Column metadata (field descriptions)
- `식품의약품안전처_건강기능식품영양성분정보_20251230.csv`: Actual data (4,380 records)

**Main Columns**:
- Food Basic Information: Food code, food name, manufacturer name, etc.
- Food Classification: Major/medium/minor/detailed classification
- Nutrition Components: Energy, protein, fat, carbohydrates, dietary fiber, etc.
- Vitamins: A, C, D, thiamine, riboflavin, niacin, etc.
- Minerals: Calcium, iron, phosphorus, potassium, sodium, etc.
- Manufacturing/Distribution Information: Manufacturer, importer, country of origin, etc.

### 2. Supabase Table Design
**File**: `database/create_nutrition_info_table.sql`

**Table Name**: `nutrition_info`

**Schema Structure**:
```sql
CREATE TABLE nutrition_info (
  id BIGSERIAL PRIMARY KEY,
  food_code TEXT UNIQUE NOT NULL,  -- Food code (unique identifier)
  food_name TEXT,                   -- Food name

  -- 60+ columns (food classification, nutrition components, vitamins, minerals, etc.)

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Main Features**:
- Set `food_code` as UNIQUE constraint
- Created 5 indexes (food_code, food_name, manufacturer_name, etc.)
- Implemented `updated_at` auto-update trigger
- Use NUMERIC type for accurate nutrition component values

### 3. Data Upload Script Creation
**File**: `upload-nutrition-info.mjs`

**Main Features**:
```javascript
// 1. CSV column name mapping (Korean → English)
const COLUMN_MAPPING = {
  '식품코드': 'food_code',
  '식품명': 'food_name',
  '에너지(kcal)': 'energy_kcal',
  // ... 60 columns
}

// 2. Automatic numeric column parsing
function parseNumeric(value) {
  if (!value || value.trim() === '') return null
  return parseFloat(value)
}

// 3. Batch upload (1000 records at a time)
for (let i = 0; i < data.length; i += 1000) {
  await supabase.from('nutrition_info').upsert(batch)
}
```

### 4. Table Creation Script
**Files**:
- `create-nutrition-table.mjs`: Using Supabase JavaScript SDK (requires RPC)
- `create-table-pg.mjs`: Direct PostgreSQL client connection
- Final: **Direct SQL execution in Supabase web console**

### 5. Documentation Written
**File**: `README-nutrition-setup.md`

Provides table creation and data upload guide

## Troubleshooting

### Issue 1: All Column Values Parsed as null
**Problem**:
```javascript
Sample data: {
  food_code: null,
  food_name: null,
  // All values are null
}
```

**Cause**:
- Column names corrupted when reading CSV file as EUC-KR
- Example: `'식품코드'` → `'癤우떇뭹肄붾뱶'`

**Solution**:
```javascript
// Before
const buffer = fs.readFileSync(csvPath)
const fileContent = iconv.decode(buffer, 'euc-kr')

// After
const fileContent = fs.readFileSync(csvPath, 'utf-8')
const cleanedContent = fileContent.replace(/^\uFEFF/, '') // Remove BOM
```

### Issue 2: BOM (Byte Order Mark) Handling
**Problem**: CSV file first line contains `﻿` (BOM)

**Solution**: Remove BOM with regex
```javascript
const cleanedContent = fileContent.replace(/^\uFEFF/, '')
```

### Issue 3: Cannot Create Table with Supabase SDK
**Problem**: Supabase JavaScript SDK cannot execute DDL (CREATE TABLE)

**Methods Attempted**:
1. `supabase.rpc('exec_sql')` → RPC function does not exist
2. Using PostgreSQL client → Requires DATABASE_URL environment variable

**Final Solution**: Direct execution in Supabase web console SQL Editor

## Upload Results

### Data Statistics
- **Total Records**: 4,380
- **Upload Method**: Batch upload (1000 at a time)
- **Time Taken**: Approximately 20 seconds
- **Success Rate**: 100%

### Sample Data
```javascript
{
  food_code: 'F102-054540000-0037',
  food_name: '힐리 엠에스엠 770',
  manufacturer_name: 'PIONITY HEALTH&BIO EXPERT GROUP',
  energy_kcal: 3,
  protein_g: 0,
  fat_g: 0,
  carbohydrate_g: 0.5,
  sodium_mg: 0,
  origin_country_name: '미국'
}
```

## Technology Stack

### Newly Added Packages
```json
{
  "pg": "^8.x" // PostgreSQL client
}
```

### Technologies Used
- **Node.js + JavaScript**: Upload script
- **csv-parse**: CSV parsing
- **iconv-lite**: Encoding conversion (not used, UTF-8 sufficient)
- **Supabase JavaScript SDK**: Batch upsert
- **PostgreSQL**: Table creation SQL

## File Structure

```
database/
  └── create_nutrition_info_table.sql    # Table creation SQL

upload-nutrition-info.mjs                # Data upload script
create-nutrition-table.mjs               # Supabase SDK table creation attempt
create-table-pg.mjs                      # PostgreSQL client table creation
README-nutrition-setup.md                # Setup guide

식품의약품안전처_건강기능식품영양성분정보_20251230.csv  # Original data
products_master.csv                      # Column metadata
```

## Git Commit History

```
commit 9cd5ee4
feat: Set up Ministry of Food and Drug Safety health functional food nutrition database

- database/create_nutrition_info_table.sql: 60+ column table definition
- upload-nutrition-info.mjs: Batch upload of 4,380 records
- Automatic Korean column name → English mapping
- UTF-8 encoding + BOM removal handling
```

## Usage Plans

### 1. Product Nutrition Component Verification
```javascript
// Query nutrition components by product name
const { data } = await supabase
  .from('nutrition_info')
  .select('*')
  .ilike('food_name', '%lutein%')
```

### 2. Product Search by Manufacturer
```javascript
const { data } = await supabase
  .from('nutrition_info')
  .select('food_name, energy_kcal, protein_g')
  .eq('manufacturer_name', 'California Gold Nutrition')
```

### 3. Nutrition Component Comparative Analysis
```javascript
// High vitamin D content order
const { data } = await supabase
  .from('nutrition_info')
  .select('food_name, vitamin_d_ug')
  .not('vitamin_d_ug', 'is', null)
  .order('vitamin_d_ug', { ascending: false })
  .limit(10)
```

### 4. Review Fact-Check Integration
- Extract product name mentioned in review
- Query product nutrition components from nutrition_info table
- Compare review content with actual nutrition components

## Next Steps

1. **Product Name Matching Logic Implementation**
   - Connect existing products table with nutrition_info
   - Similarity-based product name matching algorithm

2. **Nutrition Component Verification API Development**
   - Product name input → Return nutrition components
   - Compare review content vs actual nutrition components

3. **Streamlit Dashboard Integration**
   - Visualize nutrition component information
   - Add product comparison functionality

4. **Regular Data Updates**
   - Review MFDS API integration
   - Create automatic update script

## Lessons Learned

### 1. CSV Encoding Precautions
- Must check actual file encoding first
- BOM (Byte Order Mark) handling required
- `file -bi` command can guess encoding but not perfect

### 2. Supabase DDL Execution Limitations
- Supabase JS SDK only supports SELECT/INSERT/UPDATE/DELETE
- DDL (CREATE/ALTER/DROP) requires web console or PostgreSQL client

### 3. Large Data Upload
- Batch processing improves performance (1000 at a time)
- upsert + onConflict for duplicate handling
- Progress display improves user experience

### 4. Data Type Selection
- NUMERIC vs FLOAT: Use NUMERIC when precise decimals needed
- TEXT vs VARCHAR: Prefer TEXT when no length limit
- TIMESTAMPTZ: Timezone-inclusive timestamp

## References
- [Supabase SQL Editor](https://supabase.com/docs/guides/database/overview)
- [PostgreSQL NUMERIC Type](https://www.postgresql.org/docs/current/datatype-numeric.html)
- [csv-parse Documentation](https://csv.js.org/parse/)
- [Ministry of Food and Drug Safety Public Data](https://www.data.go.kr/)
