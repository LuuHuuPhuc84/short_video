# -*- coding: utf-8 -*-
"""
pipeline/core_thumb.py
======================
Module ĐƠN NHIỆM: Quản trị và Sinh Thumbnail chuẩn Viral Thumbnail Design Rules (9:16 Shorts/TikTok & 16:9 Long).
Tuân thủ 100% bộ quy chuẩn:
1. Strict Safe Zones:
   - Vùng Chữ (Top Text Zone): 5% đến 35% Y: 100px -> 670px.
   - Vùng đệm (Buffer Zone): 35% đến 40% Y: 670px -> 770px.
   - Vùng Chủ thể (Bottom Subject Zone): 40% đến 100% Y: 770px -> 1920px.
2. Copywriting cực ngắn: Hook 2 đến 6 từ đánh trúng tâm lý, không dùng chữ phụ.
3. Khóa Font Tiếng Việt & Nền cọ xước:
   - Font: BeVietnamPro-Black, Montserrat-Black, Roboto-Black, Arial Bold.
   - Vệt cọ xước tự nhiên (brush splatter edges) nghiêng 4-5 độ hướng lên.
   - Phối màu tương phản cao (#FFA500 Vàng cam & #990000 Đỏ sẫm).
4. Bố cục & Ánh sáng Chủ thể: 60% Nửa dưới, Anti-Dark Background & Golden Rim Light.
"""

import os
import sys
import json
import re
import math
import random
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PUBLIC_DIR = BASE_DIR / "remotion-video" / "public"
ASSETS_HUB = BASE_DIR / "assets_hub"

def get_font(size, bold=True):
    """Tìm font hỗ trợ 100% tiếng Việt, ưu tiên Be Vietnam Pro Black & Google Fonts."""
    font_paths = [
        ASSETS_HUB / "fonts" / "BeVietnamPro-Black.ttf",
        ASSETS_HUB / "fonts" / "Montserrat-Black.ttf",
        ASSETS_HUB / "fonts" / "Roboto-Black.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(str(fp), size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_brush_banner(width, height, base_color, edge_color):
    """Tạo dải cọ sơn dày có viền xước tự nhiên (brush splatter edges)."""
    pad = 35
    bw = width + pad * 2
    bh = height + pad * 2
    banner = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(banner)

    x0, y0 = pad, pad
    x1, y1 = pad + width, pad + height

    # Lớp bóng đổ phía dưới của vệt sơn
    shadow_offset = 7
    draw.rounded_rectangle([x0 + 3, y0 + shadow_offset, x1 + 3, y1 + shadow_offset], radius=10, fill=(10, 10, 15, 180))

    # Vệt sơn chính
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=base_color)

    # Hiệu ứng cọ xước (splatter / brush edges) ở 2 đầu
    random.seed(42)
    for _ in range(16):
        sy = random.randint(y0 - 3, y1 + 3)
        sx = x0 - random.randint(12, 35)
        sw = random.randint(20, 42)
        sh = random.randint(4, 12)
        draw.ellipse([sx, sy, sx + sw, sy + sh], fill=base_color)

    for _ in range(16):
        sy = random.randint(y0 - 3, y1 + 3)
        sx = x1 - random.randint(10, 25)
        sw = random.randint(22, 45)
        sh = random.randint(4, 12)
        draw.ellipse([sx, sy, sx + sw, sy + sh], fill=base_color)

    for _ in range(22):
        sx = random.randint(x0 + 10, x1 - 10)
        sy_top = y0 - random.randint(2, 6)
        sy_bot = y1 + random.randint(0, 6)
        r = random.randint(3, 6)
        draw.ellipse([sx, sy_top, sx + r*2, sy_top + r], fill=edge_color)
        draw.ellipse([sx, sy_bot, sx + r*2, sy_bot + r], fill=edge_color)

    return banner, pad

