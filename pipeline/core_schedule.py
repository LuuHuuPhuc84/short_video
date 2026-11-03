# -*- coding: utf-8 -*-
"""
pipeline/core_schedule.py
=========================
Module ĐƠN NHIỆM: Quản lý và thay đổi lịch phát sóng (Schedule) siêu tốc.
Chỉ làm đúng 3 việc nhẹ:
1. Cập nhật publishAt trên YouTube Data API v3 (nếu video đã đăng).
2. Cập nhật schedule_time trong file info.json (output/{vid}/ và remotion-video/public/).
3. Cập nhật ô Lịch phát sóng trong file Excel scripts_short_video.xlsx.

TUYỆT ĐỐI KHÔNG:
- Không render / remotion.
- Không upload lại video MP4 hay B-roll lên Google Drive.
- Không quét tải nguyên liệu.
"""

import re
import sys
import json
import datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PUBLIC_DIR = BASE_DIR / "remotion-video" / "public"
PIPELINE_DIR = BASE_DIR / "pipeline"

def parse_to_iso_utc(time_str):
    """
    Chuyển chuỗi YYYY-MM-DD HH:MM (Giờ Việt Nam UTC+7) sang ISO 8601 UTC.
    Ví dụ: '2026-11-02 19:30' -> '2026-11-02T12:30:00Z'
    """
    time_str = time_str.strip()
    dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    # Trừ 7 tiếng để ra UTC
    utc_dt = dt - datetime.timedelta(hours=7)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:00Z")

def update_local_metadata(video_id, schedule_str):
    """Cập nhật ngày giờ schedule trong info.json local."""
    updated = False
    paths = [
        OUTPUT_DIR / video_id / "info.json",
        OUTPUT_DIR / video_id / "input" / "info.json",
        PUBLIC_DIR / f"info_{video_id}.json"
    ]
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                data["schedule_time"] = schedule_str
                data["schedule"] = schedule_str
                p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                updated = True
            except Exception as e:
                print(f"⚠️ Lỗi update {p.name}: {e}")
    return updated

EXCEL_PATH = BASE_DIR / "scripts_short_video.xlsx"

def reorder_sheets_by_schedule(wb):
    """
    Sắp xếp lại thứ tự các sheet tab trong file Excel:
    1. Sheet '📋 TỔNG QUAN' LUÔN LUÔN đứng ở vị trí ĐẦU TIÊN (tab index 0).
    2. Các sheet video tiếp theo được sắp xếp theo thời gian phát sóng xa nhất / mới nhất giảm dần.
    """
    overview_sheet = None
    video_sheets = []

    for ws in list(wb._sheets):
        if "TỔNG QUAN" in ws.title.upper():
            overview_sheet = ws
        else:
            video_sheets.append(ws)

    def get_sheet_schedule(ws):
        for r in range(1, 35):
            val_label = ws.cell(r, 1).value
            if val_label and "LỊCH ĐĂNG" in str(val_label).upper():
                val_time = ws.cell(r, 2).value
                if val_time:
                    m = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", str(val_time))
                    if m:
                        try:
                            return datetime.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
                        except Exception:
                            pass
        return datetime.datetime.min

    video_sheets.sort(key=get_sheet_schedule, reverse=True)

    if overview_sheet:
        wb._sheets = [overview_sheet] + video_sheets
        wb.active = overview_sheet
    else:
        wb._sheets = video_sheets
        if wb._sheets:
            wb.active = wb._sheets[0]

