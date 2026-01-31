from cv2.gapi import video
import gradio as gr, os, json

from src.agent_v5 import format_content, process_complete_workflow, match_video, match_multiple_videos, delete_video
from src.autocut.cut_v5 import autoCut
from src.tts.cosyvoice.tts import TTS
import time

# 全局变量存储候选视频信息
candidate_videos_state = {
    "sentence_id": None,
    "text": "",
    "audio_length": "",
    "videos": []
}

def regenerate_audio_for_sentence(text: str, sentence_id: int, topic_name: str) -> tuple:
    """
    重新生成单个句子的语音
    
    Args:
        text (str): 文本内容
        sentence_id (int): 句子ID
        topic_name (str): 主题名称
        
    Returns:
        tuple: (audio_path, audio_length, success_message)
    """
    try:
        print(f"[INFO] 开始重新生成句子 {sentence_id} 的语音: {text}")
        
        # 确保目标目录存在
        target_dir = f"draft/JianyingPro Drafts/{topic_name}/Resources/audioAlg"
        os.makedirs(target_dir, exist_ok=True)
        
        # 初始化TTS
        tts = TTS(voice_id="刘涛", speech_rate=1.2)
        
        # 生成音频文件名
        audio_filename = f"{sentence_id}.mp3"
        audio_path = os.path.join(target_dir, audio_filename)
        
        # 生成音频文件
        print(f"尝试生成音频文件: {text}")
        success = tts.textToAudio(text=text, out_path=audio_path)
        
        if success:
            # 获取音频时长
            from src.agent_v5 import get_audio_duration
            audio_length = get_audio_duration(audio_path)
            if audio_length is None:
                audio_length = 3  # 默认时长
                
            success_message = f"✅ 句子 {sentence_id} 语音重新生成成功！"
            print(f"[INFO] 句子 {sentence_id} 语音重新生成完成，音频长度: {audio_length}秒")
            
            return audio_path, audio_length, success_message
        else:
            error_message = f"❌ 句子 {sentence_id} 语音重新生成失败"
            print(f"[ERROR] 句子 {sentence_id} 语音重新生成失败")
            return None, None, error_message
            
    except Exception as e:
        error_message = f"❌ 重新生成语音时出错: {str(e)}"
        print(f"[ERROR] 重新生成语音时出错: {e}")
        return None, None, error_message

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
                'audio_patch': '',  # 暂时留空（配音后会被更新）
                'danmu': '', # 弹幕内容
                'danmu_style': '' # 弹幕样式
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
    with gr.Blocks() as demo:
        with gr.Row():
            # 左侧：文案格式化功能
            with gr.Column(scale=1):
                # 主题输入框
                topic_input = gr.Textbox(
                    label="主题名称",
                    placeholder="请输入项目主题名称...",
                    elem_id="topic_input"
                )

                input_text = gr.Textbox(
                    label="输入文案",
                    placeholder="请在此输入文案内容，每行一句话...",
                    lines=3,
                    elem_id="input_text"
                )
                
                format_button = gr.Button(
                    value="格式化文案 ①",
                    variant="primary",
                    size="md",
                    elem_id="format_button"
                )
                
                output_text = gr.Textbox(
                    label="格式化数据",
                    lines=6,
                    max_lines=6,
                    interactive=True,
                    elem_id="output_text"
                )
            
            # 右侧：配音功能
            with gr.Column():
                                # 文案片段选择和重新生成按钮
                with gr.Row():
                    # 配音按钮
                    voice_button = gr.Button(
                        value="🎤 开始配音 ②",
                        variant="secondary",
                        size="md",
                        elem_id="voice_button",
                        elem_classes=["matchvoice"]
                    )
                    # 文案片段选择
                    tts_dropdown = gr.Dropdown(
                        choices=["请选择"],
                        label="文案片段选择",
                        value="请选择",
                        interactive=True,  # 修复：设置为可交互
                        elem_id="tts_dropdown",
                        scale=3
                    )
                    
                    # 加载数据按钮
                    load_data_button = gr.Button(
                        value="📂 加载数据",
                        variant="secondary",
                        size="lg",
                        elem_id="load_data_button",
                        scale=1,
                        min_width=100,
                        elem_classes=["matchvoice"]
                    )

                with gr.Row():
                    with gr.Column(scale=1):
                        # 保留原有的主背景视频播放器
                        tts_video_player = gr.Video(
                            label="背景视频",
                            interactive=False,
                            elem_id="tts_video_player",
                            scale=3,
                            height=255
                        )
                    with gr.Column(scale=1):
                        # 音频播放器
                        tts_audio_player = gr.Audio(
                            label="音频播放器",
                            type="filepath",
                            interactive=False,  # 确保音频播放器是可交互的
                            elem_id="tts_audio_player",
                            elem_classes=["audioplayer"],
                            show_label=False
                        )
                        # 重新生成按钮
                        regen_audio_button = gr.Button(
                            value="🔄 重新生成",
                            variant="secondary",
                            size="lg",
                            elem_id="regen_audio_button",
                            scale=1,
                            min_width=100,
                            elem_classes=["matchvoice"]
                        )
                with gr.Row():
                    with gr.Column(scale=1):
                        # 视频数量选择器
                        video_count_selector = gr.Dropdown(
                            choices=[32, 40],
                            value=40,
                            label="📊 候选视频数量",
                            interactive=True,
                            elem_id="video_count_selector",
                            elem_classes=["houxunvideo"]
                        )
                    with gr.Column(scale=1):
                        # 配视频按钮
                        video_button = gr.Button(
                            value="🎥 开始配视频 ③",
                            variant="primary",
                            size="lg",
                            elem_id="video_button",
                            elem_classes=["matchvideo"]
                        )
        # 弹幕配置区域
        with gr.Row():
            # 弹幕配置标题
            with gr.Column(scale=1):
                gr.Markdown("### 💬 弹幕配置")
                with gr.Row():
                # 弹幕文本输入框（重点标注）
                    danmu_text_input = gr.TextArea(
                        label="📝 弹幕文本",
                        placeholder="请输入要显示的弹幕内容...",
                        interactive=True,
                        elem_id="danmu_text_input",
                        scale=3,
                        lines=4,
                    )
                    
                    # 弹幕位置选择器
                    danmu_position_dropdown = gr.Dropdown(
                        choices=["请选择", "middle", "top", "bottom", "left", "right"],
                        value="请选择",
                        label="📍 弹幕位置",
                        interactive=True,
                        elem_id="danmu_position_dropdown"
                    )
            with gr.Column(scale=1):
                gr.Markdown("📚 翻页")        
                with gr.Row():
                    now_text = gr.Text(
                        label="📜 当前文案",
                        value="",
                        interactive=False,
                        elem_id="text"
                    )
                with gr.Row():
                    prev_button = gr.Button(
                        value="⬅️ 上一条",
                        variant="secondary",
                        size="lg",
                        elem_id="prev_button",
                        scale=1,
                        min_width=100
                    )
                    next_button = gr.Button(    
                        value="➡️ 下一条",
                        variant="primary",
                        size="lg",
                        elem_id="next_button",
                        scale=1,
                        min_width=100
                    )

        # 候选视频区域
        # 创建五行8列的候选视频布局（总共40个候选视频）
        candidate_videos = []
        candidate_buttons = []
        delete_buttons = []
        
        # 创建40个候选视频的布局（5行8列）
        for row_start in range(0, 40, 8):
            with gr.Row():
                for i in range(row_start + 1, min(row_start + 9, 41)):
                    with gr.Column(elem_classes=["width350"], min_width=50):
                        # 视频播放器
                        video_player = gr.Video(
                            label=f"候选视频 {i}",
                            interactive=False,
                            elem_id=f"candidate_video_{i}",
                            height=150,  # 减少高度以适应更多视频
                            autoplay=True,
                            loop=True,
                            include_audio=False
                        )
                        candidate_videos.append(video_player)
                        
                        # 选择和删除按钮布局
                        with gr.Row():
                            # 选择按钮（3/4宽度）
                            select_button = gr.Button(
                                value=f"选择",
                                variant="secondary",
                                size="sm",
                                elem_id=f"select_video_{i}",
                                scale=3,
                                min_width=75
                            )
                            candidate_buttons.append(select_button)
                            
                            # 删除按钮（1/4宽度）
                            delete_button = gr.Button(
                                value="删除",
                                variant="stop",
                                size="sm",
                                elem_id=f"delete_video_{i}",
                                scale=1,
                                min_width=25
                            )
                            delete_buttons.append(delete_button)
        
        # 存储候选视频信息的隐藏组件
        candidate_videos_info = gr.Textbox(
            label="候选视频信息",
            visible=False,
            elem_id="candidate_videos_info",
            value=""
        )
                        # 背景音乐选择器
        bgm_dropdown = gr.Dropdown(
            choices=["无"] + [f for f in os.listdir('material/bgm') if f.endswith('.mp3')],
            label="🎵 背景音乐",
            value="无",
            info="选择背景音乐",
            interactive=True,
            elem_id="bgm_dropdown"
        )
        
        # 背景音乐播放器
        bgm_audio_player = gr.Audio(
            label="背景音乐预览",
            type="filepath",
            interactive=False,
            elem_id="bgm_audio_player"
        )        
        general_button = gr.Button(
            value="🚀 开始生成",
            variant="primary",
            size="md",
            elem_id="general_button"
        )

        result_text = gr.Textbox(
            label="生成结果",
            lines=12,
            info="生成的视频和音频将显示在这里",
            interactive=False,
            elem_id="result_text"
        )

        # 生成草稿
        def general_draft(topic_input, output_text, bgm_name):
            # 调用草稿生成函数
            bgm_file = bgm_name if bgm_name and bgm_name != "无" else ""
            cut = autoCut(title=topic_input, list=output_text, bgm=bgm_file)
            result = cut.general_draft()
            if result:
                bgm_display = bgm_name.replace('.mp3', '') if bgm_name and bgm_name != "无" else "无"
                return f'✅ 草稿生成成功！\n背景音乐: {bgm_display}'
            else:
                return "生成失败"

        general_button.click(
            fn=general_draft,
            inputs=[topic_input, output_text, bgm_dropdown],
            outputs=[result_text]
        )
        
        # 绑定按钮点击事件
        format_button.click(
            fn=format_text,
            inputs=input_text,
            outputs=output_text
        )
        
        # 绑定音频选择变化事件
        def update_tts_audio_preview(choice, topic_name, output_data):
            # 如果是"请选择"，直接返回 None
            if choice == "请选择":
                return None, None, ""
            
            audio_path = None
            video_path = None
            text_content = ""
            
            # 从输出数据中查找对应的音频和视频路径
            if output_data and choice != "请选择":
                try:
                    # 解析JSON数据
                    import json
                    data = json.loads(output_data)
                    
                    # 从choice中提取句子ID
                    if "句子" in choice:
                        sentence_id = int(choice.split("句子")[1].split(":")[0])
                        
                        # 查找对应的audio_patch和video_path
                        for item in data:
                            if item.get('id') == sentence_id:
                                # 获取文本内容
                                text_content = item.get('text', '')
                                
                                # 获取音频路径 - 直接使用audio_patch的值
                                audio_patch = item.get('audio_patch', '')
                                
                                # 构建完整音频路径
                                if audio_patch:
                                    audio_path = audio_patch
                                
                                # 获取视频路径
                                video_patch = item.get('video_path', '')
                                if video_patch:
                                    video_path = video_patch
                                break
                except Exception as e:
                    print(f"[ERROR] 解析JSON数据时出错: {e}")
                    print(f"[DEBUG] 原始输出数据: {output_data[:500]}...")
            
            return audio_path, video_path, text_content
        
        tts_dropdown.change(
            fn=update_tts_audio_preview,
            inputs=[tts_dropdown, topic_input, output_text],
            outputs=[tts_audio_player, tts_video_player, now_text]
        )
        
        # 弹幕文本输入和位置选择事件处理
        def update_danmu_config(danmu_text, danmu_position, selected_choice, output_data):
            """
            处理弹幕文本和位置配置的更新
            只有在选择了danmu_style时（不是"请选择"）才进行更新
            如果选择了"请选择"，则清空danmu和danmu_style字段
            """
            if not output_data or not selected_choice or selected_choice == "请选择":
                return output_data
            
            try:
                # 从选择的句子中提取ID
                if "句子" in selected_choice:
                    sentence_id = int(selected_choice.split("句子")[1].split(":")[0])
                    
                    # 解析输出数据
                    data = json.loads(output_data)
                    
                    # 更新对应的句子的弹幕配置
                    for item in data:
                        if item.get('id') == sentence_id:
                            # 只有在选择了danmu_style时才进行更新
                            if danmu_position and danmu_position != "请选择":
                                # 更新弹幕位置
                                item['danmu_style'] = danmu_position
                                
                                # 如果有弹幕文本，也更新弹幕文本
                                if danmu_text and danmu_text.strip():
                                    # 对换行符进行转义处理
                                    escaped_danmu_text = danmu_text.strip().replace('\n', '\\n')
                                    item['danmu'] = escaped_danmu_text
                                else:
                                    # 如果没有弹幕文本，设置为空字符串
                                    item['danmu'] = ""
                                
                                print(f"[DEBUG] 更新句子 {sentence_id} 的弹幕配置: text={danmu_text}, position={danmu_position}")
                            elif danmu_position == "请选择":
                                # 如果选择了"请选择"，清空弹幕相关字段
                                item['danmu'] = ""
                                item['danmu_style'] = ""
                                print(f"[DEBUG] 清空句子 {sentence_id} 的弹幕配置")
                            
                            break
                    
                    # 返回更新后的JSON数据
                    return json.dumps(data, ensure_ascii=False, indent=2)
            
            except Exception as e:
                print(f"[ERROR] 更新弹幕配置时出错: {e}")
                return output_data
            
            return output_data
        
        # 绑定弹幕文本输入事件（不直接触发更新，只保存状态）
        def update_danmu_text_only(danmu_text, selected_choice, output_data):
            """
            只更新弹幕文本输入框的状态，不触发格式化结果更新
            """
            if not output_data or not selected_choice or selected_choice == "请选择":
                return output_data
            
            # 这个函数主要用于保存弹幕文本输入状态
            # 实际的格式化结果更新在位置选择器change时触发
            return output_data
        
        danmu_text_input.change(
            fn=update_danmu_text_only,
            inputs=[danmu_text_input, tts_dropdown, output_text],
            outputs=[output_text]
        )
        
        # 绑定弹幕位置选择事件（主要更新逻辑）
        danmu_position_dropdown.change(
            fn=update_danmu_config,
            inputs=[danmu_text_input, danmu_position_dropdown, tts_dropdown, output_text],
            outputs=[output_text]
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
                # 执行完整的配音工作流程
                result = process_complete_workflow(content, topic_name)
                
                if result.get("status") == "success":
                    print(f"[INFO] 配音完成")
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
                                'audio_patch': audio_path,
                                'danmu': item.get('danmu', ''),
                                'danmu_style': item.get('danmu_style', '')
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
        
        # 加载数据按钮的事件处理
        def load_data_to_dropdown(output_data):
            """
            加载格式化数据到文案片段选择下拉框
            """
            if not output_data:
                return gr.update(choices=["请选择"], value="请选择")
            
            try:
                data = json.loads(output_data)
                if not data:
                    return gr.update(choices=["请选择"], value="请选择")
                
                # 生成选项列表
                segment_choices = ["请选择"]
                for item in data:
                    item_id = item.get('id', '')
                    item_text = item.get('text', '')[:20] if item.get('text') else ''
                    choice_label = f"句子{item_id}: {item_text}..."
                    segment_choices.append(choice_label)
                
                print(f"[INFO] 加载了 {len(data)} 个文案片段")
                return gr.update(choices=segment_choices, value="请选择")
                
            except Exception as e:
                print(f"[ERROR] 加载数据失败: {e}")
                return gr.update(choices=["请选择"], value="请选择")
        
        # 绑定加载数据按钮点击事件
        load_data_button.click(
            fn=load_data_to_dropdown,
            inputs=[output_text],
            outputs=[tts_dropdown]
        )
        
        # 上一条按钮的事件处理
        def go_to_prev_item(selected_choice, output_data):
            """
            处理上一条按钮点击
            将下拉选择向上移动，并将当前选择的文案显示到text文本框
            """
            if not output_data or selected_choice == "请选择":
                return gr.update(choices=["请选择"], value="请选择"), ""
            
            try:
                data = json.loads(output_data)
                if not data:
                    return gr.update(choices=["请选择"], value="请选择"), ""
                
                # 生成所有选项
                segment_choices = ["请选择"]
                for item in data:
                    item_id = item.get('id', '')
                    item_text = item.get('text', '')[:20] if item.get('text') else ''
                    choice_label = f"句子{item_id}: {item_text}..."
                    segment_choices.append(choice_label)
                
                # 解析当前选择的句子ID
                current_id = None
                if "句子" in selected_choice:
                    current_id = int(selected_choice.split("句子")[1].split(":")[0])
                
                # 找到当前句子的索引
                current_index = -1
                for i, item in enumerate(data):
                    if item.get('id') == current_id:
                        current_index = i
                        break
                
                if current_index <= 0:
                    # 已经是第一条，跳转到最后一条
                    new_index = len(data) - 1
                else:
                    new_index = current_index - 1
                
                # 获取新句子的信息
                new_item = data[new_index]
                new_id = new_item.get('id', 0)
                new_text = new_item.get('text', '')
                
                # 生成新的选择标签
                choice_label = f"句子{new_id}: {new_text[:20]}..."
                
                print(f"[DEBUG] 上一条: 从 {current_id} 跳转到 {new_id}")
                
                return gr.update(choices=segment_choices, value=choice_label), new_text
                
            except Exception as e:
                print(f"[ERROR] 上一条处理失败: {e}")
                return gr.update(choices=["请选择"], value="请选择"), ""
        
        # 下一条按钮的事件处理
        def go_to_next_item(selected_choice, output_data):
            """
            处理下一条按钮点击
            将下拉选择向下移动，并将当前选择的文案显示到text文本框
            """
            if not output_data or selected_choice == "请选择":
                return gr.update(choices=["请选择"], value="请选择"), ""
            
            try:
                data = json.loads(output_data)
                if not data:
                    return gr.update(choices=["请选择"], value="请选择"), ""
                
                # 生成所有选项
                segment_choices = ["请选择"]
                for item in data:
                    item_id = item.get('id', '')
                    item_text = item.get('text', '')[:20] if item.get('text') else ''
                    choice_label = f"句子{item_id}: {item_text}..."
                    segment_choices.append(choice_label)
                
                # 解析当前选择的句子ID
                current_id = None
                if "句子" in selected_choice:
                    current_id = int(selected_choice.split("句子")[1].split(":")[0])
                
                # 找到当前句子的索引
                current_index = -1
                for i, item in enumerate(data):
                    if item.get('id') == current_id:
                        current_index = i
                        break
                
                if current_index >= len(data) - 1:
                    # 已经是最后一条，跳转到第一条
                    new_index = 0
                else:
                    new_index = current_index + 1
                
                # 获取新句子的信息
                new_item = data[new_index]
                new_id = new_item.get('id', 0)
                new_text = new_item.get('text', '')
                
                # 生成新的选择标签
                choice_label = f"句子{new_id}: {new_text[:20]}..."
                
                print(f"[DEBUG] 下一条: 从 {current_id} 跳转到 {new_id}")
                
                return gr.update(choices=segment_choices, value=choice_label), new_text
                
            except Exception as e:
                print(f"[ERROR] 下一条处理失败: {e}")
                return gr.update(choices=["请选择"], value="请选择"), ""
        
        # 绑定上一条按钮点击事件
        prev_button.click(
            fn=go_to_prev_item,
            inputs=[tts_dropdown, output_text],
            outputs=[tts_dropdown, now_text]
        )
        
        # 绑定下一条按钮点击事件
        next_button.click(
            fn=go_to_next_item,
            inputs=[tts_dropdown, output_text],
            outputs=[tts_dropdown, now_text]
        )
        
        # 重新生成按钮的事件处理
        def handle_regenerate_audio(selected_choice, topic_name, output_data):
            """
            处理重新生成语音的逻辑
            """
            if selected_choice == "请选择":
                return None, "请先选择一个文案片段", output_data
            
            try:
                # 从选择的句子中提取ID
                if "句子" in selected_choice:
                    sentence_id = int(selected_choice.split("句子")[1].split(":")[0])
                    
                    # 从输出数据中找到对应的文本
                    if output_data:
                        data = json.loads(output_data)
                        for item in data:
                            if item.get('id') == sentence_id:
                                text = item.get('text', '')
                                if not text:
                                    return None, "未找到对应文本", output_data
                                
                                # 重新生成语音，获取音频路径和长度
                                audio_path, audio_length, message = regenerate_audio_for_sentence(
                                    text=text, 
                                    sentence_id=sentence_id, 
                                    topic_name=topic_name
                                )
                                
                                # 更新输出数据中的audio_patch和audio_length
                                if audio_path and audio_length is not None:
                                    item['audio_patch'] = audio_path  # 保存完整路径
                                    item['audio_length'] = audio_length
                                    # 重新生成JSON字符串
                                    updated_output_data = json.dumps(data, ensure_ascii=False, indent=2)
                                    
                                    print(f"[INFO] 已更新句子 {sentence_id} 的音频信息: 路径={item['audio_patch']}, 长度={audio_length}秒")
                                    
                                    return audio_path, f"{message}\n\n✅ 已更新到音频播放器，音频长度: {audio_length}秒", updated_output_data
                                elif audio_path:
                                    # 如果只有路径但没有长度，至少更新路径
                                    item['audio_patch'] = audio_path  # 保存完整路径
                                    # 重新生成JSON字符串
                                    updated_output_data = json.dumps(data, ensure_ascii=False, indent=2)
                                    
                                    return audio_path, f"{message}\n\n✅ 已更新到音频播放器", updated_output_data
                                else:
                                    return None, message, output_data
                                break
                    else:
                        return None, "没有可用的格式化数据", output_data
                else:
                    return None, "无效的选择格式", output_data
                    
            except Exception as e:
                error_msg = f"重新生成失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                return None, error_msg, output_data
        
        # 绑定重新生成按钮事件
        regen_audio_button.click(
            fn=handle_regenerate_audio,
            inputs=[tts_dropdown, topic_input, output_text],
            outputs=[tts_audio_player, result_text, output_text]
        )

        # 背景音乐选择器变化时直接更新播放器
        def update_bgm_player(bgm_name):
            if bgm_name == "无":
                return None
            bgm_path = f"material/bgm/{bgm_name}"
            if os.path.exists(bgm_path):
                return bgm_path
            return None
        
        bgm_dropdown.change(
            fn=update_bgm_player,
            inputs=[bgm_dropdown],
            outputs=[bgm_audio_player]
        )
        
        # 绑定视频按钮点击事件        
        def match_video_for_selection(choice, topic_name, output_data, video_count):
            """
            处理视频匹配，根据用户选择展示相应数量的候选视频
            """
            # 如果是"请选择"，直接返回
            if choice == "请选择":
                print("[DEBUG] 用户选择了'请选择'，清空候选视频")
                return tuple([None] * 40 + [output_data, "", None])

            # 根据选择动态初始化数组
            video_paths = [None] * 40  # 初始化40个视频路径
            video_content = [None] * 40  # 初始化40个视频内容用于UI
            selection_info = {"sentence_id": None, "video_index": None}
            candidate_info_json = ""
            updated_data = None  # 用于存储更新后的数据
            
            # 从输出数据中查找对应的文本
            if output_data and choice != "请选择":
                try:
                    # 解析JSON数据
                    data = json.loads(output_data)
                    
                    # 从choice中提取句子ID
                    if "句子" in choice:
                        sentence_id = int(choice.split("句子")[1].split(":")[0])
                        selection_info["sentence_id"] = sentence_id
                        
                        # 查找对应的文本
                        for item in data:
                            if item.get('id') == sentence_id:
                                text = item.get('text', '')
                                audio_length = item.get('audio_length', '')
                                
                                # 根据用户选择获取对应数量的候选视频
                                if text:
                                    video_list = match_multiple_videos(text=text, audio_length=audio_length, n_results=video_count)
                                    print(f"[DEBUG] 获取到 {len(video_list)} 个候选视频")
                                    # 更新视频路径列表（最多40个视频）
                                    for i, video_info in enumerate(video_list):
                                        if i < 40:  # UI最多显示40个
                                            video_paths[i] = video_info["file_path"]
                                            video_content[i] = video_info["content"]
                                    # 为多余的槽位设置占位符
                                    for i in range(len(video_list), 40):
                                        video_paths[i] = None  # 多余的槽位保持为None
                                    
                                    # 匹配最佳视频
                                    # match_video_index = match_video(text=str(video_content))
                                    match_video_index = 0
                                    print(f"[DEBUG] 最佳视频index: {match_video_index}")
                                    
                                    # 直接将最佳视频更新到格式化结果中
                                    if match_video_index is not None and 0 <= match_video_index < len(video_list):
                                        best_video_path = video_list[match_video_index]["file_path"]
                                        item['video_path'] = best_video_path
                                    
                                    # 保存更新后的数据
                                    updated_data = data
                                    
                                    # 更新全局状态
                                    candidate_videos_state.update({
                                        "sentence_id": sentence_id,
                                        "text": text,
                                        "audio_length": audio_length,
                                        "videos": video_list
                                    })
                                    candidate_info_json = json.dumps(candidate_videos_state, ensure_ascii=False)
                                    break
                                    
                except Exception as e:
                    print(f"[ERROR] 匹配视频时出错: {e}")
            
            # 返回40个视频路径、更新后的输出数据、选择信息和候选视频信息
            # 确保最佳视频显示在tts_video_player中
            best_video_for_player = None
            if match_video_index is not None and 0 <= match_video_index < len(video_paths):
                best_video_for_player = video_paths[match_video_index]
            
            return tuple([video_paths[0], video_paths[1], video_paths[2], video_paths[3], video_paths[4], 
                         video_paths[5], video_paths[6], video_paths[7], video_paths[8], video_paths[9], 
                         video_paths[10], video_paths[11], video_paths[12], video_paths[13], video_paths[14],
                         video_paths[15], video_paths[16], video_paths[17], video_paths[18], video_paths[19],
                         video_paths[20], video_paths[21], video_paths[22], video_paths[23], video_paths[24],
                         video_paths[25], video_paths[26], video_paths[27], video_paths[28], video_paths[29],
                         video_paths[30], video_paths[31], video_paths[32], video_paths[33], video_paths[34],
                         video_paths[35], video_paths[36], video_paths[37], video_paths[38], video_paths[39],
                         json.dumps(updated_data, ensure_ascii=False, indent=2) if updated_data else output_data, 
                         candidate_info_json, best_video_for_player])

        # 为每个候选视频选择按钮创建事件处理函数
        def create_video_selection_handler(video_index):
            def select_video(output_data):
                """
                处理视频选择，更新格式化和主视频播放器
                """
                print(f"[DEBUG] 选择按钮 {video_index + 1} 被点击")
                print(f"[DEBUG] 全局状态: sentence_id={candidate_videos_state.get('sentence_id')}, 视频数量={len(candidate_videos_state.get('videos', []))}")
                print(f"[DEBUG] 输出数据长度: {len(output_data) if output_data else 'None'}")
                
                if not output_data:
                    print("[WARNING] 输出数据为空")
                    return None, output_data
                
                # 检查全局状态中是否有候选视频信息
                sentence_id = candidate_videos_state.get("sentence_id")
                videos = candidate_videos_state.get("videos", [])
                
                if sentence_id is None or not videos:
                    print("[WARNING] 没有候选视频信息或句子ID为空")
                    return None, output_data
                
                try:
                    # 检查视频索引是否有效
                    if video_index >= len(videos) or video_index < 0:
                        print(f"[ERROR] 无效的视频索引: {video_index}, 视频列表长度: {len(videos)}")
                        return None, output_data
                    
                    # 获取选中的视频信息
                    selected_video = videos[video_index]
                    selected_video_path = selected_video.get("file_path", "")
                    
                    print(f"[DEBUG] 选中的视频路径: {selected_video_path}")
                    
                    # 解析当前格式化数据
                    data = json.loads(output_data)
                    
                    # 更新对应句子的video_path
                    for item in data:
                        if item.get('id') == sentence_id:
                            old_path = item.get('video_path', '')
                            item['video_path'] = selected_video_path
                            print(f"[DEBUG] 更新句子 {sentence_id} 的视频路径: {old_path} -> {selected_video_path}")
                            break
                    
                    # 重新生成JSON字符串
                    updated_output_data = json.dumps(data, ensure_ascii=False, indent=2)
                    
                    print(f"[INFO] 为句子 {sentence_id} 选择视频 {video_index + 1}: {selected_video_path}")
                    
                    # 返回选中的视频路径和更新的格式化数据
                    return selected_video_path, updated_output_data
                    
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON解析错误: {e}")
                    return None, output_data
                except Exception as e:
                    print(f"[ERROR] 选择视频时出错: {e}")
                    return None, output_data
            
            return select_video

        # 为每个候选视频删除按钮创建事件处理函数
        def create_video_deletion_handler(video_index):
            def delete_video_handler():
                """
                处理视频删除，从候选视频列表中移除指定的视频
                """
                try:
                    # 检查全局状态中是否有候选视频信息
                    sentence_id = candidate_videos_state.get("sentence_id")
                    videos = candidate_videos_state.get("videos", [])
                    
                    if sentence_id is None or not videos:
                        print("[WARNING] 没有候选视频信息或句子ID为空")
                        return None, None, "❌ 没有候选视频信息，无法删除"
                    
                    # 检查视频索引是否有效
                    if video_index >= len(videos) or video_index < 0:
                        print(f"[ERROR] 无效的视频索引: {video_index}, 视频列表长度: {len(videos)}")
                        return None, None, f"❌ 无效的视频索引: {video_index + 1}"
                    
                    # 获取要删除的视频信息
                    video_to_delete = videos[video_index]
                    video_id = video_to_delete.get("id", "")
                    video_file_path = video_to_delete.get("file_path", "")
                    
                    print(f"[DEBUG] 删除视频ID: {video_id}, 路径: {video_file_path}")
                    
                    # 调用删除视频的函数（使用ID和文件路径）
                    delete_success = False
                    if video_id or video_file_path:
                        try:
                            delete_success = delete_video(video_id=video_id, video_file_path=video_file_path)
                            print(f"[INFO] 删除视频结果: {delete_success}")
                        except Exception as e:
                            print(f"[WARNING] 删除视频时出错: {e}")
                    
                    # 从候选视频列表中移除该视频
                    videos.pop(video_index)
                    
                    # 更新全局状态
                    candidate_videos_state.update({
                        "sentence_id": sentence_id,
                        "text": candidate_videos_state.get("text", ""),
                        "audio_length": candidate_videos_state.get("audio_length", ""),
                        "videos": videos
                    })
                    
                    # 生成成功提示消息
                    if delete_success:
                        success_message = f"✅ 成功删除候选视频 {video_index + 1}"
                    else:
                        success_message = f"⚠️ 已从列表移除候选视频 {video_index + 1}（文件删除失败）"
                    
                    print(f"[INFO] {success_message}，剩余视频数量: {len(videos)}")
                    
                    # 返回None表示清空对应的视频播放器
                    return None, None, success_message
                    
                except Exception as e:
                    error_message = f"❌ 删除视频时出错: {str(e)}"
                    print(f"[ERROR] {error_message}")
                    return None, None, error_message
            
            return delete_video_handler

        # 为每个选择按钮绑定事件（支持40个候选视频）
        for i in range(40):
            selection_handler = create_video_selection_handler(i)
            candidate_buttons[i].click(
                fn=selection_handler,
                inputs=[output_text],
                outputs=[tts_video_player, output_text]
            )
            
            # 为对应的删除按钮绑定事件
            deletion_handler = create_video_deletion_handler(i)
            delete_buttons[i].click(
                fn=deletion_handler,
                inputs=[],
                outputs=[candidate_videos[i], candidate_videos_info, result_text]
            )
            

        
        video_button.click(
            fn=match_video_for_selection,
            inputs=[tts_dropdown, topic_input, output_text, video_count_selector],
            outputs=[candidate_videos[0], candidate_videos[1], candidate_videos[2], candidate_videos[3], candidate_videos[4],
                    candidate_videos[5], candidate_videos[6], candidate_videos[7], candidate_videos[8], candidate_videos[9],
                    candidate_videos[10], candidate_videos[11], candidate_videos[12], candidate_videos[13], candidate_videos[14],
                    candidate_videos[15], candidate_videos[16], candidate_videos[17], candidate_videos[18], candidate_videos[19],
                    candidate_videos[20], candidate_videos[21], candidate_videos[22], candidate_videos[23], candidate_videos[24],
                    candidate_videos[25], candidate_videos[26], candidate_videos[27], candidate_videos[28], candidate_videos[29],
                    candidate_videos[30], candidate_videos[31], candidate_videos[32], candidate_videos[33], candidate_videos[34],
                    candidate_videos[35], candidate_videos[36], candidate_videos[37], candidate_videos[38], candidate_videos[39],
                    output_text, candidate_videos_info, tts_video_player]
        )
        
        # 添加示例文案
        gr.Examples(
            examples=[
                ["是曾经拥有过全世界的绚烂，最后只剩下一地鸡毛的凄凉。\n这种落差，比从未拥有过更让人绝望。", "李清照词赏析"],
                ["开篇连用14个叠字，寻寻觅觅，冷冷清清，凄凄惨惨戚戚。\n看似只是文字的堆叠，实则是一个女人在精神崩溃边缘的低声呢喃。", "声声慢解析"],
                ["它被公认为宋词里的万古愁心之祖", "宋词经典赏析"]
            ],
            inputs=[input_text, topic_input],
            label="示例文案"
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    css = """
    .width250 {width: 250px;}
    .width350 {width: 350px;}
    .width450 {width: 450px;}
    .matchvoice {height: 89px;}
    .audioplayer {height: 150px;}
    .houxunvideo {height: 87px;}
    .matchvideo {height: 87px;}
    """
    demo.launch(server_port=9005, css=css, allowed_paths=["D:/Material"])