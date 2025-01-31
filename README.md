# Voice Translator / 语音翻译助手

[English](#english) | [中文](#chinese)

## English

### Introduction
Voice Translator is a powerful desktop application that provides real-time voice and text translation support across multiple languages. It features a user-friendly interface and supports various translation services.

### Features
- **Voice Recognition**: Real-time voice input with automatic language detection
- **Text Translation**: Support for text input and translation
- **Multiple Languages**: Supports:
  - Chinese (Simplified & Traditional)
  - English
  - Japanese
  - Korean
  - French
  - German
  - Spanish
  - Russian

- **Multiple Translation Services**:
  - Smart Selection (automatically chooses the best service)
  - Local Package (for common phrases)
  - DeepL Translate
  - Google Translate
  - Baidu Translate
  - Youdao Translate
  - Microsoft Translate
  - Tencent Translate
  - AWS Translate
  - Caiyun Translate
  - Niutrans Translate

- **Voice Output**: Text-to-speech capability for translated content
- **History Tracking**: Keeps track of translation history
- **Customizable Settings**: Adjustable voice speed and microphone selection
- **Bilingual Interface**: Supports both English and Chinese interfaces

### Installation
1. Ensure Python 3.7+ is installed
2. Install required packages:
```bash
pip install -r requirements.txt
```

### Configuration
1. Create a `.env` file in the project root directory
2. Add your API keys for the translation services you want to use:
```
DEEPL_API_KEY=your_key
BAIDU_APP_ID=your_id
BAIDU_SECRET_KEY=your_key
YOUDAO_APP_KEY=your_key
YOUDAO_APP_SECRET=your_secret
AZURE_TRANSLATOR_KEY=your_key
AZURE_TRANSLATOR_REGION=your_region
AZURE_TRANSLATOR_ENDPOINT=your_endpoint
TENCENT_SECRET_ID=your_id
TENCENT_SECRET_KEY=your_key
AWS_ACCESS_KEY=your_key
AWS_SECRET_KEY=your_key
AWS_REGION=your_region
CAIYUN_TOKEN=your_token
NIUTRANS_KEY=your_key
```

### Usage
1. Run the application:
```bash
python voice_translator.py
```
2. Select source and target languages
3. Choose translation service
4. Use either:
   - Click "Start Recording" for voice input
   - Type text in the input area and click "Translate" or press Ctrl+Enter

### Notes
- Internet connection required for online translation services
- Some translation services require API keys
- Voice recognition quality depends on microphone and environment

---

## Chinese

### 简介
语音翻译助手是一款功能强大的桌面应用程序，提供实时语音和文本翻译支持，支持多种语言，界面友好，支持多个翻译服务。

### 功能特点
- **语音识别**：实时语音输入，支持自动语言检测
- **文本翻译**：支持文本输入和翻译
- **多语言支持**：
  - 中文（简体和繁体）
  - 英语
  - 日语
  - 韩语
  - 法语
  - 德语
  - 西班牙语
  - 俄语

- **多种翻译服务**：
  - 智能选择（自动选择最佳服务）
  - 本地翻译包（常用短语）
  - DeepL翻译
  - 谷歌翻译
  - 百度翻译
  - 有道翻译
  - 微软翻译
  - 腾讯翻译
  - AWS翻译
  - 彩云翻译
  - 小牛翻译

- **语音输出**：支持文本转语音
- **历史记录**：保存翻译历史
- **自定义设置**：可调节语音速度和选择麦克风
- **双语界面**：支持中英文界面切换

### 安装
1. 确保已安装Python 3.7+
2. 安装所需包：
```bash
pip install -r requirements.txt
```

### 配置
1. 在项目根目录创建`.env`文件
2. 添加需要使用的翻译服务的API密钥：
```
DEEPL_API_KEY=你的密钥
BAIDU_APP_ID=你的应用ID
BAIDU_SECRET_KEY=你的密钥
YOUDAO_APP_KEY=你的应用密钥
YOUDAO_APP_SECRET=你的密钥
AZURE_TRANSLATOR_KEY=你的密钥
AZURE_TRANSLATOR_REGION=你的区域
AZURE_TRANSLATOR_ENDPOINT=你的终端点
TENCENT_SECRET_ID=你的密钥ID
TENCENT_SECRET_KEY=你的密钥
AWS_ACCESS_KEY=你的访问密钥
AWS_SECRET_KEY=你的密钥
AWS_REGION=你的区域
CAIYUN_TOKEN=你的令牌
NIUTRANS_KEY=你的密钥
```

### 使用方法
1. 运行应用程序：
```bash
python voice_translator.py
```
2. 选择源语言和目标语言
3. 选择翻译服务
4. 使用方式：
   - 点击"开始录音"进行语音输入
   - 在输入区域输入文本，点击"翻译文本"或按Ctrl+Enter

### 注意事项
- 在线翻译服务需要网络连接
- 部分翻译服务需要API密钥
- 语音识别质量取决于麦克风和环境 