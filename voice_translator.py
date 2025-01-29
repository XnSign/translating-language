import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import speech_recognition as sr
import pyttsx3
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator, MicrosoftTranslator
import random

class TranslationContext:
    def __init__(self, max_history=5):
        self.history = []
        self.max_history = max_history
        self._lock = threading.Lock()
    
    def add_context(self, text, translation):
        with self._lock:
            self.history.append((text, translation))
            if len(self.history) > self.max_history:
                self.history.pop(0)
    
    def get_context(self):
        with self._lock:
            return list(self.history)
    
    def clear_context(self):
        with self._lock:
            self.history = []

class VoiceTranslator:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 初始化翻译上下文
        self.context = TranslationContext()
        
        # 初始化消息队列
        self.message_queue = queue.Queue()
        
        self.window = tk.Tk()
        self.window.title('智能语音翻译器 Pro Plus')
        self.window.geometry('800x600')
        
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        
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
            
        self.init_ui()
        
        # 启动UI更新线程
        self.window.after(100, self.process_message_queue)
    
    def process_message_queue(self):
        """处理消息队列中的UI更新请求"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                message_type = message.get('type')
                
                if message_type == 'update_text':
                    self.text_area.insert(tk.END, message['text'])
                    self.text_area.see(tk.END)
                elif message_type == 'update_history':
                    self.update_history_display()
                elif message_type == 'speak':
                    self.speak_text(message['text'], message['lang'])
                elif message_type == 'set_source_lang':
                    self.source_lang.set(message['lang'])
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.process_message_queue)
    
    def add_message(self, message_type, **kwargs):
        """添加消息到队列"""
        message = {'type': message_type}
        message.update(kwargs)
        self.message_queue.put(message)
    
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
        try:
            # 1. 检查是否有上下文特殊处理
            context_translation = self.analyze_context(text, self.context.get_context())
            if context_translation:
                return {
                    'text': context_translation,
                    'detected_language': source_lang,
                    'confidence': 1.0,
                    'source': 'context'
                }
            
            # 2. 尝试使用 Google 翻译
            try:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                translation = translator.translate(text)
                if translation:
                    return {
                        'text': translation,
                        'detected_language': source_lang,
                        'confidence': 0.9,
                        'source': 'Google翻译'
                    }
            except Exception as e:
                print(f"Google翻译错误: {str(e)}")
            
            # 3. 如果 Google 翻译失败，尝试使用 Microsoft 翻译
            try:
                translator = MicrosoftTranslator(source=source_lang, target=target_lang)
                translation = translator.translate(text)
                if translation:
                    return {
                        'text': translation,
                        'detected_language': source_lang,
                        'confidence': 0.8,
                        'source': 'Microsoft翻译'
                    }
            except Exception as e:
                print(f"Microsoft翻译错误: {str(e)}")
            
            return None
            
        except Exception as e:
            print(f"翻译错误: {str(e)}")
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
        
    def update_history_display(self):
        """更新历史记录显示"""
        self.history_area.delete(1.0, tk.END)
        for text, translation in reversed(self.context.get_context()):
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
                        self.add_message('update_text', text="正在听取语音...\n")
                        
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # 获取源语言和文本
                        if self.auto_detect.get():
                            detected_lang, text = self.detect_language(audio)
                            if detected_lang:
                                self.add_message('set_source_lang', lang=detected_lang)
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
                            source = translation_result['source']
                            
                            # 更新UI
                            result_text = f"原文 ({self.source_lang.get()}): {text}\n"
                            result_text += f"译文 ({self.target_lang.get()}): {translated_text}\n"
                            result_text += f"翻译源: {source}\n"
                            if confidence:
                                result_text += f"置信度: {confidence:.2%}\n"
                            result_text += "\n"
                            
                            self.add_message('update_text', text=result_text)
                            
                            # 更新历史记录
                            self.context.add_context(text, translated_text)
                            self.add_message('update_history')
                            
                            # 语音输出翻译结果
                            self.add_message('speak', text=translated_text, lang=target_lang)
                        else:
                            self.add_message('update_text', text="翻译失败，请重试...\n")
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.add_message('update_text', text="未能识别语音，请重试...\n")
                    except Exception as e:
                        self.add_message('update_text', text=f"错误: {str(e)}\n")
        except Exception as e:
            messagebox.showerror("错误", f"录音过程出错：{str(e)}")
            self.is_recording = False
            self.record_button.configure(text='开始录音')

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    translator = VoiceTranslator()
    translator.run() 