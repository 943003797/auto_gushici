import gradio as gr
from agent.agent_v5 import format_content, process_complete_workflow
from pathlib import Path
import os

def format_text(content):
    """
    格式化文案的函数
    """
    if not content or not content.strip():
        return "请输入文案内容"
    
    try:
        structured_data = format_content(content)
        if not structured_data:
            return "没有有效的文案内容"
        
        # 将结构化数据格式化为可读的文本
        formatted_text = "[\n"
        for i, item in enumerate(structured_data):
            formatted_text += f"  {{\n"
            formatted_text += f"    'id': {item['id']},\n"
            formatted_text += f"    'text': '{item['text']}',\n"
            formatted_text += f"    'audio_length': {item['audio_length']},\n"
            # video_path 和 audio_patch 暂时留空（配音后会被更新）
            formatted_text += f"    'video_path': '',\n"
            formatted_text += f"    'audio_patch': ''\n"
            if i < len(structured_data) - 1:
                formatted_text += "  },\n"
            else:
                formatted_text += "  }\n"
        formatted_text += "]"
        
        return formatted_text
    except Exception as e:
        return f"格式化出错: {str(e)}"

def voice_generation(content, topic_name):
    """
    配音功能的实现函数
    """
    import time
    
    if not content or not content.strip():
        yield "请先输入文案内容", None, "", []
        return
    
    if not topic_name or not topic_name.strip():
        yield "请输入主题名称", None, "", []
        return
    
    try:
        # 实时更新配音状态
        status_messages = [
            "正在准备配音...",
            "正在复制项目模板...",
            "正在生成语音文件...",
            "正在优化音频质量...",
            "配音生成中！"
        ]
        
        for i, message in enumerate(status_messages):
            time.sleep(0.5)  # 模拟处理时间
            yield message, None, "", []
        
        # 执行完整的配音工作流程
        result = process_complete_workflow(content, topic_name)
        
        if result.get("status") == "success":
            final_message = f"配音完成！\n\n项目路径: draft/JianyingPro Drafts/{topic_name}\n\n{result.get('voice_result', {}).get('message', '')}"
            
            # 获取更新后的结构化数据并格式化为JSON字符串
            updated_data = result.get('voice_result', {}).get('updated_data', [])
            if updated_data:
                formatted_json = "[\n"
                for i, item in enumerate(updated_data):
                    formatted_json += f"  {{\n"
                    formatted_json += f"    'id': {item['id']},\n"
                    formatted_json += f"    'text': '{item['text']}',\n"
                    formatted_json += f"    'audio_length': {item['audio_length']},\n"
                    formatted_json += f"    'video_path': '{item['video_path']}',\n"
                    formatted_json += f"    'audio_patch': '{item.get('audio_patch', '')}'\n"
                    if i < len(updated_data) - 1:
                        formatted_json += "  },\n"
                    else:
                        formatted_json += "  }\n"
                formatted_json += "]"
                
                # 生成配音选择列表
                voice_choices = []
                for item in updated_data:
                    if item.get('audio_patch'):
                        choice_label = f"句子{item['id']}: {item['text'][:20]}..."
                        voice_choices.append(choice_label)
            else:
                formatted_json = ""
                voice_choices = []
            
            yield final_message, None, formatted_json, voice_choices
        else:
            error_message = f"配音失败: {result.get('message', '未知错误')}"
            yield error_message, None, "", []
            
    except Exception as e:
        error_message = f"配音过程中出现错误: {str(e)}"
        yield error_message, None, "", []

