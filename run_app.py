import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

if __name__ == "__main__":
    # 指向你的主程序文件
    app_path = resolve_path("badminton_app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())