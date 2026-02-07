import pandas as pd
import os
import sys
import streamlit as st

# --- 新增：获取当前运行的基础路径 ---
def get_base_path():
    """
    获取资源文件的基础路径。
    如果是 exe 运行，则返回 exe 所在目录；
    如果是脚本运行，则返回当前工作目录。
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe
        return os.path.dirname(sys.executable)
    else:
        # 普通 python 运行
        return os.getcwd()

BASE_DIR = get_base_path()
SESSIONS_FILE = os.path.join(BASE_DIR, "sessions_cleaned.csv")
EQUIPMENT_FILE = os.path.join(BASE_DIR, "equipment_cleaned.csv")
# -----------------------------------

def get_file_mtime(filepath):
    return os.path.getmtime(filepath) if os.path.exists(filepath) else 0

@st.cache_data
def _load_data_cached(mtime_s, mtime_e):
    """
    实际执行加载数据的函数，带缓存装饰器。
    传入文件的修改时间戳 (mtime) 作为参数，只有当文件修改时，
    参数变化，Streamlit 才会重新执行此函数。
    """
    df_s = pd.DataFrame()
    if os.path.exists(SESSIONS_FILE):
        try:
            # 加入 on_bad_lines='skip' 自动跳过之前写错的那几行数据，防止崩溃
            df_s = pd.read_csv(SESSIONS_FILE, on_bad_lines='skip')
            if not df_s.empty:
                # 统一清理日期格式
                df_s['日期'] = pd.to_datetime(df_s['日期'], errors='coerce')
                df_s = df_s.dropna(subset=['日期']) # 剔除无法解析日期的脏数据
                df_s['持续时间'] = pd.to_numeric(df_s['持续时间'], errors='coerce').round(1)
                df_s['金额'] = pd.to_numeric(df_s['金额'], errors='coerce').round(2)
                df_s['年份'] = df_s['日期'].dt.year
                df_s['周数'] = df_s['日期'].dt.isocalendar().week
                
                # 如果CSV中没有身体评分列，则初始化为8
                if '身体评分' not in df_s.columns:
                    df_s['身体评分'] = 8
                else:
                    df_s['身体评分'] = pd.to_numeric(df_s['身体评分'], errors='coerce').fillna(8)

        except Exception as e:
            st.error(f"数据加载失败: {e}")
    
    if os.path.exists(EQUIPMENT_FILE):
        df_e = pd.read_csv(EQUIPMENT_FILE)
        df_e['日期'] = pd.to_datetime(df_e['日期'])
        df_e['金额'] = pd.to_numeric(df_e['金额'], errors='coerce').round(2)
        df_e['年份'] = df_e['日期'].dt.year
    else:
        df_e = pd.DataFrame(columns=["日期", "类型", "型号", "金额", "说明", "年份"])
        
    return df_s, df_e

def load_data():
    """加载核心数据 (自动检测文件变更)"""
    # 动态获取文件修改时间，作为缓存键
    ts_s = get_file_mtime(SESSIONS_FILE)
    ts_e = get_file_mtime(EQUIPMENT_FILE)
    return _load_data_cached(ts_s, ts_e)

def save_session(new_row_df):
    """追加保存打球记录"""
    # 确保列顺序一致
    cols = ["年份","日期","周数","起始时间","结束时间","类型","金额","持续时间","时间段","身体评分","备注"]
    new_row = new_row_df[cols]
    new_row.to_csv(SESSIONS_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

def save_equipment(new_row_df):
    """追加保存装备记录"""
    new_row_df.to_csv(EQUIPMENT_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
