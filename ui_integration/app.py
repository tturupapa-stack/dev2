"""
건기식 리뷰 팩트체크 시스템 - Streamlit UI
루테인 제품 5종 비교 분석
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from mock_data import (
    get_all_products,
    get_all_analysis_results,
    search_products,
    get_analysis_result
)
from visualizations import (
    render_gauge_chart,
    render_trust_badge,
    render_comparison_table,
    render_radar_chart,
    render_review_sentiment_chart,
    render_checklist_visual,
    render_price_comparison_chart
)
from utils import (
    sanitize_user_input,
    validate_score,
    validate_product_data,
    validate_review_data,
    safe_render_html
)


# 페이지 설정
st.set_page_config(
    page_title="건기식 리뷰 팩트체크",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 커스텀 CSS (안전한 방식 - 사용자 입력 없음)
CSS_STYLES = """
<style>
    .main-title {
        font-size: 42px;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 18px;
        color: #6b7280;
        text-align: center;
        margin-bottom: 30px;
    }
    .product-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f2937;
    }
    .review-card {
        background-color: #f9fafb;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 4px;
    }
    .review-card.ad-suspected {
        border-left-color: #ef4444;
        background-color: #fef2f2;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        color: #1f2937;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 8px;
    }
    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 16px;
        border-radius: 4px;
        margin: 20px 0;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 16px;
        border-radius: 4px;
        margin: 20px 0;
    }