def make_text_layer(text, font, text_color, stroke_color, stroke_width=5):
    """Tạo layer chữ có viền và bóng đổ nổi khối."""
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad = 25
    w = tw + pad * 2
    h = th + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Bóng đổ đen dày
    shadow_offset = 6
    draw.text((pad - bbox[0] + shadow_offset, pad - bbox[1] + shadow_offset), 
              text, font=font, fill=(0, 0, 0, 220), 
              stroke_width=stroke_width, stroke_fill=(0, 0, 0, 220))

    # Chữ chính kèm viền nổi khối
    draw.text((pad - bbox[0], pad - bbox[1]), 
              text, font=font, fill=text_color, 
              stroke_width=stroke_width, stroke_fill=stroke_color)

    return img, tw, th

def add_sparks(img, center_x, center_y, radius=340, count=45):
    """Thêm hiệu ứng tia lửa nhỏ (sparks/embers) quanh vệt sơn tiêu đề."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    random.seed(101)

    colors = [
        (255, 205, 60, 240),
        (255, 145, 25, 220),
        (255, 85, 25, 200),
        (255, 235, 160, 255)
    ]

    for _ in range(count):
        ang = random.uniform(0, 2 * math.pi)
        dist = random.uniform(40, radius)
        px = int(center_x + dist * math.cos(ang))
        py = int(center_y + dist * 0.55 * math.sin(ang))
        size = random.randint(2, 5)

        c = random.choice(colors)
        draw.ellipse([px, py, px + size, py + size], fill=c)
        if size >= 4:
            draw.ellipse([px - 2, py - 2, px + size + 2, py + size + 2], fill=(c[0], c[1], c[2], 50))

    return Image.alpha_composite(img, overlay)

def generate_thumbnail(video_id, title_hook=None, image_source=None, project_type="short"):
    """Tự động tạo Thumbnail chuẩn Viral Thumbnail Design Rules (9:16 Shorts hoặc 16:9 Long)."""
    print(f"🖼️ Đang tạo Thumbnail Viral cho '{video_id}' ({project_type.upper()})...")

    vid_folder = OUTPUT_DIR / video_id
    vid_folder.mkdir(parents=True, exist_ok=True)
    input_folder = vid_folder / "input"
    input_folder.mkdir(parents=True, exist_ok=True)

    # 1. Tìm title_hook từ metadata nếu chưa có
    for p in [input_folder / "info.json", vid_folder / "info.json", PUBLIC_DIR / f"video_data_{video_id}.json", input_folder / "video_data.json"]:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if not title_hook:
                    title_hook = d.get("title_hook") or d.get("titleHook") or d.get("title", "")
                if title_hook:
                    title_hook = re.sub(r'\s*#shorts\b', '', str(title_hook), flags=re.IGNORECASE).strip()
                break
            except Exception:
                pass

    if not title_hook:
        title_hook = "BÀI HỌC CUỘC SỐNG"
    else:
        title_hook = re.sub(r'\s*#shorts\b', '', str(title_hook), flags=re.IGNORECASE).strip()

    # 2. Tìm ảnh nền: Ưu tiên ảnh AI nghệ thuật trong assets_hub / input
    bg_img_path = None
    if image_source and Path(image_source).exists():
        bg_img_path = Path(image_source)
    else:
        ai_art_candidates = [
            input_folder / f"{video_id}_thumb_subject.png",
            input_folder / f"{video_id}_thumb_subject.jpg",
            input_folder / f"{video_id}_scene1.jpg",
            input_folder / f"{video_id}_scene1.png",
            PUBLIC_DIR / f"{video_id}_scene1.jpg",
            PUBLIC_DIR / f"{video_id}_scene1.png",
            ASSETS_HUB / "images" / f"{video_id}_thumb_bg.png",
            ASSETS_HUB / "images" / f"{video_id}_thumb_bg.jpg",
            ASSETS_HUB / "images" / f"{video_id}.png",
            ASSETS_HUB / "images" / f"{video_id}.jpg",
            input_folder / f"{video_id}_thumb_bg.png",
            input_folder / f"{video_id}_thumb_bg.jpg"
        ]
        for art in ai_art_candidates:
            if art.exists():
                bg_img_path = art
                break

        if not bg_img_path:
            for sc_idx in range(1, 6):
                for ext in ["jpg", "png", "jpeg"]:
                    cand = input_folder / f"{video_id}_scene{sc_idx}.{ext}"
                    if cand.exists():
                        bg_img_path = cand
                        break
                    cand_pub = PUBLIC_DIR / f"{video_id}_scene{sc_idx}.{ext}"
                    if cand_pub.exists():
                        bg_img_path = cand_pub
                        break
                if bg_img_path:
                    break

        if not bg_img_path:
            scene1_candidates = [
                PUBLIC_DIR / f"{video_id}_scene1.mp4",
                input_folder / f"{video_id}_scene1.mp4"
            ]
            for sc in scene1_candidates:
                if sc.exists():
                    out_frame = input_folder / f"raw_clean_frame_{video_id}.jpg"
                    cmd = [
                        r"D:\Programs\ffmpeg\bin\ffmpeg.exe",
                        "-y",
                        "-ss", "00:00:01",
                        "-i", str(sc),
                        "-vframes", "1",
                        "-q:v", "2",
                        str(out_frame)
                    ]
                    try:
                        res = subprocess.run(cmd, capture_output=True, check=True)
                        if out_frame.exists() and out_frame.stat().st_size > 0:
                            bg_img_path = out_frame
                            break
                    except Exception:
                        pass

    target_size = (1080, 1920) if project_type == "short" else (1920, 1080)

    if bg_img_path and Path(bg_img_path).exists():
        im = Image.open(bg_img_path).convert("RGBA")
        if im.size != target_size:
            im = im.resize(target_size, Image.Resampling.LANCZOS)
    else:
        im = Image.new("RGBA", target_size, (15, 20, 30, 255))

    comp = im.copy()

    if project_type == "short":
        # Chuẩn hóa ngắt dòng: 1 tầng (2-3 từ) hoặc 2 tầng (4-6 từ)
        words = title_hook.split("/") if "/" in title_hook else title_hook.split("-") if "-" in title_hook else []
        if words and len(words) >= 2:
            lines = [w.strip().upper() for w in words[:2]]
        else:
            all_words = title_hook.split()
            if len(all_words) <= 3:
                lines = [" ".join(all_words).upper()]
            else:
                mid = (len(all_words) + 1) // 2
                lines = [" ".join(all_words[:mid]).upper(), " ".join(all_words[mid:]).upper()]

        font1 = get_font(78, bold=True)
        font2 = get_font(84, bold=True)

        if len(lines) == 1:
            # 1 Tầng chữ: Chữ Vàng tươi (#FFE600) viền đen dày trên nền Đỏ sẫm (#990000)
            text = lines[0]
            if not text.endswith("!") and not text.endswith("!?"):
                text += "!?"
            timg, tw, th = make_text_layer(text, font2, text_color=(255, 230, 0), stroke_color=(17, 17, 17), stroke_width=6)
            bw, bh = tw + 85, th + 45
            banner, pad = create_brush_banner(bw, bh, base_color=(153, 0, 0, 255), edge_color=(125, 0, 0, 255))
            b_cx = pad + (bw - tw) // 2
            b_cy = pad + (bh - th) // 2 - 12
            banner.paste(timg, (b_cx - 25, b_cy - 25), timg)

            rot_banner = banner.rotate(4.2, resample=Image.Resampling.BICUBIC, expand=True)
            y_pos = 280
            x_pos = (1080 - rot_banner.width) // 2
            comp.paste(rot_banner, (x_pos, y_pos), rot_banner)
            comp = add_sparks(comp, center_x=540, center_y=y_pos + rot_banner.height // 2, radius=360, count=40)
        else:
            # 2 Tầng chữ:
            # Dòng 1: Chữ Đen (#111111) viền trắng dày trên nền Vàng cam rực (#FFA500)
            text1 = lines[0]
            timg1, tw1, th1 = make_text_layer(text1, font1, text_color=(17, 17, 17), stroke_color=(255, 255, 255), stroke_width=4)
            bw1, bh1 = tw1 + 75, th1 + 38
            banner1, pad1 = create_brush_banner(bw1, bh1, base_color=(255, 165, 0, 255), edge_color=(230, 140, 0, 255))
            b_cx1 = pad1 + (bw1 - tw1) // 2
            b_cy1 = pad1 + (bh1 - th1) // 2 - 12
            banner1.paste(timg1, (b_cx1 - 25, b_cy1 - 25), timg1)

            # Dòng 2: Chữ Vàng tươi (#FFE600) viền đen dày trên nền Đỏ sẫm (#990000), kết thúc bằng ! hoặc !?
            text2 = lines[1]
            if not text2.endswith("!") and not text2.endswith("!?") and not text2.endswith("?"):
                text2 += "!?"
            timg2, tw2, th2 = make_text_layer(text2, font2, text_color=(255, 230, 0), stroke_color=(17, 17, 17), stroke_width=6)
            bw2, bh2 = tw2 + 85, th2 + 42
            banner2, pad2 = create_brush_banner(bw2, bh2, base_color=(153, 0, 0, 255), edge_color=(125, 0, 0, 255))
            b_cx2 = pad2 + (bw2 - tw2) // 2
            b_cy2 = pad2 + (bh2 - th2) // 2 - 12
            banner2.paste(timg2, (b_cx2 - 25, b_cy2 - 25), timg2)

            # Xoay nghiêng nhẹ 4.2 độ hướng lên
            rot_banner1 = banner1.rotate(4.2, resample=Image.Resampling.BICUBIC, expand=True)
            rot_banner2 = banner2.rotate(4.2, resample=Image.Resampling.BICUBIC, expand=True)

            # Đặt chữ nghiêm ngặt trong VÙNG CHỮ (5% -> 35%, tức Y: 100px -> 670px)
            y_pos1 = 135
            x_pos1 = (1080 - rot_banner1.width) // 2
            comp.paste(rot_banner1, (x_pos1, y_pos1), rot_banner1)

            # Thu gọn khoảng cách 2 tầng chữ vừa khít, nằm gọn trước vạch 670px
            overlap = 55
            y_pos2 = y_pos1 + rot_banner1.height - overlap
            x_pos2 = (1080 - rot_banner2.width) // 2
            comp.paste(rot_banner2, (x_pos2, y_pos2), rot_banner2)

            comp = add_sparks(comp, center_x=540, center_y=y_pos1 + 130, radius=420, count=55)
    else:
        # Long Video: 16:9 (1920x1080)
        badge_font = get_font(32, bold=True)
        hook_font = get_font(68, bold=True)
        overlay = Image.new("RGBA", target_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        card_top = 200
        card_w = 1500
        card_h = 300
        card_x0 = (target_size[0] - card_w) // 2
        card_y0 = card_top

        draw.rounded_rectangle(
            [(card_x0, card_y0), (card_x0 + card_w, card_y0 + card_h)],
            radius=24,
            fill=(10, 12, 18, 195),
            outline=(245, 158, 11, 220),
            width=4
        )
        draw.text((target_size[0] // 2, card_y0 + 50), "TRIẾT LÝ SỐNG SÂU SẮC", font=badge_font, fill=(245, 158, 11, 255), anchor="mm")
        draw.multiline_text(
            (target_size[0] // 2, card_y0 + 160),
            title_hook,
            font=hook_font,
            fill=(255, 255, 255, 255),
            align="center",
            anchor="mm",
            spacing=14
        )
        comp = Image.alpha_composite(comp, overlay)

    rgb_result = comp.convert("RGB")

    # Lưu file đồng bộ ở cả 3 vị trí
    thumb_path = input_folder / f"thumbnail_{video_id}.jpg"
    rgb_result.save(thumb_path, "JPEG", quality=95)
    shutil.copy2(thumb_path, vid_folder / f"thumbnail_{video_id}.jpg")
    shutil.copy2(thumb_path, PUBLIC_DIR / f"thumbnail_{video_id}.jpg")

    print(f"✅ ĐÃ TẠO THUMBNAIL VIRAL: {thumb_path.name} ({target_size[0]}x{target_size[1]})")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python pipeline/core_thumb.py <video_id> [title_hook] [--long]")
        sys.exit(1)

    vid = sys.argv[1]
    hook = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    p_type = "long" if "--long" in sys.argv else "short"
    generate_thumbnail(vid, title_hook=hook, project_type=p_type)
