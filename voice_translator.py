import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speech_recognition as sr
import pyttsx3
import json
from datetime import datetime
import os
import requests
import hashlib
import time
from dotenv import load_dotenv
import random
from googletrans import Translator as GoogleTranslator
import deepl
import uuid
import locale

class TranslationContext:
    def __init__(self, max_history=5):
        self.history = []
        self.max_history = max_history
    
    def add_context(self, text, translation):
        self.history.append((text, translation))
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self):
        return self.history
    
    def clear_context(self):
        self.history = []

class VoiceTranslator:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 初始化翻译上下文
        self.context = TranslationContext()
        
        # 初始化翻译服务
        self.init_translation_services()
        
        # 常用短语映射
        self.phrase_mapping = {
            '你好': {
                'en': 'hello',
                'ja': 'こんにちは',
                'ko': '안녕하세요',
                'fr': 'bonjour',
                'de': 'hallo',
                'es': 'hola',
                'ru': 'здравствуйте'
            },
            '早上好': {
                'en': 'good morning',
                'ja': 'おはようございます',
                'ko': '안녕하세요',
                'fr': 'bonjour',
                'de': 'guten morgen',
                'es': 'buenos días',
                'ru': 'доброе утро'
            },
            '下午好': {
                'en': 'good afternoon',
                'ja': 'こんにちは',
                'ko': '안녕하세요',
                'fr': 'bon après-midi',
                'de': 'guten tag',
                'es': 'buenas tardes',
                'ru': 'добрый день'
            },
            '晚上好': {
                'en': 'good evening',
                'ja': 'こんばんは',
                'ko': '안녕하세요',
                'fr': 'bonsoir',
                'de': 'guten abend',
                'es': 'buenas noches',
                'ru': 'добрый вечер'
            },
            '晚安': {
                'en': 'good night',
                'ja': 'おやすみなさい',
                'ko': '안녕히 주무세요',
                'fr': 'bonne nuit',
                'de': 'gute nacht',
                'es': 'buenas noches',
                'ru': 'спокойной ночи'
            },
            '谢谢': {
                'en': 'thank you',
                'ja': 'ありがとう',
                'ko': '감사합니다',
                'fr': 'merci',
                'de': 'danke',
                'es': 'gracias',
                'ru': 'спасибо'
            },
            '再见': {
                'en': 'goodbye',
                'ja': 'さようなら',
                'ko': '안녕히 가세요',
                'fr': 'au revoir',
                'de': 'auf wiedersehen',
                'es': 'adiós',
                'ru': 'до свидания'
            },
            '对不起': {
                'en': 'sorry',
                'ja': 'すみません',
                'ko': '죄송합니다',
                'fr': 'désolé',
                'de': 'entschuldigung',
                'es': 'lo siento',
                'ru': 'извините'
            },
            '请': {
                'en': 'please',
                'ja': 'お願いします',
                'ko': '부탁합니다',
                'fr': 's\'il vous plaît',
                'de': 'bitte',
                'es': 'por favor',
                'ru': 'пожалуйста'
            },
            '好的': {
                'en': 'okay',
                'ja': 'はい',
                'ko': '네',
                'fr': 'd\'accord',
                'de': 'okay',
                'es': 'bien',
                'ru': 'хорошо'
            }
        }
        
        # 界面语言设置
        self.ui_languages = {
            '简体中文': {
                'title': '语音翻译助手',
                'ui_language': '界面语言：',
                'source_lang': '源语言：',
                'target_lang': '目标语言：',
                'trans_source': '翻译源：',
                'smart_select': '智能选择',
                'local_package': '本地翻译包',
                'auto_detect': '自动检测语言',
                'trans_result': '翻译结果',
                'text_input': '文本输入区域',
                'translate_btn': '翻译文本',
                'start_record': '开始录音',
                'stop_record': '停止录音',
                'history': '历史记录',
                'api_settings': 'API设置',
                'select_mic': '选择麦克风：',
                'enable_voice': '启用语音输出',
                'select_voice': '选择声音：',
                'voice_speed': '语速：',
                'shortcut': '快捷键: Ctrl+Enter',
                'listening': '正在听取语音...',
                'recognition_conf': '语音识别置信度: ',
                'original_text': '原始识别: ',
                'smart_correction': '智能纠正: ',
                'translating': '正在翻译...',
                'trans_failed': '翻译失败，请重试...',
                'input_prompt': '请输入要翻译的文本',
                'settings_saved': '设置已保存',
                'save_settings': '保存设置',
                'original': '原文',
                'translation': '译文',
                'deepl_key': 'DeepL API密钥',
                'baidu_app_id': '百度翻译APP ID',
                'baidu_secret': '百度翻译密钥',
                'youdao_app_key': '有道翻译APP KEY',
                'youdao_secret': '有道翻译密钥',
                'azure_key': '微软翻译密钥',
                'azure_region': '微软翻译区域',
                'azure_endpoint': '微软翻译终端',
                'tencent_id': '腾讯翻译Secret ID',
                'tencent_key': '腾讯翻译Secret Key',
                'aws_access': 'AWS访问密钥',
                'aws_secret': 'AWS密钥',
                'aws_region': 'AWS区域',
                'caiyun_token': '彩云小译Token',
                'niutrans_key': '小牛翻译密钥',
                'languages': {
                    'Chinese (Simplified)': '中文(简体)',
                    'Chinese (Traditional)': '中文(繁体)',
                    'English': '英语',
                    'Japanese': '日语',
                    'Korean': '韩语',
                    'French': '法语',
                    'German': '德语',
                    'Spanish': '西班牙语',
                    'Russian': '俄语'
                },
                'error': '错误',
                'warning': '警告',
                'success': '成功',
                'mic_not_found': '未检测到麦克风设备！请确保麦克风已正确连接。',
                'mic_error': '初始化麦克风时出错：{}\n请检查麦克风是否正确连接和启用。',
                'voice_init_error': '初始化语音输出引擎失败：{}',
                'processing_error': '处理翻译结果时出错: {}',
                'recording_error': '录音过程出错：{}',
                'api_not_configured': '{}未配置API密钥，请先配置后再使用。',
                'confidence': '置信度: ',
                'source_text': '原文 ({}): ',
                'target_text': '译文 ({}): ',
                'translation_source': '翻译源: ',
                'translation_confidence': '翻译置信度: ',
                'not_in_local': '本地翻译包中未找到词条：{}',
                'local_not_loaded': '本地翻译包未加载',
                'all_failed': '所有翻译源都失败了，请重试',
                'voice_output_error': '语音输出错误: {}',
                'local_package_loaded': '成功加载常用词汇翻译包',
                'local_package_not_found': '未找到常用词汇翻译包，将使用在线翻译服务',
                'recognition_error': '未能识别语音，请重试...',
                'unknown_source': '未知来源',
                'translation_sources': {
                    'DeepL翻译': 'DeepL翻译',
                    '谷歌翻译': '谷歌翻译',
                    '百度翻译': '百度翻译',
                    '有道翻译': '有道翻译',
                    '微软翻译': '微软翻译',
                    '腾讯翻译': '腾讯翻译',
                    'AWS翻译': 'AWS翻译',
                    '彩云翻译': '彩云翻译',
                    '小牛翻译': '小牛翻译'
                }
            },
            'English': {
                'title': 'Voice Translator',
                'ui_language': 'UI Language:',
                'source_lang': 'Source Language:',
                'target_lang': 'Target Language:',
                'trans_source': 'Translation Source:',
                'smart_select': 'Smart Select',
                'local_package': 'Local Package',
                'auto_detect': 'Auto Detect Language',
                'trans_result': 'Translation Results',
                'text_input': 'Text Input Area',
                'translate_btn': 'Translate',
                'start_record': 'Start Recording',
                'stop_record': 'Stop Recording',
                'history': 'History',
                'api_settings': 'API Settings',
                'select_mic': 'Select Microphone:',
                'enable_voice': 'Enable Voice Output',
                'select_voice': 'Select Voice:',
                'voice_speed': 'Speed:',
                'shortcut': 'Shortcut: Ctrl+Enter',
                'listening': 'Listening...',
                'recognition_conf': 'Recognition Confidence: ',
                'original_text': 'Original: ',
                'smart_correction': 'Corrected: ',
                'translating': 'Translating...',
                'trans_failed': 'Translation failed, please try again...',
                'input_prompt': 'Please enter text to translate',
                'settings_saved': 'Settings saved',
                'save_settings': 'Save Settings',
                'original': 'Original',
                'translation': 'Translation',
                'deepl_key': 'DeepL API Key',
                'baidu_app_id': 'Baidu APP ID',
                'baidu_secret': 'Baidu Secret Key',
                'youdao_app_key': 'Youdao APP KEY',
                'youdao_secret': 'Youdao Secret',
                'azure_key': 'Microsoft Translator Key',
                'azure_region': 'Microsoft Translator Region',
                'azure_endpoint': 'Microsoft Translator Endpoint',
                'tencent_id': 'Tencent Secret ID',
                'tencent_key': 'Tencent Secret Key',
                'aws_access': 'AWS Access Key',
                'aws_secret': 'AWS Secret Key',
                'aws_region': 'AWS Region',
                'caiyun_token': 'Caiyun Token',
                'niutrans_key': 'Niutrans Key',
                'languages': {
                    'Chinese (Simplified)': 'Chinese (Simplified)',
                    'Chinese (Traditional)': 'Chinese (Traditional)',
                    'English': 'English',
                    'Japanese': 'Japanese',
                    'Korean': 'Korean',
                    'French': 'French',
                    'German': 'German',
                    'Spanish': 'Spanish',
                    'Russian': 'Russian'
                },
                'error': 'Error',
                'warning': 'Warning',
                'success': 'Success',
                'mic_not_found': 'No microphone detected! Please ensure the microphone is properly connected.',
                'mic_error': 'Error initializing microphone: {}\nPlease check if the microphone is properly connected and enabled.',
                'voice_init_error': 'Failed to initialize voice output engine: {}',
                'processing_error': 'Error processing translation result: {}',
                'recording_error': 'Recording error: {}',
                'api_not_configured': '{} API key not configured, please configure it first.',
                'confidence': 'Confidence: ',
                'source_text': 'Source ({}): ',
                'target_text': 'Target ({}): ',
                'translation_source': 'Translation Source: ',
                'translation_confidence': 'Translation Confidence: ',
                'not_in_local': 'Entry not found in local package: {}',
                'local_not_loaded': 'Local translation package not loaded',
                'all_failed': 'All translation sources failed, please try again',
                'voice_output_error': 'Voice output error: {}',
                'local_package_loaded': 'Successfully loaded common words translation package',
                'local_package_not_found': 'Common words translation package not found, will use online translation services',
                'recognition_error': 'Speech recognition failed, please try again...',
                'unknown_source': 'Unknown Source',
                'translation_sources': {
                    'DeepL翻译': 'DeepL Translate',
                    '谷歌翻译': 'Google Translate',
                    '百度翻译': 'Baidu Translate',
                    '有道翻译': 'Youdao Translate',
                    '微软翻译': 'Microsoft Translate',
                    '腾讯翻译': 'Tencent Translate',
                    'AWS翻译': 'AWS Translate',
                    '彩云翻译': 'Caiyun Translate',
                    '小牛翻译': 'Niutrans Translate'
                }
            }
        }
        
        # 获取系统语言并设置默认界面语言
        try:
            system_lang = locale.getdefaultlocale()[0].lower()
            if system_lang.startswith('zh'):
                self.current_ui_lang = '简体中文'
            else:
                self.current_ui_lang = 'English'
        except:
            # 如果无法获取系统语言，默认使用英文
            self.current_ui_lang = 'English'
        
        self.window = tk.Tk()
        self.window.title(self.ui_languages[self.current_ui_lang]['title'])
        self.window.geometry('800x600')
        
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        
        # 检查麦克风
        try:
            self.mic_list = sr.Microphone.list_microphone_names()
            if not self.mic_list:
                messagebox.showerror(
                    self.ui_languages[self.current_ui_lang]['error'],
                    self.ui_languages[self.current_ui_lang]['mic_not_found']
                )
                self.window.destroy()
                return
        except Exception as e:
            messagebox.showerror(
                self.ui_languages[self.current_ui_lang]['error'],
                self.ui_languages[self.current_ui_lang]['mic_error'].format(str(e))
            )
            self.window.destroy()
            return
        
        # 支持的语言
        self.supported_languages = {
            'Chinese (Simplified)': 'zh-CN',
            'Chinese (Traditional)': 'zh-TW',
            'English': 'en',
            'Japanese': 'ja',
            'Korean': 'ko',
            'French': 'fr',
            'German': 'de',
            'Spanish': 'es',
            'Russian': 'ru'
        }
        
        # 常见短语映射（用于上下文理解）
        self.common_phrases = {
            '可以': {
                'context_yes': ['yes', 'sure', 'okay', 'alright'],
                'context_ability': ['can', 'could', 'able to'],
                'context_permission': ['may', 'allowed to']
            },
            '好的': {
                'context_agreement': ['okay', 'alright', 'sure'],
                'context_quality': ['good', 'nice', 'fine']
            }
        }
        
        self.common_words_translator = None
        try:
            from translation_packages.common_words import CommonWordsTranslator
            self.common_words_translator = CommonWordsTranslator()
            print(self.ui_languages[self.current_ui_lang]['local_package_loaded'])
        except ImportError:
            print(self.ui_languages[self.current_ui_lang]['local_package_not_found'])
        
        # 初始化语音引擎
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.voice_list = [voice.name for voice in voices]
        except Exception as e:
            messagebox.showerror(
                self.ui_languages[self.current_ui_lang]['error'],
                self.ui_languages[self.current_ui_lang]['voice_init_error'].format(str(e))
            )
            self.engine = None
            self.voice_list = []
        
        self.init_ui()
        
    def init_translation_services(self):
        """初始化所有翻译服务"""
        # 加载环境变量
        load_dotenv()
        
        # Azure/微软翻译
        self.azure_key = os.getenv('AZURE_TRANSLATOR_KEY')
        self.azure_region = os.getenv('AZURE_TRANSLATOR_REGION')
        self.azure_endpoint = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
        
        # 百度翻译
        self.baidu_app_id = os.getenv('BAIDU_APP_ID')
        self.baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        # 有道翻译
        self.youdao_app_key = os.getenv('YOUDAO_APP_KEY')
        self.youdao_app_secret = os.getenv('YOUDAO_APP_SECRET')
        
        # DeepL翻译
        self.deepl_api_key = os.getenv('DEEPL_API_KEY')
        if self.deepl_api_key:
            try:
                self.deepl_translator = deepl.Translator(self.deepl_api_key)
            except Exception as e:
                print(f"DeepL初始化错误: {str(e)}")
                self.deepl_translator = None
        else:
            self.deepl_translator = None
            
        # 腾讯翻译
        self.tencent_secret_id = os.getenv('TENCENT_SECRET_ID')
        self.tencent_secret_key = os.getenv('TENCENT_SECRET_KEY')
        
        # Amazon Translate
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY')
        self.aws_secret_key = os.getenv('AWS_SECRET_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # 彩云小译
        self.caiyun_token = os.getenv('CAIYUN_TOKEN')
        
        # 小牛翻译
        self.niutrans_key = os.getenv('NIUTRANS_KEY')
    
    def analyze_context(self, text, prev_texts):
        """分析上下文，返回更适合的翻译"""
        # 对于常见短语的特殊处理
        if text in self.common_phrases:
            # 分析上下文中的关键词
            context_text = ' '.join([t[0] for t in prev_texts[-3:]])  # 获取最近3条记录
            
            if '是否' in context_text or '可不可以' in context_text or '行吗' in context_text:
                return random.choice(self.common_phrases[text]['context_yes'])
            elif '能' in context_text or '会' in context_text:
                return random.choice(self.common_phrases[text]['context_ability'])
            else:
                # 默认选择最常用的上下文
                return random.choice(self.common_phrases[text]['context_yes'])
        
        return None
    
    def translate_text(self, text, source_lang=None, target_lang=None):
        """翻译文本"""
        if not text:
            return {
                "text": "",
                "confidence": 0.0,
                "source": self.ui_languages[self.current_ui_lang].get('unknown_source', 'Unknown Source')
            }
        
        # 获取选定的翻译源
        selected_source = self.selected_source.get()
        
        try:
            # 如果选择了本地翻译包
            if selected_source == self.ui_languages[self.current_ui_lang]['local_package']:
                if self.common_words_translator:
                    result = self.common_words_translator.translate(text, source_lang, target_lang)
                    if result:
                        return result
                    else:
                        return {
                            "text": self.ui_languages[self.current_ui_lang]['not_in_local'].format(text),
                            "confidence": 0.0,
                            "source": self.ui_languages[self.current_ui_lang]['local_package']
                        }
                else:
                    return {
                        "text": self.ui_languages[self.current_ui_lang]['local_not_loaded'],
                        "confidence": 0.0,
                        "source": self.ui_languages[self.current_ui_lang]['local_package']
                    }
            
            # 其他翻译源的处理
            if selected_source == self.ui_languages[self.current_ui_lang]['smart_select']:
                # 首先尝试使用本地翻译包
                if self.common_words_translator:
                    result = self.common_words_translator.translate(text, source_lang, target_lang)
                    if result:
                        return result
                result = self.smart_translate(text, source_lang, target_lang)
                if isinstance(result, tuple):
                    return {
                        "text": result[0],
                        "confidence": result[1],
                        "source": self.ui_languages[self.current_ui_lang]['smart_select']
                    }
                return result
            elif selected_source == 'DeepL翻译':
                result = self.deepl_translate(text, source_lang, target_lang)
                if isinstance(result, tuple):
                    return {
                        "text": result[0],
                        "confidence": result[1],
                        "source": "DeepL翻译"
                    }
                return result
            elif selected_source == '百度翻译':
                result = self.baidu_translate(text, source_lang, target_lang)
                if isinstance(result, tuple):
                    return {
                        "text": result[0],
                        "confidence": result[1],
                        "source": "百度翻译"
                    }
                return result
            elif selected_source == '有道翻译':
                result = self.youdao_translate(text, source_lang, target_lang)
                if isinstance(result, tuple):
                    return {
                        "text": result[0],
                        "confidence": result[1],
                        "source": "有道翻译"
                    }
                return result
            else:  # 默认使用谷歌翻译
                result = self.google_translate(text, source_lang, target_lang)
                if isinstance(result, tuple):
                    return {
                        "text": result[0],
                        "confidence": result[1],
                        "source": "谷歌翻译"
                    }
                return result
        except Exception as e:
            print(f"翻译错误: {str(e)}")
            return {
                "text": self.ui_languages[self.current_ui_lang]['trans_failed'],
                "confidence": 0.0,
                "source": self.ui_languages[self.current_ui_lang]['error']
            }
    
    def baidu_translate(self, text, from_lang, to_lang):
        """调用百度翻译API"""
        try:
            if not self.baidu_app_id or not self.baidu_secret_key:
                return {
                    'text': self.ui_languages[self.current_ui_lang]['api_not_configured'].format(self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']),
                    'confidence': 0.0,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']
                }

            url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
            salt = str(random.randint(32768, 65536))
            sign = hashlib.md5((self.baidu_app_id + text + salt + self.baidu_secret_key).encode()).hexdigest()
            
            # 语言代码映射
            lang_map = {
                'zh-CN': 'zh',
                'zh-TW': 'cht',
                'en': 'en',
                'ja': 'jp',
                'ko': 'kor',
                'fr': 'fra',
                'de': 'de',
                'es': 'spa',
                'ru': 'ru'
            }
            
            # 转换语言代码
            from_lang = lang_map.get(from_lang, from_lang)
            to_lang = lang_map.get(to_lang, to_lang)
            
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': self.baidu_app_id,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params)
            result = response.json()
            
            if 'trans_result' in result and result['trans_result']:
                # 根据文本特征调整置信度
                is_chinese = 'zh' in from_lang or 'zh' in to_lang
                confidence = 0.9 if is_chinese else 0.75
                return {
                    'text': result['trans_result'][0]['dst'],
                    'confidence': confidence,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']
                }
            else:
                error_msg = result.get('error_msg', self.ui_languages[self.current_ui_lang]['unknown_source'])
                error_code = result.get('error_code', 'unknown')
                return {
                    'text': f'{self.ui_languages[self.current_ui_lang]["translation_sources"]["百度翻译"]}{self.ui_languages[self.current_ui_lang]["error"]}: {error_code} - {error_msg}',
                    'confidence': 0.0,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']
                }
            
        except Exception as e:
            print(f"{self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']}{self.ui_languages[self.current_ui_lang]['error']}: {str(e)}")
            return {
                'text': f'{self.ui_languages[self.current_ui_lang]["translation_sources"]["百度翻译"]}{self.ui_languages[self.current_ui_lang]["error"]}: {str(e)}',
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']
            }
    
    def youdao_translate(self, text, from_lang, to_lang):
        """调用有道翻译API"""
        try:
            if not self.youdao_app_key or not self.youdao_app_secret:
                return {
                    'text': self.ui_languages[self.current_ui_lang]['api_not_configured'].format(self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']),
                    'confidence': 0.0,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']
                }

            url = 'https://openapi.youdao.com/api'
            curtime = str(int(time.time()))
            salt = str(uuid.uuid1())
            
            # 计算input长度
            input_len = len(text)
            if input_len <= 20:
                input_text = text
            else:
                input_text = text[:10] + str(input_len) + text[-10:]
            
            # 计算签名
            sign_str = self.youdao_app_key + input_text + salt + curtime + self.youdao_app_secret
            sign = hashlib.sha256(sign_str.encode()).hexdigest()
            
            # 语言代码映射
            lang_map = {
                'zh-CN': 'zh-CHS',
                'zh-TW': 'zh-CHT',
                'en': 'en',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru'
            }
            
            from_lang = lang_map.get(from_lang, from_lang)
            to_lang = lang_map.get(to_lang, to_lang)
            
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appKey': self.youdao_app_key,
                'salt': salt,
                'sign': sign,
                'signType': 'v3',
                'curtime': curtime,
            }
            
            response = requests.get(url, params=params)
            result = response.json()
            
            if 'translation' in result and result['translation']:
                # 根据文本特征调整置信度
                is_short = len(text.split()) <= 3
                confidence = 0.85 if is_short else 0.7
                return {
                    'text': result['translation'][0],
                    'confidence': confidence,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']
                }
            else:
                error_msg = result.get('errorMessage', self.ui_languages[self.current_ui_lang]['unknown_source'])
                error_code = result.get('errorCode', 'unknown')
                return {
                    'text': f'{self.ui_languages[self.current_ui_lang]["translation_sources"]["有道翻译"]}{self.ui_languages[self.current_ui_lang]["error"]}: {error_code} - {error_msg}',
                    'confidence': 0.0,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']
                }
            
        except Exception as e:
            print(f"{self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']}{self.ui_languages[self.current_ui_lang]['error']}: {str(e)}")
            return {
                'text': f'{self.ui_languages[self.current_ui_lang]["translation_sources"]["有道翻译"]}{self.ui_languages[self.current_ui_lang]["error"]}: {str(e)}',
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']
            }
    
    def azure_translate(self, text, from_lang, to_lang):
        """调用Azure翻译API"""
        try:
            url = f"{self.azure_endpoint}/translate"
            params = {
                'api-version': '3.0',
                'from': from_lang,
                'to': to_lang
            }
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_key,
                'Ocp-Apim-Subscription-Region': self.azure_region,
                'Content-type': 'application/json'
            }
            body = [{'text': text}]
            
            response = requests.post(url, params=params, headers=headers, json=body)
            response.raise_for_status()
            
            result = response.json()
            if result and len(result) > 0:
                return {
                    'text': result[0]['translations'][0]['text'],
                    'confidence': result[0].get('detectedLanguage', {}).get('score', 0.7)
                }
            return None
        except Exception as e:
            print(f"Azure翻译请求错误: {str(e)}")
            return None
    
    def tencent_translate(self, text, from_lang, to_lang):
        """调用腾讯云翻译API"""
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.tmt.v20180321 import tmt_client, models
            
            cred = credential.Credential(self.tencent_secret_id, self.tencent_secret_key)
            httpProfile = HttpProfile()
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)
            req = models.TextTranslateRequest()
            req.SourceText = text
            req.Source = from_lang
            req.Target = to_lang
            req.ProjectId = 0
            
            response = client.TextTranslate(req)
            return response.to_json_string()
        except Exception as e:
            print(f"腾讯翻译请求错误: {str(e)}")
            return None
            
    def aws_translate(self, text, from_lang, to_lang):
        """调用AWS Translate API"""
        try:
            import boto3
            
            client = boto3.client('translate',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            response = client.translate_text(
                Text=text,
                SourceLanguageCode=from_lang,
                TargetLanguageCode=to_lang
            )
            return response
        except Exception as e:
            print(f"AWS翻译请求错误: {str(e)}")
            return None
            
    def caiyun_translate(self, text, from_lang, to_lang):
        """调用彩云小译API"""
        try:
            url = "http://api.interpreter.caiyunai.com/v1/translator"
            payload = {
                "source": text,
                "trans_type": f"{from_lang}2{to_lang}",
                "request_id": "demo",
                "detect": True,
            }
            headers = {
                "content-type": "application/json",
                "x-authorization": f"token {self.caiyun_token}"
            }
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"彩云小译请求错误: {str(e)}")
            return None
            
    def niutrans_translate(self, text, from_lang, to_lang):
        """调用小牛翻译API"""
        try:
            url = "http://api.niutrans.com/NiuTransServer/translation"
            params = {
                "apikey": self.niutrans_key,
                "src_text": text,
                "from": from_lang,
                "to": to_lang
            }
            response = requests.post(url, data=params)
            return response.json()
        except Exception as e:
            print(f"小牛翻译请求错误: {str(e)}")
            return None
    
    def init_ui(self):
        # 创建主布局
        left_frame = ttk.Frame(self.window)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = ttk.Frame(self.window)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        # 添加界面语言选择
        lang_frame = ttk.Frame(left_frame)
        lang_frame.pack(anchor=tk.NE, pady=5)
        
        ttk.Label(lang_frame, text=self.ui_languages[self.current_ui_lang]['ui_language']).pack(side=tk.LEFT)
        self.ui_lang_select = ttk.Combobox(lang_frame, values=list(self.ui_languages.keys()), width=10)
        self.ui_lang_select.set(self.current_ui_lang)
        self.ui_lang_select.pack(side=tk.LEFT, padx=5)
        self.ui_lang_select.bind('<<ComboboxSelected>>', self.change_ui_language)
        
        # 添加API设置按钮
        api_button = ttk.Button(left_frame, text=self.ui_languages[self.current_ui_lang]['api_settings'], 
                               command=self.show_api_settings)
        api_button.pack(anchor=tk.NE, pady=5)
        
        # 左侧：翻译区域
        # 语言选择框
        frame_langs = ttk.Frame(left_frame)
        frame_langs.pack(pady=10)
        
        # 源语言标签和选择框
        source_lang_label = ttk.Label(frame_langs, text=self.ui_languages[self.current_ui_lang]['source_lang'])
        source_lang_label.pack(side=tk.LEFT)
        self.source_lang = ttk.Combobox(frame_langs, values=[self.ui_languages[self.current_ui_lang]['languages'][lang] for lang in self.supported_languages.keys()])
        self.source_lang.set(self.ui_languages[self.current_ui_lang]['languages']['Chinese (Simplified)'])
        self.source_lang.pack(side=tk.LEFT, padx=5)
        
        # 目标语言标签和选择框
        target_lang_label = ttk.Label(frame_langs, text=self.ui_languages[self.current_ui_lang]['target_lang'])
        target_lang_label.pack(side=tk.LEFT)
        self.target_lang = ttk.Combobox(frame_langs, values=[self.ui_languages[self.current_ui_lang]['languages'][lang] for lang in self.supported_languages.keys()])
        self.target_lang.set(self.ui_languages[self.current_ui_lang]['languages']['English'])
        self.target_lang.pack(side=tk.LEFT, padx=5)
        
        # 翻译源标签和选择框
        trans_source_label = ttk.Label(frame_langs, text=self.ui_languages[self.current_ui_lang]['trans_source'])
        trans_source_label.pack(side=tk.LEFT)
        
        # 获取翻译源的显示名称列表
        source_display_names = [
            self.ui_languages[self.current_ui_lang]['smart_select'],
            self.ui_languages[self.current_ui_lang]['local_package']
        ]
        source_display_names.extend([
            self.ui_languages[self.current_ui_lang]['translation_sources'][key] for key in [
                'DeepL翻译', '谷歌翻译', '百度翻译', '有道翻译',
                '微软翻译', '腾讯翻译', 'AWS翻译', '彩云翻译', '小牛翻译'
            ]
        ])
        
        self.translation_sources = {
            self.ui_languages[self.current_ui_lang]['smart_select']: 'auto',
            self.ui_languages[self.current_ui_lang]['local_package']: 'local'
        }
        
        # 添加翻译源映射
        for key in ['DeepL翻译', '谷歌翻译', '百度翻译', '有道翻译',
                   '微软翻译', '腾讯翻译', 'AWS翻译', '彩云翻译', '小牛翻译']:
            display_name = self.ui_languages[self.current_ui_lang]['translation_sources'][key]
            source_code = {
                'DeepL翻译': 'deepl',
                '谷歌翻译': 'google',
                '百度翻译': 'baidu',
                '有道翻译': 'youdao',
                '微软翻译': 'azure',
                '腾讯翻译': 'tencent',
                'AWS翻译': 'aws',
                '彩云翻译': 'caiyun',
                '小牛翻译': 'niutrans'
            }[key]
            self.translation_sources[display_name] = source_code
        
        self.selected_source = ttk.Combobox(frame_langs, values=source_display_names, width=15)
        self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        self.selected_source.pack(side=tk.LEFT, padx=5)
        
        # 绑定翻译源选择事件
        self.selected_source.bind('<<ComboboxSelected>>', self.on_source_selected)
        
        # 自动检测语言复选框
        self.auto_detect = tk.BooleanVar(value=True)
        self.auto_detect_cb = ttk.Checkbutton(
            frame_langs,
            text=self.ui_languages[self.current_ui_lang]['auto_detect'],
            variable=self.auto_detect
        )
        self.auto_detect_cb.pack(side=tk.LEFT, padx=5)
        
        # 文本显示区域（翻译结果）
        result_labelframe = ttk.LabelFrame(left_frame, text=self.ui_languages[self.current_ui_lang]['trans_result'])
        result_labelframe.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # 创建带滚动条的翻译结果区域
        result_scroll = ttk.Scrollbar(result_labelframe)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(result_labelframe, height=15, undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # 连接滚动条和文本区域
        self.text_area.config(yscrollcommand=result_scroll.set)
        result_scroll.config(command=self.text_area.yview)
        
        # 麦克风和语音设置
        settings_frame = ttk.Frame(left_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 麦克风选择
        frame_mic = ttk.Frame(settings_frame)
        frame_mic.pack(side=tk.LEFT, padx=5)
        
        # 麦克风选择标签
        mic_label = ttk.Label(frame_mic, text=self.ui_languages[self.current_ui_lang]['select_mic'])
        mic_label.pack(side=tk.LEFT)
        
        # 麦克风选择下拉框
        self.mic_select = ttk.Combobox(frame_mic, values=self.mic_list, width=25)
        if self.mic_list:
            self.mic_select.set(self.mic_list[0])
        self.mic_select.pack(side=tk.LEFT, padx=5)
        
        # 语音输出设置
        frame_voice = ttk.Frame(settings_frame)
        frame_voice.pack(side=tk.LEFT, padx=5)
        
        # 启用语音输出复选框
        self.voice_output_enabled = tk.BooleanVar(value=True)
        self.voice_checkbox = ttk.Checkbutton(
            frame_voice,
            text=self.ui_languages[self.current_ui_lang]['enable_voice'],
            variable=self.voice_output_enabled
        )
        self.voice_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 语音选择和速度设置
        if self.voice_list:
            # 语音选择标签
            voice_label = ttk.Label(frame_voice, text=self.ui_languages[self.current_ui_lang]['select_voice'])
            voice_label.pack(side=tk.LEFT)
            
            # 语音选择下拉框
            self.voice_select = ttk.Combobox(frame_voice, values=self.voice_list, width=25)
            self.voice_select.set(self.voice_list[0])
            self.voice_select.pack(side=tk.LEFT, padx=5)
            
            # 语速标签
            speed_label = ttk.Label(frame_voice, text=self.ui_languages[self.current_ui_lang]['voice_speed'])
            speed_label.pack(side=tk.LEFT)
            
            # 语速滑块
            self.rate_scale = ttk.Scale(
                frame_voice,
                from_=50,
                to=300,
                orient=tk.HORIZONTAL,
                length=100
            )
            self.rate_scale.set(150)
            self.rate_scale.pack(side=tk.LEFT, padx=5)
        
        # 添加文本输入区域
        input_labelframe = ttk.LabelFrame(left_frame, text=self.ui_languages[self.current_ui_lang]['text_input'])
        input_labelframe.pack(fill=tk.X, pady=5, padx=5)
        
        frame_input = ttk.Frame(input_labelframe)
        frame_input.pack(fill=tk.X, pady=5, padx=5)
        
        # 创建带滚动条的文本输入区域
        input_scroll = ttk.Scrollbar(frame_input)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.input_area = tk.Text(frame_input, height=4, undo=True)
        self.input_area.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 连接滚动条和文本区域
        self.input_area.config(yscrollcommand=input_scroll.set)
        input_scroll.config(command=self.input_area.yview)
        
        # 添加翻译按钮和快捷键提示
        button_frame = ttk.Frame(input_labelframe)
        button_frame.pack(fill=tk.X, pady=(0, 5), padx=5)
        
        shortcut_label = ttk.Label(button_frame, text=self.ui_languages[self.current_ui_lang]['shortcut'])
        shortcut_label.pack(side=tk.LEFT)
        
        self.translate_button = ttk.Button(
            button_frame,
            text=self.ui_languages[self.current_ui_lang]['translate_btn'],
            command=self.translate_input_text
        )
        self.translate_button.pack(side=tk.RIGHT)
        
        # 添加快捷键绑定
        self.input_area.bind('<Control-Return>', lambda e: self.translate_input_text())
        
        # 录音按钮
        self.record_button = ttk.Button(left_frame, text=self.ui_languages[self.current_ui_lang]['start_record'], command=self.toggle_recording)
        self.record_button.pack(pady=5)
        
        # 右侧：历史记录
        ttk.Label(right_frame, text=self.ui_languages[self.current_ui_lang]['history'], font=('Arial', 12, 'bold')).pack(pady=5)
        self.history_area = tk.Text(right_frame, width=30, height=30)
        self.history_area.pack(fill=tk.BOTH, expand=True)
        self.update_history_display()
    
    def update_history_display(self):
        """更新历史记录显示"""
        self.history_area.delete(1.0, tk.END)
        history = self.context.get_context()
        for text, translation in reversed(history):  # 显示最近的记录
            self.history_area.insert(tk.END, f"{self.ui_languages[self.current_ui_lang]['original']}: {text}\n")
            self.history_area.insert(tk.END, f"{self.ui_languages[self.current_ui_lang]['translation']}: {translation}\n")
            self.history_area.insert(tk.END, "-" * 30 + "\n")
    
    def detect_language(self, audio):
        """检测音频语言，返回语言和置信度"""
        try:
            # 尝试用不同的语言识别
            results = []
            
            for lang_name, lang_code in self.supported_languages.items():
                try:
                    text = self.recognizer.recognize_google(audio, language=lang_code, show_all=True)
                    if text and isinstance(text, dict) and text.get('alternative'):
                        for alt in text['alternative']:
                            confidence = alt.get('confidence', 0)
                            transcript = alt.get('transcript', '')
                            if transcript:
                                results.append({
                                    'lang': self.ui_languages[self.current_ui_lang]['languages'][lang_name],
                                    'text': transcript,
                                    'confidence': confidence
                                })
                except:
                    continue
            
            # 按置信度排序
            results.sort(key=lambda x: x['confidence'], reverse=True)
            
            if results:
                return results[0]['lang'], results[0]['text'], results[0]['confidence']
            
            return None, None, 0
            
        except Exception as e:
            print(f"{self.ui_languages[self.current_ui_lang]['error']}: {str(e)}")
            return None, None, 0
    
    def speak_text(self, text, lang):
        """使用语音输出文本"""
        if not self.voice_output_enabled.get() or not self.engine:
            return
            
        try:
            rate = int(self.rate_scale.get())
            self.engine.setProperty('rate', rate)
            
            if self.voice_list:
                voices = self.engine.getProperty('voices')
                selected_voice = voices[self.voice_list.index(self.voice_select.get())]
                self.engine.setProperty('voice', selected_voice.id)
            
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['voice_output_error'].format(str(e)) + "\n")
            self.text_area.see(tk.END)
    
    def toggle_recording(self):
        if not self.is_recording:
            try:
                mic_index = self.mic_list.index(self.mic_select.get())
                self.current_mic = sr.Microphone(device_index=mic_index)
                
                with self.current_mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.is_recording = True
                self.record_button.configure(text=self.ui_languages[self.current_ui_lang]['stop_record'])
                self.recording_thread = threading.Thread(target=self.record_audio)
                self.recording_thread.start()
                
            except Exception as e:
                messagebox.showerror(
                    self.ui_languages[self.current_ui_lang]['error'],
                    self.ui_languages[self.current_ui_lang]['mic_error'].format(str(e))
                )
                self.is_recording = False
                self.record_button.configure(text=self.ui_languages[self.current_ui_lang]['start_record'])
        else:
            self.is_recording = False
            self.record_button.configure(text=self.ui_languages[self.current_ui_lang]['start_record'])
    
    def smart_speech_correction(self, text, language):
        """智能语音识别纠正"""
        # 常见的发音相近词对
        similar_words = {
            'en': {  # 英语发音相近词
                'wall': ['war', 'walk', 'wool'],
                'war': ['wall', 'warm', 'ward'],
                'piece': ['peace', 'peas'],
                'peace': ['piece', 'peas'],
                'right': ['write', 'ride'],
                'write': ['right', 'ride'],
                'there': ['their', 'they\'re'],
                'their': ['there', 'they\'re'],
                'here': ['hear', 'hair'],
                'hear': ['here', 'hair'],
                'buy': ['by', 'bye'],
                'by': ['buy', 'bye'],
                'know': ['no', 'now'],
                'no': ['know', 'now'],
                'sea': ['see', 'she'],
                'see': ['sea', 'she']
            },
            'zh-CN': {  # 中文发音相近词
                '是': ['事', '市', '式'],
                '事': ['是', '市', '式'],
                '在': ['再', '载'],
                '再': ['在', '载'],
                '给': ['及', '级'],
                '及': ['给', '级'],
                '和': ['河', '合'],
                '河': ['和', '合'],
                '地': ['的', '得'],
                '的': ['地', '得']
            }
        }
        
        # 语言特定的上下文关键词
        context_keywords = {
            'en': {
                'wall': ['build', 'brick', 'stone', 'paint', 'house', 'room'],
                'war': ['fight', 'battle', 'army', 'soldier', 'peace'],
                'peace': ['war', 'treaty', 'agreement', 'quiet', 'calm'],
                'piece': ['part', 'slice', 'portion', 'cake', 'puzzle']
            },
            'zh-CN': {
                '是': ['对', '正确', '确实', '就是'],
                '事': ['工作', '办', '处理', '事情'],
                '在': ['位于', '存在', '正在'],
                '再': ['还要', '又', '重新']
            }
        }
        
        words = text.lower().split()
        corrected_words = []
        
        # 获取最近的上下文
        recent_texts = [t[0].lower() for t in self.context.get_context()[-3:]]
        context_text = ' '.join(recent_texts + [text.lower()])
        
        for word in words:
            if language in similar_words and word in similar_words[language]:
                candidates = similar_words[language][word]
                best_word = word
                max_score = 0
                
                for candidate in candidates:
                    score = 0
                    # 检查上下文关键词
                    if language in context_keywords and candidate in context_keywords[language]:
                        for keyword in context_keywords[language][candidate]:
                            if keyword in context_text:
                                score += 1
                    
                    # 检查最近的翻译历史
                    for hist_text in recent_texts:
                        if candidate in hist_text:
                            score += 0.5
                    
                    if score > max_score:
                        max_score = score
                        best_word = candidate
                
                corrected_words.append(best_word)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

    def record_audio(self):
        try:
            with self.current_mic as source:
                while self.is_recording:
                    try:
                        self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['listening'] + "\n")
                        self.text_area.see(tk.END)
                        
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # 获取源语言和文本
                        if self.auto_detect.get():
                            detected_lang, text, speech_confidence = self.detect_language(audio)
                            if detected_lang:
                                self.source_lang.set(detected_lang)
                                self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['recognition_conf'] + 
                                                   f"{speech_confidence:.2%}\n")
                            else:
                                # 如果检测失败，使用选定的源语言
                                source_lang = self.get_lang_code(self.source_lang.get())
                                text = self.recognizer.recognize_google(audio, language=source_lang)
                        else:
                            source_lang = self.get_lang_code(self.source_lang.get())
                            text = self.recognizer.recognize_google(audio, language=source_lang)
                        
                        if not text:
                            continue
                        
                        # 智能纠正识别结果
                        source_lang = self.supported_languages[self.source_lang.get()]
                        corrected_text = self.smart_speech_correction(text, source_lang)
                        
                        # 如果纠正后的文本与原文不同，显示提示
                        if corrected_text != text:
                            self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['original_text'] + f"{text}\n")
                            self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['smart_correction'] + f"{corrected_text}\n")
                            text = corrected_text
                        
                        # 翻译文本
                        target_lang = self.supported_languages[self.target_lang.get()]
                        translation_result = self.translate_text(text, source_lang, target_lang)
                        
                        if translation_result:
                            translated_text = translation_result['text']
                            confidence = translation_result['confidence']
                            source = translation_result['source']
                            
                            # 更新UI
                            result_text = self.ui_languages[self.current_ui_lang]['source_text'].format(self.source_lang.get()) + text + "\n"
                            result_text += self.ui_languages[self.current_ui_lang]['target_text'].format(self.target_lang.get()) + translated_text + "\n"
                            result_text += self.ui_languages[self.current_ui_lang]['translation_source'] + source + "\n"
                            if confidence:
                                result_text += self.ui_languages[self.current_ui_lang]['translation_confidence'] + f"{confidence:.2%}\n"
                            result_text += "\n"
                            
                            self.text_area.insert(tk.END, result_text)
                            self.text_area.see(tk.END)
                            
                            # 保存历史记录
                            self.context.add_context(text, translated_text)
                            self.update_history_display()
                            
                            # 语音输出翻译结果
                            self.speak_text(translated_text, target_lang)
                        else:
                            self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['trans_failed'] + "\n")
                            self.text_area.see(tk.END)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['recognition_error'] + "\n")
                        self.text_area.see(tk.END)
                    except Exception as e:
                        self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['error'] + f": {str(e)}\n")
                        self.text_area.see(tk.END)
        except Exception as e:
            messagebox.showerror(
                self.ui_languages[self.current_ui_lang]['error'],
                self.ui_languages[self.current_ui_lang]['recording_error'].format(str(e))
            )
            self.is_recording = False
            self.record_button.configure(text=self.ui_languages[self.current_ui_lang]['start_record'])
    
    def translate_input_text(self):
        """处理文本输入翻译"""
        try:
            # 获取输入文本
            text = self.input_area.get("1.0", tk.END).strip()
            if not text:
                messagebox.showinfo(
                    self.ui_languages[self.current_ui_lang]['warning'],
                    self.ui_languages[self.current_ui_lang]['input_prompt']
                )
                return
            
            # 禁用翻译按钮，防止重复点击
            self.translate_button.configure(state='disabled')
            
            # 显示翻译中提示
            self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['translating'] + "\n")
            self.text_area.see(tk.END)
            
            # 在新线程中执行翻译
            threading.Thread(target=self._async_translate_text, args=(text,), daemon=True).start()
            
        except Exception as e:
            error_msg = self.ui_languages[self.current_ui_lang]['processing_error'].format(str(e)) + "\n"
            self.text_area.insert(tk.END, error_msg)
            self.text_area.see(tk.END)
            self.translate_button.configure(state='normal')

    def _async_translate_text(self, text):
        """异步执行翻译过程"""
        try:
            # 获取源语言和目标语言
            source_lang = self.get_lang_code(self.source_lang.get())
            target_lang = self.get_lang_code(self.target_lang.get())
            
            # 如果启用了自动检测，尝试检测语言
            if self.auto_detect.get():
                try:
                    # 使用选定的翻译源进行语言检测
                    selected_source = self.translation_sources[self.selected_source.get()]
                    if selected_source == 'google':
                        translator = GoogleTranslator()
                        detected_info = translator.detect(text)
                        if detected_info and detected_info.lang:
                            for lang_name, lang_code in self.supported_languages.items():
                                if lang_code == detected_info.lang:
                                    self.window.after(0, lambda: self.source_lang.set(self.ui_languages[self.current_ui_lang]['languages'][lang_name]))
                                    source_lang = lang_code
                                    break
                except Exception as e:
                    print(f"{self.ui_languages[self.current_ui_lang]['error']}: {str(e)}")
            
            # 使用选定的翻译源进行翻译
            translation_result = self.translate_text(text, source_lang, target_lang)
            
            if translation_result:
                self._handle_translation_result(translation_result, text, target_lang)
            else:
                self.window.after(0, lambda: self.text_area.insert(tk.END, self.ui_languages[self.current_ui_lang]['trans_failed'] + "\n"))
                self.window.after(0, lambda: self.text_area.see(tk.END))
            
        except Exception as e:
            error_msg = self.ui_languages[self.current_ui_lang]['processing_error'].format(str(e)) + "\n"
            self.window.after(0, lambda: self.text_area.insert(tk.END, error_msg))
            self.window.after(0, lambda: self.text_area.see(tk.END))
        finally:
            # 恢复翻译按钮状态
            self.window.after(0, lambda: self.translate_button.configure(state='normal'))

    def _handle_translation_result(self, result, original_text, target_lang):
        """处理翻译结果"""
        def update_ui():
            try:
                # 确保结果是字典格式
                if isinstance(result, tuple):
                    translated_text = result[0]
                    confidence = result[1]
                    source = self.ui_languages[self.current_ui_lang]['unknown_source']
                elif isinstance(result, dict):
                    translated_text = result.get('text', '')
                    confidence = result.get('confidence', 0.0)
                    source = result.get('source', self.ui_languages[self.current_ui_lang]['unknown_source'])
                else:
                    translated_text = str(result)
                    confidence = 0.0
                    source = self.ui_languages[self.current_ui_lang]['unknown_source']
                
                # 更新UI
                result_text = self.ui_languages[self.current_ui_lang]['source_text'].format(self.source_lang.get()) + original_text + "\n"
                result_text += self.ui_languages[self.current_ui_lang]['target_text'].format(self.target_lang.get()) + translated_text + "\n"
                result_text += self.ui_languages[self.current_ui_lang]['translation_source'] + source + "\n"
                if confidence:
                    result_text += self.ui_languages[self.current_ui_lang]['translation_confidence'] + f"{confidence:.2%}\n"
                result_text += "\n"
                
                self.text_area.insert(tk.END, result_text)
                self.text_area.see(tk.END)
                
                # 更新历史记录
                self.context.add_context(original_text, translated_text)
                self.update_history_display()
                
                # 语音输出翻译结果
                if self.voice_output_enabled.get():
                    self.speak_text(translated_text, target_lang)
                
                # 清空输入框
                self.input_area.delete("1.0", tk.END)
            except Exception as e:
                error_msg = self.ui_languages[self.current_ui_lang]['processing_error'].format(str(e)) + "\n"
                self.text_area.insert(tk.END, error_msg)
                self.text_area.see(tk.END)
        
        # 在主线程中更新UI
        self.window.after(0, update_ui)

    def on_source_selected(self, event):
        """处理翻译源选择事件"""
        selected = self.selected_source.get()
        source_code = self.translation_sources.get(selected)
        
        # 检查选择的翻译源是否可用
        if source_code == 'deepl' and not self.deepl_translator:
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'baidu' and not (self.baidu_app_id and self.baidu_secret_key):
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'youdao' and not (self.youdao_app_key and self.youdao_app_secret):
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'azure' and not self.azure_key:
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['微软翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'tencent' and not (self.tencent_secret_id and self.tencent_secret_key):
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['腾讯翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'aws' and not (self.aws_access_key and self.aws_secret_key):
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['AWS翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'caiyun' and not self.caiyun_token:
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['彩云翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])
        elif source_code == 'niutrans' and not self.niutrans_key:
            messagebox.showwarning(
                self.ui_languages[self.current_ui_lang]['warning'],
                self.ui_languages[self.current_ui_lang]['api_not_configured'].format(
                    self.ui_languages[self.current_ui_lang]['translation_sources']['小牛翻译']
                )
            )
            self.selected_source.set(self.ui_languages[self.current_ui_lang]['smart_select'])

    def run(self):
        self.window.mainloop()

    def smart_translate(self, text, source_lang, target_lang):
        """智能翻译：根据文本特点选择最合适的翻译源"""
        try:
            translations = []
            confidence_scores = []
            translation_sources = []
            
            # 1. 首先检查是否是常用短语
            text_stripped = text.strip()
            if text_stripped in self.phrase_mapping and target_lang in self.phrase_mapping[text_stripped]:
                return {
                    'text': self.phrase_mapping[text_stripped][target_lang],
                    'confidence': 1.0,
                    'source': self.ui_languages[self.current_ui_lang]['local_package']
                }
            
            # 2. 尝试使用DeepL翻译（高质量但较慢）
            if self.deepl_translator:
                try:
                    deepl_lang_map = {
                        'zh-CN': 'zh',
                        'zh-TW': 'zh',
                        'en': 'en-US',
                        'ja': 'ja',
                        'ko': 'ko',
                        'fr': 'fr',
                        'de': 'de',
                        'es': 'es',
                        'ru': 'ru'
                    }
                    source_lang_code = deepl_lang_map.get(source_lang)       
                    target_lang_code = deepl_lang_map.get(target_lang)
                    if source_lang_code and target_lang_code:
                        result = self.deepl_translator.translate_text(
                            text,
                            source_lang=source_lang_code,
                            target_lang=target_lang_code
                        )
                        if result:
                            translations.append(result.text)
                            confidence_scores.append(0.95)  # DeepL通常质量较高
                            translation_sources.append(self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译'])
                except Exception as e:
                    print(f"DeepL翻译错误: {str(e)}")
            
            # 3. 尝试使用谷歌翻译（速度快）
            try:
                translator = GoogleTranslator()
                result = translator.translate(text, src=source_lang, dest=target_lang)
                if result and result.text:
                    translations.append(result.text)
                    # 根据文本长度和复杂度调整置信度
                    complexity = len(text.split()) + len([c for c in text if c in ',.!?;:'])
                    confidence = 0.85 if complexity > 5 else 0.8
                    confidence_scores.append(confidence)
                    translation_sources.append(self.ui_languages[self.current_ui_lang]['translation_sources']['谷歌翻译'])
            except Exception as e:
                print(f"谷歌翻译错误: {str(e)}")
            
            # 4. 尝试使用百度翻译（适合中文）
            if self.baidu_app_id and self.baidu_secret_key:
                try:
                    baidu_result = self.baidu_translate(text, source_lang, target_lang)
                    if baidu_result and 'trans_result' in baidu_result:
                        translations.append(baidu_result['trans_result'][0]['dst'])
                        # 中文相关翻译给予更高置信度
                        is_chinese = 'zh' in source_lang or 'zh' in target_lang
                        confidence = 0.9 if is_chinese else 0.75
                        confidence_scores.append(confidence)
                        translation_sources.append(self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译'])
                except Exception as e:
                    print(f"百度翻译错误: {str(e)}")
            
            # 5. 尝试使用有道翻译（补充）
            if self.youdao_app_key and self.youdao_app_secret:
                try:
                    youdao_result = self.youdao_translate(text, source_lang, target_lang)
                    if youdao_result and 'translation' in youdao_result:
                        translations.append(youdao_result['translation'][0])
                        # 根据文本特征调整置信度
                        is_short = len(text.split()) <= 3
                        confidence = 0.85 if is_short else 0.7
                        confidence_scores.append(confidence)
                        translation_sources.append(self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译'])
                except Exception as e:
                    print(f"有道翻译错误: {str(e)}")
            
            # 如果有多个翻译结果，进行智能合并
            if translations:
                # 计算每个翻译的出现次数
                translation_counts = {}
                for t in translations:
                    translation_counts[t] = translation_counts.get(t, 0) + 1
                
                # 选择最佳翻译
                best_translation = None
                best_confidence = 0
                best_source = None
                
                for i, translation in enumerate(translations):
                    # 基础置信度
                    base_confidence = confidence_scores[i]
                    
                    # 根据多个翻译源的一致性调整置信度
                    agreement_bonus = (translation_counts[translation] - 1) * 0.1
                    
                    # 根据翻译源的特点调整置信度
                    source_weight = {
                        self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']: 1.1,
                        self.ui_languages[self.current_ui_lang]['translation_sources']['谷歌翻译']: 1.0,
                        self.ui_languages[self.current_ui_lang]['translation_sources']['百度翻译']: 1.0 if 'zh' in source_lang or 'zh' in target_lang else 0.9,
                        self.ui_languages[self.current_ui_lang]['translation_sources']['有道翻译']: 0.9
                    }.get(translation_sources[i], 1.0)
                    
                    # 计算最终置信度
                    final_confidence = min(1.0, base_confidence * source_weight + agreement_bonus)
                    
                    if final_confidence > best_confidence:
                        best_confidence = final_confidence
                        best_translation = translation
                        best_source = translation_sources[i]
                
                return {
                    'text': best_translation,
                    'confidence': best_confidence,
                    'source': best_source
                }
            
            # 如果所有翻译源都失败了，返回错误信息
            return {
                'text': self.ui_languages[self.current_ui_lang]['all_failed'],
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['error']
            }
        
        except Exception as e:
            return {
                'text': self.ui_languages[self.current_ui_lang]['processing_error'].format(str(e)),
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['error']
            }

    def google_translate(self, text, source_lang, target_lang):
        """使用谷歌翻译API"""
        try:
            from googletrans import Translator
            translator = Translator()
            
            # 语言代码映射
            lang_map = {
                'zh-CN': 'zh-cn',
                'zh-TW': 'zh-tw',
                'en': 'en',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru'
            }
            
            # 转换语言代码
            source_lang = lang_map.get(source_lang, source_lang)
            target_lang = lang_map.get(target_lang, target_lang)
            
            # 如果源语言是auto，则让谷歌自动检测
            if source_lang == 'auto' or not source_lang:
                source_lang = 'auto'
            
            result = translator.translate(text, src=source_lang, dest=target_lang)
            if result and hasattr(result, 'text') and result.text:
                # 根据文本长度和复杂度调整置信度
                complexity = len(text.split()) + len([c for c in text if c in ',.!?;:'])
                confidence = 0.85 if complexity > 5 else 0.8
                return {
                    'text': result.text,
                    'confidence': confidence,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['谷歌翻译']
                }
            return {
                'text': self.ui_languages[self.current_ui_lang]['trans_failed'],
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['translation_sources']['谷歌翻译']
            }
        except Exception as e:
            print(f"{self.ui_languages[self.current_ui_lang]['translation_sources']['谷歌翻译']}{self.ui_languages[self.current_ui_lang]['error']}: {str(e)}")
            return {
                'text': f'{self.ui_languages[self.current_ui_lang]["translation_sources"]["谷歌翻译"]}{self.ui_languages[self.current_ui_lang]["error"]}: {str(e)}',
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['translation_sources']['谷歌翻译']
            }

    def deepl_translate(self, text, source_lang, target_lang):
        """使用DeepL翻译API"""
        try:
            if not self.deepl_translator:
                return {
                    'text': self.ui_languages[self.current_ui_lang]['api_not_configured'].format(self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']),
                    'confidence': 0.0,
                    'source': self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']
                }
            
            deepl_lang_map = {
                'zh-CN': 'zh',
                'zh-TW': 'zh',
                'en': 'en-US',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru'
            }
            source_lang_code = deepl_lang_map.get(source_lang)
            target_lang_code = deepl_lang_map.get(target_lang)
            
            if source_lang_code and target_lang_code:
                result = self.deepl_translator.translate_text(
                    text,
                    source_lang=source_lang_code,
                    target_lang=target_lang_code
                )
                if result:
                    return {
                        'text': result.text,
                        'confidence': 0.95,
                        'source': self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']
                    }
            return {
                'text': self.ui_languages[self.current_ui_lang]['trans_failed'],
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']
            }
        except Exception as e:
            print(f"{self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']}{self.ui_languages[self.current_ui_lang]['error']}: {str(e)}")
            return {
                'text': f'{self.ui_languages[self.current_ui_lang]["translation_sources"]["DeepL翻译"]}{self.ui_languages[self.current_ui_lang]["error"]}: {str(e)}',
                'confidence': 0.0,
                'source': self.ui_languages[self.current_ui_lang]['translation_sources']['DeepL翻译']
            }

    def show_api_settings(self):
        """显示API设置窗口"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title(self.ui_languages[self.current_ui_lang]['api_settings'])
        settings_window.geometry('600x400')
        
        # 创建滚动框架
        canvas = tk.Canvas(settings_window)
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # API设置项
        api_settings = [
            (self.ui_languages[self.current_ui_lang]['deepl_key'], 'DEEPL_API_KEY', self.deepl_api_key),
            (self.ui_languages[self.current_ui_lang]['baidu_app_id'], 'BAIDU_APP_ID', self.baidu_app_id),
            (self.ui_languages[self.current_ui_lang]['baidu_secret'], 'BAIDU_SECRET_KEY', self.baidu_secret_key),
            (self.ui_languages[self.current_ui_lang]['youdao_app_key'], 'YOUDAO_APP_KEY', self.youdao_app_key),
            (self.ui_languages[self.current_ui_lang]['youdao_secret'], 'YOUDAO_APP_SECRET', self.youdao_app_secret),
            (self.ui_languages[self.current_ui_lang]['azure_key'], 'AZURE_TRANSLATOR_KEY', self.azure_key),
            (self.ui_languages[self.current_ui_lang]['azure_region'], 'AZURE_TRANSLATOR_REGION', self.azure_region),
            (self.ui_languages[self.current_ui_lang]['azure_endpoint'], 'AZURE_TRANSLATOR_ENDPOINT', self.azure_endpoint),
            (self.ui_languages[self.current_ui_lang]['tencent_id'], 'TENCENT_SECRET_ID', self.tencent_secret_id),
            (self.ui_languages[self.current_ui_lang]['tencent_key'], 'TENCENT_SECRET_KEY', self.tencent_secret_key),
            (self.ui_languages[self.current_ui_lang]['aws_access'], 'AWS_ACCESS_KEY', self.aws_access_key),
            (self.ui_languages[self.current_ui_lang]['aws_secret'], 'AWS_SECRET_KEY', self.aws_secret_key),
            (self.ui_languages[self.current_ui_lang]['aws_region'], 'AWS_REGION', self.aws_region),
            (self.ui_languages[self.current_ui_lang]['caiyun_token'], 'CAIYUN_TOKEN', self.caiyun_token),
            (self.ui_languages[self.current_ui_lang]['niutrans_key'], 'NIUTRANS_KEY', self.niutrans_key)
        ]
        
        # 创建输入框和标签
        entries = {}
        for i, (label_text, env_key, current_value) in enumerate(api_settings):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=label_text + ":").pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=50)
            entry.pack(side=tk.LEFT, padx=5)
            if current_value:
                entry.insert(0, current_value)
            entries[env_key] = entry
        
        def save_settings():
            # 读取现有的.env文件内容
            env_content = {}
            if os.path.exists('.env'):
                with open('.env', 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            env_content[key] = value
            
            # 更新值
            for env_key, entry in entries.items():
                value = entry.get().strip()
                if value:
                    env_content[env_key] = value
            
            # 保存到.env文件
            with open('.env', 'w', encoding='utf-8') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
            
            # 重新初始化翻译服务
            self.init_translation_services()
            messagebox.showinfo(
                self.ui_languages[self.current_ui_lang]['success'],
                self.ui_languages[self.current_ui_lang]['settings_saved']
            )
            settings_window.destroy()
        
        # 保存按钮
        save_button = ttk.Button(
            scrollable_frame,
            text=self.ui_languages[self.current_ui_lang]['save_settings'],
            command=save_settings
        )
        save_button.pack(pady=10)
        
        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def change_ui_language(self, event=None):
        """切换界面语言"""
        new_lang = self.ui_lang_select.get()
        if new_lang != self.current_ui_lang:
            old_lang = self.current_ui_lang
            self.current_ui_lang = new_lang
            ui_text = self.ui_languages[new_lang]
            
            # 更新窗口标题
            self.window.title(ui_text['title'])
            
            # 更新语言选择框的值
            self.source_lang['values'] = [ui_text['languages'][lang] for lang in self.supported_languages.keys()]
            self.target_lang['values'] = [ui_text['languages'][lang] for lang in self.supported_languages.keys()]
            
            # 保持当前选择的语言
            current_source = self.source_lang.get()
            current_target = self.target_lang.get()
            
            # 找到当前语言在旧语言配置中的键
            old_source_key = None
            old_target_key = None
            for lang_key, lang_text in self.ui_languages[old_lang]['languages'].items():
                if current_source == lang_text:
                    old_source_key = lang_key
                if current_target == lang_text:
                    old_target_key = lang_key
            
            # 使用找到的键来设置新的语言文本
            if old_source_key:
                self.source_lang.set(ui_text['languages'][old_source_key])
            if old_target_key:
                self.target_lang.set(ui_text['languages'][old_target_key])
            
            # 更新翻译源选择框
            current_source = self.selected_source.get()
            
            # 获取翻译源的显示名称列表
            source_display_names = [
                ui_text['smart_select'],
                ui_text['local_package']
            ]
            source_display_names.extend([
                ui_text['translation_sources'][key] for key in [
                    'DeepL翻译', '谷歌翻译', '百度翻译', '有道翻译',
                    '微软翻译', '腾讯翻译', 'AWS翻译', '彩云翻译', '小牛翻译'
                ]
            ])
            
            # 更新翻译源映射
            self.translation_sources = {
                ui_text['smart_select']: 'auto',
                ui_text['local_package']: 'local'
            }
            
            # 添加翻译源映射
            for key in ['DeepL翻译', '谷歌翻译', '百度翻译', '有道翻译',
                       '微软翻译', '腾讯翻译', 'AWS翻译', '彩云翻译', '小牛翻译']:
                display_name = ui_text['translation_sources'][key]
                source_code = {
                    'DeepL翻译': 'deepl',
                    '谷歌翻译': 'google',
                    '百度翻译': 'baidu',
                    '有道翻译': 'youdao',
                    '微软翻译': 'azure',
                    '腾讯翻译': 'tencent',
                    'AWS翻译': 'aws',
                    '彩云翻译': 'caiyun',
                    '小牛翻译': 'niutrans'
                }[key]
                self.translation_sources[display_name] = source_code
            
            self.selected_source['values'] = source_display_names
            
            # 更新当前选择的翻译源
            if current_source == self.ui_languages[old_lang]['smart_select']:
                self.selected_source.set(ui_text['smart_select'])
            elif current_source == self.ui_languages[old_lang]['local_package']:
                self.selected_source.set(ui_text['local_package'])
            else:
                # 查找对应的翻译源名称
                for key in ['DeepL翻译', '谷歌翻译', '百度翻译', '有道翻译',
                          '微软翻译', '腾讯翻译', 'AWS翻译', '彩云翻译', '小牛翻译']:
                    if current_source == self.ui_languages[old_lang]['translation_sources'][key]:
                        self.selected_source.set(ui_text['translation_sources'][key])
                        break
            
            # 更新各个控件的文本
            self.translate_button.configure(text=ui_text['translate_btn'])
            self.record_button.configure(text=ui_text['start_record'] if not self.is_recording else ui_text['stop_record'])
            self.auto_detect_cb.configure(text=ui_text['auto_detect'])
            self.voice_checkbox.configure(text=ui_text['enable_voice'])
            
            # 递归更新所有标签文本
            def update_widget_text(widget):
                if isinstance(widget, ttk.Label):
                    current_text = widget.cget('text')
                    # 检查当前文本是否匹配旧语言配置中的任何文本
                    for key in self.ui_languages[old_lang]:
                        if isinstance(self.ui_languages[old_lang][key], str) and current_text == self.ui_languages[old_lang][key]:
                            widget.configure(text=ui_text[key])
                            break
                elif isinstance(widget, ttk.LabelFrame):
                    current_text = widget.cget('text')
                    # 检查当前文本是否匹配旧语言配置中的任何文本
                    for key in self.ui_languages[old_lang]:
                        if isinstance(self.ui_languages[old_lang][key], str) and current_text == self.ui_languages[old_lang][key]:
                            widget.configure(text=ui_text[key])
                            break
                elif isinstance(widget, ttk.Button):
                    current_text = widget.cget('text')
                    # 检查当前文本是否匹配旧语言配置中的任何文本
                    for key in self.ui_languages[old_lang]:
                        if isinstance(self.ui_languages[old_lang][key], str) and current_text == self.ui_languages[old_lang][key]:
                            widget.configure(text=ui_text[key])
                            break
                
                # 递归处理子控件
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        update_widget_text(child)
            
            # 更新所有控件的文本
            update_widget_text(self.window)
            
            # 更新历史记录显示
            self.update_history_display()

    def get_lang_code(self, lang_name):
        """获取语言代码的通用方法"""
        # 如果输入已经是语言代码，直接返回
        if lang_name in self.supported_languages.values():
            return lang_name
        # 从界面语言名称映射到语言代码
        for key, value in self.ui_languages[self.current_ui_lang]['languages'].items():
            if value == lang_name:
                return self.supported_languages.get(key, 'auto')
        return 'auto'

if __name__ == '__main__':
    translator = VoiceTranslator()
    translator.run() 