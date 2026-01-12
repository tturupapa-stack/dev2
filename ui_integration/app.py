"""
건기식 리뷰 팩트체크 시스템 - Streamlit UI
모든 데이터를 활용한 종합 분석 대시보드
"""

import streamlit as st
import pandas as pd
import os
from typing import Dict, List, Optional

# 페이지 설정을 먼저 실행 (Streamlit 초기화)
st.set_page_config(
    page_title="건기식 리뷰 팩트체크",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이후 모듈 import (같은 디렉토리에서 직접 import)
try:
    from supabase_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    import traceback
    print(f"[ERROR] Supabase import failed: {e}")
    print(traceback.format_exc())
    from mock_data import get_all_analysis_results, get_all_products, search_products
    USE_SUPABASE = False

try:
    from visualizations import (
        render_gauge_chart,
        render_trust_badge,
        render_comparison_table,
        render_radar_chart,
        render_review_sentiment_chart,
        render_checklist_visual,
        render_price_comparison_chart
    )
except ImportError as e:
    import traceback
    st.error(f"Visualizations import failed: {e}")
    print(f"[ERROR] Visualizations import failed: {e}")
    print(traceback.format_exc())
    raise

# 커스텀 CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #3b82f6;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .review-card {
        background: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .ad-suspected {
        border-left-color: #ef4444;
        background: #fef2f2;
    }
    .verified-review {
        border-left-color: #22c55e;
    }
</style>
""", unsafe_allow_html=True)


def render_checklist_details(checklist_results: Dict) -> None:
    """체크리스트 상세 정보 표시"""
    checklist_items = {
        "1_verified_purchase": "인증 구매 비율",
        "2_reorder_rate": "재구매율",
        "3_long_term_use": "장기 사용 비율",
        "4_rating_distribution": "평점 분포 적절성",
        "5_review_length": "리뷰 길이",
        "6_time_distribution": "시간 분포 자연성",
        "7_ad_detection": "광고성 리뷰 탐지",
        "8_reviewer_diversity": "리뷰어 다양성"
    }
    
    for key, label in checklist_items.items():
        if key in checklist_results:
            result = checklist_results[key]
            status = "✅" if result.get("passed", False) else "❌"
            rate = result.get("rate", 0) * 100
            desc = result.get("description", "")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{status} {label}**")
                st.progress(rate / 100)
            with col2:
                st.caption(f"{desc} ({rate:.1f}%)")


def render_rating_analysis(reviews: List[Dict], product_rating_avg: Optional[float] = None) -> None:
    """평점 분석 섹션"""
    if not reviews:
        st.warning("리뷰 데이터가 없습니다.")
        return
    
    # 평점 분포 계산
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating = review.get("rating", 5)
        if rating in rating_counts:
            rating_counts[rating] += 1
    
    total_reviews = len(reviews)
    avg_rating = sum(r.get("rating", 5) for r in reviews) / total_reviews if total_reviews > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("평균 평점", f"{avg_rating:.2f}", f"{avg_rating - 3.0:.2f}")
    with col2:
        st.metric("총 리뷰 수", f"{total_reviews}개")
    with col3:
        if product_rating_avg:
            diff = avg_rating - product_rating_avg
            st.metric("제품 평균과 차이", f"{diff:+.2f}")
    
    # 평점 분포 차트
    import plotly.graph_objects as go
    fig = go.Figure(data=[
        go.Bar(
            x=list(rating_counts.keys()),
            y=list(rating_counts.values()),
            marker_color=['#ef4444', '#f59e0b', '#eab308', '#84cc16', '#22c55e'],
            text=[f"{count}개" for count in rating_counts.values()],
            textposition='auto'
        )
    ])
    fig.update_layout(
        title="평점 분포",
        xaxis_title="평점",
        yaxis_title="리뷰 수",
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_individual_review_analysis(reviews: List[Dict]) -> None:
    """개별 리뷰 분석 표시"""
    st.markdown("#### 📝 개별 리뷰 상세 분석")
    
    # 필터 옵션
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        rating_filter = st.multiselect(
            "평점 필터",
            options=[1, 2, 3, 4, 5],
            default=[1, 2, 3, 4, 5],
            key="rating_filter"
        )
    with col_f2:
        highlight_ads = st.checkbox("광고 의심 리뷰 하이라이트", value=True, key="highlight_ads")
    with col_f3:
        show_verified_only = st.checkbox("인증 구매만 보기", value=False, key="verified_only")
    
    # 리뷰 필터링
    filtered_reviews = [
        r for r in reviews
        if r.get("rating") in rating_filter
        and (not show_verified_only or r.get("verified", False))
    ]
    
    if not filtered_reviews:
        st.info("필터 조건에 맞는 리뷰가 없습니다.")
        return
    
    st.markdown(f"**총 {len(filtered_reviews)}개의 리뷰**")
    
    # 리뷰 카드 표시
    for idx, review in enumerate(filtered_reviews[:20]):  # 최대 20개만 표시
        rating = review.get("rating", 5)
        text = review.get("text", "")
        date = review.get("date", "")
        reviewer = review.get("reviewer", "익명")
        verified = review.get("verified", False)
        reorder = review.get("reorder", False)
        one_month = review.get("one_month_use", False)
        
        # 광고 의심 여부 (간단한 휴리스틱)
        is_ad_suspected = (
            rating == 5 and 
            not one_month and 
            len(text) < 100 and
            ("최고" in text or "대박" in text or "강력 추천" in text)
        )
        
        card_class = "review-card"
        if is_ad_suspected and highlight_ads:
            card_class += " ad-suspected"
        elif verified:
            card_class += " verified-review"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            # 평점 표시
            stars = "⭐" * rating + "☆" * (5 - rating)
            st.markdown(f"**{stars} ({rating}/5)** | {reviewer} | {date}")
            
            # 배지
            badge_html = ""
            if verified:
                badge_html += '<span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;">✓ 인증구매</span>'
            if reorder:
                badge_html += '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;">🔄 재구매</span>'
            if one_month:
                badge_html += '<span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;">📅 1개월+</span>'
            if is_ad_suspected:
                badge_html += '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">⚠️ 광고 의심</span>'
            
            if badge_html:
                st.markdown(badge_html, unsafe_allow_html=True)
            
            # 리뷰 텍스트
            st.markdown(f"<p style='margin-top: 0.5rem;'>{text}</p>", unsafe_allow_html=True)
        
        with col_r2:
            # 통계 정보
            st.caption(f"길이: {len(text)}자")
            if is_ad_suspected:
                st.error("광고 의심")
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    """메인 앱 함수"""
    st.markdown('<div class="main-title">🔍 건기식 리뷰 팩트체크 시스템</div>', unsafe_allow_html=True)
    
    # 데이터 로드
    try:
        all_data = get_all_analysis_results()
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        st.info("목업 데이터로 전환합니다.")
        from mock_data import get_all_analysis_results as get_mock_data
        all_data = get_mock_data()
    
    if not all_data:
        st.error("데이터를 불러올 수 없습니다.")
        return
    
    product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}
    
    # ========== 사이드바: 탭 구조 ==========
    with st.sidebar:
        # Supabase 연결 상태
        if USE_SUPABASE:
            st.success("✅ Supabase 연동 활성화")
        else:
            st.warning("⚠️ 목업 데이터 사용 중")
        
        # 사이드바 탭
        sidebar_tab1, sidebar_tab2, sidebar_tab3 = st.tabs(["🔍 기본 설정", "⚙️ 고급 필터", "📊 통계 보기"])
        
        # 탭 1: 기본 설정
        with sidebar_tab1:
            st.header("⚙️ 분석 설정")
            selected_labels = st.multiselect(
                "분석할 제품을 선택하세요",
                options=list(product_options.keys()),
                default=list(product_options.keys())[:3],
                key="product_select"
            )
            
            st.markdown("---")
            st.markdown("### ℹ️ 신뢰도 등급 안내")
            st.markdown("""
            - **HIGH (70점 이상)**: 신뢰할 수 있는 제품
            - **MEDIUM (50-70점)**: 보통 수준
            - **LOW (50점 미만)**: 주의 필요
            """)
            
            st.markdown("---")
            st.markdown("### 📊 분석 기준")
            st.markdown("""
            1. 인증 구매 비율
            2. 재구매율
            3. 장기 사용 비율
            4. 평점 분포 적절성
            5. 리뷰 길이
            6. 시간 분포 자연성
            7. 광고성 리뷰 탐지
            8. 리뷰어 다양성
            """)
        
        # 탭 2: 고급 필터
        with sidebar_tab2:
            st.header("🔎 고급 필터")
            
            # 신뢰도 필터
            trust_filter = st.multiselect(
                "신뢰도 등급",
                options=["HIGH", "MEDIUM", "LOW"],
                default=["HIGH", "MEDIUM", "LOW"],
                key="trust_filter"
            )
            
            # 가격 범위 필터
            all_products_list = get_all_products()
            if all_products_list:
                prices = [p.get("price", 0) for p in all_products_list if p.get("price")]
                if prices:
                    min_price = min(prices)
                    max_price = max(prices)
                    price_range = st.slider(
                        "가격 범위 ($)",
                        min_value=float(min_price),
                        max_value=float(max_price),
                        value=(float(min_price), float(max_price)),
                        key="price_range"
                    )
            
            # 브랜드 필터
            brands = sorted(list(set(p.get("brand", "") for p in all_products_list if p.get("brand"))))
            if brands:
                brand_filter = st.multiselect(
                    "브랜드 선택",
                    options=brands,
                    default=brands,
                    key="brand_filter"
                )
            
            # 검색 기능
            search_query = st.text_input(
                "제품명 또는 브랜드 검색",
                placeholder="예: NOW Foods, Lutein...",
                key="search_query"
            )
        
        # 탭 3: 통계 보기
        with sidebar_tab3:
            st.header("📊 전체 통계")
            
            # 전체 제품 통계
            total_products = len(all_data)
            total_reviews = sum(len(data.get("reviews", [])) for data in all_data.values())
            avg_trust = sum(data.get("ai_result", {}).get("trust_score", 0) for data in all_data.values()) / total_products if total_products > 0 else 0
            
            st.metric("전체 제품 수", f"{total_products}개")
            st.metric("전체 리뷰 수", f"{total_reviews}개")
            st.metric("평균 신뢰도", f"{avg_trust:.1f}점")
            
            # 신뢰도 등급 분포
            trust_levels = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for data in all_data.values():
                level = data.get("ai_result", {}).get("trust_level", "medium").upper()
                if level == "HIGH":
                    trust_levels["HIGH"] += 1
                elif level == "MEDIUM":
                    trust_levels["MEDIUM"] += 1
                else:
                    trust_levels["LOW"] += 1
            
            st.markdown("### 신뢰도 등급 분포")
            for level, count in trust_levels.items():
                st.progress(count / total_products if total_products > 0 else 0, text=f"{level}: {count}개")
    
    # 제품 선택 검증
    if not selected_labels:
        st.warning("분석할 제품을 하나 이상 선택해주세요.")
        return
    
    # 필터링 적용
    selected_data = [all_data[product_options[label]] for label in selected_labels]
    
    # 신뢰도 필터 적용
    if trust_filter:
        selected_data = [
            d for d in selected_data
            if d.get("ai_result", {}).get("trust_level", "").upper() in [f.upper() for f in trust_filter]
        ]
    
    # 가격 필터 적용
    if 'price_range' in locals():
        selected_data = [
            d for d in selected_data
            if price_range[0] <= d.get("product", {}).get("price", 0) <= price_range[1]
        ]
    
    # 브랜드 필터 적용
    if 'brand_filter' in locals() and brand_filter:
        selected_data = [
            d for d in selected_data
            if d.get("product", {}).get("brand", "") in brand_filter
        ]
    
    # 검색 필터 적용
    if search_query:
        search_results = search_products(search_query)
        search_ids = [p.get("id") for p in search_results]
        selected_data = [
            d for d in selected_data
            if d.get("product", {}).get("id") in search_ids
        ]
    
    if not selected_data:
        st.warning("필터 조건에 맞는 제품이 없습니다.")
        return
    
    # ========== 메인 영역: 탭 구성 ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 종합 비교 분석",
        "💊 AI 제품별 정밀 진단",
        "💬 리뷰 딥다이브",
        "📈 상세 통계 분석"
    ])
    
    # 탭 1: 종합 비교 분석
    with tab1:
        st.markdown('<div class="section-header">📊 모든 제품 한눈에 비교</div>', unsafe_allow_html=True)
        
        # 레이더 차트와 가격 비교를 더 크게 표시
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("#### 🕸️ 다차원 비교 (레이더 차트)")
            fig_radar = render_radar_chart(selected_data)
            st.plotly_chart(fig_radar, use_container_width=True, height=600)
        
        with col2:
            st.markdown("#### 💰 가격 및 신뢰도 요약")
            fig_price = render_price_comparison_chart(selected_data)
            st.plotly_chart(fig_price, use_container_width=True, height=400)
            
            # 신뢰도 요약 카드
            st.markdown("#### 📊 신뢰도 요약")
            for data in selected_data:
                product = data.get("product", {})
                ai_result = data.get("ai_result", {})
                trust_score = ai_result.get("trust_score", 0)
                trust_level = ai_result.get("trust_level", "medium")
                
                col_card1, col_card2 = st.columns([2, 1])
                with col_card1:
                    st.markdown(f"**{product.get('brand', '')}**")
                with col_card2:
                    st.markdown(render_trust_badge(trust_level), unsafe_allow_html=True)
                st.progress(trust_score / 100, text=f"{trust_score:.1f}점")
        
        st.markdown("#### 📋 세부 지표 비교표")
        comparison_df = render_comparison_table(selected_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=400)
    
    # 탭 2: AI 제품별 정밀 진단
    with tab2:
        st.markdown('<div class="section-header">💊 제품별 심층 데이터 분석</div>', unsafe_allow_html=True)
        
        for data in selected_data:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            checklist = data.get("checklist_results", {})
            
            with st.expander(
                f"📌 {product.get('brand', '')} - {product.get('name', '')} 상세 보기",
                expanded=True
            ):
                # 상단: 신뢰도 게이지와 체크리스트
                col_top1, col_top2, col_top3 = st.columns([1, 1, 1.5])
                
                with col_top1:
                    st.markdown("#### 🎯 신뢰도 점수")
                    fig_gauge = render_gauge_chart(ai_result.get("trust_score", 0), "신뢰도")
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    st.markdown(render_trust_badge(ai_result.get("trust_level", "medium")), unsafe_allow_html=True)
                
                with col_top2:
                    st.markdown("#### ✅ 8단계 체크리스트")
                    render_checklist_visual(checklist)
                
                with col_top3:
                    st.markdown("#### 💡 AI 약사 인사이트")
                    st.info(f"**요약**: {ai_result.get('summary', '정보 없음')}")
                    st.success(f"**효능**: {ai_result.get('efficacy', '정보 없음')}")
                    st.warning(f"**부작용**: {ai_result.get('side_effects', '정보 없음')}")
                    st.info(f"**권장사항**: {ai_result.get('recommendations', '정보 없음')}")
                    st.error(f"**주의사항**: {ai_result.get('warnings', '정보 없음')}")
                
                # 체크리스트 상세
                st.markdown("---")
                st.markdown("#### 📋 체크리스트 상세 분석")
                render_checklist_details(checklist)
                
                # 제품 정보
                st.markdown("---")
                st.markdown("#### 📦 제품 정보")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"**브랜드**: {product.get('brand', '')}")
                    st.markdown(f"**제품명**: {product.get('name', '')}")
                    st.markdown(f"**가격**: ${product.get('price', 0):.2f}")
                with col_info2:
                    st.markdown(f"**용량**: {product.get('serving_size', '')}")
                    st.markdown(f"**총 용량**: {product.get('servings_per_container', '')}정")
                    if product.get('product_url'):
                        st.markdown(f"[제품 링크]({product.get('product_url')})")
    
    # 탭 3: 리뷰 딥다이브
    with tab3:
        st.markdown('<div class="section-header">💬 실제 사용자 리뷰 팩트체크</div>', unsafe_allow_html=True)
        
        # 제품 선택
        target_label = st.selectbox(
            "리뷰를 확인할 제품 선택",
            options=selected_labels,
            key="review_product_select"
        )
        target_data = next(
            d for d in selected_data
            if f"{d['product']['brand']} {d['product']['name']}" == target_label
        )
        
        reviews = target_data.get("reviews", [])
        product = target_data.get("product", {})
        
        if not reviews:
            st.warning("이 제품에 대한 리뷰가 없습니다.")
        else:
            # 평점 분석
            st.markdown("#### 📊 평점 분석")
            product_rating_avg = product.get("rating_avg")
            render_rating_analysis(reviews, product_rating_avg)
            
            # 리뷰 감정 분석 차트
            st.markdown("---")
            col_s1, col_s2 = st.columns([1, 1])
            with col_s1:
                st.markdown("#### 📈 리뷰 감정 분석")
                fig_sentiment = render_review_sentiment_chart(reviews)
                st.plotly_chart(fig_sentiment, use_container_width=True, height=400)
            
            with col_s2:
                st.markdown("#### 📋 리뷰 통계")
                total_reviews = len(reviews)
                verified_count = sum(1 for r in reviews if r.get("verified", False))
                reorder_count = sum(1 for r in reviews if r.get("reorder", False))
                one_month_count = sum(1 for r in reviews if r.get("one_month_use", False))
                
                st.metric("총 리뷰 수", f"{total_reviews}개")
                st.metric("인증 구매", f"{verified_count}개 ({verified_count/total_reviews*100:.1f}%)")
                st.metric("재구매", f"{reorder_count}개 ({reorder_count/total_reviews*100:.1f}%)")
                st.metric("1개월+ 사용", f"{one_month_count}개 ({one_month_count/total_reviews*100:.1f}%)")
            
            # 개별 리뷰 분석
            st.markdown("---")
            render_individual_review_analysis(reviews)
    
    # 탭 4: 상세 통계 분석
    with tab4:
        st.markdown('<div class="section-header">📈 상세 통계 분석</div>', unsafe_allow_html=True)
        
        # 전체 통계 요약
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        total_products = len(selected_data)
        total_reviews_all = sum(len(d.get("reviews", [])) for d in selected_data)
        avg_trust_all = sum(d.get("ai_result", {}).get("trust_score", 0) for d in selected_data) / total_products if total_products > 0 else 0
        avg_price = sum(d.get("product", {}).get("price", 0) for d in selected_data) / total_products if total_products > 0 else 0
        
        with col_stat1:
            st.metric("선택된 제품 수", f"{total_products}개")
        with col_stat2:
            st.metric("총 리뷰 수", f"{total_reviews_all}개")
        with col_stat3:
            st.metric("평균 신뢰도", f"{avg_trust_all:.1f}점")
        with col_stat4:
            st.metric("평균 가격", f"${avg_price:.2f}")
        
        # 제품별 상세 통계 테이블
        st.markdown("#### 📊 제품별 상세 통계")
        stats_data = []
        for data in selected_data:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            reviews = data.get("reviews", [])
            checklist = data.get("checklist_results", {})
            
            stats_data.append({
                "제품명": f"{product.get('brand', '')} {product.get('name', '')}",
                "가격 ($)": product.get("price", 0),
                "신뢰도 점수": ai_result.get("trust_score", 0),
                "신뢰도 등급": ai_result.get("trust_level", "").upper(),
                "리뷰 수": len(reviews),
                "평균 평점": sum(r.get("rating", 5) for r in reviews) / len(reviews) if reviews else 0,
                "인증 구매 비율": checklist.get("1_verified_purchase", {}).get("rate", 0) * 100,
                "재구매율": checklist.get("2_reorder_rate", {}).get("rate", 0) * 100,
                "장기 사용 비율": checklist.get("3_long_term_use", {}).get("rate", 0) * 100,
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
