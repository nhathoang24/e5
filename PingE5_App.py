import requests
import os
import random
import time
import sys
from datetime import datetime

# === Optional: Load .env khi chạy local ===
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Bỏ qua trên GitHub Actions

# === Khởi tạo log lưu trữ ===
log_messages = []

# === Hệ thống theo dõi lỗi ===
action_results = []  # Danh sách (tên hành động, thành công/thất bại, mô tả)

def log(*args):
    msg = " ".join(str(arg) for arg in args)
    print(msg)
    log_messages.append(msg)

def record_action(action_name, success, detail=""):
    """Ghi nhận kết quả của một hành động."""
    icon = "✅" if success else "❌"
    action_results.append((icon, action_name, detail))

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
        res = requests.post(url, data=data, timeout=100)
        log(f"📨 Gửi Telegram → {res.status_code}")
    except Exception as e:
        log(f"❌ Gửi Telegram lỗi: {e}")

# === Validate environment variables ===
log("🔍 Kiểm tra biến môi trường...")
REQUIRED_VARS = [
    "CLIENT_ID", "CLIENT_SECRET", "TENANT_ID", 
    "USER_EMAIL", "SHAREPOINT_SITE_ID", "SHAREPOINT_DRIVE_ID"
]

missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    error_msg = f"❌ Thiếu biến môi trường: {', '.join(missing_vars)}"
    log(error_msg)
    send_telegram_message(f"*GitHub Actions Error*\n{error_msg}")
    
    with open("error.txt", "w") as f:
        f.write(f"Missing environment variables:\n{', '.join(missing_vars)}")
    
    sys.exit(1)

# === Load biến môi trường ===
current_date = datetime.now().strftime("%d/%m/%Y")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
user_email = os.getenv("USER_EMAIL")
sharepoint_site_id = os.getenv("SHAREPOINT_SITE_ID")
sharepoint_drive_id = os.getenv("SHAREPOINT_DRIVE_ID")
groq_api_key = os.getenv("GROQ_API_KEY")

# === Lấy access token Microsoft ===
log("🔐 Đang lấy access_token Microsoft...")
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
scopes = ["https://graph.microsoft.com/.default"]
data = {
    "client_id": client_id,
    "scope": " ".join(scopes),
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}

try:
    resp = requests.post(token_url, data=data, timeout=100)
    resp.raise_for_status()
    token = resp.json().get("access_token")
    
    if not token:
        raise ValueError("No access_token in response")
    
    log("✅ Access token lấy thành công")
    record_action("Lấy Access Token Microsoft", True)
    
except Exception as e:
    error_msg = f"❌ Lỗi lấy token: {e}"
    log(error_msg)
    record_action("Lấy Access Token Microsoft", False, str(e))
    send_telegram_message(f"*Authentication Failed*\n`{error_msg}`")
    
    with open("error.txt", "w") as f:
        f.write(f"Authentication Error:\n{str(e)}\n{resp.text if 'resp' in locals() else ''}")
    
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# === Hàm GET an toàn ===
def safe_get(url, label, timeout=100):
    try:
        res = requests.get(url, headers=headers, timeout=timeout)
        res.raise_for_status()
        log(f"✅ {label} → Status: {res.status_code}")
        record_action(label, True)
        return res
    except Exception as e:
        log(f"❌ {label} → Lỗi: {e}")
        record_action(label, False, str(e))
        return None

