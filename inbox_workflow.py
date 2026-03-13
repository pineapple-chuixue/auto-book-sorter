import json
import re
import shutil
import subprocess
from pathlib import Path

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
DIR_CFG = config["directories"]
FILE_CFG = config["files"]

def parse_filename(filename):
    clean_name = re.sub(r'\(z-lib\.org\)|\(Z-Library\)|z-lib|zlibrary', '', filename, flags=re.IGNORECASE)
    clean_name = re.sub(r'\.(pdf|epub|mobi|azw3|txt|azw)$', '', clean_name, flags=re.IGNORECASE).strip()
    title = clean_name
    if ' by ' in clean_name: title = clean_name.split(' by ')[0].strip()
    elif ' - ' in clean_name: title = clean_name.split(' - ')[0].strip()
    elif '_' in clean_name: title = clean_name.split('_')[0].strip()
    return title

def phase1_scan_inbox():
    inbox_path = Path(DIR_CFG["inbox_dir"])
    inbox_path.mkdir(parents=True, exist_ok=True)

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
        print("📭 Inbox 是空的。")
        return

    with open(FILE_CFG["local_map"], 'w', encoding='utf-8') as f:
        json.dump(local_map, f, ensure_ascii=False, indent=2)
    with open(FILE_CFG["ai_input"], 'w', encoding='utf-8') as f:
        json.dump(ai_task_list, f, ensure_ascii=False, indent=2)

    try:
        with open(FILE_CFG["categories_file"], 'r', encoding='utf-8') as f:
            categories = json.load(f)
        cat_string = "\n".join([f"- {c}" for c in categories])
        
        prompt_text = f"""请作为图书分类专家，根据我提供的 JSON 书单（包含 ID 和书名）进行精准分类。
【规则】：
1. 优先从已有列表中选择分类：\n{cat_string}
2. 【允许创造】：如果属全新领域，可按现有规范(如"08_新领域/细分领域")自创新分类路径。
3. 模糊不清的分类为 "00_需手动确认"。
必须且只返回格式为 [{{"id": 1, "category": "分类"}}] 的 JSON 数组，不要输出 markdown 标记。"""

        subprocess.run(['clip'], input=prompt_text, text=True, check=True)
        print(f"✅ 生成 {len(ai_task_list)} 本书的任务。Prompt 已自动复制到剪贴板！")
    except Exception as e:
        print("⚠️ 未找到分类字典或自动复制失败。")

def phase2_move_books():
    try:
        with open(FILE_CFG["local_map"], 'r', encoding='utf-8') as f:
            local_map = json.load(f)
        with open(FILE_CFG["ai_output"], 'r', encoding='utf-8') as f:
            ai_results = json.load(f)
    except FileNotFoundError:
        print(f"❌ 未找到 {FILE_CFG['ai_output']}，请确保已保存 AI 结果。")
        return

    path_dict = {item['id']: item['filepath'] for item in local_map}
    lib_path = Path(DIR_CFG["library_dir"])
    success, fail = 0, 0
    used_categories = set() 
    
    for result in ai_results:
        b_id, category = result.get('id'), result.get('category', '00_需手动确认')
        used_categories.add(category)
        
        if b_id in path_dict and Path(path_dict[b_id]).exists():
            src_file = Path(path_dict[b_id])
            target_folder = lib_path / category
            target_folder.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(src_file, target_folder / src_file.name)
                print(f"🚚 -> [{category}] {src_file.name[:20]}")
                success += 1
            except Exception: fail += 1
        else: fail += 1
            
    # 动态更新字典
    try:
        with open(FILE_CFG["categories_file"], 'r', encoding='utf-8') as f:
            existing_cats = set(json.load(f))
    except FileNotFoundError: existing_cats = set()

    new_cats = used_categories - existing_cats - {'00_需手动确认'}
    if new_cats:
        with open(FILE_CFG["categories_file"], 'w', encoding='utf-8') as f:
            json.dump(sorted(list(existing_cats | new_cats)), f, ensure_ascii=False, indent=2)
        print(f"🆕 已将 {len(new_cats)} 个新分类更新至字典。")

    # 清理垃圾
    for tmp in [FILE_CFG["ai_input"], FILE_CFG["ai_output"], FILE_CFG["local_map"]]:
        if Path(tmp).exists(): Path(tmp).unlink()
    print("✨ Inbox 归档并清理完毕！")

if __name__ == "__main__":
    while True:
        print("\n📚 Inbox 流水线 (1: 生成任务并复制Prompt | 2: 归档并清理 | 0: 退出)")
        choice = input("👉 请输入 (0/1/2): ").strip()
        if choice == '1': phase1_scan_inbox()
        elif choice == '2': phase2_move_books()
        elif choice == '0': break