import gradio as gr
from pathlib import Path
import src.cover.cover as cover


def get_templates_list():
    templates = cover.get_cover_templates()
    if not templates:
        return ["请先将封面模板添加到 material/baseCover 目录"]
    return templates


def get_fonts_list():
    fonts_dir = Path("material/fonts")
    if not fonts_dir.exists():
        return ["请先将字体文件添加到 material/fonts 目录"]
    fonts = list(fonts_dir.glob("*.ttf"))
    if not fonts:
        return ["material/fonts 目录下未找到 ttf 字体文件"]
    return [f.stem for f in fonts]


def get_font_path(font_name):
    if not font_name or font_name.startswith("请先") or font_name.startswith("未找到"):
        return None
    font_path = Path(f"material/fonts/{font_name}.ttf")
    if font_path.exists():
        return str(font_path)
    return None


def update_preview(template_name):
    if not template_name or template_name.startswith("请先"):
        return None

    template_path = cover.get_template_path(template_name)
    if Path(template_path).exists():
        return template_path
    return None


def get_base_template(template_name):
    if template_name.startswith("请先"):
        return template_name
    if template_name.endswith("_heng.png"):
        return template_name.replace("_heng.png", ".png")
    elif "_heng." in template_name:
        base_name = template_name.rsplit("_heng", 1)[0]
        ext = template_name.rsplit(".", 1)[1] if "." in template_name else "png"
        return f"{base_name}.{ext}"
    return template_name


def get_oriented_templates(orient):
    base_templates = get_templates_list()
    if orient == "横版":
        oriented_templates = []
        for t in base_templates:
            if t.startswith("请先"):
                oriented_templates.append(t)
            else:
                base_name = t.rsplit('.', 1)[0]
                ext = t.rsplit('.', 1)[1] if '.' in t else 'png'
                heng_name = f"{base_name}_heng.{ext}"
                oriented_templates.append(heng_name)
        return oriented_templates
    return base_templates


def generate_cover_vertical(
    template_name,
    font_name,
    text1, color1, font_size1,
    text2, color2, font_size2,
    pos1_x, pos1_y,
    pos2_x, pos2_y,
    line_spacing
):
    if not template_name or template_name.startswith("请先"):
        return None, "请先选择封面模板"

    base_template_name = get_base_template(template_name)
    template_path = cover.get_template_path(base_template_name)
    if not Path(template_path).exists():
        return None, f"模板文件不存在: {template_path}"

    font_path = get_font_path(font_name)

    texts = [text1, text2]
    colors = [color1, color2]
    font_sizes = [font_size1, font_size2]
    positions = [(pos1_x, pos1_y), (pos2_x, pos2_y)]

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
            font_sizes=font_sizes,
            line_spacing=line_spacing,
            custom_font_path=font_path,
            positions=positions,
            is_horizontal=False
        )
        return output_path, f"生成成功！文件已保存至: {output_path}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"生成失败: {str(e)}"


