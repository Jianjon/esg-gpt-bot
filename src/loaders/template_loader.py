# 📂 src/loaders/template_loader.py
"""
讀取報告語句模組 .md 檔，解析 YAML 標頭，依照 industry_type 與 report_section 整理語句。
回傳 nested dict 結構，供報告產生器使用。
"""

import os
import yaml

TEMPLATE_FOLDER = "templates/report_sentences"


def load_all_templates(template_folder=TEMPLATE_FOLDER):
    """
    從指定資料夾中讀取所有 .md 模板檔案，
    回傳 nested dict 結構：{industry_type: {report_section: [sentences]}}
    """
    template_dict = {}

    for filename in os.listdir(template_folder):
        if not filename.endswith(".md"):
            continue

        file_path = os.path.join(template_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 拆分 YAML 與內容
        if content.startswith("---"):
            _, header, body = content.split("---", 2)
            meta = yaml.safe_load(header)
        else:
            raise ValueError(f"❌ 缺少 YAML 區塊：{filename}")

        industry = meta.get("industry_type")
        section = meta.get("report_section")
        if not industry or not section:
            raise ValueError(f"❌ YAML 缺少欄位：{filename}")

        # 內容句子：按行分割、去除空行
        sentences = [line.strip() for line in body.strip().splitlines() if line.strip()]

        if industry not in template_dict:
            template_dict[industry] = {}
        if section not in template_dict[industry]:
            template_dict[industry][section] = []

        template_dict[industry][section].extend(sentences)

    return template_dict


if __name__ == "__main__":
    result = load_all_templates()
    for industry, sections in result.items():
        print(f"\n✅ {industry}")
        for section, items in sections.items():
            print(f"  - {section}：{len(items)} 句")
