# -*- coding: utf-8 -*-
"""
pipeline/core_flow.py
=====================
Core module quản lý tự động hóa sinh ảnh bằng Google Flow (Playwright qua Chrome CDP).
DÙNG CHUNG cho cả 2 dự án:
  - Short Video (Tỷ lệ 9:16, 1080x1920 Full HD dọc)
  - Long Video  (Tỷ lệ 16:9, 1920x1080 Widescreen ngang)

Đặc điểm kỹ thuật:
  1. Kết nối qua Remote Debugging Port 9222 (Profile riêng biệt tại %USERPROFILE%/ChromeFlowProfile).
  2. Không lưu password/cookie trong repo, chỉ tái sử dụng session đăng nhập đã mở.
  3. Tự động ép chế độ '1x' (tiết kiệm 50% credit so với 2x mặc định).
  4. Trích xuất ảnh gốc độ phân giải cao nhất (=s0).
  5. Đồng bộ đồng thời vào thư mục duyệt (output/{video_id}/input/) và thư mục dựng video (public/).
"""

import sys
import os
import io
import time
import json
import base64
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Union
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Đường dẫn thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
OUTPUT_DIR = BASE_DIR / "output"
REMOTION_PUBLIC = BASE_DIR / "remotion-video" / "public"

CDP_DEFAULT_URL = "http://127.0.0.1:9222"
DEFAULT_PROFILE_DIR = Path.home() / "ChromeFlowProfile"

# Cấu hình chuẩn tỷ lệ khung hình
ASPECT_RATIOS = {
    "short": {
        "ratio": "9:16",
        "prefix": "Vertical 9:16 aspect ratio. Generate exactly 1 image. ",
        "resolution": "1080x1920",
        "desc": "Short Video (Khổ dọc 9:16)"
    },
    "long": {
        "ratio": "16:9",
        "prefix": "Horizontal 16:9 widescreen aspect ratio. Generate exactly 1 image. ",
        "resolution": "1920x1080",
        "desc": "Long Video (Khổ ngang 16:9)"
    }
}


def get_aspect_config(project_or_ratio: str = "short") -> Dict[str, str]:
    """Trả về cấu hình tỷ lệ khung hình theo loại dự án (short/long) hoặc chuỗi tỷ lệ (9:16, 16:9)."""
    p = str(project_or_ratio).strip().lower()
    if p in ("short", "9:16", "vertical"):
        return ASPECT_RATIOS["short"]
    elif p in ("long", "16:9", "horizontal", "widescreen"):
        return ASPECT_RATIOS["long"]
    return ASPECT_RATIOS["short"]


def check_flow_status(cdp_url: str = CDP_DEFAULT_URL) -> Dict[str, Union[bool, str, int]]:
    """
    Kiểm tra trạng thái kết nối tới trình duyệt Chrome debug và tab Google Flow.
    """
    status = {
        "browser_running": False,
        "tab_found": False,
        "url": "",
        "image_count": 0,
        "project_id": "",
        "message": ""
    }
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(cdp_url, timeout=4000)
            status["browser_running"] = True
            
            flow_page = None
            for page in browser.contexts[0].pages:
                u = page.url or ""
                if "flow.google" in u:
                    flow_page = page
                    status["tab_found"] = True
                    status["url"] = u
                    if "/project/" in u:
                        status["project_id"] = u.split("/project/")[-1].split("?")[0]
                    break
            
            if flow_page:
                imgs = flow_page.query_selector_all("img")
                flow_imgs = [i for i in imgs if "/asb/" in (i.get_attribute("src") or "")]
                status["image_count"] = len(flow_imgs)
                status["message"] = f"OK. Tìm thấy Google Flow ({status['image_count']} ảnh trong dự án)."
            else:
                status["message"] = "Trình duyệt đang mở nhưng chưa thấy tab https://flow.google"
    except Exception as e:
        status["message"] = f"Không kết nối được CDP ({cdp_url}): {e}"
        
    return status


