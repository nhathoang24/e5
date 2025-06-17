import requests
import os
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import subprocess

current_date = datetime.now().strftime("%d/%m/%Y")
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
user_email = os.getenv("USER_EMAIL")

# Step 1 - Get token
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
scopes = ["https://graph.microsoft.com/.default"]
data = {
    "client_id": client_id,
    "scope": " ".join(scopes),
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}
print("🔐 Đang lấy access_token...")
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

# Step 2 - Gửi mail tới nhiều người
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

# Step 3 - Ping Graph API nhiều dịch vụ
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}", "👤 User info")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/drive", "📁 OneDrive")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders", "📨 MailFolders")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/inbox/messages?$top=1", "📥 Inbox latest")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/joinedTeams", "💬 Teams")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/calendars", "📅 Calendar list")

# Step 4 - Xoá nội dung thư mục OneDrive và tạo file giả trực tiếp trên cloud
print("🧹 Xoá toàn bộ nội dung trong thư mục teste5 (giữ nguyên thư mục)...")
os.system("rclone delete onde:teste5")

print("📄 Tạo ngẫu nhiên 3-4 file giả trực tiếp trên OneDrive...")
for i in range(random.randint(3, 4)):
    filename = f"note_{random.randint(1000, 9999)}.txt"
    content = f"Đây là file giả số {i+1} để giữ OneDrive hoạt động."
    upload_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/root:/teste5/{filename}:/content"
    res = requests.put(upload_url, headers=headers, data=content.encode("utf-8"))
    print(f"📎 Upload {filename} → Status:", res.status_code)

print("🧹 Xoá toàn bộ nội dung trong thư mục teste5 (giữ nguyên thư mục)...")
subprocess.run(["rclone", "delete", "onde:teste5"], check=True)

print("🖼️ Upload ảnh từ local thư mục images lên teste5...")
subprocess.run(["rclone", "copy", "images", "onde:teste5", "--transfers=4", "--checkers=8", "--fast-list", "--ignore-times"], check=True)