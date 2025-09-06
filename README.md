# Edge TTS Plugin for Anki

## 功能 / Features

- 为 Anki 编辑器字段生成语音（Text-to-Speech, TTS）
- 自动识别中文和英文，使用不同的语音
- 支持缓存生成的音频，避免重复生成
- 可通过快捷键 Ctrl+T 生成语音并插入字段

## 依赖库 / Dependencies

本插件依赖以下 Python 库：

- [`edge-tts`](https://pypi.org/project/edge-tts/)：用于生成文本到语音（TTS）

### 安装方式 / Installation

1. 确保已安装 Python（Anki 内置 Python 即可）  
2. 使用 pip 安装依赖库：

```bash
pip install edge-tts