def launch_flow_browser(port: int = 9222, profile_dir: Optional[Path] = None):
    """
    Khởi động Google Chrome ở chế độ Remote Debugging Port 9222 độc lập.
    """
    if profile_dir is None:
        profile_dir = DEFAULT_PROFILE_DIR
    profile_dir.mkdir(parents=True, exist_ok=True)

    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    chrome_exe = None
    for cand in chrome_candidates:
        if Path(cand).exists():
            chrome_exe = cand
            break

    if not chrome_exe:
        print("[!] Không tìm thấy trình duyệt Chrome hoặc Edge trên máy tính.")
        return False

    cmd = [
        chrome_exe,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={str(profile_dir)}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://flow.google"
    ]
    print(f"[*] Đang khởi động trình duyệt Chrome với profile: {profile_dir} (Port {port})...")
    subprocess.Popen(cmd)
    time.sleep(2)
    print("[+] Đã gửi lệnh mở trình duyệt thành công!")
    return True


def format_prompt(prompt_text: str, project_or_ratio: str = "short") -> str:
    """
    Chuẩn hóa prompt để Flow hiểu chính xác tỷ lệ và chỉ sinh 1 ảnh (1x mode).
    """
    cfg = get_aspect_config(project_or_ratio)
    prefix = cfg["prefix"]
    
    cleaned = prompt_text.strip()
    # Loại bỏ tiền tố tỷ lệ cũ nếu có để tránh lặp
    for k in ["Vertical 9:16 aspect ratio. Generate exactly 1 image.",
              "Horizontal 16:9 widescreen aspect ratio. Generate exactly 1 image.",
              "Vertical 9:16 aspect ratio.", "Horizontal 16:9 aspect ratio."]:
        if cleaned.startswith(k):
            cleaned = cleaned[len(k):].strip()
            
    return prefix + cleaned