</style>
"""
st.markdown(CSS_STYLES, unsafe_allow_html=True)  # CSS는 정적이므로 안전


@st.cache_data
def load_analysis_data() -> Dict[str, Any]:
    """
    분석 데이터 로드 (캐싱 적용)
    
    Returns:
        Dict: 모든 분석 결과
    """
    try:
        return get_all_analysis_results()
    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return {}


def main():
    """메인 앱 함수"""
    try:
        # 헤더 (안전한 방식 - 사용자 입력 없음)
        st.markdown('<div class="main-title">🔍 건기식 리뷰 팩트체크</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">루테인 제품 상위 3종 비교 분석</div>', unsafe_allow_html=True)

        # 사이드바 - 검색 및 필터
        with st.sidebar:
        st.markdown("### 🔎 제품 검색")

        search_query_raw = st.text_input(
            "제품명 또는 브랜드 검색",
            placeholder="예: NOW Foods, Lutein...",
            key="search"
        )
        
        # 사용자 입력 검증 및 이스케이프
        search_query = sanitize_user_input(search_query_raw) if search_query_raw else ""

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

        # 데이터 로드 (캐싱 적용)
        all_analysis = load_analysis_data()
        
        if not all_analysis:
            st.error("데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
            return

        # 검색 처리
    try:
        if search_query:
            filtered_products = search_products(search_query)
            products_data = []
            
            for p in filtered_products:
                product_id = p.get("id")
                if product_id and product_id in all_analysis:
                    products_data.append(all_analysis[product_id])

            if not products_data:
                st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다.")
                return
        else:
                products_data = list(all_analysis.values())
        except Exception as e:
            st.error(f"검색 처리 중 오류 발생: {str(e)}")
            products_data = list(all_analysis.values())

        # 신뢰도 점수 기준 정렬 (내림차순, 안전한 방식)
        try:
            products_data_sorted = sorted(
                products_data,
                key=lambda x: x.get("ai_result", {}).get("trust_score", 0),
                reverse=True
            )
        except Exception as e:
            st.error(f"정렬 중 오류 발생: {str(e)}")
            products_data_sorted = products_data

        # 상위 3개 선별
        top3_products = products_data_sorted[:3]
        # 나머지 제품 (기타 제품용)
        other_products = products_data_sorted[3:]

        # 순위 배지 매핑
        rank_badges = {
            0: "🥇",
            1: "🥈",
            2: "🥉"
        }

        # 섹션 1: 상위 3개 제품 카드 (가로 배치)
        st.markdown('<div class="section-header">📦 제품 개요 (상위 3개)</div>', unsafe_allow_html=True)

        cols = st.columns(3)

    for idx, data in enumerate(top3_products):
        try:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            
            # 데이터 검증
            if not product or not ai_result:
                continue
            
            with cols[idx]:
                # 순위 배지 표시 (안전한 방식)
                rank_badge = rank_badges.get(idx, "")
                st.markdown(
                    f'<div style="text-align: center; font-size: 36px; margin-bottom: 10px;">{rank_badge}</div>',
                    unsafe_allow_html=True
                )

                # 제품 정보 (이스케이프 처리)
                brand = sanitize_user_input(product.get('brand', ''))
                name = sanitize_user_input(product.get('name', ''))
                price = product.get('price', 0)
                
                st.markdown(f"**{brand}**")
                st.markdown(f"<small>{name}</small>", unsafe_allow_html=True)
                
                # 가격 검증
                try:
                    price_val = float(price)
                    st.markdown(f"<span style='color: #3b82f6; font-size: 18px; font-weight: bold;'>${price_val:.2f}</span>", unsafe_allow_html=True)
                except (TypeError, ValueError):
                    st.markdown("<span style='color: #6b7280;'>가격 정보 없음</span>", unsafe_allow_html=True)

                # 신뢰도 게이지
                try:
                    trust_score = validate_score(ai_result.get("trust_score", 50), 0, 100)
                    fig_gauge = render_gauge_chart(trust_score, "신뢰도")
                    st.plotly_chart(fig_gauge, key=f"gauge_{product.get('id', idx)}")
                except Exception as e:
                    st.error(f"차트 생성 실패: {str(e)}")

                # 신뢰도 배지 (안전한 렌더링)
                try:
                    trust_level = ai_result.get("trust_level", "medium")
                    badge_html = safe_render_html(render_trust_badge(trust_level))
                    st.markdown(badge_html, unsafe_allow_html=True)
                except Exception:
                    pass  # 배지 렌더링 실패 시 무시
            except Exception as e:
                st.error(f"제품 정보 표시 중 오류: {str(e)}")
                continue

        # 섹션 2: 비교 테이블 (상위 3개만)
        st.markdown('<div class="section-header">📊 종합 비교표 (상위 3개)</div>', unsafe_allow_html=True)

        comparison_df = render_comparison_table(top3_products)
        st.dataframe(
            comparison_df,
            hide_index=True,
            height=250
        )

        # 섹션 3: 차트 분석 (상위 3개만)
        st.markdown('<div class="section-header">📈 시각화 분석 (상위 3개)</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🕸️ 다차원 비교 (레이더 차트)")
            fig_radar = render_radar_chart(top3_products)
            st.plotly_chart(fig_radar, key="radar_main")

        with col2:
            st.markdown("#### 💰 가격 비교")
            fig_price = render_price_comparison_chart(top3_products)
            st.plotly_chart(fig_price, key="price_main")

        # 섹션 3.5: 기타 제품 (나머지 제품)
        if other_products:
            st.markdown('<div class="section-header">📋 기타 제품</div>', unsafe_allow_html=True)

            with st.expander("기타 제품 보기 (간략 정보)", expanded=False):
                for idx, data in enumerate(other_products):
                    product = data["product"]
                    ai_result = data["ai_result"]

                    col1, col2, col3, col4 = st.columns([3, 2, 1, 2])

                    with col1:
                        st.markdown(f"**{product['brand']}** {product['name']}")

                    with col2:
                        st.markdown(f"신뢰도: **{ai_result['trust_score']:.1f}점**")

                    with col3:
                        st.markdown(render_trust_badge(ai_result["trust_level"]), unsafe_allow_html=True)

                    with col4:
                        st.markdown(f"💰 ${product['price']:.2f}")

                    if idx < len(other_products) - 1:
                        st.markdown("---")

        # 섹션 4: AI 약사 인사이트 (상위 3개만)
        st.markdown('<div class="section-header">💊 AI 약사 인사이트 (상위 3개)</div>', unsafe_allow_html=True)

        for idx, data in enumerate(top3_products):
            product = data["product"]
            ai_result = data["ai_result"]
            checklist = data["checklist_results"]

            # 순위 배지 포함
            rank_badge = rank_badges[idx]
            with st.expander(f"{rank_badge} {product['brand']} {product['name']} - 상세 분석"):

                col_left, col_right = st.columns([2, 1])

                with col_left:
                    st.markdown(f"**📝 요약**")
                    st.info(ai_result["summary"])

                    st.markdown(f"**✅ 효능**")
                    st.markdown(ai_result["efficacy"])

                    st.markdown(f"**⚠️ 부작용**")
                    st.markdown(ai_result["side_effects"])

                    st.markdown(f"**💡 복용 권장사항**")
                    st.markdown(ai_result["recommendations"])

                    st.markdown(f"**🚨 주의사항**")
                    st.warning(ai_result["warnings"])

                with col_right:
                    st.markdown("**🎯 체크리스트 결과**")
                    render_checklist_visual(checklist)

        # 섹션 5: 리뷰 상세 (상위 3개만)
        st.markdown('<div class="section-header">💬 리뷰 상세 보기 (상위 3개)</div>', unsafe_allow_html=True)

        # 제품 선택 (상위 3개만)
        selected_product = st.selectbox(
            "제품 선택",
            options=[f"{d['product']['brand']} {d['product']['name']}" for d in top3_products],
            key="product_select"
        )

        # 선택된 제품의 데이터 찾기
        selected_data = None
        for data in top3_products:
            if f"{data['product']['brand']} {data['product']['name']}" == selected_product:
                selected_data = data
                break

        if selected_data:
            reviews = selected_data["reviews"]

            col_filter1, col_filter2 = st.columns(2)

            with col_filter1:
                highlight_ads = st.checkbox("광고 의심 리뷰 하이라이트", value=True, key="highlight_ads")

            with col_filter2:
                rating_filter = st.multiselect(
                    "평점 필터",
                    options=[1, 2, 3, 4, 5],
                    default=[1, 2, 3, 4, 5],
                    key="rating_filter"
                )

            # 평점 분포 차트
            st.markdown("#### 📊 평점 분포")
            fig_sentiment = render_review_sentiment_chart(reviews)
            st.plotly_chart(fig_sentiment, key="sentiment_main")

            # 리뷰 필터링
            filtered_reviews = [r for r in reviews if r["rating"] in rating_filter]

            st.markdown(f"#### 💬 리뷰 목록 ({len(filtered_reviews)}개)")

            # 리뷰 표시
            for review in filtered_reviews[:20]:  # 최대 20개만 표시
                # 광고 의심 여부 판단
                is_ad_suspected = review["rating"] == 5 and not review["one_month_use"] and len(review["text"]) < 100

                if is_ad_suspected and highlight_ads:
                    card_class = "review-card ad-suspected"
                    badge = '<span style="background-color: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">광고 의심</span>'
                else:
                    card_class = "review-card"
                    badge = ""

                # 평점 별 표시
                stars = "⭐" * review["rating"]

                # 인증 구매 배지
                verified_badge = '<span style="background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 4px;">인증구매</span>' if review["verified"] else ""

                # 재구매 배지
                reorder_badge = '<span style="background-color: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 4px;">재구매</span>' if review["reorder"] else ""

                # 한달 사용 배지
                one_month_badge = '<span style="background-color: #8b5cf6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 4px;">1개월+</span>' if review["one_month_use"] else ""

                # 리뷰 데이터 검증 및 이스케이프
                try:
                    reviewer = sanitize_user_input(review.get('reviewer', '익명'))
                    date = sanitize_user_input(review.get('date', ''))
                    review_text = sanitize_user_input(review.get('text', ''))
                    
                    review_html = f"""
                    <div class="{card_class}">
                        <div style="margin-bottom: 8px;">
                            <strong>{reviewer}</strong>
                            <span style="margin-left: 8px; color: #6b7280;">{date}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            {stars} {badge} {verified_badge} {reorder_badge} {one_month_badge}
                        </div>
                        <div style="color: #1f2937; line-height: 1.6;">
                            {review_text}
                        </div>
                    </div>
                    """
                    
                    # 안전한 HTML 렌더링
                    safe_html = safe_render_html(review_html)
                    st.markdown(safe_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"리뷰 표시 중 오류: {str(e)}")
                    continue

            if len(filtered_reviews) > 20:
                st.info(f"총 {len(filtered_reviews)}개의 리뷰 중 20개만 표시됩니다.")

        # 푸터 (안전한 방식)
        st.markdown("---")
        footer_html = """
        <div style="text-align: center; color: #6b7280; padding: 20px;">
            <p>🔍 건기식 리뷰 팩트체크 시스템 v1.0</p>
            <p style="font-size: 12px;">본 분석은 리뷰 데이터를 기반으로 한 참고 자료입니다. 제품 구매 시 전문가와 상담하세요.</p>
        </div>
        """
        st.markdown(safe_render_html(footer_html), unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"앱 실행 중 오류 발생: {str(e)}")
        st.info("페이지를 새로고침하거나 잠시 후 다시 시도해주세요.")


if __name__ == "__main__":
    main()
