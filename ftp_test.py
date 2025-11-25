from ftplib import FTP
import socket
import time

FTP_HOST = "192.168.10.123"
FTP_PORT = 21
FTP_USER = "molink"
FTP_PASS = "molinkadmin"

remote_folder = "/sdcard"
local_file = "/home/pi/fan-display/test.txt"
remote_file = "test.txt"


def try_upload(pasv_mode):
    try:
        print(f"\n[INFO] Testing PASV={pasv_mode}")

        ftp = FTP(timeout=25)
        ftp.set_debuglevel(2)  # debug

        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)

        ftp.set_pasv(pasv_mode)

        ftp.cwd(remote_folder)

        with open(local_file, "rb") as f:
            ftp.storbinary(f"STOR " + remote_file, f)

        print(f"[OK] Upload berhasil dengan PASV={pasv_mode}")
        ftp.quit()
        return True

    except Exception as e:
        print("[ERROR]", e)
        return False


if __name__ == "__main__":
    print("[INFO] Uji koneksi ke port 21...")

    s = socket.socket()
    s.settimeout(5)

    try:
        s.connect((FTP_HOST, FTP_PORT))
        print("[OK] Port 21 reachable\n")
    except Exception as e:
        print("[FAIL] Raspberry tidak bisa reach port 21:", e)
        exit()

    # Coba PASV
    if not try_upload(True):
        print("\n[INFO] PASV gagal → mencoba ACTIVE mode...")
        time.sleep(1)
        try_upload(False)
