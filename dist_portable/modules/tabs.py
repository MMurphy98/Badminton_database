import streamlit as st
import pandas as pd
import plotly.express as px
from .styles import highlight_snapped_lines

def render_tabs(df_s, df_e, df_raw_s, df_raw_e, theme):
    """渲染主要功能标签页"""
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 专项统计", "📈 趋势负荷", "🧬 装备透视", "🛡️ 竞技负荷监控", "📋 明细回顾"])

    with tab1:
        _render_stats_tab(df_s, df_e, theme)
        
    with tab2:
        _render_trends_tab(df_s, theme)

    with tab3:
        _render_equipment_insight_tab(df_raw_e)

    with tab4:
        _render_load_monitoring_tab(df_raw_s)

    with tab5:
        _render_details_tab(df_s, df_e)

def _render_stats_tab(df_s, df_e, theme):
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

def _render_trends_tab(df_s, theme):
    w_stats = df_s.groupby(['周数', '类型']).agg({'持续时间': 'sum', '金额': 'sum'}).reset_index()
    fig_time = px.bar(w_stats, x='周数', y='持续时间', color='类型', barmode='stack', title="⚡ 周强度负荷 (Hour)", color_discrete_sequence=theme['palette'])
    fig_time.update_traces(marker=dict(line=dict(color='white', width=1)))
    fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=theme['borderSoft']), legend=dict(font=dict(size=13)))
    st.plotly_chart(fig_time, use_container_width=True)
    fig_cost = px.bar(w_stats, x='周数', y='金额', color='类型', barmode='stack', title="💸 周金额开销 (RMB)", color_discrete_sequence=theme['palette'])
    fig_cost.update_traces(marker=dict(line=dict(color='white', width=1)))
    fig_cost.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=theme['borderSoft']), legend=dict(font=dict(size=13)))
    st.plotly_chart(fig_cost, use_container_width=True)

def _render_equipment_insight_tab(df_raw_e):
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

def _render_load_monitoring_tab(df_raw_s):
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

def _render_details_tab(df_s, df_e):
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
