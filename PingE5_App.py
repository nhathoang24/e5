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
gemini_api_key = os.getenv("GEMINI_API_KEY")

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
    
except Exception as e:
    error_msg = f"❌ Lỗi lấy token: {e}"
    log(error_msg)
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
        log(f"{label} → Status: {res.status_code}")
        return res
    except Exception as e:
        log(f"⚠️ {label} → Lỗi: {e}")
        return None

# === Hàm lấy nội dung từ Gemini API ===
def get_gemini_content():
    if not gemini_api_key:
        log("⚠️ Không tìm thấy GEMINI_API_KEY. Sử dụng nội dung mặc định.")
        return None

    log("🤖 Đang nhờ Gemini viết nội dung...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={gemini_api_key}"
    
    prompts = [
        "Viết một đoạn văn ngắn (khoảng 50 từ) về một sự thật thú vị trong khoa học máy tính.",
        "Viết một mẹo nhỏ hữu ích cho lập trình viên Python.",
        "Giải thích ngắn gọn khái niệm Cloud Computing bằng tiếng Việt.",
        "Viết một câu danh ngôn truyền cảm hứng cho người làm công nghệ.",
        "Tóm tắt ngắn gọn lịch sử của Internet trong 3 câu.",
        "Mô tả ngắn gọn cách hoạt động của thuật toán sắp xếp nhanh (QuickSort).",
        "Viết một đoạn văn 40–60 từ về một ứng dụng thú vị của trí tuệ nhân tạo trong đời sống.",
        "Giải thích tại sao cấu trúc dữ liệu cây nhị phân lại quan trọng.",
        "Viết một mẹo tối ưu hiệu suất cho lập trình viên JavaScript.",
        "Trình bày ngắn gọn sự khác nhau giữa TCP và UDP.",
        "Giải thích khái niệm 'REST API' bằng lời đơn giản.",
        "Viết một câu động lực dành cho người đang học lập trình.",
        "Tóm tắt lợi ích chính của việc sử dụng Git trong phát triển phần mềm.",
        "Giải thích ngắn gọn kiến trúc microservices.",
        "Viết một đoạn mô tả ngắn về tầm quan trọng của bảo mật thông tin.",
        "Giải thích sự khác biệt giữa RAM và ROM cho người mới học.",
        "Viết một ví dụ đơn giản về ứng dụng của học máy trong y tế.",
        "Tóm tắt vai trò của hệ điều hành trong máy tính.",
        "Mô tả ngắn gọn mô hình Client–Server.",
        "Viết một mẹo giúp cải thiện chất lượng code trong bất kỳ ngôn ngữ lập trình nào.",
        "Giải thích khái niệm Container (như Docker) bằng tiếng Việt.",
        "Tóm tắt cách hoạt động của trình biên dịch (compiler).",
        "Mô tả ngắn gọn kiến trúc mạng LAN.",
        "Giải thích 'big data' bằng một đoạn 2–3 câu.",
        "Viết một mô tả ngắn về blockchain và lý do nó được ứng dụng rộng rãi."
    ]

    selected_prompt = random.choice(prompts)

    payload = {
        "contents": [{
            "parts": [{"text": selected_prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=100)
        if response.status_code == 200:
            result = response.json()
            text_content = result['candidates'][0]['content']['parts'][0]['text']
            log("✅ Gemini đã trả về nội dung.")
            return text_content
        else:
            log(f"⚠️ Lỗi Gemini API: {response.status_code}")
            return None
    except Exception as e:
        log(f"⚠️ Lỗi khi gọi Gemini: {e}")
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
except Exception as e:
    log(f"⚠️ Gửi mail lỗi: {e}")

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
        
        # 2. Lọc ra các file do bot tạo (có tiền tố gemini_log_)
        # Lưu ý: Lọc để tránh xóa nhầm file quan trọng khác của bạn
        log_files = [f for f in items if f.get('name', '').startswith('gemini_log_')]
        
        # 3. Sắp xếp theo thời gian tạo (Mới nhất đứng đầu)
        # API trả về createdDateTime dạng chuỗi ISO, có thể sort trực tiếp
        log_files.sort(key=lambda x: x['createdDateTime'], reverse=True)
        
        # 4. Kiểm tra số lượng
        if len(log_files) > keep_count:
            files_to_delete = log_files[keep_count:] # Lấy danh sách file dư thừa
            log(f"⚠️ Tìm thấy {len(log_files)} file log. Sẽ xóa {len(files_to_delete)} file cũ...")
            
            for file in files_to_delete:
                file_id = file['id']
                file_name = file['name']
                delete_url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}/items/{file_id}"
                
                try:
                    del_res = requests.delete(delete_url, headers=headers, timeout=60)
                    if del_res.status_code == 204:
                        log(f"🗑️ Đã xóa: {file_name}")
                    else:
                        log(f"❌ Xóa thất bại {file_name}: {del_res.status_code}")
                except Exception as e:
                    log(f"❌ Lỗi khi xóa {file_name}: {e}")
        else:
            log(f"✅ Số lượng file ({len(log_files)}) vẫn trong giới hạn cho phép.")
            
    except Exception as e:
        log(f"⚠️ Lỗi trong quá trình dọn dẹp: {e}")
        
# === TẠO VÀ UPLOAD FILE TỪ GEMINI ===
log("📝 Đang chuẩn bị file upload...")

gemini_text = get_gemini_content()
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if gemini_text:
    file_content = f"--- AUTOMATED CONTENT BY GEMINI ---\nTime: {timestamp}\n\n{gemini_text}\n\n-----------------------------------"
else:
    log("⚠️ Dùng nội dung fallback do Gemini lỗi/thiếu key.")
    random_id = random.randint(100000, 999999)
    file_content = f"Auto-generated file for E5 Keep Active.\nTime: {timestamp}\nRandom ID: {random_id}"

filename = f"gemini_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

upload_url = (
    f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_id}/drives/{sharepoint_drive_id}"
    f"/root:/{filename}:/content"
)

upload_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "text/plain; charset=utf-8"
}

log(f"🚀 Upload file lên SharePoint: {filename}")
        
except Exception as e:
    log(f"⚠️ Upload lỗi: {e}")

try:
    res = requests.put(upload_url, headers=upload_headers, data=file_content.encode('utf-8-sig'), timeout=100)
    res.raise_for_status()
    log(f"✅ Upload thành công! → Status: {res.status_code}")
    
    if res.status_code in [200, 201]:
        response_data = res.json()
        file_url = response_data.get("webUrl", "N/A")
        log(f"📎 File URL: {file_url}")
        
    # === GỌI HÀM DỌN DẸP TẠI ĐÂY ===
    cleanup_old_files(keep_count=5) 
    # ===============================

except Exception as e:
    log(f"⚠️ Upload lỗi: {e}")

# === Hoàn tất ===
log("✅ Hoàn thành ping E5!")

# === Gửi log về Telegram ===
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
