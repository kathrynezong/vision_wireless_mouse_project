# Vision Wireless Mouse — Software Requirements

## 1. Project Objective

Develop a wireless mouse system that uses computer vision to track an intended target and translate its movement into cursor control on a laptop.

The initial system uses UDP communication over a local network.

## 2. Functional Requirements

### FR-01: UDP Mouse Movement

- The Linux device shall transmit relative mouse movement commands over UDP.
- Movement commands shall contain horizontal and vertical displacement values (`dx`, `dy`).
- The laptop receiver shall interpret supported commands and move the cursor accordingly.

**Status:** Basic functionality verified.

### FR-02: Continuous Communication

- The sender shall support repeated movement updates without restarting.
- The transmission frequency shall be configurable.
- The sender shall support clean termination.

**Status:** Planned.

### FR-03: Vision Tracking

- The system shall capture camera frames.
- The system shall detect and track an intended target.
- The tracking component shall output target coordinates.
- The system shall handle target detection failures.

**Status:** Planned.

### FR-04: Movement Processing

- The system shall convert tracked positions into relative displacement.
- Movement sensitivity shall be configurable.
- The system shall support techniques to reduce unintended cursor jitter.
- The system shall avoid unintended movement when valid tracking data is unavailable.

**Status:** Planned.

### FR-05: System Integration

- The vision, movement processing, and networking modules shall work together.
- The system shall support real-time cursor control.
- The system shall recover or fail safely when tracking or communication is interrupted.

**Status:** Planned.

## 3. Non-Functional Requirements

### Performance

- Minimize end-to-end input latency.
- Maintain stable cursor movement.
- Avoid unnecessary CPU and memory usage.

Specific quantitative targets will be established through prototype measurements.

### Reliability

- Handle invalid command-line arguments.
- Handle socket and network errors.
- Avoid unintended cursor movement during tracking loss.
- Release system resources on shutdown.

### Maintainability

- Use modular code.
- Separate platform-specific functionality.
- Document external dependencies.
- Provide reproducible build and test instructions.

## 4. Current Technology Choices

| Component | Technology | Status |
|---|---|---|
| Sender | C++17 on Linux | Implemented |
| Transport | UDP | Implemented |
| Receiver | Existing laptop mouse receiver | Working in basic test |
| Computer vision | To be determined | Planned |
| Movement filtering | To be determined | Planned |
| Build system | g++ currently | In use |

## 5. Open Design Questions

- What camera and Linux hardware will be used?
- What exactly will the camera track?
- What tracking algorithm is most appropriate?
- What update frequency will provide acceptable responsiveness?
- How will mouse clicking and scrolling be supported?
- What latency and accuracy targets are acceptable?
- Will the system use calibration or a fixed sensitivity?

These questions should be resolved as the project develops rather than treated as finalized requirements.
