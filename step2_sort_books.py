import json
import shutil
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
from get_categories import update_categories_file, load_config

def main():
    config = load_config()
    DIR_CFG = config["directories"]
    FILE_CFG = config["files"]

    try:
        with open(FILE_CFG["categories_file"], 'r', encoding='utf-8') as f:
            old_cats = set(json.load(f))
    except FileNotFoundError:
        old_cats = set()

    try:
        with open(FILE_CFG["local_map"], 'r', encoding='utf-8') as f:
            local_map = json.load(f)
        with open(FILE_CFG["ai_output"], 'r', encoding='utf-8') as f:
            ai_results = json.load(f)
    except FileNotFoundError:
        print(f"❌ 未找到所需文件，请确保 AI 分类结果已保存为 {FILE_CFG['ai_output']}，并且先运行了 step1 生成了映射文件。")
        return

    path_dict = {item['id']: item['filepath'] for item in local_map}
    lib_path = Path(DIR_CFG["library_dir"])
    lib_path.mkdir(parents=True, exist_ok=True)
    
    success, fail = 0, 0
    moved_records_by_cat = {}
    print(f"🚀 开始将 Inbox 中的书籍移动到分类书架...\n")

    for result in ai_results:
        b_id = result.get('id')
        category = result.get('category', '00_需手动确认')
        
        if b_id in path_dict and Path(path_dict[b_id]).exists():
            src_file = Path(path_dict[b_id])
            target_folder = lib_path / category
            target_folder.mkdir(parents=True, exist_ok=True)
            
            try:
                # 移动书籍：如果是同名文件会被覆盖
                shutil.move(str(src_file), str(target_folder / src_file.name))
                print(f"🚚 -> [{category}] {src_file.name[:25]}...")
                if category not in moved_records_by_cat:
                    moved_records_by_cat[category] = []
                moved_records_by_cat[category].append(src_file.name)
                success += 1
            except Exception as e:
                print(f"⚠️ 移动失败 [{src_file.name}]: {e}")
                fail += 1
        else:
            fail += 1

    print(f"\n🎉 归档完成！成功移动 {success} 本，失败 {fail} 本。")
    
    # 归档后更新书库最新分类结构
    cats = update_categories_file(lib_path, FILE_CFG["categories_file"])
    new_cats = set(cats) - old_cats
    
    print(f"🔄 分类目录已同步更新，当前书库有 {len(cats)} 个真实分类。")
    if new_cats:
        print(f"🆕 发现了 {len(new_cats)} 个新分类：")
        for c in new_cats:
            print(f"  - {c}")
    else:
        print("ℹ️ 本次归档没有产生新的分类。")

    # 生成 Markdown 清单
    if moved_records_by_cat:
        report_file = "sort_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# 📚 电子书归档报告\n\n")
            if new_cats:
                f.write(f"## 🆕 新增了 {len(new_cats)} 个独立分类\n")
                for c in sorted(list(new_cats)):
                    f.write(f"- `{c}`\n")
                f.write("\n")
            f.write("## 📦 书籍移动明细\n")
            for cat in sorted(moved_records_by_cat.keys()):
                f.write(f"### 📂 {cat}\n")
                for book in sorted(moved_records_by_cat[cat]):
                    f.write(f"- **{book}**\n")
                f.write("\n")
        print(f"📄 已生成详细的归档清单文件：{report_file}")

    # 清理垃圾
    print("🧹 正在清理 Inbox 暂存任务文件...")
    for tmp in [FILE_CFG["ai_input"], FILE_CFG["ai_output"], FILE_CFG["local_map"]]:
        tmp_path = Path(tmp)
        if tmp_path.exists():
            tmp_path.unlink()
            
    print("✨ 执行完毕！")

if __name__ == "__main__":
    main()
