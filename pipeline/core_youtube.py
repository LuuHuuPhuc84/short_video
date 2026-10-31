# -*- coding: utf-8 -*-
"""
pipeline/core_youtube.py
========================
Module ĐƠN NHIỆM: Quản lý và đăng video lên kênh YouTube "Nửa Chén Trà".
Chỉ nhận video đã render sẵn + metadata để xuất bản (Draft / Scheduled).
Không dính líu đến render hay Drive.
"""

import os
import sys
import json
import datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PIPELINE_DIR = BASE_DIR / "pipeline"
TOKEN_FILE = PIPELINE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def get_youtube_service():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file token YouTube: {TOKEN_FILE}")
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    try:
        from token_guard import ensure_token_health
        ensure_token_health(auto_refresh=True)
    except Exception:
        pass

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Lưu lại access token mới
            with open(TOKEN_FILE, "r", encoding="utf-8") as rf:
                td = json.load(rf)
            td["token"] = creds.token
            with open(TOKEN_FILE, "w", encoding="utf-8") as wf:
                json.dump(td, wf, indent=2, ensure_ascii=False)

    return build("youtube", "v3", credentials=creds)

def publish_video_to_youtube(video_id, schedule=None, draft=False):
    """Xuất bản video lên YouTube Shorts."""
    from googleapiclient.http import MediaFileUpload

    print("========================================================")
    print(f"📺 YOUTUBE PUBLISHER: Đăng video '{video_id}'")
    print("========================================================")

    vid_folder = OUTPUT_DIR / video_id
    mp4_file = vid_folder / f"video_{video_id}.mp4"
    if not mp4_file.exists():
        candidates = list(vid_folder.glob("*.mp4"))
        if candidates:
            mp4_file = sorted(candidates, key=lambda f: f.stat().st_mtime, reverse=True)[0]

    if not mp4_file.exists():
        print(f"❌ Không tìm thấy file video trong: {vid_folder}")
        return False

    # Đọc metadata
    info_file = vid_folder / "info.json"
    title = f"Bài học cuộc sống #shorts | {video_id}"
    description = "Nhìn sâu để sống nhẹ — Nửa Chén Trà #nuachentra #shorts"
    tags = ["Nửa Chén Trà", "nhìn sâu để sống nhẹ", "shorts", "bài học cuộc sống"]
    schedule_str = schedule

    if info_file.exists():
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                d = json.load(f)
            title = d.get("title") or title
            description = d.get("description") or description
            tags = d.get("tags") or tags
            if not schedule_str:
                schedule_str = d.get("schedule") or d.get("schedule_time")
        except Exception as e:
            print(f"⚠️ Lỗi đọc info.json: {e}")

    # QUY CHUẨN BẮT BUỘC: Luôn luôn ghi hashtag số tập #<video_id> vào mô tả và thẻ tags
    ep_hashtag = f"#{video_id}"
    if ep_hashtag not in description and video_id not in description:
        if "#shorts" in description:
            description = description.replace("#shorts", f"{ep_hashtag} #shorts")
        else:
            description = f"{description.strip()} {ep_hashtag}"

    if not isinstance(tags, list):
        tags = [str(tags)] if tags else []
    if video_id not in tags:
        tags.insert(0, video_id)

    if "#shorts" not in title.lower():
        title = f"{title} #shorts"

    privacy = d.get("privacyStatus") or d.get("privacy") or "private"
    if str(schedule_str).strip().lower() in ["now", "public", "công chiếu ngay", "công chiếu luôn", "immediately"]:
        privacy = "public"
        schedule_str = None

    status_dict = {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": True
    }

    if privacy == "public":
        publish_log = "PUBLIC (Công chiếu công khai ngay)"
    elif schedule_str and not draft:
        try:
            s = str(schedule_str).strip()
            now = datetime.datetime.now()
            if " " in s:
                schedule_dt = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")
            else:
                t = datetime.datetime.strptime(s, "%H:%M").time()
                schedule_dt = datetime.datetime.combine(now.date(), t)
                if schedule_dt <= now:
                    schedule_dt += datetime.timedelta(days=1)
            tz_vn = datetime.timezone(datetime.timedelta(hours=7))
            schedule_dt = schedule_dt.replace(tzinfo=tz_vn)
            utc_dt = schedule_dt.astimezone(datetime.timezone.utc)
            iso_utc = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            status_dict["publishAt"] = iso_utc
            publish_log = f"SCHEDULED (Hẹn giờ phát sóng lúc {schedule_str} VN -> {iso_utc})"
        except Exception as e:
            print(f"⚠️ Lỗi parse schedule '{schedule_str}': {e}. Giữ Private Draft.")
            publish_log = "PRIVATE (Bản nháp / Draft)"
    else:
        publish_log = "PRIVATE (Bản nháp / Draft)"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": "22"
        },
        "status": status_dict
    }

    service = get_youtube_service()
    size_mb = round(mp4_file.stat().st_size / (1024 * 1024), 2)
    print(f"🚀 File: {mp4_file.name} ({size_mb} MB)")
    print(f"📌 Tiêu đề: {title}")
    print(f"📅 Chế độ: {publish_log}")
    print(f"🤖 Synthetic Media: Đã tick bật (Tuân thủ chính sách AI)")

    media = MediaFileUpload(str(mp4_file), mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    print("☁️ Đang tải video lên YouTube...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"   Tiến độ tải lên: {pct}%")

    yt_id = response.get("id")
    print(f"\n🎉 TẢI LÊN YOUTUBE THÀNH CÔNG! Video ID: {yt_id}")
    print(f"🔗 Link xem: https://youtube.com/shorts/{yt_id}")

    # Upload thumbnail nếu có
    thumb_candidates = [
        vid_folder / f"thumbnail_{video_id}.jpg",
        vid_folder / "input" / f"thumbnail_{video_id}.jpg",
        vid_folder / f"thumbnail_{video_id}.png"
    ]
    thumb_path = None
    for tc in thumb_candidates:
        if tc.exists():
            thumb_path = tc
            break

    if thumb_path:
        try:
            print(f"🖼️ Đang cập nhật Thumbnail: {thumb_path.name}...")
            service.thumbnails().set(
                videoId=yt_id,
                media_body=MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
            ).execute()
            print("✓ Đã gắn Thumbnail thành công!")
        except Exception as e:
            print(f"⚠️ Gắn Thumbnail: {e}")

    # Tự động gỡ bỏ video cũ nếu có replace_youtube_id
    old_yt_id = None
    if info_file.exists():
        try:
            with open(info_file, "r", encoding="utf-8-sig") as f:
                inf = json.load(f)
            old_yt_id = inf.get("replace_youtube_id") or inf.get("old_youtube_id")
        except Exception:
            pass
    if old_yt_id and old_yt_id != yt_id:
        try:
            print(f"🗑️ Đang tự động gỡ bỏ video cũ trên YouTube: {old_yt_id}...")
            service.videos().delete(id=old_yt_id).execute()
            print(f"✅ ĐÃ XÓA THÀNH CÔNG VIDEO CŨ ({old_yt_id}) ĐỂ THAY THẾ BẰNG BẢN MỚI ({yt_id})!")
        except Exception as de:
            print(f"⚠️ Cảnh báo gỡ video cũ {old_yt_id}: {de}")

    return yt_id

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python pipeline/core_youtube.py <video_id> [--draft] [--schedule 'YYYY-MM-DD HH:MM']")
        sys.exit(1)

    vid = sys.argv[1]
    is_draft = "--draft" in sys.argv
    sched = None
    if "--schedule" in sys.argv:
        idx = sys.argv.index("--schedule")
        if idx + 1 < len(sys.argv):
            sched = sys.argv[idx + 1]

    publish_video_to_youtube(vid, schedule=sched, draft=is_draft)