# === Hàm lấy nội dung từ Groq API ===
def get_groq_content():
    if not groq_api_key:
        log("⚠️ Không tìm thấy GROQ_API_KEY. Sử dụng nội dung mặc định.")
        record_action("Gọi Groq API", False, "Thiếu GROQ_API_KEY")
        return None

    log("🤖 Đang nhờ Groq viết nội dung...")
    url = "https://api.groq.com/openai/v1/responses"

    # Meta-prompt: để Groq tự chọn chủ đề mỗi lần chạy
    run_time = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    selected_prompt = (
        f"Bây giờ là {run_time}. Hãy tự nghĩ ra một chủ đề ngẫu nhiên, độc đáo về công nghệ, lập trình, "
        "khoa học máy tính hoặc kỹ thuật số (không được lặp lại các chủ đề quá phổ biến), "
        "rồi viết một đoạn văn ngắn 50–80 từ bằng tiếng Việt về chủ đề đó. "
        "Chỉ đưa ra nội dung văn xuôi, không giải thích hay đặt tiêu đề."
    )

    payload = {
        "model": "openai/gpt-oss-120b",
        "input": selected_prompt
    }

    req_headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=req_headers, timeout=100)
        if response.status_code == 200:
            result = response.json()
            # Groq Responses API: output[0].content[0].text
            text_content = result["output"][0]["content"][0]["text"]
            log("✅ Groq đã trả về nội dung.")
            record_action("Gọi Groq API", True)
            return text_content
        else:
            log(f"❌ Lỗi Groq API: {response.status_code} — {response.text}")
            record_action("Gọi Groq API", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log(f"❌ Lỗi khi gọi Groq: {e}")
        record_action("Gọi Groq API", False, str(e))
        return None

# === Kiểm tra thông tin SharePoint ===
log("🔍 Kiểm tra thông tin SharePoint...")
safe_get(f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}", "📊 Site info")
safe_get(f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}", "📁 Drive info")

# === Email recipients (HARDCODED) ===
recipients = [
    "phongse@h151147f.onmicrosoft.com",
    "phongsg@h151147f.onmicrosoft.com",
    "Fongsg@h151147f.onmicrosoft.com",
    "hd3906427@gmail.com",
]

# === Gửi mail ===
mail_payload = {
  "message": {
    "subject": f"E5 Developer Activity Report ({current_date})",
    "body": {
      "contentType": "Text",
      "content": (
        f"Ngày {current_date}\n\n"
        "Hệ thống E5 Developer Checkpoint.\n"
        "Tiến trình tự động duy trì hoạt động.\n"
        "API Graph: OK\n"
        "SharePoint: OK\n\n"
        "Trân trọng,"
      )
    },
    "toRecipients": [{"emailAddress": {"address": email}} for email in recipients]
  }
}

log("📬 Gửi mail kích hoạt activity...")
try:
    res = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail",
        headers=headers,
        json=mail_payload,
        timeout=100
    )
    res.raise_for_status()
    log(f"✅ Email sent → Status: {res.status_code}")
    record_action("Gửi Email Activity", True)
except Exception as e:
    log(f"❌ Gửi mail lỗi: {e}")
    record_action("Gửi Email Activity", False, str(e))

# === Ping các API Microsoft ===
log("🔄 Ping các dịch vụ Microsoft Graph...")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}", "👤 User info")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/drive", "📁 OneDrive")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders", "📨 MailFolders")
safe_get(f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/inbox/messages?$top=1", "📥 Inbox latest")

def cleanup_old_files(keep_count=5):
    log("🧹 Đang kiểm tra và dọn dẹp file cũ...")
    try:
        # 1. Lấy danh sách file trong thư mục gốc của Drive
        list_url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}/root/children"
        res = requests.get(list_url, headers=headers, timeout=100)
        res.raise_for_status()
        
        items = res.json().get('value', [])
        
        # 2. Lọc ra các file do bot tạo (có tiền tố groq_log_)
        log_files = [f for f in items if f.get('name', '').startswith('groq_log_')]
        
        # 3. Sắp xếp theo thời gian tạo (Mới nhất đứng đầu)
        log_files.sort(key=lambda x: x['createdDateTime'], reverse=True)
        
        # 4. Kiểm tra số lượng
        if len(log_files) > keep_count:
            files_to_delete = log_files[keep_count:]
            log(f"⚠️ Tìm thấy {len(log_files)} file log. Sẽ xóa {len(files_to_delete)} file cũ...")
            
            for file in files_to_delete:
                file_id = file['id']
                file_name = file['name']
                delete_url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}/items/{file_id}"
                
                try:
                    del_res = requests.delete(delete_url, headers=headers, timeout=60)
                    if del_res.status_code == 204:
                        log(f"🗑️ Đã xóa: {file_name}")
                        record_action(f"Xóa file cũ: {file_name}", True)
                    else:
                        log(f"❌ Xóa thất bại {file_name}: {del_res.status_code}")
                        record_action(f"Xóa file cũ: {file_name}", False, f"HTTP {del_res.status_code}")
                except Exception as e:
                    log(f"❌ Lỗi khi xóa {file_name}: {e}")
                    record_action(f"Xóa file cũ: {file_name}", False, str(e))
        else:
            log(f"✅ Số lượng file ({len(log_files)}) vẫn trong giới hạn cho phép.")
            record_action("Dọn dẹp file cũ", True, f"{len(log_files)} file, không cần xóa")
            
    except Exception as e:
        log(f"❌ Lỗi trong quá trình dọn dẹp: {e}")
        record_action("Dọn dẹp file cũ", False, str(e))
        
