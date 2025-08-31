#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnkiConnect 接口模块
用于直接将卡片导入到 Anki 中
"""

import requests
import json
import time

class AnkiConnect:
    def __init__(self, api_key="MY_SECRET_KEY_123", host="127.0.0.1", port=8765):
        self.api_key = api_key
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        
    def _invoke(self, action, params=None):
        """调用 AnkiConnect API"""
        if params is None:
            params = {}
            
        request_data = {
            "action": action,
            "version": 6,
            "key": self.api_key,
            "params": params
        }
        
        try:
            response = self.session.post(self.base_url, json=request_data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("error"):
                raise Exception(f"AnkiConnect 错误: {result['error']}")
                
            return result.get("result")
        except requests.exceptions.RequestException as e:
            raise Exception(f"连接 Anki 失败: {str(e)}")
        except Exception as e:
            raise Exception(f"AnkiConnect 调用失败: {str(e)}")
    
    def test_connection(self):
        """测试与 Anki 的连接"""
        try:
            version = self._invoke("version")
            return True, f"连接成功，AnkiConnect 版本: {version}"
        except Exception as e:
            return False, str(e)
    
    def get_deck_names(self):
        """获取所有牌组名称"""
        try:
            decks = self._invoke("deckNames")
            return decks
        except Exception as e:
            print(f"获取牌组失败: {e}")
            return []
    
    def create_deck(self, deck_name):
        """创建新牌组"""
        try:
            self._invoke("createDeck", {"deck": deck_name})
            return True, f"牌组 '{deck_name}' 创建成功"
        except Exception as e:
            return False, f"创建牌组失败: {str(e)}"
    
    def get_model_names(self):
        """获取所有模板名称"""
        try:
            models = self._invoke("modelNames")
            return models
        except Exception as e:
            print(f"获取模板失败: {e}")
            return []
    
    def create_basic_model(self):
        """创建基础模板"""
        model_data = {
            "modelName": "Basic",
            "inOrderFields": ["Front", "Back"],
            "css": ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }",
            "cardTemplates": [
                {
                    "Name": "Card 1",
                    "Front": "{{Front}}",
                    "Back": "{{FrontSide}}<hr id=\"answer\">{{Back}}"
                }
            ]
        }
        
        try:
            self._invoke("createModel", model_data)
            return True
        except Exception as e:
            print(f"创建基础模板失败: {e}")
            return False
    
    def add_note(self, front, back, deck_name="阅读中的收获", tags=None):
        """添加卡片到 Anki"""
        if tags is None:
            tags = ["books", "translation"]
        
        # 获取可用的模板
        models = self.get_model_names()
        
        # 尝试不同的模板和字段组合
        attempts = [
            ("Basic", {"Front": front, "Back": back}),
            ("基础", {"正面": front, "背面": back}),
            ("Cloze", {"Text": f"{front}<br><br>{back}"}),
        ]
        
        # 如果有其他模板，也尝试使用
        for model in models:
            if model not in ["Basic", "基础", "Cloze"]:
                try:
                    model_fields = self._invoke("modelFieldNames", {"modelName": model})
                    if len(model_fields) >= 2:
                        fields = {
                            model_fields[0]: front,
                            model_fields[1]: back
                        }
                        # 其他字段填空
                        for field in model_fields[2:]:
                            fields[field] = ""
                        attempts.append((model, fields))
                except:
                    continue
        
        # 尝试每种组合
        for model_name, fields in attempts:
            if model_name in models or model_name == "Basic":
                note = {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": fields,
                    "tags": tags
                }
                
                try:
                    note_id = self._invoke("addNote", {"note": note})
                    return True, f"卡片添加成功 (模板: {model_name}, ID: {note_id})"
                except Exception as e:
                    print(f"模板 {model_name} 失败: {e}")
                    continue
        
        return False, "所有模板都无法添加卡片，请检查 Anki 设置"
    
    def add_notes_batch(self, notes_data, deck_name="阅读中的收获"):
        """批量添加卡片"""
        notes = []
        for note_data in notes_data:
            note = {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": note_data.get("front", ""),
                    "Back": note_data.get("back", "")
                },
                "tags": note_data.get("tags", ["books", "translation"])
            }
            notes.append(note)
        
        try:
            result = self._invoke("addNotes", {"notes": notes})
            success_count = len([r for r in result if r is not None])
            return True, f"批量添加完成，成功: {success_count}/{len(notes)}"
        except Exception as e:
            return False, f"批量添加失败: {str(e)}"
    
    def find_notes(self, query):
        """查找卡片"""
        try:
            note_ids = self._invoke("findNotes", {"query": query})
            return note_ids
        except Exception as e:
            print(f"查找卡片失败: {e}")
            return []
    
    def get_note_info(self, note_ids):
        """获取卡片信息"""
        try:
            notes_info = self._invoke("notesInfo", {"notes": note_ids})
            return notes_info
        except Exception as e:
            print(f"获取卡片信息失败: {e}")
            return []

# 测试函数
def test_anki_connect():
    """测试 AnkiConnect 连接"""
    print("🔍 测试 AnkiConnect 连接...")
    
    anki = AnkiConnect()
    
    # 测试连接
    success, message = anki.test_connection()
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        return False
    
    # 获取牌组列表
    decks = anki.get_deck_names()
    print(f"📚 现有牌组: {decks}")
    
    # 确保 阅读中的收获 牌组存在
    if "阅读中的收获" not in decks:
        success, message = anki.create_deck("阅读中的收获")
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    # 测试添加卡片
    test_front = "test word"
    test_back = "测试单词"
    success, message = anki.add_note(test_front, test_back, "阅读中的收获", ["test"])
    
    if success:
        print(f"✅ 测试卡片添加成功: {message}")
    else:
        print(f"❌ 测试卡片添加失败: {message}")
    
    return success

if __name__ == "__main__":
    test_anki_connect()