def generate_cover_horizontal(
    template_name,
    font_name,
    text1, color1, font_size1,
    text2, color2, font_size2,
    pos1_x, pos1_y,
    pos2_x, pos2_y,
    line_spacing
):
    if not template_name or template_name.startswith("请先"):
        return None, "请先选择封面模板"

    base_template_name = get_base_template(template_name)
    template_path = cover.get_template_path(base_template_name)
    if not Path(template_path).exists():
        return None, f"模板文件不存在: {template_path}"

    font_path = get_font_path(font_name)

    texts = [text1, text2]
    colors = [color1, color2]
    font_sizes = [font_size1, font_size2]
    positions = [(pos1_x, pos1_y), (pos2_x, pos2_y)]

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
            font_sizes=font_sizes,
            line_spacing=line_spacing,
            custom_font_path=font_path,
            positions=positions,
            is_horizontal=True
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

                fonts = get_fonts_list()
                font_dropdown = gr.Dropdown(
                    choices=fonts,
                    label="选择字体",
                    value=fonts[0] if fonts else None
                )

                template_preview = gr.Image(
                    label="模板预览",
                    type="filepath",
                    interactive=False,
                    value=initial_preview
                )

        with gr.Tabs():
            with gr.Tab("竖版"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 竖版封面")

                        fonts = get_fonts_list()
                        font_dropdown = gr.Dropdown(
                            choices=fonts,
                            label="选择字体",
                            value=fonts[0] if fonts else None
                        )

                        v_templates = get_oriented_templates("竖版")
                        v_template_dropdown = gr.Dropdown(
                            choices=v_templates,
                            label="选择封面模板",
                            value=v_templates[0] if v_templates else None
                        )

                        v_template_preview = gr.Image(
                            label="模板预览",
                            type="filepath",
                            interactive=False,
                            value=initial_preview
                        )

                        def on_v_template_change(template_name):
                            base_name = get_base_template(template_name)
                            preview_path = update_preview(base_name)
                            return gr.update(value=preview_path)

                        v_template_dropdown.change(
                            fn=on_v_template_change,
                            inputs=v_template_dropdown,
                            outputs=v_template_preview
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("## 文字内容")

                        with gr.Row():
                            v_text1 = gr.Textbox(
                                label="主标题",
                                placeholder="请输入主标题...",
                                value="春江花月夜",
                                lines=1,
                                scale=3
                            )
                            v_color1 = gr.ColorPicker(
                                label="主标题文字颜色",
                                value="#0D131A",
                                scale=2
                            )

                        with gr.Row():
                            v_font_size1 = gr.Slider(
                                minimum=24,
                                maximum=240,
                                value=120,
                                step=4,
                                label="主标题字体大小"
                            )

                        with gr.Row():
                            v_pos1_x = gr.Slider(
                                minimum=0,
                                maximum=2000,
                                value=600,
                                step=10,
                                label="主标题X坐标"
                            )
                            v_pos1_y = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=300,
                                step=10,
                                label="主标题Y坐标"
                            )

                        with gr.Row():
                            v_text2 = gr.Textbox(
                                label="副标题",
                                placeholder="请输入副标题...",
                                value="虞美人",
                                lines=1,
                                scale=3
                            )
                            v_color2 = gr.ColorPicker(
                                label="副标题文字颜色",
                                value="#0D131A",
                                scale=2
                            )

                        with gr.Row():
                            v_font_size2 = gr.Slider(
                                minimum=24,
                                maximum=240,
                                value=64,
                                step=4,
                                label="副标题字体大小"
                            )

                        with gr.Row():
                            v_pos2_x = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=800,
                                step=10,
                                label="副标题X坐标"
                            )
                            v_pos2_y = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=360,
                                step=10,
                                label="副标题Y坐标"
                            )

                        v_line_spacing_slider = gr.Slider(
                            minimum=10,
                            maximum=60,
                            value=60,
                            step=2,
                            label="行距"
                        )

                        v_generate_btn = gr.Button("生成竖版封面", variant="primary")

                    with gr.Column(scale=3):
                        gr.Markdown("## 生成结果")

                        v_result_image = gr.Image(
                            label="生成的封面",
                            type="filepath",
                            interactive=False
                        )

                        v_status_message = gr.Textbox(
                            label="状态信息",
                            interactive=False,
                            lines=2
                        )

                        v_generate_btn.click(
                            fn=generate_cover_vertical,
                            inputs=[
                                v_template_dropdown,
                                font_dropdown,
                                v_text1, v_color1, v_font_size1,
                                v_text2, v_color2, v_font_size2,
                                v_pos1_x, v_pos1_y,
                                v_pos2_x, v_pos2_y,
                                v_line_spacing_slider
                            ],
                            outputs=[v_result_image, v_status_message]
                        )

            with gr.Tab("横版"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 横版封面")

                        fonts = get_fonts_list()
                        h_font_dropdown = gr.Dropdown(
                            choices=fonts,
                            label="选择字体",
                            value=fonts[0] if fonts else None
                        )

                        h_templates = get_oriented_templates("横版")
                        h_template_dropdown = gr.Dropdown(
                            choices=h_templates,
                            label="选择封面模板",
                            value=h_templates[0] if h_templates else None
                        )

                        h_template_preview = gr.Image(
                            label="模板预览",
                            type="filepath",
                            interactive=False,
                            value=initial_preview
                        )

                        def on_h_template_change(template_name):
                            base_name = get_base_template(template_name)
                            preview_path = update_preview(base_name)
                            return gr.update(value=preview_path)

                        h_template_dropdown.change(
                            fn=on_h_template_change,
                            inputs=h_template_dropdown,
                            outputs=h_template_preview
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("## 文字内容")

                        with gr.Row():
                            h_text1 = gr.Textbox(
                                label="主标题",
                                placeholder="请输入主标题...",
                                value="春江花月夜",
                                lines=1,
                                scale=3
                            )
                            h_color1 = gr.ColorPicker(
                                label="主标题文字颜色",
                                value="#0D131A",
                                scale=2
                            )

                        with gr.Row():
                            h_font_size1 = gr.Slider(
                                minimum=24,
                                maximum=240,
                                value=120,
                                step=4,
                                label="主标题字体大小"
                            )

                        with gr.Row():
                            h_pos1_x = gr.Slider(
                                minimum=0,
                                maximum=2000,
                                value=1120,
                                step=10,
                                label="主标题X坐标"
                            )
                            h_pos1_y = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=430,
                                step=10,
                                label="主标题Y坐标"
                            )

                        with gr.Row():
                            h_text2 = gr.Textbox(
                                label="副标题",
                                placeholder="请输入副标题...",
                                value="虞美人",
                                lines=1,
                                scale=3
                            )
                            h_color2 = gr.ColorPicker(
                                label="副标题文字颜色",
                                value="#0D131A",
                                scale=2
                            )

                        with gr.Row():
                            h_font_size2 = gr.Slider(
                                minimum=24,
                                maximum=240,
                                value=64,
                                step=4,
                                label="副标题字体大小"
                            )

                        with gr.Row():
                            h_pos2_x = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=920,
                                step=10,
                                label="副标题X坐标"
                            )
                            h_pos2_y = gr.Slider(
                                minimum=0,
                                maximum=1000,
                                value=630,
                                step=10,
                                label="副标题Y坐标"
                            )

                        h_line_spacing_slider = gr.Slider(
                            minimum=10,
                            maximum=60,
                            value=60,
                            step=2,
                            label="行距"
                        )

                        h_generate_btn = gr.Button("生成横版封面", variant="primary")

                    with gr.Column(scale=3):
                        gr.Markdown("## 生成结果")

                        h_result_image = gr.Image(
                            label="生成的封面",
                            type="filepath",
                            interactive=False
                        )

                        h_status_message = gr.Textbox(
                            label="状态信息",
                            interactive=False,
                            lines=2
                        )

                        h_generate_btn.click(
                            fn=generate_cover_horizontal,
                            inputs=[
                                h_template_dropdown,
                                h_font_dropdown,
                                h_text1, h_color1, h_font_size1,
                                h_text2, h_color2, h_font_size2,
                                h_pos1_x, h_pos1_y,
                                h_pos2_x, h_pos2_y,
                                h_line_spacing_slider
                            ],
                            outputs=[h_result_image, h_status_message]
                        )

    return demo


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=9002)
