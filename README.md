# Edge TTS Plugin for Anki

## 插件代码 / AnkiWeb ID
`2034321258` 用户可以在 Anki 中 **工具 → 插件 → 获取插件** 输入该 ID 直接安装。

## 功能 / Features

- 为 Anki 编辑器字段生成语音（Text-to-Speech, TTS）
- 自动识别中文和英文，使用不同的语音
- 支持缓存生成的音频，避免重复生成
- 可通过快捷键 **Ctrl+T** 生成语音并插入字段

## 依赖库 / Dependencies

- [`edge-tts`](https://pypi.org/project/edge-tts/)：用于生成文本到语音（TTS）  
  👉 已内置在插件中，无需手动安装

## 安装方式 / Installation

1. 下载 `.ankiaddon` 文件  
2. 在 Anki 中打开菜单 **工具 → 插件 → 从文件安装...**  
3. 选择下载的 `.ankiaddon` 文件并安装  
4. 重启 Anki

安装完成后，编辑器中会出现 **Edge TTS 按钮**，或者可直接使用快捷键 **Ctrl+T** 生成语音。

## 配置 / Configuration

可以在插件的 **配置界面** 中修改以下选项：

- `chinese_voice`: 中文语音名称（默认: `zh-CN-XiaoxiaoNeural`）  
- `english_voice`: 英文语音名称（默认: `en-US-AriaNeural`）  
- `speech_rate`: 语速（如 `+0%`, `-10%`, `+20%`）  
- `volume`: 音量（如 `+0%`, `+50%`）  
- `cache_enabled`: 是否启用缓存，避免重复生成  

## 开发 / Development

如果需要调试插件，可以在本地克隆代码，并在 `vendor/` 目录中手动安装依赖：

```bash
pip install --target=vendor edge-tts
```

然后重新打包成 .ankiaddon 即可。
```bash
zip -r ../edge-tts-for-anki.ankiaddon *
```