def update_excel_schedule(video_id, new_schedule_str=None, wb=None, save=True):
    """
    Cập nhật trực tiếp (in-place) đúng 1 ô 'LỊCH ĐĂNG' trong sheet của video_id.
    TUYỆT ĐỐI KHÔNG XÓA SHEET, giữ nguyên 100% định dạng, nội dung bảng và dữ liệu.
    Tự động đưa sheet phát sóng cuối cùng lên vị trí đầu tiên.
    """
    if not EXCEL_PATH.exists():
        print(f"  ⚠️ Không tìm thấy file Excel: {EXCEL_PATH}")
        return False

    if not new_schedule_str:
        info_path = OUTPUT_DIR / video_id / "info.json"
        if info_path.exists():
            try:
                data = json.loads(info_path.read_text(encoding="utf-8"))
                new_schedule_str = data.get("schedule") or data.get("schedule_time", "")
            except Exception:
                pass
    if not new_schedule_str:
        return False

    import openpyxl

    should_close = False
    if wb is None:
        wb = openpyxl.load_workbook(str(EXCEL_PATH))
        should_close = True

    if video_id not in wb.sheetnames:
        # Nếu chưa có sheet thì mới dùng export_video_to_excel để khởi tạo ban đầu
        try:
            from export_scripts_excel import export_video_to_excel
            export_video_to_excel(video_id, project="short")
            print(f"  ✓ Đã khởi tạo mới sheet Excel: {video_id}")
            return True
        except Exception as e:
            print(f"  ⚠️ Lỗi tạo sheet {video_id}: {e}")
            return False

    ws = wb[video_id]
    updated_cell = False

    # Tìm ô có nhãn 'LỊCH ĐĂNG' ở Cột A (rows 1 -> 35)
    for r in range(1, 35):
        val = ws.cell(r, 1).value
        if val and "LỊCH ĐĂNG" in str(val).upper():
            ws.cell(r, 2, value=str(new_schedule_str))
            updated_cell = True
            break

    if not updated_cell:
        from export_scripts_excel import export_video_to_excel
        export_video_to_excel(video_id, project="short")
        return True

    # Cập nhật Tab Tổng Quan
    try:
        from export_scripts_excel import update_master_overview_tab
        update_master_overview_tab(wb, project="short")
    except Exception as e:
        print(f"  ⚠️ Lỗi update master overview: {e}")

    # Sắp xếp lại thứ tự tab: Tổng quan ở đầu, video phát sóng cuối cùng đứng kế tiếp
    reorder_sheets_by_schedule(wb)

    if save and should_close:
        wb.save(str(EXCEL_PATH))

    print(f"  ✓ Đã cập nhật ô 'LỊCH ĐĂNG' ({video_id} -> {new_schedule_str}) & Tab '📋 TỔNG QUAN' [In-Place]")
    return True

def update_youtube_schedule(video_id, schedule_str):
    """Cập nhật publishAt trên YouTube Shorts qua YouTube Data API v3."""
    try:
        from core_youtube import get_youtube_service
        yt = get_youtube_service()

        # Đọc title để tìm đúng video trên kênh
        info_path = OUTPUT_DIR / video_id / "info.json"
        video_title = None
        if info_path.exists():
            data = json.loads(info_path.read_text(encoding="utf-8"))
            video_title = data.get("title")

        # Tìm video ID trên kênh bằng Search API hoặc List API
        yt_video_id = None
        req = yt.search().list(part="snippet", forMine=True, type="video", maxResults=25, order="date")
        res = req.execute()

        for item in res.get("items", []):
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            # So khớp theo title hoặc mã video
            if video_title and (title.strip().lower() == video_title.strip().lower() or video_title[:25].lower() in title.lower()):
                yt_video_id = item["id"]["videoId"]
                break
            elif f"| {video_id}" in title or video_id in title:
                yt_video_id = item["id"]["videoId"]
                break

        if not yt_video_id:
            print(f"  ℹ️ Không tìm thấy video '{video_id}' đã xuất bản trên YouTube (có thể chưa đăng).")
            return False

        # Cập nhật status
        iso_utc = parse_to_iso_utc(schedule_str)
        body = {
            "id": yt_video_id,
            "status": {
                "privacyStatus": "private",
                "publishAt": iso_utc,
                "selfDeclaredMadeForKids": False
            }
        }
        resp = yt.videos().update(part="status", body=body).execute()
        actual_pub = resp.get("status", {}).get("publishAt")
        print(f"  ✓ Đã cập nhật lịch YouTube ({yt_video_id}): {schedule_str} (UTC: {actual_pub})")
        return True
    except Exception as e:
        print(f"  ⚠️ Lỗi YouTube API cho {video_id}: {e}")
        return False

def schedule_single_video(video_id, schedule_str):
    """Đổi lịch cho 1 video đơn lẻ."""
    print("========================================================")
    print(f"⏱️ RESCHEDULE CHUYÊN TRÁCH: {video_id} -> {schedule_str}")
    print("========================================================")
    # 1. Local metadata
    update_local_metadata(video_id, schedule_str)
    # 2. Excel
    update_excel_schedule(video_id)
    # 3. YouTube API
    update_youtube_schedule(video_id, schedule_str)
    print(f"🎉 Hoàn tất đổi lịch cho {video_id}!\n")

def parse_slot_time(dt):
    """Quy chuẩn nhịp đăng Shorts: 11:30 và 19:30 mỗi ngày."""
    return dt.strftime("%Y-%m-%d %H:%M")

def get_next_slot(current_dt):
    """
    Tính slot phát sóng tiếp theo theo nhịp 11:30 và 19:30.
    Nếu đang là 11:30 -> sang 19:30 cùng ngày.
    Nếu đang là 19:30 -> sang 11:30 ngày hôm sau.
    """
    if current_dt.hour < 12:
        return current_dt.replace(hour=19, minute=30, second=0, microsecond=0)
    else:
        next_day = current_dt + datetime.timedelta(days=1)
        return next_day.replace(hour=11, minute=30, second=0, microsecond=0)

