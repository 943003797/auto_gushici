import gradio as gr
import agent as ag
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
                
                copy_content = gr.TextArea(label="文案内容", lines=10)
                confirm_copy_btn = gr.Button("确认文案")
            
            # 右侧区域
            with gr.Column(scale=1):
                gr.Markdown("## 视频制作")
                # 右边从上到下
                confirmed_theme = gr.Textbox(label="主题", interactive=False)
                confirmed_copy = gr.TextArea(label="文案内容", lines=5, interactive=False)
                
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
        def confirm_copy(theme, copy_text):
            return theme, copy_text
        
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




                
        # 绑定事件
        generate_copy_btn.click(
            fn=ag.general_base_data,
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
        
        generate_video_btn.click(
            fn=lambda: gr.Info("短视频生成中，请稍候..."),
            inputs=None,
            outputs=None
        )
    
    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch()

