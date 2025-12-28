import os
from PIL import Image, ImageDraw, ImageFont
from typing import Any, List, Optional, Tuple, Union


def get_chinese_font(size: int = 48) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    font_paths = [
        "material/fonts/xingshu.ttf"
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, size)
            return font

    return ImageFont.load_default()


def hex_to_rgb(color: str) -> Tuple[int, int, int]:
    if not color:
        return (255, 255, 255)

    color_str = str(color).strip()

    if color_str.startswith("rgba("):
        color_str = color_str[5:-1]
        parts = [p.strip() for p in color_str.split(",")]
        if len(parts) >= 3:
            try:
                r = int(float(parts[0]))
                g = int(float(parts[1]))
                b = int(float(parts[2]))
                return (r, g, b)
            except (ValueError, IndexError):
                pass

    if color_str.startswith("rgb("):
        color_str = color_str[4:-1]
        parts = [p.strip() for p in color_str.split(",")]
        if len(parts) >= 3:
            try:
                r = int(float(parts[0]))
                g = int(float(parts[1]))
                b = int(float(parts[2]))
                return (r, g, b)
            except (ValueError, IndexError):
                pass

    if not color_str.startswith("#"):
        color_str = "#" + color_str

    color_str = color_str.lstrip("#")
    color_len = len(color_str)

    if color_len == 6:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        return (r, g, b)
    elif color_len == 8:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        return (r, g, b)
    elif color_len == 3:
        r = int(color_str[0:1], 16) * 17
        g = int(color_str[1:2], 16) * 17
        b = int(color_str[2:3], 16) * 17
        return (r, g, b)

    return (255, 255, 255)


def add_text_to_cover(
    template_path: str,
    output_path: str,
    texts: List[str],
    colors: List[str],
    font_size: int = 48,
    line_spacing: int = 20,
    custom_font_path: Optional[str] = None
) -> bool:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    valid_texts = [t.strip() for t in texts if t and t.strip()]
    if not valid_texts:
        raise ValueError("至少需要输入一行文字内容")

    valid_colors = []
    for i, color in enumerate(colors):
        if color:
            valid_colors.append(color)
        elif i < len(valid_texts):
            valid_colors.append("#FFFFFF")
        else:
            valid_colors.append("#FFFFFF")

    while len(valid_colors) < len(valid_texts):
        valid_colors.append("#FFFFFF")

    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    if custom_font_path and os.path.exists(custom_font_path):
        font = ImageFont.truetype(custom_font_path, font_size)
    else:
        font = get_chinese_font(font_size)

    img_width, img_height = image.size

    text_positions = []
    current_y = 0

    for text in valid_texts:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (img_width - text_width) // 2
        text_positions.append((x, text_height))
        current_y += text_height + line_spacing

    total_text_height = current_y - line_spacing
    start_y = (img_height - total_text_height) // 2

    current_y = start_y
    for i, (text, color) in enumerate(zip(valid_texts, valid_colors)):
        text_height = text_positions[i][1]
        x = text_positions[i][0]
        y = current_y

        rgb_color = hex_to_rgb(color)
        draw.text((x, y), text, font=font, fill=rgb_color)

        current_y += text_height + line_spacing

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_image = image.convert("RGB")
    output_image.save(output_path, "PNG")

    return True


def get_cover_templates() -> List[str]:
    template_dir = "material/baseCover"
    if not os.path.exists(template_dir):
        return []

    templates = []
    for f in os.listdir(template_dir):
        if f.lower().endswith('.png') and os.path.isfile(os.path.join(template_dir, f)):
            templates.append(f)

    return sorted(templates)


def get_template_path(template_name: str) -> str:
    return os.path.join("material/baseCover", template_name)
