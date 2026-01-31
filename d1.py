import gradio as gr
import os
from src.agents.agent_d1 import process_complete_workflow

def voice_generation_function(topic_input, title_input, content_textarea):
    """
    配音生成功能
    """
    try:
        if not content_textarea.strip():
            return None
        
        # 调用配音工作流
        result = process_complete_workflow(
            title=title_input,
            wenan=content_textarea,
            topic_name=topic_input
        )
        
        if result.get("status") == "success":
            # 获取生成的音频文件路径
            draft_dir = os.getenv("DRAFT_DIR") or "draft"
            audio_path = f"{draft_dir}/{topic_input}/Resources/audioAlg/wenan.mp3"
            print(audio_path)
            
            if os.path.exists(audio_path):
                return audio_path
            else:
                return None
        else:
            return None
            
    except Exception as e:
        print(f"配音生成出错: {str(e)}")
        return None

def create_interface():
    """
    创建短视频D1的Gradio界面
    """
    with gr.Blocks(title="短视频D1") as demo:
        gr.Markdown("# 短视频D1")
        gr.Markdown("欢迎使用短视频D1处理工具")
        
        # topic输入框
        topic_input = gr.Textbox(label="📝 topic", placeholder="请输入topic...")

         # 标题输入框
        title_input = gr.Textbox(label="📝 文案标题", placeholder="请输入文案标题...")
        
        # 文案文本区域
        content_textarea = gr.Textbox(label="✍️ 文案", placeholder="请输入文案内容...", lines=20)
        
        # 配音按钮
        voice_btn = gr.Button("🔊 配音")
        
        # 音频预览播放器
        audio_player = gr.Audio(label="🎵 音频预览")
        
        # 生成视频按钮
        generate_btn = gr.Button("🎬 生成视频")
        
        # 绑定配音按钮事件
        voice_btn.click(
            fn=voice_generation_function,
            inputs=[topic_input, title_input, content_textarea],
            outputs=[audio_player]
        )
        

    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=1001, show_error=True)