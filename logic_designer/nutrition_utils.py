"""
영양성분 DB 통합 공통 유틸리티 함수
식품의약품안전처 영양성분 DB를 활용한 검증 및 분석 지원
"""

import re
from typing import Dict, List, Optional, Any
from database.supabase_client import SupabaseClient


def get_nutrition_info_safe(product_id: int) -> Optional[Dict[str, Any]]:
    """
    제품의 영양성분 정보 조회 (안전한 방식)
    
    Args:
        product_id: 제품 ID
        
    Returns:
        Dict: 영양성분 정보 또는 None (오류/정보 없음)
        
    Note:
        - 오류 발생 시 None 반환 (오류 없이)
        - 영양성분 DB가 없어도 기존 기능은 정상 동작
    """
    try:
        client = SupabaseClient()
        supabase = client.get_client()
        
        # nutrition_info 테이블에서 제품 정보 조회
        # 실제 스키마에 맞게 조정 필요
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return {
                'ingredients': response.data,
                'product_id': product_id
            }
        return None  # 정보 없음 (오류 아님)
    except Exception:
        # 모든 예외를 무시하고 None 반환 (오류 없이)
        return None


def extract_ingredients(text: str) -> List[str]:
    """
    리뷰 텍스트에서 성분명 추출
    
    Args:
        text: 리뷰 텍스트
        
    Returns:
        List[str]: 추출된 성분명 리스트
    """
    if not text:
        return []
    
    # 주요 건강기능식품 성분 패턴
    ingredient_patterns = [
        # 비타민류
        r'비타민\s*[A-Z]?\d*',
        r'비타민\s*[A-Z]',
        r'Vitamin\s*[A-Z]?\d*',
        r'Vitamin\s*[A-Z]',
        
        # 카로티노이드
        r'루테인',
        r'제아잔틴',
        r'제아잔틴',
        r'리코펜',
        r'베타카로틴',
        r'Lutein',
        r'Zeaxanthin',
        r'Lycopene',
        r'Beta[-\s]?carotene',
        
        # 오메가
        r'오메가\s*3',
        r'오메가\s*6',
        r'오메가\s*9',
        r'Omega\s*3',
        r'Omega\s*6',
        r'Omega\s*9',
        r'DHA',
        r'EPA',
        
        # 프로바이오틱스
        r'프로바이오틱스',
        r'Probiotic',
        r'락토바실러스',
        r'비피도박테리움',
        r'Lactobacillus',
        r'Bifidobacterium',
        
        # 미네랄
        r'칼슘',
        r'마그네슘',
        r'아연',
        r'셀레늄',
        r'Calcium',
        r'Magnesium',
        r'Zinc',
        r'Selenium',
        
        # 기타
        r'코엔자임\s*Q10',
        r'CoQ10',
        r'글루코사민',
        r'콘드로이틴',
        r'Glucosamine',
        r'Chondroitin',
    ]
    
    extracted = []
    text_lower = text.lower()
    
    for pattern in ingredient_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        extracted.extend(matches)
    
    # 중복 제거 및 정규화
    normalized = []
    seen = set()
    
    for item in extracted:
        normalized_item = item.strip().lower()
        if normalized_item and normalized_item not in seen:
            seen.add(normalized_item)
            normalized.append(item.strip())
    
    return normalized


def normalize_ingredient_name(name: str) -> str:
    """
    성분명 정규화 (비교를 위해)
    
    Args:
        name: 성분명
        
    Returns:
        str: 정규화된 성분명
    """
    if not name:
        return ""
    
    # 소문자 변환
    normalized = name.lower().strip()
    
    # 공백 제거
    normalized = re.sub(r'\s+', '', normalized)
    
    # 하이픈/대시 통일
    normalized = re.sub(r'[-_]+', '', normalized)
    
    return normalized


def is_valid_ingredient(
    mentioned_name: str,
    nutrition_info: Dict[str, Any]
) -> bool:
    """
    언급된 성분이 실제 제품에 포함되어 있는지 확인
    
    Args:
        mentioned_name: 리뷰에서 언급된 성분명
        nutrition_info: 영양성분 정보 딕셔너리
        
    Returns:
        bool: 유효한 성분이면 True
    """
    if not mentioned_name or not nutrition_info:
        return False
    
    mentioned_normalized = normalize_ingredient_name(mentioned_name)
    ingredients = nutrition_info.get('ingredients', [])
    
    if not ingredients:
        return False
    
    for ingredient in ingredients:
        # 실제 스키마에 맞게 조정 필요
        # 현재는 food_name, representative_food_name 등을 확인
        ingredient_name = ingredient.get('food_name', '') or \
                         ingredient.get('representative_food_name', '') or \
                         ingredient.get('ingredient_name', '')
        
        if not ingredient_name:
            continue
        
        official_normalized = normalize_ingredient_name(ingredient_name)
        
        # 정확히 일치하거나 포함 관계 확인
        if mentioned_normalized in official_normalized or \
           official_normalized in mentioned_normalized:
            return True
        
        # 동의어 확인 (ingredient_aliases가 있는 경우)
        aliases = ingredient.get('ingredient_aliases', [])
        if isinstance(aliases, list):
            for alias in aliases:
                alias_normalized = normalize_ingredient_name(str(alias))
                if mentioned_normalized in alias_normalized or \
                   alias_normalized in mentioned_normalized:
                    return True
    
    return False


def get_official_efficacy(
    ingredient_name: str,
    nutrition_info: Dict[str, Any]
) -> List[str]:
    """
    성분의 공식 효능 목록 조회
    
    Args:
        ingredient_name: 성분명
        nutrition_info: 영양성분 정보
        
    Returns:
        List[str]: 공식 효능 목록
    """
    if not ingredient_name or not nutrition_info:
        return []
    
    ingredients = nutrition_info.get('ingredients', [])
    efficacy_list = []
    
    for ingredient in ingredients:
        ingredient_name_db = ingredient.get('ingredient_name', '') or \
                            ingredient.get('food_name', '')
        
        if normalize_ingredient_name(ingredient_name) == \
           normalize_ingredient_name(ingredient_name_db):
            official_efficacy = ingredient.get('official_efficacy', [])
            if isinstance(official_efficacy, list):
                efficacy_list.extend(official_efficacy)
            break
    
    return list(set(efficacy_list))  # 중복 제거


def get_typical_effect_period(
    ingredient_name: str,
    nutrition_info: Dict[str, Any]
) -> Optional[int]:
    """
    성분의 일반적 효과 발현 기간 조회
    
    Args:
        ingredient_name: 성분명
        nutrition_info: 영양성분 정보
        
    Returns:
        int: 효과 발현 기간 (일) 또는 None
    """
    if not ingredient_name or not nutrition_info:
        return None
    
    ingredients = nutrition_info.get('ingredients', [])
    
    for ingredient in ingredients:
        ingredient_name_db = ingredient.get('ingredient_name', '') or \
                            ingredient.get('food_name', '')
        
        if normalize_ingredient_name(ingredient_name) == \
           normalize_ingredient_name(ingredient_name_db):
            period = ingredient.get('typical_effect_period_days')
            if period:
                return int(period)
            break
    
    return None
