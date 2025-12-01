import gradio as gr

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
                bg_audio_dropdown = gr.Dropdown(
                    choices=["古筝音乐", "笛子音乐", "琵琶音乐", "自然音效"],
                    label="背景音频",
                    value="古筝音乐"
                )
                audio_player = gr.Audio(label="背景音频试听", type="filepath")
                
                # 背景视频选择
                bg_video_dropdown = gr.Dropdown(
                    choices=["山水画风格", "书法展示", "古风动画", "实景拍摄"],
                    label="背景视频",
                    value="山水画风格"
                )
                video_preview = gr.Video(label="背景视频预览")
                
                generate_video_btn = gr.Button("生成短视频")
        
        # 功能绑定
        def generate_copy(theme):
            # 这里应该调用实际的文案生成逻辑
            sample_copies = {
                "春天": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
                "夏天": "泉眼无声惜细流，树阴照水爱晴柔。小荷才露尖尖角，早有蜻蜓立上头。",
                "秋天": "远上寒山石径斜，白云深处有人家。停车坐爱枫林晚，霜叶红于二月花。",
                "冬天": "千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。",
                "离别": "多情自古伤离别，更那堪冷落清秋节。今宵酒醒何处？杨柳岸晓风残月。",
                "思念": "红豆生南国，春来发几枝。愿君多采撷，此物最相思。"
            }
            return sample_copies.get(theme, f"这里是关于'{theme}'的古诗词文案示例...")
        
        def confirm_copy(theme, copy_text):
            return theme, copy_text
        
        def update_audio(choice):
            # 模拟音频文件路径
            audio_map = {
                "古筝音乐": "https://example.com/guzheng.mp3",
                "笛子音乐": "https://example.com/dizi.mp3",
                "琵琶音乐": "https://example.com/pipa.mp3",
                "自然音效": "https://example.com/nature.mp3"
            }
            return audio_map.get(choice, None)
        
        def update_video(choice):
            # 模拟视频文件路径
            video_map = {
                "山水画风格": "https://example.com/shanshui.mp4",
                "书法展示": "https://example.com/shufa.mp4",
                "古风动画": "https://example.com/gufeng.mp4",
                "实景拍摄": "https://example.com/shijing.mp4"
            }
            return video_map.get(choice, None)
        
        # 绑定事件
        generate_copy_btn.click(
            fn=generate_copy,
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

