#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试翻译质量对比
对比原有翻译器和高质量翻译器的效果
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from 右键Anki服务 import RightClickAnkiService
from premium_translator import PremiumTranslator, TranslationQuality

def compare_translation_quality():
    """对比翻译质量"""
    print("🔍 翻译质量对比测试")
    print("=" * 60)
    
    # 创建翻译器实例
    original_service = RightClickAnkiService()
    premium_translator = PremiumTranslator()
    
    # 测试用例
    test_cases = [
        # 英文句子
        ("Hello world", "简单问候"),
        ("This is a beautiful day", "日常表达"),
        ("The quick brown fox jumps over the lazy dog", "经典测试句"),
        ("Artificial intelligence is transforming our world", "技术术语"),
        ("I would like to make a reservation for dinner", "正式表达"),
        
        # 中文句子
        ("你好世界", "简单问候"),
        ("今天天气很好", "日常表达"),
        ("人工智能正在改变我们的世界", "技术表达"),
        ("我想预订今晚的晚餐", "正式表达"),
        ("这本书非常有趣，我推荐给大家", "推荐表达"),
    ]
    
    print("📊 翻译质量对比结果：")
    print()
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"🧪 测试 {i}: {description}")
        print(f"📝 原文: '{text}'")
        print()
        
        # 检测语言和目标语言
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            target_lang = "en"
            lang_desc = "中译英"
        else:
            target_lang = "zh"
            lang_desc = "英译中"
        
        print(f"🌐 翻译方向: {lang_desc}")
        print()
        
        # 原有翻译器
        print("📋 原有翻译器:")
        try:
            original_result = original_service.translate_sentence(text, "auto", target_lang)
            if original_result and original_result.get('translation'):
                print(f"  ✅ 译文: {original_result['translation']}")
            else:
                print("  ❌ 翻译失败")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print()
        
        # 高质量翻译器 - 基础模式
        print("🔧 高质量翻译器 (基础模式):")
        try:
            basic_result = premium_translator.translate(text, target_lang, TranslationQuality.BASIC)
            if basic_result:
                print(f"  ✅ 译文: {basic_result.translated_text}")
                print(f"  📊 质量分数: {basic_result.quality_score:.2f}")
                print(f"  🎯 置信度: {basic_result.confidence:.2f}")
                print(f"  🌐 翻译源: {basic_result.translation_source}")
            else:
                print("  ❌ 翻译失败")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print()
        
        # 高质量翻译器 - 高级模式
        print("🚀 高质量翻译器 (高级模式):")
        try:
            premium_result = premium_translator.translate(text, target_lang, TranslationQuality.PREMIUM)
            if premium_result:
                print(f"  ✅ 译文: {premium_result.translated_text}")
                print(f"  📊 质量分数: {premium_result.quality_score:.2f}")
                print(f"  🎯 置信度: {premium_result.confidence:.2f}")
                print(f"  🌐 翻译源: {premium_result.translation_source}")
                if premium_result.alternatives:
                    print(f"  📋 备选翻译: {', '.join(premium_result.alternatives[:2])}")
            else:
                print("  ❌ 翻译失败")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print("=" * 60)
        print()

def test_word_translation():
    """测试单词翻译质量"""
    print("📚 单词翻译质量测试")
    print("=" * 60)
    
    original_service = RightClickAnkiService()
    
    test_words = [
        "price", "knowledge", "beautiful", "important", "development",
        "technology", "environment", "education", "communication", "opportunity"
    ]
    
    for word in test_words:
        print(f"📝 测试单词: {word}")
        
        try:
            # 词典查询
            dict_result = original_service.dictionary_lookup(word)
            if dict_result and dict_result.get('found', True):
                print(f"  📖 词典查询成功")
                print(f"  🔤 音标: {dict_result.get('phonetic', 'N/A')}")
                
                definitions = dict_result.get('definitions', [])
                for i, def_item in enumerate(definitions[:2], 1):
                    pos = def_item.get('pos', '')
                    def_content = def_item.get('def', '')
                    print(f"  {i}. {pos} {def_content}")
                
                examples = dict_result.get('examples', [])
                if examples:
                    print(f"  📋 例句: {examples[0]}")
            else:
                print("  ❌ 词典查询失败")
                
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print("-" * 30)

def analyze_translation_issues():
    """分析翻译问题"""
    print("🔍 翻译问题分析")
    print("=" * 60)
    
    issues = [
        "🔸 词汇选择不准确 - 使用了不合适的词汇",
        "🔸 语法结构问题 - 句子结构不自然",
        "🔸 语境理解偏差 - 没有考虑上下文",
        "🔸 专业术语翻译 - 技术词汇翻译不准确",
        "🔸 语言风格不匹配 - 正式/非正式语言混用",
        "🔸 文化差异处理 - 没有考虑文化背景",
    ]
    
    print("📋 常见翻译质量问题：")
    for issue in issues:
        print(f"  {issue}")
    
    print()
    print("💡 高质量翻译器的改进：")
    improvements = [
        "✅ 多翻译源对比 - 选择最佳翻译结果",
        "✅ 质量评估算法 - 自动评估翻译质量",
        "✅ 文本后处理 - 清理和优化翻译文本",
        "✅ 上下文感知 - 更好的语境理解",
        "✅ 专业术语库 - 准确翻译技术词汇",
        "✅ 语言风格适配 - 保持一致的语言风格",
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")

if __name__ == "__main__":
    print("🧪 翻译质量测试套件")
    print("=" * 60)
    
    try:
        # 分析问题
        analyze_translation_issues()
        print()
        
        # 单词翻译测试
        test_word_translation()
        print()
        
        # 质量对比测试
        compare_translation_quality()
        
        print("🎉 翻译质量测试完成！")
        print("💡 建议使用高质量翻译器以获得更好的翻译效果")
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()