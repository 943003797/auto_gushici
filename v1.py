import gradio as gr
from tomlkit import value
from agent import agent as ag
from autocut import auto_cut as act
import os, json, shutil
import asyncio
from pathlib import Path
from autocut.auto_cut_v2 import autoCut

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

                # 确认文案按钮和文案输入
                confirm_copy_btn = gr.Button("确认文案")
                confirm_poetry = gr.Textbox(label="Confirm poetry", lines=20)
                
                # 文案输入字段（用于重新生成配音）
                wenan_input = gr.Textbox(label="文案", placeholder="请输入文案文本...", lines=5)

            # Right box
            with gr.Column(scale=1):
                gr.Markdown("## 视频生成")
                
                generate_tts_btn = gr.Button("配音")
                regenerate_tts_btn = gr.Button("重新生成选中配音")
                
                # 参考音频选择
                ref_audio_dir = Path("material/reference_audio")
                if ref_audio_dir.exists():
                    ref_audio_files = ["请选择"] + [f.name for f in ref_audio_dir.iterdir() if f.suffix.lower() in [".wav", ".mp3"]]
                else:
                    ref_audio_files = ["请选择", "未找到参考音频文件"]
                reference_audio_dropdown = gr.Dropdown(
                    choices=ref_audio_files,
                    label="参考音频选择",
                    value="请选择"
                )
                reference_audio_player = gr.Audio(label="参考音频试听", type="filepath")
                
                def update_reference_audio_preview(choice):
                    # 如果是"请选择"或错误提示信息，直接返回 None
                    if choice == "请选择" or choice == "未找到参考音频文件":
                        return None
                    # 构建实际的参考音频文件路径
                    audio_path = f"material/reference_audio/{choice}"
                    if os.path.exists(audio_path):
                        return audio_path
                    else:
                        return None
                reference_audio_dropdown.change(
                    fn=update_reference_audio_preview,
                    inputs=reference_audio_dropdown,
                    outputs=reference_audio_player
                )
                
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
                def generate_tts(title, wenan, poetry, reference_audio_choice):
                    print(title, wenan, poetry)
                    
                    # 获取参考音频文件路径
                    reference_audio_path = "material/reference_audio/风吟.wav"  # 默认值
                    if reference_audio_choice != "请选择" and reference_audio_choice != "未找到参考音频文件":
                        reference_audio_path = f"material/reference_audio/{reference_audio_choice}"
                    
                    draft_dir = os.getenv("DRAFT_DIR") or ""
                    copy_dir("material/baseDraft", draft_dir + title)
                    audio_dir = Path(draft_dir + title + "/Resources/audioAlg/")
                    tts_file = asyncio.run(ag.generate_tts(title, wenan, poetry, str(audio_dir), reference_audio_path))
                    if tts_file:
                        # 重新加载 tts_dropdown，读取 draft 目录下的音频文件
                        if audio_dir.exists():
                            draft_files = ["请选择"] + [f.name for f in audio_dir.iterdir() if f.suffix.lower() == ".mp3"]
                        else:
                            draft_files = ["请选择", "未找到音频文件"]
                        return gr.update(choices=draft_files, value="请选择")
                    else:
                        return []
                generate_tts_btn.click(
                    fn=generate_tts,
                    inputs=[title_input, wenan_input, confirm_poetry, reference_audio_dropdown],
                    outputs=[tts_dropdown]
                )

                tts_player = gr.Audio(label="TTS试听", type="filepath")
                def regenerate_tts(choice, title, wenan, poetry, reference_audio_choice):
                    if choice == "请选择" or choice == "未找到音频文件":
                        return None
                    
                    # 获取参考音频文件路径
                    reference_audio_path = "material/reference_audio/风吟.wav"  # 默认值
                    if reference_audio_choice != "请选择" and reference_audio_choice != "未找到参考音频文件":
                        reference_audio_path = f"material/reference_audio/{reference_audio_choice}"
                    
                    draft_dir = os.getenv("DRAFT_DIR") or ""
                    audio_dir = Path(draft_dir + title + "/Resources/audioAlg/")
                    if(choice.startswith("wenan_")):
                        id = int(choice.replace("wenan_", "").replace(".mp3", ""))
                        if wenan and len(wenan.split("，")) > id:
                            asyncio.run(ag.generate_text(text=wenan.split("，")[id], name=choice, out_dir=str(audio_dir), reference_audio=reference_audio_path))
                            return True
                    else:
                        try:
                            zuobiao = [int(x) for x in choice.replace(".mp3", "").split("_")]
                            if poetry:
                                for p in json.loads(poetry):
                                    print(p["id"])
                                    print(zuobiao[0])
                                    if(int(p["id"]) == int(zuobiao[0])):
                                        text = p["shangju"] if zuobiao[1] == 1 else p["xiaju"]
                                        print(text)
                                        print(choice)
                                        asyncio.run(ag.generate_text(text=text, name=choice, out_dir=str(audio_dir), reference_audio=reference_audio_path))
                                        break
                        except (ValueError, json.JSONDecodeError):
                            # 忽略格式错误的文件名
                            return None
                    
                    if audio_dir.exists():
                        draft_files = ["请选择"] + [f.name for f in audio_dir.iterdir() if f.suffix.lower() == ".mp3"]
                    else:
                        draft_files = ["请选择", "未找到音频文件"]
                    return gr.update(choices=draft_files, value="请选择")
                
                regenerate_tts_btn.click(
                    fn=regenerate_tts,
                    inputs=[tts_dropdown, title_input, wenan_input, confirm_poetry, reference_audio_dropdown],
                    outputs=[tts_dropdown]
                )
                
                def update_tts_audio(choice, title):
                    # 如果是"请选择"或错误提示信息，直接返回 None
                    if choice == "请选择" or choice == "未找到音频文件":
                        return None
                    # 构建实际的音频文件路径
                    tts_path = os.getenv("DRAFT_DIR") or ""
                    audio_path = f"{tts_path}/{title}/Resources/audioAlg/{choice}"
                    print(audio_path)
                    if os.path.exists(audio_path):
                        return audio_path
                    else:
                        return None
                tts_dropdown.change(
                    fn=update_tts_audio,
                    inputs=[tts_dropdown, title_input],
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
                tmp: tuple = (f"{potry['shangju']}{potry['xiaju']}", potry["id"])
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
        
        def generateDraft(title: str, confirm_poetry: str, bgm: str, bgv: str):
            act = autoCut(title=title, list=json.loads(confirm_poetry), bgm=bgm, bgv=bgv)
            return act.general_draft()
        gr.Button("Go").click(
            fn=generateDraft,
            inputs=[title_input, confirm_poetry, bg_audio_dropdown, bg_video_dropdown]
        )

    return demo

def copy_dir(from_path: str, to_path: str) -> str:
        if not os.path.isdir(from_path):
            raise FileNotFoundError(f'源目录不存在: {from_path}')
        # 创建目标目录
        os.makedirs(to_path, exist_ok=True)
        # 复制所有文件（包含子目录）
        for root, _, files in os.walk(from_path):
            # 计算目标路径
            relative_path = os.path.relpath(root, from_path)
            target_dir = os.path.join(to_path, relative_path)
            
            # 创建目标子目录
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制当前目录下的所有文件
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                shutil.copy2(src_file, dst_file)
        return "success"
if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=9001)



