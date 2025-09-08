
import os, sys, json, subprocess

ADDON_ROOT = os.path.dirname(__file__)
VENDOR = os.path.join(ADDON_ROOT, "vendor")
if VENDOR not in sys.path:
    sys.path.insert(0, VENDOR)

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
DEFAULT_CONFIG = {
    "chinese_voice": "zh-CN-XiaoxiaoNeural",
    "english_voice": "en-US-AriaNeural",
    "speech_rate": "+0%",
    "volume": "+0%",
    "cache_enabled": True
}

def load_config():
    """尝试读取 config.json，如果失败则返回默认配置"""
    config_path = os.path.join(ADDON_ROOT, "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # 合并默认配置，避免缺少字段
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    except Exception as e:
        showInfo(f"加载 config.json 出错，使用默认配置: {e}")
    return DEFAULT_CONFIG.copy()

CONFIG = load_config()

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

# ------------------ 菜单功能 ------------------
def open_config_file():
    """打开 config.json"""
    path = os.path.join(ADDON_ROOT, "config.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    try:
        if sys.platform.startswith("darwin"):
            subprocess.call(("open", path))
        elif os.name == "nt":
            os.startfile(path)
        else:
            subprocess.call(("xdg-open", path))
    except Exception as e:
        showInfo(f"无法打开配置文件: {e}")

def reload_config():
    """重新加载配置"""
    load_config()
    showInfo("Edge TTS 配置已重新加载 ✅")

def about_plugin():
    """显示插件说明"""
    msg = (
        "🔊 Edge TTS for Anki\n\n"
        "为 Anki 编辑器添加微软 Edge TTS 语音合成功能。\n"
        "支持中文和英文自动切换。\n\n"
        "依赖库: edge-tts\n"
        "配置文件: config.json"
    )
    showInfo(msg)

# ------------------ 初始化 ------------------
def add_editor_buttons():
    """添加编辑器按钮"""
    addHook("setupEditorButtons", add_tts_button)

def setup_menu():
    menu = QMenu("Edge TTS", mw)
    mw.form.menuTools.addMenu(menu)

    action_open = QAction("打开配置文件", mw)
    action_open.triggered.connect(open_config_file)
    menu.addAction(action_open)

    action_reload = QAction("重载配置", mw)
    action_reload.triggered.connect(reload_config)
    menu.addAction(action_reload)

    action_about = QAction("关于插件", mw)
    action_about.triggered.connect(about_plugin)
    menu.addAction(action_about)

# 初始化插件
add_editor_buttons()
setup_menu()
