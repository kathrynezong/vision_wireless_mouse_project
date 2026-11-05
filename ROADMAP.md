# Vision Wireless Mouse — Development Roadmap

## Project Overview

The goal of this project is to develop a wireless mouse system that uses computer vision to track movement and translate it into real-time cursor control on a laptop.

The system will run computer vision and movement processing on a Linux device, then transmit mouse movement commands over UDP to a receiver running on the laptop.

### High-Level System Architecture

```text
Camera
   |
   v
Computer Vision / Object Tracking
   |
   v
Movement Calculation (dx, dy)
   |
   v
C++ UDP Sender (Linux)
   |
   |  Wi-Fi / UDP
   v
UDP Receiver (Laptop)
   |
   v
Operating System Mouse Control
   |
   v
Cursor Movement
```

## Phase 1 — UDP Communication (Completed)

**Objective:** Establish communication between the Linux device and laptop to control mouse movement remotely.

### Tasks
- [x] Set up a UDP receiver on the laptop.
- [x] Test UDP communication using Bash.
- [x] Implement a C++ UDP sender on Linux.
- [x] Parse command-line arguments for IP, port, dx, and dy.
- [x] Implement socket creation, IP conversion, and UDP transmission.
- [x] Verify that sending a UDP packet produces cursor movement.
- [ ] Complete additional error-handling and directional tests.

**Deliverable:** A functioning C++ program capable of sending a single mouse movement command over UDP.

---

## Phase 2 — Continuous Mouse Communication

**Objective:** Extend the UDP sender to support continuous movement updates without restarting the program.

### Tasks
- [ ] Refactor UDP transmission into a reusable function or class.
- [ ] Implement a continuous movement update loop.
- [ ] Simulate movement using predefined dx and dy values.
- [ ] Implement a configurable update frequency.
- [ ] Support clean shutdown and socket cleanup.
- [ ] Test repeated movement commands and communication reliability.

**Deliverable:** A reusable UDP communication module that can transmit movement commands continuously.

**Definition of Done:** The cursor responds to a sequence of movement commands without requiring the sender to restart.

---

## Phase 3 — Computer Vision and Tracking

**Objective:** Implement computer vision to detect and track the target using a camera.

### Tasks
- [ ] Set up camera access on the Linux device.
- [ ] Evaluate a suitable computer vision framework (e.g., OpenCV).
- [ ] Implement real-time frame capture and processing.
- [ ] Select and implement a tracking approach.
- [ ] Extract target coordinates (x, y) from each frame.
- [ ] Visualize tracking results for debugging.
- [ ] Handle situations where tracking is lost.

**Deliverable:** A standalone vision tracking module that continuously outputs target coordinates.

**Definition of Done:** The system consistently detects and tracks the intended target and produces usable position data.

---

## Phase 4 — Movement Processing and Cursor Mapping

**Objective:** Convert tracked target positions into accurate and stable mouse movement commands.

### Tasks
- [ ] Calculate relative displacement between successive tracked positions.
- [ ] Convert displacement into dx and dy commands.
- [ ] Implement configurable mouse sensitivity.
- [ ] Add smoothing to reduce jitter.
- [ ] Implement a dead zone to prevent unintended movement.
- [ ] Handle coordinate scaling and orientation.
- [ ] Test movement accuracy and responsiveness.

**Deliverable:** A movement processing module that converts computer vision coordinates into mouse commands.

**Definition of Done:** Tracked movements produce stable and predictable dx and dy values suitable for cursor control.

---

## Phase 5 — System Integration

**Objective:** Combine computer vision, movement processing, and UDP communication into a single working system.

### Tasks
- [ ] Connect the vision tracking output to the movement processing module.
- [ ] Connect movement processing to the C++ UDP sender.
- [ ] Implement an end-to-end processing loop.
- [ ] Verify real-time communication with the laptop receiver.
- [ ] Handle tracking failures and network errors.
- [ ] Implement startup, shutdown, and configuration procedures.

**Deliverable:** A fully integrated vision-based wireless mouse prototype.

**Definition of Done:** Moving the tracked target produces corresponding cursor movement on the laptop in real time.

---

## Phase 6 — Performance Optimization and Testing

**Objective:** Improve the responsiveness, accuracy, stability, and reliability of the complete system.

### Tasks
- [ ] Measure end-to-end latency.
- [ ] Evaluate tracking accuracy under different conditions.
- [ ] Measure frame processing and UDP transmission rates.
- [ ] Optimize CPU and memory usage.
- [ ] Evaluate movement smoothness and cursor precision.
- [ ] Test communication stability and packet loss.
- [ ] Tune sensitivity, smoothing, and dead-zone parameters.
- [ ] Conduct extended runtime and reliability tests.

**Deliverable:** A responsive and stable vision-based wireless mouse system.

**Definition of Done:** The system achieves acceptable latency, cursor accuracy, and stability during normal operation.

---

## Phase 7 — Documentation and Finalization

**Objective:** Prepare the project for reproducible setup, demonstration, and future development.

### Tasks
- [ ] Document the system architecture and software dependencies.
- [ ] Write installation and setup instructions for Linux and the laptop receiver.
- [ ] Document build and execution commands.
- [ ] Add configuration examples and troubleshooting instructions.
- [ ] Organize source code into maintainable modules.
- [ ] Record testing results and known limitations.
- [ ] Create a final demonstration.

**Deliverable:** A documented and reproducible project ready for demonstration and further development.

---

## Future Enhancements (Optional)

Potential features to explore after the core system is working:

- Mouse clicking and gesture recognition.
- Scrolling functionality.
- Adaptive movement sensitivity.
- Improved tracking using machine learning.
- Automatic device discovery on the local network.
- Wireless communication security.
- A graphical interface for configuration and calibration.
- Support for multiple operating systems.

---

## Project Milestone Tracker

| Phase | Milestone | Status |
|---|---|---|
| 1 | UDP Communication | Completed (core functionality) |
| 2 | Continuous Mouse Communication | Next |
| 3 | Computer Vision and Tracking | Not Started |
| 4 | Movement Processing and Cursor Mapping | Not Started |
| 5 | System Integration | Not Started |
| 6 | Performance Optimization and Testing | Not Started |
| 7 | Documentation and Finalization | Not Started |

## Development Approach

Each module should be developed and tested independently before system integration.

The project will follow an incremental approach:

1. **Build:** Implement the smallest functional version of a component.
2. **Test:** Verify the component works independently.
3. **Integrate:** Connect it with existing components.
4. **Evaluate:** Identify performance issues and improvements.
5. **Document:** Commit tested changes to GitHub and update project documentation.

This approach helps isolate problems, simplify debugging, and maintain steady progress throughout development.
