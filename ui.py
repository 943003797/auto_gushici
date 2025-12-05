import gradio as gr
import agent as ag
import os
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
                
                # Poetry list
                poetry_list = gr.CheckboxGroup(label="Poetry list", choices=[], interactive=True)

                # Confirm poetry button
                confirm_copy_btn = gr.Button("确认文案")

            # Right box
            with gr.Column(scale=1):
                gr.Markdown("## 视频生成")
                
                confirm_poetry_list = gr.CheckboxGroup(label="Confirm poetry", choices=[], interactive=True)
                

        def update_poetry_list(title: str):
            new_choices = asyncio.run(ag.general_poetry(title))
            checkList = []
            for potry in new_choices:
                tmp: tuple = (potry["shiju"], potry["id"])
                checkList.append(tmp)
            return gr.update(choices=checkList)
        
        generate_poetry_btn.click(
            fn=update_poetry_list,
            inputs=[title_input],
            outputs=[poetry_list]
        )

        def update_confirm_poetry_list(poetry_list: list, confirm_poetry_list: list):
            # 将已勾选的诗词追加到右侧确认列表，并去重保持顺序
            merged = confirm_poetry_list.copy()
            for p in poetry_list:
                    merged.append(p)
            return gr.update(choices=merged)
        
        confirm_copy_btn.click(
            fn=update_confirm_poetry_list,
            inputs=[poetry_list, confirm_poetry_list],
            outputs=[confirm_poetry_list]
        )

        
    return demo

if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=9001)



