# Hướng dẫn cấu hình hệ thống & Lấy Environment Variables

Tài liệu này hướng dẫn chi tiết cách lấy các giá trị cấu hình cho file `.env`.

---

## 1. Cấu hình Microsoft Azure & SharePoint (Quan trọng)

Để bot có thể truy cập SharePoint, bạn cần đăng ký ứng dụng trên Azure và cấp quyền.

### Bước 1: Lấy Tenant ID và Đăng ký App
1. Truy cập [Azure Portal](https://portal.azure.com/).
2. Tìm và chọn **Microsoft Entra ID** (tên cũ là Azure Active Directory).
3. Tại trang **Overview**, sao chép **Tenant ID**.
   -> Điền vào `.env`: `TENANT_ID`
4. Ở menu trái, chọn **App registrations** -> **New registration**.
   - **Name**: `SharePointBot` (hoặc tên tùy ý).
   - **Supported account types**: *Accounts in this organizational directory only*.
   - Nhấn **Register**.

### Bước 2: Lấy Client ID
Tại trang **Overview** của App vừa tạo, sao chép **Application (client) ID**.
-> Điền vào `.env`: `CLIENT_ID`

### Bước 3: Tạo Client Secret
1. Vào menu **Certificates & secrets** -> **Client secrets** -> **New client secret**.
2. Đặt tên và hạn sử dụng -> **Add**.
3. **QUAN TRỌNG:** Sao chép ngay giá trị ở cột **Value** (Không phải Secret ID).
   -> Điền vào `.env`: `CLIENT_SECRET`

### Bước 4: Cấp quyền (API Permissions)
1. Vào menu **API permissions** -> **Add a permission** -> **Microsoft Graph**.
2. Chọn **Application permissions**.
3. Tìm và tích chọn:
   - `Sites.Read.All` (hoặc `Sites.ReadWrite.All`)
   - `Files.Read.All` (hoặc `Files.ReadWrite.All`)
4. Nhấn **Add permissions**.
5. Nhấn nút **Grant admin consent for...** (dấu tích xanh) để hiệu lực hóa quyền.

### Bước 5: Điền thông tin sơ bộ vào .env
Trước khi lấy Site ID và Drive ID, bạn cần điền 4 thông số đã lấy ở trên và email của bạn vào file `.env`:
```env
TENANT_ID=xxxx-xxxx-xxxx
CLIENT_ID=xxxx-xxxx-xxxx
CLIENT_SECRET=xxxx-xxxx-xxxx
USER_EMAIL=email_cua_ban@domain.com
