# AGENTS.md — Quy chuẩn Vận hành Short Video (Nửa Chén Trà)

> File này được tải vào System Prompt của Agent đầu mỗi phiên. Chỉ chứa các quy tắc bất biến, quy trình kiểm soát và định tuyến tài liệu chuyên sâu.

## 1. QUY TẮC BẤT BIẾN (STRICT POLICIES)
- **100% CLOUD RENDER & CLOUD UPLOAD (GITHUB ACTIONS):**
  - Toàn bộ Render MP4 (Studio Quality CRF 16, 320k audio) và Upload YouTube Shorts (kèm thumbnail, lịch Scheduled, tick `containsSyntheticMedia: True`) BẮT BUỘC 100% do GitHub Actions Cloud Worker thực hiện (`python pipeline/cli.py {render|cloud}`).
  - Tuyệt đối KHÔNG render local (trừ khi có cờ `--local` tường minh) và KHÔNG upload YouTube/Drive từ máy local.
  - Máy local chỉ đóng gói vào `output/{id}/input/` để commit. Cloud Worker render xong sẽ đồng bộ trọn gói 1 lần duy nhất lên Google Drive (`1FUTzv6wXSe6o-0q_7Fuy-al7b9CsZ2qx`), upload YouTube và dọn sạch workflow (Zero-Trace).
- **TIÊU ĐỀ SHORTS — STRICT NO #SHORTS IN TITLE:**
  - Tiêu đề trang nhã, gợi cảm xúc, <55 ký tự, tuyệt đối KHÔNG bao giờ gắn `#shorts` vào Tiêu đề (chỉ để ở Description và Tags).
  - Độc lập 100% (Standalone Shorts), không để chữ "Chương X", "Tập X". Badge sách & tác giả đặt nhỏ tinh tế ở góc trên.
