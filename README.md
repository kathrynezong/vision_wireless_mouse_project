# Vision-Based Wireless Mouse

A Raspberry Pi 5 prototype that sends mouse movement to a laptop over Wi-Fi.
The project is designed to connect an OpenCV tracking pipeline on the Pi to a
lightweight UDP receiver that controls the laptop cursor with PyAutoGUI.

> [!NOTE]
> The Pi-to-laptop UDP link has been validated with manual movement packets.
> Automatic OpenCV tracking and the C++ sender are the next development steps.

## Project status

| Component | Status |
| --- | --- |
| Laptop UDP receiver | Working prototype |
| Pi-to-laptop network test | Verified |
| Relative cursor movement | Verified |
| C++ UDP sender | Planned |
| OpenCV tracking integration | Planned |
| Smoothing and gesture input | Planned |

## How it works

```text
Camera / tracking input
          |
          v
Raspberry Pi 5 + OpenCV
          |
          v
Calculate relative movement (dx, dy)
          |
          v
UDP sender over Wi-Fi
          |
          v
Python receiver on laptop (port 5005)
          |
          v
PyAutoGUI moves the laptop cursor
```

Movement is sent as a small UTF-8 UDP datagram:

```text
dx,dy
```

For example, `50,0` moves the pointer 50 pixels to the right.

## Requirements

### Laptop

- Python 3
- [PyAutoGUI](https://pyautogui.readthedocs.io/)
- A firewall rule that permits inbound UDP traffic on port `5005`

### Raspberry Pi

- Raspberry Pi 5
- A network connection to the laptop
- Bash for the current proof-of-concept test
- C++17 and OpenCV for the planned tracking integration

The UDP sender can be compiled on Raspberry Pi/Linux or Windows. On Raspberry
Pi/Linux, use `g++ -std=c++17 -Wall -Wextra -pedantic
vision_mouse_sender.cpp -o vision_mouse_sender`. On Windows with MinGW, use
`g++ -std=c++17 -Wall -Wextra -pedantic vision_mouse_sender.cpp -lws2_32 -o
vision_mouse_sender.exe`.

## Quick start

### 1. Clone the project

```bash
git clone https://github.com/kathrynezong/vision_wireless_mouse_project.git
cd vision_wireless_mouse_project
```

### 2. Install the laptop dependency

```bash
python -m pip install pyautogui
```

### 3. Start the receiver

Run this command on the laptop that will be controlled:

```bash
python scripts/test_wireless_movement.py
```

The receiver listens on all network interfaces at UDP port `5005`.

### 4. Find the laptop's IP address

On Windows, run:

```powershell
ipconfig
```

Find the IPv4 address for the active Wi-Fi adapter.

### 5. Send a test packet from the Pi

From a Bash shell on the Raspberry Pi, replace `LAPTOP_IP` with the address
from the previous step:

```bash
echo -n "50,0" > /dev/udp/LAPTOP_IP/5005
```

The laptop cursor should move to the right. Press `Ctrl+C` in the receiver
terminal to stop listening.

## Repository structure

```text
.
|-- scripts/
|   `-- test_wireless_movement.py  # Laptop UDP receiver
|-- .gitignore
`-- README.md
```

## Roadmap

- [x] Prove UDP connectivity between the Raspberry Pi and laptop
- [x] Move the laptop cursor from a relative movement packet
- [ ] Implement a reusable C++ UDP sender
- [ ] Connect OpenCV tracking output to the sender
- [ ] Add sensitivity, dead-zone, smoothing, and rate controls
- [ ] Validate packet source and reject malformed or excessive movement
- [ ] Add click and gesture events
- [ ] Document installation and startup for both devices

## Safety and security

This is an experimental local-network prototype. The current protocol has no
authentication or encryption, so use it only on a trusted network. Anyone able
to reach the receiver's UDP port could attempt to send movement packets.

The test receiver also disables PyAutoGUI's corner fail-safe. Keep its terminal
visible and use `Ctrl+C` as the stop mechanism while testing. A production
receiver should restore the fail-safe, restrict accepted senders, validate
packet bounds, and provide a dedicated enable/disable control.

## Known limitations

- The receiver must be running on the laptop being controlled.
- UDP packets may be lost, duplicated, forged, or delivered out of order.
- The current receiver accepts movement from any reachable sender.
- Camera tracking is not yet connected to the network transport.
- This project does not emulate a native USB or Bluetooth HID device.

## Contributing

Issues and small pull requests are welcome. When reporting a problem, include
the operating system, Python version, network setup, and steps to reproduce it.
