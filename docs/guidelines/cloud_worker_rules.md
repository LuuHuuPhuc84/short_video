# QUY CHUẨN VẬN HÀNH CLOUD WORKER TRÊN GITHUB ACTIONS (ANTI-HANG & PERFORMANCE)

> **MỤC TIÊU:** Đảm bảo toàn bộ quy trình Cloud Render & Auto-Upload (Google Drive / YouTube) trên GitHub Actions diễn ra ổn định, tuyệt đối không bị treo vô hạn (Hung / Deadlock), tiết kiệm thời gian và tài nguyên máy ảo.

---

## 1. NGUYÊN NHÂN GỐC RỄ GÂY TREO WORKFLOW (POST-MORTEM & INCIDENT REPORT)

### Sự cố ngày 05/11/2026:
Workflow bị treo hơn 11 phút ở bước `📦 Cài đặt thư viện hệ thống cho Chromium & FFmpeg`:
1. **Thiếu biến môi trường `DEBIAN_FRONTEND=noninteractive`:** Trình quản lý gói `apt-get` bị block chờ người dùng nhập câu trả lời qua STDIN.
2. **Gói font chữ CJK khổng lồ (`fonts-noto-cjk`):** Chứa hàng chục ngàn ký tự Đông Á, dung lượng giải nén >1.2 GB làm nghẽn CPU/Disk I/O và treo `fc-cache`.
3. **Mạng APT Mirror bị nghẽn (TCP Timeout):** Mặc định `apt-get` không có timeout ngắn cho kết nối HTTP/TCP.
4. **Thiếu giới hạn thời gian chạy (`timeout-minutes`):** Mặc định GitHub Actions chạy tối đa 360 phút (6 tiếng).

### Sự cố ngày 11/11/2026:
Step cài đặt thư viện hệ thống bị timeout sau 4 phút (`Get:1 file:/etc/apt/apt-mirrors.txt Mirrorlist [144 B]`):
1. **Lỗi `mirror+file:/etc/apt/apt-mirrors.txt` Deadlock:**
   - Trên Ubuntu 22.04 runner của GitHub Actions, cơ chế phân giải `apt-mirrors.txt` qua geolocation Canonical thường xuyên bị nghẽn hoặc deadlock khi nhiều job chạy song song.
   - **Giải pháp:** Thay thế toàn bộ `mirror+file:/etc/apt/apt-mirrors.txt` bằng mirror trực tiếp Azure Ubuntu `http://azure.archive.ubuntu.com/ubuntu/` (kết nối nội bộ Azure tốc độ cao, không bao giờ bị nghẽn).
2. **Lệnh `apt-get install` thiếu Timeout:**
   - Cờ `-o Acquire::http::Timeout=20` trước đây chỉ được đặt ở `apt-get update`, còn `apt-get install` không có, dẫn đến việc bị treo vĩnh viễn ở pha tải 61 MB.
   - **Giải pháp:** Cấu hình file toàn cục `/etc/apt/apt.conf.d/99timeout` áp dụng cho mọi lệnh APT.
3. **Gói `fonts-noto` cồng kềnh:**
   - `fonts-noto` kéo theo 76 package (174 MB disk). Kênh Nửa Chén Trà chỉ cần font Tiếng Việt, đã có font riêng trong code và chỉ cần `fonts-roboto fonts-dejavu-core fonts-liberation`.
   - **Giải pháp:** Bỏ `fonts-noto`, chỉ cài các font nhẹ cần thiết.

---

## 2. QUY CHUẨN BẮT BUỘC ĐỂ KHÔNG BAO GIỜ BỊ LẠI

### Quy tắc 1: Luôn giới hạn `timeout-minutes`
- **Cấp Job:** Mọi job Render (`render` trong `render_short_video.yml` và `batch_render_shorts.yml`) **BẮT BUỘC** khai báo `timeout-minutes: 15`. Một video Shorts 30-45s chỉ cần 1.5 - 3 phút để render. Quá 15 phút là dấu hiệu bất thường và phải tự động fail ngay lập tức.
- **Cấp Step cài đặt hệ thống:** Khai báo `timeout-minutes: 6`.

### Quy tắc 2: Khóa biến môi trường `DEBIAN_FRONTEND=noninteractive`
Ở cấp độ job hoặc trước mỗi lệnh apt:
```yaml
env:
  DEBIAN_FRONTEND: noninteractive
```

### Quy tắc 3: Cấu hình APT với Azure Mirror & Timeout & Retries & No Recommends
```bash
# 1. Chống treo APT do mirror+file:/etc/apt/apt-mirrors.txt (dùng trực tiếp Azure Ubuntu mirror)
sudo sed -i 's|mirror+file:/etc/apt/apt-mirrors.txt|http://azure.archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2>/dev/null || true

# 2. Cấu hình Timeout và Retry toàn cục cho APT (tránh deadlock mạng)
echo 'Acquire::http::Timeout "20";' | sudo tee /etc/apt/apt.conf.d/99timeout
echo 'Acquire::https::Timeout "20";' | sudo tee -a /etc/apt/apt.conf.d/99timeout
echo 'Acquire::Retries "3";' | sudo tee -a /etc/apt/apt.conf.d/99timeout

# 3. Cập nhật và cài đặt thư viện cần thiết (loại bỏ fonts-noto cồng kềnh, chỉ cài font tối ưu)
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ffmpeg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
  libxcomposite1 libxdamage1 libxrandr2 libgbm1 fonts-roboto fonts-dejavu-core fonts-liberation
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libasound2 || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libasound2t64
```
- **Tuyệt đối CẤM:** Không thêm `fonts-noto-cjk` hoặc `fonts-noto` vào danh sách cài đặt.

### Quy tắc 4: Giám sát chủ động & Hủy sớm (Proactive Cancel)
- Khi đẩy Cloud Render, kiểm tra bằng lệnh:
  `python pipeline/cli.py cloud status`
- Nếu bất kỳ bước nào trong Job vượt quá **5 phút**, hệ thống tự động phát hiện và gửi lệnh cancel qua GitHub API thay vì để người dùng chờ đợi.
