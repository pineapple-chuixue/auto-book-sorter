import json
import re
from pathlib import Path

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

def parse_filename(filename):
    clean_name = re.sub(r'\(z-lib\.org\)|\(Z-Library\)|z-lib|zlibrary', '', filename, flags=re.IGNORECASE)
    clean_name = re.sub(r'\.(pdf|epub|mobi|azw3|txt|azw)$', '', clean_name, flags=re.IGNORECASE).strip()
    title = clean_name
    if ' by ' in clean_name:
        title = clean_name.split(' by ')[0].strip()
    elif ' - ' in clean_name:
        title = clean_name.split(' - ')[0].strip()
    elif '_' in clean_name: 
        title = clean_name.split('_')[0].strip()
    return title

def process_books(directory):
    ebook_extensions = {'.epub', '.pdf', '.mobi', '.azw3', '.txt', '.azw'}
    full_data, ai_data = [], []
    path = Path(directory)
    
    if not path.exists():
        print(f"❌ 错误：目录 {directory} 不存在！请检查 config.json")
        return [], []

    book_id = 1
    for file_path in path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ebook_extensions:
            title = parse_filename(file_path.name)
            full_data.append({"id": book_id, "path": str(file_path.absolute())})
            ai_data.append({"id": book_id, "title": title})
            book_id += 1
            
    return full_data, ai_data

if __name__ == "__main__":
    target_dir = config["directories"]["unorganized_dir"]
    full_json = config["files"]["batch_full_data"]
    ai_json = config["files"]["ai_input"]
    
    print(f"🔍 正在扫描旧书目录：{target_dir} ...")
    full_data, ai_data = process_books(target_dir)
    
    if full_data:
        with open(full_json, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
        with open(ai_json, 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, ensure_ascii=False, indent=2)
        print(f"🎉 共处理 {len(full_data)} 本书。已生成 {full_json} 和 {ai_json}")