# 多源语音翻译器

## 安装说明

### 1. 环境要求
- Python 3.8 或更高版本
- pip（Python包管理器）
- 虚拟环境（推荐）

### 2. 安装步骤

#### 2.1 创建并激活虚拟环境（推荐）
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖包
```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果安装PyAudio失败，可以尝试：
# Windows:
pip install pipwin
pipwin install pyaudio

# Linux:
# 先安装系统依赖
sudo apt-get install python3-pyaudio  # Ubuntu/Debian
sudo yum install python3-pyaudio      # CentOS/RHEL

# Mac:
brew install portaudio
pip install pyaudio
```

#### 2.3 配置API密钥
创建一个`.env`文件，并添加以下内容（根据需要填写）：
```
# DeepL翻译
DEEPL_API_KEY=your_key_here

# 百度翻译
BAIDU_APP_ID=your_app_id
BAIDU_SECRET_KEY=your_secret_key

# 有道翻译
YOUDAO_APP_KEY=your_app_key
YOUDAO_APP_SECRET=your_secret

# 微软翻译
AZURE_TRANSLATOR_KEY=your_key
AZURE_TRANSLATOR_REGION=your_region
AZURE_TRANSLATOR_ENDPOINT=your_endpoint

# 腾讯翻译
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key

# AWS翻译
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_REGION=your_region

# 彩云小译
CAIYUN_TOKEN=your_token

# 小牛翻译
NIUTRANS_KEY=your_key
```

### 3. 常见问题解决

#### 3.1 PyAudio 安装失败
- Windows用户：使用pipwin安装
- Linux用户：先安装系统依赖
- Mac用户：使用brew安装portaudio

#### 3.2 依赖冲突
如果遇到依赖冲突，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-deps
pip install -r requirements.txt
```

#### 3.3 特定翻译API的问题
- 谷歌翻译：无需API密钥，但可能需要代理
- DeepL：需要API密钥，可以使用免费版
- 百度/有道/腾讯等：需要在对应平台注册开发者账号

### 4. 运行程序
```bash
python voice_translator.py
```

### 5. 更新依赖
```bash
pip freeze > requirements.txt  # 更新依赖列表
```

## 注意事项
1. 建议使用虚拟环境，避免依赖冲突
2. 不是所有翻译API都需要配置，程序会自动使用已配置的API
3. 谷歌翻译为免费服务，但可能需要网络代理
4. 建议至少配置2-3个翻译源，以提高可靠性

## 功能特点

- 实时语音识别
- 中英文互译
- 简洁的图形界面
- 实时显示原文和译文

## 使用方法

1. 运行程序：
```bash
python voice_translator.py
```

2. 在界面上选择源语言和目标语言
3. 点击"开始录音"按钮开始录音
4. 对着麦克风说话
5. 程序会实时显示识别到的文字和翻译结果
6. 点击"停止录音"按钮结束录音

## 注意事项

- 请确保电脑已正确连接麦克风
- 需要连接网络才能使用语音识别和翻译功能
- 建议在较安静的环境下使用，以提高识别准确率 