# 🤖 PingE5 — Bot Tự Động Duy Trì Microsoft 365 E5 Developer

Bot tự động thực hiện các tác vụ trên Microsoft Graph API (gửi email, ping SharePoint, upload file...) để duy trì hoạt động tài khoản **Microsoft 365 E5 Developer**, tránh bị thu hồi do không sử dụng.

Thông báo trạng thái được gửi về **Telegram**. Nội dung file log được tạo bởi **Google Gemini AI**.

---

## 📋 Danh sách biến môi trường cần cấu hình

| Biến | Mô tả | Lấy ở đâu |
|---|---|---|
| `TENANT_ID` | ID tenant của Microsoft | Azure Portal |
| `CLIENT_ID` | ID ứng dụng Azure | Azure App Registration |
| `CLIENT_SECRET` | Mật khẩu ứng dụng Azure | Azure App Registration |
| `USER_EMAIL` | Email tài khoản E5 | Email đăng ký E5 của bạn |
| `SHAREPOINT_SITE_ID` | ID của SharePoint Site | Graph Explorer hoặc script |
| `SHAREPOINT_DRIVE_ID` | ID của Drive trong SharePoint | Graph Explorer hoặc script |
| `GEMINI_API_KEY` | API key của Google Gemini AI | Google AI Studio |
| `TELEGRAM_BOT_TOKEN` | Token của Telegram Bot | @BotFather trên Telegram |
| `TELEGRAM_CHAT_ID` | ID chat để nhận thông báo | @userinfobot trên Telegram |

---

## 🔷 Phần 1: Cấu hình Microsoft Azure

### Bước 1: Lấy Tenant ID

