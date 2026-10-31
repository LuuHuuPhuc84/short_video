# MEMORY.md — Bộ nhớ dự án

> Agent đọc file này đầu mỗi phiên và cập nhật khi có quyết định mới. Chỉ ghi điều đã chốt.

## Quyết định đã chốt
- **KIẾN TRÚC MODULE HÓA ĐƠN NHIỆM (TIẾT KIỆM 90% TOKEN & KHÔNG PHỤ THUỘC LẪN NHAU):**
  Hệ thống chuẩn hóa hoàn toàn thành 10 module độc lập điều phối qua CLI trung tâm `pipeline/cli.py`:
  1. *Module 1 - Render thuần túy (`pipeline/core_render.py` hoặc `python pipeline/cli.py render <id> [--local]`):*
     - Chỉ làm 1 việc duy nhất: Sinh file video `output/{id}/video_{id}.mp4` (mặc định Cloud, thêm `--local` nếu render máy).
     - Toàn bộ Style/Color được chọn qua `"stylePreset"`, KHÔNG BAO GIỜ sửa trực tiếp code React `.tsx`.
  2. *Module 2 - Google Drive Sync (`pipeline/core_drive.py` hoặc `python pipeline/cli.py drive <id> [--input]`):*
     - Chỉ làm 1 việc: Tải video thành phẩm hoặc thư mục `input/` lên Google Drive cá nhân để xem thử hoặc lưu trữ.
  3. *Module 3 - YouTube Publisher (`pipeline/core_youtube.py` hoặc `python pipeline/cli.py youtube <id> [--schedule]`):*
     - Chỉ làm 1 việc: Xuất bản video đã có lên YouTube (Draft hoặc Scheduled) kèm thumbnail và `containsSyntheticMedia: True`.
  4. *Module 4 - Reschedule Siêu Tốc (`pipeline/core_schedule.py` hoặc `python pipeline/cli.py schedule <id|batch> <time>`):*
     - Đổi lịch phát sóng đã xuất bản trên YouTube (publishAt), cập nhật file Excel và info.json trong ~1 giây.
  5. *Module 5 - Fast Music Manager (`pipeline/core_music.py` hoặc `python pipeline/cli.py music {list|suggest|swap}`):*
     - Quản trị 18 bản nhạc No-Copyright trong kho `assets_hub/music/`.
     - Fast Music Swap: Đổi bài nhạc nền và hòa âm lại audio trong đúng 1-2 giây mà KHÔNG cần đọc lại TTS hay chạy lại Whisper.
     - Tự động áp dụng chuẩn hòa âm: BGM cố định volume=0.15 (Shorts) hoặc Gentle Sidechain Ducking (Long).
  6. *Module 6 - AI Voice & Karaoke (`pipeline/core_voice.py` hoặc `python pipeline/cli.py voice {gen|align} <id>`):*
     - Sinh giọng đọc mộc 48kHz VieNeu-TTS v3 Turbo (Thiện Minh 0.88, ngắt nghỉ 0.35s).
     - Trích xuất phụ đề Karaoke Whisper Forced Alignment (Text Lock) khớp từng mili-giây.
  7. *Module 7 - B-roll & Visual Inspection (`pipeline/core_broll.py` hoặc `python pipeline/cli.py broll {inspect|swap} <id>`):*
     - Trích xuất keyframes tiêu biểu từng cảnh ra thư mục `preview/` để người dùng duyệt mắt trong 3 giây.
     - Fast Scene Swap: Thay thế 1 cảnh B-roll bất kỳ trong 1 giây mà không ảnh hưởng audio.
  8. *Module 8 - Thumbnail & Cover Studio (`pipeline/core_thumb.py` hoặc `python pipeline/cli.py thumb make <id>`):*
     - Tạo ảnh bìa chuẩn Safe Zone (Top 280-350px, thẻ Zen Amber Glass). Tự động chèn Cover Frame Trick (Frame 0-30 @ 30fps) cho Shorts.
  9. *Module 9 - Cloud Worker Coordinator (`pipeline/core_cloud.py` hoặc `python pipeline/cli.py cloud {batch|single|status}`):*
     - Điều phối GitHub Actions Parallel Matrix Worker render video song song và kiểm tra tiến độ trực tiếp qua CLI.
  10. *Module 10 - System Doctor & Backup (`pipeline/core_doctor.py` hoặc `python pipeline/cli.py {doctor|backup}`):*
     - Khám sức khỏe toàn diện hệ thống (Token Drive, Token YouTube, GitHub PAT, Disk Space).
     - Sao lưu 100% hệ thống lên Google Drive.
  11. *Lệnh quy trình toàn diện:* `python pipeline/cli.py all <id>`.
- **TỰ ĐỘNG GIA HẠN TOKEN OAUTH HÀNG TUẦN (ZERO-TOUCH TOKEN GUARDS):**
  1. *YouTube Token AutoGuard:* Task Schedule `\YouTube_Token_AutoGuard` chạy 9:00 AM hàng ngày và khi login. Khi token đạt 5.5 - 6 ngày, tự động mở Opera để gia hạn và sync GitHub Secrets.
  2. *Google Drive Token AutoGuard:* Task Schedule `\GDrive_Token_AutoGuard` chạy 9:05 AM hàng ngày và khi login. Khi token đạt 5.5 - 6 ngày, tự động mở Microsoft Edge để người dùng bấm Allow 1-click, lưu token và đồng bộ tự động lên GitHub Secrets cho cả 2 repo Short & Long Video.
