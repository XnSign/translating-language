"""
常用词汇翻译包
包含8000个常用词汇的多语言翻译
"""

import json
import os

class CommonWordsTranslator:
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """加载翻译数据"""
        package_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(package_dir, 'translations.json')
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print("警告: 翻译数据文件未找到")
            self.translations = {}
    
    def translate(self, word, source_lang, target_lang):
        """翻译单词
        
        Args:
            word (str): 要翻译的词
            source_lang (str): 源语言代码 (如 'zh-CN', 'en')
            target_lang (str): 目标语言代码
            
        Returns:
            dict: 包含翻译结果的字典
            {
                'text': str,  # 翻译结果
                'confidence': float,  # 置信度
                'source': str,  # 来源
                'alternatives': list  # 其他可能的翻译
            }
        """
        word = word.lower().strip()
        
        # 检查词是否在翻译库中
        if word in self.translations:
            word_data = self.translations[word]
            
            # 检查目标语言是否支持
            if target_lang in word_data['translations']:
                return {
                    'text': word_data['translations'][target_lang],
                    'confidence': 1.0,
                    'source': '常用词汇库',
                    'alternatives': word_data.get('alternatives', {}).get(target_lang, [])
                }
        
        return None
    
    def get_word_info(self, word, lang='en'):
        """获取词的详细信息
        
        Args:
            word (str): 要查询的词
            lang (str): 语言代码
            
        Returns:
            dict: 词的详细信息，包括词性、例句等
        """
        word = word.lower().strip()
        if word in self.translations:
            word_data = self.translations[word]
            return {
                'word': word,
                'translations': word_data['translations'],
                'pos': word_data.get('pos', ''),  # 词性
                'frequency': word_data.get('frequency', 0),  # 使用频率
                'examples': word_data.get('examples', {}).get(lang, []),  # 例句
                'alternatives': word_data.get('alternatives', {}),  # 其他可能的翻译
                'related': word_data.get('related', [])  # 相关词
            }
        return None
    
    def get_statistics(self):
        """获取翻译库统计信息"""
        return {
            'total_words': len(self.translations),
            'languages': self._get_supported_languages(),
            'categories': self._get_word_categories()
        }
    
    def _get_supported_languages(self):
        """获取支持的语言列表"""
        languages = set()
        for word_data in self.translations.values():
            languages.update(word_data['translations'].keys())
        return list(languages)
    
    def _get_word_categories(self):
        """获取词汇分类统计"""
        categories = {}
        for word_data in self.translations.values():
            category = word_data.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        return categories 