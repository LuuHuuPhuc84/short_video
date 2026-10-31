import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "remotion-video" / "public"
OUTPUT_DIR = BASE_DIR / "output"
PIPELINE_DIR = BASE_DIR / "pipeline"

from render_on_github import (
    run_git,
    check_video_ready_on_drive,
    download_video_from_drive,
    get_json_api,
    API_BASE,
    REPO_OWNER,
    REPO_NAME
)

def batch_render_via_github(video_ids, auto_cleanup=True, download_local=False):
    print("========================================================")
    print("🚀 BẮT ĐẦU BATCH RENDER SONG SONG TRÊN GITHUB ACTIONS")
    print(f"🎬 Danh sách video ({len(video_ids)}): {', '.join(video_ids)}")
    print("⚡ Công nghệ: Parallel Matrix Workers (Render cùng lúc tất cả video)")
    print(f"☁️ Điểm đến: Google Drive cá nhân & YouTube Shorts (Zero-Download: {'BẬT' if not download_local else 'TẢI VỀ'})")
    print("========================================================")

    # 1. Thu thập danh sách toàn bộ file cần đẩy lên cho tất cả video
    files_to_push = set()
    valid_videos = []

    for vid in video_ids:
        meta_path = PUBLIC_DIR / f"video_data_{vid}.json"
        if not meta_path.exists():
            meta_path = PUBLIC_DIR / f"{vid}.json"
        if not meta_path.exists():
            print(f"⚠️ Cảnh báo: Bỏ qua {vid} vì không tìm thấy file metadata.")
            continue

        # 0.1 QUY CHUẨN MỚI 1: Cập nhật kịch bản vào Excel
        try:
            from export_scripts_excel import export_video_to_excel
            export_video_to_excel(vid, project="short")
        except Exception as e:
            print(f"⚠️ Pre-render Excel {vid}: {e}")

        # 0.2 QUY CHUẨN MỚI 2: Copy toàn bộ hình ảnh / video B-roll đã cắt vào input/
        try:
            from pack_inputs import pack_video_input
            pack_video_input(vid)
        except Exception as e:
            print(f"⚠️ Pre-render Pack Input {vid}: {e}")

        # 0.3 QUY CHUẨN MỚI 3: Đồng bộ toàn bộ thư mục input/ lên Google Drive
        try:
            from sync_input_to_drive import sync_input_to_drive
            sync_input_to_drive(vid, project="short")
        except Exception as e:
            print(f"⚠️ Pre-render Sync Drive Input {vid}: {e}")

        # 0.4 Pre-render archive check
        try:
            from archive_render import archive_previous_renders
            archive_previous_renders(vid, target_filename=f"video_{vid}.mp4")
        except Exception as e:
            print(f"⚠️ Pre-render archive {vid}: {e}")

        valid_videos.append(vid)
        files_to_push.add(meta_path)

        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        audio_file = data.get("audioFile")
        if audio_file:
            ap = PUBLIC_DIR / audio_file
            if ap.exists():
                files_to_push.add(ap)

        for sc in data.get("scenes", []):
            bg = sc.get("image") or sc.get("backgroundVideo") or sc.get("video")
            if bg:
                bp = PUBLIC_DIR / bg
                if bp.exists():
                    files_to_push.add(bp)

        local_info = OUTPUT_DIR / vid / "info.json"
        if local_info.exists():
            try:
                with open(local_info, "r", encoding="utf-8") as f:
                    idata = json.load(f)
                ep_hashtag = f"#{vid}"
                cur_desc = idata.get("description", "")
                changed = False
                if ep_hashtag not in cur_desc and vid not in cur_desc:
                    if "#shorts" in cur_desc:
                        idata["description"] = cur_desc.replace("#shorts", f"{ep_hashtag} #shorts")
                    else:
                        idata["description"] = f"{cur_desc.strip()} {ep_hashtag}"
                    changed = True
                cur_tags = idata.get("tags", [])
                if not isinstance(cur_tags, list):
                    cur_tags = [str(cur_tags)] if cur_tags else []
                if vid not in cur_tags:
                    cur_tags.insert(0, vid)
                    changed = True
                idata["tags"] = cur_tags
                if changed:
                    with open(local_info, "w", encoding="utf-8") as f:
                        json.dump(idata, f, ensure_ascii=False, indent=2)
                    pub_inf = PUBLIC_DIR / f"info_{vid}.json"
                    with open(pub_inf, "w", encoding="utf-8") as f:
                        json.dump(idata, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ Kiểm tra hashtag {vid}: {e}")
            files_to_push.add(local_info)
        pub_info = PUBLIC_DIR / f"info_{vid}.json"
        if pub_info.exists():
            files_to_push.add(pub_info)

        # Đẩy kèm thumbnail để workflow upload lên YouTube
        thumb_pub = PUBLIC_DIR / f"thumbnail_{vid}.jpg"
        if thumb_pub.exists():
            files_to_push.add(thumb_pub)
        thumb_out = OUTPUT_DIR / vid / f"thumbnail_{vid}.jpg"
        if thumb_out.exists():
            files_to_push.add(thumb_out)

    if not valid_videos:
        print("❌ Không có video hợp lệ nào để render.")
        return False

    # Ghi manifest danh sách video cần render
    manifest_path = BASE_DIR / "batch_manifest.json"
    manifest_path.write_text(json.dumps(valid_videos), encoding="utf-8")
    files_to_push.add(manifest_path)

    print(f"\n📦 Tổng cộng {len(files_to_push)} files nguyên liệu cho {len(valid_videos)} video:")
    for fp in sorted(files_to_push):
        sz = round(fp.stat().st_size / (1024 * 1024), 2)
        print(f"   - {fp.name} ({sz} MB)")

    # 2. Đóng gói và push 1 lần duy nhất lên branch render-batch
    branch_name = "render-batch"
    print(f"\n📦 Đang đóng gói và đẩy tất cả lên nhánh: {branch_name}...")
    rel_paths = [str(fp.relative_to(BASE_DIR)).replace("\\", "/") for fp in files_to_push]
    run_git(["add", "-f"] + rel_paths)
    run_git(["commit", "-m", f"batch render: upload assets for {', '.join(valid_videos)}"])

    head_sha = run_git(["rev-parse", "HEAD"])
    print(f"🚀 Đang đẩy toàn bộ lên GitHub (Commit: {head_sha[:7]})...")
    run_git(["push", "-f", "origin", f"HEAD:refs/heads/{branch_name}"])
    print(f"✓ Đã đẩy nhánh {branch_name} lên GitHub thành công!")

    # 3. Trả lại HEAD sạch cho local
    run_git(["reset", "HEAD~1"])
    manifest_path.unlink(missing_ok=True)
    print(f"🔒 Local đã được giữ nguyên vẹn trên 'main'.")

    # 4. Theo dõi tiến trình song song trên Google Drive
    print(f"\n⏳ Đang đợi GitHub Actions chạy song song {len(valid_videos)} máy ảo...")
    print(f"🔗 Xem tiến trình tại: https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")

    start_time = time.time()
    completed_videos = set()
    total_needed = len(valid_videos)

    while len(completed_videos) < total_needed:
        time.sleep(12)
        elapsed = int(time.time() - start_time)

        # 1. Kiểm tra qua Drive nếu token còn hiệu lực
        for vid in valid_videos:
            if vid in completed_videos:
                continue

            drive_file = check_video_ready_on_drive(vid)
            if drive_file:
                print(f"\n✨ [{elapsed}s] ☁️ Video {vid} ĐÃ XONG TRÊN DRIVE & YOUTUBE: {drive_file['name']}!")
                if download_local:
                    out_target = OUTPUT_DIR / vid / f"video_{vid}.mp4"
                    ok = download_video_from_drive(vid, out_target)
                completed_videos.add(vid)
                print(f"🎉 Hoàn tất {len(completed_videos)}/{total_needed} video!")

        # 2. Kiểm tra trực tiếp qua GitHub Actions API
        runs_data = get_json_api(f"{API_BASE}/actions/runs?branch={branch_name}")
        if runs_data and runs_data.get("workflow_runs"):
            latest_run = runs_data["workflow_runs"][0]
            status = latest_run.get("status")
            conclusion = latest_run.get("conclusion")
            if status == "completed":
                print(f"\n✨ [{elapsed}s] 🚀 Workflow Batch Render trên GitHub Actions đã hoàn tất ({conclusion})!")
                completed_videos.update(valid_videos)
                break
            else:
                print(f"   [{elapsed}s] Trạng thái GitHub Actions: {status}...")

        if len(completed_videos) < total_needed:
            waiting = [v for v in valid_videos if v not in completed_videos]
            print(f"   [{elapsed}s] Đang chạy song song ({len(completed_videos)}/{total_needed} hoàn tất). Đang đợi: {', '.join(waiting)}...")

        if elapsed > 2400:  # Timeout 40 phút cho 9 video song song
            print("❌ Quá thời gian chờ (40 phút).")
            break

    # 5. Dọn dẹp trên GitHub
    if auto_cleanup:
        print(f"\n🧹 Đang xóa sạch nhánh tạm '{branch_name}' trên GitHub...")
        try:
            run_git(["push", "origin", "--delete", branch_name], check=False)
            run_git(["branch", "-D", branch_name], check=False)
            print("✨ ĐÃ XÓA SẠCH DẤU VẾT TRÊN GITHUB! Repo trở lại trạng thái sạch sẽ.")
        except Exception as e:
            print(f"⚠️ Dọn dẹp nhánh: {e}")

    print("\n========================================================")
    print("🏁 TỔNG KẾT BATCH RENDER SONG SONG:")
    for vid in valid_videos:
        status = "✅ THÀNH CÔNG" if vid in completed_videos else "❌ CHƯA XONG"
        print(f"   - {vid}: {status}")
    print("========================================================")
    return len(completed_videos) == total_needed

if __name__ == "__main__":
    raw_args = sys.argv[1:]
    download_flag = "--download" in raw_args
    vids = [a for a in raw_args if not a.startswith("--")]
    if not vids:
        vids = ["cntt_v1", "cntt_v2", "cntt_v3", "cntt_v4", "cntt_v5"]
    batch_render_via_github(vids, download_local=download_flag)
