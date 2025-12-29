import gradio as gr
from pathlib import Path
import cover


def get_templates_list():
    templates = cover.get_cover_templates()
    if not templates:
        return ["请先将封面模板添加到 material/baseCover 目录"]
    return templates


def update_preview(template_name):
    if not template_name or template_name.startswith("请先"):
        return None

    template_path = cover.get_template_path(template_name)
    if Path(template_path).exists():
        return template_path
    return None


def generate_cover(
    template_name,
    text1, color1,
    text2, color2,
    text3, color3,
    text4, color4,
    font_size,
    line_spacing
):
    if not template_name or template_name.startswith("请先"):
        return None, "请先选择封面模板"

    template_path = cover.get_template_path(template_name)
    if not Path(template_path).exists():
        return None, f"模板文件不存在: {template_path}"

    texts = [text1, text2, text3, text4]
    colors = [color1, color2, color3, color4]

    valid_texts = [t.strip() for t in texts if t and t.strip()]
    if not valid_texts:
        return None, "请至少输入一行文字内容"

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"catch/cover/generated_cover_{timestamp}.png"

    try:
        cover.add_text_to_cover(
            template_path=template_path,
            output_path=output_path,
            texts=texts,
            colors=colors,
            font_size=font_size,
            line_spacing=line_spacing
        )
        return output_path, f"生成成功！文件已保存至: {output_path}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"生成失败: {str(e)}"


def create_ui():
    with gr.Blocks(title="封面文字生成器") as demo:
        gr.Markdown("# 封面文字生成器")

        templates = get_templates_list()
        initial_preview = None
        if templates and not templates[0].startswith("请先"):
            initial_preview = update_preview(templates[0])

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 封面模板选择")

                template_dropdown = gr.Dropdown(
                    choices=templates,
                    label="选择封面模板",
                    value=templates[0] if templates else None
                )

                template_preview = gr.Image(
                    label="模板预览",
                    type="filepath",
                    interactive=False,
                    value=initial_preview
                )

                def on_template_change(template_name):
                    preview_path = update_preview(template_name)
                    return gr.update(value=preview_path)

                template_dropdown.change(
                    fn=on_template_change,
                    inputs=template_dropdown,
                    outputs=template_preview
                )

            with gr.Column(scale=1):
                gr.Markdown("## 文字内容")

                text1 = gr.Textbox(
                    label="第一行文字",
                    placeholder="请输入第一行文字...",
                    lines=1
                )
                color1 = gr.ColorPicker(
                    label="第一行文字颜色",
                    value="#FFFFFF"
                )

                text2 = gr.Textbox(
                    label="第二行文字",
                    placeholder="请输入第二行文字...",
                    lines=1
                )
                color2 = gr.ColorPicker(
                    label="第二行文字颜色",
                    value="#FFFFFF"
                )

                text3 = gr.Textbox(
                    label="第三行文字",
                    placeholder="请输入第三行文字...",
                    lines=1
                )
                color3 = gr.ColorPicker(
                    label="第三行文字颜色",
                    value="#FFFFFF"
                )

                text4 = gr.Textbox(
                    label="第四行文字",
                    placeholder="请输入第四行文字...",
                    lines=1
                )
                color4 = gr.ColorPicker(
                    label="第四行文字颜色",
                    value="#FFFFFF"
                )

                font_size_slider = gr.Slider(
                    minimum=24,
                    maximum=120,
                    value=48,
                    step=4,
                    label="字体大小"
                )

                line_spacing_slider = gr.Slider(
                    minimum=10,
                    maximum=60,
                    value=20,
                    step=2,
                    label="行距"
                )

                generate_btn = gr.Button("生成封面", variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("## 生成结果")

                result_image = gr.Image(
                    label="生成的封面",
                    type="filepath",
                    interactive=False
                )

                status_message = gr.Textbox(
                    label="状态信息",
                    interactive=False,
                    lines=2
                )

                generate_btn.click(
                    fn=generate_cover,
                    inputs=[
                        template_dropdown,
                        text1, color1,
                        text2, color2,
                        text3, color3,
                        text4, color4,
                        font_size_slider,
                        line_spacing_slider
                    ],
                    outputs=[result_image, status_message]
                )

    return demo


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=9002)