1. Truy cập [Azure Portal](https://portal.azure.com/).
2. Tại trang chủ, tìm mục **Manage Microsoft Entra ID** → chọn **View**.
3. Tại trang **Overview**, sao chép giá trị **Directory (tenant) ID** → đây là `TENANT_ID`.

---

### Bước 2: Tạo App Registration & lấy Client ID

1. Ở menu bên trái, chọn **App registrations** → **New registration**.
   - **Name**: Đặt tên tùy ý, ví dụ `PingE5App`.
   - **Supported account types**: Chọn *Accounts in this organizational directory only*.
   - Nhấn **Register**.
2. Sau khi tạo xong, tại trang **Overview** của App:
   - Sao chép giá trị **Application (client) ID** → đây là `CLIENT_ID`.

---

### Bước 3: Tạo Client Secret

1. Trong menu bên trái, chọn **Certificates & secrets**.
2. Chọn tab **Client secrets** → **New client secret**.
3. Đặt mô tả và thời gian hết hạn → nhấn **Add**.
4. > ⚠️ **QUAN TRỌNG:** Sao chép ngay giá trị ở cột **Value** (không phải *Secret ID*). Sau khi rời trang này bạn sẽ không xem lại được. Đây là `CLIENT_SECRET`.

---

### Bước 4: Cấp quyền API (API Permissions)

1. Chọn **API permissions** → **Add a permission** → **Microsoft Graph**.
2. Chọn **Application permissions**.
3. Tìm và tích chọn các quyền sau:
   - `Mail.Send`
   - `Sites.ReadWrite.All`
   - `Files.ReadWrite.All`
   - `User.Read.All`
4. Nhấn **Add permissions**.
5. Nhấn **Grant admin consent for [tên tổ chức]** để kích hoạt quyền.

---

### Bước 5: Lấy SharePoint Site ID & Drive ID

#### Cách 1: Dùng Microsoft Graph Explorer (Nhanh nhất)

1. Truy cập [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) và đăng nhập.
2. **Lấy `SHAREPOINT_SITE_ID`**: Gửi GET request đến:
   ```
   https://graph.microsoft.com/v1.0/sites/root
   ```
   Trong kết quả JSON, tìm trường `id` → đây là `SHAREPOINT_SITE_ID`.

3. **Lấy `SHAREPOINT_DRIVE_ID`**: Gửi GET request đến:
   ```
   https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_SITE_ID}/drives
   ```
   Tìm Drive tên **Documents**, sao chép giá trị `id` → đây là `SHAREPOINT_DRIVE_ID`.

#### Cách 2: Dùng script Python có sẵn

1. Tạo file `.env` cùng thư mục với `filesharepoint.py`:
   ```env
   TENANT_ID=your_tenant_id
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   ```
2. Chạy script:
   ```bash
   python filesharepoint.py
   ```
3. Script sẽ tự động hiển thị `SHAREPOINT_SITE_ID` và `SHAREPOINT_DRIVE_ID`.

---

## 🟡 Phần 2: Cấu hình Google Gemini AI

Bot dùng Gemini để tạo nội dung ngẫu nhiên cho file log upload lên SharePoint.

### Lấy GEMINI_API_KEY

1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Đăng nhập bằng tài khoản Google.
3. Nhấn **Create API key** → chọn project (hoặc tạo mới).
4. Sao chép API key được tạo ra → đây là `GEMINI_API_KEY`.

> 💡 Nếu không cấu hình `GEMINI_API_KEY`, bot vẫn chạy bình thường nhưng file log sẽ dùng nội dung mặc định thay vì do AI tạo ra.

---

## 🟢 Phần 3: Cấu hình Telegram Bot

Bot gửi toàn bộ log và thông báo lỗi về Telegram để bạn theo dõi từ xa.

### Bước 1: Lấy TELEGRAM_BOT_TOKEN

1. Mở Telegram, tìm kiếm **@BotFather**.
2. Nhấn **Start** rồi gõ lệnh `/newbot`.
3. Làm theo hướng dẫn:
   - Đặt **tên** cho bot (ví dụ: `PingE5 Notifier`).
   - Đặt **username** (phải kết thúc bằng `bot`, ví dụ: `pinge5_bot`).
4. BotFather sẽ trả về một đoạn token dạng `1234567890:AAH...` → đây là `TELEGRAM_BOT_TOKEN`.

### Bước 2: Lấy TELEGRAM_CHAT_ID

1. Tìm kiếm **@userinfobot** trên Telegram.
2. Nhấn **Start**.
3. Bot sẽ trả về ID của bạn (dạng số, ví dụ: `987654321`) → đây là `TELEGRAM_CHAT_ID`.

### Bước 3: Kích hoạt bot

> ⚠️ Bắt buộc phải làm bước này, nếu không bot sẽ không thể gửi tin nhắn cho bạn.

Tìm username bot bạn vừa tạo trên Telegram (ví dụ `@pinge5_bot`) và nhấn **Start**.

### Kiểm tra nhanh

Dán URL sau vào trình duyệt (thay thông tin của bạn vào):
```
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage?chat_id=<TELEGRAM_CHAT_ID>&text=Hello!
```
Nếu điện thoại nhận được tin "Hello!" thì cấu hình đã đúng.

---

## ⚙️ Cấu hình GitHub Actions (Chạy tự động)

Vào repository GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, thêm lần lượt các secrets:

```env
# Microsoft Azure & SharePoint
TENANT_ID=           # Directory (tenant) ID từ Microsoft Entra ID
CLIENT_ID=           # Application (client) ID từ Azure App Registration
CLIENT_SECRET=       # Client secret từ Azure App Registration
USER_EMAIL=          # Email tài khoản E5, ví dụ: user@domain.onmicrosoft.com
SHAREPOINT_SITE_ID=  # ID của SharePoint site
SHAREPOINT_DRIVE_ID= # ID của Drive trong SharePoint

# Google Gemini AI (tuỳ chọn)
GEMINI_API_KEY=      # API key từ Google AI Studio

# Telegram Bot
TELEGRAM_BOT_TOKEN=  # Token từ @BotFather
TELEGRAM_CHAT_ID=    # Chat ID từ @userinfobot
```
