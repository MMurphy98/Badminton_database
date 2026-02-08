import streamlit as st
from modules.styles import inject_custom_css
from modules.data_loader import load_data
from modules.sidebar import render_sidebar
from modules.kpi import render_kpi
from modules.heatmap import render_heatmap
from modules.tabs import render_tabs

# --- 1. 页面配置 ---
st.set_page_config(page_title="Badminton Dashboard", layout="wide", page_icon="🏸")

def main():
    # --- 2. 核心数据加载 ---
    df_raw_s, df_raw_e = load_data()

    # --- 3. 侧边栏：控制中心 ---
    selected_year, theme = render_sidebar(df_raw_s)
    
    # --- CSS 注入 ---
    inject_custom_css(theme)

    # --- 4. 数据过滤 ---
    df_s = df_raw_s[df_raw_s['年份'] == selected_year]
    df_e = df_raw_e[df_raw_e['年份'] == selected_year]

    # --- 5. 核心指标 ---
    render_kpi(df_s, df_e, selected_year)

    # --- 6. 年度热力图 ---
    render_heatmap(df_raw_s, selected_year)

    # --- 7. 功能标签页 ---
    render_tabs(df_s, df_e, df_raw_s, df_raw_e, theme)

if __name__ == "__main__":
    main()

