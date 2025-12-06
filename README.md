# Hướng dẫn lấy thông tin cấu hình (Environment Variables)

Tài liệu này hướng dẫn cách lấy các giá trị cần thiết để cấu hình file `.env` cho dự án.

## 1. Cấu hình Microsoft Azure & SharePoint
**Các biến:** `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `SHAREPOINT_SITE_ID`, `SHAREPOINT_DRIVE_ID`, `USER_EMAIL`

### Bước 1: Tạo App trên Azure Portal
1. Truy cập [Azure Portal](https://portal.azure.com/).
2. Tìm kiếm và chọn **App registrations**.
3. Chọn **New registration**.
    - Đặt tên (Name): Ví dụ `MySharePointApp`.
    - Supported account types: Chọn *Accounts in this organizational directory only*.
    - Nhấn **Register**.

### Bước 2: Lấy thông tin ID
Sau khi tạo xong, tại trang **Overview** của App, bạn sẽ thấy:
- **`CLIENT_ID`**: Sao chép giá trị tại dòng *Application (client) ID*.
- **`TENANT_ID`**: Sao chép giá trị tại dòng *Directory (tenant) ID*.

### Bước 3: Tạo Client Secret
1. Trong menu bên trái, chọn **Certificates & secrets**.
2. Chọn tab **Client secrets** > **New client secret**.
3. Đặt mô tả và thời gian hết hạn, nhấn **Add**.
4. **QUAN TRỌNG:** Sao chép ngay giá trị ở cột **Value** (không phải Secret ID). Đây chính là **`CLIENT_SECRET`**.

### Bước 4: Cấp quyền (API Permissions)
1. Chọn **API permissions** > **Add a permission** > **Microsoft Graph**.
2. Chọn **Application permissions**.
3. Tìm và tích chọn: `Sites.Read.All`, `Files.Read.All` (hoặc `Write` tùy nhu cầu).
4. Nhấn **Add permissions**.
5. Nhấn nút **Grant admin consent for...** để kích hoạt quyền.

### Bước 5: Lấy SharePoint Site ID & Drive ID
Cách dễ nhất là sử dụng [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer).
1. Đăng nhập Graph Explorer bằng tài khoản của bạn.
2. **Lấy `SHAREPOINT_SITE_ID`**:
    - Chạy GET request: `https://graph.microsoft.com/v1.0/sites/root` (hoặc thay `root` bằng `hostname:/sites/ten-site`).
    - Kết quả trả về JSON, tìm trường `id`. Giá trị này là `SHAREPOINT_SITE_ID`.
3. **Lấy `SHAREPOINT_DRIVE_ID`**:
    - Sử dụng ID vừa lấy ở trên, chạy GET request: `https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_SITE_ID}/drives`.
    - Tìm Drive mong muốn (thường là "Documents"), copy giá trị `id` của nó. Đây là `SHAREPOINT_DRIVE_ID`.

### Bước 6: Email người dùng
- **`USER_EMAIL`**: Đơn giản là địa chỉ email Microsoft/Outlook bạn sử dụng để đăng nhập và có quyền truy cập vào SharePoint nói trên.

---

## 2. Cấu hình Google Gemini
**Các biến:** `GEMINI_API_KEY`

1. Truy cập [Google AI Studio](https://aistudio.google.com/).
2. Đăng nhập bằng tài khoản Google.
3. Nhấn vào nút **Get API key** (ở menu bên trái hoặc góc trên).
4. Nhấn **Create API key**.
5. Sao chép chuỗi ký tự vừa tạo. Đây là **`GEMINI_API_KEY`**.

---

## 3. Cấu hình Telegram
**Các biến:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### Bước 1: Tạo Bot và lấy Token
1. Mở Telegram, tìm kiếm user `@BotFather`.
2. Chat lệnh `/newbot`.
3. Đặt tên hiển thị và username cho bot theo hướng dẫn (username phải kết thúc bằng `bot`).
4. BotFather sẽ gửi lại một tin nhắn chứa Access Token. Đây là **`TELEGRAM_BOT_TOKEN`**.

### Bước 2: Lấy Chat ID
1. Tìm username của bot bạn vừa tạo trên Telegram và nhấn **Start** (hoặc gửi một tin nhắn bất kỳ "Hello").
2. Mở trình duyệt web, truy cập đường dẫn sau (thay thế token của bạn vào):
   `https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getUpdates`
3. Tìm trong chuỗi JSON trả về:
   - Tìm đối tượng `chat`.
   - Giá trị `id` bên trong đó chính là **`TELEGRAM_CHAT_ID`**.
   *(Lưu ý: Nếu ID bắt đầu bằng dấu trừ `-`, hãy lấy cả dấu trừ, đó thường là ID của Group chat).*

---

## Cấu trúc file .env mẫu

Tạo file `.env` tại thư mục gốc và điền các giá trị đã lấy:

```env
# Microsoft Azure & SharePoint
TENANT_ID=
CLIENT_ID=
CLIENT_SECRET=
SHAREPOINT_SITE_ID=
SHAREPOINT_DRIVE_ID=
USER_EMAIL=

# Google Gemini
GEMINI_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