def schedule_batch_videos(video_ids, start_time_str):
    """
    Đổi lịch hàng loạt cho danh sách video theo chuỗi slot (11:30 & 19:30).
    Ví dụ: start="2026-11-02 19:30"
    v11: 02/11 19:30
    v12: 03/11 11:30
    v13: 03/11 19:30 ...
    """
    print("========================================================")
    print(f"⏱️ RESCHEDULE HÀNG LOẠT ({len(video_ids)} videos)")
    print(f"📍 Bắt đầu từ: {start_time_str}")
    print("========================================================")

    current_dt = datetime.datetime.strptime(start_time_str.strip(), "%Y-%m-%d %H:%M")

    for i, vid in enumerate(video_ids):
        sched_str = current_dt.strftime("%Y-%m-%d %H:%M")
        print(f"[{i+1}/{len(video_ids)}] Video {vid} -> Lịch: {sched_str}")
        update_local_metadata(vid, sched_str)
        update_excel_schedule(vid)
        update_youtube_schedule(vid, sched_str)
        # Tính slot kế tiếp
        current_dt = get_next_slot(current_dt)

    print("\n🎉 HOÀN TẤT ĐỔI LỊCH TOÀN BỘ DANH SÁCH!")

def pull_schedule_from_youtube(target_video_id=None):
    """
    Quét toàn bộ lịch phát sóng (publishAt) thực tế từ YouTube Studio,
    đồng bộ ngược lại vào info.json và file Excel scripts_short_video.xlsx.
    """
    print("========================================================")
    print("🔄 PULL SCHEDULE: KÉO LỊCH TỪ YOUTUBE STUDIO VỀ EXCEL")
    if target_video_id:
        print(f"🎯 Mục tiêu: {target_video_id}")
    else:
        print("🎯 Mục tiêu: Toàn bộ video trên kênh")
    print("========================================================")

    try:
        from core_youtube import get_youtube_service
        yt = get_youtube_service()
    except Exception as e:
        print(f"❌ Không thể kết nối YouTube API: {e}")
        return False

    # 1. Thu thập ID và metadata hiện tại trên máy Local
    local_info_map = {}
    yt_to_vid = {}
    for d in OUTPUT_DIR.iterdir():
        if d.is_dir():
            inf_p = d / "info.json"
            if inf_p.exists():
                try:
                    data = json.loads(inf_p.read_text(encoding="utf-8"))
                    vid = data.get("id") or d.name
                    local_info_map[vid] = data
                    yt_id = data.get("youtube_id")
                    if yt_id:
                        yt_to_vid[yt_id] = vid
                except Exception:
                    pass

    # 2. Lấy playlist uploads của kênh
    try:
        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        uploads_playlist_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except Exception as e:
        print(f"❌ Lỗi lấy uploads playlist: {e}")
        return False

    # 3. Quét danh sách video trên kênh
    playlist_items = []
    next_token = None
    while True:
        res = yt.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_token
        ).execute()
        playlist_items.extend(res.get("items", []))
        next_token = res.get("nextPageToken")
        if not next_token or len(playlist_items) >= 100:
            break

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_items]
    if not video_ids:
        print("ℹ️ Không tìm thấy video nào trên kênh.")
        return True

    # 4. Lấy chi tiết status (publishAt) của từng video
    import openpyxl
    excel_wb = openpyxl.load_workbook(str(EXCEL_PATH)) if EXCEL_PATH.exists() else None

    tz_vn = datetime.timezone(datetime.timedelta(hours=7))
    chunks = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]
    
    updated_count = 0
    matched_count = 0

    for chunk in chunks:
        vids_res = yt.videos().list(part="snippet,status", id=",".join(chunk)).execute()
        for v in vids_res.get("items", []):
            yt_id = v["id"]
            snippet = v.get("snippet", {})
            status = v.get("status", {})
            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            privacy = status.get("privacyStatus", "")
            sched_utc = status.get("publishAt")

            # Xác định video_id (ví dụ: nct_v06, nct_v09...)
            matched_vid = yt_to_vid.get(yt_id)
            if not matched_vid:
                m = re.search(r"(?:#|\b)(nct_v\d+|bhca_v\d+|gian_v\d+|gd_v\d+|cntt_v\d+)\b", desc + " " + title, re.IGNORECASE)
                if m:
                    matched_vid = m.group(1).lower()

            if not matched_vid:
                continue

            if target_video_id and matched_vid != target_video_id:
                continue

            matched_count += 1
            
            # Tính thời gian phát sóng giờ VN
            if sched_utc:
                dt_utc = datetime.datetime.fromisoformat(sched_utc.replace("Z", "+00:00"))
                dt_vn = dt_utc.astimezone(tz_vn)
                sched_vn = dt_vn.strftime("%Y-%m-%d %H:%M")
            elif privacy == "public":
                pub_utc = snippet.get("publishedAt")
                if pub_utc:
                    dt_utc = datetime.datetime.fromisoformat(pub_utc.replace("Z", "+00:00"))
                    dt_vn = dt_utc.astimezone(tz_vn)
                    sched_vn = dt_vn.strftime("%Y-%m-%d %H:%M")
                else:
                    sched_vn = "Đã công chiếu"
            else:
                sched_vn = "Bản nháp (Private)"

            curr_local_sched = local_info_map.get(matched_vid, {}).get("schedule") or local_info_map.get(matched_vid, {}).get("schedule_time", "")

            # So sánh và cập nhật nếu có thay đổi
            norm_sched = sched_vn.strip()
            norm_local = str(curr_local_sched).strip()

            if norm_sched != norm_local:
                print(f"  ↻ [{matched_vid}] Phát hiện thay đổi lịch:")
                print(f"      Cũ: {curr_local_sched or 'Chưa có'}")
                print(f"      Mới trên YouTube: {sched_vn}")
                update_local_metadata(matched_vid, sched_vn)
                for p in [OUTPUT_DIR / matched_vid / "info.json", OUTPUT_DIR / matched_vid / "input" / "info.json", PUBLIC_DIR / f"info_{matched_vid}.json"]:
                    if p.exists():
                        try:
                            d = json.loads(p.read_text(encoding="utf-8"))
                            d["youtube_id"] = yt_id
                            d["youtube_url"] = f"https://youtu.be/{yt_id}"
                            d["privacyStatus"] = privacy
                            p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
                        except Exception:
                            pass
                update_excel_schedule(matched_vid, new_schedule_str=sched_vn, wb=excel_wb, save=False)
                updated_count += 1
            else:
                print(f"  ✓ [{matched_vid}] Khớp lịch: {sched_vn}")

    if excel_wb:
        try:
            from export_scripts_excel import update_master_overview_tab
            update_master_overview_tab(excel_wb, project="short")
        except Exception as e:
            print(f"  ⚠️ Lỗi update master overview: {e}")
        reorder_sheets_by_schedule(excel_wb)
        saved = False
        try:
            excel_wb.save(str(EXCEL_PATH))
            saved = True
        except PermissionError:
            print(f"  ⚠️ File '{EXCEL_PATH.name}' đang được mở trong ứng dụng Excel.")
            print("  ⏳ Vui lòng đóng file Excel để hoàn tất lưu (đang chờ tối đa 15s)...")
            import time
            for _ in range(15):
                time.sleep(1)
                try:
                    excel_wb.save(str(EXCEL_PATH))
                    saved = True
                    break
                except PermissionError:
                    continue
            if not saved:
                backup_path = EXCEL_PATH.parent / "scripts_short_video_synced.xlsx"
                try:
                    excel_wb.save(str(backup_path))
                    print(f"  ⚠️ Đã lưu dữ liệu đồng bộ vào file phụ: {backup_path.name}")
                except Exception as e:
                    print(f"  ❌ Không thể lưu Excel: {e}")
        if saved:
            print("  💾 Đã cập nhật Tab '📋 TỔNG QUAN' và sắp xếp thứ tự các sheet theo lịch phát sóng!")

    print("\n" + "=" * 56)
    print(f"🎉 TỔNG KẾT ĐỒNG BỘ: Đã khớp {matched_count} video, cập nhật {updated_count} video vào Excel!")
    print("=" * 56)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng:")
        print("  Kéo lịch về Excel:  python pipeline/core_schedule.py pull [video_id]")
        print("  1 video (đổi lịch): python pipeline/core_schedule.py <video_id> '<YYYY-MM-DD HH:MM>'")
        print("  Hàng loạt:          python pipeline/core_schedule.py batch '<YYYY-MM-DD HH:MM>' vid1 vid2 vid3...")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd in ["pull", "sync"]:
        target_vid = sys.argv[2] if len(sys.argv) > 2 else None
        pull_schedule_from_youtube(target_vid)
    elif cmd == "batch":
        start_time = sys.argv[2]
        vids = sys.argv[3:]
        schedule_batch_videos(vids, start_time)
    else:
        if len(sys.argv) < 3:
            print("❌ Vui lòng truyền thời gian: python pipeline/core_schedule.py <video_id> '<YYYY-MM-DD HH:MM>'")
            sys.exit(1)
        vid = sys.argv[1]
        sched_time = sys.argv[2]
        schedule_single_video(vid, sched_time)
