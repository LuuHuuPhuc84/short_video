import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
import soundfile as sf
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# Ensure environment paths
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"E:\Programs\espeak-ng"
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"E:\Programs\espeak-ng\libespeak-ng.dll"
os.environ["ESPEAK_DATA_PATH"] = r"E:\Programs\espeak-ng\espeak-ng-data"
os.environ["PATH"] = r"E:\Programs\nodejs;E:\Programs\ffmpeg\bin;E:\Programs\espeak-ng;" + os.environ.get("PATH", "")

BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
PUBLIC_DIR = BASE_DIR / "remotion-video" / "public"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_text_for_tts(text):
    text = text.replace(":", ",")
    text = text.replace(";", ",")
    text = text.replace("—", ",")
    text = text.replace(" - ", ", ")
    text = text.replace("\"", "")
    text = text.replace("'", "")
    while ",," in text:
        text = text.replace(",,", ",")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()

def apply_micro_fade(wav, sample_rate, fade_in_ms=25, fade_out_ms=35):
    fade_in_len = int(sample_rate * fade_in_ms / 1000)
    fade_out_len = int(sample_rate * fade_out_ms / 1000)
    if len(wav) < fade_in_len + fade_out_len:
        return wav
    fade_in = np.linspace(0.0, 1.0, fade_in_len, dtype=np.float32)
    fade_out = np.linspace(1.0, 0.0, fade_out_len, dtype=np.float32)
    wav_out = wav.copy()
    wav_out[:fade_in_len] *= fade_in
    wav_out[-fade_out_len:] *= fade_out
    return wav_out

def apply_atempo(wav, sample_rate, speed=1.0):
    """Điều chỉnh tốc độ âm thanh (tempo) qua FFmpeg in-memory, giữ nguyên cao độ (pitch) và sample rate."""
    if not speed or abs(speed - 1.0) <= 0.01:
        return wav
    try:
        import io
        bio_in = io.BytesIO()
        sf.write(bio_in, wav, sample_rate, format='WAV')
        cmd = [
            r"E:\Programs\ffmpeg\bin\ffmpeg.exe",
            "-y",
            "-f", "wav",
            "-i", "pipe:0",
            "-filter:a", f"atempo={speed}",
            "-f", "wav",
            "pipe:1"
        ]
        res = subprocess.run(cmd, input=bio_in.getvalue(), capture_output=True, check=True)
        bio_out = io.BytesIO(res.stdout)
        out_wav, _ = sf.read(bio_out, dtype='float32')
        return out_wav
    except Exception as e:
        print(f"⚠️ Lỗi điều chỉnh atempo ({speed}): {e}, giữ nguyên wav gốc.")
        return wav

