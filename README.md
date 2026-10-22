# Edge TTS for Anki

**为 Anki 制作语音卡片更简单。** 在笔记编辑器中一键将文本转换为自然语音，并自动插入音频标签。

[![AnkiWeb](https://img.shields.io/badge/AnkiWeb-2034321258-blue)](https://ankiweb.net/shared/info/2034321258)
[![Release](https://img.shields.io/github/v/release/guanlisheng/edge-tts-for-anki)](https://github.com/guanlisheng/edge-tts-for-anki/releases)

[English](#english)

## 功能特点

- **快速生成语音**：点击编辑器工具栏中的 **Edge TTS**，或使用快捷键 **Ctrl+T**，为当前字段生成语音。
- **自动识别语言**：检测文本语言，并根据语言选择对应的语音；也可自定义语言与语音的映射。
- **灵活调整朗读效果**：自定义发音人、语速和音量。
- **缓存已生成音频**：重复处理相同内容时复用缓存，减少等待和网络请求。
- **依赖随插件提供**：`edge-tts` 等运行依赖已包含在插件包内，无需单独安装。

语音由 Microsoft Edge 在线文本转语音服务生成，使用时需要网络连接。

## 安装

### 推荐：通过 AnkiWeb 安装

1. 打开 Anki 桌面版，选择 **工具 → 插件 → 获取插件…**。
2. 输入插件代码 **`2034321258`**，点击 **确定**。
3. 重启 Anki。

### 从发布文件安装

1. 前往 [GitHub Releases](https://github.com/guanlisheng/edge-tts-for-anki/releases)，下载最新的 `.ankiaddon` 文件。
2. 在 Anki 中选择 **工具 → 插件 → 从文件安装…**，然后选中下载的文件。
3. 重启 Anki。

安装完成后，在添加或编辑笔记时，点击编辑器工具栏上的 **Edge TTS** 按钮，或按 **Ctrl+T** 即可生成语音。

## 配置

在 Anki 的 **工具 → 插件** 中选中 **Edge TTS**，打开配置，即可调整默认语音、语速、音量和缓存。配置示例：

```json
{
  "voice_mapping": {
    "zh": "zh-CN-XiaoxiaoNeural",
    "en": "en-US-AriaNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-ConradNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "es": "es-ES-ElviraNeural",
    "ru": "ru-RU-DariyaNeural",
    "ar": "ar-EG-SalmaNeural",
    "hi": "hi-IN-SwaraNeural"
  },
  "default_voice": "en-US-AriaNeural",
  "speech_rate": "+0%",
  "volume": "+0%",
  "cache_enabled": true
}
```

| 配置项 | 说明 |
| --- | --- |
| `voice_mapping` | 语言代码到语音名称的对应关系，例如 `zh` 对应中文语音。 |
| `default_voice` | 文本语言无法识别或没有对应映射时使用的语音。 |
| `speech_rate` | 语速调整，例如 `-10%` 或 `+20%`；`+0%` 表示默认语速。 |
| `volume` | 音量调整，例如 `-10%` 或 `+20%`；`+0%` 表示默认音量。 |
| `cache_enabled` | 是否缓存已生成的音频，默认开启。 |

语音名称需使用 Edge TTS 支持的 voice ID。可在 [edge-tts 项目文档](https://github.com/rany2/edge-tts)了解可用语音。

## 常见问题

**点击按钮后没有生成音频怎么办？**

请先确认 Anki 可以联网，再尝试重新生成。如果问题仍然存在，请到[项目 Issues](https://github.com/guanlisheng/edge-tts-for-anki/issues)反馈，并附上 Anki 版本和错误信息。

**快捷键是什么？**

默认快捷键是 **Ctrl+T**。在 macOS 上也可尝试 **⌘+T**。

## 开发

插件使用 Anki 桌面版运行。开发和调试时，可在项目根目录安装依赖并打包：

```bash
pip install --target=vendor -r requirements.txt
zip -r ../edge-tts-for-anki.ankiaddon . -x '*.git*' -x '__pycache__/*'
```

## English

**Create audio for your Anki cards in one click.** Edge TTS for Anki adds text-to-speech generation to the Anki note editor and inserts the resulting audio tag into the current field.

### Features

- Generate speech from the current field with the **Edge TTS** editor button or **Ctrl+T**.
- Detect the text language and select a matching voice, with customizable voice mappings.
- Adjust the voice, speech rate, and volume.
- Cache generated audio to avoid repeating the same request.
- Runtime dependencies are bundled; no separate installation is needed.

Speech is generated through Microsoft Edge's online text-to-speech service, so an internet connection is required.

### Install

**From AnkiWeb:** In Anki, open **Tools → Add-ons → Get Add-ons…**, enter **`2034321258`**, and restart Anki.

**From a release:** Download the latest `.ankiaddon` file from [GitHub Releases](https://github.com/guanlisheng/edge-tts-for-anki/releases), then use **Tools → Add-ons → Install from file…** and restart Anki.

### Configure

Open **Tools → Add-ons**, select **Edge TTS**, and choose **Config**. The settings include language-to-voice mappings, a fallback voice, speech rate, volume, and audio caching. See the Chinese section above for a complete example.

### Development

```bash
pip install --target=vendor -r requirements.txt
zip -r ../edge-tts-for-anki.ankiaddon . -x '*.git*' -x '__pycache__/*'
```

## Links

- [Install from AnkiWeb](https://ankiweb.net/shared/info/2034321258)
- [Releases](https://github.com/guanlisheng/edge-tts-for-anki/releases)
- [Report an issue](https://github.com/guanlisheng/edge-tts-for-anki/issues)
- [Project homepage](https://anki.guanlisheng.com/)
