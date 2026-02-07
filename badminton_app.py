import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import re
from themes import THEMES

# --- 1. 页面配置与 iOS 风格 CSS ---
st.set_page_config(page_title="Badminton Dashboard", layout="wide", page_icon="🏸")

# === 主题配置块 ===
# THEMES = {
#     '冷色·VSCode': {
#         'primary': '#1F6FEB',
#         'metricValue': '#1F6FEB',
#         'bgSoft': '#F7F8FA',
#         'borderSoft': '#E6E8EB',
#         'totalRowBg': '#E9EEF8',
#         'palette': ['#1F6FEB','#3A7BD5','#6EA8FE','#A5D8FF','#9E77ED','#62B6CB','#4C78A8']
#     },
#     '暖色·Sunrise': {
#         'primary': '#FF6B6B',
#         'metricValue': '#FF6B6B',
#         'bgSoft': '#FFF7F3',
#         'borderSoft': '#FFE3D6',
#         'totalRowBg': '#FFE9E3',
#         'palette': ['#FF6B6B','#FFA94D','#FFD43B','#FCC419','#FAB005','#FF922B','#FF8A5B']
#     },
#     '高对比·DarkPlus': {
#         'primary': '#58A6FF',
#         'metricValue': '#58A6FF',
#         'bgSoft': '#0D1117',
#         'borderSoft': '#30363D',
#         'totalRowBg': '#161B22',
#         'palette': ['#58A6FF','#8B949E','#1F6FEB','#E3B341','#D29922','#2EA043','#B62324']
#     },
#     '经典·默认': {
#         'primary': '#007AFF',
#         'metricValue': '#007AFF',
#         'bgSoft': '#F9F9F9',
#         'borderSoft': '#F0F0F0',
#         'totalRowBg': '#F0F4FF',
#         'palette': ['#007AFF','#5AC8FA','#5856D6','#FF9500','#FF2D55','#34C759','#AF52DE']
#     }
# }

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif; }
    div[data-testid="stMetric"] { background-color: #FFFFFF; border-radius: 16px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #E6E8EB; }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] { font-size: 15px; font-weight: 600; color: #2F3B52; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 24px; font-weight: 700; color: #1F6FEB; }
    section[data-testid="stSidebar"] { background-color: #F7F8FA; }
    div.stButton > button:first-child { border-radius: 12px; font-weight: 600; background-color: #1F6FEB; color: white; border: none; }
    /* Tabs: remove gray background for unselected */
    .stTabs [data-baseweb="tab"] { background-color: transparent; }
</style>
""", unsafe_allow_html=True)

def highlight_snapped_lines(s):
    return ['background-color: #FFE5E5; color: #D70000;' if '单线区断线' in str(s.备注) else '' for _ in s]

# --- 2. 核心数据加载 ---
def load_data():
    df_s = pd.DataFrame()
    if os.path.exists("sessions_cleaned.csv"):
        try:
            # 加入 on_bad_lines='skip' 自动跳过之前写错的那几行数据，防止崩溃
            df_s = pd.read_csv("sessions_cleaned.csv", on_bad_lines='skip')
            if not df_s.empty:
                # 统一清理日期格式
                df_s['日期'] = pd.to_datetime(df_s['日期'], errors='coerce')
                df_s = df_s.dropna(subset=['日期']) # 剔除无法解析日期的脏数据
                df_s['持续时间'] = pd.to_numeric(df_s['持续时间'], errors='coerce').round(1)
                df_s['金额'] = pd.to_numeric(df_s['金额'], errors='coerce').round(2)
                df_s['年份'] = df_s['日期'].dt.year
                df_s['周数'] = df_s['日期'].dt.isocalendar().week
                # 增强正则：无论分值在备注开头还是结尾，都能准确提取
                # df_s['身体评分'] = df_s['备注'].str.extract(r'\[(\d+)分\]').astype(float)
                
                # 如果CSV中没有身体评分列，则初始化为8
                if '身体评分' not in df_s.columns:
                    df_s['身体评分'] = 8
                else:
                    df_s['身体评分'] = pd.to_numeric(df_s['身体评分'], errors='coerce').fillna(8)

        except Exception as e:
            st.error(f"数据加载失败: {e}")
    
    if os.path.exists("equipment_cleaned.csv"):
        df_e = pd.read_csv("equipment_cleaned.csv")
        df_e['日期'] = pd.to_datetime(df_e['日期'])
        df_e['金额'] = pd.to_numeric(df_e['金额'], errors='coerce').round(2)
        df_e['年份'] = df_e['日期'].dt.year
    else:
        df_e = pd.DataFrame(columns=["日期", "类型", "型号", "金额", "说明", "年份"])
        
    return df_s, df_e

df_raw_s, df_raw_e = load_data()

# --- 3. 侧边栏：控制中心 ---
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
            
            # 2. 自动判定时间段 (匹配你原表中的：早上、中午、下午、晚上)
            h = t_s.hour
            if 5 <= h < 12: period = "早上"
            elif 12 <= h < 14: period = "中午"
            elif 14 <= h < 18: period = "下午"
            else: period = "晚上"
            
            cost = st.number_input("💰 费用 (¥)", min_value=0.0)
            body_val = st.slider("✨ 身体状态评分 (1-10)", 1, 10, 8)
            note = st.text_input("📝 备注")
            
            if st.form_submit_button("✅ 保存打球记录"):
                # 构造与当前 CSV 列顺序一致的数据：
                # 年份, 日期, 周数, 起始时间, 结束时间, 类型, 金额, 持续时间, 时间段, 身体评分, 备注
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
                
                # 写入时 header=False，保持列顺序与 CSV 一致
                new_row = new_row[["年份","日期","周数","起始时间","结束时间","类型","金额","持续时间","时间段","身体评分","备注"]]
                new_row.to_csv("sessions_cleaned.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                st.toast("🎉 记录已成功保存！")
                st.rerun()
    else:
        with st.form("e_form", clear_on_submit=True):
            d = st.date_input("购买日期")
            e_type_raw = st.selectbox("📦 分类", ["🧶 球线", "🏸 球拍", "👕 服饰", "🏸 羽毛球", "🧢 其余配件"])
            e_type = e_type_raw.split(" ")[1]
            model = st.text_input("🏷️ 型号 (如: BG80)")
            cost = st.number_input("💰 金额 (¥)", min_value=0.0)
            desc = st.text_input("ℹ️ 说明 (填球拍名, 如: ZSP)")
            if st.form_submit_button("✅ 装备入库"):
                new_e = pd.DataFrame({"日期":[d.strftime("%Y-%m-%d")],"类型":[e_type],"型号":[model],"金额":[cost],"说明":[desc]})
                new_e.to_csv("equipment_cleaned.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                st.toast("🎉 装备已入库！")
                st.cache_data.clear()
                st.rerun()

# --- 4. 数据过滤与 KPI ---
df_s = df_raw_s[df_raw_s['年份'] == selected_year]
df_e = df_raw_e[df_raw_e['年份'] == selected_year]

# KPI 说明替代横线
st.title(f"🏆 {selected_year} · 竞技座舱")
st.markdown("> 数据来源：`sessions_cleaned.csv`, `equipment_cleaned.csv`, 用于统计全年羽毛球运动的各种开销；")

k1, k2, k3, k4 = st.columns(4)
total_h = df_s['持续时间'].sum()
s_cost = df_s['金额'].sum()
e_cost = df_e['金额'].sum()
comp_cost = (s_cost + e_cost) / total_h if total_h > 0 else 0

k1.metric("⏱️ 年度总时长", f"{total_h:.1f} H")
k2.metric("💸 运动投入", f"¥{s_cost:,.0f}")
k3.metric("🛒 装备投入", f"¥{e_cost:,.0f}")
k4.metric("📊 综合时薪", f"¥{comp_cost:.1f}/h")

# --- 📆 年度热力图 (自动填满版) ---
st.markdown("### 📅 年度运动热力图")

if not df_raw_s.empty:
    # 1. 数据准备
    df_year = df_raw_s[df_raw_s['年份'] == selected_year].copy()
    
    # 构造全年的日期网格
    start_date = pd.Timestamp(f"{selected_year}-01-01")
    end_date = pd.Timestamp(f"{selected_year}-12-31")
    all_days = pd.date_range(start_date, end_date, freq='D')
    
    # 补全数据（无记录的日子填0）
    daily_stats = df_year.groupby('日期')['持续时间'].sum().reindex(all_days, fill_value=0).reset_index()
    daily_stats.columns = ['日期', '持续时间']
    
    # 2. 计算坐标系统 (x=周数, y=星期几)
    # GitHub 布局：Monday=0 (最上), Sunday=6 (最下)
    daily_stats['Weekday'] = daily_stats['日期'].dt.weekday 
    
    # 计算周数 (对齐到年初的第一个周一)
    # 逻辑：(DayOfYear + StartWeekday) // 7
    year_start_weekday = start_date.weekday()
    daily_stats['Week'] = (daily_stats['日期'] - start_date).dt.days + year_start_weekday
    daily_stats['Week'] = daily_stats['Week'] // 7
    
    # 3. 准备悬停交互文本
    daily_stats['Text'] = daily_stats.apply(lambda x: f"<b>{x['日期'].strftime('%Y-%m-%d')}</b><br>时长: {x['持续时间']:.1f} 小时", axis=1)

    # 4. 绘图 (使用 Heatmap 实现自动填充)
    import plotly.graph_objects as go
    
    # 定义 GitHub 官方绿色系 (从浅到深)
    # 0值: 灰色, 1-4级: 绿色的不同深浅
    github_colors = [
        [0.0, '#ebedf0'],   # 0h (灰色背景)
        [0.0001, '#9be9a8'],# >0h (浅绿)
        [0.2, '#9be9a8'],
        [0.2001, '#40c463'],# 中绿
        [0.5, '#40c463'],
        [0.5001, '#30a14e'],# 深绿
        [0.8, '#30a14e'],
        [0.8001, '#216e39'],# 极深绿
        [1.0, '#216e39']
    ]

    fig_gh = go.Figure(data=go.Heatmap(
        z=daily_stats['持续时间'],
        x=daily_stats['Week'],
        y=daily_stats['Weekday'],
        text=daily_stats['Text'],
        hoverinfo='text',
        colorscale=github_colors, 
        showscale=False, # 隐藏右侧色条，保持极简
        xgap=3, # 设置白色间距 (关键：模拟方块效果)
        ygap=3, 
    ))

    # 5. 布局优化 (实现自动化占满)
    fig_gh.update_layout(
        height=180, # 固定高度，宽度自动适应容器
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False, # 隐藏周数索引，更干净
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickmode='array',
            tickvals=[0, 2, 4, 6], # 只显示 Mon, Wed, Fri, Sun
            ticktext=['Mon', 'Wed', 'Fri', 'Sun'],
            autorange="reversed", # 翻转Y轴，让周一在最上面
            fixedrange=True,
        ),
        # 关键：这里不使用 scaleanchor='x'，允许方块轻微拉伸以填满整个宽度
        # 如果你必须要素是“正方形”，可以加上 scaleanchor='x'，但那样如果屏幕超宽就会有留白
    )

    st.plotly_chart(fig_gh, use_container_width=True, config={'displayModeBar': False})
    
    # 手写一个漂亮的图例
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; align-items: center; font-size: 12px; color: #586069; margin-top: -10px;">
        <span style="margin-right: 4px;">Less</span>
        <span style="background-color: #ebedf0; width: 10px; height: 10px; display: inline-block; margin: 0 2px; border-radius: 2px;"></span>
        <span style="background-color: #9be9a8; width: 10px; height: 10px; display: inline-block; margin: 0 2px; border-radius: 2px;"></span>
        <span style="background-color: #40c463; width: 10px; height: 10px; display: inline-block; margin: 0 2px; border-radius: 2px;"></span>
        <span style="background-color: #30a14e; width: 10px; height: 10px; display: inline-block; margin: 0 2px; border-radius: 2px;"></span>
        <span style="background-color: #216e39; width: 10px; height: 10px; display: inline-block; margin: 0 2px; border-radius: 2px;"></span>
        <span style="margin-left: 4px;">More</span>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("💡 暂无数据，快去录入你的第一场球局吧！")

# 动态 CSS 根据主题
st.markdown(f"""
<style>
    div[data-testid=\"stMetric\"] {{ background-color: #FFFFFF; border-radius: 16px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid {theme['borderSoft']}; }}
    div[data-testid=\"stMetric\"] [data-testid=\"stMetricLabel\"] {{ font-size: 15px; font-weight: 600; color: #2F3B52; }}
    div[data-testid=\"stMetric\"] [data-testid=\"stMetricValue\"] {{ font-size: 24px; font-weight: 700; color: {theme['metricValue']}; }}
    section[data-testid=\"stSidebar\"] {{ background-color: {theme['bgSoft']}; }}
    div.stButton > button:first-child {{ border-radius: 12px; font-weight: 600; background-color: {theme['primary']}; color: white; border: none; }}
</style>
""", unsafe_allow_html=True)

# 统一冷色主题调色板（参考 VS Code 冷色系）
COOL_PALETTE = ['#1F6FEB','#3A7BD5','#6EA8FE','#A5D8FF','#9E77ED','#62B6CB','#4C78A8']

# --- 5. 功能标签页 ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 专项统计", "📈 趋势负荷", "🧬 装备透视", "🛡️ 竞技负荷监控", "📋 明细回顾"])

with tab1:
    st.subheader("🥧 核心占比分析")
    p1, p2, p3 = st.columns(3)
    type_stats = df_s.groupby('类型').agg({'金额': 'sum', '持续时间': 'sum'}).reset_index()
    
    fixed_cats = ["球线", "球拍", "服饰", "羽毛球", "其余配件"]
    equip_stats_raw = df_e.groupby('类型')['金额'].sum().reset_index()
    equip_stats = (
        equip_stats_raw.set_index('类型').reindex(fixed_cats).fillna(0).rename_axis('类型').reset_index()
    )
    
    with p1:
        fig1 = px.pie(type_stats, values='金额', names='类型', hole=0.6, title="💰 运动支出占比", color_discrete_sequence=theme['palette'])
        fig1.update_traces(marker=dict(line=dict(color='white', width=2)))
        fig1.update_layout(legend=dict(font=dict(size=13)))
        st.plotly_chart(fig1, use_container_width=True)
        s_total = pd.DataFrame({'类型': ['合计'], '金额': [type_stats['金额'].sum()]})
        table1 = pd.concat([type_stats[['类型','金额']], s_total], ignore_index=True).style.format({'金额': '¥{:.2f}'})
        table1 = table1.apply(lambda r: [f"background-color: {theme['totalRowBg']}; color:{theme['primary']}; font-weight:700" if r.name == len(table1.data)-1 else '' for _ in r], axis=1)
        st.dataframe(table1, use_container_width=True, hide_index=True)
    with p2:
        fig2 = px.pie(type_stats, values='持续时间', names='类型', hole=0.6, title="⏳ 运动时长占比", color_discrete_sequence=theme['palette'])
        fig2.update_traces(marker=dict(line=dict(color='white', width=2)))
        fig2.update_layout(legend=dict(font=dict(size=13)))
        st.plotly_chart(fig2, use_container_width=True)
        h_total = pd.DataFrame({'类型': ['合计'], '持续时间': [type_stats['持续时间'].sum()]})
        table2 = pd.concat([type_stats[['类型','持续时间']], h_total], ignore_index=True).style.format({'持续时间': '{:.1f} H'})
        table2 = table2.apply(lambda r: [f"background-color: {theme['totalRowBg']}; color:{theme['primary']}; font-weight:700" if r.name == len(table2.data)-1 else '' for _ in r], axis=1)
        st.dataframe(table2, use_container_width=True, hide_index=True)
    with p3:
        fig3 = px.pie(equip_stats, values='金额', names='类型', hole=0.6, title="🎒 装备支出占比", color_discrete_sequence=theme['palette'])
        fig3.update_traces(marker=dict(line=dict(color='white', width=2)))
        fig3.update_layout(legend=dict(font=dict(size=13)))
        st.plotly_chart(fig3, use_container_width=True)
        e_total = pd.DataFrame({'类型': ['合计'], '金额': [equip_stats['金额'].sum()]})
        table3 = pd.concat([equip_stats[['类型','金额']], e_total], ignore_index=True).style.format({'金额': '¥{:.2f}'})
        table3 = table3.apply(lambda r: [f"background-color: {theme['totalRowBg']}; color:{theme['primary']}; font-weight:700" if r.name == len(table3.data)-1 else '' for _ in r], axis=1)
        st.dataframe(table3, use_container_width=True, hide_index=True)

# 趋势负荷：统一当前主题的配色
with tab2:
    w_stats = df_s.groupby(['周数', '类型']).agg({'持续时间': 'sum', '金额': 'sum'}).reset_index()
    fig_time = px.bar(w_stats, x='周数', y='持续时间', color='类型', barmode='stack', title="⚡ 周强度负荷 (Hour)", color_discrete_sequence=theme['palette'])
    fig_time.update_traces(marker=dict(line=dict(color='white', width=1)))
    fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=theme['borderSoft']), legend=dict(font=dict(size=13)))
    st.plotly_chart(fig_time, use_container_width=True)
    fig_cost = px.bar(w_stats, x='周数', y='金额', color='类型', barmode='stack', title="💸 周金额开销 (RMB)", color_discrete_sequence=theme['palette'])
    fig_cost.update_traces(marker=dict(line=dict(color='white', width=1)))
    fig_cost.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=theme['borderSoft']), legend=dict(font=dict(size=13)))
    st.plotly_chart(fig_cost, use_container_width=True)

with tab3:
    st.subheader("🧬 装备适配透视")
    if not df_raw_e.empty and '球线' in df_raw_e['类型'].values:
        lines_df = df_raw_e[df_raw_e['类型'] == '球线'].copy().sort_values('日期')
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**🏸 球拍视角：各个拍子用过什么线？**")
            rv = lines_df.groupby(['说明', '型号']).agg({'日期': 'max', '金额': 'count'}).reset_index()
            rv.columns = ['🏸 球拍', '🧶 球线型号', '📅 最后拉线', '🔢 累计次数']
            st.dataframe(rv.sort_values(['🏸 球拍', '🔢 累计次数'], ascending=[True, False]), use_container_width=True, hide_index=True)
        with cb:
            st.markdown("**🧶 球线视角：历史适配记录**")
            lv = lines_df.groupby(['型号', '说明']).agg({'金额': 'count', '日期': 'max'}).reset_index()
            lv.columns = ['🧶 球线', '🏸 适配拍', '🔢 使用次数', '📅 最后使用']
            st.dataframe(lv, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 暂无球线记录。")

with tab4:
    st.subheader("🛡️ 竞技负荷曲线与安全预警")
    if not df_raw_s.empty:
        # 1. 每周负荷曲线 (Line Chart)
        weekly_total = df_raw_s.groupby(['年份', '周数'])['持续时间'].sum().reset_index()
        weekly_total['周'] = weekly_total['年份'].astype(str) + " W" + weekly_total['周数'].astype(str)
        
        fig_line = px.line(weekly_total, x='周', y='持续时间', markers=True, title="📈 每周总负荷趋势 (小时)",
                          line_shape='spline', color_discrete_sequence=['#007AFF'])
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#eee'))
        st.plotly_chart(fig_line, use_container_width=True)
        
        # 2. ACWR 负荷比逻辑
        st.markdown("---")
        c_risk, c_trend = st.columns([1, 2])
        with c_risk:
            all_weeks = weekly_total['持续时间'].tolist()
            if len(all_weeks) >= 2:
                acute = all_weeks[-1]
                chronic = sum(all_weeks[-5:-1]) / 4 if len(all_weeks) >= 5 else sum(all_weeks[:-1]) / len(all_weeks[:-1])
                acwr = acute / chronic if chronic > 0 else 1.0
                
                st.metric("📊 本周负荷比 (ACWR)", f"{acwr:.2f}")
                if acwr > 1.5: st.error("🚨 预警：负荷激增！本周运动量远超均值。由于你核心强但柔韧性差，极易发生代偿性拉伤。")
                elif acwr > 1.2: st.warning("⚠️ 提醒：负荷正在快速爬升，请注意肌肉深度拉伸。")
                else: st.success("✅ 状态：负荷稳定，处于竞技安全区间。")
        
        with c_trend:
            # 3. 身体评分趋势
            score_df = df_raw_s.dropna(subset=['身体评分']).sort_values('日期')
            if not score_df.empty:
                fig_score = px.line(score_df, x='日期', y='身体评分', markers=True, title="✨ 身体清爽度趋势 (1-10)",
                                   color_discrete_sequence=['#34C759'])
                fig_score.update_layout(yaxis_range=[0,11], plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_score, use_container_width=True)
            else:
                st.info("💡 尚未录入身体评分。下次录入时请拖动侧边栏滑块。")
    else:
        st.info("数据不足，无法生成监控。")

with tab5:
    st.write("🏸 **打球记录** (🔴=单线断线)")
    # 打球记录：格式化日期为 YYYY-MM-DD，金额两位小数，移除年份列
    df_play = df_s.sort_values('日期', ascending=False).head(20).copy()
    if '年份' in df_play.columns:
        df_play = df_play.drop(columns=['年份'])
    styled_play = df_play.style.apply(highlight_snapped_lines, axis=1).format({
        '日期': '{:%Y-%m-%d}',
        '金额': '{:.2f}'
    })
    st.dataframe(styled_play, use_container_width=True, hide_index=True)
    
    st.write("🛡️ **装备明细**")
    df_equip = df_e.sort_values('日期', ascending=False).head(20).copy()
    if '年份' in df_equip.columns:
        df_equip = df_equip.drop(columns=['年份'])
    st.dataframe(df_equip.style.format({'日期': '{:%Y-%m-%d}', '金额': '{:.2f}'}), use_container_width=True, hide_index=True)

# ...removed separate calendar tab; heatmap moved under KPI...