# Hướng dẫn lấy thông tin cấu hình SharePoint

Tài liệu này hướng dẫn cách lấy các giá trị cần thiết để cấu hình Microsoft Azure & SharePoint.

## Các biến cần lấy
`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `SHAREPOINT_SITE_ID`, `SHAREPOINT_DRIVE_ID`

## Bước 1: Lấy Tenant ID
1. Truy cập [Azure Portal](https://portal.azure.com/).
2. Tại trang chủ, tìm mục **Manage Microsoft Entra ID** và chọn **View**.
3. Tại trang **Overview**, bạn sẽ thấy **`TENANT_ID`** (Tenant ID) - sao chép giá trị này.

## Bước 2: Tạo App Registration
1. Ở menu bên trái, chọn **App registrations**.
2. Chọn **New registration**.
    - Đặt tên (Name): Ví dụ `MySharePointApp`.
    - Supported account types: Chọn *Accounts in this organizational directory only*.
    - Nhấn **Register**.

## Bước 3: Lấy Client ID
Sau khi tạo xong, tại trang **Overview** của App, bạn sẽ thấy:
- **`CLIENT_ID`**: Sao chép giá trị tại dòng *Application (client) ID*.

## Bước 4: Tạo Client Secret
1. Trong menu bên trái, chọn **Certificates & secrets**.
2. Chọn tab **Client secrets** > **New client secret**.
3. Đặt mô tả và thời gian hết hạn, nhấn **Add**.
4. **QUAN TRỌNG:** Sao chép ngay giá trị ở cột **Value** (không phải Secret ID). Đây chính là **`CLIENT_SECRET`**.

## Bước 5: Cấp quyền (API Permissions)
1. Chọn **API permissions** > **Add a permission** > **Microsoft Graph**.
2. Chọn **Application permissions**.
3. Tìm và tích chọn: `Sites.Read.All`, `Files.Read.All` (hoặc `Write` tùy nhu cầu).
4. Nhấn **Add permissions**.
5. Nhấn nút **Grant admin consent for...** để kích hoạt quyền.

## Bước 6: Lấy SharePoint Site ID & Drive ID

### Cách 1: Sử dụng Microsoft Graph Explorer
Sử dụng [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer).

1. Đăng nhập Graph Explorer bằng tài khoản của bạn.

2. **Lấy `SHAREPOINT_SITE_ID`**:
    - Chạy GET request: `https://graph.microsoft.com/v1.0/sites/root` (hoặc thay `root` bằng `hostname:/sites/ten-site`).
    - Kết quả trả về JSON, tìm trường `id`. Giá trị này là `SHAREPOINT_SITE_ID`.

3. **Lấy `SHAREPOINT_DRIVE_ID`**:
    - Sử dụng ID vừa lấy ở trên, chạy GET request: `https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_SITE_ID}/drives`.
    - Tìm Drive mong muốn (thường là "Documents"), copy giá trị `id` của nó. Đây là `SHAREPOINT_DRIVE_ID`.

### Cách 2: Sử dụng script Python
1. Tải file `filesharepoint.py` về.
2. Tạo file `.env` cùng thư mục với `filesharepoint.py`.
3. Điền các giá trị đã lấy ở các bước trên vào file `.env`:
```env
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USER_EMAIL=email@ema.onmicrosoft.com
```
4. Chạy script:
```bash
python filesharepoint.py
```
5. Script sẽ tự động lấy và hiển thị `SHAREPOINT_SITE_ID` và `SHAREPOINT_DRIVE_ID`.
