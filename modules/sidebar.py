import streamlit as st
import datetime
import pandas as pd
from themes import THEMES
from .data_loader import save_session, save_equipment

def render_sidebar(df_raw_s):
    """渲染侧边栏并返回用户选择的配置"""
    with st.sidebar:
        st.header("⚙️ 控制中心")
        # 主题选择开关
        selected_theme_name = st.selectbox('🎨 页面主题', list(THEMES.keys()), index=0)
        theme = THEMES[selected_theme_name]

        all_years = sorted(df_raw_s['年份'].unique().tolist(), reverse=True) if not df_raw_s.empty else [2026]
        selected_year = st.selectbox("📅 选择复盘年份", all_years)
        
        st.divider()
        input_mode = st.radio("📝 快速录入", ["🏸 记录打球", "🎒 录入装备"])
        
        if "记录打球" in input_mode:
            _render_session_form()
        else:
            _render_equipment_form()
            
    return selected_year, theme

def _render_session_form():
    """渲染打球记录表单"""
    with st.form("s_form", clear_on_submit=True):
        d = st.date_input("日期")
        t = st.selectbox("类型", ["🏸 单打", "👥 双打", "🏃 练球"]).split(" ")[1]
        
        col1, col2 = st.columns(2)
        with col1: t_s = st.time_input("🟢 开始", datetime.time(20, 0))
        with col2: t_e = st.time_input("🔴 结束", datetime.time(22, 0))
        
        # 1. 自动核算时长
        dt_s = datetime.datetime.combine(datetime.date.today(), t_s)
        dt_e = datetime.datetime.combine(datetime.date.today(), t_e)
        if dt_e <= dt_s: dt_e += datetime.timedelta(days=1)
        dur = round((dt_e - dt_s).seconds / 3600, 1)
        
        # 2. 自动判定时间段
        h = t_s.hour
        if 5 <= h < 12: period = "早上"
        elif 12 <= h < 14: period = "中午"
        elif 14 <= h < 18: period = "下午"
        else: period = "晚上"
        
        cost = st.number_input("💰 费用 (¥)", min_value=0.0)
        body_val = st.slider("✨ 身体状态评分 (1-10)", 1, 10, 8)
        note = st.text_input("📝 备注")
        
        if st.form_submit_button("✅ 保存打球记录"):
            new_row = pd.DataFrame({
                "年份": [d.year],
                "日期": [d.strftime("%Y/%m/%d")],
                "周数": [d.isocalendar()[1]],
                "起始时间": [t_s.strftime('%H:%M')],
                "结束时间": [t_e.strftime('%H:%M')],
                "类型": [t],
                "金额": [round(cost, 2)],
                "持续时间": [dur],
                "时间段": [period],
                "身体评分": [body_val],
                "备注": [note]
            })
            
            save_session(new_row)
            st.toast("🎉 记录已成功保存！")
            st.rerun()

def _render_equipment_form():
    """渲染装备录入表单"""
    with st.form("e_form", clear_on_submit=True):
        d = st.date_input("购买日期")
        e_type_raw = st.selectbox("📦 分类", ["🧶 球线", "🏸 球拍", "👕 服饰", "🏸 羽毛球", "🧢 其余配件"])
        e_type = e_type_raw.split(" ")[1]
        model = st.text_input("🏷️ 型号 (如: BG80)")
        cost = st.number_input("💰 金额 (¥)", min_value=0.0)
        desc = st.text_input("ℹ️ 说明 (填球拍名, 如: ZSP)")
        
        if st.form_submit_button("✅ 装备入库"):
            new_e = pd.DataFrame({
                "日期": [d.strftime("%Y-%m-%d")],
                "类型": [e_type],
                "型号": [model],
                "金额": [cost],
                "说明": [desc]
            })
            save_equipment(new_e)
            st.toast("🎉 装备已入库！")
            # st.cache_data.clear() # 不需要手动清除，因为 data_loader 已根据文件修改时间自动检测
            st.rerun()
