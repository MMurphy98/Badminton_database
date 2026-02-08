import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    """获取资源的绝对路径，适配 PyInstaller 打包后的路径环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 EXE 环境，路径指向临时解压目录或 _internal 文件夹
        basedir = sys._MEIPASS
    else:
        # 如果是正常 Python 运行环境，路径指向当前脚本所在目录
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # 1. 动态定位主程序文件
    app_path = resolve_path("badminton_app.py")
    
    # 2. 检查主程序是否存在（防御性编程，防止打包丢文件）
    if not os.path.exists(app_path):
        print(f"错误：找不到主程序文件 {app_path}")
        sys.exit(1)

    # 3. 构造启动参数
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",  # 建议开启：防止弹出多余的命令行交互
    ]
    
    # 4. 启动 Streamlit
    sys.exit(stcli.main())