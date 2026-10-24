# MEMORY.md — Bộ nhớ dự án

> Agent đọc file này đầu mỗi phiên và cập nhật khi có quyết định mới. Chỉ ghi điều đã chốt.

## Quyết định đã chốt
- Chủ đề: Bài học cuộc sống, triết lý ứng dụng đời thường; chắt lọc từ "An Trú Trong Hiện Tại" của Thiền sư Thích Nhất Hạnh & trí tuệ cổ xưa.
- Định vị nội dung: **Độc lập 100% (Standalone Shorts)**. Tuyệt đối không để chữ "Chương X" hay "Tập X" để tránh gây rào cản cho người xem ngẫu nhiên.
- Nhận diện sách & tác giả: Đưa Tên sách ("AN TRÚ TRONG HIỆN TẠI") và Tác giả **"Thiền sư Thích Nhất Hạnh"** thành thanh badge nhỏ tinh tế ở góc trên, KHÔNG dùng Hero Header lớn che kín 3 giây đầu.
- **QUY CHUẨN VIDEO SHORTS MỚI (ÁP DỤNG TỪ VIDEO TIẾP THEO):**
  1. *Thời lượng & Dung lượng chữ:* Khung thời lượng chuẩn vàng là **38s – 42s** (dung lượng lý tưởng **90 – 100 từ** ở tốc độ TTS 0.95 có nhịp thở 0.28s) để vừa bảo đảm tối ưu Retention (APV > 75–85% với tổng Watch Time cao ~32s+), vừa có đủ chiều sâu câu chuyện và "độ lắng" cảm xúc (Emotional Breathing Room) chạm đến trái tim người xem, không bị vội vã.
  2. *Hook 3 giây đầu:* Đánh thẳng vào nỗi đau / nghịch lý đời thực (stress, overthinking, mất ngủ, nóng giận), giao diện thoáng, chữ Hook lớn nổi bật.
  3. *Hình ảnh & B-roll:* Chuyển sang dùng **Video B-roll chuyển động cinematic** (khói trà, mưa rơi, rừng cây, nước chảy...) hoặc Hybrid (Hook bắt buộc là video B-roll). Chuyển cảnh nhịp 2–3s/cảnh.
  4. *Giọng đọc & Nhịp điệu (TTS):* Vietneu-TTS giọng Đức Trí hoặc giọng clone mẫu **"laytutritueconhan"** (trích xuất từ `mau.mp3`, giọng chiêm nghiệm sâu lắng, đĩnh đạc) tốc độ chuẩn **0.95** (chậm rãi, trầm ấm, đĩnh đạc, đúng chất kể chuyện chiêm nghiệm).
  5. *Quy chuẩn xử lý âm thanh tự nhiên (Audio Mastering):*
     - *Gieo nhịp thở (Phrase Chunking):* Chia câu thành các cụm từ ngắn có nghĩa bằng dấu phẩy `,` để AI tự động lấy hơi và hạ giọng tự nhiên như người thật.
     - *Khử giật & tiếng khựng:* Áp dụng Micro-fade (25ms in / 35ms out) và khoảng nghỉ nhịp thở **0.28s** giữa các câu.
     - *Hòa âm Sidechain Ducking:* Nhạc nền Piano tự thở (lùi xuống 8–10% khi có lời thoại, nổi lên 16–18% ở các khoảng nghỉ ngắt câu).
     - *Broadcast Warmth EQ & EBU R128:* Tăng dải trầm 220Hz tạo độ dày ấm, giảm chói gắt 6000Hz, chuẩn hóa độ to -14 LUFS cho YouTube Shorts / TikTok.
  7. *CTA (Keyword Comment Hook - Tối ưu tương tác 1 từ khóa):*
     - *Nguyên tắc:* Tuyệt đối không dùng câu hỏi mở mơ hồ (bắt người xem nghĩ và gõ dài gây lười comment). Sử dụng kỹ thuật Micro-CTA yêu cầu gõ một từ khóa cụ thể, ngắn gọn (1–2 phím chạm) để giảm lực cản hành động (Cognitive Friction = 0), kích hoạt thuật toán phân phối viral.
     - *Đồng bộ 2 lớp ở 2–3 giây cuối:*
       + *Lời đọc (Voiceover):* Câu chốt kêu gọi hành động trực tiếp. (Ví dụ: *"Nếu bạn vừa thở một hơi thật sâu, hãy bình luận chữ 'ĐÃ THỞ' nhé."*, *"Hôm nay bạn đã gọi cho mẹ chưa? Hãy bình luận 'RỒI' hoặc 'CHƯA'."*, *"Cầu chúc bạn một đêm an giấc, để lại chữ 'AN' nhé."*).
       + *Chữ trên màn hình (Highlight Text):* Thẻ chữ nổi bật cỡ lớn, màu vàng hổ phách `#fbbf24`, hiển thị rõ ràng từ khóa cần gõ (ví dụ: `BÌNH LUẬN "ĐÃ THỞ"`, `BÌNH LUẬN "RỒI" / "CHƯA"`).
