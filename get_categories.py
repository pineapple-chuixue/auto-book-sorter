import json
from pathlib import Path

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

def extract_categories(library_root, output_file):
    root = Path(library_root)
    if not root.exists():
        print(f"❌ 找不到书库目录: {library_root}")
        return

    categories = set()
    ebook_extensions = {'.epub', '.pdf', '.mobi', '.azw3', '.txt', '.azw'}
    
    for file_path in root.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ebook_extensions:
            rel_path = file_path.parent.relative_to(root)
            category_str = str(rel_path).replace('\\', '/')
            if category_str != '.':
                categories.add(category_str)

    sorted_categories = sorted(list(categories))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_categories, f, ensure_ascii=False, indent=2)
    
    print(f"🎯 已提取 {len(sorted_categories)} 个分类，并保存至 {output_file}")
    for cat in sorted_categories:
        print(f"  - {cat}")

if __name__ == "__main__":
    extract_categories(
        config["directories"]["library_dir"], 
        config["files"]["categories_file"]
    )