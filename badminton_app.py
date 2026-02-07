import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

# --- 1. 页面配置与 iOS 风格 CSS ---
st.set_page_config(page_title="🏸 羽毛球数字化开销分析系统V3.2", layout="wide", page_icon="🏸")

# 注入 iOS 风格 CSS
st.markdown("""
<style>
    /* 全局字体：优先使用苹果系统字体 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 指标卡片 (Metrics) 样式 optimization */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* 柔和阴影 */
        border: 1px solid #F0F0F0;
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    
    /* 侧边栏背景微调 */
    section[data-testid="stSidebar"] {
        background-color: #F9F9F9;
    }
    
    /* 按钮样式 (仿 iOS 按钮) */
    div.stButton > button:first-child {
        border-radius: 12px;
        font-weight: 600;
        border: none;
        background-color: #007AFF; /* iOS Blue */
        color: white;
    }
    div.stButton > button:first-child:hover {
        background-color: #0056b3;
    }

    /* 选项卡样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 10px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #E5E5EA;
    }
</style>
""", unsafe_allow_html=True)

def highlight_snapped_lines(s):
    return ['background-color: #FFE5E5; color: #D70000; border-radius: 4px;' if '单线区断线' in str(s.备注) else '' for _ in s]

# --- 2. 核心数据加载 ---
def load_data():
    if os.path.exists("sessions_cleaned.csv"):
        df_s = pd.read_csv("sessions_cleaned.csv")
        df_s['日期'] = pd.to_datetime(df_s['日期'])
        df_s['持续时间'] = pd.to_numeric(df_s['持续时间'], errors='coerce').round(1)
        df_s['金额'] = pd.to_numeric(df_s['金额'], errors='coerce').round(2)
        df_s['年份'] = df_s['日期'].dt.year
        df_s['周数'] = df_s['日期'].dt.isocalendar().week
    else:
        df_s = pd.DataFrame(columns=["日期", "类型", "金额", "持续时间", "备注", "年份", "周数"])

    if os.path.exists("equipment_cleaned.csv"):
        df_e = pd.read_csv("equipment_cleaned.csv")
        df_e['日期'] = pd.to_datetime(df_e['日期'])
        df_e['金额'] = pd.to_numeric(df_e['金额'], errors='coerce').round(2)
        df_e['年份'] = df_e['日期'].dt.year
    else:
        df_e = pd.DataFrame(columns=["日期", "类型", "型号", "金额", "说明", "年份"])
        
    return df_s, df_e

df_raw_s, df_raw_e = load_data()

