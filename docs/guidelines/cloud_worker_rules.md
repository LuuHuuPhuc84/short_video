# QUY CHUẨN VẬN HÀNH CLOUD WORKER TRÊN GITHUB ACTIONS (ANTI-HANG & PERFORMANCE)

> **MỤC TIÊU:** Đảm bảo toàn bộ quy trình Cloud Render & Auto-Upload (Google Drive / YouTube) trên GitHub Actions diễn ra ổn định, tuyệt đối không bị treo vô hạn (Hung / Deadlock), tiết kiệm thời gian và tài nguyên máy ảo.

---

## 1. NGUYÊN NHÂN GỐC RỄ GÂY TREO WORKFLOW (POST-MORTEM & INCIDENT REPORT)

Sự cố ngày 05/11/2026: Workflow `render_short_video.yml` bị treo hơn 11 phút ở bước `📦 Cài đặt thư viện hệ thống cho Chromium & FFmpeg`.

### Các nguyên nhân cốt lõi:
1. **Thiếu biến môi trường `DEBIAN_FRONTEND=noninteractive`:**
   - Trình quản lý gói `apt-get` trên Ubuntu khi cài đặt một số gói phụ thuộc (như font cache, cấu hình font hoặc tzdata) có thể kích hoạt các câu hỏi cấu hình tương tác (`debconf`).
   - Trên môi trường CI/CD không có bàn phím tương tác (STDIN), tiến trình bị block vô hạn để chờ người dùng nhập câu trả lời.
2. **Gói font chữ CJK khổng lồ (`fonts-noto-cjk`):**
   - Gói `fonts-noto-cjk` chứa hàng chục ngàn ký tự Đông Á (Trung - Nhật - Hàn), dung lượng giải nén vượt quá 1.2 GB.
   - Khi cài đặt, tiến trình `fc-cache -fv` phải quét toàn bộ hệ điều hành, gây nghẽn 100% CPU/Disk I/O của runner ảo và có thể dẫn đến treo tiến trình (I/O deadlock). Video của kênh là Tiếng Việt đã có font nhúng riêng (`BeVietnamPro-Black`, `Montserrat`), hoàn toàn không cần gói CJK này.
3. **Mạng APT Mirror bị nghẽn (TCP Timeout):**
   - Mặc định `apt-get` không có timeout ngắn cho kết nối HTTP/TCP. Nếu một mirror của Canonical phản hồi chậm hoặc rớt gói tin, tiến trình cài đặt sẽ retry vô hạn.
4. **Thiếu giới hạn thời gian chạy (`timeout-minutes`):**
   - Mặc định của GitHub Actions là cho phép một Job chạy tối đa **360 phút (6 tiếng)**. Khi không khai báo `timeout-minutes`, nếu xảy ra lỗi kẹt mạng hoặc chờ STDIN, cả workflow sẽ treo suốt 6 tiếng mà không tự ngắt hay báo lỗi.

---

## 2. QUY CHUẨN BẮT BUỘC ĐỂ KHÔNG BAO GIỜ BỊ LẠI

### Quy tắc 1: Luôn giới hạn `timeout-minutes`
- **Cấp Job:** Mọi job Render (`render` trong `render_short_video.yml` và `batch_render_shorts.yml`) **BẮT BUỘC** khai báo `timeout-minutes: 15`. Một video Shorts 30-45s chỉ cần 1.5 - 3 phút để render. Quá 15 phút là dấu hiệu bất thường và phải tự động fail ngay lập tức.
- **Cấp Step cài đặt hệ thống:** Khai báo `timeout-minutes: 4`.

### Quy tắc 2: Khóa biến môi trường `DEBIAN_FRONTEND=noninteractive`
Ở cấp độ job hoặc trước mỗi lệnh apt:
```yaml
env:
  DEBIAN_FRONTEND: noninteractive
```

### Quy tắc 3: Cấu hình APT với Timeout & Retries & No Recommends
Không bao giờ chạy `sudo apt-get install -y` một cách trần trụi. Bắt buộc:
```bash
sudo apt-get update -o Acquire::Retries=3 -o Acquire::http::Timeout=20
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ffmpeg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
  libxcomposite1 libxdamage1 libxrandr2 libgbm1 fonts-noto fonts-roboto fonts-dejavu-core
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libasound2 || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libasound2t64
```
- **Tuyệt đối CẤM:** Không thêm `fonts-noto-cjk` vào danh sách cài đặt.

### Quy tắc 4: Giám sát chủ động & Hủy sớm (Proactive Cancel)
- Khi đẩy Cloud Render, kiểm tra bằng lệnh:
  `python pipeline/cli.py cloud status`
- Nếu bất kỳ bước nào trong Job vượt quá **5 phút**, hệ thống tự động phát hiện và gửi lệnh cancel qua GitHub API thay vì để người dùng chờ đợi.
