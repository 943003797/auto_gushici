import gradio as gr
from agent import agent as ag
import os
from pathlib import Path

def create_ui():
    with gr.Blocks(title="古诗词短视频生成器") as demo:
        gr.Markdown("# 古诗词短视频生成器")
        
        with gr.Row():
            # 左侧区域
            with gr.Column(scale=1):
                gr.Markdown("## 文案生成")
                # 左边部分从上到下
                theme_input = gr.Textbox(label="主题", placeholder="请输入古诗词主题...")
                generate_copy_btn = gr.Button("生成文案")
                
                # 左侧多选列表，用于显示生成的古诗词
                copy_content = gr.CheckboxGroup(label="文案内容", choices=[
                    ("1", "问君能有几多愁，恰似一江春水向东流。"),
                    ("2", "国破山河在，城春草木深。"),
                    ("3", "山有木兮木有枝，心悦君兮君不知。")
                ], interactive=True)
                confirm_copy_btn = gr.Button("确认文案")
            
            # 右侧区域
            with gr.Column(scale=1):
                gr.Markdown("## 视频制作")
                # 右边从上到下
                confirmed_theme = gr.Textbox(label="主题", interactive=False)
                # 右侧多选列表，用于显示确认的古诗词
                confirmed_copy = gr.CheckboxGroup(label="文案内容", choices=[], interactive=True)
                delete_copy_btn = gr.Button("删除选中项")
                
                # 背景音频选择
                # 动态获取 material/bgm 目录下的 MP3 文件
                bgm_dir = Path("material/bgm")
                if bgm_dir.exists():
                    audio_files = ["请选择"] + [f.name for f in bgm_dir.iterdir() if f.suffix.lower() == ".mp3"]
                else:
                    audio_files = ["请选择", "未找到音频文件"]
                
                bg_audio_dropdown = gr.Dropdown(
                    choices=audio_files,
                    label="背景音频",
                    value="请选择"
                )
                audio_player = gr.Audio(label="背景音频试听", type="filepath")
                
                # 背景视频选择
                # 动态获取 material/bgv 目录下的 MP4 文件
                bgv_dir = Path("material/bgv")
                if bgv_dir.exists():
                    video_files = ["请选择"] + [f.name for f in bgv_dir.iterdir() if f.suffix.lower() == ".mp4"]
                else:
                    video_files = ["请选择", "未找到视频文件"]
                
                bg_video_dropdown = gr.Dropdown(
                    choices=video_files,
                    label="背景视频",
                    value="请选择"
                )
                video_preview = gr.Video(label="背景视频预览")
                
                generate_video_btn = gr.Button("生成短视频")
        




        # 功能绑定
        def parse_poetry_json(json_str):
            """解析JSON字符串，将其转换为CheckboxGroup的选项格式"""
            import json
            try:
                data = json.loads(json_str)
                choices = []
                # 创建选项元组，格式为 (显示文本, 值)
                for poem in data.get("poems", []):
                    # 格式化显示文本：序号、诗句、诗名、作者、译文
                    display_text = f"{poem['id']}. {poem['shiju']} - {poem['shiming']} ({poem['zuozhe']})\n译文: {poem['yiwen']}"
                    choices.append((display_text, poem['id']))  # (label, value)
                return choices
            except Exception as e:
                print(f"解析JSON时出错: {e}")
                return []

        def confirm_copy(theme, copy_choices):
            """确认文案功能，将左侧选中的项目同步到右侧"""
            # copy_choices 是左侧选中的项目值列表
            # 我们需要获取当前左侧的所有选项，然后筛选出选中的项
            return theme, copy_choices
        
        def update_audio(choice):
            # 如果是"请选择"或错误提示信息，直接返回 None
            if choice == "请选择" or choice == "未找到音频文件":
                return None
            
            # 构建实际的音频文件路径
            audio_path = f"material/bgm/{choice}"
            if os.path.exists(audio_path):
                return audio_path
            else:
                return None
        
        def update_video(choice):
            # 如果是"请选择"或错误提示信息，直接返回 None
            if choice == "请选择" or choice == "未找到视频文件":
                return None
            
            # 构建实际的视频文件路径
            video_path = f"material/bgv/{choice}"
            if os.path.exists(video_path):
                return video_path
            else:
                return None
        
        def delete_selected_poems(selected_poems, current_choices):
            """删除右侧选中的诗词"""
            # current_choices 是当前所有选项 [(label, value), ...]
            # selected_poems 是选中的项的值列表
            # 返回过滤后的选项列表
            if not selected_poems:
                return current_choices
            updated_choices = [choice for choice in current_choices if choice[1] not in selected_poems]
            return updated_choices




        def generate_and_parse_poetry(theme):
            """生成并解析古诗词数据"""
            import asyncio
            # 调用原始函数获取JSON数据
            json_result = asyncio.run(ag.general_base_data(theme))
            print(json_result)
            # 解析JSON并返回CheckboxGroup格式
            return parse_poetry_json(json_result)  
        # 绑定事件
        generate_copy_btn.click(
            fn=generate_and_parse_poetry,
            inputs=theme_input,
            outputs=copy_content
        )

        confirm_copy_btn.click(
            fn=confirm_copy,
            inputs=[theme_input, copy_content],
            outputs=[confirmed_theme, confirmed_copy]
        )
        
        bg_audio_dropdown.change(
            fn=update_audio,
            inputs=bg_audio_dropdown,
            outputs=audio_player
        )
        
        bg_video_dropdown.change(
            fn=update_video,
            inputs=bg_video_dropdown,
            outputs=video_preview
        )
        
        delete_copy_btn.click(
            fn=delete_selected_poems,
            inputs=[confirmed_copy, confirmed_copy],
            outputs=confirmed_copy
        )
        
        generate_video_btn.click(
            fn=lambda: gr.Info("短视频生成中，请稍候..."),
            inputs=None,
            outputs=None
        )
    
    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch()



