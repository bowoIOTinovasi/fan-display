from ftplib import FTP
import os
import time

FTP_HOST = "192.168.10.123"
FTP_PORT = 21
FTP_USER = "molink"
FTP_PASS = "molinkadmin"

remote_folder = "/extsd"
local_file = "/home/pi/fan-display/vid1.mp4"
remote_file = "vid1.mp4"

BUFFER_SIZE = 16 * 1024   # 16 KB (aman untuk Raspberry Pi Zero)
TIMEOUT = 120             # Timeout besar 2 menit


def upload_large_file():
    ftp = FTP(timeout=TIMEOUT)
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)

    ftp.cwd(remote_folder)

    filesize = os.path.getsize(local_file)
    print(f"[INFO] Uploading {local_file} ({filesize/1024/1024:.2f} MB)")

    with open(local_file, "rb") as f:
        # Open data connection
        conn = ftp.transfercmd(f"STOR {remote_file}")

        sent = 0
        start = time.time()

        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break

            conn.sendall(chunk)
            sent += len(chunk)

            # Progress
            percent = sent * 100 / filesize
            print(f"\r[UPLOAD] {percent:.1f}% ({sent}/{filesize} bytes)", end='')

        conn.close()
        ftp.voidresp()

    print("\n[OK] Upload selesai!")
    ftp.quit()


if __name__ == "__main__":
    upload_large_file()
