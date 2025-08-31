#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anki词卡导出工具
支持多种格式导出和自定义模板
"""

import json
import csv
import html
from datetime import datetime
import os

class AnkiExporter:
    def __init__(self):
        self.templates = {
            'basic': {
                'name': '基础模板',
                'front': '{word} {phonetic}',
                'back': '{translations}<br><br>{definitions}'
            },
            'detailed': {
                'name': '详细模板',
                'front': '{word}<br><span style="color: blue;">{phonetic}</span>',
                'back': '<b>翻译:</b> {translations}<br><br><b>释义:</b> {definitions}<br><br><b>例句:</b> {examples}'
            },
            'cloze': {
                'name': '填空模板',
                'front': '{{{{c1::{word}}}}} - {translations}',
                'back': '{definitions}<br><br>{examples}'
            }
        }
    
    def export_to_txt(self, cards_data, filename, template='basic'):
        """导出为Anki TXT格式"""
        template_config = self.templates.get(template, self.templates['basic'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            for card in cards_data:
                front = self.format_card_side(template_config['front'], card)
                back = self.format_card_side(template_config['back'], card)
                
                # Anki格式：正面\t背面\t标签
                f.write(f"{front}\t{back}\ttranslation\n")
    
    def export_to_csv(self, cards_data, filename, template='basic'):
        """导出为CSV格式"""
        template_config = self.templates.get(template, self.templates['basic'])
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow(['Front', 'Back', 'Tags'])
            
            for card in cards_data:
                front = self.format_card_side(template_config['front'], card)
                back = self.format_card_side(template_config['back'], card)
                
                writer.writerow([front, back, 'translation'])
    
    def export_to_json(self, cards_data, filename):
        """导出为JSON格式（用于备份）"""
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_cards': len(cards_data),
            'cards': cards_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def format_card_side(self, template, card):
        """格式化卡片内容"""
        # 准备数据
        data = {
            'word': card.get('word', ''),
            'phonetic': card.get('phonetic', ''),
            'translations': card.get('translations', ''),
            'definitions': card.get('definitions', ''),
            'examples': card.get('examples', ''),
            'created_time': card.get('created_time', '')
        }
        
        # 处理空值
        for key, value in data.items():
            if not value:
                data[key] = ''
            elif key == 'phonetic' and value:
                data[key] = f"[{value}]"
        
        # 格式化模板
        try:
            formatted = template.format(**data)
            # 清理多余的空行和空格
            formatted = self.clean_html(formatted)
            return formatted
        except KeyError as e:
            print(f"模板格式错误: {e}")
            return f"{data['word']} - {data['translations']}"
    
    def clean_html(self, text):
        """清理HTML格式"""
        # 移除多余的<br>标签
        text = text.replace('<br><br><br>', '<br><br>')
        text = text.replace('<br><br> <br>', '<br><br>')
        
        # 移除空的HTML标签
        text = text.replace('<b></b>', '')
        text = text.replace('<i></i>', '')
        
        # 清理首尾空白
        text = text.strip()
        
        return text
    
    def create_anki_deck_file(self, cards_data, filename, deck_name="翻译词卡"):
        """创建Anki牌组文件（.apkg格式需要额外库）"""
        # 这里创建一个包含导入说明的文件
        base_name = os.path.splitext(filename)[0]
        txt_file = f"{base_name}.txt"
        instruction_file = f"{base_name}_导入说明.txt"
        
        # 导出TXT格式
        self.export_to_txt(cards_data, txt_file)
        
        # 创建导入说明
        instructions = f"""Anki词卡导入说明

文件: {os.path.basename(txt_file)}
牌组名称: {deck_name}
词卡数量: {len(cards_data)}
导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

导入步骤:
1. 打开Anki软件
2. 点击"导入文件"
3. 选择文件: {os.path.basename(txt_file)}
4. 设置字段分隔符为"制表符"
5. 设置字段映射:
   - 字段1: 正面
   - 字段2: 背面  
   - 字段3: 标签
6. 选择目标牌组: {deck_name}
7. 点击"导入"完成

注意事项:
- 确保Anki版本支持HTML格式
- 如有重复卡片，选择更新或跳过
- 建议先备份现有牌组

模板建议:
- 正面: {{{{Front}}}}
- 背面: {{{{Back}}}}
- 样式可自定义CSS美化
"""
        
        with open(instruction_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        return txt_file, instruction_file
    
    def get_available_templates(self):
        """获取可用模板列表"""
        return [(key, template['name']) for key, template in self.templates.items()]
    
    def add_custom_template(self, name, front_template, back_template):
        """添加自定义模板"""
        self.templates[name] = {
            'name': name,
            'front': front_template,
            'back': back_template
        }
    
    def preview_card(self, card_data, template='basic'):
        """预览卡片效果"""
        template_config = self.templates.get(template, self.templates['basic'])
        
        front = self.format_card_side(template_config['front'], card_data)
        back = self.format_card_side(template_config['back'], card_data)
        
        return {
            'front': front,
            'back': back,
            'template': template_config['name']
        }

# 使用示例
if __name__ == "__main__":
    # 测试数据
    test_cards = [
        {
            'word': 'hello',
            'phonetic': '/həˈloʊ/',
            'translations': '你好；喂',
            'definitions': 'n. 问候语；int. 喂',
            'examples': 'Hello, how are you? 你好，你好吗？',
            'created_time': '2024-01-01 12:00:00'
        },
        {
            'word': 'world',
            'phonetic': '/wɜːrld/',
            'translations': '世界；地球',
            'definitions': 'n. 世界，地球；领域',
            'examples': 'Welcome to the world! 欢迎来到这个世界！',
            'created_time': '2024-01-01 12:01:00'
        }
    ]
    
    exporter = AnkiExporter()
    
    # 导出不同格式
    exporter.export_to_txt(test_cards, 'test_cards.txt', 'detailed')
    exporter.export_to_csv(test_cards, 'test_cards.csv', 'basic')
    exporter.export_to_json(test_cards, 'test_cards.json')
    
    # 创建完整的Anki导入包
    txt_file, instruction_file = exporter.create_anki_deck_file(
        test_cards, 'my_vocabulary.apkg', '我的词汇'
    )
    
    print(f"导出完成:")
    print(f"- TXT文件: {txt_file}")
    print(f"- 说明文件: {instruction_file}")
    
    # 预览卡片
    preview = exporter.preview_card(test_cards[0], 'detailed')
    print(f"\n预览 ({preview['template']}):")
    print(f"正面: {preview['front']}")
    print(f"背面: {preview['back']}")