import json
import shutil
from pathlib import Path

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

def migrate_books(full_data_path, categorized_data_path, output_root):
    try:
        with open(full_data_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        with open(categorized_data_path, 'r', encoding='utf-8') as f:
            categorized_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ 找不到文件: {e.filename}。")
        return

    path_mapping = { item['id']: item['path'] for item in full_data }
    root_dir = Path(output_root)
    root_dir.mkdir(parents=True, exist_ok=True)

    success_count, fail_count = 0, 0
    print(f"🚀 开始执行归类迁移，目标：{output_root}\n")

    for book in categorized_data:
        book_id = book.get('id')
        category = book.get('category', '00_需手动确认')

        if book_id in path_mapping:
            original_path = Path(path_mapping[book_id])
            if not original_path.exists():
                fail_count += 1
                continue

            target_folder = root_dir / category
            target_folder.mkdir(parents=True, exist_ok=True)
            target_file_path = target_folder / original_path.name

            try:
                shutil.copy2(original_path, target_file_path) # 默认使用复制，安全第一
                print(f"✅ [{category}] <- {original_path.name[:20]}...")
                success_count += 1
            except Exception as e:
                fail_count += 1
        else:
            fail_count += 1

    print(f"\n🎉 迁移完成！成功 {success_count} 本，失败 {fail_count} 本。")

if __name__ == "__main__":
    migrate_books(
        config["files"]["batch_full_data"], 
        config["files"]["ai_output"], 
        config["directories"]["library_dir"]
    )