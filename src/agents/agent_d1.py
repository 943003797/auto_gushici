import json, os, shutil
import math
from mutagen import File
from mutagen.wave import WAVE
from src.tts.minimax.tts import TTS
from src.ai_models.big_model.llm import LLM
from src.vector.vectordb import VectorDB

def get_audio_duration(audio_path):
    """
    获取音频文件的时长（秒）
    
    Args:
        audio_path (str): 音频文件路径
        
    Returns:
        int: 音频时长（秒），不足一秒则向上取整
    """
    try:
        if not os.path.exists(audio_path):
            return None
        
        # 首先尝试使用 mutagen.File（支持多种格式）
        try:
            audio = File(audio_path)
            if audio is not None and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                duration = audio.info.length
                return math.ceil(duration)
        except Exception as e:
            print(f"使用 mutagen.File 获取时长失败: {e}")
        
        # 如果 mutagen.File 失败，尝试使用 WAVE 类
        try:
            audio = WAVE(audio_path)
            duration = audio.info.length
            return math.ceil(duration)
        except Exception as e:
            print(f"使用 WAVE 获取时长失败: {e}")
        
        return None
    except Exception as e:
        print(f"获取音频时长失败: {e}")
        return None

def copy_base_draft_to_draft(topic_name):
    """
    复制material/baseDraft到目标目录
    
    Args:
        topic_name (str): 主题名称（从输入框获取）
        
    Returns:
        bool: 是否复制成功
    """
    try:
        source_path = "material/baseDraft"
        target_dir = f"draft/JianyingPro Drafts/{topic_name}"
        
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制整个baseDraft目录
        if os.path.exists(source_path):
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)  # 如果目标目录存在，先删除
            shutil.copytree(source_path, target_dir)
            return True
        else:
            return False
    except Exception as e:
        print(f"复制失败: {e}")
        return False

def generate_text(text: str = "", name: str = "", out_dir: str = "") -> bool:
    if not out_dir:
        out_dir = os.getenv("DRAFT_DIR") or ""
    tts = TTS(voice_id="少女朗诵", speech_rate=0.9)
    tts.textToAudio(text=text + '。', out_path=f"{out_dir}/{name}/Resources/audioAlg/wenan.mp3")
    return True

def process_complete_workflow(title: str = "", wenan: str = "", topic_name: str = ""):
    """
    完整的配音工作流程：格式化文案 + 复制目录 + 生成配音
    
    Args:
        title (str): 标题
        wenan (str): 文案内容
        topic_name (str): 主题名称
        
    Returns:
        dict: 完整的工作流结果
    """
    try:
        # 2. 复制baseDraft到目标目录
        copy_success = copy_base_draft_to_draft(topic_name)
        if not copy_success:
            return {"status": "error", "message": "复制baseDraft失败"}
        
        # 3. 生成配音
        voice_result = generate_text(text=wenan, name=topic_name)
        
        return {
            "status": "success",
            "copy_result": {"success": copy_success},
            "voice_result": voice_result
        }
        
    except Exception as e:
        return {"status": "error", "message": f"工作流执行失败: {e}"}