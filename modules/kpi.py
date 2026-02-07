import streamlit as st

def render_kpi(df_s, df_e, selected_year):
    """渲染顶部 KPI 指标"""
    
    # KPI title
    st.title(f"🏆 {selected_year} · 竞技座舱")
    st.markdown("> 数据来源：`sessions_cleaned.csv`, `equipment_cleaned.csv`, 用于统计全年羽毛球运动的各种开销；")

    k1, k2, k3, k4 = st.columns(4)
    
    total_h = df_s['持续时间'].sum()
    s_cost = df_s['金额'].sum()
    e_cost = df_e['金额'].sum()
    
    # Calculate composite hourly rate (Total Cost / Total Hours)
    comp_cost = (s_cost + e_cost) / total_h if total_h > 0 else 0

    k1.metric("⏱️ 年度总时长", f"{total_h:.1f} H")
    k2.metric("💸 运动投入", f"¥{s_cost:,.0f}")
    k3.metric("🛒 装备投入", f"¥{e_cost:,.0f}")
    k4.metric("📊 综合时薪", f"¥{comp_cost:.1f}/h")
