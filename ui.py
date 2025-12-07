import gradio as gr
from tomlkit import value
import agent as ag
import os, json
import asyncio
from pathlib import Path

def create_ui():
    with gr.Blocks(title="古诗词短视频生成器") as demo:
        gr.Markdown("# 古诗词短视频生成器")
        
        with gr.Row():
            # Left box
            with gr.Column(scale=1):
                gr.Markdown("## 文案生成")

                # Top to bottoom
                title_input = gr.Textbox(label="主题", placeholder="请输入古诗词主题...")
                generate_poetry_btn = gr.Button("生成文案")
                poetry = gr.Textbox(label="编辑诗词", lines=20, type="text")

                # Confirm poetry button
                confirm_copy_btn = gr.Button("确认文案")
                confirm_poetry = gr.Textbox(label="Confirm poetry", lines=20, type="text", value="")

            # Right box
            with gr.Column(scale=1):
                gr.Markdown("## 视频生成")
                
                generate_tts_btn = gr.Button("配音")
                regenerate_tts_btn = gr.Button("重新生成选中配音")
                # TTS 试听
                tts_dir = Path("material/bgm")
                if tts_dir.exists():
                    tts_files = ["请选择"] + [f.name for f in tts_dir.iterdir() if f.suffix.lower() == ".mp3"]
                else:
                    tts_files = ["请选择", "未找到音频文件"]
                tts_dropdown = gr.Dropdown(
                    choices=tts_files,
                    label="TTS音频预览",
                    value="请选择"
                )
                def generate_tts(title, poetry):
                    print(title, poetry)
                    tts_file = asyncio.run(ag.generate_tts(title, poetry))
                    if tts_file:
                        return []
                    else:
                        return []
                generate_tts_btn.click(
                    fn=generate_tts,
                    inputs=[title_input, confirm_poetry],
                    outputs=[tts_dropdown]
                )

                tts_player = gr.Audio(label="TTS试听", type="filepath")
                def update_tts_audio(choice):
                    # 如果是"请选择"或错误提示信息，直接返回 None
                    if choice == "请选择" or choice == "未找到音频文件":
                        return None
                    # 构建实际的音频文件路径
                    audio_path = f"material/bgm/{choice}"
                    if os.path.exists(audio_path):
                        return audio_path
                    else:
                        return None
                tts_dropdown.change(
                    fn=update_tts_audio,
                    inputs=tts_dropdown,
                    outputs=tts_player
                )


                # 背景音频选择
                # 动态获取 material/bgm 目录下的 MP3 文件
                bgm_dir = Path("material/bgm")
                if bgm_dir.exists():
                    bgm_files = ["请选择"] + [f.name for f in bgm_dir.iterdir() if f.suffix.lower() == ".mp3"]
                else:
                    bgm_files = ["请选择", "未找到音频文件"]
                bg_audio_dropdown = gr.Dropdown(
                    choices=bgm_files,
                    label="背景音频",
                    value="请选择"
                )
                audio_player = gr.Audio(label="背景音频试听", type="filepath")
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
                bg_audio_dropdown.change(
                    fn=update_audio,
                    inputs=bg_audio_dropdown,
                    outputs=audio_player
                )


                # 背景视频选择
                bgv_player = gr.Video(label="背景视频预览")
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
                def update_video_preview(choice):
                    # 如果是"请选择"或错误提示信息，直接返回 None
                    if choice == "请选择" or choice == "未找到视频文件":
                        return None
                    # 构建实际的视频文件路径
                    video_path = f"material/bgv/{choice}"
                    if os.path.exists(video_path):
                        return video_path
                    else:
                        return None
                bg_video_dropdown.change(
                    fn=update_video_preview,
                    inputs=bg_video_dropdown,
                    outputs=bgv_player
                )

        def update_poetry_list(title: str):
            new_choices = asyncio.run(ag.general_poetry(title))
            checkList = []
            for potry in new_choices:
                tmp: tuple = (potry["shiju"], potry["id"])
                checkList.append(tmp)
            return gr.update(value=json.dumps(new_choices, ensure_ascii=False, indent=4))
        generate_poetry_btn.click(
            fn=update_poetry_list,
            inputs=[title_input],
            outputs=[poetry]
        )

        def poetry_append(poetry: str, confirm_poetry: str):
            poetry_list = json.loads(poetry)
            if confirm_poetry == "":
                confirm_poetry_list = []
            else:
                confirm_poetry_list = json.loads(confirm_poetry)
            for item in poetry_list:
                confirm_poetry_list.append(item)

            return json.dumps(confirm_poetry_list, ensure_ascii=False, indent=4)
        confirm_copy_btn.click(
            fn=poetry_append,
            inputs=[poetry, confirm_poetry],
            outputs=[confirm_poetry]
        )

        def update_confirm_poetry_list(poetry_list: list, confirm_poetry_list: list):
            # 将已勾选的诗词追加到右侧确认列表，并去重保持顺序
            merged = confirm_poetry_list.copy()
            for p in poetry_list:
                    merged.append(p)
            return gr.update(choices=merged)

        
    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=9001)



