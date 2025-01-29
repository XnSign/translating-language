import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speech_recognition as sr
from googletrans import Translator
import pyttsx3

class VoiceTranslator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('实时语音翻译器')
        self.window.geometry('600x400')
        
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        
        # 初始化语音引擎
        try:
            self.engine = pyttsx3.init()
            # 获取可用的声音列表
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
        
    def init_ui(self):
        # 创建语言选择下拉框
        frame_langs = ttk.Frame(self.window)
        frame_langs.pack(pady=10)
        
        ttk.Label(frame_langs, text="源语言：").pack(side=tk.LEFT)
        self.source_lang = ttk.Combobox(frame_langs, values=['中文', '英语'])
        self.source_lang.set('中文')
        self.source_lang.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_langs, text="目标语言：").pack(side=tk.LEFT)
        self.target_lang = ttk.Combobox(frame_langs, values=['中文', '英语'])
        self.target_lang.set('英语')
        self.target_lang.pack(side=tk.LEFT, padx=5)
        
        # 创建麦克风选择下拉框
        frame_mic = ttk.Frame(self.window)
        frame_mic.pack(pady=5)
        ttk.Label(frame_mic, text="选择麦克风：").pack(side=tk.LEFT)
        self.mic_select = ttk.Combobox(frame_mic, values=self.mic_list)
        if self.mic_list:
            self.mic_select.set(self.mic_list[0])
        self.mic_select.pack(side=tk.LEFT, padx=5)
        
        # 创建语音输出设置
        frame_voice = ttk.Frame(self.window)
        frame_voice.pack(pady=5)
        
        # 语音输出开关
        self.voice_output_enabled = tk.BooleanVar(value=True)
        self.voice_checkbox = ttk.Checkbutton(
            frame_voice, 
            text="启用语音输出", 
            variable=self.voice_output_enabled
        )
        self.voice_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 语音选择（如果有多个声音）
        if self.voice_list:
            ttk.Label(frame_voice, text="选择声音：").pack(side=tk.LEFT)
            self.voice_select = ttk.Combobox(frame_voice, values=self.voice_list)
            self.voice_select.set(self.voice_list[0])
            self.voice_select.pack(side=tk.LEFT, padx=5)
            
            # 语速调节
            ttk.Label(frame_voice, text="语速：").pack(side=tk.LEFT)
            self.rate_scale = ttk.Scale(
                frame_voice, 
                from_=50, 
                to=300,
                orient=tk.HORIZONTAL,
                length=100
            )
            self.rate_scale.set(150)  # 默认语速
            self.rate_scale.pack(side=tk.LEFT, padx=5)
        
        # 创建文本显示区域
        self.text_area = tk.Text(self.window, height=15)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 创建录音按钮
        self.record_button = ttk.Button(self.window, text='开始录音', command=self.toggle_recording)
        self.record_button.pack(pady=10)
        
    def speak_text(self, text, lang):
        """使用语音输出文本"""
        if not self.voice_output_enabled.get() or not self.engine:
            return
            
        try:
            # 设置语速
            rate = int(self.rate_scale.get())
            self.engine.setProperty('rate', rate)
            
            # 设置选中的声音
            if self.voice_list:
                voices = self.engine.getProperty('voices')
                selected_voice = voices[self.voice_list.index(self.voice_select.get())]
                self.engine.setProperty('voice', selected_voice.id)
            
            # 朗读文本
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.text_area.insert(tk.END, f"语音输出错误: {str(e)}\n")
            self.text_area.see(tk.END)
        
    def toggle_recording(self):
        if not self.is_recording:
            try:
                # 获取选中的麦克风索引
                mic_index = self.mic_list.index(self.mic_select.get())
                self.current_mic = sr.Microphone(device_index=mic_index)
                
                # 测试麦克风
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
        lang_map = {'中文': 'zh-CN', '英语': 'en'}
        try:
            with self.current_mic as source:
                while self.is_recording:
                    try:
                        self.text_area.insert(tk.END, "正在听取语音...\n")
                        self.text_area.see(tk.END)
                        
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        source_lang = lang_map[self.source_lang.get()]
                        text = self.recognizer.recognize_google(audio, language=source_lang)
                        
                        # 翻译文本
                        target_lang = lang_map[self.target_lang.get()]
                        translation = self.translator.translate(
                            text, 
                            src=source_lang, 
                            dest=target_lang
                        )
                        
                        # 更新UI
                        result_text = f"原文: {text}\n译文: {translation.text}\n\n"
                        self.text_area.insert(tk.END, result_text)
                        self.text_area.see(tk.END)
                        
                        # 语音输出翻译结果
                        self.speak_text(translation.text, target_lang)
                        
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
    
    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    translator = VoiceTranslator()
    translator.run() 