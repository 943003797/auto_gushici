import gradio as gr
from agent.agent_v5 import format_content, process_complete_workflow, match_video
from pathlib import Path
import os
import json

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
        
        # 将结构化数据格式化为JSON字符串
        import json
        result_data = []
        for item in structured_data:
            result_data.append({
                'id': item['id'],
                'text': item['text'],
                'audio_length': item['audio_length'],
                'video_path': '',  # 暂时留空（配音后会被更新）
                'audio_patch': ''  # 暂时留空（配音后会被更新）
            })
        
        return json.dumps(result_data, ensure_ascii=False, indent=2)
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
                # 主题输入框
                topic_input = gr.Textbox(
                    label="主题名称",
                    placeholder="请输入项目主题名称...",
                    info="将作为项目文件夹名称",
                    elem_id="topic_input"
                )

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
            with gr.Column():
                gr.Markdown("### 🎤 配音功能")
                
                # 配音按钮
                voice_button = gr.Button(
                    value="🎤 开始配音",
                    variant="secondary",
                    size="md",
                    elem_id="voice_button"
                )
                
                # 文案片段选择
                tts_dropdown = gr.Dropdown(
                    choices=["请选择"],
                    label="文案片段选择",
                    value="请选择",
                    info="选择要播放的文案片段",
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
                
                # 视频播放器
                with gr.Row():
                    tts_video_player = gr.Video(
                        label="视频播放器",
                        interactive=True,
                        elem_id="tts_video_player",
                        scale=3  # 视频播放器占据3/4的宽度
                    )
                    
                    # 配视频按钮
                    video_button = gr.Button(
                        value="🎥 开始配视频",
                        variant="secondary",
                        size="md",
                        elem_id="video_button",
                        scale=1  # 按钮占据1/4的宽度
                    )
        
        # 绑定按钮点击事件
        format_button.click(
            fn=format_text,
            inputs=input_text,
            outputs=output_text
        )
        
        # 绑定音频选择变化事件
        def update_tts_audio_preview(choice, topic_name, output_data):
            print(f"[DEBUG] 选择: {choice}, 主题: {topic_name}, 输出数据存在: {bool(output_data)}")
            
            # 如果是"请选择"，直接返回 None
            if choice == "请选择":
                return None, None
            
            audio_path = None
            video_path = None
            
            # 从输出数据中查找对应的音频和视频路径
            if output_data and choice != "请选择":
                try:
                    # 解析JSON数据
                    import json
                    data = json.loads(output_data)
                    print(f"[DEBUG] JSON数据解析成功，包含 {len(data)} 个项目")
                    print(f"[DEBUG] 第一个项目示例: {data[0] if data else 'None'}")
                    
                    # 从choice中提取句子ID
                    if "句子" in choice:
                        sentence_id = int(choice.split("句子")[1].split(":")[0])
                        print(f"[DEBUG] 提取的句子ID: {sentence_id}")
                        
                        # 查找对应的audio_patch和video_path
                        for item in data:
                            if item.get('id') == sentence_id:
                                print(f"[DEBUG] 找到匹配的项目ID: {item.get('id')}")
                                # 获取音频路径 - 直接使用audio_patch的值
                                audio_patch = item.get('audio_patch', '')
                                print(f"[DEBUG] 原始audio_patch: '{audio_patch}'")
                                
                                # 构建完整音频路径
                                if audio_patch:
                                    audio_path = audio_patch
                                    print(f"[DEBUG] 设置音频路径: {audio_path}")
                                
                                # 获取视频路径
                                video_patch = item.get('video_path', '')
                                print(f"[DEBUG] 原始video_path: '{video_patch}'")
                                if video_patch:
                                    video_path = video_patch
                                    print(f"[DEBUG] 设置视频路径: {video_path}")
                                break
                except Exception as e:
                    print(f"[ERROR] 解析JSON数据时出错: {e}")
                    print(f"[DEBUG] 原始输出数据: {output_data[:500]}...")
            
            print(f"[DEBUG] 最终结果 - 选择: {choice}, 音频路径: {audio_path}, 视频路径: {video_path}")
            return audio_path, video_path
        
        tts_dropdown.change(
            fn=update_tts_audio_preview,
            inputs=[tts_dropdown, topic_input, output_text],
            outputs=[tts_audio_player, tts_video_player]
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
                        import json
                        result_data = []
                        for item in updated_data:
                            # 处理音频路径
                            audio_patch = item.get('audio_patch', '')
                            if audio_patch:
                                # 确保路径使用正斜杠
                                audio_path = f"draft/JianyingPro Drafts/{topic_name}/Resources/audioAlg/{audio_patch}"
                                audio_path = audio_path.replace('\\', '/')
                            else:
                                audio_path = ''
                            
                            # 处理视频路径
                            video_path = item.get('video_path', '')
                            if not video_path or video_path == 'none':
                                # 构造默认视频路径
                                video_filename = f"sentence_{item['id']}.mp4"
                                video_path = f"draft/JianyingPro Drafts/{topic_name}/video_output/{video_filename}"
                            video_path = video_path.replace('\\', '/')
                            
                            result_data.append({
                                'id': item['id'],
                                'text': item['text'],
                                'audio_length': item['audio_length'],
                                'video_path': video_path,
                                'audio_patch': audio_path
                            })
                        
                        formatted_json = json.dumps(result_data, ensure_ascii=False, indent=2)
                    else:
                        formatted_json = ""
                    
                    # 生成文案片段选择列表
                    segment_choices = ["请选择"]
                    for item in updated_data:
                        choice_label = f"句子{item['id']}: {item['text'][:20]}..."
                        segment_choices.append(choice_label)
                    
                    yield (gr.update(choices=segment_choices, value="请选择"), formatted_json)
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

        # 绑定视频按钮点击事件
        def match_video_for_selection(choice, topic_name, output_data):
            # 如果是"请选择"，直接返回
            if choice == "请选择":
                return gr.update(value=None), output_data

            video_path = None
            
            # 从输出数据中查找对应的文本
            if output_data and choice != "请选择":
                try:
                    # 解析JSON数据
                    data = json.loads(output_data)
                    
                    # 从choice中提取句子ID
                    if "句子" in choice:
                        sentence_id = int(choice.split("句子")[1].split(":")[0])
                        
                        # 查找对应的文本
                        for item in data:
                            if item.get('id') == sentence_id:
                                text = item.get('text', '')
                                # 调用match_video获取视频路径
                                if text:
                                    video_path = match_video(text)
                                    print(f"[DEBUG] 匹配视频 - 文案: {text[:30]}..., 视频路径: {video_path}")
                                    
                                    # 更新video_path
                                    item['video_path'] = video_path if video_path else ''
                                    
                                    # 重新生成JSON字符串
                                    output_data = json.dumps(data, ensure_ascii=False, indent=2)
                                    
                                    # 更新下拉框的值为当前选择的句子
                                    choice_value = choice
                                    
                                    print(f"[DEBUG] 更新后的JSON数据: {output_data[:200]}...")
                                    break
                except Exception as e:
                    print(f"[ERROR] 匹配视频时出错: {e}")
            
            return video_path, output_data, choice
        
        video_button.click(
            fn=match_video_for_selection,
            inputs=[tts_dropdown, topic_input, output_text],
            outputs=[tts_video_player, output_text, tts_dropdown]
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
    demo.launch(server_port=9005, allowed_paths=["D:/Material/fragment"])