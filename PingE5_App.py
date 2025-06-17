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

# === Kiểm tra thông tin SharePoint trước khi upload ===
print("🔍 Kiểm tra thông tin SharePoint...")
site_info = safe_get(f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}", "📊 Site info")
if site_info and site_info.status_code == 200:
    site_data = site_info.json()
    print(f"✅ Site name: {site_data.get('displayName', 'N/A')}")
    print(f"✅ Site URL: {site_data.get('webUrl', 'N/A')}")

drive_info = safe_get(f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}", "📁 Drive info")
if drive_info and drive_info.status_code == 200:
    drive_data = drive_info.json()
    print(f"✅ Drive name: {drive_data.get('name', 'N/A')}")
    print(f"✅ Drive type: {drive_data.get('driveType', 'N/A')}")

# === Kiểm tra thư mục đích ===
folder_path = "teste5"
print(f"📂 Kiểm tra thư mục: {folder_path}")
folder_check = safe_get(
    f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}/root:/{folder_path}", 
    "📂 Folder check"
)

if folder_check and folder_check.status_code == 404:
    print(f"📁 Thư mục {folder_path} không tồn tại, đang tạo...")
    create_folder_payload = {
        "name": folder_path,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    }
    create_folder_res = requests.post(
        f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}/root/children",
        headers=headers,
        json=create_folder_payload
    )
    print(f"📁 Tạo thư mục → Status: {create_folder_res.status_code}")
    if create_folder_res.status_code != 201:
        print("❌ Lỗi tạo thư mục:", create_folder_res.text)

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

# === Upload ảnh ngẫu nhiên lên SharePoint với debug chi tiết ===
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

print(f"🔗 URL ảnh: {image_url}")
image_response = requests.get(image_url)
print(f"📥 Tải ảnh → Status: {image_response.status_code}, Size: {len(image_response.content)} bytes")

if image_response.status_code != 200:
    print("❌ Không thể tải ảnh từ URL")
    exit()

image_data = image_response.content
filename = f"random_image_{random.randint(1000, 9999)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

# === Upload với headers chính xác ===
upload_url = (
    f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
    f"/root:/{folder_path}/{filename}:/content"
)

# Sử dụng headers riêng cho upload (không có Content-Type: application/json)
upload_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "image/jpeg"
}

print(f"🚀 Upload ảnh lên SharePoint: {filename}")
print(f"📍 Upload URL: {upload_url}")
res = requests.put(upload_url, headers=upload_headers, data=image_data)
print(f"📤 Upload → Status: {res.status_code}")

if res.status_code in [200, 201]:
    response_data = res.json()
    print("✅ Upload thành công!")
    print(f"📁 File ID: {response_data.get('id', 'N/A')}")
    print(f"📁 File name: {response_data.get('name', 'N/A')}")
    print(f"📁 Web URL: {response_data.get('webUrl', 'N/A')}")
    
    # Kiểm tra file đã được upload
    time.sleep(2)  # Chờ 2 giây
    check_file = safe_get(
        f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}/root:/{folder_path}/{filename}",
        "🔍 Verify upload"
    )
    if check_file and check_file.status_code == 200:
        print("✅ Xác nhận: File đã tồn tại trên SharePoint")
    else:
        print("⚠️ Cảnh báo: Không thể xác nhận file trên SharePoint")
else:
    print("❌ Lỗi upload:", res.text)
    
    # Thử upload với tên file đơn giản hơn
    simple_filename = f"test_{random.randint(100, 999)}.jpg"
    simple_upload_url = (
        f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
        f"/root:/{folder_path}/{simple_filename}:/content"
    )
    print(f"🔄 Thử lại với tên file đơn giản: {simple_filename}")
    retry_res = requests.put(simple_upload_url, headers=upload_headers, data=image_data)
    print(f"🔄 Retry → Status: {retry_res.status_code}")
    if retry_res.status_code in [200, 201]:
        print("✅ Upload thành công với tên file đơn giản!")
        retry_data = retry_res.json()
        print(f"📁 Web URL: {retry_data.get('webUrl', 'N/A')}")
    else:
        print("❌ Vẫn lỗi:", retry_res.text)
