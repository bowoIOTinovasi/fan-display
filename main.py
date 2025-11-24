import socket
import struct
from ftplib import FTP
import time

DEVICE_IP = "192.168.10.123"
TCP_PORT = 9910

FTP_USER = "molink"
FTP_PASS = "molinkadmin"

# ========== FUNGSI BUAT COMMAND PACKET ==========
def build_cmd(cmd_type, data_str=""):
    data_bytes = data_str.encode()
    length = len(data_bytes)

    packet = b""
    packet += b"\x7E"                          # head
    packet += struct.pack(">I", length)         # 4-byte big-endian length
    packet += bytes([cmd_type])                 # command type
    packet += data_bytes                        # payload
    packet += b"\x7F"                           # tail

    return packet

# ========== KIRIM COMMAND DAN TERIMA BALASAN ==========
def tcp_send_command(cmd_type, data=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((DEVICE_IP, TCP_PORT))

    packet = build_cmd(cmd_type, data)
    sock.sendall(packet)

    resp = sock.recv(2048)
    sock.close()

    print("RESP RAW:", resp)
    return resp

# ========== FTP UPLOAD / DOWNLOAD ==========
def ftp_connect():
    ftp = FTP()
    ftp.connect(DEVICE_IP, 21)
    ftp.login(FTP_USER, FTP_PASS)
    print("FTP connected.")
    return ftp

def ftp_upload(local_file, remote_file):
    ftp = ftp_connect()
    with open(local_file, "rb") as f:
        ftp.storbinary(f"STOR {remote_file}", f)
    ftp.quit()
    print("Upload success:", remote_file)

def ftp_download(remote_file, local_file):
    ftp = ftp_connect()
    with open(local_file, "wb") as f:
        ftp.retrbinary(f"RETR {remote_file}", f.write)
    ftp.quit()
    print("Download success:", remote_file)

# ==================== DEMO ====================
print("=== Request device info (CMD 0x01) ===")
tcp_send_command(0x01)

time.sleep(1)

print("=== Notify device before upload (CMD 0x03) ===")
tcp_send_command(0x03, 'DisplayImageIdData=test.mp4')

time.sleep(1)

print("=== Upload file via FTP like FileZilla ===")
ftp_upload("/home/pi/video.mp4", "video.mp4")

time.sleep(1)

print("=== Notify device upload done (CMD 0x05) ===")
tcp_send_command(0x05)
