"""
Streamlit 앱 유틸리티 함수
보안 및 입력 검증 관련 함수
"""

import html
from typing import Optional, Dict, Any


def sanitize_html_string(text: str) -> str:
    """
    HTML 특수문자를 이스케이프하는 함수 (XSS 방지)
    
    Args:
        text: 이스케이프할 텍스트
        
    Returns:
        str: 이스케이프된 텍스트
    """
    if not text:
        return ""
    return html.escape(str(text))


def sanitize_user_input(text: Optional[str]) -> str:
    """
    사용자 입력 검증 및 이스케이프
    
    Args:
        text: 사용자 입력 텍스트
        
    Returns:
        str: 검증 및 이스케이프된 텍스트
    """
    if text is None:
        return ""
    
    # 문자열로 변환
    text = str(text)
    
    # HTML 이스케이프
    text = sanitize_html_string(text)
    
    # 길이 제한 (보안을 위해)
    if len(text) > 1000:
        text = text[:1000]
    
    return text


def validate_score(score: Any, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    점수 값 검증
    
    Args:
        score: 검증할 점수
        min_val: 최소값
        max_val: 최대값
        
    Returns:
        float: 검증된 점수
        
    Raises:
        ValueError: 점수가 유효하지 않은 경우
    """
    try:
        score = float(score)
        if score < min_val or score > max_val:
            raise ValueError(f"점수는 {min_val}과 {max_val} 사이여야 합니다.")
        return score
    except (TypeError, ValueError) as e:
        raise ValueError(f"유효하지 않은 점수 값: {score}")


def validate_product_data(product: Dict[str, Any]) -> bool:
    """
    제품 데이터 검증
    
    Args:
        product: 제품 데이터 딕셔너리
        
    Returns:
        bool: 유효하면 True
        
    Raises:
        ValueError: 데이터가 유효하지 않은 경우
    """
    required_fields = ["id", "name", "brand", "price"]
    
    for field in required_fields:
        if field not in product:
            raise ValueError(f"필수 필드 누락: {field}")
    
    # 가격 검증
    try:
        price = float(product["price"])
        if price < 0:
            raise ValueError("가격은 0 이상이어야 합니다.")
    except (TypeError, ValueError):
        raise ValueError(f"유효하지 않은 가격 값: {product['price']}")
    
    return True


def validate_review_data(review: Dict[str, Any]) -> bool:
    """
    리뷰 데이터 검증
    
    Args:
        review: 리뷰 데이터 딕셔너리
        
    Returns:
        bool: 유효하면 True
        
    Raises:
        ValueError: 데이터가 유효하지 않은 경우
    """
    required_fields = ["text", "rating", "reviewer"]
    
    for field in required_fields:
        if field not in review:
            raise ValueError(f"필수 필드 누락: {field}")
    
    # 평점 검증
    rating = review.get("rating")
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValueError(f"평점은 1-5 사이의 정수여야 합니다: {rating}")
    
    # 리뷰 텍스트 검증
    text = review.get("text", "")
    if not isinstance(text, str) or len(text.strip()) < 3:
        raise ValueError("리뷰 텍스트는 최소 3자 이상이어야 합니다.")
    
    return True


def safe_render_html(html_content: str, allow_script: bool = False) -> str:
    """
    안전한 HTML 렌더링 (스크립트 태그 제거)
    
    Args:
        html_content: HTML 내용
        allow_script: 스크립트 허용 여부 (기본값: False, 보안상 권장하지 않음)
        
    Returns:
        str: 안전한 HTML 내용
    """
    if not html_content:
        return ""
    
    # 스크립트 태그 제거 (보안)
    if not allow_script:
        import re
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'on\w+\s*=', '', html_content, flags=re.IGNORECASE)  # 이벤트 핸들러 제거
    
    return html_content
