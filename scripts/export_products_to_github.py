"""
Supabase products 데이터를 GitHub에 업데이트하는 스크립트
"""
import os
import sys
import json
import requests
from datetime import datetime

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 프로젝트 루트를 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Supabase 설정 (secrets.toml에서 읽기)
SUPABASE_URL = "https://bvowxbpqtfpkkxkzsumf.supabase.co"
SUPABASE_KEY = "sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2"

def fetch_products():
    """Supabase에서 products 데이터 가져오기"""
    print("Supabase에서 products 데이터 가져오는 중...")
    url = f"{SUPABASE_URL}/rest/v1/products"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    params = {
        "select": "*",
        "order": "id.asc"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {len(data)}개 제품 데이터 조회 성공")
            return data
        else:
            print(f"✗ 오류: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return None

def save_to_github_repo(products_data):
    """데이터를 GitHub 저장소에 저장"""
    # ica-github 저장소 경로
    github_repo_path = os.path.join(project_root, "ica-github", "dev2-2Hour", "dev2-main")
    
    # data 디렉토리 생성
    data_dir = os.path.join(github_repo_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # JSON 파일로 저장
    json_path = os.path.join(data_dir, "products.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✓ 데이터 저장 완료: {json_path}")
    print(f"  총 {len(products_data)}개 제품")
    
    return json_path

def main():
    print("=" * 60)
    print("Supabase Products 데이터 GitHub 업데이트")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Supabase에서 데이터 가져오기
    products_data = fetch_products()
    
    if not products_data:
        print("✗ 데이터 가져오기 실패")
        return
    
    # 2. GitHub 저장소에 저장
    json_path = save_to_github_repo(products_data)
    
    # 3. 샘플 데이터 출력
    if products_data:
        print("\n--- 샘플 데이터 (최대 3개) ---")
        for i, product in enumerate(products_data[:3]):
            print(f"\n[{i+1}] {product.get('brand', 'N/A')} - {product.get('title', 'N/A')}")
            print(f"    ID: {product.get('id')}")
            print(f"    가격: ${product.get('price', 0)}")
            print(f"    평점: {product.get('rating_avg', 0)} ({product.get('rating_count', 0)}개 리뷰)")
    
    print("\n" + "=" * 60)
    print("완료! 다음 단계:")
    print(f"1. cd {os.path.join(project_root, 'ica-github', 'dev2-2Hour', 'dev2-main')}")
    print("2. git add data/products.json")
    print("3. git commit -m 'chore: Supabase products 데이터 업데이트'")
    print("4. git push origin main")
    print("=" * 60)

if __name__ == "__main__":
    main()
