# AGENTS.md — Vision Wireless Mouse

## Project Context

This project is a computer-vision-based wireless mouse system.

A Linux device processes tracking information and sends relative mouse movement commands over UDP to a receiver running on a laptop.

The system is being developed incrementally, with each component tested independently before integration.

## Project Documentation

Before implementing significant changes, consult the relevant documents:

- `README.md` — project overview and setup.
- `ROADMAP.md` — current milestone and future development.
- `docs/REQUIREMENTS.md` — expected system behavior.
- `docs/ARCHITECTURE.md` — system components and data flow.
- `docs/PROTOCOL.md` — UDP communication contract.
- `docs/DECISIONS.md` — documented technical decisions, if available.

If these files are missing or incomplete, do not assume they contain finalized decisions.

## Development Environment

- Sender platform: Linux.
- Receiver platform: Laptop (currently Windows).
- Sender language: C++17.
- Networking: UDP over a local network.
- Computer vision: Planned; framework and tracking approach not finalized.
- Build system: Currently g++; CMake may be introduced later.
- Version control: Git and GitHub.

## Coding Guidelines

- Prefer simple, readable, modular C++.
- Use descriptive function and variable names.
- Separate networking, movement processing, and vision tracking.
- Prefer standard libraries where practical.
- Handle errors explicitly and release resources correctly.
- Avoid unnecessary dependencies and abstractions.
- Do not introduce new frameworks without explaining the benefits.
- Keep platform-specific implementation details isolated.

## AI Collaboration Instructions

When assisting with development:

1. Read the relevant documentation and existing code first.
2. Identify the current development milestone.
3. Explain the implementation approach before significant changes.
4. Prefer small, incremental changes rather than large rewrites.
5. Preserve currently working functionality.
6. Do not change the UDP message format without identifying and updating affected components.
7. Include build commands and verification steps.
8. Distinguish tested behavior from assumptions or unverified changes.
9. Explain important technical decisions and trade-offs.
10. Update relevant documentation when implementation or behavior changes.

## Testing Expectations

- Compile modified C++ code with warnings enabled.
- Test individual modules before integration.
- Validate UDP messages and error handling.
- Verify that mouse movement behaves correctly on the receiver.
- Do not claim hardware or network tests passed unless they were actually executed.

## Safety and Reliability

- Avoid uncontrolled or unbounded cursor movement during testing.
- Provide a reliable way to stop continuous transmission.
- Validate network addresses, ports, and movement inputs.
- Handle camera tracking loss without unintended movement.
- Do not commit credentials, private keys, or machine-specific secrets.

## Current Project Status

- Basic UDP sender: Implemented and manually verified.
- Continuous UDP transmission: Finite test sequence implemented; network
  reliability testing remains.
- Computer vision tracking: Not yet implemented.
- Vision-to-cursor integration: Not yet implemented.

Update this section as project milestones are completed.
