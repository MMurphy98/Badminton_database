import streamlit as st

def inject_custom_css(theme):
    """注入全局 CSS 样式"""
    st.markdown(f"""
    <style>
        html, body, [class*="css"] {{ font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif; }}
        
        /* Metric Cards */
        div[data-testid="stMetric"] {{ 
            background-color: #FFFFFF; 
            border-radius: 16px; 
            padding: 24px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.06); 
            border: 1px solid {theme.get('borderSoft', '#E6E8EB')}; 
        }}
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{ 
            font-size: 15px; 
            font-weight: 600; 
            color: #2F3B52; 
        }}
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ 
            font-size: 24px; 
            font-weight: 700; 
            color: {theme.get('metricValue', '#1F6FEB')}; 
        }}
        
        /* Sidebar */
        section[data-testid="stSidebar"] {{ 
            background-color: {theme.get('bgSoft', '#F7F8FA')}; 
        }}
        
        /* Buttons */
        div.stButton > button:first-child {{ 
            border-radius: 12px; 
            font-weight: 600; 
            background-color: {theme.get('primary', '#1F6FEB')}; 
            color: white; 
            border: none; 
        }}
        
        /* Tabs: remove gray background for unselected */
        .stTabs [data-baseweb="tab"] {{ background-color: transparent; }}
        
        /* Custom Heatmap Legend */
        .heatmap-legend {{
            display: flex; 
            justify-content: flex-end; 
            align-items: center; 
            font-size: 12px; 
            color: #586069; 
            margin-top: -10px;
        }}
        .heatmap-box {{
            width: 10px; 
            height: 10px; 
            display: inline-block; 
            margin: 0 2px; 
            border-radius: 2px;
        }}
    </style>
    """, unsafe_allow_html=True)

def highlight_snapped_lines(s):
    """高亮断线记录"""
    return ['background-color: #FFE5E5; color: #D70000;' if '单线区断线' in str(s['备注']) else '' for _ in s]

# GitHub color scale for heatmap
GITHUB_COLORS = [
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
