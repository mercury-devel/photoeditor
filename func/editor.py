from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
from sys import platform
import numpy as np
import random
import os


async def liquid_rescale(pic):
    c = random.choice([True, False])
    if c:
        p1 = '%'
        p2 = ''
    else:
        p1 = ''
        p2 = '%'
    s1 = random.randint(25, 100)
    s2 = random.randint(25, 100)
    if platform == "linux" or platform == "linux2":
        c = "convert"
    else:
        c = "magick"
    os.system(f'{c} {pic} -alpha set -liquid-rescale {s1}{p1}x{s2}{p2} {pic}')

async def bad_quality(pic):
    img = Image.open(pic)
    img.save(pic, quality=random.randint(1, 10))

async def make_sketch(pic):
    img = Image.open(pic)
    img = img.filter(ImageFilter.CONTOUR)
    img.save(pic)

async def make_moire(pic):
    img = Image.open(pic)
    new_image = img
    width, height = new_image.size
    moire_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(moire_image)
    line_spacing = 2
    for i in range(height):
        x = i * line_spacing
        draw.line([(x, 0), (x, height)], fill=(0, 0, 0))
    rotated = moire_image.rotate(90, expand=True)
    rotated = rotated.resize((width, height))
    new_image.paste(moire_image, (0, 0), moire_image)
    new_image.paste(rotated, (0, 0), rotated)
    new_image.save(pic)

async def make_noise(pic):
    image = Image.open(pic)
    mean = 0
    stddev = 100
    noise_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    image_array = np.array(noise_layer)
    noise1 = np.random.normal(mean, stddev, image_array.shape).astype(np.uint8)
    noise_layer = image_array + noise1
    noise_layer = np.clip(noise_layer, 0, 255).astype(np.uint8)
    noise_layer = Image.fromarray(noise_layer)
    noise_layer.putalpha(15)
    image.paste(noise_layer, (0, 0), noise_layer)
    image.save(pic)

async def make_bright(pic):
    image = Image.open(pic)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(random.choice([0.7, 1.3]))
    image.save(pic)

async def make_sat(pic):
    image = Image.open(pic)
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(random.choice([0.7, 1.3]))
    image.save(pic)

async def draw_text_with_outline(image, text, font, text_color, outline_color, outline_width, x, y):
    draw = ImageDraw.Draw(image)
    for i in range(1, outline_width + 1):
        for offset in [(-i, -i), (-i, i), (i, -i), (i, i)]:
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

async def print_text(font_type, text, draw, font, image, width, height, up_text):
    _, _, text_width, text_height = draw.textbbox((0, 0), text, font)
    x = (width - text_width) / 2
    if up_text:
        y = 20
    else:
        y = height-text_height-20
    if font_type == "goth":
        await draw_text_with_outline(image, text, font, "black", "black", 2, x, y)
        await draw_text_with_outline(image, text, font, "black", "white", 1, x, y)
    if font_type == "impact":
        await draw_text_with_outline(image, text, font, "white", "black", 3, x, y)

async def add_text_to_photo(font_type, up_text, down_text, pic):
    image = Image.open(pic)
    draw = ImageDraw.Draw(image)
    width, height = image.size
    font_size = min(width, height) // 10
    if font_type == "goth":
        font_path = "fonts/goth.otf"
    elif font_type == "impact":
        font_path = "fonts/impact.ttf"
    font = ImageFont.truetype(font_path, font_size)
    if up_text:
        await print_text(font_type, up_text, draw, font, image, width, height, True)
    if down_text:
        await print_text(font_type, down_text, draw, font, image, width, height, False)
    image.save(pic)
