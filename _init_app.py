# _init_app.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 將 src/ 加入 sys.path，讓 app.py 等主程式能正確匯入自訂模組
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# 載入 .env 檔
load_dotenv()

# 可選：印出初始化資訊
print(f"[INIT] src/ 模組路徑已載入")
print(f"[INIT] .env 已載入")
