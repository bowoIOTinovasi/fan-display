import os
import time
import subprocess
import socket
import struct
from ftplib import FTP

DEVICE_SSID = "Z7H2_D5E53327"  # ganti sesuai device kamu
DEVICE_PASS = "12345678"

DEVICE_IP = "192.168.10.123"  # default IP device dalam mode AP
TCP_PORT = 9910

FTP_USER = "molink"
FTP_PASS = "molinkadmin"


# -------------------------------------------------------------------
# WIFI: Connect ke Hotspot Device
# -------------------------------------------------------------------
def wifi_connect():
    print("[WiFi] Menghubungkan ke hotspot device...")

    # Buat file config wpa_supplicant sementara
    config = f"""
    network={{
        ssid="{DEVICE_SSID}"
        psk="{DEVICE_PASS}"
    }}
    """
    
    with open("/tmp/device_wifi.conf", "w") as f:
        f.write(config)

    # Matikan service wpa_supplicant bawaan
    os.system("sudo systemctl stop wpa_supplicant")

    # Jalankan wpa_supplicant manual
    os.system("sudo wpa_supplicant -B -i wlan0 -c /tmp/device_wifi.conf")

    # Ambil IP dari DHCP
    time.sleep(3)
    os.system("sudo dhclient wlan0")

    print("[WiFi] Menunggu IP...")
    time.sleep(5)


def wifi_has_ip():
    """Cek apakah sudah dapat IP 192.168.10.xxx"""
    try:
        ip = subprocess.check_output("hostname -I", shell=True).decode()
        print("[WiFi] IP Saat ini:", ip)
        return "192.168.10." in ip
    except:
        return False


# -------------------------------------------------------------------
# TCP COMMAND BUILDER
# -------------------------------------------------------------------
def build_cmd(cmd_type, data_str=""):
    data_bytes = data_str.encode()
    length = len(data_bytes)
    packet = b""
    packet += b"\x7E"                       # head
    packet += struct.pack(">I", length)     # 4 byte length
    packet += bytes([cmd_type])             # cmd byte
    packet += data_bytes                    # data
    packet += b"\x7F"                       # tail
    return packet


def tcp_send(cmd_type, data=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((DEVICE_IP, TCP_PORT))

    packet = build_cmd(cmd_type, data)
    sock.sendall(packet)

    resp = sock.recv(2048)
    sock.close()

    print("[TCP] RESP RAW:", resp)
    return resp


# -------------------------------------------------------------------
# FTP
# -------------------------------------------------------------------
def ftp_connect():
    ftp = FTP()
    ftp.connect(DEVICE_IP, 21)
    ftp.login(FTP_USER, FTP_PASS)
    print("[FTP] connected.")
    return ftp


def ftp_upload(local_path, remote_name):
    ftp = ftp_connect()
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_name}", f)
    ftp.quit()
    print("[FTP] Upload done:", remote_name)


# -------------------------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------------------------
print("=== CONNECTING TO DEVICE HOTSPOT ===")

wifi_connect()

while not wifi_has_ip():
    print("[WiFi] Belum dapat IP 192.168.10.x, mencoba ulang...")
    wifi_connect()

print("[WiFi] Terhubung ke hotspot device.")

# ---------------------------
# Tes command 0x01 (device info)
# ---------------------------
print("\n=== REQUEST DEVICE INFO (CMD 0x01) ===")
tcp_send(0x01)

# ---------------------------
# Notify before upload
# ---------------------------
print("\n=== SEND CMD 0x03 (notify before upload) ===")
tcp_send(0x03, "DisplayImageIdData=test.mp4")

# ---------------------------
# Upload file via FTP
# ---------------------------
print("\n=== UPLOAD VIA FTP ===")
ftp_upload("/home/pi/test.mp4", "test.mp4")

# ---------------------------
# Notify upload complete (CMD 0x05)
# ---------------------------
print("\n=== SEND CMD 0x05 (upload done) ===")
tcp_send(0x05)
