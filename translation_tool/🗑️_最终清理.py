#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终清理 - 只保留核心文件
"""

import os
from pathlib import Path

def final_cleanup():
    """最终清理，只保留核心文件"""
    print("🗑️ 最终清理 - 只保留核心文件")
    print("=" * 50)
    
    current_dir = Path(__file__).parent
    
    # 绝对必须保留的文件
    keep_files = {
        "智能分类翻译器.py",
        "anki_connect.py", 
        "anki_exporter.py",
        "requirements.txt",
        "🧠_启动智能分类翻译器.sh",
        "🧠_智能分类翻译器使用指南.md",
        "🎉_智能翻译器AnkiConnect升级完成.md",
        "🔧_翻译导入时序问题修复.md",
        "🔧_翻译输出一致性修复.md",
        "🎨_界面优化调整说明.md",
        "🎉_翻译工具最终清理完成.md",
        "dictionaries",
        "__pycache__",
        "🗑️_最终清理.py"
    }
    
    deleted_count = 0
    kept_count = 0
    
    for item in current_dir.iterdir():
        if item.name in keep_files:
            print(f"✅ 保留: {item.name}")
            kept_count += 1
        else:
            try:
                if item.is_file():
                    item.unlink()
                    print(f"🗑️ 删除: {item.name}")
                    deleted_count += 1
                elif item.is_dir() and item.name not in keep_files:
                    import shutil
                    shutil.rmtree(item)
                    print(f"🗑️ 删除目录: {item.name}")
                    deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {item.name}: {e}")
    
    print(f"\n📊 清理完成: 保留 {kept_count} 个，删除 {deleted_count} 个")
    
    # 创建简化的使用说明
    create_simple_guide()

def create_simple_guide():
    """创建简化的使用说明"""
    guide_content = """# 🧠 智能分类翻译器 - 简化版

## 🚀 快速启动

```bash
cd translation_tool
./🧠_启动智能分类翻译器.sh
```

或者：

```bash
cd translation_tool
python3 智能分类翻译器.py
```

## ✨ 主要功能

- 🧠 **智能分类**: 自动识别单词、短语、句子
- 📚 **词典查询**: 提供音标、释义、例句
- 🔄 **智能翻译**: 中英文双向翻译
- ⚡ **一键导入**: 翻译+导入Anki一步完成
- 🎯 **自动导入**: 直接导入到"阅读中的收获"牌组

## 🎯 使用方法

1. **启动程序**
2. **输入单词或句子**
3. **选择功能**:
   - 🧠 智能翻译 - 查看翻译结果
   - ⚡ 翻译+导入 - 翻译并自动导入Anki

## 📋 前提条件

- Python 3.x
- Anki软件已打开
- AnkiConnect插件已安装

---

现在目录已经清理完毕，只保留核心功能！
"""
    
    with open("🚀_使用指南.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("✅ 创建简化使用指南")

if __name__ == "__main__":
    final_cleanup()