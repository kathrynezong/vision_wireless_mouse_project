# Raspberry Pi Wi-Fi Mouse Controller

A Raspberry Pi 5 mouse-control project using OpenCV-based tracking and a UDP network bridge to move a laptop's cursor over Wi-Fi.

> **Current status:** The basic Pi-to-laptop UDP link has been tested successfully: a manually sent `50,0` packet moved the laptop cursor. Automatic OpenCV-to-UDP integration is the **next step**, not yet verified.

## Project goal

Use a Raspberry Pi 5 to process camera/tracking input, calculate pointer movement, and control a laptop's cursor without a physical USB-C data connection.

## Architecture

```text
[Camera / tracking input]
           |
           v
[Raspberry Pi 5: OpenCV processing]
           |
           v
[Compute relative cursor movement: dx, dy]   <- integration planned
           |
           v
[C++ UDP sender on Raspberry Pi]             <- next implementation
           |
           |  Wi-Fi: UDP packets, e.g. "50,0"
           v
[Python UDP receiver on laptop :5005]        <- tested
           |
           v
[PyAutoGUI relative cursor movement]         <- tested
           |
           v
[Laptop cursor]
```

## Hardware and software

- Raspberry Pi 5, accessible over SSH
- Laptop connected to a network that can reach the Pi
- Python 3 and `pyautogui` on the laptop
- Bash on the Pi for the initial UDP test
- Planned: C++ POSIX sockets and OpenCV tracking integration on the Pi

## Progress

| Task | Status | Evidence / notes |
| --- | --- | --- |
| Connect to Raspberry Pi via SSH | ✅ Complete | Existing SSH session used to run commands on the Pi |
| Identify laptop LAN IPv4 address | ✅ Complete | Used as the UDP packet destination; specific IP not recorded here |
| Start Python UDP receiver on laptop | ✅ Complete | Receiver listens on UDP port 5005 |
| Send test UDP packet from Pi | ✅ Complete | Bash `/dev/udp` sent `50,0` |
| Confirm laptop cursor moves from UDP data | ✅ Complete | Cursor jumped as expected |
| Connect tracking/vision pipeline to UDP | ⏳ Next | Replace test packets with live movement data |
| Validate smoothing, latency and reliability | ⏳ Planned | Add filtering, rate limiting and safeguards |
| Package and document startup | ⏳ Planned | Dependency setup and launch commands |

## Current UDP protocol

For the initial prototype, each UDP datagram contains a UTF-8 string:

```text
dx,dy
```

Example:

```text
50,0
```

This is **relative movement**: `dx=50` means 50 pixels right, and `dy=0` means no vertical movement. If the tracking algorithm outputs absolute coordinates, they must first be mapped or converted appropriately; `pyautogui.moveTo(x, y)` is an alternative for an absolute-position design.

## Reproduce the working network test

### 1. Find the laptop IP

On Windows:

```powershell
ipconfig
```

Find the `IPv4 Address` under the active Wi-Fi adapter. Use that address as `LAPTOP_IP` below. Both systems must have a network path between them; guest Wi-Fi or client isolation may block this.

### 2. Start the laptop receiver

Install the Python dependency:

```bash
python -m pip install pyautogui
```

Save this as `receiver.py` on the laptop:

```python
import socket
import pyautogui

HOST = "0.0.0.0"
PORT = 5005
MAX_STEP = 100  # Prevent unexpectedly large single-packet jumps.

# Leave PyAutoGUI's corner fail-safe enabled.
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((HOST, PORT))
    print(f"Listening for mouse packets on UDP port {PORT}...")

    while True:
        data, address = sock.recvfrom(1024)
        try:
            payload = data.decode("utf-8").strip()
            parts = payload.split(",")
            if len(parts) != 2:
                continue
            dx, dy = (int(v) for v in parts)
            if abs(dx) > MAX_STEP or abs(dy) > MAX_STEP:
                continue
            pyautogui.moveRel(dx, dy, duration=0)
        except pyautogui.FailSafeException:
            print("PyAutoGUI fail-safe triggered; stopping receiver.")
            break
        except (ValueError, UnicodeDecodeError):
            continue
```

