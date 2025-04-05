import os
import shutil

def delete_pycache(path='.'):
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if d == '__pycache__':
                full_path = os.path.join(root, d)
                shutil.rmtree(full_path)
                print(f"✅ 已刪除 {full_path}")

if __name__ == '__main__':
    delete_pycache("src")  # 或改成 "." 一次清整個資料夾
