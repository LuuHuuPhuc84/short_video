# -*- coding: utf-8 -*-
"""
pack_inputs.py
==============
Đóng gói trọn bộ nguyên liệu đầu vào vào thư mục output/{video_id}/input/:
1. video_data.json, voiceover.wav, script.json, script.md
2. Toàn bộ các file hình ảnh hoặc video B-roll đã cắt dùng cho từng cảnh.
3. Đồng bộ trọn gói lên Google Drive sau khi duyệt.
"""

import os
import sys
import shutil
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
PUBLIC_DIR = BASE_DIR / 'remotion-video' / 'public'
PIPELINE_DIR = BASE_DIR / 'pipeline'
ASSETS_HUB = BASE_DIR / 'assets_hub'

def generate_script_markdown(video_id, meta):
    scenes = meta.get('scenes', [])
    title = meta.get('title', f'Video {video_id}')
    book = meta.get('book', '')
    author = meta.get('author', '')
    title_hook = meta.get('titleHook', '')
    md = f'# Kịch Bản Chi Tiết: {title}\n\n'
    md += f'- **Video ID:** `{video_id}`\n'
    md += f'- **Sách:** {book}\n'
    md += f'- **Tác giả:** {author}\n'
    md += f'- **Title Hook (0 - 1.5s):** `{title_hook}`\n'
    md += f'- **Tổng thời lượng:** {round(meta.get("durationInFrames", 0)/30, 2)}s\n\n'
    md += '## Phân Cảnh & Lời Thoại\n\n'
    for sc in scenes:
        md += f'### Cảnh {sc.get("scene")}: [{sc.get("startFrame")} - {sc.get("startFrame") + sc.get("durationInFrames")} frames]\n'
        md += f'- **Visual (B-roll):** `{sc.get("image") or sc.get("video") or sc.get("backgroundVideo")}`\n'
        md += f'- **Highlight Text:** `{sc.get("highlight")}`\n'
        md += f'- **Voiceover:** "{sc.get("text")}"\n\n'
    return md

def pack_video_input(vid):
    """
    Đóng gói toàn bộ nguyên liệu vào output/{vid}/input/:
    - video_data.json, voiceover.wav, script.json, script.md
    - TOÀN BỘ các hình ảnh hoặc video B-roll đã cắt của các cảnh.
    """
    out_fol = OUTPUT_DIR / vid
    out_fol.mkdir(parents=True, exist_ok=True)
    input_fol = out_fol / 'input'
    input_fol.mkdir(parents=True, exist_ok=True)

    print(f"\n📦 Đang đóng gói nguyên liệu vào thư mục duyệt: output/{vid}/input/ ...")

    # 1. Metadata JSON
    meta_src = PUBLIC_DIR / f'video_data_{vid}.json'
    if not meta_src.exists():
        meta_src = PUBLIC_DIR / f'{vid}.json'
    meta = {}
    if meta_src.exists():
        with open(meta_src, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        shutil.copy2(meta_src, input_fol / 'video_data.json')
        print(f'  ✓ Đã lưu: video_data.json')

    # 2. Audio Voiceover
    voice_src = PUBLIC_DIR / f'voiceover_{vid}.wav'
    if not voice_src.exists() and meta.get("audioFile"):
        voice_src = PUBLIC_DIR / meta.get("audioFile")
    if voice_src.exists():
        shutil.copy2(voice_src, input_fol / 'voiceover.wav')
        print(f'  ✓ Đã lưu: voiceover.wav')

    # 3. Kịch bản JSON
    script_src = PIPELINE_DIR / f'script_{vid}.json'
    if script_src.exists():
        shutil.copy2(script_src, input_fol / 'script.json')
        print(f'  ✓ Đã lưu: script.json')

    # 4. Kịch bản Markdown
    script_md = generate_script_markdown(vid, meta)
    (input_fol / 'script.md').write_text(script_md, encoding='utf-8')
    print(f'  ✓ Đã lưu: script.md')

    # 5. COPY TOÀN BỘ HÌNH ẢNH HOẶC VIDEO ĐÃ CẮT CỦA CÁC CẢNH
    scenes = meta.get('scenes', [])
    copied_media = []
    for sc in scenes:
        media_name = sc.get('image') or sc.get('video') or sc.get('backgroundVideo')
        if not media_name:
            continue
        # Tìm media ở public hoặc assets_hub
        media_src = PUBLIC_DIR / media_name
        if not media_src.exists():
            media_src = ASSETS_HUB / ('videos' if media_name.endswith('.mp4') else 'images') / media_name
        
        if media_src.exists():
            dest_media = input_fol / media_name
            if not dest_media.exists() or dest_media.stat().st_size != media_src.stat().st_size:
                shutil.copy2(media_src, dest_media)
            copied_media.append(media_name)
            print(f'  ✓ Đã copy media B-roll: {media_name} ({media_src.stat().st_size / (1024*1024):.1f} MB)')
        else:
            print(f'  ⚠️ Không tìm thấy media: {media_name}')

    # 6. BẮT BUỘC COPY ẢNH THUMBNAIL VÀO THƯ MỤC INPUT ĐỂ DUYỆT & GẮN VÀO FRAME 0
    thumb_candidates = [
        input_fol / f'thumbnail_{vid}.jpg',
        out_fol / f'thumbnail_{vid}.jpg',
        out_fol / 'test' / f'thumbnail_v1_bo_chua_tung_noi.jpg',
        out_fol / 'test' / f'thumbnail_{vid}.jpg',
        PUBLIC_DIR / f'thumbnail_{vid}.jpg',
        ASSETS_HUB / 'images' / f'thumbnail_{vid}.jpg'
    ]
    for tc in thumb_candidates:
        if tc.exists():
            dest_thumb = input_fol / f'thumbnail_{vid}.jpg'
            if not dest_thumb.exists() or dest_thumb.stat().st_size != tc.stat().st_size:
                shutil.copy2(tc, dest_thumb)
            pub_thumb = PUBLIC_DIR / f'thumbnail_{vid}.jpg'
            if not pub_thumb.exists() or pub_thumb.stat().st_size != tc.stat().st_size:
                shutil.copy2(tc, pub_thumb)
            print(f'  ✓ Đã lưu Thumbnail để duyệt & Frame 0: thumbnail_{vid}.jpg')

            # Cập nhật thumbnailImage vào video_data để Remotion hiển thị ở giây đầu tiên (Frame 0-30)
            if meta:
                meta['thumbnailImage'] = f'thumbnail_{vid}.jpg'
                if (PUBLIC_DIR / f'video_data_{vid}.json').exists():
                    with open(PUBLIC_DIR / f'video_data_{vid}.json', 'w', encoding='utf-8') as f:
                        json.dump(meta, f, ensure_ascii=False, indent=2)
                with open(input_fol / 'video_data.json', 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
            break

    all_files = [f.name for f in input_fol.iterdir()]
    print(f"👉 Tổng cộng {len(all_files)} files trong output/{vid}/input/:")
    for fn in all_files:
        print(f"   - {fn}")
    return input_fol

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else ['gian_v1']
    for t in targets:
        pack_video_input(t)
