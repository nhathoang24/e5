import requests
import os
import random
import time
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup

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
    "hd3906420@gmail.com",
]

mail_payload = {
  "message": {
    "subject": f"Thư Cảm Ơn – Ghi Nhận Những Nỗ Lực Nổi Bật ({current_date})",
    "body": {
      "contentType": "Text",
      "content": (
        f"Ngày {current_date}\n\n"
        "Thân gửi toàn thể anh chị em,\n\n"
        "Mong rằng mọi người đã có một buổi sáng đầy hứng khởi và năng lượng.\n\n"
        "Nhân dịp tổng kết hoạt động gần đây, tôi muốn gửi lời cảm ơn sâu sắc đến cả đội vì những đóng góp xuất sắc và tinh thần làm việc không ngừng nghỉ trong suốt thời gian qua. "
        "Chính nhờ sự đồng lòng, nhiệt huyết và trách nhiệm cao mà chúng ta đã đạt được nhiều cột mốc đáng tự hào.\n\n"
        "Tôi đánh giá rất cao tinh thần đồng đội và khả năng thích ứng linh hoạt của mỗi cá nhân trong tập thể. "
        "Sự đoàn kết và quyết tâm ấy chính là nền tảng vững chắc giúp chúng ta vững bước chinh phục những mục tiêu mới.\n\n"
        "Chúc cả nhà một ngày mới làm việc đầy hiệu quả, hứng khởi và ngập tràn năng lượng tích cực.\n\n"
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

# === Hàm lấy URL ảnh ngẫu nhiên ===
def get_random_anhmoe_url():
    try:
        res = requests.get("https://anh.moe/?random", timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            img_tag = soup.find("img", {"class": "media"})
            if img_tag and img_tag.get("src"):
                return img_tag["src"]
    except Exception as e:
        log(f"❌ Lỗi lấy ảnh từ anh.moe: {e}")
    return None

# === Upload ảnh ===
log("🌐 Đang tải ảnh ngẫu nhiên từ Internet...")
image_url = get_random_anhmoe_url()
if not image_url:
    log("❌ Không lấy được ảnh.")
    log(image_url)
    
else:
    log(f"🔗 URL ảnh: {image_url}")
    image_response = requests.get(image_url)
    log(f"📥 Tải ảnh → Status: {image_response.status_code}, Size: {len(image_response.content)} bytes")

    if image_response.status_code == 200:
        image_data = image_response.content
        filename = f"random_image_{random.randint(1000, 9999)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        upload_url = (
            f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
            f"/root:/{filename}:/content"
        )

        upload_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/jpeg"
        }

        log(f"🚀 Upload ảnh lên SharePoint: {filename}")
        res = requests.put(upload_url, headers=upload_headers, data=image_data)
        log(f"📤 Upload → Status: {res.status_code}")

        if res.status_code in [200, 201]:
            response_data = res.json()
            file_url = response_data.get("webUrl", "N/A")
        else:
            log(f"❌ *Upload ảnh lỗi!*\nStatus: `{res.status_code}`\n{res.text}")
    else:
        log("❌ Không thể tải ảnh từ URL")

# === Hoàn tất ===
log("✅ Hoàn thành ping E5!")

# === Gửi toàn bộ log về Telegram ===
log_text = "\n".join(log_messages)
max_length = 4000  # Telegram giới hạn 4096 ký tự
for i in range(0, len(log_text), max_length):
    chunk = log_text[i:i + max_length]
    res = requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
        data={"chat_id": os.getenv('TELEGRAM_CHAT_ID'), "text": chunk}
    )
    log(f"📨 Gửi Telegram → {res.status_code}")
    time.sleep(2)  # tránh spam
