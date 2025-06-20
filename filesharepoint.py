import requests
import os
from dotenv import load_dotenv

# === Load biến môi trường ===
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
user_email = os.getenv("USER_EMAIL")

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

print("✅ Token lấy thành công!")

# === Từ URL SharePoint của bạn ===
sharepoint_hostname = "h151147f.sharepoint.com"
sharepoint_site_path = ""  # Root site

print(f"\n🔍 === Lấy Site ID từ {sharepoint_hostname} ===")

# === Cách 1: Lấy root site theo hostname ===
try:
    site_url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_hostname}"
    site_res = requests.get(site_url, headers=headers)
    print(f"Site by hostname → Status: {site_res.status_code}")
    
    if site_res.status_code == 200:
        site_data = site_res.json()
        site_id = site_data.get('id')
        
        print(f"✅ Site tìm thấy:")
        print(f"   📛 Name: {site_data.get('displayName', 'N/A')}")
        print(f"   🆔 Site ID: {site_id}")
        print(f"   🔗 URL: {site_data.get('webUrl', 'N/A')}")
        
        # === Lấy các drives của site này ===
        print(f"\n📁 === Lấy Drives của Site ===")
        drives_res = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives", headers=headers)
        print(f"Drives → Status: {drives_res.status_code}")
        
        if drives_res.status_code == 200:
            drives_data = drives_res.json()
            print(f"📁 Tìm thấy {len(drives_data.get('value', []))} drives:")
            
            documents_drive_id = None
            
            for i, drive in enumerate(drives_data.get('value', [])):
                drive_name = drive.get('name', 'N/A')
                drive_id = drive.get('id', 'N/A')
                drive_type = drive.get('driveType', 'N/A')
                
                print(f"\n📁 Drive {i+1}:")
                print(f"   📛 Name: {drive_name}")
                print(f"   🆔 ID: {drive_id}")
                print(f"   📂 Type: {drive_type}")
                
                # Tìm drive "Documents" hoặc "Shared Documents"
                if "Documents" in drive_name or drive_name == "Documents":
                    documents_drive_id = drive_id
                    print(f"   ⭐ → ĐÂY LÀ DRIVE CHO 'Shared Documents'!")
            
            if documents_drive_id:
                print(f"\n🎯 === KẾT QUẢ CUỐI CÙNG ===")
                print(f"SHAREPOINT_SITE_ID={site_id}")
                print(f"SHAREPOINT_DRIVE_ID={documents_drive_id}")
                
                # === Kiểm tra thư mục teste5 ===
                print(f"\n📂 === Kiểm tra thư mục teste5 ===")
                folder_check_res = requests.get(
                    f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{documents_drive_id}/root:/teste5",
                    headers=headers
                )
                print(f"Folder check → Status: {folder_check_res.status_code}")
                
                if folder_check_res.status_code == 200:
                    folder_data = folder_check_res.json()
                    print(f"✅ Thư mục teste5 tồn tại:")
                    print(f"   📛 Name: {folder_data.get('name', 'N/A')}")
                    print(f"   🆔 ID: {folder_data.get('id', 'N/A')}")
                elif folder_check_res.status_code == 404:
                    print(f"⚠️ Thư mục teste5 chưa tồn tại, sẽ được tạo khi upload")
                else:
                    print(f"❌ Lỗi kiểm tra folder: {folder_check_res.text}")
                
                # === Test upload một file nhỏ ===
                print(f"\n🧪 === Test Upload ===")
                test_content = "Test file content from Python script"
                test_filename = "test_upload.txt"
                
                upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{documents_drive_id}/root:/teste5/{test_filename}:/content"
                
                upload_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "text/plain"
                }
                
                upload_res = requests.put(upload_url, headers=upload_headers, data=test_content.encode('utf-8'))
                print(f"Test upload → Status: {upload_res.status_code}")
                
                if upload_res.status_code in [200, 201]:
                    upload_data = upload_res.json()
                    print("✅ Test upload thành công!")
                    print(f"   📁 File: {upload_data.get('name', 'N/A')}")
                    print(f"   🔗 Web URL: {upload_data.get('webUrl', 'N/A')}")
                    
                    print(f"\n🎉 === HOÀN TẤT - CẬP NHẬT .ENV ===")
                    print(f"Thêm vào file .env của bạn:")
                    print(f"SHAREPOINT_SITE_ID={site_id}")
                    print(f"SHAREPOINT_DRIVE_ID={documents_drive_id}")
                else:
                    print(f"❌ Test upload thất bại: {upload_res.text}")
            else:
                print("❌ Không tìm thấy Documents drive")
        else:
            print(f"❌ Lỗi lấy drives: {drives_res.text}")
    else:
        print(f"❌ Lỗi lấy site: {site_res.text}")
        
        # === Thử cách khác nếu hostname không work ===
        print(f"\n🔄 === Thử cách khác: Tìm kiếm site ===")
        search_res = requests.get(f"https://graph.microsoft.com/v1.0/sites?search=h151147f", headers=headers)
        print(f"Search sites → Status: {search_res.status_code}")
        
        if search_res.status_code == 200:
            search_data = search_res.json()
            sites = search_data.get('value', [])
            print(f"Tìm thấy {len(sites)} sites:")
            
            for i, site in enumerate(sites):
                print(f"\n📍 Site {i+1}:")
                print(f"   📛 Name: {site.get('displayName', 'N/A')}")
                print(f"   🆔 ID: {site.get('id', 'N/A')}")
                print(f"   🔗 URL: {site.get('webUrl', 'N/A')}")
        else:
            print(f"❌ Search failed: {search_res.text}")

except Exception as e:
    print(f"❌ Exception: {e}")

# === Backup: Sử dụng OneDrive nếu SharePoint không work ===
print(f"\n🔄 === BACKUP: OneDrive của User ===")
try:
    onedrive_res = requests.get(f"https://graph.microsoft.com/v1.0/users/{user_email}/drive", headers=headers)
    print(f"OneDrive → Status: {onedrive_res.status_code}")
    
    if onedrive_res.status_code == 200:
        onedrive_data = onedrive_res.json()
        print(f"📁 OneDrive backup option:")
        print(f"   📛 Name: {onedrive_data.get('name', 'N/A')}")
        print(f"   🆔 Drive ID: {onedrive_data.get('id', 'N/A')}")
        print(f"   📂 Type: {onedrive_data.get('driveType', 'N/A')}")
        print(f"\n💡 Nếu SharePoint không work, có thể dùng:")
        print(f"   SHAREPOINT_SITE_ID=  # Để trống cho OneDrive")
        print(f"   SHAREPOINT_DRIVE_ID={onedrive_data.get('id', 'N/A')}")
    else:
        print(f"❌ OneDrive error: {onedrive_res.text}")
except Exception as e:
    print(f"❌ OneDrive exception: {e}")