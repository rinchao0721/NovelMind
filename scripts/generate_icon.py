import os
from PIL import Image, ImageDraw, ImageFont


def generate_icons():
    # Configuration
    size = 1024
    bg_color = "#409EFF"  # Element Plus primary blue
    text_color = "#FFFFFF"
    text = "N"

    # Ensure directories exist
    # paths are relative to where the script is run, or we make them absolute based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    res_dir = os.path.join(project_root, "resources", "icons")
    public_dir = os.path.join(project_root, "public")

    os.makedirs(res_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    # Create base image (Transparent)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle (or circle)
    draw.ellipse([50, 50, size - 50, size - 50], fill=bg_color)

    # Draw Text
    # Try to load a font, fallback to default
    try:
        # Windows path to Arial
        font = ImageFont.truetype("arial.ttf", 600)
    except:
        try:
            # Linux path
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 600
            )
        except:
            print("Warning: Could not load custom font, using default.")
            # Default font is very small, so we might need a better fallback if possible,
            # but for now rely on Arial being present on Windows or standard paths.
            font = ImageFont.load_default()

    # Calculate text position to center it
    try:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
    except AttributeError:
        # Fallback for older Pillow versions
        text_width, text_height = draw.textsize(text, font=font)

    x = (size - text_width) / 2
    y = (size - text_height) / 2 - (text_height * 0.1)  # slightly adjust up

    draw.text((x, y), text, fill=text_color, font=font)

    # Save PNG
    png_path = os.path.join(res_dir, "icon.png")
    img.save(png_path, "PNG")
    print(f"Generated {png_path}")

    # Save ICO (Standard sizes)
    ico_path = os.path.join(res_dir, "icon.ico")
    # Resize for ICO to avoid issues with large sizes in some viewers
    img_ico = img.resize((256, 256), Image.Resampling.LANCZOS)
    img_ico.save(
        ico_path, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    )
    print(f"Generated {ico_path}")

    # Generate SVG for favicon
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
  <circle cx="{size / 2}" cy="{size / 2}" r="{size / 2 - 50}" fill="{bg_color}"/>
  <text x="50%" y="65%" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="600" font-weight="bold">{text}</text>
</svg>'''

    svg_path = os.path.join(public_dir, "favicon.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {svg_path}")


if __name__ == "__main__":
    generate_icons()
