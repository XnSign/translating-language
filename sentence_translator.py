import json
import re

class SentenceTranslator:
    def __init__(self, translations_file='translation_packages/common_words/translations.json'):
        print(f"\n正在加载翻译文件: {translations_file}")
        try:
            with open(translations_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
                print(f"成功加载翻译文件，包含 {len(self.translations)} 个词条")
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到翻译文件: {translations_file}")
        except json.JSONDecodeError:
            raise ValueError(f"翻译文件格式错误: {translations_file}")
        except Exception as e:
            raise Exception(f"加载翻译文件时出错: {str(e)}")
        
        # 初始化支持的语言列表
        self.supported_languages = set()
        
        # 为每种语言创建双向查找字典
        # 从翻译到键值的映射
        self.trans_to_key = {}
        # 从键值到翻译的映射
        self.key_to_trans = {}
        
        print("\n初始化翻译数据...")
        
        # 第一遍遍历：收集所有支持的语言
        for key, data in self.translations.items():
            for lang in data['translations'].keys():
                self.supported_languages.add(lang)
        
        print(f"支持的语言: {self.supported_languages}")
        
        # 为每种语言初始化字典
        for lang in self.supported_languages:
            self.trans_to_key[lang] = {}
            self.key_to_trans[lang] = {}
        
        # 第二遍遍历：构建双向映射
        for key, data in self.translations.items():
            for lang, trans in data['translations'].items():
                # 存储原始翻译
                self.trans_to_key[lang][trans] = key
                self.key_to_trans[lang][key] = trans
                
                # 如果有替代形式，也添加到查找字典中
                if 'alternatives' in data and lang in data['alternatives']:
                    for alt in data['alternatives'][lang]:
                        self.trans_to_key[lang][alt] = key
                
                # 打印调试信息
                if lang == 'zh-CN':
                    print(f"添加中文词条: {trans} -> {key} -> {data['translations'].get('en', '未知')}")
        
        # 打印所有中文词条及其英文翻译
        if 'zh-CN' in self.trans_to_key:
            print("\n所有中文词条及其英文翻译:")
            print(f"中文词条数量: {len(self.trans_to_key['zh-CN'])}")
            for zh_word, key in self.trans_to_key['zh-CN'].items():
                en_word = self.translations[key]['translations'].get('en', '未知')
                print(f"- {zh_word} -> {en_word}")
                
        print("\n初始化完成")

    def translate_sentence(self, sentence, from_lang, to_lang):
        """
        将句子从一种语言翻译成另一种语言
        """
        if from_lang not in self.supported_languages:
            raise ValueError(f"不支持的源语言: {from_lang}")
        if to_lang not in self.supported_languages:
            raise ValueError(f"不支持的目标语言: {to_lang}")

        # 首先尝试将整个句子作为一个短语进行翻译
        sentence = sentence.strip()
        
        print(f"\n开始翻译...")
        print(f"输入句子: '{sentence}'")
        print(f"源语言: {from_lang}")
        print(f"目标语言: {to_lang}")
        print(f"支持的语言: {self.supported_languages}")
        print(f"词典大小: {len(self.translations)}")
        
        full_translation = self._translate_word_or_phrase(sentence, from_lang, to_lang)
        if full_translation:
            return full_translation

        # 如果整句翻译失败，将句子分割成单词
        if from_lang in ['zh-CN', 'ja', 'ko']:
            words = list(sentence)
        else:
            words = sentence.split()
        
        # 翻译每个部分
        translated_words = []
        i = 0
        while i < len(words):
            # 尝试不同长度的组合
            found = False
            for j in range(min(5, len(words) - i + 1), 0, -1):
                if from_lang in ['zh-CN', 'ja', 'ko']:
                    current = ''.join(words[i:i+j])
                else:
                    current = ' '.join(words[i:i+j])
                
                translated = self._translate_word_or_phrase(current, from_lang, to_lang)
                if translated:
                    translated_words.append(translated)
                    i += j
                    found = True
                    break
            
            if not found:
                # 尝试查找原文
                original = words[i]
                translated = self._translate_word_or_phrase(original, from_lang, to_lang)
                if translated:
                    translated_words.append(translated)
                else:
                    print(f"\n未找到翻译:")
                    print(f"当前词: '{original}'")
                translated_words.append(original)
                i += 1
        
        # 组合翻译结果
        result = self._combine_translations(translated_words, to_lang)
        if not result:
            return sentence
        return result

    def _translate_word_or_phrase(self, word, from_lang, to_lang):
        """
        翻译单个单词或短语
        """
        if not word:
            return None
            
        print(f"\n尝试翻译: '{word}'")
        print(f"源语言: {from_lang}, 目标语言: {to_lang}")
        print(f"当前语言的所有词条: {list(self.trans_to_key[from_lang].keys())}")
        
        # 通过源语言找到键值
        if word in self.trans_to_key[from_lang]:
            key = self.trans_to_key[from_lang][word]
            print(f"找到键值: {key}")
            # 通过键值找到目标语言的翻译
            result = self.translations[key]['translations'].get(to_lang)
            if result:
                print(f"找到匹配: {word} -> {key} -> {result}")
                return result
            else:
                print(f"未找到目标语言的翻译")
        else:
            print(f"在词典中未找到源语言词条")
            
        return None

    def _combine_translations(self, translated_words, to_lang):
        """
        根据目标语言的特点组合翻译结果
        """
        if not translated_words:
            return ""
            
        # 过滤掉空字符串
        translated_words = [w for w in translated_words if w and w.strip()]
        
        if to_lang in ['zh-CN', 'ja', 'ko']:
            return ''.join(translated_words)
        else:
            return ' '.join(translated_words)

    def get_supported_languages(self):
        """
        获取支持的语言列表
        """
        return list(self.supported_languages)

def main():
    # 创建翻译器实例
    translator = SentenceTranslator()
    
    # 打印支持的语言
    print("\n支持的语言代码:", translator.get_supported_languages())
    print("\n语言代码说明：")
    print("zh-CN: 中文(简体)")
    print("en: 英语")
    print("ja: 日语")
    print("ko: 韩语")
    print("fr: 法语")
    print("de: 德语")
    print("es: 西班牙语")
    print("ru: 俄语")
    
    while True:
        print("\n" + "="*50)
        # 获取用户输入
        sentence = input("\n请输入要翻译的句子（输入'q'退出）: ")
        if sentence.lower() == 'q':
            break
            
        from_lang = input("请输入源语言代码: ")
        to_lang = input("请输入目标语言代码: ")
        
        try:
            print("\n正在翻译...")
            # 翻译句子
            translated = translator.translate_sentence(sentence, from_lang, to_lang)
            print(f"原文 ({from_lang}): {sentence}")
            print(f"译文 ({to_lang}): {translated}")
            print("翻译源: 本地翻译包")
        except Exception as e:
            print(f"\n翻译出错: {str(e)}")

if __name__ == "__main__":
    main() 