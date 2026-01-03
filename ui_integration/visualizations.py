"""
건기식 리뷰 팩트체크 시스템 - 시각화 컴포넌트
Plotly 기반 인터랙티브 차트
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st


def render_gauge_chart(score, title="신뢰도"):
    """
    신뢰도 게이지 차트 렌더링

    Args:
        score (float): 0-100 사이의 점수
        title (str): 차트 제목

    Returns:
        plotly.graph_objects.Figure
    """
    # 신뢰도 레벨 결정
    if score >= 70:
        color = "#22c55e"  # green
        level = "HIGH"
    elif score >= 50:
        color = "#f59e0b"  # amber
        level = "MEDIUM"
    else:
        color = "#ef4444"  # red
        level = "LOW"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        number={'suffix': "", 'font': {'size': 32, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},   # red-100
                {'range': [50, 70], 'color': '#fef3c7'},  # amber-100
                {'range': [70, 100], 'color': '#dcfce7'}  # green-100
            ],
            'threshold': {
                'line': {'color': "darkgray", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#1f2937", 'family': "Arial"}
    )

    return fig


def render_trust_badge(level):
    """
    신뢰도 등급 배지 렌더링 (HTML)

    Args:
        level (str): 'high', 'medium', 'low'

    Returns:
        str: HTML 배지 코드
    """
    badge_configs = {
        "high": {
            "text": "HIGH TRUST",
            "bg_color": "#22c55e",
            "icon": "✓"
        },
        "medium": {
            "text": "MEDIUM TRUST",
            "bg_color": "#f59e0b",
            "icon": "○"
        },
        "low": {
            "text": "LOW TRUST",
            "bg_color": "#ef4444",
            "icon": "✕"
        }
    }

    config = badge_configs.get(level.lower(), badge_configs["medium"])

    badge_html = f"""
    <div style="
        display: inline-block;
        background-color: {config['bg_color']};
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
        margin: 4px 0;
    ">
        {config['icon']} {config['text']}
    </div>
    """

    return badge_html


def render_comparison_table(products_data):
    """
    제품 비교 테이블 렌더링

    Args:
        products_data (list): 제품 분석 결과 리스트

    Returns:
        pandas.DataFrame
    """
    table_data = []

    for data in products_data:
        product = data["product"]
        ai_result = data["ai_result"]
        reviews = data["reviews"]
        checklist = data["checklist_results"]

        # 광고 의심률 계산
        ad_suspected = sum(1 for r in reviews if r["rating"] == 5 and not r["one_month_use"] and len(r["text"]) < 100)
        ad_rate = ad_suspected / len(reviews) * 100 if reviews else 0

        # 재구매율
        reorder_rate = sum(1 for r in reviews if r["reorder"]) / len(reviews) * 100 if reviews else 0

        # 한달사용 비율
        one_month_rate = sum(1 for r in reviews if r["one_month_use"]) / len(reviews) * 100 if reviews else 0

        # 평균 평점
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0

        table_data.append({
            "제품명": f"{product['brand']}\n{product['name']}",
            "신뢰도": f"{ai_result['trust_score']:.1f}",
            "광고의심률": f"{ad_rate:.1f}%",
            "재구매율": f"{reorder_rate:.1f}%",
            "한달사용": f"{one_month_rate:.1f}%",
            "평균평점": f"{avg_rating:.1f}"
        })

    df = pd.DataFrame(table_data)
    return df


def render_radar_chart(products_data):
    """
    5개 제품 다차원 비교 레이더 차트

    Args:
        products_data (list): 제품 분석 결과 리스트

    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()

    categories = ['신뢰도', '재구매율', '한달사용', '평균평점', '리뷰다양성']

    colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6']

    for idx, data in enumerate(products_data):
        product = data["product"]
        ai_result = data["ai_result"]
        reviews = data["reviews"]

        # 각 지표 계산 (0-100 스케일로 정규화)
        trust_score = ai_result['trust_score']
        reorder_rate = sum(1 for r in reviews if r["reorder"]) / len(reviews) * 100 if reviews else 0
        one_month_rate = sum(1 for r in reviews if r["one_month_use"]) / len(reviews) * 100 if reviews else 0
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews) * 20 if reviews else 0  # 5점 만점 -> 100점 환산
        diversity_rate = len(set(r["reviewer"] for r in reviews)) / len(reviews) * 100 if reviews else 0

        values = [trust_score, reorder_rate, one_month_rate, avg_rating, diversity_rate]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f"{product['brand']}",
            line=dict(color=colors[idx % len(colors)], width=2),
            opacity=0.6
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#1f2937")
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        height=400,
        margin=dict(l=80, r=80, t=40, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#1f2937", 'family': "Arial"}
    )

    return fig


