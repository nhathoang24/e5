# Hướng dẫn lấy thông tin cấu hình (Environment Variables)

Tài liệu này hướng dẫn chi tiết cách lấy các giá trị cấu hình cho file `.env`.

## 1. Cấu hình Microsoft Azure & SharePoint
**Các biến cần lấy:** `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `SHAREPOINT_SITE_ID`, `SHAREPOINT_DRIVE_ID`, `USER_EMAIL`

### Bước 1: Lấy Tenant ID và Tạo App
1. Truy cập [Azure Portal](https://portal.azure.com/).
2. Trên thanh tìm kiếm hoặc trang chủ, chọn **Microsoft Entra ID** (trước đây là Azure Active Directory).
3. Tại trang **Overview** (Tổng quan) của Microsoft Entra ID:
    - Tìm dòng **Tenant ID** (hoặc *Directory ID*) ở phần thông tin cơ bản.
    - Sao chép giá trị này -> Đây là **`TENANT_ID`**.
4. Nhìn sang menu bên tay trái, tìm và chọn mục **App registrations** (nằm trong nhóm *Manage*).
5. Chọn **New registration**:
    - **Name**: Đặt tên cho ứng dụng (Ví dụ: `SharePointBot`).
    - **Supported account types**: Chọn *Accounts in this organizational directory only* (Single tenant).
    - Nhấn **Register**.

### Bước 2: Lấy Client ID
Sau khi tạo xong App, bạn sẽ được chuyển đến trang **Overview** của App đó:
- Tìm dòng **Application (client) ID**.
- Sao chép giá trị này -> Đây là **`CLIENT_ID`**.

### Bước 3: Tạo Client Secret
1. Trong menu bên trái của App vừa tạo, chọn **Certificates & secrets**.
2. Chọn tab **Client secrets** -> bấm **New client secret**.
3. Nhập mô tả (Description) và chọn thời gian hết hạn (Expires). Nhấn **Add**.
4. **QUAN TRỌNG:** Sao chép ngay giá trị tại cột **Value** (Không phải *Secret ID*).
    - Giá trị này là **`CLIENT_SECRET`**.
    - *Lưu ý: Nếu bạn tải lại trang, giá trị này sẽ bị ẩn đi.*

### Bước 4: Cấp quyền (API Permissions)
1. Chọn menu **API permissions** -> **Add a permission** -> **Microsoft Graph**.
2. Chọn **Application permissions**.
3. Tìm và tích chọn các quyền sau:
    - `Sites.Read.All` (hoặc `Sites.ReadWrite.All`)
    - `Files.Read.All` (hoặc `Files.ReadWrite.All`)
4. Nhấn **Add permissions**.
5. Nhấn nút **Grant admin consent for [Tên tổ chức]** để kích hoạt quyền (nút này thường có dấu tích xanh).

### Bước 5: Lấy SharePoint Site ID & Drive ID
Sử dụng công cụ [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) để lấy ID chính xác:
1. Đăng nhập Graph Explorer bằng tài khoản Microsoft của bạn.
2. **Lấy `SHAREPOINT_SITE_ID`**:
    - Chạy lệnh GET: `https://graph.microsoft.com/v1.0/sites/root` (nếu dùng site chính) hoặc `https://graph.microsoft.com/v1.0/sites/hostname:/sites/ten-site`.
    - Trong kết quả trả về, copy giá trị của trường `id`.
3. **Lấy `SHAREPOINT_DRIVE_ID`**:
    - Chạy lệnh GET: `https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_SITE_ID_VỪA_LẤY}/drives`.
    - Tìm Drive bạn muốn (thường tên là "Documents"), copy giá trị `id` của nó.

### Bước 6: Email người dùng
- **`USER_EMAIL`**: Điền email Microsoft 365 mà bạn dùng để quản lý hoặc truy cập dữ liệu SharePoint này.

---

## 2. Cấu hình Google Gemini
**Biến cần lấy:** `GEMINI_API_KEY`

1. Truy cập [Google AI Studio](https://aistudio.google.com/).
2. Đăng nhập tài khoản Google.
3. Chọn **Get API key** -> **Create API key**.
4. Sao chép chuỗi ký tự vừa tạo -> Đây là **`GEMINI_API_KEY`**.

---

## 3. Cấu hình Telegram
**Biến cần lấy:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### Bước 1: Lấy Token
1. Chat với `@BotFather` trên Telegram.
2. Gửi lệnh `/newbot` và làm theo hướng dẫn đặt tên.
3. BotFather sẽ gửi Token truy cập -> Đây là **`TELEGRAM_BOT_TOKEN`**.

### Bước 2: Lấy Chat ID
1. Chat với con bot bạn vừa tạo (gửi "Hello").
2. Truy cập trình duyệt: `https://api.telegram.org/bot<TOKEN_CỦA_BẠN>/getUpdates`
3. Tìm trong đoạn JSON kết quả: `"chat": { "id": 123456789, ... }`.
4. Số `123456789` là **`TELEGRAM_CHAT_ID`**. (Nếu là Group chat, ID sẽ có dấu âm `-`).

---

## Mẫu file .env

```env
# Microsoft Azure (Entra ID) & SharePoint
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
