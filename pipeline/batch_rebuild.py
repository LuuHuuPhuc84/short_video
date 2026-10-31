# -*- coding: utf-8 -*-
"""
pipeline/batch_rebuild.py
=========================
Module CHUẨN HÓA DÙNG CHUNG (General Engine):
Tạo lại giọng đọc VieNeu-TTS v3 Turbo (Thiện Minh 0.88, nghỉ thở 0.35s),
TỰ ĐỘNG CHỌN NHẠC NỀN THEO CẢM XÚC KỊCH BẢN qua music_selector (kho 18 bài No-Copyright),
Hòa âm chuẩn mới (volume=0.15, không Sidechain Ducking, EQ ấm 220Hz / 6000Hz, -14 LUFS),
Căn chỉnh phụ đề Karaoke từng mili-giây qua Whisper (Khóa cứng văn bản kịch bản gốc Text Lock),
và đồng bộ vào metadata, info.json, Excel cho BẤT KỲ danh sách video nào.

Cách dùng:
  python pipeline/batch_rebuild.py nct_v21 nct_v22 nct_v23 nct_v24 nct_v25 nct_v26
"""

import os
import sys
import json
import shutil
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path

# Cấu hình môi trường Espeak & FFmpeg
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"E:\Programs\espeak-ng"
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"E:\Programs\espeak-ng\libespeak-ng.dll"
os.environ["ESPEAK_DATA_PATH"] = r"E:\Programs\espeak-ng\espeak-ng-data"
os.environ["PATH"] = r"E:\Programs\nodejs;E:\Programs\ffmpeg\bin;E:\Programs\espeak-ng;" + os.environ.get("PATH", "")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "remotion-video" / "public"
OUTPUT_DIR = BASE_DIR / "output"
PIPELINE_DIR = BASE_DIR / "pipeline"
MUSIC_DIR = BASE_DIR / "assets_hub" / "music"

if str(PIPELINE_DIR) not in sys.path:
    sys.path.append(str(PIPELINE_DIR))

import vieneu
import whisper
from music_selector import select_music_for_content
from export_scripts_excel import export_video_to_excel

VOICE_NAME = "Thiện Minh"
SPEED = 0.88
BREATH_PAUSE = 0.35
FPS = 30

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
        print(f"⚠️ Lỗi atempo ({speed}): {e}")
        return wav

def master_audio_with_bgm(voice_path, output_path, total_duration_sec, bgm_path=None):
    if bgm_path is None or not Path(bgm_path).exists():
        bgm_path = PUBLIC_DIR / "background_music.mp3"
    
    if not bgm_path.exists():
        print("⚠️ Không tìm thấy file nhạc nền, giữ voiceover thuần.")
        return False
        
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
        shutil.move(str(temp_mastered), str(output_path))
        return True
    else:
        print(f"⚠️ Lỗi FFmpeg master: {res.stderr[:200]}")
        return False

