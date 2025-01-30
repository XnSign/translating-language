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
        
        self.window = tk.Tk()
        self.window.title('留生机demo')
        self.window.geometry('800x600')
        
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        
        # 初始化语音引擎
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.voice_list = [voice.name for voice in voices]
        except Exception as e:
            messagebox.showerror("错误", f"初始化语音输出引擎失败：{str(e)}")
            self.engine = None
            self.voice_list = []
        
        # 检查麦克风
        try:
            self.mic_list = sr.Microphone.list_microphone_names()
            if not self.mic_list:
                messagebox.showerror("错误", "未检测到麦克风设备！请确保麦克风已正确连接。")
                self.window.destroy()
                return
        except Exception as e:
            messagebox.showerror("错误", f"初始化麦克风时出错：{str(e)}\n请检查麦克风是否正确连接和启用。")
            self.window.destroy()
            return
        
        # 支持的语言
        self.supported_languages = {
            '中文(简体)': 'zh-CN',
            '中文(繁体)': 'zh-TW',
            '英语': 'en',
            '日语': 'ja',
            '韩语': 'ko',
            '法语': 'fr',
            '德语': 'de',
            '西班牙语': 'es',
            '俄语': 'ru'
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
        
        self.init_ui()
        
    def init_translation_services(self):
        """初始化所有翻译服务"""
        # Azure 翻译
        self.azure_key = os.getenv('AZURE_TRANSLATOR_KEY')
        self.azure_region = os.getenv('AZURE_TRANSLATOR_REGION')
        self.azure_endpoint = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
        
        # 百度翻译
        self.baidu_app_id = os.getenv('BAIDU_APP_ID')
        self.baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        # 有道翻译
        self.youdao_app_key = os.getenv('YOUDAO_APP_KEY')
        self.youdao_app_secret = os.getenv('YOUDAO_APP_SECRET')
    
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
    
    def translate_text(self, text, source_lang, target_lang):
        """使用多个翻译源进行翻译"""
        translations = []
        confidence_scores = []
        
        # 1. 检查是否有上下文特殊处理
        context_translation = self.analyze_context(text, self.context.get_context())
        if context_translation:
            return {
                'text': context_translation,
                'detected_language': source_lang,
                'confidence': 1.0,
                'source': 'context'
            }
        
        # 2. 尝试使用百度翻译
        if self.baidu_app_id and self.baidu_secret_key:
            try:
                # 百度翻译语言代码映射
                baidu_lang_map = {
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
                
                baidu_result = self.baidu_translate(
                    text,
                    baidu_lang_map.get(source_lang, source_lang),
                    baidu_lang_map.get(target_lang, target_lang)
                )
                if baidu_result and 'trans_result' in baidu_result:
                    translations.append(baidu_result['trans_result'][0]['dst'])
                    confidence_scores.append(0.8)  # 百度翻译默认置信度
            except Exception as e:
                print(f"百度翻译错误: {str(e)}")
        
        # 3. 尝试使用有道翻译
        if self.youdao_app_key and self.youdao_app_secret:
            try:
                # 有道翻译语言代码映射
                youdao_lang_map = {
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
                
                youdao_result = self.youdao_translate(
                    text,
                    youdao_lang_map.get(source_lang, source_lang),
                    youdao_lang_map.get(target_lang, target_lang)
                )
                if youdao_result and 'translation' in youdao_result:
                    translations.append(youdao_result['translation'][0])
                    confidence_scores.append(0.8)  # 有道翻译默认置信度
            except Exception as e:
                print(f"有道翻译错误: {str(e)}")
        
        # 4. 尝试使用Azure翻译
        if self.azure_key:
            try:
                azure_result = self.azure_translate(
                    text,
                    source_lang,  # Azure使用标准语言代码
                    target_lang
                )
                if azure_result:
                    translations.append(azure_result['text'])
                    confidence_scores.append(azure_result.get('confidence', 0.7))
            except Exception as e:
                print(f"Azure翻译错误: {str(e)}")
        
        # 如果有多个翻译结果，选择置信度最高的
        if translations:
            best_index = confidence_scores.index(max(confidence_scores))
            best_translation = translations[best_index]
            
            # 更新上下文
            self.context.add_context(text, best_translation)
            
            return {
                'text': best_translation,
                'detected_language': source_lang,
                'confidence': confidence_scores[best_index],
                'source': ['百度翻译', '有道翻译', 'Azure翻译'][best_index]
            }
        
        return None
    
    def baidu_translate(self, text, from_lang, to_lang):
        """调用百度翻译API"""
        try:
            url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
            salt = str(random.randint(32768, 65536))
            sign = hashlib.md5((self.baidu_app_id + text + salt + self.baidu_secret_key).encode()).hexdigest()
            
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': self.baidu_app_id,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"百度翻译请求错误: {str(e)}")
            return None
    
    def youdao_translate(self, text, from_lang, to_lang):
        """调用有道翻译API"""
        try:
            url = 'https://openapi.youdao.com/api'
            salt = str(int(time.time() * 1000))
            sign_str = self.youdao_app_key + text + salt + self.youdao_app_secret
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appKey': self.youdao_app_key,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"有道翻译请求错误: {str(e)}")
            return None
    
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
    
    def init_ui(self):
        # 创建主布局
        left_frame = ttk.Frame(self.window)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = ttk.Frame(self.window)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        # 左侧：翻译区域
        # 语言选择框
        frame_langs = ttk.Frame(left_frame)
        frame_langs.pack(pady=10)
        
        ttk.Label(frame_langs, text="源语言：").pack(side=tk.LEFT)
        self.source_lang = ttk.Combobox(frame_langs, values=list(self.supported_languages.keys()))
        self.source_lang.set('中文(简体)')
        self.source_lang.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_langs, text="目标语言：").pack(side=tk.LEFT)
        self.target_lang = ttk.Combobox(frame_langs, values=list(self.supported_languages.keys()))
        self.target_lang.set('英语')
        self.target_lang.pack(side=tk.LEFT, padx=5)
        
        # 自动检测语言复选框
        self.auto_detect = tk.BooleanVar(value=True)
        self.auto_detect_cb = ttk.Checkbutton(
            frame_langs,
            text="自动检测语言",
            variable=self.auto_detect
        )
        self.auto_detect_cb.pack(side=tk.LEFT, padx=5)
        
        # 添加文本输入区域（使用LabelFrame使其更明显）
        input_labelframe = ttk.LabelFrame(left_frame, text="文本输入区域")
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
        
        shortcut_label = ttk.Label(button_frame, text="快捷键: Ctrl+Enter", font=('Arial', 8))
        shortcut_label.pack(side=tk.LEFT)
        
        self.translate_button = ttk.Button(
            button_frame,
            text='翻译文本',
            command=self.translate_input_text
        )
        self.translate_button.pack(side=tk.RIGHT)
        
        # 添加快捷键绑定
        self.input_area.bind('<Control-Return>', lambda e: self.translate_input_text())
        
        # 麦克风选择
        frame_mic = ttk.Frame(left_frame)
        frame_mic.pack(pady=5)
        ttk.Label(frame_mic, text="选择麦克风：").pack(side=tk.LEFT)
        self.mic_select = ttk.Combobox(frame_mic, values=self.mic_list)
        if self.mic_list:
            self.mic_select.set(self.mic_list[0])
        self.mic_select.pack(side=tk.LEFT, padx=5)
        
        # 语音输出设置
        frame_voice = ttk.Frame(left_frame)
        frame_voice.pack(pady=5)
        
        self.voice_output_enabled = tk.BooleanVar(value=True)
        self.voice_checkbox = ttk.Checkbutton(
            frame_voice,
            text="启用语音输出",
            variable=self.voice_output_enabled
        )
        self.voice_checkbox.pack(side=tk.LEFT, padx=5)
        
        if self.voice_list:
            ttk.Label(frame_voice, text="选择声音：").pack(side=tk.LEFT)
            self.voice_select = ttk.Combobox(frame_voice, values=self.voice_list)
            self.voice_select.set(self.voice_list[0])
            self.voice_select.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(frame_voice, text="语速：").pack(side=tk.LEFT)
            self.rate_scale = ttk.Scale(
                frame_voice,
                from_=50,
                to=300,
                orient=tk.HORIZONTAL,
                length=100
            )
            self.rate_scale.set(150)
            self.rate_scale.pack(side=tk.LEFT, padx=5)
        
        # 文本显示区域
        self.text_area = tk.Text(left_frame, height=15)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 录音按钮
        self.record_button = ttk.Button(left_frame, text='开始录音', command=self.toggle_recording)
        self.record_button.pack(pady=10)
        
        # 右侧：历史记录
        ttk.Label(right_frame, text="历史记录", font=('Arial', 12, 'bold')).pack(pady=5)
        self.history_area = tk.Text(right_frame, width=30, height=30)
        self.history_area.pack(fill=tk.BOTH, expand=True)
        self.update_history_display()
        
    def update_history_display(self):
        """更新历史记录显示"""
        self.history_area.delete(1.0, tk.END)
        history = self.context.get_context()
        for text, translation in reversed(history):  # 显示最近的记录
            self.history_area.insert(tk.END, f"原文: {text}\n")
            self.history_area.insert(tk.END, f"译文: {translation}\n")
            self.history_area.insert(tk.END, "-" * 30 + "\n")
    
    def detect_language(self, audio):
        """检测音频语言"""
        try:
            # 尝试用不同的语言识别
            best_result = None
            max_confidence = 0
            detected_lang = None
            
            for lang_name, lang_code in self.supported_languages.items():
                try:
                    text = self.recognizer.recognize_google(audio, language=lang_code, show_all=True)
                    if text and isinstance(text, dict) and text.get('alternative'):
                        confidence = text['alternative'][0].get('confidence', 0)
                        if confidence > max_confidence:
                            max_confidence = confidence
                            best_result = text['alternative'][0]['transcript']
                            detected_lang = lang_name
                except:
                    continue
            
            if detected_lang and best_result:
                return detected_lang, best_result
            
            # 如果所有语言都识别失败，返回None
            return None, None
            
        except Exception as e:
            print(f"语言检测错误: {str(e)}")
            return None, None
    
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
            self.text_area.insert(tk.END, f"语音输出错误: {str(e)}\n")
            self.text_area.see(tk.END)
    
    def toggle_recording(self):
        if not self.is_recording:
            try:
                mic_index = self.mic_list.index(self.mic_select.get())
                self.current_mic = sr.Microphone(device_index=mic_index)
                
                with self.current_mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.is_recording = True
                self.record_button.configure(text='停止录音')
                self.recording_thread = threading.Thread(target=self.record_audio)
                self.recording_thread.start()
                
            except Exception as e:
                messagebox.showerror("错误", f"启动录音失败：{str(e)}\n请检查麦克风设置。")
                self.is_recording = False
                self.record_button.configure(text='开始录音')
        else:
            self.is_recording = False
            self.record_button.configure(text='开始录音')
    
    def record_audio(self):
        try:
            with self.current_mic as source:
                while self.is_recording:
                    try:
                        self.text_area.insert(tk.END, "正在听取语音...\n")
                        self.text_area.see(tk.END)
                        
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # 获取源语言和文本
                        if self.auto_detect.get():
                            detected_lang, text = self.detect_language(audio)
                            if detected_lang:
                                self.source_lang.set(detected_lang)
                            else:
                                # 如果检测失败，使用选定的源语言
                                source_lang = self.supported_languages[self.source_lang.get()]
                                text = self.recognizer.recognize_google(audio, language=source_lang)
                        else:
                            source_lang = self.supported_languages[self.source_lang.get()]
                            text = self.recognizer.recognize_google(audio, language=source_lang)
                        
                        if not text:
                            continue
                            
                        # 翻译文本
                        source_lang = self.supported_languages[self.source_lang.get()]
                        target_lang = self.supported_languages[self.target_lang.get()]
                        
                        translation_result = self.translate_text(text, source_lang, target_lang)
                        
                        if translation_result:
                            translated_text = translation_result['text']
                            confidence = translation_result['confidence']
                            
                            # 更新UI
                            result_text = f"原文 ({self.source_lang.get()}): {text}\n"
                            result_text += f"译文 ({self.target_lang.get()}): {translated_text}\n"
                            if confidence:
                                result_text += f"识别置信度: {confidence:.2%}\n"
                            result_text += "\n"
                            
                            self.text_area.insert(tk.END, result_text)
                            self.text_area.see(tk.END)
                            
                            # 保存历史记录
                            self.save_history(
                                text,
                                translated_text,
                                self.source_lang.get(),
                                self.target_lang.get()
                            )
                            self.update_history_display()
                            
                            # 语音输出翻译结果
                            self.speak_text(translated_text, target_lang)
                        else:
                            self.text_area.insert(tk.END, "翻译失败，请重试...\n")
                            self.text_area.see(tk.END)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.text_area.insert(tk.END, "未能识别语音，请重试...\n")
                        self.text_area.see(tk.END)
                    except Exception as e:
                        self.text_area.insert(tk.END, f"错误: {str(e)}\n")
                        self.text_area.see(tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"录音过程出错：{str(e)}")
            self.is_recording = False
            self.record_button.configure(text='开始录音')
    
    def translate_input_text(self):
        """处理文本输入翻译"""
        try:
            # 获取输入文本
            text = self.input_area.get("1.0", tk.END).strip()
            if not text:
                messagebox.showinfo("提示", "请输入要翻译的文本")
                return
            
            # 禁用翻译按钮，防止重复点击
            self.translate_button.configure(state='disabled')
            
            # 显示翻译中提示
            self.text_area.insert(tk.END, "正在翻译...\n")
            self.text_area.see(tk.END)
            
            # 在新线程中执行翻译
            threading.Thread(target=self._async_translate_text, args=(text,), daemon=True).start()
            
        except Exception as e:
            error_msg = f"翻译错误: {str(e)}\n"
            self.text_area.insert(tk.END, error_msg)
            self.text_area.see(tk.END)
            self.translate_button.configure(state='normal')

    def _async_translate_text(self, text):
        """异步执行翻译过程"""
        try:
            # 获取源语言和目标语言
            source_lang = self.supported_languages[self.source_lang.get()]
            target_lang = self.supported_languages[self.target_lang.get()]
            
            # 如果启用了自动检测，尝试检测语言
            if self.auto_detect.get():
                try:
                    # 使用Google翻译的语言检测功能
                    translator = GoogleTranslator()
                    detected_info = translator.detect(text)
                    if detected_info and detected_info.lang:
                        # 在支持的语言中查找匹配的语言代码
                        for lang_name, lang_code in self.supported_languages.items():
                            if lang_code == detected_info.lang:
                                self.window.after(0, lambda: self.source_lang.set(lang_name))
                                source_lang = lang_code
                                break
                except Exception as e:
                    print(f"语言检测错误: {str(e)}")
            
            # 优先使用Google翻译（最快）
            try:
                translator = GoogleTranslator()
                translation = translator.translate(text, src=source_lang, dest=target_lang)
                if translation and translation.text:
                    self._handle_translation_result({
                        'text': translation.text,
                        'confidence': 0.9,
                        'source': 'Google翻译',
                        'detected_language': source_lang
                    }, text, target_lang)
                    return
            except Exception as e:
                print(f"Google翻译错误: {str(e)}")
            
            # 如果Google翻译失败，尝试其他翻译源
            translation_result = self.translate_text(text, source_lang, target_lang)
            if translation_result:
                self._handle_translation_result(translation_result, text, target_lang)
            else:
                self.window.after(0, lambda: self.text_area.insert(tk.END, "翻译失败，请重试...\n"))
                self.window.after(0, lambda: self.text_area.see(tk.END))
            
        except Exception as e:
            error_msg = f"翻译错误: {str(e)}\n"
            self.window.after(0, lambda: self.text_area.insert(tk.END, error_msg))
            self.window.after(0, lambda: self.text_area.see(tk.END))
        finally:
            # 恢复翻译按钮状态
            self.window.after(0, lambda: self.translate_button.configure(state='normal'))

    def _handle_translation_result(self, result, original_text, target_lang):
        """处理翻译结果"""
        def update_ui():
            translated_text = result['text']
            confidence = result['confidence']
            source = result['source']
            
            # 更新UI
            result_text = f"原文 ({self.source_lang.get()}): {original_text}\n"
            result_text += f"译文 ({self.target_lang.get()}): {translated_text}\n"
            result_text += f"翻译源: {source}\n"
            if confidence:
                result_text += f"置信度: {confidence:.2%}\n"
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
        
        # 在主线程中更新UI
        self.window.after(0, update_ui)

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    translator = VoiceTranslator()
    translator.run() 