# --- 3. 侧边栏：控制与双模录入 (iOS Update) ---
with st.sidebar:
    st.header("⚙️ 控制中心")
    all_years = sorted(df_raw_s['年份'].unique().tolist(), reverse=True) if not df_raw_s.empty else [2026]
    selected_year = st.selectbox("📅 选择复盘年份", all_years)
    
    st.divider()
    # iOS Segmented Control style via radio
    input_mode = st.radio("📝 快速录入", ["🏸 记录打球", "🎒 录入装备"])
    
    if "记录打球" in input_mode:
        with st.form("s_form", clear_on_submit=True):
            st.caption("填写本次运动详情")
            d = st.date_input("日期")
            t = st.selectbox("类型", ["🏸 单打", "👥 双打", "🏃 练球"]) # Added emojis
            t = t.split(" ")[1] # Strip emoji for storage
            
            col1, col2 = st.columns(2)
            with col1: t_s = st.time_input("🟢 开始", datetime.time(20, 0))
            with col2: t_e = st.time_input("🔴 结束", datetime.time(22, 0))
            
            dt_s = datetime.datetime.combine(datetime.date.today(), t_s)
            dt_e = datetime.datetime.combine(datetime.date.today(), t_e)
            if dt_e <= dt_s: dt_e += datetime.timedelta(days=1)
            dur = round((dt_e - dt_s).seconds / 3600, 1)
            
            cost = st.number_input("💰 费用 (¥)", min_value=0.0)
            note = st.text_input("📝 备注 (如: 单线区断线)")
            
            if st.form_submit_button("✅ 保存打球记录"):
                new = pd.DataFrame({"日期":[d.strftime("%Y-%m-%d")],"类型":[t],"金额":[cost],"持续时间":[dur],"备注":[f"[{t_s.strftime('%H:%M')}-{t_e.strftime('%H:%M')}] {note}"]})
                new.to_csv("sessions_cleaned.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                st.toast("🎉 打球记录已保存！")
                st.rerun()
    else:
        with st.form("e_form", clear_on_submit=True):
            st.caption("填写新装备详情")
            d = st.date_input("购买日期")
            e_type_raw = st.selectbox("📦 分类", ["🧶 球线", "🏸 球拍", "👕 服饰", "🏸 羽毛球", "🧢 其余配件"])
            e_type = e_type_raw.split(" ")[1] # Strip emoji settings
            
            model = st.text_input("🏷️ 型号 (如: BG80)")
            cost = st.number_input("💰 金额 (¥)", min_value=0.0)
            desc = st.text_input("ℹ️ 说明 (填球拍名, 如: ZSP)")
            
            if st.form_submit_button("✅ 装备入库"):
                new_e = pd.DataFrame({"日期":[d.strftime("%Y-%m-%d")],"类型":[e_type],"型号":[model],"金额":[cost],"说明":[desc]})
                new_e.to_csv("equipment_cleaned.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                st.toast("🎉 装备已入库！")
                st.rerun()

# --- 4. 数据过滤 ---
df_s = df_raw_s[df_raw_s['年份'] == selected_year]
df_e = df_raw_e[df_raw_e['年份'] == selected_year]

# --- 5. 顶端 KPI (iOS Dashboard) ---
st.title(f"🏆 {selected_year} · 竞技座舱")
st.markdown("##### 🏸 羽毛球数字化开销分析系统")
st.markdown("---")

k1, k2, k3, k4 = st.columns(4)

total_h = df_s['持续时间'].sum()
s_cost = df_s['金额'].sum()
e_cost = df_e['金额'].sum()
comp_cost = (s_cost + e_cost) / total_h if total_h > 0 else 0

# Metrics styling is handled by CSS, we just provide clean labels
k1.metric("⏱️ 年度总时长", f"{total_h:.1f} H")
k2.metric("💸 运动投入", f"¥{s_cost:,.0f}")
k3.metric("🛒 装备投入", f"¥{e_cost:,.0f}")
k4.metric("📊 综合时薪成本", f"¥{comp_cost:.1f}/h")

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# --- 6. 功能标签页 ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 专项统计", "📈 趋势负荷", "📋 明细回顾", "🧬 装备透视"])

with tab1:
    st.subheader("🥧 核心占比分析")
    p1, p2, p3 = st.columns(3)
    
    # 数据准备
    type_stats = df_s.groupby('类型').agg({'金额': 'sum', '持续时间': 'sum'}).reset_index()
    equip_stats = df_e.groupby('类型')['金额'].sum().reset_index()
    all_e_cats = ["球线", "球拍", "服饰", "羽毛球", "其余配件"]
    equip_stats = equip_stats.set_index('类型').reindex(all_e_cats).fillna(0).reset_index()

    with p1:
        st.plotly_chart(px.pie(type_stats, values='金额', names='类型', hole=0.6, title="💰 运动支出占比", color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    with p2:
        st.plotly_chart(px.pie(type_stats, values='持续时间', names='类型', hole=0.6, title="⏳ 运动时长占比", color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    with p3:
        st.plotly_chart(px.pie(equip_stats, values='金额', names='类型', hole=0.6, title="🎒 装备支出占比", color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    
    st.markdown("### 🔢 数据概览")
    c_list1, c_list2 = st.columns(2)
    with c_list1:
        st.caption("运动数据详情")
        s_total = pd.DataFrame({'类型':['🔴 合计'], '金额':[s_cost], '持续时间':[total_h]})
        # Hide index for cleaner iOS list look
        st.dataframe(pd.concat([type_stats, s_total], ignore_index=True).style.format({"金额": "¥{:.2f}", "持续时间": "{:.1f}H"}), use_container_width=True, hide_index=True)
    with c_list2:
        st.caption("装备支出详情")
        e_total = pd.DataFrame({'类型':['🔴 合计'], '金额':[e_cost]})
        st.dataframe(pd.concat([equip_stats, e_total], ignore_index=True).style.format({"金额": "¥{:.2f}"}), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("📈 赛季趋势")
    w_stats = df_s.groupby(['周数', '类型']).agg({'持续时间': 'sum', '金额': 'sum'}).reset_index()
    
    # Cleaner Bar Charts - Reverted colors to default
    fig_time = px.bar(w_stats, x='周数', y='持续时间', color='类型', barmode='stack', title="⚡ 周强度负荷 (Hour)")
    fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
    st.plotly_chart(fig_time, use_container_width=True)
    
    fig_cost = px.bar(w_stats, x='周数', y='金额', color='类型', barmode='stack', title="💸 周金额开销 (RMB)")
    fig_cost.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
    st.plotly_chart(fig_cost, use_container_width=True)

with tab3:
    st.subheader("📝 历史明细")
    ml, mr = st.columns(2)
    with ml:
        st.caption("🏸 打球记录 (Top 20 | 🔴=断线)")
        # Apply style
        styled_df = df_s.sort_values('日期', ascending=False).head(20).style.apply(highlight_snapped_lines, axis=1).format({"日期": "{:%Y-%m-%d}", "金额": "¥{:.0f}"})
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    with mr:
        st.caption("🛡️ 装备明细 (Top 20)")
        st.dataframe(df_e.sort_values('日期', ascending=False).head(20).style.format({"日期": "{:%Y-%m-%d}", "金额": "¥{:.0f}"}), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("🧬 装备适配透视 (球拍 × 球线)")
    if not df_raw_e.empty and '球线' in df_raw_e['类型'].values:
        lines_df = df_raw_e[df_raw_e['类型'] == '球线'].copy()
        
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**🏸 球拍视角：各个拍子用过什么线？**")
            rv = lines_df.groupby(['说明', '型号']).agg({'日期': 'max', '金额': 'count'}).reset_index()
            rv.columns = ['🏸 球拍', '🧶 球线型号', '📅 最后拉线日期', '🔢 累计次数']
            st.dataframe(rv.sort_values(['🏸 球拍', '🔢 累计次数'], ascending=[True, False]), use_container_width=True, hide_index=True)
            
        with cb:
            st.markdown("**🧶 球线视角：各个球线适配过什么拍子？**")
            lv = lines_df.groupby(['型号', '说明']).agg({'日期': 'max', '金额': 'count'}).reset_index()
            lv.columns = ['🧶 球线', '🏸 适配球拍', '📅 最后使用日期', '🔢 使用次数']
            st.dataframe(lv.sort_values(['🧶 球线', '🔢 使用次数'], ascending=[True, False]), use_container_width=True, hide_index=True)
            
        st.success("💡 **教练提示**：对比‘累计次数’。如果你发现 ZSP 的大部分断线记录都集中在某款线上，那说明该线种可能无法承受你的下压爆发力，建议更换耐打型线材（如95线）。")
    else:
        st.warning("⚠️ 暂无球线记录，请在侧边栏录入分类为‘球线’的装备以解锁此面板。")