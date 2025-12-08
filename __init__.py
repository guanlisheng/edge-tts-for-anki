# file __init__.py
import os, sys, json, subprocess

ADDON_ROOT = os.path.dirname(__file__)
VENDOR = os.path.join(ADDON_ROOT, "vendor")
if VENDOR not in sys.path:
    sys.path.insert(0, VENDOR)

import re
import html
import asyncio
import edge_tts
import langdetect
from langdetect.lang_detect_exception import LangDetectException

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip
from aqt.editor import Editor
from anki.hooks import addHook

# 插件配置
DEFAULT_CONFIG = {
    # 新版：语音映射表（语言代码 -> Edge TTS 语音名称）
    "voice_mapping": {
        "zh": "zh-CN-XiaoxiaoNeural",    # 中文
        "en": "en-US-AriaNeural",        # 英文
        "fr": "fr-FR-DeniseNeural",      # 法语
        "de": "de-DE-ConradNeural",      # 德语
        "ja": "ja-JP-NanamiNeural",      # 日语
        "ko": "ko-KR-SunHiNeural",       # 韩语
        "es": "es-ES-ElviraNeural",      # 西班牙语
        "ru": "ru-RU-DariyaNeural",      # 俄语
        "ar": "ar-EG-SalmaNeural",       # 阿拉伯语
        "hi": "hi-IN-SwaraNeural",       # 印地语
        "it": "it-IT-ElsaNeural",        # 意大利语
        "pt": "pt-BR-FranciscaNeural",   # 葡萄牙语
    },
    # 当检测失败或未映射时的默认语音
    "default_voice": "en-US-AriaNeural",
    # 兼容旧版配置的字段（用于自动迁移）
    "chinese_voice": None,
    "english_voice": None,
    # 其他参数保持不变
    "speech_rate": "+0%",
    "volume": "+0%",
    "cache_enabled": True
}

def load_config():
    """加载并迁移配置"""
    config_path = os.path.join(ADDON_ROOT, "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            
            # 从 DEFAULT_CONFIG 深拷贝开始
            merged = json.loads(json.dumps(DEFAULT_CONFIG))
            merged.update(user_cfg)
            
            # 自动迁移旧版配置
            if merged["chinese_voice"] or merged["english_voice"]:
                if merged["chinese_voice"]:
                    merged["voice_mapping"]["zh"] = merged["chinese_voice"]
                if merged["english_voice"]:
                    merged["voice_mapping"]["en"] = merged["english_voice"]
                # 标记已迁移
                merged["chinese_voice"] = None
                merged["english_voice"] = None
                
                # 保存迁移后的配置
                try:
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump({k: v for k, v in merged.items() 
                                 if k not in ["chinese_voice", "english_voice"]}, 
                                f, indent=4, ensure_ascii=False)
                    print("配置已自动迁移至新版格式")
                except:
                    pass
            
            return merged
    except Exception as e:
        print(f"配置加载失败，使用默认值: {e}")
    
    return DEFAULT_CONFIG.copy

CONFIG = load_config()

# 语音缓存
_tts_cache = {}

def get_config():
    return CONFIG

# ------------------ TTS 核心功能 ------------------

def detect_language(text):
    """
    提升 langdetect 的准确率，特别是中/日/韩。
    优雅降级：langdetect -> 语系检测 -> 字符检测 -> 默认
    """
    # 清理文本：去除HTML标签和符号
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'[0-9\W_]+', ' ', clean).strip()

    if not clean or len(clean) < 2:
        return "en"

    # ---- ① CJK 预检测（最可靠）----
    has_hanzi = bool(re.search(r'[\u4e00-\u9fff]', text))
    has_jp_kana = bool(re.search(r'[\u3040-\u30ff]', text))
    has_hangul = bool(re.search(r'[\uAC00-\uD7A3]', text))

    if has_hangul:
        return "ko"
    if has_jp_kana:
        return "ja"
    # 含中文汉字但无假名 → 99% 是中文
    if has_hanzi and not has_jp_kana:
        return "zh"

    # ---- ② langdetect：带概率过滤 ----
    try:
        langdetect.DetectorFactory.seed = 0
        langs = detect_langs(clean)  # 返回: ['en:0.98', 'fr:0.02']

        best = langs[0]
        lang = best.lang
        prob = best.prob

        # 对 CJK：如果 langdetect 不确定（低于阈值），不用它
        if lang in ("zh-cn", "zh-tw", "ja", "ko") and prob < 0.85:
            pass
        else:
            # 正常语言（英文/印欧语系）用 langdetect 结果
            if prob >= 0.70:  # 防止置信度过低
                return lang[:2]

    except LangDetectException:
        pass

    # ---- ③ 再次执行 CJK 的降级判断 ----
    if has_jp_kana:
        return "ja"
    if has_hangul:
        return "ko"
    if has_hanzi:
        # 如果有假名 → 日文；否则中文
        if has_jp_kana:
            return "ja"
        return "zh"

    # ---- ④ 西里尔、阿拉伯等语系检测 ----
    if re.search(r'[\u0400-\u04FF]', text):
        return "ru"
    if re.search(r'[\u0600-\u06FF]', text):
        return "ar"
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"

    # ---- ⑤ 基础拉丁字母：认为是英文 ----
    if re.search(r'[a-zA-Z]', text):
        return "en"

    # ---- ⑥ 完全无法识别
    return "en"

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


    # 检测语言
    lang_code = detect_language(text)

    # 从映射表获取语音，若未配置则使用默认
    voice_mapping = config.get("voice_mapping", {})
    voice = voice_mapping.get(lang_code, config.get("default_voice", "en-US-AriaNeural"))
    
    # 检查缓存
    cache_key = f"{text}_{voice}_{config['speech_rate']}_{config['volume']}"
    if config["cache_enabled"] and cache_key in _tts_cache:
        return _tts_cache[cache_key]
    
    # 确保媒体目录存在
    media_dir = mw.col.media.dir()
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    # 生成唯一的输出文件名
    output_filename = os.path.join(media_dir, f"tts_{lang_code}_{hash(cache_key)}.mp3")
    
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
