import os
import requests
from flask import Flask, redirect, request
import random
import string
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
redirect_uri = "http://localhost:8000/callback"

authorize_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

scopes = [
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Files.ReadWrite",
    "https://graph.microsoft.com/Calendars.ReadWrite",
    "https://graph.microsoft.com/Group.Read.All",
    "https://graph.microsoft.com/ChannelMessage.Send",
    "https://graph.microsoft.com/Team.ReadBasic.All",
    "https://graph.microsoft.com/Channel.ReadBasic.All"
]

@app.route("/")
def home():
    return redirect(
        f"{authorize_url}?client_id={client_id}&response_type=code"
        f"&redirect_uri={redirect_uri}&response_mode=query&scope={' '.join(scopes)}"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_data = {
        "client_id": client_id,
        "scope": " ".join(scopes),
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "client_secret": client_secret
    }
    token_res = requests.post(token_url, data=token_data)
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    print("🔑 access_token:", access_token)

    if not access_token:
        return "❌ Không lấy được access_token: " + token_res.text

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 🧹 Xoá file trong thư mục teste5 nếu có
    print("🧹 Dọn dẹp thư mục teste5...")
    delete_url = "https://graph.microsoft.com/v1.0/me/drive/root:/teste5"
    delete_list = requests.get(delete_url, headers=headers).json()
    if "value" in delete_list:
        for item in delete_list["value"]:
            item_id = item["id"]
            requests.delete(f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}", headers=headers)

    # 📧 Gửi mail
    recipients = [
        "phongse@h151147f.onmicrosoft.com", "phongsg@h151147f.onmicrosoft.com",
        "Fongsg@h151147f.onmicrosoft.com", "hd3906420@gmail.com",
    ]
    mail_payload = {
        "message": {
            "subject": "Mail khen thưởng nội bộ và ngoài hệ thống",
            "body": {
                "contentType": "Text",
                "content": "Ping mail nội bộ giữ tài khoản sống"
            },
            "toRecipients": [{"emailAddress": {"address": email}} for email in recipients]
        }
    }
    mail_resp = requests.post("https://graph.microsoft.com/v1.0/me/sendMail", headers=headers, json=mail_payload)

    # 📁 Upload file giữ acc
    file_resp = requests.put(
        "https://graph.microsoft.com/v1.0/me/drive/root:/teste5/PingAlive.txt:/content",
        headers=headers,
        data="File giữ OneDrive sống".encode("utf-8")
    )

    # 📄 Tạo file giả
    print("📄 Đang tạo file giả...")
    for _ in range(random.randint(5, 10)):
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ".txt"
        content = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=random.randint(100, 200)))
        res = requests.put(
            f"https://graph.microsoft.com/v1.0/me/drive/root:/teste5/{name}:/content",
            headers=headers,
            data=content.encode("utf-8")
        )

    # 🖼️ Upload ảnh local
    uploads = []
    if os.path.exists("images"):
        for filename in os.listdir("images"):
            path = os.path.join("images", filename)
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    content = f.read()
                upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/teste5/{filename}:/content"
                res = requests.put(upload_url, headers=headers, data=content)
                uploads.append((filename, res.status_code))

    # 📅 Tạo calendar event
    calendar_payload = {
        "subject": "Ping Calendar",
        "start": {"dateTime": "2025-06-01T08:00:00", "timeZone": "UTC"},
        "end": {"dateTime": "2025-06-01T09:00:00", "timeZone": "UTC"}
    }
    calendar_resp = requests.post("https://graph.microsoft.com/v1.0/me/events", headers=headers, json=calendar_payload)

    # 📢 Gửi bài Teams (tự động lấy team_id và channel_id)
    teams_status = "ok"
    try:
        teams_data = requests.get("https://graph.microsoft.com/v1.0/me/joinedTeams", headers=headers).json()
        if "value" in teams_data and len(teams_data["value"]) > 0:
            team_id = teams_data["value"][0]["id"]
            print("team id: ", team_id)
            channels_data = requests.get(f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels", headers=headers).json()
            general_channel = next((ch for ch in channels_data["value"] if ch["displayName"].lower() == "general"), None)
            if general_channel:
                channel_id = general_channel["id"]
                print("channel_id: ", channel_id)
                msg_payload = {
                    "body": {
                        "content": "Ping bài đăng xác thực tài khoản trong Microsoft Teams"
                    }
                }
                teams_url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
                teams_res = requests.post(teams_url, headers=headers, json=msg_payload)
                teams_status = f"{teams_res.status_code} - Đã gửi vào kênh General"
            else:
                teams_status = "⚠️ Không tìm thấy kênh General"
    except Exception as e:
        teams_status = f"❌ Lỗi gửi bài Teams: {e}"

    uploads_str = "<br>".join([f"{f}: {s}" for f, s in uploads]) if uploads else "❌ Không có ảnh"

    return f"""
    ✅ Token OK<br>
    📧 Mail gửi: {mail_resp.status_code}<br>
    📁 PingAlive.txt: {file_resp.status_code}<br>
    📄 File giả tạo ngẫu nhiên: OK<br>
    🖼️ Ảnh upload: {uploads_str}<br>
    📅 Lịch: {calendar_resp.status_code}<br>
    📢 Bài đăng Teams: {teams_status}<br>
    🔑 Token đã in ra terminal để dùng Postman
    """

if __name__ == "__main__":
    print("⚡ Mở trình duyệt login tài khoản Microsoft 365...")
    app.run(host="0.0.0.0", port=8000)
