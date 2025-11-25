from ftplib import FTP

FTP_HOST = "192.168.10.123"
FTP_PORT = 21
FTP_USER = "molink"
FTP_PASS = "molinkadmin"

remote_folder = "/sdcard"   # Folder tujuan
local_file = "video.mp4"    # File di komputer lokal
remote_file = "video.mp4"   # Nama file di server

def upload_file():
    try:
        # Connect
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
        ftp.login(FTP_USER, FTP_PASS)

        print("[+] Connected to FTP server")

        # Pindah ke folder tujuan
        try:
            ftp.cwd(remote_folder)
        except:
            print(f"[!] Folder {remote_folder} tidak ada, membuat folder...")
            ftp.mkd(remote_folder)
            ftp.cwd(remote_folder)

        # Upload file
        with open(local_file, "rb") as f:
            ftp.storbinary(f"STOR {remote_file}", f)
            print(f"[+] Upload berhasil: {local_file} → {remote_folder}/{remote_file}")

        # Close connection
        ftp.quit()

    except Exception as e:
        print("[ERROR]", e)

if __name__ == "__main__":
    upload_file()
