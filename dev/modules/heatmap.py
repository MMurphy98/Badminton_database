import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from .styles import GITHUB_COLORS

def render_heatmap(df_raw_s, selected_year):
    """渲染年度运动热力图"""
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
        fig_gh = go.Figure(data=go.Heatmap(
            z=daily_stats['持续时间'],
            x=daily_stats['Week'],
            y=daily_stats['Weekday'],
            text=daily_stats['Text'],
            hoverinfo='text',
            colorscale=GITHUB_COLORS, 
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
        )

        st.plotly_chart(fig_gh, use_container_width=True, config={'displayModeBar': False})
        
        # 图例
        st.markdown("""
        <div class="heatmap-legend">
            <span style="margin-right: 4px;">Less</span>
            <span class="heatmap-box" style="background-color: #ebedf0;"></span>
            <span class="heatmap-box" style="background-color: #9be9a8;"></span>
            <span class="heatmap-box" style="background-color: #40c463;"></span>
            <span class="heatmap-box" style="background-color: #30a14e;"></span>
            <span class="heatmap-box" style="background-color: #216e39;"></span>
            <span style="margin-left: 4px;">More</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("💡 暂无数据，快去录入你的第一场球局吧！")
