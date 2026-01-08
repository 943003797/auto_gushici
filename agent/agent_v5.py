import json, os, shutil
import math
from mutagen import File
from mutagen.wave import WAVE
from tts.cosyvoice.tts import TTS

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

def match_video(text: str) -> str:
    """
    根据文案内容匹配对应的视频文件路径
    
    Args:
        text (str): 输入的文案内容
        
    Returns:
        str: 匹配到的视频文件路径，若未匹配到则返回空字符串
    """
    return "D:/Material/fragment/1.mp4"

def format_content(content):
    """
    将传入的文案格式化为结构化数据
    
    Args:
        content (str): 待格式化的文案内容
        
    Returns:
        list: 包含多个字典的列表，每个字典包含id、text、audio_length、video_path、audio_patch
    """
    if not content or not content.strip():
        return []
    
    # 按行分割文案，去除空行和空白字符
    lines = content.strip().split('\n')
    sentences = []
    
    for line in lines:
        line = line.strip()
        if line:  # 非空行
            sentences.append(line)
    
    # 构建结构化数据
    structured_data = []
    for i, sentence in enumerate(sentences, 1):
        structured_data.append({
            'id': i,
            'text': sentence,
            'audio_length': None,  # 留空，等待后续处理
            'video_path': '',       # 留空，等待后续处理
            'audio_patch': ''       # 留空，等待后续处理
        })
    
    return structured_data

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

def generate_voice_for_content(formatted_json_str, topic_name, voice_id="风吟"):
    """
    为格式化的文案内容生成配音
    
    Args:
        formatted_json_str (str): 格式化后的JSON字符串
        topic_name (str): 主题名称
        voice_id (str): 音色ID，默认"风吟"
        
    Returns:
        dict: 包含配音结果的状态信息
    """
    try:
        # 解析JSON字符串
        structured_data = json.loads(formatted_json_str)
        if not structured_data:
            return {"status": "error", "message": "没有有效的文案内容"}
        
        # 确保目标目录存在
        target_dir = f"draft/JianyingPro Drafts/{topic_name}/Resources/audioAlg"
        os.makedirs(target_dir, exist_ok=True)
        
        # 初始化TTS
        tts = TTS()
        
        results = []
        success_count = 0
        total_count = len(structured_data)
        
        for item in structured_data:
            sentence_id = item['id']
            text = item['text']
            audio_filename = f"{sentence_id}.wav"  # 生成音频文件名，如001.wav
            
            try:
                # 生成音频文件
                audio_path = os.path.join(target_dir, audio_filename)
                success = tts.textToAudio(text=text, out_path=audio_path)
                
                if success:
                    results.append({
                        "id": sentence_id,
                        "text": text,
                        "audio_path": audio_path,
                        "status": "success"
                    })
                    success_count += 1
                else:
                    results.append({
                        "id": sentence_id,
                        "text": text,
                        "audio_path": None,
                        "status": "failed"
                    })
            except Exception as e:
                results.append({
                    "id": sentence_id,
                    "text": text,
                    "audio_path": None,
                    "status": "error",
                    "error": str(e)
                })
        
        # 更新结构化数据中的audio_length、video_path和audio_patch
        for result in results:
            for item in structured_data:
                if item['id'] == result['id']:
                    if result['status'] == 'success':
                        # 获取音频时长
                        audio_length = get_audio_duration(result['audio_path'])
                        item['audio_length'] = audio_length if audio_length is not None else None
                        item['video_path'] = result['audio_path']
                        # 更新audio_patch为音频文件名（相对路径）
                        item['audio_patch'] = os.path.basename(result['audio_path'])
                    break
        
        # 返回结果
        return {
            "status": "completed",
            "message": f"配音完成！成功生成 {success_count}/{total_count} 个音频文件",
            "results": results,
            "updated_data": structured_data,
            "target_directory": target_dir
        }
        
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"JSON解析错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"配音生成失败: {e}"}

def process_complete_workflow(content, topic_name, voice_id="风吟"):
    """
    完整的配音工作流程：格式化文案 + 复制目录 + 生成配音
    
    Args:
        content (str): 原始文案内容
        topic_name (str): 主题名称
        voice_id (str): 音色ID
        
    Returns:
        dict: 完整的工作流结果
    """
    try:
        # 1. 格式化文案
        structured_data = format_content(content)
        if not structured_data:
            return {"status": "error", "message": "没有有效的文案内容"}
        
        # 转换为JSON字符串
        formatted_json_str = json.dumps(structured_data, ensure_ascii=False, indent=2)
        
        # 2. 复制baseDraft到目标目录
        copy_success = copy_base_draft_to_draft(topic_name)
        if not copy_success:
            return {"status": "error", "message": "复制baseDraft失败"}
        
        # 3. 生成配音
        voice_result = generate_voice_for_content(formatted_json_str, topic_name, voice_id)
        
        return {
            "status": "success",
            "formatted_data": structured_data,
            "formatted_json": formatted_json_str,
            "copy_result": {"success": copy_success},
            "voice_result": voice_result
        }
        
    except Exception as e:
        return {"status": "error", "message": f"工作流执行失败: {e}"}