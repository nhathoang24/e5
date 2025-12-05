import requests
import os
import random
import time
from dotenv import load_dotenv
from datetime import datetime
# Đã bỏ import BeautifulSoup vì không cần dùng nữa

# === Khởi tạo log lưu trữ ===
log_messages = []

def log(*args):
    msg = " ".join(str(arg) for arg in args)
    print(msg)
    log_messages.append(msg)

# === Hàm gửi Telegram ===
def send_telegram_message(msg):
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not telegram_token or not telegram_chat_id:
        log("⚠️ Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, data=data)
        log(f"📨 Gửi Telegram → {res.status_code}")
    except Exception as e:
        log(f"❌ Gửi Telegram lỗi: {e}")

# === Load biến môi trường ===
load_dotenv()
current_date = datetime.now().strftime("%d/%m/%Y")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
user_email = os.getenv("USER_EMAIL")
sharepoint_site_id = os.getenv("SHAREPOINT_SITE_ID")
sharepoint_drive_id = os.getenv("SHAREPOINT_DRIVE_ID")

# === Lấy access token ===
log("🔐 Đang lấy access_token...")
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
scopes = ["https://graph.microsoft.com/.default"]
data = {
    "client_id": client_id,
    "scope": " ".join(scopes),
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}
resp = requests.post(token_url, data=data)
token = resp.json().get("access_token")
if not token:
    send_telegram_message("❌ *Lỗi lấy Access Token!*")
    log(f"❌ Lỗi lấy token: {resp.text}")
    exit()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# === Hàm GET an toàn ===
def safe_get(url, label):
    try:
        res = requests.get(url, headers=headers)
        log(f"{label} → Status:", res.status_code)
        return res
    except Exception as e:
        log(f"{label} → Lỗi:", e)

# === Kiểm tra thông tin SharePoint ===
log("🔍 Kiểm tra thông tin SharePoint...")
site_info = safe_get(f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}", "📊 Site info")
drive_info = safe_get(f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}", "📁 Drive info")

# === Gửi mail ===
recipients = [
    "phongse@h151147f.onmicrosoft.com",
    "phongsg@h151147f.onmicrosoft.com",
    "Fongsg@h151147f.onmicrosoft.com",
]

mail_payload = {
  "message": {
    "subject": f"Thư Cảm Ơn – Ghi Nhận Những Nỗ Lực Nổi Bật ({current_date})",
    "body": {
      "contentType": "Text",
      "content": (
        f"Ngày {current_date}\n\n"
        "Thân gửi toàn thể anh chị em,\n\n"
        "Hệ thống E5 Developer Checkpoint.\n"
        "Tiến trình tự động duy trì hoạt động.\n\n"
        "Trân trọng,"
      )
    },
    "toRecipients": [{"emailAddress": {"address": email}} for email in recipients]
  }
}

log("📬 Gửi mail nội bộ và ngoài hệ thống ...")
res = requests.post(
    f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail",
    headers=headers,
    json=mail_payload
)

# === Ping các API Microsoft để duy trì kết nối ===
log("🔄 Ping các dịch vụ Microsoft Graph...")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}", "👤 User info")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/drive", "📁 OneDrive")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders", "📨 MailFolders")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/inbox/messages?$top=1", "📥 Inbox latest")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/joinedTeams", "💬 Teams")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/calendars", "📅 Calendar list")

# === TẠO VÀ UPLOAD FILE NGẪU NHIÊN (MỚI) ===
log("📝 Đang tạo file text ngẫu nhiên...")

# 1. Tạo nội dung file
random_id = random.randint(100000, 999999)
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
file_content = f"Auto-generated file for E5 Keep Active.\nTime: {timestamp}\nRandom ID: {random_id}"

# 2. Tạo tên file
filename = f"auto_ping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# 3. Chuẩn bị upload
upload_url = (
    f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
    f"/root:/{filename}:/content"
)

upload_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "text/plain"  # Đổi content-type thành text/plain
}

log(f"🚀 Upload file text lên SharePoint: {filename}")

# 4. Thực hiện upload
try:
    # encode('utf-8') để chuyển string thành bytes trước khi gửi
    res = requests.put(upload_url, headers=upload_headers, data=file_content.encode('utf-8'))
    log(f"📤 Upload → Status: {res.status_code}")

    if res.status_code in [200, 201]:
        response_data = res.json()
        file_url = response_data.get("webUrl", "N/A")
        log(f"✅ Upload thành công! URL: {file_url}")
    else:
        log(f"❌ *Upload lỗi!*\nStatus: `{res.status_code}`\n{res.text}")
except Exception as e:
    log(f"❌ Lỗi ngoại lệ khi upload: {e}")

# === Hoàn tất ===
log("✅ Hoàn thành ping E5!")

# === Gửi toàn bộ log về Telegram ===
log_text = "\n".join(log_messages)
max_length = 4000  # Telegram giới hạn 4096 ký tự
for i in range(0, len(log_text), max_length):
    chunk = log_text[i:i + max_length]
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
            data={"chat_id": os.getenv('TELEGRAM_CHAT_ID'), "text": chunk}
        )
    except Exception as e:
        print(f"Lỗi gửi log Telegram: {e}")
    time.sleep(2)  # tránh spam
