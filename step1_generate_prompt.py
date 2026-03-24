import json
import re
import sys
import subprocess
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from get_categories import update_categories_file, load_config

def parse_filename(filename):
    clean_name = re.sub(r'\(z-lib\.org\)|\(Z-Library\)|z-lib|zlibrary', '', filename, flags=re.IGNORECASE)
    clean_name = re.sub(r'\.(pdf|epub|mobi|azw3|txt|azw)$', '', clean_name, flags=re.IGNORECASE).strip()
    title = clean_name
    if ' by ' in clean_name: title = clean_name.split(' by ')[0].strip()
    elif ' - ' in clean_name: title = clean_name.split(' - ')[0].strip()
    elif '_' in clean_name: title = clean_name.split('_')[0].strip()
    return title

def main():
    config = load_config()
    DIR_CFG = config["directories"]
    FILE_CFG = config["files"]

    inbox_path = Path(DIR_CFG["inbox_dir"])
    inbox_path.mkdir(parents=True, exist_ok=True)
    lib_path = Path(DIR_CFG["library_dir"])

    ebook_extensions = {'.epub', '.pdf', '.mobi', '.azw3', '.txt', '.azw'}
    local_map, ai_task_list = [], []
    book_id = 1

    for file_path in inbox_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ebook_extensions:
            title = parse_filename(file_path.name)
            local_map.append({"id": book_id, "filename": file_path.name, "filepath": str(file_path.absolute())})
            ai_task_list.append({"id": book_id, "title": title})
            book_id += 1

    if not ai_task_list:
        print("📭 Inbox (暂存区) 没有任何电子书。")
        return

    # 先提取一遍最新的真实书架分类，确保字典最新鲜
    categories = update_categories_file(lib_path, FILE_CFG["categories_file"])
    
    with open(FILE_CFG["local_map"], 'w', encoding='utf-8') as f:
        json.dump(local_map, f, ensure_ascii=False, indent=2)
    with open(FILE_CFG["ai_input"], 'w', encoding='utf-8') as f:
        json.dump(ai_task_list, f, ensure_ascii=False, indent=2)

    cat_string = "\n".join([f"- {c}" for c in categories])
    books_json_str = json.dumps(ai_task_list, ensure_ascii=False, indent=2)
    prompt_text = f"""请作为图书分类专家，根据我提供的 JSON 书单（包含 ID 和书名）进行精准分类。
【规则】：
1. 优先从已有列表中选择分类：\n{cat_string}
2. 【允许创造】：如果属全新领域，可按现有规范(如"新领域/细分领域")自创新分类路径。
3. 模糊不清的分类为 "00_需手动确认"。
必须且只返回格式为 [{{"id": 1, "category": "分类"}}] 的 JSON 数组，不要输出 markdown 标记。

【需分类的书单】：
{books_json_str}"""

    with open("prompt_for_ai.txt", "w", encoding="utf-8") as f:
        f.write(prompt_text)

    try:
        subprocess.run(['powershell', '-noprofile', '-command', 'Get-Content prompt_for_ai.txt -Encoding UTF8 | Set-Clipboard'], check=True)
        print(f"✅ 从 Inbox 发现了 {len(ai_task_list)} 本书。AI 提示词已自动复制到剪贴板！（内容已备份至 prompt_for_ai.txt）")
        print(f"👉 下一步：发给网页端 AI 并在获取 JSON 后，粘贴保存为本目录下的 `{FILE_CFG['ai_output']}` 。然后运行 step2_sort_books.py")
    except Exception as e:
        print(f"⚠️ 自动复制剪贴板失败: {e}\n👉 请手动打开本目录下的 `prompt_for_ai.txt` 复制全部内容并发送给 AI。")

if __name__ == "__main__":
    main()