- Chủ đề: Bài học cuộc sống, triết lý ứng dụng đời thường; chắt lọc từ "An Trú Trong Hiện Tại" của Thiền sư Thích Nhất Hạnh & trí tuệ cổ xưa.
- Định vị nội dung: **Độc lập 100% (Standalone Shorts)**. Tuyệt đối không để chữ "Chương X" hay "Tập X" để tránh gây rào cản cho người xem ngẫu nhiên.
- Nhận diện sách & tác giả: Đưa Tên sách ("AN TRÚ TRONG HIỆN TẠI") và Tác giả **"Thiền sư Thích Nhất Hạnh"** thành thanh badge nhỏ tinh tế ở góc trên, KHÔNG dùng Hero Header lớn che kín 3 giây đầu.
- **QUY CHUẨN VIDEO SHORTS MỚI (ÁP DỤNG TỪ VIDEO TIẾP THEO):**
  1. *Thời lượng & Dung lượng chữ:* Khung thời lượng chuẩn vàng là **38s – 42s** (dung lượng lý tưởng **90 – 100 từ** ở tốc độ TTS 0.95 có nhịp thở 0.28s) để vừa bảo đảm tối ưu Retention (APV > 75–85% với tổng Watch Time cao ~32s+), vừa có đủ chiều sâu câu chuyện và "độ lắng" cảm xúc (Emotional Breathing Room) chạm đến trái tim người xem, không bị vội vã.
  2. *Hook 3 giây đầu & Xuất hiện ngay giây 00:00:*
     - Khán giả lướt Shorts cực nhanh. Tuyệt đối tránh mở đầu bằng khoảng lặng hay intro nhạc nền dài. Câu nói đầu tiên và dòng chữ đầu tiên phải xuất hiện ngay lập tức tại giây `00:00`.
     - Đánh thẳng vào nỗi đau / nghịch lý đời thực (stress, overthinking, mất ngủ, nóng giận), giao diện thoáng, chữ Hook lớn nổi bật.
     - Tận dụng phụ đề động (dynamic captions) với từ khóa nổi bật được đổi màu để kích thích thị giác người xem ngay từ mili-giây đầu tiên.
  3. *Hình ảnh & Nhịp điệu bổ trợ (Visual Pacing):*
     - Chuyển sang dùng **Video B-roll chuyển động cinematic** (khói trà, mưa rơi, rừng cây, nước chảy...) hoặc Hybrid (Hook bắt buộc là video B-roll).
     - Đối với các video triết lý/chiêm nghiệm, tránh giữ một góc quay tĩnh quá 3–4 giây. Hãy xen kẽ các cảnh quay cận (rót nước, ánh sáng, góc mặt, cử chỉ tay, làn khói) để người xem không bị cảm giác nhàm chán. Chuyển cảnh nhịp 2–3s/cảnh.
  4. *Giọng đọc & Nhịp điệu (TTS v3 Turbo 0.88) & Phụ đề Karaoke chuẩn xác (Word-level Timestamps):*
     - **Giọng đọc chuẩn:** Mặc định 100% cho cả Short Video và Long Video sử dụng **VieNeu-TTS v3 Turbo** chất lượng phòng thu **48kHz** (tốc độ chuẩn **0.88**, trầm ấm, chiêm nghiệm, ngắt nhịp thở 0.35s). Sử dụng giọng đọc chuẩn sạch bản quyền **`Thiện Minh`** (Nam · Bắc · Đĩnh đạc & kể chuyện triết lý).
     - **Phụ đề Karaoke khớp từng mili-giây (Word-level Timestamps) & Khóa cứng văn bản kịch bản gốc (Forced Alignment Text Lock):**
       + Bắt buộc trích xuất chính xác timestamp từng từ (`words: [{word, startFrame, endFrame}]`) qua Whisper / Forced Alignment trực tiếp từ audio thực tế. Tuyệt đối KHÔNG chia đều thời lượng cảnh tuyến tính (tránh chữ đi sau tiếng 1–3s). Remotion component `KaraokeWordBounce` đọc trực tiếp `startFrame` và `endFrame` thực tế của từng từ, đảm bảo chữ nảy khớp 100% từng từ phát ra.
       + **BẮT BUỘC KHÓA CỨNG VĂN BẢN KỊCH BẢN GỐC (TEXT LOCK):** Mảng `words` hiển thị trên màn hình BẮT BUỘC lấy 100% từ ngữ từ kịch bản gốc (`sc['text'].split()`). Whisper CHỈ ĐƯỢC PHÉP cung cấp mốc thời gian (`startFrame`, `endFrame`), TUYỆT ĐỐI KHÔNG lấy văn bản nhận dạng (ASR transcription) của Whisper gán vào `word`. Quy tắc này bảo đảm 100% không bao giờ bị sai chính tả hay biến dạng chữ khi Whisper nghe nhầm phương ngữ (như giọng miền Nam bị nghe nhầm 'dài' -> 'giải', 'trà nguội' -> 'tràn nguội', 'đang' -> 'đàn').
     - **Quy chuẩn chống trùng lặp B-roll & Cơ chế nhảy đoạn an toàn (Strict Anti-Duplicate & Safe Offset Engine):** 
       + Quản trị kho B-roll độc bản bằng mã SHA-256 và sổ cái persistent `assets_hub/broll_segment_tracker.json`.
       + **Cơ chế nhảy đoạn an toàn (Safe Offset Engine):** Khi một file video stock (dài 15s-40s) được sử dụng hoặc tải lại, hệ thống tự động lưu vết chính xác khoảng giây đã dùng `[start_sec, end_sec]`. Lần sau nếu tái sử dụng file đó, hệ thống tự động nhảy sang phân đoạn mới với **Khoảng bảo vệ (Safety Buffer = 2.0s)** (ví dụ: lần 1 dùng `0s - 4.5s`, lần 2 tự động lấy từ `6.5s` trở đi), bảo đảm 100% không trùng lặp góc nhìn thị giác.
       + **Từ chối tái sử dụng khi cạn thời lượng:** Khi file gốc không còn đủ khoảng trống an toàn cho thời lượng câu thoại mới, hệ thống tự động từ chối và bắt buộc người dùng chọn video stock mới khác.
       + Lệnh kiểm tra sổ cái phân đoạn: `python pipeline/cli.py broll tracker`.
     - **Quy tắc bảo vệ video đã công chiếu:** Các video đã được công chiếu hoặc người dùng đánh dấu đã phát sóng (ví dụ `nct_v08`) phải được loại trừ 100% khỏi các lệnh batch render lại.
  5. *Quy chuẩn xử lý âm thanh tự nhiên (Audio Mastering):*
     - *Gieo nhịp thở (Phrase Chunking):* Chia câu thành các cụm từ ngắn có nghĩa bằng dấu phẩy `,` để AI tự động lấy hơi và hạ giọng tự nhiên như người thật.
     - *Khử giật & tiếng khựng:* Áp dụng Micro-fade (25ms in / 35ms out) và khoảng nghỉ nhịp thở **0.35s** giữa các câu.
     - *Hòa âm BGM chuẩn hóa theo từng dự án (Khắc phục triệt để nghẹt tiếng khi thoại dày):*
       + **Dự án Short Video (38s-42s, đọc liên tục):** Giữ cố định nhạc nền ở mức **`volume=0.15`** (khoảng 0.14 - 0.16), KHÔNG dùng Sidechain Compression để tránh nhạc bị dìm mất hút khi đọc liên tục. Nhạc piano dìu dặt chảy đều làm nền êm ái, rõ ràng.
       + **Dự án Long Video (8-15 phút, nhiều đoạn ngắt ý):** Áp dụng Gentle Sidechain Ducking (`volume=0.26`, `ratio=2`, `attack=30`, `release=180ms`). Khi có lời thoại nhạc chỉ lùi nhẹ xuống ~12-14% (nghe rõ giai điệu, không bị lấn át), khi ngắt câu 0.35s nhạc nhả nén nhanh ngân nga lên 24-26% tạo chiều sâu điện ảnh.
     - *Broadcast Warmth EQ & EBU R128:* Tăng dải trầm 220Hz tạo độ dày ấm, giảm chói gắt 6000Hz, chuẩn hóa độ to -14 LUFS cho YouTube Shorts / TikTok.
  6. *Cú chốt, Vòng lặp & Nhận diện kênh (Ending, Looping & Brand Outro):*
     - Không gượng ép kêu gọi bình luận hay bắt người xem tương tác giả tạo.
     - Câu kết của Shorts được gọt giũa ngắn gọn, tạo cảm giác lắng đọng hoặc kết nối mượt mà trở lại câu mở đầu (Seamless Looping), khiến người xem muốn dừng lại xem lại lần 2 hoặc để lại bình luận chia sẻ câu chuyện của chính họ.
     - Cuối mỗi video kết thúc bằng câu đúc kết sâu sắc, tự nhiên của kịch bản, kèm hình ảnh nửa chén trà và slogan nhận diện: *"Nhìn sâu để sống nhẹ"* để lại dư âm lắng đọng cho người xem.
  7. *Quy chuẩn bắt buộc ghi Hashtag số tập (#<video_id>) vào Mô tả & Tags (Strict Episode Tagging Rule):*
     - Mọi video Shorts khi sản xuất mới hoặc upload BẮT BUỘC phải chứa hashtag số tập tương ứng (ví dụ: `#nct_v25`, `#nct_v26`, `#nct_v100`) trong:
       + Phần mô tả (Description) của YouTube, TikTok, file Excel và `info.json`.
       + Danh sách từ khóa (Tags) của video trên YouTube (`<video_id>`).
     - Toàn bộ pipeline (`auto_make_video.py`, `core_youtube.py`, `upload_to_youtube.py`, `batch_render_on_github.py`, `render_on_github.py`, `batch_rebuild.py`) đều tự động kiểm tra và chèn hashtag số tập này nếu chưa có trước khi lưu file hoặc upload lên YouTube Studio.
- **QUY CHUẨN ÂM NHẠC BẮT BUỘC (ZERO COPYRIGHT CLAIM POLICY - 100% NHẠC SẠCH KHÔNG BẢN QUYỀN):**
  1. *Nguyên tắc triệt để:* Tuyệt đối KHÔNG sử dụng các bài nhạc lofi/ambient trôi nổi có đăng ký bảo hộ Content ID qua các bên thứ ba như HAAWK, Identifyy, Audiam, CD Baby, Believe Music (bài học: bản nhạc *Lofi Study* của FASSounds từng bị HAAWK claim từ 2:27 đến 5:39 ở tập 5).
  2. *Nguồn nhạc hợp lệ duy nhất:*
     - Thư viện âm thanh YouTube (YouTube Audio Library - No Attribution Required).
     - Tác phẩm CC0 / Creative Commons không Content ID của Kevin MacLeod (Incompetech).
     - Nhạc piano thiền định của Liborio Conti (*On A Piano Cloud*, *Tranquil Reflections*) không đăng ký Content ID.
     - Nhạc tự sản xuất hoặc Public Domain (CC0).
  3. *Lưu trữ chuẩn:* File nhạc nền chính thức được đặt tại `remotion-video/public/background_music.mp3` của cả 2 dự án (bản chuẩn hiện tại là *On A Piano Cloud*, 20 phút piano ambient thư thái, an toàn 100% không Content ID).
  4. *Kho nhạc đa dạng & Tự động chọn nhạc theo nội dung (Mood-based Dynamic Music Selection):* Đã tích hợp kho 18 bản nhạc No-Copyright chuẩn Studio đặt tại `assets_hub/music/` (kèm file `music_registry.json`). Module `pipeline/music_selector.py` tự động phân tích tiêu đề và kịch bản (gia đình, cha mẹ, cơn giận, thiền trà, hy vọng) để ghép bản nhạc có tần số cảm xúc tương thích nhất cho từng video.
  5. *BẮT BUỘC CHỌN NHẠC ĐỘNG CHO MỌI VIDEO (TUYỆT ĐỐI CẤM DÙNG DUY NHẤT 1 BÀI CHO TOÀN KÊNH):*
     - Tuyệt đối KHÔNG hardcode hay mặc định dùng duy nhất một bản *On A Piano Cloud* cho toàn bộ các video. Việc lặp lại một bài nhạc duy nhất sẽ gây nhàm chán và làm mất cảm xúc riêng của từng chủ đề.
     - Mọi script sản xuất trong pipeline (`auto_make_video.py`, v.v.) BẮT BUỘC phải gọi `music_selector.select_music_for_content(title, script_text)` để tự động gán bản nhạc phù hợp nhất từ kho 18 bài trong `assets_hub/music/`.
     - Tên bản nhạc đã chọn bắt buộc phải được ghi nhận vào `info.json`, `video_data.json` và file Excel `scripts_short_video.xlsx`.
- **QUY CHUẨN BẮT BUỘC TẠO THUMBNAIL CHO SHORTS & DUYỆT THỊ GIÁC (MỚI CHỐT):**
  1. *Bắt buộc tạo file Thumbnail riêng (1080x1920):* Do YouTube Shorts đã mở tính năng upload ảnh bìa (Upload file) trực tiếp từ PC, mỗi video Shorts khi sản xuất BẮT BUỘC phải tạo 1 file ảnh thumbnail riêng (`thumbnail_{video_id}.jpg`).
  2. *Bắt buộc đưa Thumbnail vào thư mục `input/` để duyệt:* File ảnh thumbnail BẮT BUỘC phải được lưu trong thư mục `output/{video_id}/input/` để người dùng mở kiểm tra và duyệt trực tiếp cùng với toàn bộ nguyên liệu trước khi kích hoạt render.
  3. *Tiêu chuẩn thiết kế Thumbnail Shorts:*
     - *Tỷ lệ & Kích thước:* Chuẩn dọc 9:16 (1080 x 1920 Full HD).
     - *Hình ảnh nền:* Dùng hình ảnh AI nghệ thuật vẽ đúng bối cảnh, sâu lắng, chân thực và đậm chất cảm xúc của kịch bản.
     - *Chọn khung hình có biểu cảm / hành động đắt giá:* Khi chọn ảnh bìa (thumbnail) hoặc chọn frame trích xuất, ưu tiên khung hình rõ nét, giàu cảm xúc nhất (khoảnh khắc rót trà, bàn tay nhăn nheo của cha mẹ, ánh mắt lặng lẽ).
     - *Title Hook đắt giá & Text Overlay:* Dòng chữ ngắn (3–5 từ, tối đa 6–8 chữ, ví dụ: `"Càng giữ, càng khó ngủ"`, `"Đừng để chữ MAI..."`), chữ to (60–64px bold), màu vàng hổ phách `#fbbf24` hoặc trắng viền đen tương phản cao, đặt ở nửa trên khung hình (Safe Zone) tránh bị nút Like/Comment che. Thẻ kính mờ Zen Amber Glass viền vàng.
     - *Tọa độ Safe Zone vàng:* Nằm ở 1/3 phía trên khung hình (`top: 280px – 350px`), dưới badge thương hiệu/sách, tuyệt đối tránh vùng đáy và cạnh phải để không bị tên kênh và cụm nút tương tác của Shorts che.
  4. *BẮT BUỘC 1 GIÂY ĐẦU TIÊN CỦA VIDEO LÀ HÌNH THUMBNAIL (COVER FRAME TRICK):*
     - Do YouTube Shorts trên ứng dụng điện thoại chỉ cho phép kéo con trỏ chọn ảnh bìa từ các khung hình bên trong video, mỗi video Shorts khi render BẮT BUỘC phải chèn ảnh Thumbnail (`thumbnail_{video_id}.jpg`) vào đúng **1 giây đầu tiên (Frame 0 – 30 @ 30fps)** của video.
     - Frame 0 hiển thị 100% hình ảnh Thumbnail hoàn chỉnh 1080x1920 (kết hợp tranh AI + Title Hook nổi bật trong Safe Zone + Top Badge thương hiệu).
     - Từ Frame 24 đến 29: Cross-fade hòa tan mượt mà (5 frames) sang video B-roll chuyển động.
     - Khi người dùng đăng video Shorts trên điện thoại hoặc hệ thống tự động bắt frame đầu, chỉ cần chọn ngay Frame 0 (giây đầu tiên) là video có ngay ảnh bìa hoàn mỹ, chuyên nghiệp, giữ chân người xem.
     - Hơn 97% thời lượng còn lại (từ giây thứ 1 đến hết) là 100% Video B-roll chuyển động thực tế, bảo đảm an toàn tuyệt đối cho chính sách Bật kiếm tiền (YPP) của YouTube (hoàn toàn không bị tính là video slideshow tĩnh).

- **QUY CHUẨN B-ROLL CHO SHORTS (100% NATIVE VERTICAL 9:16 & ƯU TIÊN TẢI MỚI):**
  1. *Nguyên tắc bắt buộc 100% video quay dọc (Native Vertical 1080x1920):* Bắt buộc `height >= width` (1080x1920 hoặc 4K dọc). Tuyệt đối cấm lấy video ngang 16:9 zoom crop làm vỡ hạt. Toàn bộ video ngang trong assets_hub của Short đã bị thanh trừng, chỉ lưu trữ 100% video dọc.
  2. *Quy trình ưu tiên tải video mới (New Native Vertical First):*
     - Khi sản xuất video, pipeline BẮT BUỘC ưu tiên tìm kiếm và tải các video MỚI từ kho stock quay dọc (Mixkit Vertical, Pexels Portrait) bám sát chi tiết ngữ cảnh của từng cảnh trong kịch bản.
     - Chỉ trong trường hợp không thể tải hoặc không tìm thấy video mới phù hợp, mới được phép tái sử dụng video trong kho nội bộ.
  3. *Bắt buộc trích xuất Keyframe thẩm định thị giác:*
     - Mỗi khi tải video mới về, pipeline BẮT BUỘC dùng FFmpeg cắt ra 1–3 khung hình tiêu biểu (keyframes) để thẩm định trực tiếp: đúng phong cách Á Đông, tĩnh lặng, ấm áp, giàu tính điện ảnh và đúng ẩn dụ kịch bản, tuyệt đối không chọn dựa trên thẻ tags văn bản.
- **QUY CHUẨN THẨM ĐỊNH THỊ GIÁC KHI TẢI / CHỌN B-ROLL (STRICT VISUAL INSPECTION - TUYỆT ĐỐI KHÔNG DỰA TRÊN NHÃN/TAGS):**
  1. *Nguyên tắc cốt tử:* TUYỆT ĐỐI KHÔNG dựa trên tiêu đề, thẻ tag hay mô tả văn bản của video stock để chọn bừa vào kịch bản (bài học: tag "father", "tea", "nature" trên stock thường là cảnh người phương Tây, bánh pancake, đường phố hiện đại hoặc cành lá/mặt nước vu vơ không liên quan).
  2. *Bắt buộc trích xuất Frame thẩm định bằng mắt:* Khi tải hoặc cân nhắc video B-roll, pipeline BẮT BUỘC phải dùng FFmpeg cắt ra 1–3 khung hình tiêu biểu (keyframes) để xem xét trực tiếp tính phù hợp trước khi quyết định chọn.
  3. *Tiêu chuẩn thẩm định 3 lớp:*
     - *Lớp 1 - Bối cảnh & Văn hóa:* Phải mang phong cách Á Đông, mộc mạc, tĩnh lặng hoặc đời sống gia đình hoài niệm, tuyệt đối không dính người/cảnh phương Tây lạc quẻ.
     - *Lớp 2 - Tông màu & Ánh sáng:* Giàu tính điện ảnh (cinematic), trầm ấm, hoài niệm, không dùng cảnh màu mè rực rỡ hay góc quay lia giật cục.
     - *Lớp 3 - Tính biểu tượng (Cinematic Metaphor):* Video phải là thước phim ẩn dụ nâng tầm cảm xúc cho câu thoại (ví dụ: bánh xe lăn chậm trên đường sớm mờ sương, ngọn lửa ấm bập bùng, làn khói trà bốc lên nhẹ nhàng).
- **QUY CHUẨN DUYỆT TIỀN RENDER & HỎI GIỜ LÊN LỊCH (BẮT BUỘC 100% CHO CẢ 2 DỰ ÁN SHORT VIDEO VÀ LONG VIDEO):**
  Trước khi bắt đầu render video (dù render Local hay qua GitHub Actions Cloud Worker), pipeline BẮT BUỘC phải thực hiện nghiêm ngặt theo đúng 4 bước:
  1. *Bước 1 - Cập nhật Excel & Hỏi lịch hẹn giờ (Schedule):* 
     - Tự động cập nhật nội dung kịch bản vào file Excel tương ứng (`scripts_short_video.xlsx` cho Short Video, `scripts_long_video.xlsx` cho Long Video, mỗi video 1 sheet riêng mang tên `video_id`).
     - **BẮT BUỘC DỪNG LẠI**, thông báo cho người dùng mở file Excel duyệt/chỉnh sửa nội dung lời thoại, ĐỒNG THỜI **BẮT BUỘC PHẢI HỎI NGƯỜI DÙNG GIỜ SCHEDULE LÊN LỊCH** (`YYYY-MM-DD HH:MM`) cho từng video.
     - Sau khi người dùng phản hồi giờ đăng, ghi nhận giờ schedule này vào file Excel, `info.json` và metadata của video.
  2. *Bước 2 - Copy toàn bộ video/hình ảnh đã cắt vào thư mục input để duyệt:* Copy toàn bộ các file hình ảnh hoặc video B-roll đã cắt (footage/clips/images chuẩn tỷ lệ 9:16 cho Short hoặc 16:9 cho Long) của tất cả các cảnh vào thư mục `output/{video_id}/input/` đầu ra (cùng với `video_data.json`, `voiceover.wav`, `script.json`, `script.md`) để người dùng có thể mở ra kiểm tra, duyệt thị giác trực tiếp.
  3. *Bước 3 - Đồng bộ toàn bộ thư mục input lên Google Drive sau khi duyệt:* Sau khi người dùng xác nhận duyệt xong kịch bản, giờ hẹn lịch và nguyên liệu, pipeline mới tiến hành copy/đồng bộ TOÀN BỘ thư mục `output/{video_id}/input/` (chứa đầy đủ video, hình ảnh đã cắt, audio, script, metadata) lên Google Drive cá nhân tại thư mục `{video_id}/input/` tương ứng.
  4. *Bước 4 - Render & Tự động lên lịch phát sóng:* Sau khi đồng bộ Drive thành công 100%, mới kích hoạt bước render video thành phẩm. Hệ thống tự động sử dụng giờ schedule đã thống nhất để đặt lịch phát sóng (Scheduled) trực tiếp lên YouTube (ở chế độ Private Scheduled) và TikTok.
- **QUY CHUẨN BẮT BUỘC TICK NỘI DUNG AI (containsSyntheticMedia = True):**
  Mọi video (cả Short và Long Video) khi upload lên YouTube (dù qua Cloud GitHub Actions hay Local script) BẮT BUỘC luôn tự động đặt `"containsSyntheticMedia": True` trong `status` của YouTube Data API v3. Điều này bảo đảm minh bạch 100% nội dung AI (giọng đọc TTS/clone, hình ảnh AI), bảo vệ kênh an toàn tuyệt đối, tránh mọi nguy cơ bị YouTube quét phạt hoặc tước quyền Bật kiếm tiền (YPP).
- **QUY TRÌNH PHÊ DUYỆT & RENDER (MẶC ĐỊNH GITHUB ACTIONS CLOUD WORKER):**
  - **Duyệt kịch bản:** Liệt kê chi tiết nội dung (Timeline, Lời thoại/Voiceover, Highlight, Mô tả B-roll/Visual) trước trong chat để người dùng duyệt và sửa đổi.
  - **Render mặc định qua GitHub Actions Cloud Worker (0% tài nguyên máy):**
    - Repo GitHub: `LuuHuuPhuc84/short_video` & `LuuHuuPhuc84/long_video` (Public Repo - Render miễn phí không giới hạn phút).
    - Mô hình: *Ephemeral Render Worker (Zero-switch & Zero-Download Cloud Automation)*:
      + Chỉ nạp metadata + audio + B-roll của đúng video đó lên nhánh tạm `render-{video_id}`.
      + GitHub Actions tự động render Full HD (1080x1920 cho Short, 1920x1080 cho Long) với chất lượng Studio `--crf=18`, `--concurrency=2`.
      + **Tự động đẩy thẳng lên Google Drive cá nhân** (`phuclh.hut@gmail.com` qua OAuth 2.0).
      + **Tự động tải thẳng lên YouTube ở chế độ Nháp / Lên lịch (Draft/Scheduled)** qua YouTube Data API v3 (`YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`). Video lập tức xuất hiện trong YouTube Studio để kiểm tra, gắn thumbnail và hẹn giờ phát sóng mà không cần tải file về máy.
      + **Tự động đồng bộ Secrets lên GitHub (Zero-Touch Secrets Automation):** Mỗi khi cấp quyền YouTube trên máy (`get_youtube_oauth_token.py`), script tự động mở **trình duyệt Opera** (nơi lưu sẵn phiên đăng nhập), dùng PyNaCl mã hóa đầu cuối và đồng bộ thẳng `YOUTUBE_REFRESH_TOKEN`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` lên cả 2 repo `short_video` và `long_video` qua GitHub REST API (sử dụng token lưu an toàn trong `pipeline/github_token.txt`). Người dùng không bao giờ phải copy/paste Secret thủ công trên web.
      + **Tạo thư mục riêng cho từng video trên Drive:** Thư mục `{video_id}/` chứa đầy đủ: file video `video_{video_id}.mp4`, file mô tả `info.json`, file ảnh thumbnail (cho Long Video), và **thư mục con `input/`** chứa trọn vẹn nguyên liệu gốc (`video_data.json`, `voiceover.wav`, `script.json`, `script.md`).
      + **Không sinh file MP4 trên GitHub:** Tuyệt đối không lưu file MP4 vào Artifacts hay Releases trên GitHub.
      + **Xóa sạch dữ liệu tạm & Workflow History trên GitHub (Zero-Trace):** Nhánh tạm `render-{video_id}` được xóa ngay sau khi render xong. Hệ thống tự động xóa sạch toàn bộ lịch sử Workflow Run trên GitHub Actions qua workflow `cleanup_history.yml` và action `Mattraks/delete-workflow-runs` với quyền `actions: write`, giữ repo luôn là khung rỗng sạch sẽ, 0% rác và 100% bảo mật riêng tư.
      + **Mặc định không cần tải video về máy local (Zero-Download):** Tiết kiệm 100% dung lượng ổ cứng. Khi thực sự cần file MP4 tại máy tính mới thêm cờ `--download`.
    - Lệnh 1-click: `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/auto_make_video.py [tên_video.mp4]`
    - Lệnh kích hoạt render nhanh qua GitHub Actions (khi nguyên liệu đã sẵn):
      `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/render_on_github.py [video_id]`
    - Tùy chọn tải video về máy local: thêm cờ `--download`.
    - Tùy chọn render tại máy local: thêm cờ `--local`.
  - **QUY CHUẨN BATCH RENDER ĐỘC LẬP TRÊN GITHUB ACTIONS (AUTONOMOUS PARALLEL MATRIX):**
    - Áp dụng khi sản xuất nhiều video cùng lúc (từ 2 video trở lên, ví dụ chuỗi 5-10 video):
      1. Đóng gói toàn bộ nguyên liệu (audio master giọng chuẩn `laytutritueconhan` tốc độ 0.75, B-roll thiên nhiên độc bản, timeline, file `info.json` có gắn sẵn lịch schedule chuẩn) vào `output/{vid}/input/` và đồng bộ 100% lên Google Drive.
      2. Đẩy một lần duy nhất lên nhánh `render-batch` (kèm file `batch_manifest.json` ghi danh sách video cần chạy).
      3. Workflow `batch_render_shorts.yml` trên GitHub Actions tự động kích hoạt ma trận song song `strategy: matrix` với `max-parallel: 2` (chạy 2 video đồng thời, lần lượt đến khi hoàn tất toàn bộ danh sách).
      4. Mỗi runner trên GitHub khi render xong sẽ tự động upload file MP4 lên Drive và tự động upload + đặt lịch (Schedule) trên YouTube.
      5. **Tính năng độc lập 100% (Headless & Autonomous):** Sau khi đẩy lệnh lên GitHub Actions thành công, toàn bộ quy trình chạy ngầm hoàn toàn trên Cloud. Người dùng có thể tắt Antigravity hoặc tắt máy tính cá nhân; GitHub Actions vẫn tự động render, upload, schedule và tự xóa sạch lịch sử (Zero-Trace) khi hoàn tất.
    - Lệnh chạy Batch:
      `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/batch_render_on_github.py [vid1] [vid2] ...`

- **QUY CHUẨN ÁNH SÁNG & ĐỘ TRONG TRẺO (BẢO TOÀN 100% ÁNH SÁNG GỐC CỦA VIDEO/ẢNH):**
  1. *Triệt tiêu hoàn toàn lớp phủ đen toàn màn hình:* Không dùng bất kỳ lớp `CinematicGradientOverlay` hay màng đen nào dìm tối toàn khung hình.
  2. *Không dùng bộ lọc dìm sáng:* Bỏ các filter `brightness(0.95)`, `contrast`, giữ nguyên 100% độ sáng, độ nét và màu sắc tự nhiên của video/ảnh B-roll gốc.
  3. *Chỉ duy nhất ô hộp phụ đề (Caption Card) có nền mờ:* Hộp chữ phụ đề ở phía dưới đã có nền kính mờ riêng (`rgba(10, 15, 30, 0.85)` + blur) bảo đảm chữ luôn nổi bật và dễ đọc trên mọi nền sáng, toàn bộ khu vực xung quanh giữ trọn vẹn 100% ánh sáng gốc.
- **MẪU THIẾT KẾ ĐẶC TRƯNG (DESIGN PRESET): "ZEN AMBER GLASS" (THIỀN TRÀ KÍNH MỜ):**
  - *Tính linh hoạt (Tùy biến theo chủ đề):* Mẫu này được lưu lại như một bộ Preset hoàn chỉnh để có thể tái sử dụng bất cứ lúc nào. Việc áp dụng là linh hoạt theo từng video, không áp đặt cứng nhắc 100% video nào cũng giống nhau (tùy theo chủ đề, cảm xúc hay yêu cầu cụ thể của người dùng để chọn dùng Zen Amber Glass hoặc các phong cách hình ảnh khác).
  - *Ý niệm thẩm mỹ:* Kết hợp giữa sự tĩnh lặng của Trà đạo / Thiền học với ngôn ngữ thiết kế kính mờ cao cấp (Glassmorphism) và điểm xuyết sắc vàng hổ phách đặc trưng (`#e0a96d`, `#fbbf24`).
  - *Bảo toàn ánh sáng:* Không dìm tối khung hình, giữ nguyên 100% màu sắc và chuyển động của video B-roll thiên nhiên. Mọi nhãn dán, thẻ chữ và phụ đề đều dùng nền kính mờ bán trong suốt (`backdrop-filter: blur(8px – 20px)`).
  - *Áp dụng cho Long Video (16:9 - 1920x1080):*
    1. *Top-Left Brand Badge (Logo & Thương hiệu):* Thẻ viên thuốc (pill) góc trên trái (`top: 36px, left: 48px`), chứa icon tách trà bốc khói vàng kim, chữ `"NỬA CHÉN TRÀ"` in hoa đậm nét và slogan `"Nhìn sâu để sống nhẹ"`. Nền `rgba(18, 20, 26, 0.75)` + blur 12px, viền vàng hổ phách `rgba(224, 169, 109, 0.35)`.
    2. *Top-Right Dynamic Chapter Indicator (Chương động):* Nhãn góc trên phải (`top: 40px, right: 48px`), tự động cập nhật tên chương bám sát kịch bản (`HAI LỰA CHỌN QUEN THUỘC`, `VÌ SAO ĐÈ NÉN THẤT BẠI`...). Nền `rgba(10, 12, 16, 0.7)` + blur 10px, viền trắng mờ thanh mảnh.
    3. *Center Hero Text Card (Dành cho cảnh THẺ CHỮ):* Hộp thẻ chữ trung tâm lớn với `backdrop-filter: blur(20px)`, viền đôi vàng hổ phách, nhãn tag phía trên (`✦ CÂU HỎI TỰ THẤU HIỂU ✦` hoặc nhãn cảnh), chữ highlight vàng rực rỡ đổ bóng mềm.
    4. *Bottom Paced Sentence Caption (Hộp phụ đề kính mờ):* Nằm ở đáy màn hình, viền bo tròn 16px, hiển thị phụ đề theo từng câu nói với các từ khóa đắt giá được tự động tô sáng màu vàng hổ phách `#fbbf24`.
  - *Áp dụng cho Short Video (9:16 - 1080x1920):*
    1. *Top Badge Thương hiệu / Tác giả (Top 80px):* Nhãn nhỏ tinh tế bo tròn 999px chứa tên sách/tác giả/kênh, không che khuất màn hình mở đầu.
    2. *Title Hook 1.5s Tự Động Làm Thumbnail (Top 290px):* Thẻ kính mờ `rgba(10, 15, 30, 0.72)` viền vàng bo góc 24px, chữ vàng hổ phách `#fbbf24` in hoa 900 đậm, nằm gọn trong Safe Zone không bị giao diện Shorts che.
    3. *Center Hero Text Card (Cảnh THẺ CHỮ dọc):* Thẻ kính mờ trung tâm với video thiên nhiên mờ phía sau.
    4. *Bottom-Center Karaoke Caption (Top ~1320px - 1450px):* Chữ động bám nhịp đọc, từ khóa vàng kim, định vị trên vùng tiêu đề và nút tương tác của TikTok/Shorts.
- Nền tảng: YouTube Shorts, TikTok, Facebook Reels (chuẩn 9:16, 1080x1920).
- Công cụ: Antigravity + Vietneu-TTS + Remotion.

- **QUY CHUẨN TẠO HÌNH ẢNH AI (TRÁNH LỖI 429 & TỐI ƯU HẠN MỨC QUOTA):**
  1. *Nguyên tắc dứt điểm:* Ưu tiên hoàn thành hình ảnh của 1 tập trước (hoàn thiện 100% các cảnh của tập đó trước khi chuyển sang tập tiếp theo).
  2. *Giới hạn gọi song song:* Khi tạo ảnh AI, chỉ sinh song song tối đa 3 ảnh trong 1 lần gọi (batch <= 3 ảnh) để bảo đảm không chạm trần tốc độ dồn dập (Burst Limit / Rate Limit 429) của API.
- **QUY CHUẨN KIỂM TRA CHỐNG TRÙNG LẶP ASSETS (STRICT SHA-256 HASH VERIFICATION):**
  1. *Nguyên tắc triệt để (Zero-Duplication):* Mỗi hình ảnh, video B-roll được đưa vào sản xuất BẮT BUỘC phải là tài nguyên độc bản (100% unique), không được phép trùng lặp mã băm SHA-256 với bất kỳ tài nguyên nào đã dùng trong cùng dự án hoặc giữa các video với nhau.
  2. *Rà soát tự động trước khi đóng gói:* Trước khi chốt thư mục input/ và render, pipeline BẮT BUỘC phải chạy script kiểm tra pipeline/verify_assets_uniqueness.py để quét toàn bộ mã băm SHA-256 của tất cả các file hình ảnh / video trong thư mục input/ và kho ssets_hub. Nếu phát hiện bất kỳ file nào trùng hash SHA-256 (dù khác tên file), hệ thống phải BÁO ĐỎ và DỪNG LẠI NGAY LẬP TỨC để thay thế tài nguyên mới độc bản trước khi bước vào các bước tiếp theo.
  3. *Cơ chế ghi nhận Registry:* File ssets_hub/asset_registry.json lưu trữ toàn bộ SHA-256 hash của từng asset. Khi lấy asset mới, nếu hash đã tồn tại trong registry của các video trước đó thì BẮT BUỘC phải từ chối (Hard Rejection) và tải asset mới khác biệt 100%.

## Quy trình sản xuất
1. Chọn chủ đề chạm đúng nỗi đau thực tế, chắt lọc bài học cốt lõi từ sách/triết lý.
2. AI viết kịch bản chuẩn Shorts (25–35s, 4 bước: Hook đời thực -> Nghịch lý -> Giải pháp hành động -> Comment Hook).
3. Người dùng rà soát và duyệt kịch bản (lời thoại, visual, highlight).
4. Chuẩn bị xong âm thanh & B-roll -> Tự động kích hoạt Render Cloud Worker trên GitHub Actions (hoặc `--local` nếu người dùng muốn render tại máy).
5. Render hoàn tất -> Kiểm tra video tại `output/{video_id}/` -> Ghi `Nhật ký video`.

- **QUY CHUẨN FILE EXCEL (KHÔNG FREEZE PANES & SHEET MỚI NHẤT LÊN ĐẦU):**
  - Tuyệt đối KHÔNG đóng băng (freeze_panes = None) bất kỳ dòng hay cột nào trong tất cả các file Excel kịch bản (scripts_short_video.xlsx, scripts_long_video.xlsx, v.v.).
  - Giữ bảng tính ở trạng thái tự do để người dùng dễ dàng cuộn lên xuống xem toàn bộ nội dung mà không bị che khuất tầm nhìn.
  - **ĐẶT SHEET MỚI NHẤT LÊN ĐẦU TIÊN (INDEX 0):** Mỗi khi tạo hoặc cập nhật kịch bản video mới, sheet của video đó BẮT BUỘC phải được chèn vào vị trí đầu tiên (index=0) của workbook và được kích hoạt (wb.active = 0), tuyệt đối KHÔNG để ở cuối cùng, để người dùng vừa mở file Excel là thấy ngay kịch bản mới nhất.

## Đường dẫn & lệnh
- Thư mục dự án: `E:\Project\short video`
- Môi trường TTS: `E:\Programs\vieneu-env\Scripts\python.exe`
- Template Remotion: `remotion-video`
- Lệnh chạy render Full HD chính thức (1-click):
  `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/auto_make_video.py [tên_video.mp4]`
- Lệnh render nhanh (giữ audio cũ nếu có sẵn):
  `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/auto_make_video.py [tên_video.mp4] --skip-audio`
- Tự động upload & đặt lịch phát sóng (Scheduled) YouTube Shorts qua API:
  - Token & Secrets: `pipeline/token.json` & `pipeline/client_secrets.json` (Kênh "Nửa Chén Trà")
  - Lệnh upload & hẹn giờ:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/upload_youtube_short.py [tên_video.mp4] --title "Tiêu đề #shorts" --schedule "YYYY-MM-DD HH:MM"`
  - Ví dụ:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/upload_youtube_short.py video_bhca_v1.mp4 --title "Chiếc Hoa Trắng Ở Tokyo" --schedule "2026-10-17 11:30"`
- **Quản lý, đổi trạng thái & sửa lịch hẹn giờ YouTube (Áp dụng cho cả Long & Short Video):**
  - Xem thông tin video hiện tại:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/update_youtube_video.py [video_id hoặc URL]`
  - Đổi sang Công khai ngay lập tức (Public):
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/update_youtube_video.py [video_id] --privacy public`
  - Đổi / Đặt lịch hẹn giờ mới (Schedule):
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/update_youtube_video.py [video_id] --schedule "YYYY-MM-DD HH:MM"`
  - Đổi Thumbnail hoặc Tiêu đề / Mô tả:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/update_youtube_video.py [video_id] --thumb [path_ảnh] --title "[tiêu đề mới]"`
- Tự động upload & đặt lịch phát sóng (Scheduled) TikTok Shorts qua Playwright:
  - Cookie Session: `pipeline/sessionid.txt` (Kênh "Nửa Chén Trà" / 365ngammoingay)
  - Lệnh upload & hẹn giờ đơn lẻ:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/upload_tiktok_short.py [tên_video.mp4] --caption "Nội dung #nuachentra #shorts" --schedule "YYYY-MM-DD HH:MM"`
  - Lệnh hẹn giờ hàng loạt chuỗi 5 video:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/schedule_5_tiktok_videos.py`
  - **QUY CHUẨN TIÊU ĐỀ & CAPTION TIKTOK (TỐI ƯU VIEW & TƯƠNG TÁC):**
    1. *Tuyệt đối không dùng chữ "Sách...", "Chương X", "Review sách":* Tránh kích hoạt tâm lý né tránh bài tập / quảng cáo của người xem.
    2. *Đưa Hook cảm xúc / nỗi đau / nghịch lý lên đầu:* (Ví dụ: "Vì sao ngày lễ Vu Lan có người cài hoa hồng, có người cài hoa trắng?", "Bao lâu rồi bạn chưa nhìn kỹ gương mặt mẹ?").
    3. *Hashtag tập trung cảm xúc đời sống:* `#nuachentra #nhinsoudesongnhe #giadinh #me #baihoccuocsong #tamtrang`.
- **ĐỒNG BỘ NGUYÊN LIỆU LÊN GOOGLE DRIVE (CHO MÁY B RENDER):**
  - **QUY CHUẨN THƯ MỤC OUTPUT VÀ ĐÓNG GÓI NGUYÊN LIỆU (LOCAL & CLOUD DRIVE):**
    1. *Tổ chức theo thư mục con riêng biệt:* Mỗi video được lưu trong thư mục `output/{video_id}/` (vd: `output/essay_ep01/`, `output/essay_ep02/`).
    2. *Thư mục con `input/` lưu trữ công thức gốc:* Mỗi video bắt buộc có thư mục con `output/{video_id}/input/` chứa đầy đủ: `video_data.json` (timeline/sub/phân cảnh), `voiceover.wav` (audio giọng đọc đã master), `script.json` và `script.md` (kịch bản chi tiết).
    3. *Đồng bộ trọn gói lên Google Drive:* Thư mục `{video_id}/` trên Google Drive cũng tự động tạo thư mục con `input/` và chứa đầy đủ các file input này để lưu trữ và tái tạo độc lập 100%. Thư mục `remotion-video/public/` chỉ là nơi staging trung gian khi render.
    4. *File thông tin kèm theo:* Trong mỗi thư mục con luôn có file `info.json` chứa đầy đủ: tiêu đề, mô tả, hashtag, lịch đăng, đường dẫn link YouTube và kích thước file.
    5. *Tự động dọn dẹp bản cũ:* Khi render hoặc xuất bản video mới, pipeline tự động giữ lại duy nhất video hoàn thiện cuối cùng và xóa sạch các bản nháp/test trung gian để tiết kiệm dung lượng ổ đĩa.
  - **QUY CHUẨN KHO TÀI NGUYÊN B-ROLL KHÔNG TRÙNG LẶP & CLOUD BACKUP (ASSETS HUB - CHUẨN NATIVE 16:9):**
    1. *Tách biệt độc lập 100% giữa Short và Long:* Dự án Long Video có kho `assets_hub/` riêng biệt, chỉ chứa tài nguyên ngang chuẩn **16:9 (1920x1080 hoặc 4K ngang)**. Bắt buộc 100% video/ảnh là **quay ngang nguyên bản (Native 16:9 Horizontal)**, tuyệt đối cấm tải video dọc 9:16 rồi zoom crop làm vỡ hạt, mờ pixel.
    2. *Thư mục lưu trữ tập trung:* `assets_hub/images/` & `assets_hub/videos/`.
    3. *Sổ theo dõi chống trùng (Registry):* `assets_hub/asset_registry.json` lưu trữ thông tin: SHA256 Hash, loại file, kích thước, số lần sử dụng (`usage_count`) và danh sách video đã dùng (`used_in: ["essay_ep01", ...]`).
    4. *Tự động sao lưu lên Google Drive:* Mỗi khi có video B-roll hoặc ảnh tĩnh mới được nạp vào kho qua pipeline, hệ thống tự động tải lên thư mục riêng `Video_Render/Long_Video/Assets_Hub/videos/` hoặc `Video_Render/Long_Video/Assets_Hub/images/` trên Google Drive để backup vĩnh viễn.
  - Thư mục Short Video: `G:\Drive của tôi\Video_Render\Short_Video\`
  - Thư mục Long Video: `G:\Drive của tôi\Video_Render\Long_Video\`
  - Cấu trúc gói trên Drive: `pkg_{video_id}/` (chứa JSON, Audio, B-roll, `run_render.bat`, `post_info.json` và thư mục con `output/` để nhận video render xong từ Máy B).
  - Lệnh đóng gói 1-click lên Google Drive:
  - Lệnh tự động kéo video từ Drive (thư mục output/) và đăng YouTube/TikTok:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/publish_from_drive.py [video_id]`
- **TỰ ĐỘNG RENDER TRÊN GITHUB ACTIONS (CLOUD WORKER - STUDIO QUALITY CỰC ĐẠI):**
  - Repo GitHub: `LuuHuuPhuc84/long_video` (Public Repo - Render miễn phí không giới hạn phút).
  - Cấu hình chất lượng Studio tối đa: Remotion render với `--crf=18` (cân bằng hoàn hảo tốc độ và độ sắc nét cao), `--pixel-format=yuv420p`, `--audio-bitrate=320k`, `--concurrency=2` (ổn định RAM runner), bổ sung bộ font tiếng Việt (`fonts-noto`, `fonts-noto-cjk`, `fonts-roboto`, `fonts-dejavu-core`) đảm bảo chữ và hình ảnh sắc nét tuyệt đối.
  - Mô hình: *Ephemeral Render Worker (Zero-Download)*:
    + Chỉ nạp Audio + B-roll của đúng video đó lên Git nhánh tạm.
    + GitHub Actions tự động render MP4 Full HD 1920x1080.
    + Tự động đẩy file video + metadata lên Google Drive.
    + Tự động đẩy thẳng video lên YouTube ở chế độ Nháp (Draft/Private) qua API v3.
    + Xóa sạch nhánh tạm và toàn bộ Workflow Run History trên GitHub sau khi hoàn tất (Zero-Trace).
    + Mặc định không tải video về máy tính để tiết kiệm 100% dung lượng ổ cứng (chỉ tải khi truyền `--download`).
  - Lệnh render 1-click qua GitHub Actions:
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/render_on_github.py [video_id]`
- **HỆ THỐNG SAO LƯU DỰ PHÒNG ANTIGRAVITY (WEEKLY CLOUD BACKUP):**
  1. *Phạm vi sao lưu:* Toàn bộ cấu hình Antigravity (`%USERPROFILE%\.gemini\antigravity\`), pipeline và scripts của cả 2 dự án (`Long video` và `short video`) được tự động nén zip và tải lên Google Drive tại:
     `G:\Drive của tôi\Video_Render\Antigravity_System_Backup/`.
  2. *Lập lịch tự động hàng tuần:* Chạy tự động lúc **23:00 Chủ nhật hàng tuần** qua Windows Task Scheduler (`AntigravityWeeklyBackup`).
  3. *Lệnh sao lưu thủ công:*
     `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/backup_antigravity.py`
  4. *Khôi phục trên máy tính mới (1-click):* Tải thư mục backup từ Drive về máy mới và chạy:
     `python restore_antigravity.py` (đi kèm hướng dẫn chi tiết trong file `HUONG_DAN_KHOI_PHUC_MAY_MOI.md`).
- **QUY CHUẨN ĐỔI TÊN FILE CŨ TRƯỚC KHI RENDER LẠI (PRE-RENDER ARCHIVE & ANTI-COLLISION BẮT BUỘC CHO CẢ 2 DỰ ÁN):**
  1. *Nguyên nhân cốt lõi:* Khi render lại cùng một `video_id`, Google Drive và máy Local giữ lại file video cũ mang tên `video_{video_id}.mp4`. Google Drive không ghi đè mà lưu nhiều file cùng tên hoặc sinh đuôi `(1)`, khiến script kiểm tra nhầm tưởng video đã xong và kéo nhầm bản cũ về máy.
  2. *Quy tắc bắt buộc trước khi render lại (Pre-render Archival):*
     - Trước khi bắt đầu render lại bất kỳ video nào (cả render Local lẫn dispatch GitHub Actions Cloud Worker), pipeline BẮT BUỘC phải chạy hàm kiểm tra và đổi tên toàn bộ file cũ trên CẢ MÁY LOCAL VÀ GOOGLE DRIVE.
     - **Công thức đổi tên:** `tên_mới = {tên_file_cũ}_{ký_tự_ngẫu_nhiên}.mp4` (vd: `video_essay_ep04.mp4` -> `video_essay_ep04_a8f2k.mp4`).
     - Module chuẩn hóa: `pipeline/archive_render.py` (gọi hàm `archive_previous_renders(video_id)` trước bước render).
  3. *Hiệu quả giải phóng 100%:*
     - Tên file chính thức `video_{video_id}.mp4` hoàn toàn sạch bóng trên cả Local và Google Drive trước khi render bắt đầu.
     - Khi GitHub Actions render xong và đẩy file mới lên Google Drive, Drive chỉ có duy nhất 1 file mang tên chuẩn `video_{video_id}.mp4`, không sinh đuôi `(1)`.
     - Script theo dõi (`check_video_ready_on_drive`) và đồng bộ (`download_video_from_drive`) chỉ nhận diện chính xác 100% file vừa render mới xong, triệt tiêu hoàn toàn khả năng kéo nhầm bản cũ.
     - Bản cũ vẫn được bảo tồn nguyên vẹn trên cả Local và Cloud dưới tên gắn mã ngẫu nhiên để an toàn dữ liệu, không bị ghi đè hay mất mát.
- **QUY CHUẨN XUẤT KỊCH BẢN RA EXCEL (BẮT BUỘC CHO CẢ 2 DỰ ÁN):**
  1. *Nguyên tắc bắt buộc:* Sau khi tạo hoặc render xong bất kỳ video nào (cả Short Video và Long Video, dù render local hay qua GitHub Actions), pipeline BẮT BUỘC phải tự động gọi hàm xuất/cập nhật kịch bản vào file Excel tương ứng (`scripts_short_video.xlsx` hoặc `scripts_long_video.xlsx`).
  2. *Cấu trúc:* Mỗi video sở hữu 1 sheet riêng biệt với tên sheet là `video_id`.
  3. *Nội dung sheet:* Gồm phần thông tin tổng quan (Video ID, Tiêu đề, Tác giả, Thời lượng, Link YouTube, Lịch đăng) và bảng phân cảnh chi tiết (Cảnh #, Voiceover, Highlight Text, Visual/B-roll, Timing).
  4. *Lệnh xuất thủ công khi cần:*
     - Cho Short Video: `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/export_scripts_excel.py [--video-id video_id]`
     - Cho Long Video: `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/export_scripts_excel.py --project long [--video-id video_id]`
- **LỆNH DỌN DẸP Ổ ĐĨA & THU HỒI DUNG LƯỢNG LOCAL (CLEAN DISK):**
  - Chạy kiểm tra dung lượng rác (không xóa):
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/clean_disk.py --dry-run`
  - Chạy dọn sạch rác tự động cho cả 2 dự án (Short Video & Long Video):
    `& "E:\Programs\vieneu-env\Scripts\python.exe" pipeline/clean_disk.py`
  - *Cơ chế an toàn:* Xóa sạch cache build Remotion, dọn `downloads/`, dọn staging `public/` (chỉ giữ nhạc nền và chuông thiền), thu hồi bộ nhớ `.git/` (`git gc --prune=now`). Tuyệt đối không xóa video `output/` hay nguyên liệu `input/`.
- **QUY CHUẨN ĐẶT TIÊU ĐỀ YOUTUBE & KHUNG PROMPT CHUẨN (PACKAGING CHO LONG VIDEO & SHORTS):**
  1. *Triết lý chung (YouTube Packaging — Quy tắc 1 + 1 = 3):*
     - Tiêu đề và Thumbnail / Hook text không bao giờ lặp lại nguyên văn mà tung hứng cho nhau (Thumbnail/Hook khơi gợi thị giác & gây tò mò, Tiêu đề mở rộng bối cảnh & chạm đúng nỗi niềm).
     - Tuyệt đối không spoil câu trả lời / kết luận trong tiêu đề (tránh làm người lướt đọc xong thấy đã đủ).
     - Giữ giọng điệu điềm đạm, chiêm nghiệm, ấm áp và sâu lắng của "Nửa Chén Trà" (triệt để cấm clickbait rẻ tiền, giật gân, thô thiển).
     - Không viết hoa toàn bộ (All Caps), không chèn số tập (#01, #02), không chèn tên kênh vào tiêu đề.
  2. *Khung Prompt chuẩn cho YouTube Long Video (Dưới 55 ký tự):*
     - *Quy chuẩn kỹ thuật:* Tiêu đề dài tối đa **55 ký tự** (tính cả dấu cách) để hiển thị trọn vẹn 100% trên điện thoại mà không bị cắt ba chấm `...`. Bắt buộc ghi rõ `[số ký tự]` ở cuối mỗi gợi ý.
     - *Mẫu prompt chuẩn:*
       ```markdown
       Bạn là chuyên gia tư vấn đóng gói nội dung (packaging) cho kênh YouTube chủ đề triết lý sống, tản văn, tĩnh tâm và chữa lành (Kênh: "Nửa Chén Trà").

       Hãy giúp tôi đặt tiêu đề YouTube cho video tiếp theo dựa trên thông tin sau:
       - Chủ đề chính / Tóm tắt nội dung video: [Dán tóm tắt nội dung hoặc ý tưởng video vào đây]
       - Cảm xúc / Thông điệp cốt lõi muốn gửi gắm: [Ví dụ: Giúp người nghe buông bỏ kỳ vọng, bớt mệt mỏi nội tâm...]
       - Ý tưởng hình ảnh & Text trên thumbnail dự kiến: [Ví dụ: Hình ảnh tách trà nghiêng bóng hoàng hôn, chữ trên ảnh: "Thôi chấp niệm"]

       Yêu cầu kỹ thuật & phong cách đặt tiêu đề:
       1. Độ dài: Tối đa 55 ký tự (tính cả dấu cách) để hiển thị trọn vẹn 100% trên giao diện điện thoại. Ghi rõ [số ký tự] ở cuối mỗi tiêu đề.
       2. Quy tắc nội dung & Packaging:
          - Tạo "khoảng trống tò mò" (Curiosity Gap) hoặc chạm trúng nỗi trăn trở nội tâm, sự mệt mỏi thầm kín của người xem.
          - Không tiết lộ ngay bài học/kết luận trong tiêu đề (tránh làm người lướt đọc xong thấy đã đủ câu trả lời).
          - Tung hứng ăn ý với Thumbnail: Không lặp lại chữ trên thumbnail; Thumbnail tạo ấn tượng thị giác, Tiêu đề khơi gợi câu hỏi hoặc mở ra bối cảnh.
          - Không giật tít câu view rẻ tiền, giữ giọng điệu chiêm nghiệm, điềm đạm, sâu lắng.
          - Không viết hoa toàn bộ (All Caps), không chèn số tập (#01, #02), không để tên kênh vào tiêu đề.

       Hãy đưa ra gợi ý theo 2 nhóm (mỗi nhóm 3-4 phương án):
       1. Nhóm 'Hợp phong cách kênh': Nhẹ nhàng, trầm lắng, triết lý gần gũi, tạo cảm giác được vỗ về, chữa lành.
       2. Nhóm 'Tăng tương tác & kích thích tò mò': Đặt góc nhìn sắc bén, đặt câu hỏi hoặc khơi mào mâu thuẫn cảm xúc khiến người xem muốn bấm vào tìm câu trả lời (phù hợp để làm A/B Test).
       ```
  3. *Khung Prompt chuẩn cho YouTube Shorts (25 – 40 ký tự + 2 hashtag):*
     - *Quy chuẩn kỹ thuật:* Phần tiêu đề chữ dài từ **25 đến 40 ký tự**. Tổng chuỗi (Tiêu đề + 2 hashtag ngắn như `#chualanh #shorts`) không vượt quá **55 ký tự** để không bị giao diện Shorts di động che khuất.
     - *Phối hợp Hook 1.5s đầu:* Title Hook trên màn hình (Frame 0–1.5s) đập vào mắt người xem; tiêu đề bên dưới giữ chân và kích hoạt hành vi "Lưu lại" (Save/Loop) để nghe lại ban đêm.
     - *Mẫu prompt chuẩn:*
       ```markdown
       Bạn là chuyên gia sáng tạo nội dung YouTube Shorts cho kênh tản văn, triết lý sống, chữa lành và tĩnh tâm (Kênh: "Nửa Chén Trà").

       Hãy giúp tôi đặt tiêu đề cho video Shorts tiếp theo dựa trên thông tin sau:
       - Câu nói hay nhất / Đoạn trích đắt giá trong video: [Dán câu nói đắt giá nhất hoặc tóm tắt 30-45 giây nội dung vào đây]
       - Cảm xúc cốt lõi của người xem: [Ví dụ: Thấy nhẹ nhõm, bừng tỉnh, được vỗ về khi cô đơn, bớt dằn vặt bản thân...]
       - Chữ hiển thị trên màn hình ở 3 giây đầu (Hook Text): [Dán dòng chữ Hook trên video nếu có]

       Yêu cầu kỹ thuật & phong cách đặt tiêu đề Shorts:
       1. Độ dài: Cực kỳ tinh gọn, từ 25 đến 40 ký tự (không tính hashtag). Tổng độ dài (Tiêu đề + 2 hashtag) không vượt quá 55 ký tự để hiển thị nguyên vẹn 100% trên giao diện Shorts điện thoại. Ghi rõ [số ký tự] ở mỗi câu.
       2. Phối hợp với Hook 3 giây đầu:
          - Tiêu đề bên dưới KHÔNG lặp lại dòng chữ Hook trên màn hình.
          - Dòng chữ trên màn hình đánh thức sự chú ý, dòng tiêu đề bên dưới giữ chân người xem và chạm vào một nỗi niềm cụ thể.
       3. Yếu tố kích thích tương tác ngầm:
          - Tạo cảm giác đồng cảm sâu sắc khiến người nghe muốn bấm "Lưu lại" (Save) để nghe lại khi tĩnh lặng hoặc trước lúc ngủ.
          - Giữ giọng điệu mộc mạc, tĩnh lặng, ấm áp của "Nửa Chén Trà"; tuyệt đối không dùng từ ngữ giật gân, câu view rẻ tiền.
       4. Hashtag: Mỗi gợi ý tự động đính kèm đúng 2 hashtag ngắn gọn ở cuối (ví dụ: #chualanh #shorts hoặc #tamly #shorts).

       Hãy đưa ra các gợi ý theo 3 phong cách sau (mỗi phong cách 2-3 phương án):
       1. Nhóm 'Chạm cảm xúc': Ngắn gọn, ấm áp, như một cái ôm cho tâm hồn đang mệt mỏi.
       2. Nhóm 'Chiêm nghiệm sâu sắc': Một góc nhìn lạ hoặc một câu hỏi tự vấn khiến người lướt phải dừng lại suy ngẫm.
       3. Nhóm 'Lời nhắn nhủ': Lời thì thầm nhắc nhở bản thân buông bỏ bớt gánh nặng và sống chậm lại.
       ```

## Backlog ý tưởng
- [x] Chương 1: Tiếng Chuông Thức Tỉnh, Dập Tắt Mọi Cơn Giận (Chương 1 - Nghe chuông và chắp tay)
- [x] Chương 2: Bài Tập 60 Giây Thở Và Mỉm Cười, Giải Tỏa Căng Thẳng (Chương 2 - Ngồi thở và kinh hành: Tĩnh lặng - Mỉm cười - Hiện tại - Tuyệt vời)
- [x] Chương 3: Phép Lạ Là Đi Trên Mặt Đất, Tự Tại Từng Bước Chân (Chương 3 - Thiền hành: Ẩn dụ phi hành gia & Đi mà không tới)
- [x] Chương 4: Nghệ Thuật Uống Một Chén Trà (Chương 4 - Thiền trà)
- [x] Chương 5: Rửa Bát Để Rửa Bát Hay Rửa Bát Để Xem Tivi? (Chương 5 - Chánh niệm trong mọi việc)
- [x] Chương 6: Bạn Có Đang Sở Hữu Hàng Trăm Hạnh Phúc? (Chương 6 - Bài học 'không đau răng', chuyển xả thọ thành lạc thọ)
- [x] Chương 7: Ôm Ấp Cơn Giận Như Mẹ Ôm Con Thơ (Chương 7 - Tứ niệm xứ)
- [x] Chương 8: 24 Giờ Tinh Khôi Mỗi Sáng (Phụ lục - Thi kệ thực tập)
- [x] Bông Hồng Cài Áo - Video 1: Chiếc Hoa Trắng Ở Tokyo (Nguồn gốc bông hồng cài áo & nỗi lòng kẻ mồ côi)
- [x] Bông Hồng Cài Áo - Video 2: Bữa Cơm Cuối Cùng Của Chị (Nỗi lòng người mẹ khi con cái lớn khôn)
- [x] Bông Hồng Cài Áo - Video 3: Tại Sao Ngọc Hoàng Không Hạnh Phúc Bằng Bạn? (Thương mẹ là sự hưởng thụ)
- [x] Bông Hồng Cài Áo - Video 4: Cả Đời Bên Mẹ Nhưng Chưa Từng Nhìn Kỹ (Bi kịch vô tâm của người bận rộn)
- [x] Bông Hồng Cài Áo - Video 5: Câu Hỏi 30 Giây: "Mẹ Có Biết Không?" (Bài tập chánh niệm yêu thương)
- [x] Giận - Video 1: Nhà Đang Cháy, Đừng Đuổi Theo Kẻ Châm Lửa (`gian_v1` - Cứu căn nhà tâm hồn)
- [x] Giận - Video 2: Cơn Giận Là Một Đứa Bé Đang Khóc (`gian_v2` - Chăm sóc em bé sân hận)
- [x] Giận - Video 3: Người Làm Vườn Giỏi Không Vứt Rác (`gian_v3` - Biến rác thành hoa)
- [x] Giận - Video 4: Một Hòn Sỏi Trong Túi Áo Giữ Bạn Khỏi Lời Nói Đau (`gian_v4` - Tiếng chuông nhắc dừng)
- [x] Giận - Video 5: Đừng Cãi Nhau Ngay, Hãy Hẹn Tối Thứ Sáu (`gian_v5` - Nghệ thuật làm hòa)

## Nhật ký Short Video (Chuỗi 5 Video "GIẬN" — 9:16)
| Video ID | Tiêu đề | Chủ đề / Sách | Thời lượng | Kích thước | Micro-CTA | File Output |
|---|---|---|---|---|---|---|
| `gian_v1` | NHÀ ĐANG CHÁY, ĐỪNG ĐUỔI THEO KẺ CHÂM LỬA | Giận (Thiền sư Thích Nhất Hạnh) | 40.57s | 42.93 MB | BÌNH LUẬN "THỞ" | `output/gian_v1/video_gian_v1.mp4` |
| `gian_v2` | CƠN GIẬN LÀ MỘT ĐỨA BÉ ĐANG KHÓC | Giận (Thiền sư Thích Nhất Hạnh) | 44.56s | 72.51 MB | BÌNH LUẬN "ÔM" | `output/gian_v2/video_gian_v2.mp4` |
| `gian_v3` | NGƯỜI LÀM VƯỜN GIỎI KHÔNG VỨT RÁC | Giận (Thiền sư Thích Nhất Hạnh) | 41.21s | 49.48 MB | BÌNH LUẬN "HOA" | `output/gian_v3/video_gian_v3.mp4` |
| `gian_v4` | MỘT HÒN SỎI TRONG TÚI ÁO GIỮ BẠN KHỎI LỜI NÓI ĐAU | Giận (Thiền sư Thích Nhất Hạnh) | 42.79s | 65.53 MB | BÌNH LUẬN "SỎI" | `output/gian_v4/video_gian_v4.mp4` |
| `gian_v5` | ĐỪNG CÃI NHAU NGAY, HÃY HẸN TỐI THỨ SÁU | Giận (Thiền sư Thích Nhất Hạnh) | 44.85s | 31.99 MB | BÌNH LUẬN "HẸN" | `output/gian_v5/video_gian_v5.mp4` |

> [!NOTE]
> Toàn bộ 5 video đã áp dụng chuẩn Studio: 100% Native 9:16 Vertical B-roll không trùng lặp, Vietneu-TTS Đức Trí 0.95, gieo nhịp thở bằng dấu phẩy, Sidechain Ducking BGM, EBU R128 (-14 LUFS), Micro-CTA 1 từ khóa ở 2-3s cuối, Title Hook Frame 0-1.5s tối ưu làm thumbnail Shorts, thư mục con `input/` lưu công thức gốc và tự động đồng bộ vào `scripts_short_video.xlsx`.

## Nhật ký video (Long Video 16:9)
| Ngày | Tiêu đề | Chủ đề | Nền tảng | Output | Ghi chú |
|------|---------|--------|----------|--------|---------|
| 13/10/2026 | NÓNG GIẬN VỚI NGƯỜI THÂN: BẢN NĂNG HAY SỰ BẤT LỰC? | Triết lý ứng dụng đời thường • Nửa Chén Trà | YouTube (16:9) | `output/essay_ep01/video_essay_ep01.mp4` | 8m 42s (70.2 MB). **Đã đăng YouTube**. Đã đóng gói input/ và Drive. |
| 15/10/2026 | TÂM THÁI BÌNH THƯỜNG LÀ ĐẠO: BÍ QUYẾT AN YÊN GIỮA ĐỜI | Triết lý ứng dụng đời thường • Nửa Chén Trà | YouTube (16:9) | `output/essay_ep02/video_essay_ep02_tam_thai_binh_thuong.mp4` | 11m 18s (368.9 MB). **Đã đăng YouTube**. Đã đóng gói thumbnail, input/ và Drive. |
| 17/10/2026 | BUÔNG BỎ MUỘN PHIỀN ĐỂ ĐỜI NHẸ TÊNH | Triết lý ứng dụng đời thường • Nửa Chén Trà | YouTube (16:9) | `output/essay_ep03/video_essay_ep03_buong_bo_muon_phien.mp4` | 13m 20s (314.2 MB). **Đã đăng YouTube:** [S8J_4AJfYgU](https://youtu.be/S8J_4AJfYgU). Đã đóng gói thumbnail, input/ và Drive. |
| 18/10/2026 | CÁCH THỨ BA KHI NỔI GIẬN: KHÔNG ĐÈ NÉN, KHÔNG BÙNG NỔ | Triết lý ứng dụng đời thường • Nửa Chén Trà | YouTube (16:9) | `output/essay_ep04/video_essay_ep04.mp4` | 5m 31s (428.5 MB). **Đã đăng YouTube:** [wJblFje-tGM](https://youtu.be/wJblFje-tGM). Thumbnail Bản A. Đã đóng gói input/, Drive và Excel. |
| 18/10/2026 | MẸ GIÀ ĐI TỪ LÚC NÀO MÀ TA KHÔNG ĐỂ Ý? | Triết lý ứng dụng đời thường • Nửa Chén Trà | YouTube (16:9) | `output/essay_ep05/video_essay_ep05.mp4` | 5m 39s. **Đã đăng YouTube:** [QcNQtYBvb5E](https://youtu.be/QcNQtYBvb5E) (Hẹn giờ: 19h30 19/10/2026). 100% B-roll Thiên nhiên. 100% Nhạc sạch không bản quyền (*On A Piano Cloud*). Thumbnail Cinematic Mẹ nhìn ra biển. Đã đóng gói input/, Drive và Excel. |

## Bài học rút ra (từ số liệu)
- (vd: hook dạng câu hỏi giữ chân tốt hơn câu trích)

## Quy tắc kênh (đừng lặp lại sai lầm)
- Không bịa hoặc gán nhầm trích dẫn; không chắc thì bỏ.
- Không đọc/chép nguyên văn bài báo; chỉ dùng làm nguyên liệu và viết lại bằng lời mình.
- Một bài nhiều câu chuyện → tách thành nhiều video.
- Không dùng nhạc/hình không rõ bản quyền.

## Chưa quyết định
- Tên kênh, phong cách hình ảnh, tần suất đăng, nguồn nhạc nền.