# 创建Gradio界面
def create_interface():
    with gr.Blocks(title="文案格式化工具") as demo:
        gr.Markdown("# 文案格式化工具")
        
        with gr.Row():
            # 左侧：文案格式化功能
            with gr.Column(scale=1):
                gr.Markdown("### 📝 文案格式化")
                
                input_text = gr.Textbox(
                    label="输入文案",
                    placeholder="请在此输入文案内容，每行一句话...",
                    lines=8,
                    info="请输入需要格式化的文案，支持多行文本",
                    elem_id="input_text"
                )
                
                format_button = gr.Button(
                    value="格式化文案",
                    variant="primary",
                    size="md",
                    elem_id="format_button"
                )
                
                output_text = gr.Textbox(
                    label="格式化结果",
                    lines=12,
                    info="格式化后的结构化数据将显示在这里",
                    interactive=False,
                    elem_id="output_text"
                )
            
            # 右侧：配音功能
            with gr.Column(scale=1):
                gr.Markdown("### 🎤 配音功能")
                
                # 主题输入框
                topic_input = gr.Textbox(
                    label="主题名称",
                    placeholder="请输入项目主题名称...",
                    info="将作为项目文件夹名称",
                    elem_id="topic_input"
                )
                
                # 配音按钮
                voice_button = gr.Button(
                    value="🎤 开始配音",
                    variant="secondary",
                    size="md",
                    elem_id="voice_button"
                )
                
                # TTS 音频预览
                tts_dropdown = gr.Dropdown(
                    choices=["请选择"],
                    label="音频文件选择",
                    value="请选择",
                    info="选择要播放的音频文件",
                    interactive=True,  # 修复：设置为可交互
                    elem_id="tts_dropdown"
                )
                
                # 音频播放器
                tts_audio_player = gr.Audio(
                    label="音频播放器",
                    type="filepath",
                    interactive=True,  # 确保音频播放器是可交互的
                    elem_id="tts_audio_player"
                )
        
        # 绑定按钮点击事件
        format_button.click(
            fn=format_text,
            inputs=input_text,
            outputs=output_text
        )
        
        # 绑定音频选择变化事件
        def update_tts_audio_preview(choice, topic_name):
            # 如果是"请选择"或错误提示信息，直接返回 None
            if choice == "请选择" or choice == "未找到音频文件":
                return None
            
            # 构建实际的TTS音频文件路径
            if topic_name:
                audio_path = f"draft/JianyingPro Drafts/{topic_name}/Resources/audioAlg/{choice}"
                if os.path.exists(audio_path):
                    return audio_path
            
            return None
        
        tts_dropdown.change(
            fn=update_tts_audio_preview,
            inputs=[tts_dropdown, topic_input],
            outputs=tts_audio_player
        )
        
        # 绑定配音按钮点击事件
        def voice_generation_with_updates(content, topic_name):
            import time
            
            if not content or not content.strip():
                yield (None, None)
                return
            
            if not topic_name or not topic_name.strip():
                yield (None, None)
                return
            
            try:
                # 实时更新配音状态
                status_messages = [
                    "正在准备配音...",
                    "正在复制项目模板...",
                    "正在生成语音文件...",
                    "正在优化音频质量...",
                    "配音生成完成！"
                ]
                
                for message in status_messages:
                    time.sleep(0.5)  # 模拟处理时间
                    yield (None, None)
                
                # 执行完整的配音工作流程
                result = process_complete_workflow(content, topic_name)
                
                if result.get("status") == "success":
                    # 获取更新后的结构化数据并格式化为JSON字符串
                    updated_data = result.get('voice_result', {}).get('updated_data', [])
                    if updated_data:
                        formatted_json = "[\n"
                        for i, item in enumerate(updated_data):
                            formatted_json += f"  {{\n"
                            formatted_json += f"    'id': {item['id']},\n"
                            formatted_json += f"    'text': '{item['text']}',\n"
                            formatted_json += f"    'audio_length': {item['audio_length']},\n"
                            # video_path 暂时留空
                            formatted_json += f"    'video_path': '',\n"
                            # audio_patch 显示完整音频路径
                            audio_path = f"draft/JianyingPro Drafts/{topic_name}/Resources/audioAlg/{item.get('audio_patch', '')}"
                            formatted_json += f"    'audio_patch': '{audio_path}'\n"
                            if i < len(updated_data) - 1:
                                formatted_json += "  },\n"
                            else:
                                formatted_json += "  }\n"
                        formatted_json += "]"
                    else:
                        formatted_json = ""
                    
                    # 参考v4.py的模式：重新加载 TTS 下拉框
                    audio_dir = Path(f"draft/JianyingPro Drafts/{topic_name}/Resources/audioAlg/")
                    if audio_dir.exists():
                        draft_files = ["请选择"] + [f.name for f in audio_dir.iterdir() if f.suffix.lower() in [".wav", ".mp3"]]
                    else:
                        draft_files = ["请选择", "未找到音频文件"]
                    
                    yield (gr.update(choices=draft_files, value="请选择"), formatted_json)
                else:
                    yield (gr.update(choices=["请选择"]), "")
                    
            except Exception as e:
                yield (gr.update(choices=["请选择"]), "")
        
        # 绑定配音按钮点击事件
        voice_button.click(
            fn=voice_generation_with_updates,
            inputs=[input_text, topic_input],
            outputs=[tts_dropdown, output_text]
        )
        
        # 添加示例文案
        gr.Examples(
            examples=[
                ["是曾经拥有过全世界的绚烂，最后只剩下一地鸡毛的凄凉。\n这种落差，比从未拥有过更让人绝望。", "李清照词赏析"],
                ["开篇连用14个叠字，寻寻觅觅，冷冷清清，凄凄惨惨戚戚。\n看似只是文字的堆叠，实则是一个女人在精神崩溃边缘的低声呢喃。", "声声慢解析"],
                ["它被公认为宋词里的\"万古愁心之祖\"。\n全篇没有一个\"泪\"字，却让无数人在读完后感到窒息般的压抑。", "宋词经典赏析"]
            ],
            inputs=[input_text, topic_input],
            label="示例文案"
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_port=9005)