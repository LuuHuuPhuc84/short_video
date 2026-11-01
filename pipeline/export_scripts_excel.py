# -*- coding: utf-8 -*-
"""
export_scripts_excel.py
=======================
Xuất kịch bản video ra file Excel — mỗi video = 1 sheet.

Cách dùng:
  # Xuất TẤT CẢ video (short + long) ra Excel
  python pipeline/export_scripts_excel.py

  # Xuất / cập nhật 1 video cụ thể (thêm/replace sheet)
  python pipeline/export_scripts_excel.py --video-id bhca_v1
  python pipeline/export_scripts_excel.py --video-id essay_ep01 --project long

  # Chỉ định file Excel đầu ra riêng
  python pipeline/export_scripts_excel.py --output my_scripts.xlsx

Tích hợp pipeline:
  Gọi hàm `export_video_to_excel(video_id, project)` từ auto_make_video.py
  sau khi render xong để tự động cập nhật sheet.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import openpyxl
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import (
        Alignment, Border, Font, GradientFill, PatternFill, Side
    )
    from openpyxl.utils import get_column_letter
except ImportError:
    print("❌ Thiếu thư viện openpyxl. Chạy: pip install openpyxl")
    sys.exit(1)

# ── Đường dẫn dự án ──────────────────────────────────────────────────────────
SHORT_VIDEO_DIR = Path(__file__).parent.parent          # E:\Project\short video
LONG_VIDEO_DIR  = Path("E:/Project/long video")

SHORT_EXCEL_FILE = SHORT_VIDEO_DIR / "scripts_short_video.xlsx"
LONG_EXCEL_FILE  = LONG_VIDEO_DIR  / "scripts_long_video.xlsx"

# ── Màu sắc chủ đề ───────────────────────────────────────────────────────────
COLOR = {
    "header_bg":    "1A2233",   # Nền tiêu đề cột — xanh đậm
    "header_font":  "FFFFFF",   # Chữ tiêu đề — trắng
    "meta_bg":      "2C3E50",   # Nền info tổng quan — xanh slate
    "meta_font":    "ECF0F1",   # Chữ info — xám sáng
    "label_bg":     "34495E",   # Nền label trong info
    "label_font":   "BDC3C7",   # Chữ label
    "scene_odd":    "EBF5FB",   # Nền hàng scene lẻ — xanh nhạt
    "scene_even":   "FDFEFE",   # Nền hàng scene chẵn — trắng
    "highlight_bg": "FFF3CD",   # Nền cột Highlight — vàng nhạt
    "hook_bg":      "D5E8D4",   # Nền hàng Hook (scene 1) — xanh lá nhạt
    "cta_bg":       "DAE8FC",   # Nền hàng CTA (scene cuối) — xanh nhạt
    "text_dark":    "1C2833",
    "accent":       "F39C12",   # Màu vàng cam nhấn
}

# ── Helper styles ─────────────────────────────────────────────────────────────

def _font(bold=False, size=10, color="000000", italic=False):
    return Font(name="Calibri", bold=bold, size=size, color=color, italic=italic)

def _fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def _align(h="left", v="center", wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def _border_thin():
    side = Side(style="thin", color="CCCCCC")
    return Border(left=side, right=side, top=side, bottom=side)

def _set_cell(ws, row, col, value, bold=False, size=10, font_color="000000",
              bg=None, halign="left", valign="center", wrap=True, italic=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font      = _font(bold=bold, size=size, color=font_color, italic=italic)
    cell.alignment = _align(h=halign, v=valign, wrap=wrap)
    cell.border    = _border_thin()
    if bg:
        cell.fill = _fill(bg)
    return cell


# ── Đọc dữ liệu video ────────────────────────────────────────────────────────

def _load_video_data(video_id: str, project: str = "short") -> dict:
    """
    Trả về dict tổng hợp từ info.json + script.json (+ video_data.json).
    Hỗ trợ cả video cũ (chỉ có info.json) lẫn video mới (có input/).
    """
    if project == "short":
        base = SHORT_VIDEO_DIR / "output" / video_id
    else:
        base = LONG_VIDEO_DIR  / "output" / video_id

    info_path       = base / "info.json"
    script_path     = base / "input" / "script.json"
    video_data_path = base / "input" / "video_data.json"

    result = {"video_id": video_id, "project": project, "scenes": []}

    # info.json (bắt buộc)
    if info_path.exists():
        with open(info_path, encoding="utf-8-sig") as f:
            result.update(json.load(f))

    # script.json (ưu tiên vì có lời thoại chi tiết)
    if script_path.exists():
        with open(script_path, encoding="utf-8-sig") as f:
            script = json.load(f)
        result.update({k: v for k, v in script.items() if k != "scenes"})
        raw_scenes = script.get("scenes", [])
        if raw_scenes and isinstance(raw_scenes[0], list):
            converted = []
            for idx, item in enumerate(raw_scenes):
                converted.append({
                    "scene": idx + 1,
                    "tag": item[0] if len(item) > 0 else "",
                    "voiceoverText": item[1] if len(item) > 1 else "",
                    "text": item[1] if len(item) > 1 else "",
                    "highlight": item[2] if len(item) > 2 else "",
                    "image": item[3] if len(item) > 3 else "",
                })
            result["scenes"] = converted
        else:
            result["scenes"] = raw_scenes

    # Fallback: tìm trong pipeline/script_*.json nếu chưa có scenes
    # (dành cho video cũ chưa có thư mục input/)
    if not result["scenes"] and project == "short":
        pipeline_dir = SHORT_VIDEO_DIR / "pipeline"

        # Mapping cứng: folder video_id → tên file script trong pipeline/
        EXPLICIT_MAP = {
            "an_tru_chuong1": "script_book_tnh_ch1.json",   # nếu có
            "an_tru_chuong2": "script_book_ch2.json",
            "an_tru_chuong3": "script_book_ch3.json",
            "an_tru_chuong4": "script_book_tnh_ch4.json",
            "an_tru_chuong5": "script_book_tnh_ch5.json",
            "an_tru_chuong6": "script_book_tnh_ch6.json",
            "an_tru_chuong7": "script_book_tnh_ch7.json",
            "an_tru_chuong8": "script_book_tnh_ch8.json",
        }

        candidate = None

        # 1. Dùng mapping cứng
        if video_id in EXPLICIT_MAP:
            p = pipeline_dir / EXPLICIT_MAP[video_id]
            if p.exists():
                candidate = p

        # 2. Tìm file tên khớp video_id: pipeline/script_{video_id}.json
        if candidate is None:
            p = pipeline_dir / f"script_{video_id}.json"
            if p.exists():
                candidate = p

        # 3. Fuzzy: so sánh 3 từ đầu của title
        if candidate is None:
            info_title = result.get("title", "").upper()
            info_words = info_title.split()[:3]
            best, best_score = None, 0
            for sf in sorted(pipeline_dir.glob("script_*.json")):
                try:
                    with open(sf, encoding="utf-8") as f:
                        sd = json.load(f)
                    sc_words = sd.get("title", "").upper().split()[:3]
                    matches = sum(1 for w in info_words if w in sc_words)
                    if matches > best_score:
                        best_score, best = matches, sf
                except Exception:
                    continue
            if best_score >= 2:
                candidate = best

        if candidate and candidate.exists():
            with open(candidate, encoding="utf-8") as f:
                script = json.load(f)
            # Gộp: ưu tiên giữ info.json, chỉ lấy scenes + trường còn trống
            for k, v in script.items():
                if k == "id":
                    continue
                if k == "scenes":
                    result["scenes"] = v
                elif not result.get(k):
                    result[k] = v
            result["video_id"] = video_id  # luôn giữ folder name làm ID
            result["_script_source"] = candidate.name  # debug info

    # video_data.json — bổ sung frame timing nếu có
    if video_data_path.exists():
        with open(video_data_path, encoding="utf-8") as f:
            vd = json.load(f)
        # Ghép timing vào từng scene nếu chưa có
        vd_scenes = {s.get("scene"): s for s in vd.get("scenes", [])}
        for sc in result["scenes"]:
            if not isinstance(sc, dict):
                continue
            snum = sc.get("scene")
            if snum in vd_scenes:
                for k in ("startFrame", "durationInFrames", "videoDurationInFrames"):
                    if k in vd_scenes[snum] and k not in sc:
                        sc[k] = vd_scenes[snum][k]
        fps = vd.get("fps", 30)
        result.setdefault("fps", fps)
        result.setdefault("durationInFrames", vd.get("durationInFrames"))
        result.setdefault("width",  vd.get("width"))
        result.setdefault("height", vd.get("height"))

    return result


def _duration_str(data: dict) -> str:
    fps = data.get("fps", 30)
    frames = data.get("durationInFrames")
    if frames and fps:
        total_s = frames / fps
        return f"{total_s:.1f}s ({frames} frames @ {fps}fps)"
    return ""


# ── Viết 1 sheet kịch bản ────────────────────────────────────────────────────

def _write_sheet(ws, data: dict):
    """Điền nội dung kịch bản vào worksheet ws."""
    # ws.freeze_panes = None  # Không đóng băng dòng nào để người dùng cuộn lên cuộn xuống dễ nhìn
    ws.freeze_panes = None

    # ── PHẦN 1: THÔNG TIN TỔNG QUAN ──────────────────────────────────────────
    meta_rows = [
        ("VIDEO ID",   data.get("video_id",  "—")),
        ("DỰ ÁN",      "Short Video" if data.get("project") == "short" else "Long Video"),
        ("TIÊU ĐỀ",    data.get("title",     "—")),
        ("SÁCH / NGUỒN", data.get("book",    data.get("subtitle", "—"))),
        ("TÁC GIẢ",    data.get("author",    "—")),
        ("CHƯƠNG",     data.get("chapter",   "—")),
        ("MÔ TẢ",      data.get("description", "—")),
    ]
    # Hàng 1: Tiêu đề lớn (merge A1:E1) và Nút quay lại Tổng Quan (F1)
    title_cell = ws.cell(row=1, column=1,
                         value=f"📋  KỊCH BẢN: {data.get('title','').upper()}")
    title_cell.font      = _font(bold=True, size=13, color=COLOR["accent"])
    title_cell.alignment = _align(h="center", v="center", wrap=False)
    title_cell.fill      = _fill(COLOR["meta_bg"])
    ws.merge_cells("A1:E1")
    ws.row_dimensions[1].height = 30

    back_btn = ws.cell(row=1, column=6, value='=HYPERLINK("#\'📋 TỔNG QUAN\'!A1", "⬅ VỀ TỔNG QUAN")')
    back_btn.font = _font(bold=True, size=10, color="FFFFFF")
    back_btn.alignment = _align(h="center", v="center", wrap=False)
    back_btn.fill = _fill("2980B9")

    # Hàng 2: thông tin kỹ thuật nhỏ
    tech_info = []
    if data.get("speed"):     tech_info.append(f"TTS Speed: {data['speed']}")
    if data.get("fps"):       tech_info.append(f"FPS: {data['fps']}")
    dur_str = _duration_str(data)
    if dur_str:               tech_info.append(f"Thời lượng: {dur_str}")
    if data.get("file_size_mb"): tech_info.append(f"File: {data['file_size_mb']} MB")
    tech_cell = ws.cell(row=2, column=1, value="  |  ".join(tech_info))
    tech_cell.font      = _font(italic=True, size=9, color=COLOR["label_font"])
    tech_cell.alignment = _align(h="center", v="center", wrap=False)
    tech_cell.fill      = _fill(COLOR["label_bg"])
    ws.merge_cells("A2:F2")
    ws.row_dimensions[2].height = 18

    # Hàng 3-N: meta info (label | value)
    current_row = 3
    for label, value in meta_rows:
        label_cell = ws.cell(row=current_row, column=1, value=label)
        label_cell.font      = _font(bold=True, size=9, color=COLOR["label_font"])
        label_cell.alignment = _align(h="right", v="center", wrap=False)
        label_cell.fill      = _fill(COLOR["label_bg"])
        label_cell.border    = _border_thin()

        val_cell = ws.cell(row=current_row, column=2, value=str(value))
        val_cell.font      = _font(size=9, color=COLOR["meta_font"])
        val_cell.alignment = _align(h="left", v="center", wrap=True)
        val_cell.fill      = _fill(COLOR["meta_bg"])
        val_cell.border    = _border_thin()
        ws.merge_cells(f"B{current_row}:F{current_row}")

        ws.row_dimensions[current_row].height = 18
        current_row += 1

    # Thêm info platforms / youtube / schedule nếu có
    extra_meta = []
    if data.get("platforms"):
        extra_meta.append(("NỀN TẢNG", ", ".join(data["platforms"])))
    if data.get("youtube_url"):
        extra_meta.append(("YOUTUBE URL", data["youtube_url"]))
    sched_val = data.get("schedule") or data.get("schedule_time") or data.get("youtube_scheduled_at") or "—"
    extra_meta.append(("LỊCH ĐĂNG", sched_val))
    if data.get("final_video_file"):
        extra_meta.append(("FILE MP4", data["final_video_file"]))

    for label, value in extra_meta:
        label_cell = ws.cell(row=current_row, column=1, value=label)
        label_cell.font      = _font(bold=True, size=9, color=COLOR["label_font"])
        label_cell.alignment = _align(h="right", v="center")
        label_cell.fill      = _fill(COLOR["label_bg"])
        label_cell.border    = _border_thin()

        val_cell = ws.cell(row=current_row, column=2, value=str(value))
        val_cell.font      = _font(size=9, color=COLOR["meta_font"])
        val_cell.alignment = _align(h="left", v="center")
        val_cell.fill      = _fill(COLOR["meta_bg"])
        val_cell.border    = _border_thin()
        ws.merge_cells(f"B{current_row}:F{current_row}")

        ws.row_dimensions[current_row].height = 18
        current_row += 1

    # Hàng trống ngăn cách
    ws.row_dimensions[current_row].height = 8
    current_row += 1

    # ── PHẦN 2: BẢNG KỊCH BẢN TỪNG CẢNH ─────────────────────────────────────
    HEADERS = [
        ("CẢNH #",       6),
        ("TAG / NHÃN",   14),
        ("LỜI THOẠI (VOICEOVER)",  55),
        ("HIGHLIGHT (TỰA / CHỮ NỔI)",   22),
        ("VISUAL / B-ROLL",        28),
        ("TIMING",       14),
    ]

    header_row = current_row
    for col_idx, (header, _) in enumerate(HEADERS, 1):
        cell = ws.cell(row=header_row, column=col_idx, value=header)
        cell.font      = _font(bold=True, size=10, color=COLOR["header_font"])
        cell.alignment = _align(h="center", v="center", wrap=False)
        cell.fill      = _fill(COLOR["header_bg"])
        cell.border    = _border_thin()
    ws.row_dimensions[header_row].height = 22
    current_row += 1

    scenes = data.get("scenes", [])
    total  = len(scenes)

    for i, scene in enumerate(scenes):
        snum     = scene.get("scene", i + 1)
        tag      = scene.get("tag", scene.get("chapter", ""))
        text     = scene.get("text", "")
        highlight= scene.get("highlight", "")
        image    = scene.get("image", "")
        image_url= scene.get("image_url", "")
        visual   = image_url if image_url else image   # hiển thị URL nếu có

        # Timing
        timing_parts = []
        if "startFrame" in scene and data.get("fps"):
            fps = data.get("fps", 30)
            start_s = scene["startFrame"] / fps
            dur_s   = scene.get("durationInFrames", 0) / fps
            timing_parts.append(f"Bắt đầu: {start_s:.1f}s")
            timing_parts.append(f"Thời lượng: {dur_s:.1f}s")
        timing = "\n".join(timing_parts)

        # Màu nền theo vị trí
        if i == 0:
            row_bg = COLOR["hook_bg"]          # Scene 1 = Hook
        elif i == total - 1:
            row_bg = COLOR["cta_bg"]           # Scene cuối = CTA
        elif i % 2 == 0:
            row_bg = COLOR["scene_odd"]
        else:
            row_bg = COLOR["scene_even"]

        row_data = [
            (str(snum), "center", False, row_bg),
            (tag,       "left",   False, row_bg),
            (text,      "left",   False, row_bg),
            (highlight, "center", True,  COLOR["highlight_bg"]),
            (visual,    "left",   False, row_bg),
            (timing,    "center", False, row_bg),
        ]

        for col_idx, (val, halign, bold, bg) in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font      = _font(bold=bold, size=9, color=COLOR["text_dark"])
            cell.alignment = _align(h=halign, v="top", wrap=True)
            cell.fill      = _fill(bg)
            cell.border    = _border_thin()

        # Tự động cao hàng dựa vào độ dài lời thoại
        estimated_lines = max(1, len(text) // 55 + text.count("\n") + 1)
        ws.row_dimensions[current_row].height = max(36, min(estimated_lines * 15, 120))
        current_row += 1

    # ── PHẦN 3: GHI CHÚ XUẤT ─────────────────────────────────────────────────
    current_row += 1
    export_note = ws.cell(row=current_row, column=1,
                          value=f"Xuất lúc: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  |  "
                                f"Script: {data.get('video_id','')}")
    export_note.font      = _font(italic=True, size=8, color="888888")
    export_note.alignment = _align(h="left", v="center", wrap=False)
    ws.merge_cells(f"A{current_row}:F{current_row}")

    # ── Thiết lập độ rộng cột ────────────────────────────────────────────────
    for col_idx, (_, width) in enumerate(HEADERS, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Cột A (LABEL meta) cũng hẹp hơn
    ws.column_dimensions["A"].width = max(HEADERS[0][1], 14)


# ── Xử lý file Excel ─────────────────────────────────────────────────────────

OVERVIEW_TAB_NAME = "📋 TỔNG QUAN"


def _safe_sheet_name(name: str) -> str:
    """Excel giới hạn tên sheet 31 ký tự, cấm một số ký tự đặc biệt."""
    forbidden = r'\/:*?[]'
    for ch in forbidden:
        name = name.replace(ch, "_")
    return name[:31]


def update_master_overview_tab(wb, project: str = "short") -> None:
    """
    Tạo hoặc cập nhật Bảng Tổng Quan (Master Overview Tab) tại vị trí đầu tiên (index 0).
    - Tóm tắt toàn bộ danh sách video: STT, Mã Video, Tiêu đề, Hook, Lịch phát sóng, Trạng thái, Nhạc nền, Thời lượng, Link YouTube.
    - Sắp xếp: Video có lịch phát sóng mới nhất / xa nhất trong tương lai ở trên cùng.
    - Tạo hyperlink nhảy thẳng đến sheet chi tiết của từng video.
    - Ghim tab '📋 TỔNG QUAN' ở vị trí index 0 và active tab này khi mở file.
    """
    if OVERVIEW_TAB_NAME in wb.sheetnames:
        ws_overview = wb[OVERVIEW_TAB_NAME]
        ws_overview.delete_rows(1, ws_overview.max_row + 15)
    else:
        ws_overview = wb.create_sheet(title=OVERVIEW_TAB_NAME, index=0)

    output_dir = SHORT_VIDEO_DIR / "output" if project == "short" else LONG_VIDEO_DIR / "output"
    now_vn = datetime.now()

    def parse_schedule_dt(time_str):
        if not time_str:
            return datetime.min
        m = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", str(time_str))
        if m:
            try:
                return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
            except Exception:
                pass
        return datetime.min

    items = []
    for sheet_name in wb.sheetnames:
        if "TỔNG QUAN" in sheet_name.upper():
            continue
        ws = wb[sheet_name]

        # 1. Đọc từ info.json nếu có
        info_path = output_dir / sheet_name / "info.json"
        data = {}
        if info_path.exists():
            try:
                data = json.loads(info_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Tiêu đề
        title = data.get("title")
        if not title:
            for r in range(1, 15):
                lbl = ws.cell(r, 1).value
                if lbl and "TIÊU ĐỀ" in str(lbl).upper():
                    title = ws.cell(r, 2).value
                    break
        title = (str(title) if title else sheet_name).replace("#shorts", "").replace("#Shorts", "").strip()

        # Hook 3s đầu
        hook = data.get("title_hook") or data.get("titleHook")
        if not hook:
            for r in range(10, 30):
                c1_val = ws.cell(r, 1).value
                if c1_val is not None and str(c1_val).strip() == "1":
                    hook = ws.cell(r, 3).value
                    break
        hook = (str(hook) if hook else "").replace("\n", " ").strip()

        # Lịch phát sóng
        sched = data.get("schedule") or data.get("schedule_time") or data.get("youtube_scheduled_at")
        if not sched:
            for r in range(1, 25):
                lbl = ws.cell(r, 1).value
                if lbl and "LỊCH ĐĂNG" in str(lbl).upper():
                    sched = ws.cell(r, 2).value
                    break
        sched_str = str(sched).strip() if sched and str(sched).strip() != "—" else ""
        sched_dt = parse_schedule_dt(sched_str)

        # Trạng thái
        if sched_dt > datetime.min:
            if sched_dt <= now_vn:
                status = "Đã phát sóng"
            else:
                status = "Đã lên lịch"
        elif "công khai" in sched_str.lower() or "đã xuất bản" in sched_str.lower() or data.get("privacyStatus") == "public":
            status = "Đã phát sóng"
        else:
            status = "Bản nháp"

        # Nhạc nền
        music = data.get("music", "")

        # Thời lượng
        dur = ""
        if data.get("duration_seconds"):
            dur = f"{int(round(data['duration_seconds']))}s"
        elif data.get("total_frames"):
            dur = f"{int(round(data['total_frames'] / 30))}s"

        # Link YouTube
        yt_id = data.get("youtube_id", "")
        yt_url = data.get("youtube_url") or (f"https://youtu.be/{yt_id}" if yt_id else "")

        items.append({
            "sheet_name": sheet_name,
            "title": title,
            "hook": hook,
            "schedule": sched_str,
            "schedule_dt": sched_dt,
            "status": status,
            "music": music,
            "duration": dur,
            "youtube_url": yt_url,
        })

    # Sắp xếp: có lịch phát sóng mới nhất / tương lai xa nhất lên đầu
    items.sort(key=lambda x: x["schedule_dt"], reverse=True)

    # Thống kê
    total_count = len(items)
    sched_count = sum(1 for it in items if it["status"] == "Đã lên lịch")
    pub_count   = sum(1 for it in items if it["status"] == "Đã phát sóng")
    draft_count = total_count - sched_count - pub_count

    # Cố định từ dòng 5 để cuộn xem danh sách thoải mái
    ws_overview.freeze_panes = "A5"

    # Hàng 1: Banner lớn
    ws_overview.merge_cells("A1:I1")
    cell_b1 = ws_overview.cell(row=1, column=1, value="📋 BẢNG TỔNG QUAN LỊCH PHÁT SÓNG & KỊCH BẢN VIDEO")
    cell_b1.font = _font(bold=True, size=14, color="FFFFFF")
    cell_b1.alignment = _align(h="center", v="center")
    cell_b1.fill = _fill(COLOR["header_bg"])
    ws_overview.row_dimensions[1].height = 32

    # Hàng 2: Thống kê nhanh
    ws_overview.merge_cells("A2:I2")
    stat_text = (f"Tổng số: {total_count} video  |  "
                 f"Đã lên lịch: {sched_count}  |  "
                 f"Đã phát sóng: {pub_count}  |  "
                 f"Bản nháp: {draft_count}  |  "
                 f"Cập nhật lúc: {now_vn.strftime('%d/%m/%Y %H:%M')}")
    cell_b2 = ws_overview.cell(row=2, column=1, value=stat_text)
    cell_b2.font = _font(italic=True, size=10, color=COLOR["meta_font"])
    cell_b2.alignment = _align(h="center", v="center")
    cell_b2.fill = _fill(COLOR["meta_bg"])
    ws_overview.row_dimensions[2].height = 22

    # Hàng 3: Trống
    ws_overview.row_dimensions[3].height = 8

    # Hàng 4: Header cột
    OVERVIEW_HEADERS = [
        ("STT", 6, "center"),
        ("MÃ VIDEO", 15, "center"),
        ("TIÊU ĐỀ VIDEO", 36, "left"),
        ("HOOK (3S ĐẦU)", 40, "left"),
        ("LỊCH PHÁT SÓNG", 20, "center"),
        ("TRẠNG THÁI", 16, "center"),
        ("NHẠC NỀN", 20, "left"),
        ("THỜI LƯỢNG", 12, "center"),
        ("LINK YOUTUBE", 24, "center"),
    ]

    for col_idx, (hdr, width, halign) in enumerate(OVERVIEW_HEADERS, 1):
        c = ws_overview.cell(row=4, column=col_idx, value=hdr)
        c.font = _font(bold=True, size=10, color=COLOR["header_font"])
        c.alignment = _align(h=halign, v="center")
        c.fill = _fill(COLOR["header_bg"])
        c.border = _border_thin()
        ws_overview.column_dimensions[get_column_letter(col_idx)].width = width
    ws_overview.row_dimensions[4].height = 26

    # Hàng 5+: Danh sách video
    cur_r = 5
    for idx, it in enumerate(items, 1):
        sname = it["sheet_name"]
        bg_row = COLOR["scene_odd"] if idx % 2 != 0 else COLOR["scene_even"]

        # Col 1: STT
        c1 = ws_overview.cell(cur_r, 1, value=idx)
        c1.alignment = _align(h="center", v="center")

        # Col 2: Mã Video kèm hyperlink nhảy tới sheet chi tiết
        c2 = ws_overview.cell(cur_r, 2)
        c2.value = f'=HYPERLINK("#\'{sname}\'!A1", "{sname}")'
        c2.font = Font(name="Calibri", bold=True, size=10, color="0B5394", underline="single")
        c2.alignment = _align(h="center", v="center")

        # Col 3: Tiêu đề
        c3 = ws_overview.cell(cur_r, 3, value=it["title"])
        c3.font = _font(bold=True, size=10, color=COLOR["text_dark"])
        c3.alignment = _align(h="left", v="center", wrap=True)

        # Col 4: Hook
        c4 = ws_overview.cell(cur_r, 4, value=it["hook"])
        c4.font = _font(size=9, color="333333")
        c4.alignment = _align(h="left", v="center", wrap=True)

        # Col 5: Lịch phát sóng
        c5 = ws_overview.cell(cur_r, 5, value=it["schedule"] if it["schedule"] else "—")
        c5.font = _font(bold=bool(it["schedule"]), size=10, color="000000")
        c5.alignment = _align(h="center", v="center")

        # Col 6: Trạng thái
        st = it["status"]
        c6 = ws_overview.cell(cur_r, 6, value=st)
        c6.alignment = _align(h="center", v="center")
        if st == "Đã lên lịch":
            c6.fill = _fill("DDEBF7")
            c6.font = _font(bold=True, size=9, color="1F4E78")
        elif st == "Đã phát sóng":
            c6.fill = _fill("E2F0D9")
            c6.font = _font(bold=True, size=9, color="274E13")
        else:
            c6.fill = _fill("FFF2CC")
            c6.font = _font(bold=True, size=9, color="7F6000")

        # Col 7: Nhạc nền
        c7 = ws_overview.cell(cur_r, 7, value=it["music"] if it["music"] else "—")
        c7.font = _font(size=9, color="444444")
        c7.alignment = _align(h="left", v="center")

        # Col 8: Thời lượng
        c8 = ws_overview.cell(cur_r, 8, value=it["duration"] if it["duration"] else "—")
        c8.font = _font(size=9, color="444444")
        c8.alignment = _align(h="center", v="center")

        # Col 9: Link YouTube
        c9 = ws_overview.cell(cur_r, 9)
        if it["youtube_url"]:
            c9.value = f'=HYPERLINK("{it["youtube_url"]}", "Xem YouTube ↗")'
            c9.font = Font(name="Calibri", bold=True, size=9, color="C0392B", underline="single")
        else:
            c9.value = "—"
            c9.font = _font(size=9, color="888888")
        c9.alignment = _align(h="center", v="center")

        # Áp dụng border & nền
        for c_idx in [1, 3, 4, 5, 7, 8]:
            cell = ws_overview.cell(cur_r, c_idx)
            cell.border = _border_thin()
            cell.fill = _fill(bg_row)
        c2.border = _border_thin()
        c2.fill = _fill(bg_row)
        c6.border = _border_thin()
        c9.border = _border_thin()
        if not it["youtube_url"]:
            c9.fill = _fill(bg_row)

        ws_overview.row_dimensions[cur_r].height = 24
        cur_r += 1

    # Đưa sheet Tổng Quan lên vị trí đầu tiên (index 0)
    if ws_overview in wb._sheets:
        wb._sheets.remove(ws_overview)
    wb._sheets.insert(0, ws_overview)
    wb.active = ws_overview


def export_video_to_excel(video_id: str, project: str = "short",
                          excel_file: Path = None) -> Path:
    """
    Xuất/cập nhật 1 video vào Excel.
    - Nếu sheet đã tồn tại → xóa và tạo lại (replace).
    - Nếu file Excel chưa có → tạo mới.
    Trả về đường dẫn file Excel.
    """
    if excel_file is None:
        excel_file = SHORT_EXCEL_FILE if project == "short" else LONG_EXCEL_FILE

    excel_file = Path(excel_file)

    # Tải dữ liệu
    data = _load_video_data(video_id, project)
    if not data.get("title") and not data.get("scenes"):
        print(f"⚠️  Không tìm thấy dữ liệu cho video_id='{video_id}'")
        return excel_file

    # Tên sheet = video_id (ngắn gọn, dễ tra cứu)
    sheet_name = _safe_sheet_name(video_id)

    # Mở hoặc tạo workbook
    if excel_file.exists():
        wb = load_workbook(excel_file)
    else:
        wb = Workbook()
        # Xóa sheet trống mặc định
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

    # Xóa sheet cũ nếu đã tồn tại (replace)
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
        print(f"  ↻ Đã xóa sheet cũ: '{sheet_name}'")

    # Tạo sheet mới
    ws = wb.create_sheet(title=sheet_name)
    _write_sheet(ws, data)

    # Cập nhật Tab Tổng Quan
    update_master_overview_tab(wb, project)

    # Sắp xếp tab với Tổng Quan ở đầu và các sheet theo lịch phát sóng
    try:
        from core_schedule import reorder_sheets_by_schedule
        reorder_sheets_by_schedule(wb)
    except Exception as e:
        pass

    excel_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(excel_file)
    print(f"  ✅ Sheet '{sheet_name}' & '📋 TỔNG QUAN' → {excel_file}")
    return excel_file


def export_all_videos(project: str = "short", excel_file: Path = None) -> Path:
    """Xuất TẤT CẢ video của một dự án vào Excel."""
    if project == "short":
        output_dir = SHORT_VIDEO_DIR / "output"
        if excel_file is None:
            excel_file = SHORT_EXCEL_FILE
    else:
        output_dir = LONG_VIDEO_DIR / "output"
        if excel_file is None:
            excel_file = LONG_EXCEL_FILE

    if not output_dir.exists():
        print(f"❌ Không tìm thấy thư mục output: {output_dir}")
        return excel_file

    # Tìm tất cả video_id hợp lệ (có info.json)
    video_ids = sorted([
        d.name for d in output_dir.iterdir()
        if d.is_dir() and (d / "info.json").exists()
    ])

    if not video_ids:
        print(f"⚠️  Không tìm thấy video nào trong {output_dir}")
        return excel_file

    print(f"\n📊 Xuất {len(video_ids)} video ({project}) → {excel_file}")
    print("─" * 60)

    # Tạo workbook mới (ghi đè hoàn toàn khi export_all)
    wb = Workbook()
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    for vid in video_ids:
        print(f"  → Đang xử lý: {vid}")
        data = _load_video_data(vid, project)
        if not data.get("title") and not data.get("scenes"):
            print(f"     ⚠️  Bỏ qua (thiếu dữ liệu)")
            continue
        sheet_name = _safe_sheet_name(vid)
        # Chèn sheet mới nhất lên đầu (index=0)
        ws = wb.create_sheet(title=sheet_name, index=0)
        _write_sheet(ws, data)
        print(f"     ✅ Sheet: '{sheet_name}'")

    # Cập nhật Tab Tổng Quan
    update_master_overview_tab(wb, project)

    try:
        from core_schedule import reorder_sheets_by_schedule
        reorder_sheets_by_schedule(wb)
    except Exception as e:
        pass

    excel_file = Path(excel_file)
    excel_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(excel_file)
    print(f"\n🎉 Đã lưu: {excel_file}  ({len(wb.sheetnames)} sheets)")
    return excel_file


def export_all_both_projects(short_excel: Path = None, long_excel: Path = None):
    """Xuất cả Short Video và Long Video vào 2 file Excel riêng."""
    export_all_videos("short", short_excel)
    if LONG_VIDEO_DIR.exists():
        export_all_videos("long",  long_excel)
    else:
        print(f"\n⚠️  Không tìm thấy dự án Long Video tại: {LONG_VIDEO_DIR}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Xuất kịch bản video ra file Excel"
    )
    parser.add_argument(
        "--video-id", "-v",
        help="Xuất 1 video cụ thể (video_id). Bỏ qua để xuất TẤT CẢ."
    )
    parser.add_argument(
        "--project", "-p",
        choices=["short", "long", "both"],
        default="both",
        help="Dự án cần xuất (short / long / both). Mặc định: both"
    )
    parser.add_argument(
        "--output", "-o",
        help="Đường dẫn file Excel đầu ra (tùy chọn)"
    )
    args = parser.parse_args()

    excel_out = Path(args.output) if args.output else None

    if args.video_id:
        # Xuất 1 video
        project = args.project if args.project != "both" else "short"
        export_video_to_excel(args.video_id, project, excel_out)
    else:
        # Xuất tất cả
        if args.project == "both":
            export_all_both_projects(
                short_excel=excel_out or SHORT_EXCEL_FILE,
                long_excel =excel_out or LONG_EXCEL_FILE,
            )
        elif args.project == "short":
            export_all_videos("short", excel_out)
        else:
            export_all_videos("long",  excel_out)


if __name__ == "__main__":
    main()
