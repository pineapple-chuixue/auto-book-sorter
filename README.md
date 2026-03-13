# 📚 AI Book Sorter (AI 电子书半自动归类流水线)

大道至简。这是一个轻量级、零成本、无门槛的本地电子书分类工具。
无需繁琐的 API Key 配置，无需折腾本地大模型部署。利用文件提取脚本 + 网页版大语言模型（如 ChatGPT / DeepSeek / Kimi）的推理能力，帮你瞬间将杂乱无章的电子书按多级目录整理得井井有条。

## ✨ 核心特性

- **高度解耦**：所有路径配置抽离于 `config.json`，开箱即用。
- **正则预清洗**：自动剔除 Z-Library 等杂乱的文件名后缀，仅提取纯净书名。
- **无缝衔接**：自动生成 AI Prompt 并写入系统剪贴板（Windows），即粘即用。
- **字典自生长**：AI 若生成了全新的分类路径，脚本会自动收录并更新本地 `my_categories.json`。
- **阅后即焚**：归档完成后自动清理临时 JSON 映射文件，保持目录整洁。

## 🚀 快速开始

### 1. 基础配置
克隆本仓库后，修改 `config.json` 中的路径为你电脑上的实际物理路径：
- `unorganized_dir`: 存量杂乱书籍所在的旧文件夹（仅首次批量处理使用）
- `inbox_dir`: 你的日常收件箱（以后新下载的书丢这里）
- `library_dir`: 你整理好的主书库（脚本会自动在这里建多级文件夹）

### 2. 存量书籍大清扫（仅需一次）
如果你有几百本历史遗留电子书，按以下顺序执行：
1. 运行 `python extract_books.py` 提取所有书名并生成 `inbox_for_ai.json`。
2. 将书名发给 AI 进行分类（参考终端输出的 Prompt），将 AI 返回的结果保存为 `inbox_categorized.json`到本目录下。
3. 运行 `python move_books.py`，脚本会自动在主书架创建文件夹并转移书籍。
4. 运行 `python get_categories.py`，提取你现有的分类树，生成字典。

### 3. 日常 Inbox 流水线（高频使用）
平时下载了新书，直接扔进配置好的 `inbox_dir` 文件夹，然后运行：
```bash
python inbox_workflow.py
```
输入 1：自动扫描新书，提取书名，并将带有当前分类字典的 Prompt 自动复制到剪贴板。

去你喜欢的网页版 AI 粘贴对话，将结果贴进 inbox_categorized.json。

输入 2：脚本自动将书移入书库对应的细分目录，更新本地字典，并自动销毁临时文件。

🛠️ 环境要求
Python 3.6+

仅使用了 Python 标准库 (json, re, shutil, subprocess, pathlib)，无需 pip install 任何第三方包。