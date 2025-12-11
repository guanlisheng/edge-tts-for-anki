# Edge TTS Plugin for Anki

## 插件代码 / AnkiWeb ID
[`2034321258`](https://ankiweb.net/shared/info/2034321258) 用户可以在 Anki 中 **工具 → 插件 → 获取插件** 输入该 ID 直接安装。

## 功能 / Features

这是一个为 Anki 编辑器设计的语音生成插件，利用微软 Edge 的在线语音合成技术，快速为学习卡片生成高质量发音。

- **一键生成语音**：在编辑器界面点击按钮或使用快捷键 **Ctrl+T**，即可为当前字段文本生成语音并插入音频标签。
- **智能多语言识别**：自动检测文本语言（支持中、英、日、韩、法、德、西、俄等数十种语言），并为不同语言匹配最合适的语音。
- **高度可定制**：可自由配置任意语言对应的发音人、语速和音量。
- **高效的缓存机制**：自动缓存已生成的音频文件，避免对相同内容重复请求，节省时间和流量。

## 依赖库 / Dependencies

- [`edge-tts`](https://pypi.org/project/edge-tts/)：用于生成文本到语音（TTS）  
- [`langdetect`](https://pypi.org/project/langdetect/)：用于检测文本到语音
- 👆 已内置在插件中，无需手动安装

## 安装方法 / Installation

### 方法一：一键安装（推荐）
1.  在 Anki 桌面版中，点击菜单 **工具 (Tools) → 插件 (Add-ons)**。
2.  点击 **获取插件 (Get Add-ons...)**。
3.  在弹出的窗口中输入插件代码 **`2034321258`**，然后点击 **确定 (OK)**。
4.  重启 Anki 完成安装。

### 方法二：手动安装文件
1.  从[github发布页面](https://github.com/guanlisheng/edge-tts-for-anki/releases/)下载最新的 `.ankiaddon` 文件。
2.  在 Anki 中，打开 **工具 → 插件**。
3.  点击 **从文件安装... (Install from file...)**，选择下载的 `.ankiaddon` 文件。
4.  重启 Anki。

安装后，Anki 笔记编辑器的工具栏上会出现一个 **“Edge TTS”** 按钮。

## 配置 / Configuration

可以在插件的 **配置界面** 中修改以下选项：

### 核心配置项

```json
{
  "voice_mapping": {
    "zh": "zh-CN-XiaoxiaoNeural",
    "en": "en-US-AriaNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-ConradNeural"
  },
  "default_voice": "en-US-AriaNeural",
  "speech_rate": "+0%",
  "volume": "+0%",
  "cache_enabled": true
}
```

- `voice_mapping`: (关键配置): 一个字典，用于将语言代码映射到具体的 Edge TTS 语音名称。插件会自动根据检测到的语言代码选择右侧对应的发音人。
- `default_voice`: 当文本语言未在 voice_mapping 中定义时，将使用的备用语音。
- `speech_rate`: 语速（如 `+0%`, `-10%`, `+20%`）  
- `volume`: 音量（如 `+0%`, `+50%`）  
- `cache_enabled`: 是否启用缓存，避免重复生成  

## 开发 / Development

- 开发和运行环境

```
Anki 25.02.6 (6381f184)  (ao)
Python 3.9.18 Qt 6.6.2 PyQt 6.6.1
```

- 如果需要调试插件，可以在本地克隆代码，并在 `vendor/` 目录中手动安装依赖：

```bash
pip install --target=vendor -r requirements.txt
```

- 然后重新打包成 .ankiaddon 即可。
```bash
zip -r ../edge-tts-for-anki.ankiaddon *
```