- **QUY CHUẨN ÂM NHẠC BẮT BUỘC (ZERO COPYRIGHT CLAIM POLICY - 100% NHẠC SẠCH KHÔNG BẢN QUYỀN):**
  1. *Nguyên tắc triệt để:* Tuyệt đối KHÔNG sử dụng các bài nhạc lofi/ambient trôi nổi có đăng ký bảo hộ Content ID qua các bên thứ ba như HAAWK, Identifyy, Audiam, CD Baby, Believe Music (bài học: bản nhạc *Lofi Study* của FASSounds từng bị HAAWK claim từ 2:27 đến 5:39 ở tập 5).
  2. *Nguồn nhạc hợp lệ duy nhất:*
     - Thư viện âm thanh YouTube (YouTube Audio Library - No Attribution Required).
     - Tác phẩm CC0 / Creative Commons không Content ID của Kevin MacLeod (Incompetech).
     - Nhạc piano thiền định của Liborio Conti (*On A Piano Cloud*, *Tranquil Reflections*) không đăng ký Content ID.
     - Nhạc tự sản xuất hoặc Public Domain (CC0).
  3. *Lưu trữ chuẩn:* File nhạc nền chính thức được đặt tại `remotion-video/public/background_music.mp3` của cả 2 dự án (bản chuẩn hiện tại là *On A Piano Cloud*, 20 phút piano ambient thư thái, an toàn 100% không Content ID).
- **QUY CHUẨN BẮT BUỘC TẠO THUMBNAIL CHO SHORTS & DUYỆT THỊ GIÁC (MỚI CHỐT):**
  1. *Bắt buộc tạo file Thumbnail riêng (1080x1920):* Do YouTube Shorts đã mở tính năng upload ảnh bìa (Upload file) trực tiếp từ PC, mỗi video Shorts khi sản xuất BẮT BUỘC phải tạo 1 file ảnh thumbnail riêng (`thumbnail_{video_id}.jpg`).
  2. *Bắt buộc đưa Thumbnail vào thư mục `input/` để duyệt:* File ảnh thumbnail BẮT BUỘC phải được lưu trong thư mục `output/{video_id}/input/` để người dùng mở kiểm tra và duyệt trực tiếp cùng với toàn bộ nguyên liệu trước khi kích hoạt render.
  3. *Tiêu chuẩn thiết kế Thumbnail Shorts:*
     - *Tỷ lệ & Kích thước:* Chuẩn dọc 9:16 (1080 x 1920 Full HD).
     - *Hình ảnh nền:* Dùng hình ảnh AI nghệ thuật vẽ đúng bối cảnh, sâu lắng, chân thực và đậm chất cảm xúc của kịch bản.
     - *Title Hook đắt giá:* Chữ to (60–64px bold), tối đa 6–8 chữ (ví dụ: `"BỐ CHƯA TỪNG NÓI YÊU CON"`, `"MÓN ĂN KHÔNG MUA ĐƯỢC Ở ĐÂU"`), màu vàng hổ phách `#fbbf24` hoặc trắng viền đen tương phản cao. Thẻ kính mờ Zen Amber Glass viền vàng.
     - *Tọa độ Safe Zone vàng:* Nằm ở 1/3 phía trên khung hình (`top: 280px – 350px`), dưới badge thương hiệu/sách, tuyệt đối tránh vùng đáy và cạnh phải để không bị tên kênh và cụm nút tương tác của Shorts che.
  4. *BẮT BUỘC 1 GIÂY ĐẦU TIÊN CỦA VIDEO LÀ HÌNH THUMBNAIL (COVER FRAME TRICK):*
     - Do YouTube Shorts trên ứng dụng điện thoại chỉ cho phép kéo con trỏ chọn ảnh bìa từ các khung hình bên trong video, mỗi video Shorts khi render BẮT BUỘC phải chèn ảnh Thumbnail (`thumbnail_{video_id}.jpg`) vào đúng **1 giây đầu tiên (Frame 0 – 30 @ 30fps)** của video.
     - Frame 0 hiển thị 100% hình ảnh Thumbnail hoàn chỉnh 1080x1920 (kết hợp tranh AI + Title Hook nổi bật trong Safe Zone + Top Badge thương hiệu).
     - Từ Frame 24 đến 29: Cross-fade hòa tan mượt mà (5 frames) sang video B-roll chuyển động.
     - Khi người dùng đăng video Shorts trên điện thoại hoặc hệ thống tự động bắt frame đầu, chỉ cần chọn ngay Frame 0 (giây đầu tiên) là video có ngay ảnh bìa hoàn mỹ, chuyên nghiệp, giữ chân người xem.
     - Hơn 97% thời lượng còn lại (từ giây thứ 1 đến hết) là 100% Video B-roll chuyển động thực tế, bảo đảm an toàn tuyệt đối cho chính sách Bật kiếm tiền (YPP) của YouTube (hoàn toàn không bị tính là video slideshow tĩnh).

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
