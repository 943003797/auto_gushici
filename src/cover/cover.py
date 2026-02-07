import os
from PIL import Image, ImageDraw, ImageFont
from typing import Any, List, Optional, Tuple, Union


def get_chinese_font(size: int = 48) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    font_paths = [
        "material/fonts/SanJiPoMoTi-2.ttf"
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
    font_sizes: List[int],
    line_spacing: int = 20,
    custom_font_path: Optional[str] = None,
    positions: Optional[List[Tuple[int, int]]] = None,
    is_horizontal: bool = False
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

    while len(font_sizes) < len(valid_texts):
        font_sizes.append(48)

    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    img_width, img_height = image.size

    if positions is None:
        positions = []
        for i in range(len(valid_texts)):
            positions.append(((i + 1) * 200, img_height // 2))

    while len(positions) < len(valid_texts):
        positions.append((len(positions) * 200, img_height // 2))

    for col_idx, (text, color, font_size, pos) in enumerate(zip(valid_texts, valid_colors, font_sizes, positions)):
        if custom_font_path and os.path.exists(custom_font_path):
            font = ImageFont.truetype(custom_font_path, font_size)
        else:
            font = get_chinese_font(font_size)

        chars = list(text)

        bbox = draw.textbbox((0, 0), "字", font=font)
        char_height = bbox[3] - bbox[1]

        start_x, start_y = pos

        if is_horizontal:
            total_width = len(chars) * font_size + (len(chars) - 1) * line_spacing
            start_x_adjusted = start_x - total_width

            for char_idx, char in enumerate(chars):
                bbox = draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]

                x = start_x_adjusted + char_idx * (font_size + line_spacing)
                y = start_y - char_height // 2

                rgb_color = hex_to_rgb(color)
                draw.text((x, y), char, font=font, fill=rgb_color)
        else:
            for char_idx, char in enumerate(chars):
                bbox = draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]

                x = start_x - char_width
                y = start_y + char_idx * (char_height + line_spacing)

                rgb_color = hex_to_rgb(color)
                draw.text((x, y), char, font=font, fill=rgb_color)

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
