import os
import socket
import time
import subprocess

WIFI_SSID = "NamaWiFi"
WIFI_PSK  = "PasswordWiFi"

SERVER_IP   = "192.168.1.10"   # IP TCP server
SERVER_PORT = 5000             # port TCP server

def wifi_connected():
    """Cek apakah wlan0 sudah punya IP."""
    try:
        output = subprocess.check_output("hostname -I", shell=True).decode()
        return "192." in output or "10." in output or "172." in output
    except:
        return False

def connect_wifi():
    """Perintah CLI untuk menghubungkan WiFi."""
    print("[WiFi] Menghubungkan ke WiFi...")

    config = f"""
network={{
    ssid="{WIFI_SSID}"
    psk="{WIFI_PSK}"
}}
"""
    with open("/tmp/wifi.conf", "w") as f:
        f.write(config)

    os.system("sudo wpa_supplicant -B -i wlan0 -c /tmp/wifi.conf")
    time.sleep(5)
    os.system("sudo dhclient wlan0")
    time.sleep(3)

def connect_tcp():
    """Menyambungkan ke TCP server."""
    while True:
        try:
            print("[TCP] Menghubungkan ke server...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((SERVER_IP, SERVER_PORT))
            print("[TCP] Terhubung ke server!")

            while True:
                msg = "Hello from Raspberry Pi Zero"
                sock.sendall(msg.encode())
                print("[TCP] Sent:", msg)

                try:
                    data = sock.recv(1024)
                    print("[TCP] Received:", data.decode())
                except:
                    print("[TCP] Tidak ada balasan")

                time.sleep(2)

        except Exception as e:
            print("[TCP] Error:", e)
            print("[TCP] Reconnecting in 3s...")
            time.sleep(3)


def main():
    while True:
        if wifi_connected():
            print("[WiFi] Sudah terhubung ke jaringan!")
            connect_tcp()
        else:
            print("[WiFi] Tidak ada koneksi. Mencoba konek...")
            connect_wifi()
            time.sleep(5)

main()
