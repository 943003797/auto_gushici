#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import gradio as gr

def create_interface():
    """
    创建短视频D1的Gradio界面
    """
    with gr.Blocks(title="短视频D1") as demo:
        gr.Markdown("# 短视频D1")
        gr.Markdown("欢迎使用短视频D1处理工具")
        
        # 示例输入输出组件
        with gr.Row():
            input_text = gr.Textbox(label="输入文本", placeholder="请输入要处理的文本...")
            output_text = gr.Textbox(label="处理结果")
        
        # 示例按钮
        process_btn = gr.Button("处理")
        
        # 示例函数
        def process_text(text):
            return f"处理结果：{text}"
        
        process_btn.click(
            fn=process_text,
            inputs=input_text,
            outputs=output_text
        )
    
    return demo

if __name__ == "__main__":
    print("正在启动短视频D1 Gradio界面...")
    demo = create_interface()
    print("Gradio界面创建成功，正在启动服务器...")
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)