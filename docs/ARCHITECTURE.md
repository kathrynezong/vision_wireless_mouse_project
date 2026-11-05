# System Architecture

## Overview

The system converts movement detected by a camera into wireless cursor movement on a laptop.

## Proposed Data Flow

```text
Linux Device
┌─────────────────────────────┐
│ Camera                      │
│   ↓                         │
│ Vision Tracking Module      │
│   ↓ (x, y)                  │
│ Movement Processing Module  │
│   ↓ (dx, dy)                │
│ C++ UDP Sender              │
└──────────────┬──────────────┘
               │
          Wi-Fi / UDP
               │
               ▼
Laptop
┌─────────────────────────────┐
│ UDP Receiver                │
│   ↓                         │
│ Mouse Control Interface     │
│   ↓                         │
│ Operating System Cursor     │
└─────────────────────────────┘
```

## Current Implementation

The Linux sender accepts an IP address, port, dx, and dy as command-line arguments.

It creates a UDP socket and transmits a movement command to the laptop receiver.

The receiver moves the cursor based on the received command.

The basic single-command workflow has been manually verified.

## Planned Software Modules

### Vision Tracking
- Input: Camera frames
- Output: Tracked target coordinates
- Responsibilities: Detection, tracking, tracking-loss handling

### Movement Processing
- Input: Tracked target coordinates
- Output: Relative movement commands
- Responsibilities: Displacement calculation, sensitivity, smoothing, dead zone

### UDP Sender
- Input: dx, dy
- Output: UDP datagram
- Responsibilities: Message serialization and network transmission

### UDP Receiver
- Input: UDP datagram
- Output: Operating system mouse movement
- Responsibilities: Message validation, interpretation, cursor control

## Design Principles

- Keep networking independent from computer vision.
- Prefer small, testable modules.
- Preserve compatibility between sender and receiver.
- Minimize unnecessary processing and communication overhead.
- Maintain a safe way to stop mouse control.
