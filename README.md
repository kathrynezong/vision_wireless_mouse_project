# Vision-Based Wireless Mouse

A Raspberry Pi 5 prototype that sends mouse movement to a laptop over Wi-Fi.
The project is designed to connect an OpenCV tracking pipeline on the Pi to a
lightweight UDP receiver that controls the laptop cursor with PyAutoGUI.

> [!NOTE]
> The Pi-to-laptop UDP link has been validated with manual movement packets.
> The C++ sender now supports finite continuous test sequences. Automatic
> OpenCV tracking is the next development step.

## Project status

| Component | Status |
| --- | --- |
| Laptop UDP receiver | Working prototype |
| Pi-to-laptop network test | Verified |
| Relative cursor movement | Verified |
| C++ UDP sender | Continuous test sequence implemented |
| Python hand tracking prototype | Implemented; webcam tuning pending |
| Local cursor and gesture input | Implemented; manual testing pending |
| C++/UDP vision integration | Planned |

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

The UDP sender can be compiled on Raspberry Pi/Linux or Windows. From the
`sender/` directory, on Raspberry Pi/Linux use:

```bash
g++ -std=c++17 -Wall -Wextra -pedantic main.cpp udp_sender.cpp -o vision_mouse_sender
```

On Windows with MinGW, use:

```bash
g++ -std=c++17 -Wall -Wextra -pedantic main.cpp udp_sender.cpp -lws2_32 -o vision_mouse_sender.exe
```

The first computer-vision test is a standalone C++ webcam viewer. After
installing OpenCV, compile it from the project root on Linux with:

```bash
g++ -std=c++17 -Wall -Wextra -pedantic vision/webcam_test.cpp \
    $(pkg-config --cflags --libs opencv4) -o vision/webcam_test
```

Run it with the default camera:

```bash
./vision/webcam_test
```

Pass a different camera index when needed:

```bash
./vision/webcam_test 1
```

The test displays camera frames and exits when `q`, `Q`, or Escape is pressed.

### Python hand-gesture prototype

Install the Python vision dependencies from the project root:

```bash
python -m pip install -r vision/requirements.txt
```

Run the MediaPipe webcam prototype:

```bash
python vision/hand_tracker_webcam.py
```

Mouse control starts disabled. Press `M` to enable or disable it and `Q` to
quit. PyAutoGUI's corner fail-safe remains enabled.

The prototype uses four exclusive gesture states:

| State | Input | Behavior |
| --- | --- | --- |
| `IDLE` | Control disabled or no hand | Produces no mouse action |
| `MOVE` | Index fingertip movement | Moves the cursor with smoothing |
| `CLICK` | Thumb-index pinch | Produces one left click per pinch |
| `SCROLL` | Index and middle extended; ring and pinky folded | Pauses cursor movement and scrolls vertically |

Entering `SCROLL` records the current knuckle height as the neutral position.
Hold the hand above that position to scroll up continuously, hold it below to
scroll down continuously, or return near the neutral position to stop. Leaving
the gesture or losing hand tracking resets the neutral position.

Pinch distances are measured relative to palm width to reduce sensitivity to
camera distance. Gesture confirmation, pinch hysteresis, and scroll
accumulation settings are defined in `vision/gesture_processor.py` for tuning.

Run the sender from the `sender/` directory with:

```bash
./vision_mouse_sender <IP> <port> <dx> <dy> [count] [interval_ms]
```

By default, the sender transmits 20 packets 50 milliseconds apart (20 Hz).
The optional `count` and `interval_ms` arguments configure the finite test
sequence. Use `count` equal to `1` for a single packet.

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
|-- vision/
|   |-- gesture_processor.py       # Gesture state machine
|   |-- hand_tracker_webcam.py     # MediaPipe cursor prototype
|   `-- requirements.txt           # Python vision dependencies
|-- .gitignore
`-- README.md
```

## Roadmap

- [x] Prove UDP connectivity between the Raspberry Pi and laptop
- [x] Move the laptop cursor from a relative movement packet
- [x] Implement a reusable C++ UDP sender
- [x] Create a standalone C++ webcam capture test
- [x] Prototype smoothed cursor movement and core hand gestures in Python
- [ ] Connect OpenCV tracking output to the sender
- [ ] Add sensitivity, dead-zone, smoothing, and rate controls
- [ ] Validate packet source and reject malformed or excessive movement
- [ ] Extend the UDP protocol and receiver for click and scroll events
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
- Python camera tracking and gestures are not yet connected to the network
  transport.
- Gesture thresholds have automated state-machine tests but still require
  manual tuning with a real webcam, lighting conditions, and hand positions.
- This project does not emulate a native USB or Bluetooth HID device.

## Contributing

Issues and small pull requests are welcome. When reporting a problem, include
the operating system, Python version, network setup, and steps to reproduce it.
