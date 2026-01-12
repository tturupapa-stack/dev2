"""
Supabase 데이터 추출 스크립트 (REST API 사용)
products와 reviews 테이블 데이터를 CSV/JSON으로 내보내기
"""
import os
import json
import csv
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

print(f"Connecting to Supabase: {SUPABASE_URL}")

# 출력 디렉토리
OUTPUT_DIR = "ica-github/dev2-2Hour/dev2-main/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_table(table_name):
    """REST API로 테이블 데이터 조회"""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    params = {
        "select": "*"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return None

def export_table(table_name):
    """테이블 데이터 내보내기"""
    print(f"\n=== {table_name} 테이블 데이터 추출 ===")

    try:
        data = fetch_table(table_name)

        if data is None:
            print(f"[FAIL] Table query failed")
            return []

        print(f"총 {len(data)}개 레코드 조회됨")

        if data:
            # JSON 저장
            json_path = os.path.join(OUTPUT_DIR, f"{table_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"[OK] JSON saved: {json_path}")

            # CSV 저장
            csv_path = os.path.join(OUTPUT_DIR, f"{table_name}.csv")
            flat_data = []
            for row in data:
                flat_row = {}
                for k, v in row.items():
                    if isinstance(v, (dict, list)):
                        flat_row[k] = json.dumps(v, ensure_ascii=False)
                    else:
                        flat_row[k] = v
                flat_data.append(flat_row)

            if flat_data:
                keys = flat_data[0].keys()
                with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(flat_data)
                print(f"[OK] CSV saved: {csv_path}")

            # 샘플 출력
            print("\n--- 샘플 데이터 ---")
            for row in data[:2]:
                sample = {k: str(v)[:50] + "..." if len(str(v)) > 50 else v for k, v in list(row.items())[:3]}
                print(f"  - {sample}")

        return data
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return []

def check_tables():
    """사용 가능한 테이블 확인"""
    print("\n=== 테이블 확인 ===")

    tables = ["products", "reviews", "nutrition_info", "checklist_results", "analysis_results"]
    available = []

    for table in tables:
        data = fetch_table(table)
        if data is not None:
            print(f"✓ {table}: {len(data)} 레코드")
            if len(data) > 0:
                available.append(table)
        else:
            print(f"✗ {table}: 접근 불가")

    return available

def main():
    print("=" * 50)
    print("Supabase 데이터 추출 시작")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 사용 가능한 테이블 확인
    available_tables = check_tables()

    # 데이터 추출
    all_data = {}
    for table in available_tables:
        all_data[table] = export_table(table)

    # 요약
    print("\n" + "=" * 50)
    print("추출 완료 요약")
    print("=" * 50)
    for table, data in all_data.items():
        print(f"{table}: {len(data)}개")
    print(f"저장 위치: {OUTPUT_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()
