import os
import sys
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def get_youtube_service():
    client_id = (os.environ.get("YOUTUBE_CLIENT_ID") or "").strip()
    client_secret = (os.environ.get("YOUTUBE_CLIENT_SECRET") or "").strip()
    refresh_token = (os.environ.get("YOUTUBE_REFRESH_TOKEN") or "").strip()

    if not (client_id and client_secret and refresh_token):
        print("❌ Lỗi: Thiếu YOUTUBE Secrets (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN).")
        return None

    try:
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ Lỗi xác thực YouTube API: {e}")
        return None

def upload_short_to_youtube(video_path, video_id):
    youtube = get_youtube_service()
    if not youtube:
        return None

    vpath = Path(video_path)
    if not vpath.exists():
        print(f"❌ Không tìm thấy file video tại: {vpath}")
        return None

    # Tìm thông tin metadata (ưu tiên info.json, sau đó là video_data_*.json)
    info_file = None
    possible_infos = [
        Path("output") / video_id / "info.json",
        vpath.parent / "info.json",
        Path("remotion-video/public") / f"info_{video_id}.json",
        Path("pipeline") / f"script_{video_id}.json",
        Path("remotion-video/public") / f"video_data_{video_id}.json"
    ]
    for p in possible_infos:
        if p.exists():
            info_file = p
            break

    title = f"Bài học cuộc sống #shorts | {video_id}"
    description = "Nhìn sâu để sống nhẹ — Nửa Chén Trà #nuachentra #shorts"
    tags = ["Nửa Chén Trà", "nhìn sâu để sống nhẹ", "shorts", "bài học cuộc sống"]

    if info_file and info_file.exists():
        try:
            with open(info_file, "r", encoding="utf-8-sig") as f:
                d = json.load(f)
            if d.get("skip_youtube") or d.get("no_youtube"):
                print("ℹ️ Bỏ qua upload YouTube theo cấu hình info.json (skip_youtube=True).")
                return "SKIPPED_BY_CONFIG"
            title = d.get("title") or title
            description = d.get("description") or description
            tags = d.get("tags") or tags
            schedule_str = d.get("schedule")
        except Exception as e:
            print(f"⚠️ Lỗi đọc file metadata {info_file}: {e}")
            schedule_str = None
            schedule_str = None

    if "#shorts" not in title.lower():
        title = f"{title} #shorts"

    status_dict = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": True
    }

    publish_log = "PRIVATE (Bản nháp / Draft)"
    if schedule_str:
        try:
            import datetime
            s = str(schedule_str).strip()
            now = datetime.datetime.now()
            if " " in s:
                schedule_dt = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")
            else:
                time_part = datetime.datetime.strptime(s, "%H:%M").time()
                schedule_dt = datetime.datetime.combine(now.date(), time_part)
                if schedule_dt <= now:
                    schedule_dt += datetime.timedelta(days=1)
            tz_vn = datetime.timezone(datetime.timedelta(hours=7))
            schedule_dt = schedule_dt.replace(tzinfo=tz_vn)
            utc_dt = schedule_dt.astimezone(datetime.timezone.utc)
            iso_utc = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            status_dict["publishAt"] = iso_utc
            publish_log = f"SCHEDULED (Hẹn giờ phát sóng lúc {schedule_str} VN -> {iso_utc})"
        except Exception as e:
            print(f"⚠️ Lỗi định dạng schedule '{schedule_str}': {e}. Giữ chế độ private.")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "22",
            "defaultLanguage": "vi",
            "defaultAudioLanguage": "vi"
        },
        "status": status_dict
    }

    print(f"\n========================================================")
    print(f"🚀 BẮT ĐẦU TẢI YOUTUBE SHORTS TỪ GITHUB ACTIONS:")
    print(f"📌 Tiêu đề: {title}")
    print(f"📢 Chế độ: {publish_log}")
    print(f"📁 Dung lượng: {round(vpath.stat().st_size / (1024*1024), 2)} MB")
    print(f"========================================================")

    media = MediaFileUpload(str(vpath), chunksize=10*1024*1024, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"   -> Đang tải: {int(status.progress() * 100)}%")

    yt_id = response.get("id")
    yt_url = f"https://youtube.com/shorts/{yt_id}"
    studio_url = f"https://studio.youtube.com/video/{yt_id}/edit"

    print(f"\n🎉 TẢI LÊN YOUTUBE SHORTS THÀNH CÔNG!")
    print(f"🆔 YouTube Video ID: {yt_id}")
    print(f"🔗 Link Shorts: {yt_url}")
    print(f"🛠️ Link chỉnh sửa Studio: {studio_url}")

    # TỰ ĐỘNG UPLOAD THUMBNAIL LÊN YOUTUBE
    thumb_path = None
    possible_thumbs = [
        Path("output") / video_id / f"thumbnail_{video_id}.jpg",
        Path("output") / video_id / "input" / f"thumbnail_{video_id}.jpg",
        Path("remotion-video/public") / f"thumbnail_{video_id}.jpg",
        vpath.parent / f"thumbnail_{video_id}.jpg",
        vpath.parent / "input" / f"thumbnail_{video_id}.jpg",
    ]
    for pt in possible_thumbs:
        if pt.exists():
            thumb_path = pt
            break

    if thumb_path:
        try:
            print(f"🖼️ Đang tự động upload Thumbnail lên YouTube: {thumb_path.name}...")
            thumb_media = MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
            youtube.thumbnails().set(
                videoId=yt_id,
                media_body=thumb_media
            ).execute()
            print("✅ ĐÃ UPLOAD THUMBNAIL LÊN YOUTUBE THÀNH CÔNG 100%!")
        except Exception as te:
            print(f"ℹ️ Không thể set thumbnail tự động qua API (Do chính sách Shorts API hoặc kênh chưa xác minh SĐT): {te}")
            print(f"👉 Bạn có thể click vào link Studio để upload thủ công trong 2 giây: {studio_url}")
    else:
        print("ℹ️ Không tìm thấy file thumbnail để upload kèm.")

    return {
        "youtube_id": yt_id,
        "youtube_url": yt_url,
        "studio_url": studio_url
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_youtube.py <video_path> <video_id>")
        sys.exit(1)
    vpath = sys.argv[1]
    vid = sys.argv[2]
    upload_short_to_youtube(vpath, vid)
