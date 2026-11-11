# -*- coding: utf-8 -*-
"""
pipeline/cli.py
===============
Giao diện dòng lệnh trung tâm (Unified CLI) cho dự án Short Video.
Điều phối 10 module độc lập theo nhu cầu chính xác của người dùng:

1. Render:   python pipeline/cli.py render <id> [--local]
2. Drive:    python pipeline/cli.py drive <id> [--input]
3. YouTube:  python pipeline/cli.py youtube <id> [--schedule "YYYY-MM-DD HH:MM"] [--draft]
4. Schedule: python pipeline/cli.py schedule <id> "YYYY-MM-DD HH:MM" (hoặc batch)
5. Music:    python pipeline/cli.py music {list|suggest|swap} [...]
6. Voice:    python pipeline/cli.py voice {gen|align} <id> [...]
7. B-roll:   python pipeline/cli.py broll {inspect|swap} <id> [...]
8. Thumb:    python pipeline/cli.py thumb {make} <id> [...]
9. Cloud:    python pipeline/cli.py cloud {batch|single|status} [...]
10. Doctor:  python pipeline/cli.py doctor
11. Assets:  python pipeline/cli.py assets {check|music|thumb|pack|sync} [...]
12. Backup:  python pipeline/cli.py backup
13. Flow:    python pipeline/cli.py flow {check|launch|single|batch|prompt} [...]
14. Toàn bộ: python pipeline/cli.py all <id>
"""

import sys
import argparse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"