Run it:

```bash
python receiver.py
```

**Security note:** This basic prototype has no authentication. Use it only on a trusted network. A future version should validate sender addresses and ideally authenticate packets.

### 3. Send a test command from the Pi

From the Pi's Bash SSH shell, substitute the laptop's real IPv4 address:

```bash
echo -n "50,0" > /dev/udp/LAPTOP_IP/5005
```

**Observed result:** The laptop cursor moved, confirming that the Pi can reach the receiving process and that the receiver can invoke local pointer movement.

If it stops working, check the IP address, whether the receiver is running, the laptop firewall's inbound UDP rule for port 5005, and whether the devices can reach each other.

## Next: implement a C++ UDP sender

The initial sender will take `(dx, dy)` and send one datagram to the laptop. Start with a standalone test program before editing the existing `hid_emitter.cpp` or the tracking pipeline.

Example `udp_sender.cpp`:

```cpp
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::fprintf(stderr, "Usage: %s LAPTOP_IP dx dy\n", argv[0]);
        return 1;
    }

    const int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        std::perror("socket");
        return 1;
    }

    sockaddr_in destination{};
    destination.sin_family = AF_INET;
    destination.sin_port = htons(5005);
    if (inet_pton(AF_INET, argv[1], &destination.sin_addr) != 1) {
        std::fprintf(stderr, "Invalid IPv4 address\n");
        close(fd);
        return 1;
    }

    const std::string message = std::string(argv[2]) + "," + argv[3];
    const auto sent = sendto(fd, message.data(), message.size(), 0,
                             reinterpret_cast<sockaddr*>(&destination),
                             sizeof(destination));
    if (sent < 0) {
        std::perror("sendto");
        close(fd);
        return 1;
    }

    std::printf("Sent: %s\n", message.c_str());
    close(fd);
    return 0;
}
```

Compile and run on the Pi:

```bash
g++ -std=c++17 -Wall -Wextra udp_sender.cpp -o udp_sender
./udp_sender LAPTOP_IP 50 0
```

Then refactor the code into a reusable `UdpMouseSender` class or function and integrate it into the part of the OpenCV program that calculates pointer deltas.

## Integration roadmap

1. **C++ transport:** Verify `udp_sender.cpp` produces the same cursor movement as the Bash test.
2. **Tracking integration:** Identify the existing function that calculates movement; feed relative `(dx, dy)` values into the C++ sender. Avoid replacing the whole tracking pipeline.
3. **Coordinate mapping:** Convert camera coordinates to appropriate cursor deltas; handle axis inversion and scaling if required.
4. **Motion quality:** Add dead zone, smoothing, sensitivity adjustment, and packet-rate limiting (e.g. 30–60 updates/second) to reduce jitter and excess traffic.
5. **Input actions:** Add clicking or gestures only after movement is reliable; define a packet format that distinguishes actions safely.
6. **Robustness:** Add a clear enable/disable switch, startup instructions, logging and tests. On a trusted LAN, consider a protocol with sequence numbers, authenticated sender validation and source filtering.

## Design notes and trade-offs

- **UDP** is lightweight and typically suitable for real-time cursor updates, where an occasional dropped movement packet may be preferable to retransmission delays.
- **Wi-Fi control is not native USB HID.** It requires a receiver program to run on the laptop; it will not control a device that cannot run the receiver.
- **UDP is not inherently reliable or secure.** Packets can arrive out of order, be lost, or be forged on an exposed network.
- **Safety:** Keep PyAutoGUI fail-safe enabled; use an obvious stop mechanism and bound input movements.

## What has actually been demonstrated

A Raspberry Pi, connected via SSH, sent a UDP datagram containing relative movement values to a Python listener on a laptop. The Python process received those values and successfully moved the laptop cursor. This validates the **network transport proof of concept**. The end-to-end OpenCV-driven mouse controller remains to be implemented and tested.
