import os
import re
import html
import asyncio
import edge_tts
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip
from aqt.editor import Editor
from anki.hooks import addHook

# 插件配置
CONFIG = {
    "chinese_voice": "zh-CN-XiaoxiaoNeural",
    "english_voice": "en-US-AriaNeural",
    "speech_rate": "+0%",
    "volume": "+0%",
    "cache_enabled": True
}

# 语音缓存
_tts_cache = {}

def get_config():
    return CONFIG

# ------------------ TTS 核心功能 ------------------
def contains_chinese(text):
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

async def generate_speech_async(text, voice, rate, volume, output_filename):
    """异步生成语音文件"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
        await communicate.save(output_filename)
        return True
    except Exception as e:
        showInfo(f"生成语音时出错: {str(e)}")
        return False

def generate_speech(text):
    """生成语音并返回音频文件名"""
    config = get_config()
    
    # 自动检测语言
    if contains_chinese(text):
        voice = config["chinese_voice"]
    else:
        voice = config["english_voice"]
    
    # 检查缓存
    cache_key = f"{text}_{voice}_{config['speech_rate']}_{config['volume']}"
    if config["cache_enabled"] and cache_key in _tts_cache:
        return _tts_cache[cache_key]
    
    # 确保媒体目录存在
    media_dir = mw.col.media.dir()
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    # 生成唯一的输出文件名
    output_filename = os.path.join(media_dir, f"tts_{hash(cache_key)}.mp3")
    
    # 异步任务同步执行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(
        generate_speech_async(text, voice, config["speech_rate"], config["volume"], output_filename)
    )
    loop.close()
    
    if success:
        if config["cache_enabled"]:
            _tts_cache[cache_key] = output_filename
        return output_filename
    return None

def add_tts_button(buttons, editor):
    """在编辑器中添加TTS按钮"""
    # 创建按钮
    b = editor.addButton(
        None, "Edge TTS", on_tts_clicked,
        tip="🔊生成语音 (Ctrl+T)", 
        keys="Ctrl+T"
    )
    buttons.append(b)
    return buttons

def strip_html_tags(text):
    """去掉 HTML 标签和 HTML 实体"""
    # 去掉标签
    text = re.sub(r'<[^>]+>', '', text)
    # 转换 HTML 实体
    text = html.unescape(text)
    # 可选：去掉多余空格
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return text

def on_tts_clicked(editor):
    """点击TTS按钮时的处理函数"""
    # 获取当前字段文本
    current_field = editor.currentField
    if current_field is None:
        return
    
    field_text = editor.note.fields[current_field]
    
    if not field_text.strip():
        tooltip("当前字段没有文本内容")
        return
   
    # 去掉 HTML
    plain_text = strip_html_tags(field_text)
    # 生成语音
    audio_file = generate_speech(plain_text)
    
    if audio_file:
        # 将音频标签插入字段
        audio_tag = f"[sound:{os.path.basename(audio_file)}]"
        editor.note.fields[current_field] = f"{field_text}\n{audio_tag}"
        editor.loadNote()
        tooltip("语音已生成并添加到字段中")
    else:
        tooltip("语音生成失败")

def add_editor_buttons():
    """添加编辑器按钮"""
    addHook("setupEditorButtons", add_tts_button)

# 初始化插件
add_editor_buttons()
