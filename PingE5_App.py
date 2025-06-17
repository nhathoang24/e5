import requests
import os
import json
import time
import random
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup

# === Load biến môi trường ===
current_date = datetime.now().strftime("%d/%m/%Y")
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
user_email = os.getenv("USER_EMAIL")
sharepoint_site_id = os.getenv("SHAREPOINT_SITE_ID")
sharepoint_drive_id = os.getenv("SHAREPOINT_DRIVE_ID")

# === Lấy access token ===
print("🔐 Đang lấy access_token...")
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
    print("❌ Lỗi lấy token:", resp.text)
    exit()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

def safe_get(url, label):
    try:
        res = requests.get(url, headers=headers)
        print(f"{label} → Status:", res.status_code)
        return res
    except Exception as e:
        print(f"{label} → Lỗi:", e)

# === Gửi mail ===
recipients = [
    "phongse@h151147f.onmicrosoft.com", "phongsg@h151147f.onmicrosoft.com",
    "Fongsg@h151147f.onmicrosoft.com", "hd3906420@gmail.com",
]

mail_payload = {
  "message": {
    "subject": f"Thư Khen Thưởng – Ghi Nhận Đóng Góp Xuất Sắc ({current_date})",
    "body": {
      "contentType": "Text",
      "content": (
        f"Ngày {current_date}\n\n"
        "Chào buổi sáng cả nhà,\n\n"
        "Hy vọng mọi người đã có một khởi đầu ngày mới đầy năng lượng và tinh thần tích cực.\n\n"
        "Tôi muốn gửi lời cảm ơn chân thành và lời khen ngợi đặc biệt tới toàn thể đội ngũ vì những nỗ lực bền bỉ và kết quả tuyệt vời trong tháng vừa qua. "
        "Nhờ sự cống hiến không mệt mỏi và tinh thần hợp tác cao, chúng ta đã hoàn thành nhiều mục tiêu quan trọng và vượt qua không ít thử thách.\n\n"
        "Tôi thực sự tự hào khi được đồng hành cùng một tập thể chuyên nghiệp, tài năng và luôn sẵn sàng vượt lên chính mình. "
        "Hãy tiếp tục giữ vững phong độ này để chúng ta cùng nhau chinh phục những đỉnh cao mới trong thời gian tới.\n\n"
        "Chúc mọi người một ngày làm việc hiệu quả, nhiều niềm vui và thật nhiều cảm hứng!\n\n"
        "Trân trọng,"
      )
    },
    "toRecipients": [{"emailAddress": {"address": email}} for email in recipients]
  }
}

print("📬 Gửi mail nội bộ và ngoài hệ thống ...")
res = requests.post(
    f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail",
    headers=headers,
    json=mail_payload
)
print("📤 Trạng thái gửi mail:", res.status_code)

# === Gọi API để giữ các dịch vụ hoạt động ===
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}", "👤 User info")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/drive", "📁 OneDrive")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders", "📨 MailFolders")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/inbox/messages?$top=1", "📥 Inbox latest")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/joinedTeams", "💬 Teams")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/calendars", "📅 Calendar list")

# === Upload ảnh ngẫu nhiên lên SharePoint (trực tiếp, không lưu file) ===
def get_random_anhmoe_url():
    try:
        res = requests.get("https://anh.moe/?random", timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            img_tag = soup.find("img", {"class": "media"})
            if img_tag and img_tag.get("src"):
                return img_tag["src"]
    except Exception as e:
        print("❌ Lỗi lấy ảnh từ anh.moe:", e)
    return None

print("🌐 Đang tải ảnh ngẫu nhiên từ Internet...")
image_url = get_random_anhmoe_url()
if not image_url:
    print("❌ Không lấy được ảnh.")
    exit()

image_data = requests.get(image_url).content
filename = f"random_image_{random.randint(1000, 9999)}.jpg"
folder_path = "teste5"

upload_url = (
    f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
    f"/root:/{folder_path}/{filename}:/content"
)

print("🚀 Upload ảnh trực tiếp lên SharePoint...")
res = requests.put(upload_url, headers=headers, data=BytesIO(image_data))
print(f"📤 Upload lên SharePoint → Status: {res.status_code}")
if res.status_code >= 400:
    print("❌ Lỗi upload:", res.text)