def main():
    parser = argparse.ArgumentParser(description="Quản lý sản xuất Short Video - Nửa Chén Trà (Unified CLI)")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh cần thực hiện")

    # 1. Render
    p_render = subparsers.add_parser("render", help="Chỉ Render video (Cloud hoặc Local)")
    p_render.add_argument("video_id", nargs="+", help="Mã video (ví dụ: nct_v21), có thể truyền nhiều ID")
    p_render.add_argument("--local", action="store_true", help="Render tại máy thay vì Cloud")

    # 2. Drive
    p_drive = subparsers.add_parser("drive", help="Tải video hoặc input lên Google Drive")
    p_drive.add_argument("video_id", help="Mã video (ví dụ: nct_v21)")
    p_drive.add_argument("--input", action="store_true", help="Tải cả thư mục nguyên liệu input/")

    # 3. YouTube
    p_yt = subparsers.add_parser("youtube", help="Xuất bản video lên YouTube Shorts")
    p_yt.add_argument("video_id", help="Mã video (ví dụ: nct_v21)")
    p_yt.add_argument("--schedule", help="Thời gian hẹn giờ (YYYY-MM-DD HH:MM)")
    p_yt.add_argument("--draft", action="store_true", help="Lưu dưới dạng Private nháp")

    # 4. Schedule (Reschedule siêu tốc)
    p_sched = subparsers.add_parser("schedule", help="Đổi lịch phát sóng siêu tốc hoặc kéo lịch từ YouTube về Excel")
    p_sched.add_argument("target", help="Mã video (nct_v21), 'batch', hoặc 'pull' / 'sync'")
    p_sched.add_argument("time", nargs="?", default="", help="Thời gian phát sóng YYYY-MM-DD HH:MM hoặc mã video khi pull")
    p_sched.add_argument("videos", nargs="*", default=[], help="Danh sách video khi dùng lệnh batch")

    # 5. Music (Quản trị & Fast Music Swap)
    p_music = subparsers.add_parser("music", help="Quản trị 18 bài nhạc No-Copyright & Fast Music Swap 1s")
    p_music.add_argument("action", choices=["list", "suggest", "swap"], help="Hành động (list, suggest, swap)")
    p_music.add_argument("target", nargs="?", default="", help="video_id hoặc câu thoại phân tích")
    p_music.add_argument("--track", help="Tên hoặc ID bài nhạc khi swap")

    # 6. Voice (VieNeu TTS & Whisper Karaoke)
    p_voice = subparsers.add_parser("voice", help="Sinh giọng đọc VieNeu v3 Turbo & Whisper Karaoke Text Lock")
    p_voice.add_argument("action", choices=["gen", "align"], help="Hành động (gen, align)")
    p_voice.add_argument("video_id", help="Mã video")
    p_voice.add_argument("--voice", default="Thiện Minh", help="Tên giọng đọc")
    p_voice.add_argument("--speed", type=float, default=0.88, help="Tốc độ đọc (0.88)")
    p_voice.add_argument("--pause", type=float, default=0.35, help="Khoảng thở (0.35s)")

    # 7. B-roll (Thẩm định, Fast Scene Swap & Safe Tracker)
    p_broll = subparsers.add_parser("broll", help="Thẩm định B-roll, Đổi cảnh siêu tốc 1s & Sổ cái phân đoạn an toàn")
    p_broll.add_argument("action", choices=["inspect", "swap", "tracker"], help="Hành động (inspect, swap, tracker)")
    p_broll.add_argument("video_id", nargs="?", default="", help="Mã video (nếu dùng inspect/swap)")
    p_broll.add_argument("--scene", type=int, help="Số thứ tự cảnh (1, 2, 3...) khi swap")
    p_broll.add_argument("--clip", help="Đường dẫn hoặc tên clip mới khi swap")

    # 8. Thumb (Thumbnail Safe Zone Studio)
    p_thumb = subparsers.add_parser("thumb", help="Tạo Thumbnail 1080x1920 Safe Zone & Cover Frame 1s đầu")
    p_thumb.add_argument("action", choices=["make"], help="Hành động (make)")
    p_thumb.add_argument("video_id", help="Mã video")
    p_thumb.add_argument("--hook", help="Câu tiêu đề Hook nổi bật trên Thumbnail")
    p_thumb.add_argument("--image", help="Đường dẫn ảnh nền tùy chọn")

    # 9. Cloud (GitHub Actions Worker)
    p_cloud = subparsers.add_parser("cloud", help="Điều phối Cloud Render Worker trên GitHub Actions")
    p_cloud.add_argument("action", choices=["batch", "single", "status"], help="Hành động (batch, single, status)")
    p_cloud.add_argument("videos", nargs="*", default=[], help="Danh sách video_id khi render batch/single")

    # 10. Doctor (System Health)
    subparsers.add_parser("doctor", help="Khám sức khỏe toàn diện hệ thống (Token Drive, YouTube, GitHub, Disk)")

    # 11. Assets Hub
    p_assets = subparsers.add_parser("assets", help="Quản trị kho Assets Hub")
    p_assets.add_argument("action", choices=["check", "music", "thumb", "pack", "ingest", "sync", "purge"], help="Hành động")
    p_assets.add_argument("target", nargs="?", default="", help="video_id hoặc từ khóa")

    # 12. Backup
    subparsers.add_parser("backup", help="Sao lưu toàn bộ hệ thống lên Google Drive")

    # 13. Flow (Google Flow Image Automation)
    p_flow = subparsers.add_parser("flow", help="Sinh ảnh AI Google Flow 1x (Dùng chung Short 9:16 & Long 16:9)")
    p_flow.add_argument("action", choices=["check", "launch", "single", "batch", "prompt"], help="Hành động (check, launch, single, batch, prompt)")
    p_flow.add_argument("video_id", nargs="?", default="", help="Mã video (ví dụ: nct_v66)")
    p_flow.add_argument("scene_num", nargs="?", type=int, default=1, help="Số thứ tự cảnh (1, 2, 3...)")
    p_flow.add_argument("--project", default="short", choices=["short", "long"], help="Dự án: short (9:16) hoặc long (16:9)")
    p_flow.add_argument("--prompt", help="Prompt tùy chỉnh")
    p_flow.add_argument("--from-scene", type=int, default=1, help="Cảnh bắt đầu khi chạy batch")
    p_flow.add_argument("--to-scene", type=int, default=None, help="Cảnh kết thúc khi chạy batch")

    # 14. All
    p_all = subparsers.add_parser("all", help="Quy trình trọn gói: Render -> Drive -> YouTube")
    p_all.add_argument("video_id", help="Mã video")
    p_all.add_argument("--local", action="store_true", help="Render local")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    vid = getattr(args, "video_id", "")

    if args.command == "render":
        from core_render import render_video
        ids = args.video_id if isinstance(args.video_id, list) else [args.video_id]
        for v in ids:
            render_video(v, mode="local" if args.local else "cloud")

    elif args.command == "drive":
        from core_drive import upload_video_to_drive, upload_input_to_drive
        if args.input:
            upload_input_to_drive(vid)
        else:
            upload_video_to_drive(vid)

    elif args.command == "youtube":
        from core_youtube import publish_video_to_youtube
        publish_video_to_youtube(vid, schedule=args.schedule, draft=args.draft)

    elif args.command == "schedule":
        from core_schedule import schedule_single_video, schedule_batch_videos, pull_schedule_from_youtube
        target_lower = args.target.lower()
        if target_lower in ["pull", "sync"]:
            target_vid = args.time if args.time else None
            pull_schedule_from_youtube(target_video_id=target_vid)
        elif target_lower == "batch":
            if not args.videos:
                print("❌ Cần truyền danh sách video: python pipeline/cli.py schedule batch 'YYYY-MM-DD HH:MM' vid1 vid2...")
                sys.exit(1)
            schedule_batch_videos(args.videos, args.time)
        else:
            if not args.time:
                print("❌ Cần truyền thời gian: python pipeline/cli.py schedule <video_id> 'YYYY-MM-DD HH:MM'")
                sys.exit(1)
            schedule_single_video(args.target, args.time)

    elif args.command == "music":
        from core_music import list_tracks, suggest_music, swap_music
        if args.action == "list":
            list_tracks()
        elif args.action == "suggest":
            suggest_music(args.target or "an trú tĩnh lặng")
        elif args.action == "swap":
            if not args.target or not args.track:
                print("❌ Cần truyền video_id và --track: python pipeline/cli.py music swap <video_id> --track <track_name>")
                sys.exit(1)
            swap_music(args.target, args.track, project="short")

    elif args.command == "voice":
        from core_voice import generate_voice, align_subtitles_only
        if args.action == "gen":
            generate_voice(args.video_id, voice=args.voice, speed=args.speed, breath_pause=args.pause, project="short")
        elif args.action == "align":
            align_subtitles_only(args.video_id)

    elif args.command == "broll":
        from core_broll import inspect_broll, swap_broll_scene
        if args.action == "inspect":
            if not args.video_id:
                print("❌ Cần truyền video_id: python pipeline/cli.py broll inspect <video_id>")
                sys.exit(1)
            inspect_broll(args.video_id)
        elif args.action == "tracker":
            from broll_tracker import print_tracker_report
            print_tracker_report()
        elif args.action == "swap":
            if not args.video_id or not args.scene or not args.clip:
                print("❌ Cần truyền đầy đủ: python pipeline/cli.py broll swap <video_id> --scene <n> --clip <path>")
                sys.exit(1)
            swap_broll_scene(args.video_id, args.scene, args.clip, project="short")

    elif args.command == "thumb":
        from core_thumb import generate_thumbnail
        if args.action == "make":
            generate_thumbnail(args.video_id, title_hook=args.hook, image_source=getattr(args, "image", None), project_type="short")

    elif args.command == "cloud":
        from core_cloud import render_batch, render_single, get_cloud_status
        if args.action == "batch":
            if not args.videos:
                print("❌ Cần truyền danh sách video: python pipeline/cli.py cloud batch vid1 vid2...")
                sys.exit(1)
            render_batch(args.videos)
        elif args.action == "single":
            if not args.videos:
                print("❌ Cần truyền video_id: python pipeline/cli.py cloud single <video_id>")
                sys.exit(1)
            render_single(args.videos[0])
        elif args.action == "status":
            get_cloud_status()

    elif args.command == "doctor":
        from core_doctor import run_doctor
        run_doctor()

    elif args.command == "assets":
        from core_assets import check_inventory, select_music, generate_thumbnail, pack_inputs, ingest_mobile, sync_assets_to_drive, purge_local_videos
        if args.action == "check":
            check_inventory()
        elif args.action == "ingest":
            ingest_mobile()
        elif args.action == "sync":
            sync_assets_to_drive()
        elif args.action == "purge":
            purge_local_videos()
        elif args.action == "music":
            select_music(args.target or "an trú tĩnh lặng")
        elif args.action == "thumb":
            generate_thumbnail(args.target)
        elif args.action == "pack":
            pack_inputs(args.target)

    elif args.command == "all":
        from core_render import render_video
        from core_drive import upload_video_to_drive, upload_input_to_drive
        from core_youtube import publish_video_to_youtube

        print(f"🚀 BẮT ĐẦU QUY TRÌNH TOÀN DIỆN CHO: {vid}")
        ok = render_video(vid, mode="local" if args.local else "cloud")
        if not ok:
            print("❌ Render thất bại. Dừng quy trình.")
            sys.exit(1)
        upload_input_to_drive(vid)
        upload_video_to_drive(vid)
        publish_video_to_youtube(vid)
        print(f"🏁 HOÀN TẤT TOÀN BỘ CHO: {vid}")

    elif args.command == "backup":
        from backup_system_to_drive import backup_all
        backup_all()

    elif args.command == "flow":
        from core_flow import (
            check_flow_status, launch_flow_browser,
            generate_scene_image, generate_batch_scenes,
            create_flow_prompts_file
        )
        if args.action == "check":
            st = check_flow_status()
            print("=======================================================")
            print("🔍 KIỂM TRA KẾT NỐI GOOGLE FLOW (PORT 9222):")
            print(f"  - Trình duyệt Chrome debug: {'✅ Đang chạy' if st['browser_running'] else '❌ Chưa bật'}")
            print(f"  - Tab Google Flow: {'✅ Đã tìm thấy' if st['tab_found'] else '❌ Chưa thấy'}")
            if st['url']:
                print(f"  - URL: {st['url']}")
            print(f"  - Số ảnh hiện có trong dự án: {st['image_count']}")
            print(f"  - Thông báo: {st['message']}")
            print("=======================================================")
        elif args.action == "launch":
            launch_flow_browser()
        elif args.action == "prompt":
            if not args.video_id:
                print("❌ Cần truyền video_id: python pipeline/cli.py flow prompt <video_id> [--project {short,long}]")
                sys.exit(1)
            create_flow_prompts_file(args.video_id, project=args.project, force=True)
        elif args.action == "single":
            if not args.video_id:
                print("❌ Cần truyền video_id: python pipeline/cli.py flow single <video_id> [scene_num] [--project {short,long}]")
                sys.exit(1)
            generate_scene_image(args.video_id, args.scene_num, project=args.project, custom_prompt=args.prompt)
        elif args.action == "batch":
            if not args.video_id:
                print("❌ Cần truyền video_id: python pipeline/cli.py flow batch <video_id> [--project {short,long}]")
                sys.exit(1)
            generate_batch_scenes(args.video_id, project=args.project, start_scene=args.from_scene, end_scene=args.to_scene)

if __name__ == "__main__":
    main()