def rebuild_videos(video_ids):
    if not video_ids:
        print("❌ Cần truyền ít nhất 1 video_id (ví dụ: python pipeline/batch_rebuild.py nct_v21 nct_v22)")
        return False

    print("=" * 65)
    print("🎙️ BẮT ĐẦU CHUẨN HÓA & HÒA ÂM ĐỘNG CHO DANH SÁCH VIDEO")
    print(f"📋 Danh sách ({len(video_ids)}): {', '.join(video_ids)}")
    print(f"⚡ Giọng: {VOICE_NAME} | Tốc độ: {SPEED} | Nghỉ thở: {BREATH_PAUSE}s")
    print("🎵 Nhạc nền: Tự động phân tích cảm xúc từ kho 18 bài (volume=0.15, không Sidechain)")
    print("=" * 65)

    print("\n📦 Nạp mô hình VieNeu-TTS v3turbo...")
    tts = vieneu.Vieneu(mode="v3turbo")
    sample_rate = tts.sample_rate

    print("📦 Nạp mô hình Whisper base (Word-level Text Lock)...")
    whisper_model = whisper.load_model("base")
    print("✓ Mô hình đã sẵn sàng.\n")

    summary_results = []

    for vid in video_ids:
        print("=" * 65)
        print(f"🚀 XỬ LÝ VIDEO: {vid}")
        print("=" * 65)

        # 1. Đọc dữ liệu script từ public hoặc output/input hoặc pipeline
        data_path = PUBLIC_DIR / f"video_data_{vid}.json"
        if not data_path.exists():
            data_path = OUTPUT_DIR / vid / "input" / "video_data.json"
        if not data_path.exists():
            data_path = OUTPUT_DIR / vid / "input" / f"video_data_{vid}.json"
        if not data_path.exists():
            data_path = PIPELINE_DIR / f"script_{vid}.json"

        if not data_path.exists():
            print(f"⚠️ Bỏ qua {vid}: Không tìm thấy file dữ liệu kịch bản!")
            continue

        with open(data_path, "r", encoding="utf-8-sig") as f:
            vdata = json.load(f)

        scenes = vdata.get("scenes", [])
        title = vdata.get("title", "")
        print(f"📌 Tiêu đề: {title}")
        print(f"🎬 Số lượng cảnh: {len(scenes)}")

        # 2. Tự động chọn nhạc nền theo tần số cảm xúc kịch bản từ kho 18 bài
        full_script = " ".join([sc.get("text", "") for sc in scenes])
        bgm_res = select_music_for_content(title=title, script_text=full_script)
        
        if bgm_res and bgm_res.get("file_path") and bgm_res["file_path"].exists():
            chosen_bgm_path = bgm_res["file_path"]
            chosen_bgm_name = bgm_res["track"]["name"]
            chosen_bgm_file = bgm_res["track"]["file"]
            print(f"🎵 Nhạc nền được gán (Mood Match): {chosen_bgm_name} ({chosen_bgm_file}) [Điểm khớp: {bgm_res['score']}]")
        else:
            chosen_bgm_path = PUBLIC_DIR / "background_music.mp3"
            chosen_bgm_name = "On A Piano Cloud"
            chosen_bgm_file = "background_music.mp3"
            print(f"🎵 Nhạc nền mặc định: {chosen_bgm_name}")

        # 3. Sinh giọng đọc TTS từng cảnh
        combined_audio = []
        gap_silence = np.zeros(int(sample_rate * BREATH_PAUSE), dtype=np.float32)
        scene_boundaries = []

        for idx, sc in enumerate(scenes):
            text_clean = sanitize_text_for_tts(sc["text"])
            print(f"   [Cảnh {idx+1}/{len(scenes)}] Đang đọc: {text_clean[:40]}...")
            wav = tts.infer(text=text_clean, voice=VOICE_NAME)
            wav = apply_atempo(wav, sample_rate, SPEED)
            wav_smooth = apply_micro_fade(wav, sample_rate, fade_in_ms=25, fade_out_ms=35)

            s_start_frame = int(round(len(combined_audio) / sample_rate * FPS))
            s_start_sec = len(combined_audio) / sample_rate
            combined_audio.extend(wav_smooth)
            s_end_sec = len(combined_audio) / sample_rate
            s_end_frame = int(round(len(combined_audio) / sample_rate * FPS))

            scene_boundaries.append({
                "scene": sc.get("scene", idx + 1),
                "start_sec": s_start_sec,
                "end_sec": s_end_sec,
                "startFrame": s_start_frame,
                "durationInFrames": s_end_frame - s_start_frame
            })

            if idx < len(scenes) - 1:
                combined_audio.extend(gap_silence)

        total_sec = len(combined_audio) / sample_rate
        total_frames = int(round(total_sec * FPS))
        print(f"   ⏱️ Tổng thời lượng: {total_sec:.2f}s ({total_frames} frames @ 30fps)")

        # 4. Hòa âm chuẩn phòng thu mới: BGM volume=0.15 (không Sidechain) + EQ Ấm 220Hz / -2.5dB 6000Hz + EBU R128 (-14 LUFS)
        raw_temp = PUBLIC_DIR / f"raw_temp_{vid}.wav"
        sf.write(str(raw_temp), np.array(combined_audio, dtype=np.float32), sample_rate)

        target_pub_wav = PUBLIC_DIR / f"voiceover_{vid}.wav"
        input_fol = OUTPUT_DIR / vid / "input"
        input_fol.mkdir(parents=True, exist_ok=True)
        target_inp_wav = input_fol / "voiceover.wav"
        target_inp_wav2 = input_fol / f"voiceover_{vid}.wav"

        ok_master = master_audio_with_bgm(raw_temp, target_pub_wav, total_sec, bgm_path=chosen_bgm_path)
        if not ok_master:
            sf.write(str(target_pub_wav), np.array(combined_audio, dtype=np.float32), sample_rate)

        shutil.copy2(target_pub_wav, target_inp_wav)
        shutil.copy2(target_pub_wav, target_inp_wav2)
        raw_temp.unlink(missing_ok=True)
        print("   ✓ Đã hoàn tất file master voiceover chuẩn phòng thu với bản nhạc riêng biệt.")

        # 5. Whisper Word Timestamps Alignment (KHÓA CỨNG VĂN BẢN KỊCH BẢN GỐC - TEXT LOCK)
        print("   🔍 Trích xuất Word-level Timestamps qua Whisper (Text Lock)...")
        result = whisper_model.transcribe(str(target_pub_wav), word_timestamps=True, language="vi")

        whisper_words = []
        for segment in result["segments"]:
            for w in segment.get("words", []):
                whisper_words.append({
                    "word": w["word"].strip(),
                    "start": w["start"],
                    "end": w["end"]
                })

        updated_scenes = []
        for idx, sc in enumerate(scenes):
            sb = scene_boundaries[idx]
            s_start = sb["start_sec"]
            s_end = sb["end_sec"]

            matched_timings = []
            for w in whisper_words:
                if (w["start"] >= s_start - 0.15 and w["start"] < s_end + 0.15) or \
                   (w["end"] > s_start and w["end"] <= s_end + 0.15):
                    rel_start_frame = max(0, int(round((w["start"] - s_start) * FPS)))
                    rel_end_frame = max(rel_start_frame + 2, int(round((w["end"] - s_start) * FPS)))
                    matched_timings.append((rel_start_frame, rel_end_frame))

            tokens = sc.get("text", "").strip().split()
            final_words = []
            for k, token in enumerate(tokens):
                if k < len(matched_timings):
                    w_sf, w_ef = matched_timings[k]
                elif final_words:
                    w_sf = final_words[-1]["endFrame"]
                    w_ef = w_sf + 6
                else:
                    w_sf = 0
                    w_ef = 6
                final_words.append({
                    "word": token,
                    "startFrame": w_sf,
                    "endFrame": w_ef
                })

            sc_copy = dict(sc)
            sc_copy["startFrame"] = sb["startFrame"]
            sc_copy["durationInFrames"] = sb["durationInFrames"]
            sc_copy["words"] = final_words
            updated_scenes.append(sc_copy)

        # 6. Cập nhật metadata video_data
        vdata["durationInFrames"] = total_frames
        vdata["audioFile"] = f"voiceover_{vid}.wav"
        vdata["music"] = chosen_bgm_name
        vdata["musicFile"] = chosen_bgm_file
        vdata["scenes"] = updated_scenes

        pub_json = PUBLIC_DIR / f"video_data_{vid}.json"
        inp_json = input_fol / "video_data.json"
        inp_json2 = input_fol / f"video_data_{vid}.json"

        with open(pub_json, "w", encoding="utf-8") as f:
            json.dump(vdata, f, ensure_ascii=False, indent=2)
        with open(inp_json, "w", encoding="utf-8") as f:
            json.dump(vdata, f, ensure_ascii=False, indent=2)
        with open(inp_json2, "w", encoding="utf-8") as f:
            json.dump(vdata, f, ensure_ascii=False, indent=2)

        # 7. Cập nhật info.json
        info_path = OUTPUT_DIR / vid / "info.json"
        if info_path.exists():
            with open(info_path, "r", encoding="utf-8") as f:
                info_data = json.load(f)
            info_data["voice"] = VOICE_NAME
            info_data["duration_seconds"] = round(total_sec, 2)
            info_data["total_frames"] = total_frames
            info_data["speed"] = SPEED
            info_data["music"] = chosen_bgm_name
            info_data["music_file"] = chosen_bgm_file
            info_data["skip_youtube"] = False

            # BẮT BUỘC LUÔN CÓ HASHTAG SỐ TẬP
            ep_hashtag = f"#{vid}"
            cur_desc = info_data.get("description", "")
            if ep_hashtag not in cur_desc and vid not in cur_desc:
                if "#shorts" in cur_desc:
                    info_data["description"] = cur_desc.replace("#shorts", f"{ep_hashtag} #shorts")
                else:
                    info_data["description"] = f"{cur_desc.strip()} {ep_hashtag}"

            cur_tags = info_data.get("tags", [])
            if not isinstance(cur_tags, list):
                cur_tags = [str(cur_tags)] if cur_tags else []
            if vid not in cur_tags:
                cur_tags.insert(0, vid)
            info_data["tags"] = cur_tags

            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info_data, f, ensure_ascii=False, indent=2)
            shutil.copy2(info_path, PUBLIC_DIR / f"info_{vid}.json")
            shutil.copy2(info_path, input_fol / "info.json")

        # 8. Cập nhật Excel
        try:
            export_video_to_excel(vid, project="short")
            print(f"   ✓ Đã cập nhật sheet '{vid}' vào scripts_short_video.xlsx.")
        except Exception as e:
            print(f"   ⚠️ Lỗi cập nhật Excel: {e}")

        summary_results.append({
            "id": vid,
            "title": title,
            "music": chosen_bgm_name,
            "music_file": chosen_bgm_file,
            "duration": f"{total_sec:.2f}s"
        })

    print("\n" + "=" * 65)
    print("🎉 TỔNG KẾT HOÀN TẤT CHUẨN HÓA & HÒA ÂM ĐỘNG:")
    for r in summary_results:
        print(f"   - {r['id']}: 🎵 {r['music']} ({r['music_file']}) | ⏱️ {r['duration']}")
    print("=" * 65)
    return True

if __name__ == "__main__":
    vids = sys.argv[1:]
    if not vids:
        vids = ["nct_v21", "nct_v22", "nct_v23", "nct_v24", "nct_v25", "nct_v26"]
    rebuild_videos(vids)