def master_audio_with_bgm(voice_path, output_path, total_duration_sec, bgm_path=None):
    if bgm_path is None:
        bgm_path = PUBLIC_DIR / "background_music.mp3"
    
    if not bgm_path.exists():
        print("⚠️ Không tìm thấy background_music.mp3, giữ file voiceover thuần.")
        return False
        
    print(f"🎵 Đang thực hiện Audio Mastering phòng thu: Sidechain Ducking + Broadcast Warmth EQ + EBU R128...")
    fade_out_start = max(0, total_duration_sec - 3.0)
    temp_mastered = voice_path.parent / f"temp_{voice_path.stem}_mastered.wav"
    
    cmd = [
        r"E:\Programs\ffmpeg\bin\ffmpeg.exe",
        "-y",
        "-i", str(voice_path),
        "-stream_loop", "-1",
        "-i", str(bgm_path),
        "-filter_complex",
        f"[0:a]equalizer=f=220:t=o:w=1:g=2,equalizer=f=6000:t=o:w=1:g=-2.5[voice_eq];"
        f"[1:a]volume=0.15,afade=t=out:st={fade_out_start:.2f}:d=3.0[bgm_fixed];"
        f"[voice_eq][bgm_fixed]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
        f"[mixed]loudnorm=I=-14:LRA=7:TP=-1.5[out]",
        "-map", "[out]",
        "-c:a", "pcm_s16le",
        "-ar", "48000",
        str(temp_mastered)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and temp_mastered.exists():
        import shutil
        shutil.move(str(temp_mastered), str(output_path))
        print("✓ Hoàn tất Master âm thanh đạt chuẩn phòng thu (Sidechain Ducking + Broadcast Warmth)!")
        return True
    else:
        print(f"⚠️ Lỗi hòa âm FFmpeg, giữ voiceover gốc: {res.stderr[:200]}")
        return False

def resolve_script_path(script_arg, job_id):
    if script_arg:
        p = Path(script_arg)
        if not p.is_absolute():
            p = PIPELINE_DIR / script_arg
        if p.exists():
            return p
        # Thử đường dẫn tương đối trực tiếp từ CWD
        cwd_p = Path(script_arg).resolve()
        if cwd_p.exists():
            return cwd_p

    if job_id:
        job_script = PIPELINE_DIR / f"script_{job_id}.json"
        if job_script.exists():
            return job_script

    default_script = PIPELINE_DIR / "script.json"
    return default_script

def make_video(
    script_file=None,
    output_filename=None,
    voice="Thiện Minh",
    speed=0.95,
    skip_audio=False,
    job_id=None,
    draft=False,
    local_render=False,
    prepare_only=False
):
    script_path = resolve_script_path(script_file, job_id)
    if not script_path or not script_path.exists():
        print(f"❌ Lỗi: Không tìm thấy kịch bản tại {script_path}")
        return

    print(f"📄 Nạp kịch bản từ: {script_path}")
    with open(script_path, "r", encoding="utf-8") as f:
        script_raw = json.load(f)

    if isinstance(script_raw, dict):
        episode = script_raw.get("episode", 1)
        title = script_raw.get("title", "TIẾNG CHUÔNG THỨC TỈNH, DẬP TẮT MỌI CƠN GIẬN")
        subtitle = script_raw.get("subtitle", "BÍ QUYẾT LÀM CHỦ CẢM XÚC - THÍCH NHẤT HẠNH")
        book = script_raw.get("book", "")
        author = script_raw.get("author", "")
        chapter = script_raw.get("chapter", "")
        scenes = script_raw.get("scenes", [])
        if "speed" in script_raw:
            speed = script_raw["speed"]
        showHeroHeader = script_raw.get("showHeroHeader", False)
        showTitleHook = script_raw.get("showTitleHook", True)
        titleHook = script_raw.get("titleHook", "")
    else:
        episode = 1
        title = "TIẾNG CHUÔNG THỨC TỈNH, DẬP TẮT MỌI CƠN GIẬN"
        subtitle = "BÍ QUYẾT LÀM CHỦ CẢM XÚC - THÍCH NHẤT HẠNH"
        book = ""
        author = ""
        chapter = ""
        scenes = script_raw
        showHeroHeader = False
        showTitleHook = True
        titleHook = ""

    # Tự động gán Title Hook 3-5 từ đắt giá làm Thumbnail Shorts nếu chưa chỉ định rõ
    if not titleHook:
        if scenes and scenes[0].get("highlight"):
            titleHook = scenes[0].get("highlight")
        else:
            titleHook = title.split(",")[0].strip()

    fps = 30
    
    # Định danh các file theo Job ID để tránh xung đột giữa nhiều chat/tiến trình
    suffix = f"_{job_id}" if job_id else ""
    audio_file_name = f"voiceover{suffix}.wav"
    meta_file_name = f"video_data{suffix}.json"

    meta_out_path = PUBLIC_DIR / meta_file_name
    audio_out_path = PUBLIC_DIR / audio_file_name

    if not output_filename:
        output_filename = f"video_{job_id}.mp4" if job_id else "video_viral.mp4"
    if not output_filename.endswith(".mp4"):
        output_filename += ".mp4"

    if skip_audio and meta_out_path.exists() and audio_out_path.exists():
        print(f"=== BỎ QUA BƯỚC SINH ÂM THANH, CẬP NHẬT METADATA VÀ RENDER ({meta_file_name}) ===")
        with open(meta_out_path, "r", encoding="utf-8") as f:
            video_data = json.load(f)
        video_data["episode"] = episode
        video_data["title"] = title
        video_data["titleHook"] = titleHook
        video_data["showTitleHook"] = showTitleHook
        video_data["subtitle"] = subtitle
        video_data["audioFile"] = audio_file_name
        video_data["showHeroHeader"] = showHeroHeader
        if book: video_data["book"] = book
        if author: video_data["author"] = author
        if chapter: video_data["chapter"] = chapter
        for i, sc in enumerate(video_data.get("scenes", [])):
            if i < len(scenes):
                sc["tag"] = scenes[i].get("tag", "")
                sc["highlight"] = scenes[i].get("highlight", "")
                if "image" in scenes[i]:
                    sc["image"] = scenes[i]["image"]
        with open(meta_out_path, "w", encoding="utf-8") as f:
            json.dump(video_data, f, ensure_ascii=False, indent=2)
    else:
        print(f"\n=== BƯỚC 1: TẠO GIỌNG ĐỌC AI CHIÊM NGHIỆM VIENEU v3 TURBO ({voice} - Speed {speed}) ===")
        print(f"-> File audio đích: {audio_out_path.name}")
        import vieneu
        tts = vieneu.Vieneu(mode="v3turbo")

        sample_rate = tts.sample_rate

        # Tự động nạp preset nếu là giọng clone (ví dụ laytutritueconhan)
        active_voice = voice
        voice_preset_turbo_file = PIPELINE_DIR / "voices" / str(voice) / "voice_preset_turbo.json"
        if voice_preset_turbo_file.exists():
            try:
                with open(voice_preset_turbo_file, "r", encoding="utf-8") as f:
                    v_cfg = json.load(f)
                active_voice = v_cfg.get("preset", active_voice)
                print(f"🎙️ Đã nạp thành công preset giọng clone v3turbo 48kHz: {voice}")
            except Exception as e:
                print(f"⚠️ Không đọc được preset {voice}: {e}")

        combined_audio = []
        # Khoảng nghỉ tự nhiên 0.28s tạo nhịp thở sâu lắng, đệm nhạc piano
        gap_silence = np.zeros(int(sample_rate * 0.28), dtype=np.float32)
        output_metadata = []

        for idx, item in enumerate(scenes):
            text = item["text"]
            text_clean = sanitize_text_for_tts(text)
            print(f"[{idx+1}/{len(scenes)}] Đang đọc (đã tối ưu dấu câu): {text_clean[:35]}...")
            wav = tts.infer(text=text_clean, voice=active_voice)

            # Điều chỉnh nhịp đọc (tempo) nếu speed != 1.0 (chuẩn 0.95 giữ nguyên cao độ)
            if speed and abs(speed - 1.0) > 0.01:
                wav = apply_atempo(wav, sample_rate, speed)

            # Áp dụng Micro-fade khử giật, khử tiếng khựng ngắt cụt
            wav_smooth = apply_micro_fade(wav, sample_rate, fade_in_ms=25, fade_out_ms=35)
            
            start_frame = int(round(len(combined_audio) / sample_rate * fps))
            combined_audio.extend(wav_smooth)
            end_frame = int(round(len(combined_audio) / sample_rate * fps))
            
            output_metadata.append({
                "scene": item["scene"],
                "tag": item.get("tag", ""),
                "text": item["text"],
                "highlight": item.get("highlight", ""),
                "image": item.get("image", f"scene{idx+1}.jpg"),
                "startFrame": start_frame,
                "durationInFrames": end_frame - start_frame
            })
            combined_audio.extend(gap_silence)

        total_duration_sec = len(combined_audio) / sample_rate
        total_frames = int(round(total_duration_sec * fps))

        # Lưu file thô tạm để đưa vào bộ trộn âm Sidechain Ducking
        raw_audio_temp = PUBLIC_DIR / f"raw_temp_{audio_file_name}"
        sf.write(str(raw_audio_temp), np.array(combined_audio, dtype=np.float32), sample_rate)

        # Tự động chọn nhạc nền phù hợp với tần số cảm xúc kịch bản từ kho 18 bài No-Copyright
        from music_selector import select_music_for_content
        full_script_text = " ".join([item["text"] for item in scenes])
        bgm_res = select_music_for_content(title=title, script_text=full_script_text)
        
        if bgm_res and bgm_res.get("file_path") and bgm_res["file_path"].exists():
            selected_bgm_path = bgm_res["file_path"]
            chosen_track_name = bgm_res["track"]["name"]
            print(f"🎵 Nhạc nền tự động (Mood Match): {chosen_track_name} ({bgm_res['track']['file']})")
        else:
            selected_bgm_path = PUBLIC_DIR / "background_music.mp3"
            chosen_track_name = "On A Piano Cloud"
            print(f"🎵 Nhạc nền mặc định: {chosen_track_name}")

        # Thực hiện hòa âm phòng thu: BGM volume=0.15 (không Sidechain) + EQ Ấm 220Hz/6000Hz + EBU R128 (-14 LUFS)
        success_master = master_audio_with_bgm(raw_audio_temp, audio_out_path, total_duration_sec, bgm_path=selected_bgm_path)
        if not success_master:
            sf.write(str(audio_out_path), np.array(combined_audio, dtype=np.float32), sample_rate)
        if raw_audio_temp.exists():
            try:
                raw_audio_temp.unlink()
            except Exception:
                pass

        # Lưu metadata độc lập theo job
        video_data = {
            "episode": episode,
            "title": title,
            "titleHook": titleHook,
            "showTitleHook": showTitleHook,
            "subtitle": subtitle,
            "book": book,
            "author": author,
            "chapter": chapter,
            "showHeroHeader": showHeroHeader,
            "fps": fps,
            "width": 1080,
            "height": 1920,
            "durationInFrames": total_frames,
            "audioFile": audio_file_name,
            "music": chosen_track_name,
            "musicFile": selected_bgm_path.name,
            "scenes": output_metadata
        }

        with open(meta_out_path, "w", encoding="utf-8") as f:
            json.dump(video_data, f, ensure_ascii=False, indent=2)

        print(f"-> Hoàn tất âm thanh & hòa âm: {total_duration_sec:.2f}s ({total_frames} frames)")

    import datetime

    # Xác định video_id và thư mục con riêng biệt trong output/
    video_id = script_raw.get("id") or job_id
    if not video_id:
        video_id = Path(output_filename).stem.replace("video_", "").split("_")[0]
        if not video_id:
            video_id = "viral_short"

    target_folder = OUTPUT_DIR / str(video_id)
    target_folder.mkdir(parents=True, exist_ok=True)

    out_video_path = target_folder / Path(output_filename).name

    # Chuẩn bị file info.json chứa tiêu đề, mô tả, hashtag trước khi render
    info_file_path = target_folder / "info.json"
    existing_info = {}
    if info_file_path.exists():
        try:
            with open(info_file_path, "r", encoding="utf-8") as f:
                existing_info = json.load(f)
        except Exception:
            existing_info = {}

    raw_desc = existing_info.get("description", f"{title}. {subtitle}")
    ep_hashtag = f"#{video_id}"
    if ep_hashtag not in raw_desc and video_id not in raw_desc:
        if "#shorts" in raw_desc:
            final_desc = raw_desc.replace("#shorts", f"{ep_hashtag} #shorts")
        else:
            final_desc = f"{raw_desc.strip()} {ep_hashtag}"
    else:
        final_desc = raw_desc

    raw_tags = existing_info.get("tags", ["Nửa Chén Trà", "Shorts", "nhìn sâu để sống nhẹ", "bài học cuộc sống"])
    if not isinstance(raw_tags, list):
        raw_tags = [str(raw_tags)] if raw_tags else []
    if video_id not in raw_tags:
        raw_tags.insert(0, video_id)

    info_data = {
        "id": video_id,
        "title": title,
        "subtitle": subtitle,
        "book": book if book else existing_info.get("book", ""),
        "author": author if author else existing_info.get("author", ""),
        "chapter": chapter if chapter else existing_info.get("chapter", ""),
        "description": final_desc,
        "tags": raw_tags,
        "final_video_file": Path(output_filename).name,
        "music": chosen_track_name,
        "music_file": selected_bgm_path.name,
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if "schedule" in existing_info:
        info_data["schedule"] = existing_info["schedule"]
    if "youtube_url" in existing_info:
        info_data["youtube_url"] = existing_info["youtube_url"]
    if "platforms" in existing_info:
        info_data["platforms"] = existing_info["platforms"]

    with open(info_file_path, "w", encoding="utf-8") as f:
        json.dump(info_data, f, ensure_ascii=False, indent=2)

    # ── QUY CHUẨN MỚI 1: Tự động cập nhật kịch bản vào Excel TRƯỚC KHI RENDER ──
    print(f"\n📋 [BƯỚC 1 PRE-RENDER] Cập nhật kịch bản vào Excel để duyệt...")
    try:
        from export_scripts_excel import export_video_to_excel
        xlsx_path = export_video_to_excel(video_id, project="short")
        print(f"📊 Kịch bản đã được cập nhật vào Excel:\n   {xlsx_path}")
    except Exception as e:
        print(f"⚠️ Xuất Excel: {e}")

    # ── QUY CHUẨN MỚI 2: Copy toàn bộ ảnh/video B-roll đã cắt vào output/{video_id}/input/ ──
    print(f"\n📦 [BƯỚC 2 PRE-RENDER] Copy toàn bộ hình ảnh / video B-roll đã cắt vào thư mục duyệt input/...")
    try:
        from pack_inputs import pack_video_input
        pack_video_input(video_id)
        print(f"✓ Toàn bộ nguyên liệu đã sẵn sàng tại: {target_folder / 'input'}")
    except Exception as e:
        print(f"⚠️ Đóng gói input: {e}")

    # Nếu người dùng chỉ muốn chuẩn bị để duyệt hoặc dừng lại chờ duyệt
    if prepare_only:
        print("\n" + "="*66)
        print(f"⏸️ [DỪNG LẠI ĐỂ DUYỆT TRƯỚC KHI RENDER: {video_id}]")
        print(f"1. Vui lòng mở file 'scripts_short_video.xlsx' để duyệt hoặc sửa lời thoại.")
        print(f"2. Toàn bộ hình ảnh / video B-roll đã cắt đã lưu trong: output/{video_id}/input/")
        print(f"3. Sau khi duyệt xong, hãy xác nhận để hệ thống tải thư mục input/ lên Google Drive và render!")
        print("="*66 + "\n")
        return

    # ── QUY CHUẨN MỚI 3: Copy toàn bộ thư mục input/ lên Google Drive sau khi duyệt ──
    print(f"\n☁️ [BƯỚC 3 POST-APPROVAL] Đồng bộ toàn bộ thư mục input/ lên Google Drive...")
    try:
        from sync_input_to_drive import sync_input_to_drive
        sync_input_to_drive(video_id, project="short")
    except Exception as e:
        print(f"⚠️ Đồng bộ Drive: {e}")

    # ── Chuẩn hóa tiền xử lý: Đổi tên file render cũ trên Local & Drive ───────
    try:
        from archive_render import archive_previous_renders
        archive_previous_renders(video_id, target_filename=output_filename)
    except Exception as e:
        print(f"⚠️ Pre-render archive: {e}")

    # Render mặc định qua GitHub Actions Cloud Worker (Miễn phí, 0% CPU/GPU máy)
    use_local_render = local_render or draft
    if not use_local_render:
        print(f"\n=== BƯỚC 2: RENDER QUA GITHUB ACTIONS CLOUD WORKER (FULL HD 1080x1920) ===")
        print(f"⚡ Đang điều phối máy chủ GitHub Actions render video {video_id}...")
        from pipeline.render_on_github import render_short_video_via_github
        render_ok = render_short_video_via_github(video_id)
        if not render_ok:
            print("⚠️ Render trên GitHub Actions không thành công, tự động chuyển sang render tại Local...")
            use_local_render = True

    if use_local_render:
        if draft:
            out_stem = Path(output_filename).stem
            if not ("draft" in out_stem.lower() or "preview" in out_stem.lower() or "360p" in out_stem.lower()):
                output_filename = f"{out_stem}_preview_360p.mp4"
            print(f"\n=== BƯỚC 2: RENDER BẢN NHÁP DUYỆT TRƯỚC (360P DRAFT - SIÊU TỐC) ===")
            print(f"⚡ Đang áp dụng tỷ lệ thu nhỏ 360p dọc (scale=1/3, 360x640) để render duyệt trước cực nhanh trên máy không GPU...")
        else:
            print(f"\n=== BƯỚC 2: RENDER LOCAL REMOTION SANG MP4 (1080x1920) ===")

        out_video_path = target_folder / Path(output_filename).name

        # Xóa các bản nháp/bản cũ khác trong thư mục nếu đang render bản Full HD chính thức
        if not draft:
            for old_file in target_folder.glob("*.mp4"):
                if old_file.name != out_video_path.name:
                    try:
                        old_file.unlink()
                        print(f"🗑 Đã xóa phiên bản cũ để giải phóng bộ nhớ: {old_file.name}")
                    except Exception as e:
                        print(f"⚠️ Không thể xóa {old_file.name}: {e}")

        cmd = [
            "npx.cmd",
            "remotion",
            "render",
            "TiktokShort",
            str(out_video_path),
            f"--props={str(meta_out_path)}"
        ]

        if draft:
            cmd.append("--scale=0.33333334")

        print(f"-> Thư mục lưu trữ: {target_folder}")
        print(f"-> Thực thi: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=str(BASE_DIR / "remotion-video"), check=True, shell=True)

    # Tự động tạo / cập nhật file info.json chứa tiêu đề, mô tả, thông số video
    file_size_mb = round(out_video_path.stat().st_size / (1024 * 1024), 2) if out_video_path.exists() else 0
    info_file_path = target_folder / "info.json"
    
    existing_info = {}
    if info_file_path.exists():
        try:
            with open(info_file_path, "r", encoding="utf-8") as f:
                existing_info = json.load(f)
        except Exception:
            existing_info = {}

    info_data = {
        "id": video_id,
        "title": title,
        "subtitle": subtitle,
        "book": book if book else existing_info.get("book", ""),
        "author": author if author else existing_info.get("author", ""),
        "chapter": chapter if chapter else existing_info.get("chapter", ""),
        "description": existing_info.get("description", f"{title}. {subtitle}"),
        "tags": existing_info.get("tags", ["Nửa Chén Trà", "Shorts", "nhìn sâu để sống nhẹ", "bài học cuộc sống"]),
        "final_video_file": out_video_path.name,
        "file_size_mb": file_size_mb,
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if "schedule" in existing_info:
        info_data["schedule"] = existing_info["schedule"]
    if "youtube_url" in existing_info:
        info_data["youtube_url"] = existing_info["youtube_url"]
    if "platforms" in existing_info:
        info_data["platforms"] = existing_info["platforms"]

    with open(info_file_path, "w", encoding="utf-8") as f:
        json.dump(info_data, f, ensure_ascii=False, indent=2)

    try:
        from pack_inputs import pack_video_input
        pack_video_input(video_id)
    except Exception as e:
        print(f"⚠️ Đóng gói input: {e}")

    # ── Tự động xuất / cập nhật kịch bản vào Excel ──────────────────────────
    try:
        from export_scripts_excel import export_video_to_excel
        xlsx_path = export_video_to_excel(video_id, project="short")
        print(f"📊 Kịch bản đã cập nhật vào Excel:\n{xlsx_path}")
    except Exception as e:
        print(f"⚠️ Xuất Excel: {e}")

    print(f"\n✅ THÀNH CÔNG! Video đã xuất tại:\n{out_video_path}")
    print(f"📄 File thông tin (tiêu đề, mô tả) đã lưu tại:\n{info_file_path}")

def parse_args():
    parser = argparse.ArgumentParser(description="Tạo Short Video tự động với VieNeu TTS & Remotion")
    parser.add_argument("positional_output", nargs="?", default=None, help="Tên file video đầu ra (tương thích ngược)")
    parser.add_argument("-j", "--job", dest="job", default=None, help="Job ID / Session ID định danh để render độc lập không xung đột")
    parser.add_argument("-s", "--script", dest="script", default=None, help="Đường dẫn file kịch bản (mặc định: script_<job>.json hoặc script.json)")
    parser.add_argument("-o", "--output", dest="output", default=None, help="Tên video đầu ra (.mp4)")
    parser.add_argument("--voice", default="Thiện Minh", help="Tên giọng đọc VieNeu (mặc định: Thiện Minh)")
    parser.add_argument("--speed", type=float, default=0.95, help="Tốc độ đọc (mặc định: 0.95)")
    parser.add_argument("--skip-audio", action="store_true", help="Bỏ qua sinh âm thanh nếu file audio đã tồn tại")
    parser.add_argument("--draft", "--preview", "--360p", action="store_true", dest="draft", help="Render bản nháp 360p siêu nhẹ để duyệt trước")
    parser.add_argument("--local", action="store_true", dest="local_render", help="Render trực tiếp trên máy Local (mặc định: Render qua GitHub Actions Cloud Worker)")
    parser.add_argument("--prepare-only", "--no-render", action="store_true", dest="prepare_only", help="Chỉ cập nhật Excel và chuẩn bị nguyên liệu trong input/ để duyệt, không render")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Ưu tiên --output, sau đó đến positional argument, cuối cùng fallback theo make_video
    final_output = args.output or args.positional_output

    make_video(
        script_file=args.script,
        output_filename=final_output,
        voice=args.voice,
        speed=args.speed,
        skip_audio=args.skip_audio,
        job_id=args.job,
        draft=args.draft,
        local_render=args.local_render,
        prepare_only=args.prepare_only
    )
