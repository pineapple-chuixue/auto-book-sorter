import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_latest_categories(library_root):
    """
    实时扫描书库目录获取实际存在的分类路径。
    """
    root = Path(library_root)
    categories = set()
    if root.exists():
        ebook_extensions = {'.epub', '.pdf', '.mobi', '.azw3', '.txt', '.azw'}
        for file_path in root.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ebook_extensions:
                rel_path = file_path.parent.relative_to(root)
                category_str = str(rel_path).replace('\\', '/')
                if category_str != '.':
                    categories.add(category_str)
    return sorted(list(categories))

def update_categories_file(library_root, output_file):
    """
    更新包含最新分类的JSON文件并返回此分类列表。
    """
    sorted_categories = get_latest_categories(library_root)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_categories, f, ensure_ascii=False, indent=2)
    return sorted_categories

if __name__ == "__main__":
    config = load_config()
    cats = update_categories_file(
        config["directories"]["library_dir"], 
        config["files"]["categories_file"]
    )
    print(f"🎯 已提取并更新 {len(cats)} 个真实分类至 {config['files']['categories_file']}。")
    for cat in cats:
        print(f"  - {cat}")