def generate_single_image(
    prompt: str,
    dest_paths: List[Union[str, Path]],
    project_or_ratio: str = "short",
    cdp_url: str = CDP_DEFAULT_URL,
    timeout_sec: int = 90
) -> bool:
    """
    Hàm sinh ảnh cốt lõi:
    - Bơm prompt vào Google Flow
    - Nhấn nút tạo ảnh
    - Đợi xuất hiện ảnh mới (đếm ảnh tăng)
    - Tải ảnh độ phân giải gốc (=s0) và ghi ra danh sách dest_paths
    """
    final_prompt = format_prompt(prompt, project_or_ratio)
    cfg = get_aspect_config(project_or_ratio)

    print(f"\n=======================================================")
    print(f"🎨 GOOGLE FLOW: Sinh ảnh ({cfg['desc']})")
    print(f"✨ Prompt (1x mode):\n{final_prompt}")
    print(f"📁 Lưu đến: {[str(p) for p in dest_paths]}")
    print(f"=======================================================\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url, timeout=10000)
        except Exception as e:
            print(f"[-] Lỗi kết nối tới trình duyệt Chrome CDP ({cdp_url}): {e}")
            print("💡 Hãy chạy 'python pipeline/cli.py flow launch' để mở trình duyệt.")
            return False

        # Tìm tab Flow
        target_page = None
        for pg in browser.contexts[0].pages:
            u = pg.url or ""
            if "flow.google.com/project" in u:
                target_page = pg
                break
        if not target_page:
            for pg in browser.contexts[0].pages:
                if "flow.google" in (pg.url or ""):
                    target_page = pg
                    break

        if not target_page:
            print("[-] Không tìm thấy tab Google Flow. Vui lòng mở https://flow.google trên Chrome debug.")
            return False

        # Đếm số lượng ảnh Flow hiện tại
        def count_flow_images():
            imgs = target_page.query_selector_all("img")
            return len([i for i in imgs if "/asb/" in (i.get_attribute("src") or "")])

        initial_count = count_flow_images()
        print(f"[*] Số ảnh hiện có trong dự án trước khi gửi prompt: {initial_count}")

        # Tắt dialog overlay nếu có
        try:
            target_page.keyboard.press("Escape")
            backdrop = target_page.query_selector(".cdk-overlay-backdrop, [role='dialog'] button[aria-label='Close']")
            if backdrop:
                backdrop.click(force=True)
                time.sleep(0.5)
        except Exception:
            pass

        # Tìm ô nhập prompt (TipTap ProseMirror)
        box = target_page.query_selector(".tiptap.ProseMirror")
        if not box:
            box = target_page.query_selector("[role='textbox']")
        if not box:
            box = target_page.query_selector("textarea")

        if not box:
            print("[-] Không tìm thấy ô nhập prompt trên Flow!")
            return False

        try:
            box.click(force=True)
        except Exception:
            pass

        time.sleep(0.3)
        target_page.keyboard.press("Control+A")
        target_page.keyboard.press("Backspace")
        time.sleep(0.2)
        target_page.keyboard.insert_text(final_prompt)
        time.sleep(0.5)

        # Tìm nút bấm 'Bắt đầu tạo' / 'Create'
        btn = None
        candidates = target_page.query_selector_all("button")
        for b in candidates:
            txt = (b.inner_text() or "").strip()
            if any(k in txt.lower() for k in ["bắt đầu tạo", "tạo", "generate", "create", "start"]):
                btn = b
                break

        if not btn:
            for b in candidates:
                if b.get_attribute("aria-label") and any(k in b.get_attribute("aria-label").lower() for k in ["generate", "tạo", "create"]):
                    btn = b
                    break

        if not btn:
            print("[-] Không tìm thấy nút 'Bắt đầu tạo', thử nhấn Ctrl+Enter...")
            target_page.keyboard.press("Control+Enter")
        else:
            btn.click(force=True)
            print("[+] Đã click nút 'Bắt đầu tạo'.")

        print("[*] Đang chờ Google Flow tạo ảnh mới...")
        start_time = time.time()
        new_image_found = False

        while time.time() - start_time < timeout_sec:
            time.sleep(4)
            current_count = count_flow_images()
            elapsed = int(time.time() - start_time)

            is_generating = False
            spinners = target_page.query_selector_all("[role='progressbar'], svg.animate-spin, [data-is-generating='true']")
            if len(spinners) > 0:
                is_generating = True

            print(f"   [{elapsed}s] Ảnh hiện có: {current_count} (Ban đầu: {initial_count}) | Đang tạo: {is_generating}")

            if current_count > initial_count:
                new_image_found = True
                print("[+] ĐÃ XUẤT HIỆN ẢNH MỚI VÀ HOÀN TẤT!")
                break

        if not new_image_found:
            print(f"[-] Quá thời gian chờ {timeout_sec}s nhưng không thấy ảnh mới sinh ra.")
            return False

        # Lấy URL của ảnh mới nhất
        imgs = target_page.query_selector_all("img")
        flow_imgs = [i for i in imgs if "/asb/" in (i.get_attribute("src") or "")]
        if not flow_imgs:
            print("[-] Không trích xuất được thẻ img của ảnh Flow.")
            return False

        newest_img = flow_imgs[-1]
        img_src = newest_img.get_attribute("src")

        # Chuẩn hóa về độ phân giải gốc cao nhất (=s0)
        if "=s" in img_src:
            img_src = img_src.split("=s")[0] + "=s0"
        elif "=" in img_src:
            base_url = img_src.split("=")[0]
            img_src = base_url + "=s0"

        # Tải ảnh về qua base64 fetch trong ngữ cảnh page
        js_download = f"""
        async () => {{
            const response = await fetch('{img_src}');
            const blob = await response.blob();
            return new Promise((resolve) => {{
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.readAsDataURL(blob);
            }});
        }}
        """
        data_url = target_page.evaluate(js_download)
        if not data_url or "," not in data_url:
            print("[-] Không tải được dữ liệu ảnh qua fetch.")
            return False

        img_bytes = base64.b64decode(data_url.split(",")[1])

        # Ghi ra toàn bộ các đường dẫn đích
        for dst in dest_paths:
            dst_p = Path(dst)
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            with open(dst_p, "wb") as f:
                f.write(img_bytes)

        print(f"✅ THÀNH CÔNG: Đã lưu ảnh ({len(img_bytes):,} bytes) vào {len(dest_paths)} vị trí.")
        return True


def load_flow_prompts(video_id: str) -> Optional[Dict]:
    """Tìm nạp danh sách flow prompts của video_id."""
    prompts_file = PIPELINE_DIR / f"flow_prompts_{video_id}.json"
    if prompts_file.exists():
        with open(prompts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def generate_scene_image(
    video_id: str,
    scene_num: int,
    project: str = "short",
    custom_prompt: Optional[str] = None,
    cdp_url: str = CDP_DEFAULT_URL
) -> bool:
    """
    Sinh ảnh cho 1 cảnh cụ thể của video. Tự động xác định đường dẫn lưu trữ theo project.
    """
    # Xác định đường dẫn lưu
    dest_input = OUTPUT_DIR / video_id / "input" / f"{video_id}_scene{scene_num}.jpg"
    dest_public = REMOTION_PUBLIC / f"{video_id}_scene{scene_num}.jpg"
    dest_paths = [dest_input, dest_public]

    # Nếu có thư mục dự án long-video, thêm vào danh sách
    if project == "long":
        long_public = BASE_DIR / "long-video" / "public" / f"{video_id}_scene{scene_num}.jpg"
        if long_public.parent.exists():
            dest_paths.append(long_public)

    prompt_text = custom_prompt
    tag_name = f"Cảnh {scene_num}"
    voiceover_text = ""

    if not prompt_text:
        flow_data = load_flow_prompts(video_id)
        if flow_data and "scenes" in flow_data:
            for sc in flow_data["scenes"]:
                if sc.get("scene_num") == scene_num:
                    prompt_text = sc.get("flow_prompt")
                    tag_name = sc.get("tag", tag_name)
                    voiceover_text = sc.get("voiceover", "")
                    break

    if not prompt_text:
        # Dự phòng: đọc từ video_data.json
        vd_path = OUTPUT_DIR / video_id / "input" / "video_data.json"
        if vd_path.exists():
            with open(vd_path, "r", encoding="utf-8") as f:
                vd = json.load(f)
                scenes = vd.get("scenes", [])
                if 1 <= scene_num <= len(scenes):
                    sc = scenes[scene_num - 1]
                    voiceover_text = sc.get("text", "")
                    tag_name = sc.get("tag", tag_name)
                    # Tạo prompt tự động phong cách hoài niệm Á Đông
                    prompt_text = f"Cinematic 35mm photograph. An evocative Asian emotional scene depicting: {voiceover_text}. Nostalgic domestic warmth, soft natural lighting, muted earth tones, 4k photorealistic."

    if not prompt_text:
        print(f"[-] Không tìm thấy prompt cho {video_id} cảnh {scene_num}.")
        print(f"💡 Hãy tạo file 'pipeline/flow_prompts_{video_id}.json' trước.")
        return False

    print(f"\n🎬 KÍCH HOẠT CẢNH {scene_num} CHO '{video_id.upper()}' ({project.upper()} VIDEO): {tag_name}")
    if voiceover_text:
        print(f"🎙 Thoại: {voiceover_text}")

    return generate_single_image(
        prompt=prompt_text,
        dest_paths=dest_paths,
        project_or_ratio=project,
        cdp_url=cdp_url
    )


def generate_batch_scenes(
    video_id: str,
    project: str = "short",
    start_scene: int = 1,
    end_scene: Optional[int] = None,
    cdp_url: str = CDP_DEFAULT_URL
) -> Dict[str, Union[int, List[int]]]:
    """
    Sinh toàn bộ các cảnh của video (từ start_scene đến end_scene) hoàn toàn tự động.
    """
    flow_data = load_flow_prompts(video_id)
    total_scenes = 5
    if flow_data and "scenes" in flow_data:
        total_scenes = len(flow_data["scenes"])
    else:
        vd_path = OUTPUT_DIR / video_id / "input" / "video_data.json"
        if vd_path.exists():
            with open(vd_path, "r", encoding="utf-8") as f:
                vd = json.load(f)
                total_scenes = len(vd.get("scenes", [])) or 5

    if end_scene is None or end_scene > total_scenes:
        end_scene = total_scenes

    print(f"\n=======================================================")
    print(f"🚀 BẮT ĐẦU BATCH SINH ẢNH GOOGLE FLOW CHO: {video_id.upper()}")
    print(f"📐 Dự án: {project.upper()} | Phạm vi cảnh: {start_scene} -> {end_scene} (Tổng: {total_scenes})")
    print(f"=======================================================\n")

    success_scenes = []
    failed_scenes = []

    for sc in range(start_scene, end_scene + 1):
        print(f"\n--- Tiến trình: Cảnh {sc}/{end_scene} ---")
        ok = generate_scene_image(
            video_id=video_id,
            scene_num=sc,
            project=project,
            cdp_url=cdp_url
        )
        if ok:
            success_scenes.append(sc)
        else:
            failed_scenes.append(sc)
            print(f"[!] Dừng batch do lỗi ở cảnh {sc}.")
            break

    print(f"\n=======================================================")
    print(f"🏁 KẾT THÚC BATCH CHO {video_id.upper()}:")
    print(f"   ✓ Thành công ({len(success_scenes)} cảnh): {success_scenes}")
    if failed_scenes:
        print(f"   ✗ Thất bại ({len(failed_scenes)} cảnh): {failed_scenes}")
    print(f"=======================================================\n")

    return {
        "total": end_scene - start_scene + 1,
        "success": len(success_scenes),
        "failed": len(failed_scenes),
        "success_list": success_scenes,
        "failed_list": failed_scenes
    }


def create_flow_prompts_file(video_id: str, project: str = "short", force: bool = False) -> Optional[Path]:
    """
    Tự động đọc video_data.json hoặc script.json để sinh file template pipeline/flow_prompts_{video_id}.json.
    """
    out_file = PIPELINE_DIR / f"flow_prompts_{video_id}.json"
    if out_file.exists() and not force:
        print(f"[*] File flow prompts đã tồn tại: {out_file}")
        return out_file

    # Đọc dữ liệu từ input
    candidates = [
        OUTPUT_DIR / video_id / "input" / "script.json",
        OUTPUT_DIR / video_id / "input" / "video_data.json",
        OUTPUT_DIR / video_id / "input" / f"video_data_{video_id}.json",
    ]
    data = None
    for c in candidates:
        if c.exists():
            with open(c, "r", encoding="utf-8") as f:
                data = json.load(f)
                break

    if not data:
        print(f"[-] Không tìm thấy dữ liệu kịch bản cho: {video_id}")
        return None

    scenes = data.get("scenes", [])
    title = data.get("title", "")
    title_hook = data.get("title_hook", data.get("titleHook", ""))
    cfg = get_aspect_config(project)

    prompt_data = {
        "video_id": video_id,
        "project": project,
        "aspect_ratio": cfg["ratio"],
        "title": title,
        "title_hook": title_hook,
        "scenes": []
    }

    for idx, sc in enumerate(scenes, 1):
        text = sc.get("text", "")
        tag = sc.get("tag", f"Cảnh {idx}")
        highlight = sc.get("highlight", "")
        
        prompt_item = {
            "scene_num": idx,
            "tag": tag,
            "voiceover": text,
            "highlight": highlight,
            "flow_prompt": f"Cinematic 35mm film still. An evocative Asian emotional domestic setting representing: {text}. Soft warm lighting, atmospheric depth, muted natural tones, 4k photorealistic."
        }
        prompt_data["scenes"].append(prompt_item)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã tạo file prompts chuẩn cho Google Flow: {out_file} ({len(scenes)} cảnh)")
    return out_file
