#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能分类翻译器 - 升级版
根据输入内容自动分类：词典查询 vs 短句翻译
支持一键生成Anki卡片并自动导入到Anki
集成AnkiConnect自动导入功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import re
import threading
import os
from datetime import datetime
from pathlib import Path
from anki_connect import AnkiConnect

class SmartTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📚 Books Anki 智能翻译器 - 升级版")
        self.root.geometry("900x800")
        self.root.configure(bg="white")
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # 词卡数据存储
        self.cards_data = []
        self.current_translation = None
        
        # 自动导入标志
        self.auto_import_after_translation = False
        
        # 初始化AnkiConnect
        self.setup_anki_connect()
        
        # 设置Anki文件夹
        self.setup_anki_folder()
        
        # 设置界面
        self.setup_ui()
        
        print("✅ 智能分类翻译器升级版初始化完成")
        
    def setup_anki_connect(self):
        """初始化AnkiConnect连接"""
        try:
            self.anki = AnkiConnect(
                api_key="MY_SECRET_KEY_123",
                host="127.0.0.1", 
                port=8765
            )
            
            # 测试连接
            success, message = self.anki.test_connection()
            if success:
                print(f"✅ AnkiConnect连接成功: {message}")
                self.anki_connected = True
                
                # 确保"阅读中的收获"牌组存在
                decks = self.anki.get_deck_names()
                if "阅读中的收获" not in decks:
                    success, msg = self.anki.create_deck("阅读中的收获")
                    if success:
                        print(f"✅ 创建牌组: {msg}")
                    else:
                        print(f"⚠️ 创建牌组失败: {msg}")
            else:
                print(f"⚠️ AnkiConnect连接失败: {message}")
                self.anki_connected = False
        except Exception as e:
            print(f"⚠️ AnkiConnect初始化失败: {e}")
            self.anki_connected = False
    
    def setup_anki_folder(self):
        """设置Anki卡片保存文件夹"""
        desktop_path = Path.home() / "Desktop"
        self.anki_folder = desktop_path / "智能翻译Anki卡片"
        self.anki_folder.mkdir(exist_ok=True)
        print(f"📁 Anki卡片保存路径: {self.anki_folder}")
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_container, 
                              text="📚 Books Anki 智能翻译器", 
                              font=("Arial", 18, "bold"),
                              bg="white", fg="darkblue")
        title_label.pack(pady=(0, 10))
        
        # 说明文字
        desc_label = tk.Label(main_container,
                             text="📚 专为Books阅读优化 | 智能识别：单词→词典查询 | 短句→翻译处理 | 一键生成Anki卡片",
                             font=("Arial", 11),
                             bg="white", fg="gray")
        desc_label.pack(pady=(0, 15))
        
        # AnkiConnect状态显示
        anki_status_frame = tk.Frame(main_container, bg="white")
        anki_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        anki_status_text = "🔗 AnkiConnect已连接 - 自动导入到「阅读中的收获」" if self.anki_connected else "⚠️ AnkiConnect未连接 - 仅保存到文件"
        anki_status_color = "darkgreen" if self.anki_connected else "darkorange"
        
        self.anki_status_label = tk.Label(anki_status_frame,
                                         text=anki_status_text,
                                         font=("Arial", 11, "bold"),
                                         bg="lightgreen" if self.anki_connected else "lightyellow", 
                                         fg=anki_status_color)
        self.anki_status_label.pack(pady=5)
        
        # Books使用提示
        books_tip_label = tk.Label(main_container,
                                  text="💡 使用技巧：在Books中复制文本，然后在此处翻译并制作Anki卡片",
                                  font=("Arial", 10),
                                  bg="lightyellow", fg="darkorange")
        books_tip_label.pack(pady=(0, 15))
        
        # 输入区域
        input_frame = tk.LabelFrame(main_container, text="📝 输入内容", 
                                   font=("Arial", 12, "bold"), 
                                   bg="white", fg="darkgreen")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 输入框容器
        input_container = tk.Frame(input_frame, bg="white")
        input_container.pack(fill=tk.X, padx=15, pady=15)
        
        # 调整输入框大小，不再填充整个宽度
        self.input_entry = tk.Entry(input_container, font=("Arial", 14), width=35)
        self.input_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.input_entry.bind('<Return>', self.smart_translate)
        
        # 按钮容器 - 增加按钮大小和间距
        button_container = tk.Frame(input_container, bg="white")
        button_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 粘贴按钮
        paste_btn = tk.Button(button_container, text="📋 粘贴", 
                             command=self.paste_from_clipboard,
                             font=("Arial", 11, "bold"),
                             bg="lightgreen", fg="darkgreen",
                             relief="raised", bd=2,
                             width=8)
        paste_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 智能翻译按钮
        translate_btn = tk.Button(button_container, text="🧠 智能翻译", 
                                command=self.smart_translate,
                                font=("Arial", 12, "bold"),
                                bg="lightblue", fg="darkblue",
                                relief="raised", bd=2,
                                width=12)
        translate_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 翻译+导入按钮 - 加大尺寸，使用更显眼的颜色
        auto_import_btn = tk.Button(button_container, text="⚡ 翻译+导入", 
                                   command=self.translate_and_import,
                                   font=("Arial", 13, "bold"),
                                   bg="orange", fg="white",
                                   relief="raised", bd=3,
                                   width=12)
        auto_import_btn.pack(side=tk.LEFT)
        
        # 分类显示区域
        self.category_frame = tk.Frame(main_container, bg="white")
        self.category_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.category_label = tk.Label(self.category_frame,
                                      text="",
                                      font=("Arial", 11, "bold"),
                                      bg="white")
        self.category_label.pack()
        
        # 翻译结果区域
        result_frame = tk.LabelFrame(main_container, text="📖 翻译结果", 
                                   font=("Arial", 12, "bold"), 
                                   bg="white", fg="darkgreen")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 结果文本框
        self.result_text = tk.Text(result_frame, height=15, 
                                  font=("Arial", 11), 
                                  bg="lightyellow",
                                  wrap=tk.WORD,
                                  relief="sunken", bd=2)
        
        # 滚动条
        scrollbar = tk.Scrollbar(result_frame, orient="vertical", 
                               command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=15)
        
        # 按钮区域
        button_frame = tk.Frame(main_container, bg="white")
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        add_card_btn = tk.Button(button_frame, text="📚 添加到Anki", 
                               command=self.add_to_anki,
                               font=("Arial", 11, "bold"),
                               bg="lightgreen", fg="darkgreen",
                               relief="raised", bd=2)
        add_card_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # AnkiConnect重连按钮
        reconnect_btn = tk.Button(button_frame, text="🔄 重连Anki", 
                                command=self.reconnect_anki,
                                font=("Arial", 10, "bold"),
                                bg="lightcyan", fg="darkblue",
                                relief="raised", bd=2)
        reconnect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = tk.Button(button_frame, text="💾 导出Anki卡片", 
                             command=self.export_anki,
                             font=("Arial", 11, "bold"),
                             bg="lightsalmon", fg="darkred",
                             relief="raised", bd=2)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(button_frame, text="🗑️ 清空卡片", 
                            command=self.clear_cards,
                            font=("Arial", 11, "bold"),
                            bg="lightgray", fg="black",
                            relief="raised", bd=2)
        clear_btn.pack(side=tk.LEFT)
        
        # 词卡计数
        self.cards_count_label = tk.Label(button_frame,
                                         text=f"词卡数量: {len(self.cards_data)}",
                                         font=("Arial", 11),
                                         bg="white", fg="blue")
        self.cards_count_label.pack(side=tk.RIGHT)
        
        # 初始化显示
        self.show_welcome_message()
        
    def paste_from_clipboard(self):
        """从剪贴板粘贴内容"""
        try:
            # 使用AppleScript获取剪贴板内容
            import subprocess
            script = '''
            tell application "System Events"
                set clipboardContent to the clipboard
                return clipboardContent
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                clipboard_text = result.stdout.strip()
                if clipboard_text:
                    self.input_entry.delete(0, tk.END)
                    self.input_entry.insert(0, clipboard_text)
                    # 检查是否来自Books
                    if self.is_books_active():
                        self.show_books_tip()
                else:
                    messagebox.showinfo("提示", "剪贴板为空")
            else:
                messagebox.showwarning("错误", "无法获取剪贴板内容")
        except Exception as e:
            messagebox.showerror("错误", f"粘贴失败: {str(e)}")
    
    def is_books_active(self):
        """检查Books应用是否最近处于活动状态"""
        try:
            import subprocess
            script = '''
            tell application "System Events"
                set recentApps to name of every application process
                return recentApps
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return "Books" in result.stdout
        except:
            return False
    
    def show_books_tip(self):
        """显示Books使用提示"""
        self.category_label.configure(
            text="📚 检测到来自Books的内容，正在为阅读学习优化...",
            fg="green"
        )
        
    def show_welcome_message(self):
        """显示欢迎信息"""
        self.result_text.insert(tk.END, "🎉 欢迎使用 Books Anki 智能翻译器！\n\n")
        self.result_text.insert(tk.END, "📚 专为 Books 阅读优化的翻译工具\n\n")
        self.result_text.insert(tk.END, "🔥 Books 使用流程:\n")
        self.result_text.insert(tk.END, "   1. 在 Books 中选中要翻译的文本\n")
        self.result_text.insert(tk.END, "   2. 按 Cmd+C 复制文本\n")
        self.result_text.insert(tk.END, "   3. 点击 '📋 粘贴' 按钮\n")
        self.result_text.insert(tk.END, "   4. 点击 '🧠 智能翻译' 获取结果\n")
        self.result_text.insert(tk.END, "   5. 点击 '📚 添加到Anki' 制作卡片\n\n")
        self.result_text.insert(tk.END, "🧠 智能分类功能:\n")
        self.result_text.insert(tk.END, "   • 单个单词 → 词典查询（音标、释义、例句）\n")
        self.result_text.insert(tk.END, "   • 短语句子 → 翻译处理（中英互译）\n")
        self.result_text.insert(tk.END, "   • 自动识别语言和内容类型\n\n")
        self.result_text.insert(tk.END, "📚 Anki卡片功能:\n")
        self.result_text.insert(tk.END, "   • 一键添加到Anki卡片库\n")
        self.result_text.insert(tk.END, "   • 支持词典和翻译两种卡片格式\n")
        self.result_text.insert(tk.END, "   • 自动生成导入文件和说明\n")
        self.result_text.insert(tk.END, f"   • 文件保存位置: {self.anki_folder}\n\n")
        self.result_text.insert(tk.END, "✨ 使用示例:\n")
        self.result_text.insert(tk.END, "   • 输入 'hello' → 词典查询\n")
        self.result_text.insert(tk.END, "   • 输入 'How are you?' → 句子翻译\n")
        self.result_text.insert(tk.END, "   • 输入 '你好吗' → 中译英\n\n")
        self.result_text.insert(tk.END, "🚀 现在就在 Books 中复制文本开始翻译吧！")
        
    def classify_input(self, text):
        """智能分类输入内容"""
        text = text.strip()
        
        # 检查是否为空
        if not text:
            return "empty", {}
        
        # 检查是否包含中文
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        
        # 检查单词数量
        words = text.split()
        word_count = len(words)
        
        # 检查是否包含标点符号
        has_punctuation = bool(re.search(r'[.!?;:,，。！？；：]', text))
        
        # 分类逻辑
        if has_chinese:
            if word_count <= 2 and not has_punctuation:
                return "chinese_word", {"type": "词汇", "language": "中文"}
            else:
                return "chinese_sentence", {"type": "句子", "language": "中文"}
        else:
            if word_count == 1 and not has_punctuation and text.isalpha():
                return "english_word", {"type": "单词", "language": "英文"}
            elif word_count <= 3 and not has_punctuation:
                return "english_phrase", {"type": "短语", "language": "英文"}
            else:
                return "english_sentence", {"type": "句子", "language": "英文"}
    
    def smart_translate(self, event=None):
        """智能翻译主函数"""
        text = self.input_entry.get().strip()
        if not text:
            messagebox.showwarning("提示", "请输入要翻译的内容")
            return
        
        # 分类输入内容
        category, info = self.classify_input(text)
        
        # 显示分类结果
        if category != "empty":
            category_text = f"🏷️ 识别类型: {info['type']} ({info['language']})"
            self.category_label.configure(text=category_text, fg="blue")
        
        # 显示加载状态
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"🔍 正在处理 '{text}'，请稍候...\n")
        self.root.update()
        
        # 在新线程中执行翻译
        threading.Thread(target=self._do_smart_translation, 
                        args=(text, category, info), daemon=True).start()
    
    def _do_smart_translation(self, text, category, info):
        """执行智能翻译（在后台线程中）"""
        try:
            if category == "english_word":
                # 英文单词 → 词典查询
                result = self.dictionary_lookup(text)
            elif category in ["english_phrase", "english_sentence"]:
                # 英文短语/句子 → 英译中
                result = self.translate_text(text, "en", "zh")
            elif category in ["chinese_word", "chinese_sentence"]:
                # 中文内容 → 中译英
                result = self.translate_text(text, "zh", "en")
            else:
                result = None
            
            if result:
                self.current_translation = {
                    'input': text,
                    'category': category,
                    'info': info,
                    'result': result
                }
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.display_result(result, category, info))
                
                # 检查是否需要自动导入
                if self.auto_import_after_translation:
                    self.auto_import_after_translation = False  # 重置标志
                    # 显示翻译完成，准备导入
                    self.root.after(100, self._show_import_status)
                    # 延迟足够时间让用户看到翻译结果，然后自动导入
                    self.root.after(1500, self.add_to_anki)
            else:
                self.auto_import_after_translation = False  # 重置标志
                self.root.after(0, lambda: self.show_error("处理失败，请检查网络连接或稍后重试"))
                
        except Exception as e:
            self.auto_import_after_translation = False  # 重置标志
            self.root.after(0, lambda: self.show_error(f"处理出错: {str(e)}"))
    
    def _show_import_status(self):
        """显示即将导入的状态"""
        if self.current_translation:
            # 在翻译结果后添加导入提示，不覆盖原有内容
            self.result_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.result_text.insert(tk.END, "⚡ 翻译+导入模式激活\n", "header")
            self.result_text.insert(tk.END, "📚 即将自动导入到Anki...\n", "note")
            self.result_text.insert(tk.END, "🎯 目标牌组: 阅读中的收获\n", "note")
            self.result_text.insert(tk.END, "⏰ 请稍候...\n", "note")
            self.root.update()
    
    def dictionary_lookup(self, word):
        """词典查询功能"""
        # 首先尝试本地词典
        local_result = self.get_local_dictionary(word)
        if local_result and local_result.get('found'):
            return local_result
        
        # 尝试在线词典API
        online_result = self.get_online_dictionary(word)
        if online_result:
            return online_result
        
        # 如果词典查询失败，尝试翻译
        translation_result = self.translate_text(word, "en", "zh")
        if translation_result:
            return {
                'type': 'translation_fallback',
                'word': word,
                'translation': translation_result.get('translation', ''),
                'phonetic': '',
                'definitions': [],
                'examples': []
            }
        
        return None
    
    def get_local_dictionary(self, word):
        """本地词典查询"""
        local_dict = {
            'hello': {
                'phonetic': '/həˈloʊ/',
                'definitions': [
                    {'pos': 'int.', 'def': '你好；喂（用于问候或引起注意）'},
                    {'pos': 'n.', 'def': '问候；招呼'}
                ],
                'examples': [
                    'Hello, how are you? 你好，你好吗？',
                    'She said hello to everyone. 她向每个人问好。'
                ]
            },
            'world': {
                'phonetic': '/wɜːrld/',
                'definitions': [
                    {'pos': 'n.', 'def': '世界；地球'},
                    {'pos': 'n.', 'def': '领域；界'}
                ],
                'examples': [
                    'Welcome to the world! 欢迎来到这个世界！',
                    'The business world is competitive. 商业世界竞争激烈。'
                ]
            },
            'computer': {
                'phonetic': '/kəmˈpjuːtər/',
                'definitions': [
                    {'pos': 'n.', 'def': '计算机；电脑'}
                ],
                'examples': [
                    'I use a computer for work. 我用电脑工作。'
                ]
            },
            'study': {
                'phonetic': '/ˈstʌdi/',
                'definitions': [
                    {'pos': 'v.', 'def': '学习；研究'},
                    {'pos': 'n.', 'def': '学习；研究；书房'}
                ],
                'examples': [
                    'I study English every day. 我每天学习英语。',
                    'This study shows interesting results. 这项研究显示了有趣的结果。'
                ]
            },
            'translate': {
                'phonetic': '/trænsˈleɪt/',
                'definitions': [
                    {'pos': 'v.', 'def': '翻译；转换'}
                ],
                'examples': [
                    'Can you translate this sentence? 你能翻译这个句子吗？'
                ]
            },
            'book': {
                'phonetic': '/bʊk/',
                'definitions': [
                    {'pos': 'n.', 'def': '书；书籍'},
                    {'pos': 'v.', 'def': '预订；预约'}
                ],
                'examples': [
                    'This is a good book. 这是一本好书。',
                    'I need to book a hotel. 我需要预订酒店。'
                ]
            },
            'learn': {
                'phonetic': '/lɜːrn/',
                'definitions': [
                    {'pos': 'v.', 'def': '学习；学会；了解'}
                ],
                'examples': [
                    'I want to learn Chinese. 我想学中文。',
                    'Children learn quickly. 孩子们学得很快。'
                ]
            },
            'language': {
                'phonetic': '/ˈlæŋɡwɪdʒ/',
                'definitions': [
                    {'pos': 'n.', 'def': '语言；语言文字'}
                ],
                'examples': [
                    'English is a global language. 英语是全球语言。',
                    'Body language is important. 肢体语言很重要。'
                ]
            },
            'work': {
                'phonetic': '/wɜːrk/',
                'definitions': [
                    {'pos': 'v.', 'def': '工作；运转；起作用'},
                    {'pos': 'n.', 'def': '工作；职业；作品'}
                ],
                'examples': [
                    'I work in an office. 我在办公室工作。',
                    'This method works well. 这个方法很有效。'
                ]
            },
            'time': {
                'phonetic': '/taɪm/',
                'definitions': [
                    {'pos': 'n.', 'def': '时间；时刻；次数'},
                    {'pos': 'v.', 'def': '计时；安排时间'}
                ],
                'examples': [
                    'What time is it? 现在几点了？',
                    'Time flies quickly. 时间过得很快。'
                ]
            },
            'good': {
                'phonetic': '/ɡʊd/',
                'definitions': [
                    {'pos': 'adj.', 'def': '好的；良好的；善良的'},
                    {'pos': 'n.', 'def': '好处；利益'}
                ],
                'examples': [
                    'This is a good idea. 这是个好主意。',
                    'Good morning! 早上好！'
                ]
            },
            'morning': {
                'phonetic': '/ˈmɔːrnɪŋ/',
                'definitions': [
                    {'pos': 'n.', 'def': '早晨；上午'}
                ],
                'examples': [
                    'Good morning! 早上好！',
                    'I exercise every morning. 我每天早上锻炼。'
                ]
            },
            'thank': {
                'phonetic': '/θæŋk/',
                'definitions': [
                    {'pos': 'v.', 'def': '感谢；谢谢'}
                ],
                'examples': [
                    'Thank you very much. 非常感谢你。',
                    'I want to thank everyone. 我想感谢每个人。'
                ]
            },
            'help': {
                'phonetic': '/help/',
                'definitions': [
                    {'pos': 'v.', 'def': '帮助；协助'},
                    {'pos': 'n.', 'def': '帮助；援助'}
                ],
                'examples': [
                    'Can you help me? 你能帮我吗？',
                    'I need your help. 我需要你的帮助。'
                ]
            },
            'love': {
                'phonetic': '/lʌv/',
                'definitions': [
                    {'pos': 'v.', 'def': '爱；喜欢'},
                    {'pos': 'n.', 'def': '爱；爱情'}
                ],
                'examples': [
                    'I love you. 我爱你。',
                    'Love is beautiful. 爱是美好的。'
                ]
            },
            'apple': {
                'phonetic': '/ˈæpəl/',
                'definitions': [
                    {'pos': 'n.', 'def': '苹果；苹果公司'}
                ],
                'examples': [
                    'I eat an apple every day. 我每天吃一个苹果。'
                ]
            },
            'water': {
                'phonetic': '/ˈwɔːtər/',
                'definitions': [
                    {'pos': 'n.', 'def': '水；水域'},
                    {'pos': 'v.', 'def': '浇水；给...水喝'}
                ],
                'examples': [
                    'I drink water every day. 我每天喝水。',
                    'Please water the plants. 请给植物浇水。'
                ]
            },
            'house': {
                'phonetic': '/haʊs/',
                'definitions': [
                    {'pos': 'n.', 'def': '房子；住宅'},
                    {'pos': 'v.', 'def': '容纳；收藏'}
                ],
                'examples': [
                    'This is my house. 这是我的房子。',
                    'The library houses many books. 图书馆收藏了很多书。'
                ]
            },
            'car': {
                'phonetic': '/kɑːr/',
                'definitions': [
                    {'pos': 'n.', 'def': '汽车；车厢'}
                ],
                'examples': [
                    'I drive a car to work. 我开车上班。'
                ]
            },
            'phone': {
                'phonetic': '/foʊn/',
                'definitions': [
                    {'pos': 'n.', 'def': '电话；手机'},
                    {'pos': 'v.', 'def': '打电话'}
                ],
                'examples': [
                    'My phone is ringing. 我的手机在响。',
                    'Please phone me later. 请稍后给我打电话。'
                ]
            },
            'school': {
                'phonetic': '/skuːl/',
                'definitions': [
                    {'pos': 'n.', 'def': '学校；学院'},
                    {'pos': 'v.', 'def': '教育；训练'}
                ],
                'examples': [
                    'I go to school every day. 我每天上学。',
                    'She schools her children at home. 她在家教育孩子。'
                ]
            },
            'friend': {
                'phonetic': '/frend/',
                'definitions': [
                    {'pos': 'n.', 'def': '朋友；友人'},
                    {'pos': 'v.', 'def': '与...交友'}
                ],
                'examples': [
                    'He is my best friend. 他是我最好的朋友。',
                    'I want to friend you on social media. 我想在社交媒体上加你为好友。'
                ]
            },
            'family': {
                'phonetic': '/ˈfæməli/',
                'definitions': [
                    {'pos': 'n.', 'def': '家庭；家族'},
                    {'pos': 'adj.', 'def': '家庭的；家族的'}
                ],
                'examples': [
                    'I love my family. 我爱我的家人。',
                    'This is a family restaurant. 这是一家家庭餐厅。'
                ]
            },
            'money': {
                'phonetic': '/ˈmʌni/',
                'definitions': [
                    {'pos': 'n.', 'def': '钱；货币；财富'}
                ],
                'examples': [
                    'I need more money. 我需要更多钱。',
                    'Money can\'t buy happiness. 金钱买不到幸福。'
                ]
            },
            'food': {
                'phonetic': '/fuːd/',
                'definitions': [
                    {'pos': 'n.', 'def': '食物；食品；养料'}
                ],
                'examples': [
                    'I like Chinese food. 我喜欢中国菜。',
                    'Food is essential for life. 食物是生命必需的。'
                ]
            },
            'music': {
                'phonetic': '/ˈmjuːzɪk/',
                'definitions': [
                    {'pos': 'n.', 'def': '音乐；乐曲'}
                ],
                'examples': [
                    'I love listening to music. 我喜欢听音乐。',
                    'She studies music at university. 她在大学学习音乐。'
                ]
            },
            'movie': {
                'phonetic': '/ˈmuːvi/',
                'definitions': [
                    {'pos': 'n.', 'def': '电影；影片'}
                ],
                'examples': [
                    'Let\'s watch a movie tonight. 我们今晚看电影吧。',
                    'This movie is very interesting. 这部电影很有趣。'
                ]
            },
            'game': {
                'phonetic': '/ɡeɪm/',
                'definitions': [
                    {'pos': 'n.', 'def': '游戏；比赛；猎物'},
                    {'pos': 'v.', 'def': '赌博；玩游戏'}
                ],
                'examples': [
                    'Let\'s play a game. 我们来玩个游戏吧。',
                    'The football game was exciting. 足球比赛很精彩。'
                ]
            },
            'internet': {
                'phonetic': '/ˈɪntərnet/',
                'definitions': [
                    {'pos': 'n.', 'def': '互联网；因特网'}
                ],
                'examples': [
                    'I use the internet every day. 我每天使用互联网。',
                    'The internet has changed our lives. 互联网改变了我们的生活。'
                ]
            }
        }
        
        word_lower = word.lower()
        if word_lower in local_dict:
            data = local_dict[word_lower]
            return {
                'type': 'dictionary',
                'found': True,
                'word': word,
                'phonetic': data['phonetic'],
                'definitions': data['definitions'],
                'examples': data['examples']
            }
        
        return {'found': False}
    
    def get_online_dictionary(self, word):
        """多接口在线词典查询"""
        # 尝试多个词典API，提高查询成功率
        apis = [
            self.query_wordnik_api,
            self.query_dictionaryapi_dev,
            self.query_words_api,
            self.query_collins_api,
            self.query_merriam_webster_api
        ]
        
        for api_func in apis:
            try:
                result = api_func(word)
                if result:
                    print(f"✅ 词典查询成功: {api_func.__name__}")
                    return result
            except Exception as e:
                print(f"❌ {api_func.__name__} 查询失败: {e}")
                continue
        
        print(f"❌ 所有词典API查询失败: {word}")
        return None
    
    def query_wordnik_api(self, word):
        """Wordnik API查询"""
        try:
            # Wordnik API (免费，但需要API key，这里使用公开的demo key)
            base_url = "https://api.wordnik.com/v4/word.json"
            api_key = "a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5"  # 公开demo key
            
            # 获取定义
            def_url = f"{base_url}/{word}/definitions"
            def_params = {
                'limit': 5,
                'includeRelated': 'false',
                'useCanonical': 'true',
                'includeTags': 'false',
                'api_key': api_key
            }
            
            def_response = self.session.get(def_url, params=def_params, timeout=5)
            
            if def_response.status_code == 200:
                definitions_data = def_response.json()
                
                if definitions_data:
                    # 获取音标
                    phonetic = self.get_wordnik_pronunciation(word, api_key)
                    
                    # 处理定义
                    definitions = []
                    for def_item in definitions_data[:3]:
                        pos = def_item.get('partOfSpeech', '')
                        def_text = def_item.get('text', '')
                        if def_text:
                            # 翻译定义为中文
                            chinese_def = self.translate_definition(def_text)
                            if chinese_def:
                                definitions.append({'pos': pos, 'def': chinese_def})
                            else:
                                definitions.append({'pos': pos, 'def': def_text})
                    
                    # 获取例句
                    examples = self.get_wordnik_examples(word, api_key)
                    
                    return {
                        'type': 'dictionary',
                        'word': word,
                        'phonetic': phonetic,
                        'definitions': definitions,
                        'examples': examples
                    }
        except Exception as e:
            print(f"Wordnik API查询失败: {e}")
        
        return None
    
    def get_wordnik_pronunciation(self, word, api_key):
        """获取Wordnik音标"""
        try:
            pron_url = f"https://api.wordnik.com/v4/word.json/{word}/pronunciations"
            pron_params = {
                'useCanonical': 'true',
                'limit': 1,
                'api_key': api_key
            }
            
            pron_response = self.session.get(pron_url, params=pron_params, timeout=3)
            if pron_response.status_code == 200:
                pron_data = pron_response.json()
                if pron_data and len(pron_data) > 0:
                    raw_pronunciation = pron_data[0].get('raw', '')
                    if raw_pronunciation:
                        return f"/{raw_pronunciation}/"
        except:
            pass
        return ''
    
    def get_wordnik_examples(self, word, api_key):
        """获取Wordnik例句"""
        try:
            ex_url = f"https://api.wordnik.com/v4/word.json/{word}/examples"
            ex_params = {
                'includeDuplicates': 'false',
                'useCanonical': 'true',
                'limit': 3,
                'api_key': api_key
            }
            
            ex_response = self.session.get(ex_url, params=ex_params, timeout=3)
            if ex_response.status_code == 200:
                ex_data = ex_response.json()
                examples = []
                if ex_data and 'examples' in ex_data:
                    for ex in ex_data['examples'][:2]:
                        text = ex.get('text', '')
                        if text and len(text) < 200:  # 限制例句长度
                            # 翻译例句
                            chinese_ex = self.translate_example(text)
                            if chinese_ex:
                                examples.append(f"{text} {chinese_ex}")
                            else:
                                examples.append(text)
                return examples
        except:
            pass
        return []
    
    def query_dictionaryapi_dev(self, word):
        """DictionaryAPI.dev查询（原有接口）"""
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    entry = data[0]
                    
                    # 提取音标
                    phonetic = ''
                    if 'phonetics' in entry:
                        for p in entry['phonetics']:
                            if 'text' in p and p['text']:
                                phonetic = p['text']
                                break
                    
                    # 提取定义和例句
                    definitions = []
                    examples = []
                    
                    if 'meanings' in entry:
                        for meaning in entry['meanings'][:3]:
                            pos = meaning.get('partOfSpeech', '')
                            for definition in meaning.get('definitions', [])[:2]:
                                def_text = definition.get('definition', '')
                                if def_text:
                                    chinese_def = self.translate_definition(def_text)
                                    if chinese_def:
                                        definitions.append({'pos': pos, 'def': chinese_def})
                                    else:
                                        definitions.append({'pos': pos, 'def': def_text})
                                
                                example = definition.get('example', '')
                                if example and len(examples) < 3:
                                    chinese_example = self.translate_example(example)
                                    if chinese_example:
                                        examples.append(f"{example} {chinese_example}")
                                    else:
                                        examples.append(example)
                    
                    return {
                        'type': 'dictionary',
                        'word': word,
                        'phonetic': phonetic,
                        'definitions': definitions,
                        'examples': examples
                    }
        except Exception as e:
            print(f"DictionaryAPI.dev查询失败: {e}")
        
        return None
    
    def query_words_api(self, word):
        """Words API查询"""
        try:
            # Words API (RapidAPI)
            url = f"https://wordsapiv1.p.rapidapi.com/words/{word}"
            headers = {
                "X-RapidAPI-Key": "demo-key",  # 需要替换为实际的API key
                "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
            }
            
            # 由于需要API key，这里提供基础实现框架
            # 实际使用时需要注册获取API key
            return None
            
        except Exception as e:
            print(f"Words API查询失败: {e}")
        
        return None
    
    def query_collins_api(self, word):
        """Collins Dictionary API查询"""
        try:
            # Collins Dictionary API需要注册获取API key
            # 这里提供基础实现框架
            return None
            
        except Exception as e:
            print(f"Collins API查询失败: {e}")
        
        return None
    
    def query_merriam_webster_api(self, word):
        """Merriam-Webster API查询"""
        try:
            # Merriam-Webster API需要注册获取API key
            # 这里提供基础实现框架
            return None
            
        except Exception as e:
            print(f"Merriam-Webster API查询失败: {e}")
        
        return None
    
    def translate_definition(self, definition):
        """翻译英文定义为中文"""
        try:
            # 使用简单的翻译API
            translation = self.translate_with_mymemory(definition, 'en', 'zh')
            if translation and len(translation) > 0:
                return translation
        except:
            pass
        return None
    
    def translate_example(self, example):
        """翻译例句为中文"""
        try:
            # 使用简单的翻译API
            translation = self.translate_with_mymemory(example, 'en', 'zh')
            if translation and len(translation) > 0:
                return f"({translation})"
        except:
            pass
        return None
    
    def translate_text(self, text, source_lang, target_lang):
        """文本翻译功能"""
        # 尝试多个翻译API
        translation = None
        
        # 1. 尝试MyMemory API
        translation = self.translate_with_mymemory(text, source_lang, target_lang)
        
        # 2. 如果失败，尝试其他API或本地翻译
        if not translation:
            translation = self.translate_with_fallback(text, source_lang, target_lang)
        
        if translation:
            return {
                'type': 'translation',
                'original': text,
                'translation': translation,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
        
        return None
    
    def translate_with_mymemory(self, text, source_lang, target_lang):
        """使用MyMemory API翻译"""
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}'
            }
            
            response = self.session.get(url, params=params, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if 'responseData' in data and 'translatedText' in data['responseData']:
                    translation = data['responseData']['translatedText']
                    if translation and not translation.upper().startswith("MYMEMORY WARNING"):
                        return translation
        except Exception as e:
            print(f"MyMemory翻译失败: {e}")
        
        return None
    
    def translate_with_fallback(self, text, source_lang, target_lang):
        """备用翻译方法"""
        # 简单的本地翻译示例
        simple_translations = {
            'hello': '你好',
            'world': '世界',
            'how are you': '你好吗',
            'thank you': '谢谢',
            'good morning': '早上好',
            'good night': '晚安',
            '你好': 'hello',
            '世界': 'world',
            '谢谢': 'thank you',
            '早上好': 'good morning',
            '晚安': 'good night'
        }
        
        text_lower = text.lower()
        if text_lower in simple_translations:
            return simple_translations[text_lower]
        
        return f"[翻译服务暂时不可用，原文: {text}]"    

    def display_result(self, result, category, info):
        """显示翻译结果"""
        self.result_text.delete(1.0, tk.END)
        
        if result['type'] == 'dictionary':
            self.display_dictionary_result(result)
        elif result['type'] == 'translation':
            self.display_translation_result(result)
        elif result['type'] == 'translation_fallback':
            self.display_fallback_result(result)
    
    def display_dictionary_result(self, result):
        """显示词典查询结果"""
        word = result['word']
        phonetic = result.get('phonetic', '')
        definitions = result.get('definitions', [])
        examples = result.get('examples', [])
        
        # 显示单词
        self.result_text.insert(tk.END, f"📝 单词: {word}\n", "word")
        
        # 显示音标
        if phonetic:
            self.result_text.insert(tk.END, f"🔊 音标: {phonetic}\n\n", "phonetic")
        else:
            self.result_text.insert(tk.END, "\n")
        
        # 显示释义
        if definitions:
            self.result_text.insert(tk.END, "📚 释义:\n", "header")
            for i, def_item in enumerate(definitions, 1):
                pos = def_item.get('pos', '')
                definition = def_item.get('def', '')
                if pos:
                    self.result_text.insert(tk.END, f"   {i}. {pos} {definition}\n")
                else:
                    self.result_text.insert(tk.END, f"   {i}. {definition}\n")
            self.result_text.insert(tk.END, "\n")
        
        # 显示例句
        if examples:
            self.result_text.insert(tk.END, "💬 例句:\n", "header")
            for i, example in enumerate(examples, 1):
                self.result_text.insert(tk.END, f"   {i}. {example}\n")
        
        # 配置文本样式
        self.configure_text_styles()
    
    def display_translation_result(self, result):
        """显示翻译结果"""
        original = result['original']
        translation = result['translation']
        source_lang = result['source_lang']
        target_lang = result['target_lang']
        
        # 语言标识
        lang_map = {'en': '英文', 'zh': '中文'}
        source_name = lang_map.get(source_lang, source_lang)
        target_name = lang_map.get(target_lang, target_lang)
        
        self.result_text.insert(tk.END, f"🌐 翻译结果 ({source_name} → {target_name})\n\n", "header")
        
        # 显示原文
        self.result_text.insert(tk.END, f"📝 原文: {original}\n", "original")
        
        # 显示译文
        self.result_text.insert(tk.END, f"📖 译文: {translation}\n", "translation")
        
        # 配置文本样式
        self.configure_text_styles()
    
    def display_fallback_result(self, result):
        """显示备用翻译结果"""
        word = result['word']
        translation = result['translation']
        
        self.result_text.insert(tk.END, f"📝 单词: {word}\n", "word")
        self.result_text.insert(tk.END, f"📖 翻译: {translation}\n\n", "translation")
        self.result_text.insert(tk.END, "💡 提示: 词典查询失败，显示基础翻译\n", "note")
        self.result_text.insert(tk.END, "建议检查网络连接以获取完整词典信息\n", "note")
        
        # 配置文本样式
        self.configure_text_styles()
    
    def configure_text_styles(self):
        """配置文本样式"""
        self.result_text.tag_configure("word", font=("Arial", 14, "bold"), foreground="darkblue")
        self.result_text.tag_configure("phonetic", font=("Arial", 12), foreground="blue")
        self.result_text.tag_configure("header", font=("Arial", 12, "bold"), foreground="darkgreen")
        self.result_text.tag_configure("original", font=("Arial", 12), foreground="darkred")
        self.result_text.tag_configure("translation", font=("Arial", 12, "bold"), foreground="darkblue")
        self.result_text.tag_configure("note", font=("Arial", 10), foreground="gray")
    
    def show_error(self, error_msg):
        """显示错误信息"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"❌ {error_msg}\n\n")
        self.result_text.insert(tk.END, "🔧 请检查:\n")
        self.result_text.insert(tk.END, "   • 网络连接是否正常\n")
        self.result_text.insert(tk.END, "   • 输入的内容是否正确\n")
        self.result_text.insert(tk.END, "   • 稍后重试\n")
    
    def add_to_anki(self):
        """添加到Anki卡片 - 自动导入到Anki或生成文件"""
        if not self.current_translation:
            messagebox.showwarning("提示", "请先进行翻译")
            return
        
        input_text = self.current_translation['input']
        category = self.current_translation['category']
        result = self.current_translation['result']
        
        # 检查是否已存在
        for card in self.cards_data:
            if card['input'].lower() == input_text.lower():
                messagebox.showinfo("提示", f"内容 '{input_text}' 已存在于卡片列表中")
                return
        
        # 创建卡片数据
        card_data = self.create_anki_card_data(input_text, category, result)
        
        # 尝试通过AnkiConnect自动导入
        if self.anki_connected:
            success = self.import_to_anki_directly(card_data)
            if success:
                self.cards_data.append(card_data)
                self.update_cards_count()
                
                word = card_data.get('word', input_text)
                messagebox.showinfo("成功", 
                                  f"✅ 已自动导入到Anki\n"
                                  f"📚 牌组: 阅读中的收获\n"
                                  f"📝 单词: {word}")
                return
            else:
                # AnkiConnect失败，回退到文件保存
                messagebox.showwarning("警告", "AnkiConnect导入失败，将保存为文件")
        
        # 生成独立的Anki卡片文件（备用方案）
        success = self.create_individual_anki_file(card_data)
        
        if success:
            self.cards_data.append(card_data)
            self.update_cards_count()
            
            word = card_data.get('word', input_text)
            messagebox.showinfo("成功", 
                              f"✅ 已为 '{word}' 生成独立Anki卡片\n"
                              f"📁 保存位置: {self.anki_folder}")
        else:
            messagebox.showerror("错误", f"生成 '{input_text}' 的Anki卡片失败")
    
    def import_to_anki_directly(self, card_data):
        """通过AnkiConnect直接导入到Anki"""
        try:
            # 格式化卡片内容
            front, back = self.format_anki_card(card_data)
            
            # 添加标签
            tags = ["智能翻译", "阅读"]
            if card_data['type'] == 'dictionary':
                tags.append("单词")
            else:
                tags.append("句子")
            
            # 导入到Anki
            success, message = self.anki.add_note(
                front=front,
                back=back,
                deck_name="阅读中的收获",
                tags=tags
            )
            
            if success:
                print(f"✅ AnkiConnect导入成功: {message}")
                return True
            else:
                print(f"❌ AnkiConnect导入失败: {message}")
                return False
                
        except Exception as e:
            print(f"❌ AnkiConnect导入异常: {e}")
            return False
    
    def translate_and_import(self):
        """一键翻译并导入到Anki - 与智能翻译完全相同的显示效果"""
        text = self.input_entry.get().strip()
        if not text:
            messagebox.showwarning("提示", "请输入要翻译的内容")
            return
        
        # 设置自动导入标志
        self.auto_import_after_translation = True
        
        # 执行完全相同的智能翻译流程（包括界面显示）
        self.smart_translate()
    
    def reconnect_anki(self):
        """重新连接AnkiConnect"""
        try:
            # 重新初始化AnkiConnect
            self.setup_anki_connect()
            
            # 更新状态显示
            anki_status_text = "🔗 AnkiConnect已连接 - 自动导入到「阅读中的收获」" if self.anki_connected else "⚠️ AnkiConnect未连接 - 仅保存到文件"
            anki_status_color = "darkgreen" if self.anki_connected else "darkorange"
            anki_bg_color = "lightgreen" if self.anki_connected else "lightyellow"
            
            self.anki_status_label.config(
                text=anki_status_text,
                fg=anki_status_color,
                bg=anki_bg_color
            )
            
            if self.anki_connected:
                messagebox.showinfo("成功", "✅ AnkiConnect重新连接成功！\n现在可以自动导入卡片到Anki")
            else:
                messagebox.showwarning("失败", "❌ AnkiConnect连接失败\n请确保Anki已打开且AnkiConnect插件已安装")
                
        except Exception as e:
            messagebox.showerror("错误", f"重连失败: {str(e)}")
    
    def create_individual_anki_file(self, card_data):
        """为单个卡片创建独立的Anki文件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            word = card_data.get('word', card_data.get('input', 'unknown'))
            safe_word = self.sanitize_filename(word)
            
            filename = self.anki_folder / f"{safe_word}_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                front, back = self.format_anki_card(card_data)
                f.write(f"{front}\t{back}\t智能翻译\n")
            
            # 创建单个卡片的导入说明
            self.create_individual_import_instructions(filename, card_data)
            
            return True
            
        except Exception as e:
            print(f"❌ 创建独立Anki文件失败: {e}")
            return False
    
    def create_individual_import_instructions(self, card_file, card_data):
        """为单个卡片创建导入说明"""
        instruction_file = card_file.parent / f"{card_file.stem}_导入说明.txt"
        
        word = card_data.get('word', card_data.get('input', ''))
        card_type = "词典卡片" if card_data['type'] == 'dictionary' else "翻译卡片"
        
        instructions = f"""🧠 智能分类翻译器 - 单词卡片导入说明

单词: {word}
卡片类型: {card_type}
文件: {card_file.name}
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚀 导入步骤:
1. 打开Anki软件
2. 点击"导入文件"或使用快捷键 Ctrl+Shift+I (Mac: Cmd+Shift+I)
3. 选择文件: {card_file.name}
4. 设置导入选项:
   - 字段分隔符: 制表符 (Tab)
   - 字段映射:
     * 字段1 → 正面 (Front)
     * 字段2 → 背面 (Back)
     * 字段3 → 标签 (Tags)
5. 选择目标牌组或创建新牌组 "智能翻译"
6. 点击"导入"完成

💡 卡片内容预览:
"""
        
        # 添加卡片内容预览
        front, back = self.format_anki_card(card_data)
        instructions += f"正面: {front}\n"
        instructions += f"背面: {back.replace('<br>', ' | ').replace('<b>', '').replace('</b>', '')}\n\n"
        
        instructions += """🎨 推荐设置:
- 牌组名称: 智能翻译
- 卡片模板: 基础模板
- 复习间隔: 根据个人情况调整

✨ 单文件优势:
- 独立管理，便于选择性学习
- 避免重复导入
- 便于分享特定单词

祝学习愉快！🎉
"""
        
        try:
            with open(instruction_file, 'w', encoding='utf-8') as f:
                f.write(instructions)
        except Exception as e:
            print(f"❌ 创建单个卡片导入说明失败: {e}")
    
    def create_anki_card_data(self, input_text, category, result):
        """创建Anki卡片数据"""
        card_data = {
            'input': input_text,
            'category': category,
            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if result['type'] == 'dictionary':
            # 词典类型卡片
            card_data.update({
                'type': 'dictionary',
                'word': result['word'],
                'phonetic': result.get('phonetic', ''),
                'definitions': result.get('definitions', []),
                'examples': result.get('examples', [])
            })
        elif result['type'] in ['translation', 'translation_fallback']:
            # 翻译类型卡片
            card_data.update({
                'type': 'translation',
                'original': result.get('original', input_text),
                'translation': result.get('translation', ''),
                'source_lang': result.get('source_lang', ''),
                'target_lang': result.get('target_lang', '')
            })
        
        return card_data
    
    def update_cards_count(self):
        """更新卡片计数"""
        self.cards_count_label.configure(text=f"词卡数量: {len(self.cards_data)}")
    
    def export_anki(self):
        """导出Anki卡片 - 每个单词单独生成一个文件"""
        if not self.cards_data:
            messagebox.showwarning("提示", "没有卡片可以导出")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_folder = self.anki_folder / f"导出_{timestamp}"
        export_folder.mkdir(exist_ok=True)
        
        exported_files = []
        failed_exports = []
        
        try:
            for i, card in enumerate(self.cards_data, 1):
                # 为每个卡片创建单独的文件
                word = card.get('word', card.get('input', f'卡片{i}'))
                # 清理文件名中的特殊字符
                safe_word = self.sanitize_filename(word)
                filename = export_folder / f"{safe_word}_{timestamp}.txt"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        front, back = self.format_anki_card(card)
                        f.write(f"{front}\t{back}\t智能翻译\n")
                    
                    exported_files.append((word, filename))
                    
                except Exception as e:
                    failed_exports.append((word, str(e)))
            
            # 创建批量导入说明
            self.create_batch_import_instructions(export_folder, exported_files, failed_exports)
            
            # 显示导出结果
            success_count = len(exported_files)
            fail_count = len(failed_exports)
            
            result_msg = f"✅ 成功导出 {success_count} 个单词卡片"
            if fail_count > 0:
                result_msg += f"\n❌ 失败 {fail_count} 个"
            result_msg += f"\n📁 导出位置: {export_folder}"
            
            messagebox.showinfo("导出完成", result_msg)
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def sanitize_filename(self, filename):
        """清理文件名中的特殊字符"""
        # 移除或替换不安全的字符
        import re
        # 保留字母、数字、中文、连字符和下划线
        safe_name = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', filename)
        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        return safe_name
    
    def format_anki_card(self, card):
        """格式化Anki卡片"""
        if card['type'] == 'dictionary':
            # 词典卡片格式
            front = card['word']
            if card['phonetic']:
                front += f" {card['phonetic']}"
            
            back_parts = []
            
            # 添加释义
            if card['definitions']:
                definitions_text = []
                for def_item in card['definitions']:
                    pos = def_item.get('pos', '')
                    definition = def_item.get('def', '')
                    if pos:
                        definitions_text.append(f"({pos}) {definition}")
                    else:
                        definitions_text.append(definition)
                back_parts.append(f"<b>释义:</b><br>{'<br>'.join(definitions_text)}")
            
            # 添加例句
            if card['examples']:
                examples_text = '<br>'.join(card['examples'])
                back_parts.append(f"<b>例句:</b><br>{examples_text}")
            
            back = '<br><br>'.join(back_parts)
            
        else:
            # 翻译卡片格式
            front = card['original']
            back = f"<b>翻译:</b> {card['translation']}"
            
            # 添加语言信息
            if card.get('source_lang') and card.get('target_lang'):
                lang_map = {'en': '英文', 'zh': '中文'}
                source_name = lang_map.get(card['source_lang'], card['source_lang'])
                target_name = lang_map.get(card['target_lang'], card['target_lang'])
                back += f"<br><br><small>({source_name} → {target_name})</small>"
        
        return front, back
    
    def create_batch_import_instructions(self, export_folder, exported_files, failed_exports):
        """创建批量导入说明"""
        instruction_file = export_folder / "📋_Anki导入说明.txt"
        
        instructions = f"""🧠 智能分类翻译器 - 批量Anki卡片导入说明

导出文件夹: {export_folder.name}
成功导出: {len(exported_files)} 个单词卡片
失败导出: {len(failed_exports)} 个
导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 导出统计:
"""
        
        # 统计卡片类型
        dict_count = sum(1 for card in self.cards_data if card['type'] == 'dictionary')
        trans_count = sum(1 for card in self.cards_data if card['type'] == 'translation')
        
        instructions += f"   • 词典卡片: {dict_count} 张\n"
        instructions += f"   • 翻译卡片: {trans_count} 张\n\n"
        
        # 添加成功导出的文件列表
        if exported_files:
            instructions += "✅ 成功导出的文件:\n"
            for word, filepath in exported_files:
                instructions += f"   • {word} → {filepath.name}\n"
            instructions += "\n"
        
        # 添加失败的文件列表
        if failed_exports:
            instructions += "❌ 导出失败的文件:\n"
            for word, error in failed_exports:
                instructions += f"   • {word}: {error}\n"
            instructions += "\n"
        
        instructions += """🚀 批量导入步骤:

方法1: 逐个导入（推荐）
1. 打开Anki软件
2. 对每个.txt文件重复以下步骤:
   a) 点击"导入文件"或使用快捷键 Ctrl+Shift+I (Mac: Cmd+Shift+I)
   b) 选择单个.txt文件
   c) 设置导入选项:
      - 字段分隔符: 制表符 (Tab)
      - 字段映射: 字段1→正面, 字段2→背面, 字段3→标签
   d) 选择目标牌组 "智能翻译"
   e) 点击"导入"

方法2: 合并导入
1. 可以将多个.txt文件内容合并到一个文件中
2. 然后按照单文件导入方式处理

📁 文件说明:
- 每个单词对应一个独立的.txt文件
- 文件名格式: 单词_时间戳.txt
- 每个文件包含一张Anki卡片

💡 使用建议:
- 建议创建专门的"智能翻译"牌组
- 可以为不同类型的卡片设置不同标签
- 词典卡片适合单词记忆，翻译卡片适合语感培养

🎨 推荐卡片模板:
正面: {{Front}}
背面: {{Back}}

✨ 单文件优势:
- 便于单独管理每个单词
- 可以选择性导入需要的单词
- 避免重复导入已学会的单词
- 便于分类和整理

祝学习愉快！🎉
"""
        
        try:
            with open(instruction_file, 'w', encoding='utf-8') as f:
                f.write(instructions)
            print(f"📋 导入说明已创建: {instruction_file}")
        except Exception as e:
            print(f"❌ 创建说明失败: {e}")
    
    def clear_cards(self):
        """清空卡片"""
        if not self.cards_data:
            messagebox.showinfo("提示", "卡片列表已经是空的")
            return
        
        result = messagebox.askyesno("确认", f"确定要清空所有 {len(self.cards_data)} 张卡片吗？")
        if result:
            self.cards_data.clear()
            self.update_cards_count()
            messagebox.showinfo("成功", "✅ 已清空所有卡片")
    
    def run(self):
        """运行程序"""
        print("🚀 启动智能分类翻译器界面...")
        try:
            # 确保窗口显示
            self.root.update()
            self.root.deiconify()
            self.root.lift()
            
            # 启动主循环
            self.root.mainloop()
        except Exception as e:
            print(f"❌ 程序运行出错: {e}")
        finally:
            print("👋 智能分类翻译器已关闭")

if __name__ == "__main__":
    try:
        print("🚀 启动智能分类翻译器...")
        app = SmartTranslator()
        app.run()
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        print("\n🔧 故障排除:")
        print("1. 确保安装了tkinter: brew install python-tk")
        print("2. 检查Python版本和GUI环境")
        print("3. 检查网络连接")