from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "data" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

products = {
    "paint1": ("paint", "#D8C6A5"),
    "paint2": ("paint", "#F1E8D7"),
    "paint3": ("paint", "#D5C7B8"),
    "floor1": ("flooring", "#B58B5A"),
    "floor2": ("flooring", "#8D6545"),
    "floor3": ("flooring", "#D1B28A"),
    "sofa1": ("sofa", "#8C9B83"),
    "sofa2": ("sofa", "#A6A6A0"),
    "sofa3": ("sofa", "#80645B"),
    "bed1": ("bed", "#B99B7B"),
    "bed2": ("bed", "#D3C0A8"),
    "bed3": ("bed", "#8A7770"),
    "table1": ("table", "#C69C6D"),
    "table2": ("table", "#A77C50"),
    "table3": ("table", "#75543B"),
    "light1": ("lighting", "#F5D76E"),
    "light2": ("lighting", "#D7C39A"),
    "light3": ("lighting", "#E8D8B0"),
    "table4": ("table", "#B58D62"),
    "light4": ("lighting", "#E4C879"),
}

def draw_product(name, category, color):
    image = Image.new("RGB", (384, 384), "#F4F0E8")
    draw = ImageDraw.Draw(image)

    # Floor and background
    draw.rectangle((0, 285, 384, 384), fill="#D8D0C4")

    if category == "sofa":
        draw.rectangle((80, 150, 304, 260), fill=color)
        draw.rectangle((65, 125, 115, 225), fill=color)
        draw.rectangle((269, 125, 319, 225), fill=color)
        draw.rectangle((95, 250, 110, 285), fill="#55483D")
        draw.rectangle((275, 250, 290, 285), fill="#55483D")

    elif category == "bed":
        draw.rectangle((65, 145, 320, 270), fill=color)
        draw.rectangle((65, 125, 320, 160), fill="#765C48")
        draw.rectangle((85, 155, 180, 205), fill="#F8F5EF")
        draw.rectangle((190, 155, 285, 205), fill="#E8DDD0")
        draw.rectangle((85, 265, 100, 290), fill="#765C48")
        draw.rectangle((285, 265, 300, 290), fill="#765C48")

    elif category == "table":
        draw.rectangle((90, 175, 294, 200), fill=color)
        draw.rectangle((105, 200, 120, 280), fill="#765C48")
        draw.rectangle((264, 200, 279, 280), fill="#765C48")

    elif category == "lighting":
        draw.rectangle((185, 175, 200, 280), fill="#6B6258")
        draw.ellipse((130, 105, 255, 195), fill=color)
        draw.ellipse((160, 125, 225, 175), fill="#FFF2BD")

    elif category == "flooring":
        for y in range(40, 290, 45):
            draw.rectangle((0, y, 384, y + 38), fill=color)
            draw.line((0, y, 384, y), fill="#E5D7C3", width=3)
        for x in range(40, 384, 100):
            draw.line((x, 40, x, 290), fill="#E5D7C3", width=2)

    elif category == "paint":
        draw.rectangle((55, 65, 329, 290), fill=color)
        draw.rectangle((55, 65, 329, 85), fill="#FFFFFF")
        draw.rectangle((55, 270, 329, 290), fill="#B7AA98")

    draw.text((12, 350), f"{category.title()} - {name}", fill="#282521")

    image.save(IMAGE_DIR / f"{name}.jpg", quality=92)

for name, (category, color) in products.items():
    draw_product(name, category, color)

print(f"Created {len(products)} sample images in {IMAGE_DIR}")