- **TICK NỘI DUNG AI BẮT BUỘC (containsSyntheticMedia = True):** Mọi video Shorts khi upload lên YouTube bắt buộc tick `"containsSyntheticMedia": True` để bảo vệ kênh YPP.
- **HASHTAG SỐ TẬP BẮT BUỘC (#<video_id>):** Bắt buộc chứa hashtag số tập (vd `#nct_v25`) trong Description và Tags.
- **100% NHẠC SẠCH KHÔNG BẢN QUYỀN (DYNAMIC MUSIC SELECTION):**
  - Tuyệt đối cấm nhạc có Content ID (HAAWK, Identifyy, Audiam, CD Baby...). Chỉ dùng nhạc CC0 / YouTube Audio Library / Kevin MacLeod sạch từ kho 36 bản nhạc tại `assets_hub/music/` (`music_registry.json`).
  - Tuyệt đối cấm dùng 1 bài cho toàn kênh. Bắt buộc gọi `music_selector.select_music_for_content(title, script_text)` để tự động gán nhạc tương thích cảm xúc.
- **BẢO VỆ VIDEO ĐÃ CÔNG CHIẾU:** Các video đã công chiếu hoặc người dùng đánh dấu đã phát sóng (ví dụ `nct_v08`) phải được loại trừ 100% khỏi các lệnh batch render lại.

## 2. BẢNG CHỐNG NGỤY BIỆN & ĐI TẮT (ANTI-RATIONALIZATION GATES)
> *AI Agent phải tự soi chiếu bảng này trước khi đưa ra bất kỳ hành động hoặc đề xuất nào. Tuyệt đối không dùng các lý do dưới đây để phá vỡ quy chuẩn:*

| AI Ngụy biện / Lối tắt thường gặp | Thực tế kỷ luật & Hành vi bắt buộc |
| :--- | :--- |
| *"Tiêu đề thêm `#shorts` cho dễ lên xu hướng"* | **CẤM TUYỆT ĐỐI.** Tiêu đề phải trang nhã, đậm chất thiền, <55 ký tự. `#shorts` chỉ được nằm trong Description và Tags. |
| *"Kịch bản thêm chút drama / giật gân cho cuốn"* | **SAI TÔN CHỈ KÊNH.** Slogan là *"Nhìn sâu để sống nhẹ"*. Không drama, không giật tít rẻ tiền, không bịa đặt trích dẫn thiền/Phật pháp. |
| *"Script 50s–60s cũng là Shorts, dài thêm chút không sao"* | **VI PHẠM THỜI LƯỢNG VÀNG.** Shorts kênh chuẩn cứng **38s – 42s (90–100 từ)**. Dài hơn sẽ rớt Retention, ngắn hơn sẽ hụt cảm xúc. |
| *"Lấy nhạc tập trước dùng lại hoặc lấy nhạc trend mạng"* | **CẤM TỰ Ý.** Nhạc mạng dính Content ID là chết kênh. Bắt buộc gọi `music_selector` chọn từ kho 36 bản CC0/Kevin MacLeod sạch tại `assets_hub/music/`. |
| *"Thiếu ảnh/video thì lấy B-roll tập cũ đắp vào chữa cháy"* | **CẤM TỰ Ý CHỮA CHÁY.** Kênh yêu cầu B-roll độc bản. Nếu thiếu tài nguyên/hết quota API, **BẮT BUỘC DỪNG LẠI BÁO CÁO** để Người dùng quyết định. |
| *"Máy local đang rảnh, render luôn cho nhanh"* | **SAI NGUYÊN TẮC.** 100% render và upload phải do GitHub Actions Cloud Worker xử lý để đảm bảo Studio Quality (CRF 16) và giải phóng máy người dùng. |
| *"Quên tick nội dung AI chắc YouTube không biết"* | **NGUY HIỂM KÊNH YPP.** Bắt buộc tick `"containsSyntheticMedia": True` trong mọi metadata upload để bảo vệ kênh lâu dài. |
| *"Không cần hỏi giờ schedule, cứ xuất bản ngay hoặc để sau"* | **LỖI QUY TRÌNH.** Bước 1 bắt buộc DỪNG LẠI hỏi người dùng giờ hẹn lịch (`YYYY-MM-DD HH:MM`) trước khi làm tiếp. |


## 3. QUY TRÌNH PHÊ DUYỆT & SẢN XUẤT (5 BƯỚC CHUẨN)
1. **Bước 1 — Kịch bản & Hỏi giờ Schedule:**
   - Viết kịch bản vào Excel (`scripts_short_video.xlsx` hoặc `scripts_long_video.xlsx`, sheet mới ở index=0, không freeze panes). Chi tiết xem `docs/guidelines/script_and_title_rules.md`.
   - **BẮT BUỘC DỪNG LẠI:** Thông báo người dùng duyệt kịch bản và **hỏi giờ hẹn lịch phát sóng** (`YYYY-MM-DD HH:MM`). Ghi nhận vào Excel, `info.json` và metadata.
2. **Bước 2 — Đóng gói nguyên liệu & Duyệt thị giác:**
   - Thu âm giọng đọc VieNeu-TTS Thiện Minh & Whisper Karaoke Text Lock.
   - Sinh toàn bộ các Cảnh hình ảnh AI (Google Flow 1x mode qua `pipeline/core_flow.py`).
   - **Tạo Thumbnail BẮT BUỘC SAU KHI đã sinh ảnh cảnh:** Gọi `pipeline/cli.py thumb make` để tự động trích xuất Cảnh 1 (`_scene1.jpg`) làm ảnh nền nghệ thuật (chống phông nền đen).
   - Đóng gói toàn bộ vào `output/{video_id}/input/` để người dùng mở kiểm tra trực tiếp trước khi render.
3. **Bước 3 — Chuẩn hóa tiền Render (Anti-Collision Archive):**
   - Chạy `pipeline/archive_render.py` để đổi tên file cũ, chống trùng lặp và tránh sinh đuôi `(1)`.
4. **Bước 4 — Render Cloud GitHub Actions:**
   - Đẩy nhánh tạm `render-{id}` (hoặc batch qua `pipeline/batch_render_on_github.py`). Cloud Runner render độc lập, người dùng có thể tắt máy.
   - **Chống treo Cloud Runner (Anti-Hang):** Tuân thủ tuyệt đối `docs/guidelines/cloud_worker_rules.md` (khóa `DEBIAN_FRONTEND=noninteractive`, giới hạn `timeout-minutes: 15`, cấm cài `fonts-noto-cjk`, cấu hình APT timeout 20s).
5. **Bước 5 — One-Shot Cloud Sync & Xuất bản:**
   - Cloud Worker tự động tải trọn gói (Video MP4 + Thumbnail + info.json + input/) lên Drive (`1FUTzv6wXSe6o-0q_7Fuy-al7b9CsZ2qx`), upload YouTube Shorts (Scheduled), và xóa nhánh tạm Zero-Trace.

## 4. THÔNG SỐ KỸ THUẬT CỐT LÕI
- **Kích thước & Thời lượng:** 9:16 (`1080x1920 Full HD`), thời lượng **38s – 42s** (khoảng **90 – 100 từ**), Hook 3s đầu tại `00:00`.
- **Giọng đọc & Karaoke:** VieNeu-TTS v3 Turbo 48kHz giọng `Thiện Minh` (tốc độ 0.88, ngắt 0.35s). Karaoke dùng Whisper Forced Alignment + Text Lock (100% chữ từ kịch bản gốc).
- **Âm thanh & Visual:** EBU R128 (-14 LUFS, BGM volume=0.15). Tối thiểu 60% – 80% thời lượng là B-roll chuyển động thực tế (quản lý qua `assets_hub/broll_segment_tracker.json`), 1 – 2 cảnh Tranh AI nghệ thuật.
- **Cover Frame Trick:** Frame 0–30 (1s đầu) hiển thị Thumbnail hoàn chỉnh để dễ chọn ảnh bìa khi đăng trên mobile.

## 5. ĐIỀU PHỐI HỆ THỐNG & ĐƯỜNG DẪN
- **CLI Điều phối trung tâm:** Dùng `python pipeline/cli.py <module>` cho mọi tác vụ (Bao gồm 11 module: `render`, `drive`, `youtube`, `schedule`, `music`, `voice`, `broll`, `thumb`, `cloud`, `doctor`, `assets`, `flow`, `backup`, `all`).
- **Module Sinh ảnh AI Google Flow (Dùng chung Short & Long Video):** Quản trị tại `pipeline/core_flow.py` qua CLI `python pipeline/cli.py flow {check|launch|single|batch|prompt}`. Tự động chuyển đổi tỷ lệ khung hình 9:16 (Short) và 16:9 (Long Video), tự động ép 1x mode và tải ảnh gốc `=s0`.
- **Thư mục dự án:** `D:\Project\short video`
- **Môi trường Python:** `D:\Programs\vieneu-env\Scripts\python.exe`
- **Template Remotion:** `remotion-video`
- **Kho nhạc & B-roll:** `assets_hub/music/` & `assets_hub/broll_segment_tracker.json`
- **Google Drive Thư mục chuẩn:**
  - Short Video: `1FUTzv6wXSe6o-0q_7Fuy-al7b9CsZ2qx`
  - Long Video: `1PTyVFwtdmblGt6ztDDm13MPVl3NIb6y2`
- **Nguyên tắc kênh:** Không bịa trích dẫn, không chép nguyên văn bài báo, không dùng nhạc/hình không rõ bản quyền. Slogan: *"Nhìn sâu để sống nhẹ"*.
