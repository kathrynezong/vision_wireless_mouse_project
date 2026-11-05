import socket
import pyautogui

# This receiver accepts UDP packets in the "dx,dy" format and moves the
# laptop cursor by those relative amounts.

# Disable the fail-safe so the mouse doesn't get stuck in corners.
pyautogui.FAILSAFE = False

# Create one IPv4 UDP socket, bind it to every local interface, and listen on
# port 5005. recvfrom() below returns the received bytes and sender address.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
print("Listening for Pi mouse data on UDP port 5005...")

# Process packets continuously until the program is stopped.
while True:
    data, addr = sock.recvfrom(1024)
    try:
        # Input: a UTF-8 packet such as "50,0".
        # Output: two integers used as relative horizontal and vertical
        # cursor movement.
        dx, dy = map(int, data.decode().split(','))
        pyautogui.move(dx, dy)
    except Exception as e:
        # Ignore malformed packets so one bad datagram does not stop the
        # receiver. No cursor movement occurs for an invalid packet.
        pass