def render_review_sentiment_chart(reviews):
    """
    리뷰 감정 분포 차트 (평점별)

    Args:
        reviews (list): 리뷰 리스트

    Returns:
        plotly.graph_objects.Figure
    """
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for review in reviews:
        rating_counts[review["rating"]] += 1

    fig = go.Figure(data=[
        go.Bar(
            x=list(rating_counts.keys()),
            y=list(rating_counts.values()),
            marker_color=['#ef4444', '#f97316', '#f59e0b', '#22c55e', '#10b981'],
            text=list(rating_counts.values()),
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="평점 분포",
        xaxis_title="평점 (별점)",
        yaxis_title="리뷰 수",
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#1f2937", 'family': "Arial"},
        showlegend=False
    )

    return fig


def render_checklist_visual(checklist_results):
    """
    8단계 체크리스트 시각화 (Streamlit 네이티브 컴포넌트 사용)

    Args:
        checklist_results (dict): 체크리스트 결과

    Note:
        이 함수는 Streamlit 컴포넌트를 직접 렌더링합니다.
        반환값 없이 직접 UI에 렌더링됩니다.
    """
    for key, result in checklist_results.items():
        step_name = result["description"]
        rate = result["rate"]
        passed = result["passed"]

        # 통과 여부에 따른 색상과 아이콘
        icon = "✅" if passed else "❌"
        color = "green" if passed else "red"

        # 체크리스트 항목 표시
        st.markdown(f"{icon} **{step_name}** - :{color}[{rate * 100:.0f}%]")
        st.progress(rate)

    return None


def render_price_comparison_chart(products_data):
    """
    가격 비교 차트

    Args:
        products_data (list): 제품 분석 결과 리스트

    Returns:
        plotly.graph_objects.Figure
    """
    product_names = []
    prices = []
    trust_scores = []

    for data in products_data:
        product = data["product"]
        ai_result = data["ai_result"]

        product_names.append(f"{product['brand']}")
        prices.append(product["price"])
        trust_scores.append(ai_result["trust_score"])

    # 신뢰도에 따른 색상
    colors = ['#22c55e' if score >= 70 else '#f59e0b' if score >= 50 else '#ef4444' for score in trust_scores]

    fig = go.Figure(data=[
        go.Bar(
            x=product_names,
            y=prices,
            marker_color=colors,
            text=[f"${p:.2f}" for p in prices],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="제품 가격 비교",
        xaxis_title="브랜드",
        yaxis_title="가격 (USD)",
        height=300,
        margin=dict(l=40, r=40, t=60, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#1f2937", 'family': "Arial"},
        showlegend=False
    )

    return fig


if __name__ == "__main__":
    print("시각화 컴포넌트 모듈 로드 완료")
    print("사용 가능한 함수:")
    print("  - render_gauge_chart(score, title)")
    print("  - render_trust_badge(level)")
    print("  - render_comparison_table(products_data)")
    print("  - render_radar_chart(products_data)")
    print("  - render_review_sentiment_chart(reviews)")
    print("  - render_checklist_visual(checklist_results)")
    print("  - render_price_comparison_chart(products_data)")
