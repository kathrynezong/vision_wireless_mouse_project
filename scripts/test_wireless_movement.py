import socket
import pyautogui

# Disable the fail-safe so the mouse doesn't get stuck in corners
pyautogui.FAILSAFE = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
print("Listening for Pi mouse data on UDP port 5005...")

while True:
    data, addr = sock.recvfrom(1024)
    try:
        # Expecting a string like "50,0" for dx, dy
        dx, dy = map(int, data.decode().split(','))
        pyautogui.move(dx, dy)
    except Exception as e:
        pass