# === TẠO VÀ UPLOAD FILE TỪ GROQ ===
log("📝 Đang chuẩn bị file upload...")

groq_text = get_groq_content()
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if groq_text:
    file_content = f"--- AUTOMATED CONTENT BY GROQ ---\nTime: {timestamp}\n\n{groq_text}\n\n-----------------------------------"
else:
    log("⚠️ Dùng nội dung fallback do Groq lỗi/thiếu key.")
    random_id = random.randint(100000, 999999)
    file_content = f"Auto-generated file for E5 Keep Active.\nTime: {timestamp}\nRandom ID: {random_id}"

filename = f"groq_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

upload_url = (
    f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
    f"/root:/{filename}:/content"
)

upload_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "text/plain; charset=utf-8"
}

log(f"🚀 Upload file lên SharePoint: {filename}")
        
try:
    res = requests.put(upload_url, headers=upload_headers, data=file_content.encode('utf-8-sig'), timeout=100)
    res.raise_for_status()
    log(f"✅ Upload thành công! → Status: {res.status_code}")
    record_action("Upload file SharePoint", True, filename)
    
    if res.status_code in [200, 201]:
        response_data = res.json()
        file_url = response_data.get("webUrl", "N/A")
        log(f"📎 File URL: {file_url}")
        
    # === GỌI HÀM DỌN DẸP TẠI ĐÂY ===
    cleanup_old_files(keep_count=5) 
    # ===============================

except Exception as e:
    log(f"❌ Upload lỗi: {e}")
    record_action("Upload file SharePoint", False, str(e))

# === Hoàn tất ===
log("✅ Hoàn thành ping E5!")

# === Tạo bảng tóm tắt kết quả hành động ===
total = len(action_results)
failed_actions = [(icon, name, detail) for icon, name, detail in action_results if icon == "❌"]
success_count = total - len(failed_actions)

summary_lines = [f"*📋 Báo cáo E5 Ping — {current_date}*", ""]
summary_lines.append(f"✅ Thành công: {success_count}/{total}")
if failed_actions:
    summary_lines.append(f"❌ Lỗi: {len(failed_actions)}/{total}")
summary_lines.append("")

summary_lines.append("*Chi tiết hành động:*")
for icon, name, detail in action_results:
    line = f"{icon} {name}"
    if detail and icon == "❌":
        # Giới hạn độ dài lỗi để tránh quá dài
        short_detail = detail[:80] + "..." if len(detail) > 80 else detail
        line += f"\n    ↳ `{short_detail}`"
    summary_lines.append(line)

if failed_actions:
    summary_lines.append("")
    summary_lines.append("⚠️ *Có lỗi xảy ra, vui lòng kiểm tra lại!*")
else:
    summary_lines.append("")
    summary_lines.append("🎉 Tất cả hành động hoàn thành thành công!")

summary_msg = "\n".join(summary_lines)

# === Gửi bảng tóm tắt về Telegram ===
send_telegram_message(summary_msg)

# === Gửi log đầy đủ về Telegram (nếu cần debug) ===
log_text = "\n".join(log_messages)
max_length = 4000
for i in range(0, len(log_text), max_length):
    chunk = log_text[i:i + max_length]
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage",
            data={"chat_id": os.getenv('TELEGRAM_CHAT_ID'), "text": chunk}
        )
    except Exception as e:
        print(f"Lỗi gửi log Telegram: {e}")
    time.sleep(2)
