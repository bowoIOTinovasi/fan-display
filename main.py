import os
import time
import subprocess
import socket
import struct
from ftplib import FTP

DEVICE_SSID = "Z7H2_D5E53327"      # SSID AP device
DEVICE_PASS = "12345678"           # Password AP device

DEVICE_IP = "192.168.10.123"       # Default AP IP device
TCP_PORT   = 9910

FTP_USER = "molink"
FTP_PASS = "molinkadmin"

os.system("sudo killall wpa_supplicant")
os.system("sudo systemctl stop wpa_supplicant")
os.system("sudo systemctl disable wpa_supplicant")
os.system("sudo ip link set wlan0 down")
os.system("sudo ip link set wlan0 up")

# -------------------------------------------------------------------
# WIFI: Connect ke Hotspot Device
# -------------------------------------------------------------------
def wifi_connect():
    print("[WiFi] Connecting to device AP...")

    os.system("sudo killall wpa_supplicant")
    os.system("sudo systemctl stop wpa_supplicant")
    os.system("sudo ip link set wlan0 down")
    os.system("sudo ip link set wlan0 up")

    config = f'''network={{
        ssid="{DEVICE_SSID}"
        psk="{DEVICE_PASS}"
    }}'''

    with open("/tmp/device_wifi.conf", "w") as f:
        f.write(config)

    os.system("sudo wpa_supplicant -B -i wlan0 -c /tmp/device_wifi.conf")

    time.sleep(2)
    os.system("sudo dhclient -r wlan0")
    os.system("sudo dhclient wlan0")
    time.sleep(2)



def wifi_has_ip():
    """Cek apakah wlan0 sudah punya IP 192.168.10.xxx"""
    try:
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
        print("[WiFi] IP saat ini:", ip)
        return ip.startswith("192.168.10.")
    except:
        return False


# -------------------------------------------------------------------
# TCP COMMAND BUILDER
# -------------------------------------------------------------------
def build_cmd(cmd_type, data_str=""):
    data_bytes = data_str.encode()
    length = len(data_bytes)
    packet = (
        b"\x7E" +
        struct.pack(">I", length) +
        bytes([cmd_type]) +
        data_bytes +
        b"\x7F"
    )
    return packet


def tcp_send(cmd_type, data=""):
    print(f"[TCP] Send CMD {cmd_type:02X} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((DEVICE_IP, TCP_PORT))
        packet = build_cmd(cmd_type, data)
        sock.sendall(packet)

        resp = sock.recv(2048)
        print("[TCP] RESP:", resp)

        sock.close()
        return resp

    except Exception as e:
        print("[TCP] ERROR:", e)
        sock.close()
        return None


# -------------------------------------------------------------------
# FTP HANDLING
# -------------------------------------------------------------------
def ftp_connect():
    print("[FTP] Connecting...")
    ftp = FTP(timeout=30)
    ftp.connect(DEVICE_IP, 21)
    ftp.login(FTP_USER, FTP_PASS)
    print("[FTP] Connected!")
    return ftp


def ftp_upload(local_path, remote_name, folder="/sd_card"):
    ftp.sock.settimeout(30)
    ftp = ftp_connect()
    ftp.cwd(folder)
    print(f"[FTP] Uploading {local_path} → {folder}/{remote_name}")

    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_name}", f)

    ftp.quit()
    print("[FTP] Upload done.")


# -------------------------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------------------------
print("=== CONNECTING TO DEVICE HOTSPOT ===")

wifi_connect()

# Tunggu sampai dapat IP
while not wifi_has_ip():
    print("[WiFi] Belum dapat IP 192.168.10.x, retry...")
    wifi_connect()
    time.sleep(2)

print("[WiFi] Terhubung ke hotspot device!")


# ---------------------------
# CMD 0x01 → Minta info
# ---------------------------
print("\n=== CMD 0x01: REQUEST DEVICE INFO ===")
tcp_send(0x01)

time.sleep(1)

# ---------------------------
# CMD 0x03 → Notify sebelum upload
# ---------------------------
print("\n=== CMD 0x03: NOTIFY BEFORE UPLOAD ===")
tcp_send(0x03, "DisplayImageIdData=vid1.mp4")

time.sleep(1)

# ---------------------------
# FTP UPLOAD FILE
# ---------------------------
print("\n=== UPLOAD VIA FTP ===")
ftp_upload("/home/pi/fan-display/vid1.mp4", "vid1.mp4")

time.sleep(1)

# ---------------------------
# CMD 0x05 → Notify upload selesai
# ---------------------------
print("\n=== CMD 0x05: UPLOAD COMPLETE ===")
tcp_send(0x05)

# Restore normal wifi
os.system("sudo systemctl enable wpa_supplicant")
os.system("sudo systemctl start wpa_supplicant")
os.system("sudo wpa_cli -i wlan0 reconfigure")

print("\n=== SELESAI ===")
