# UDP Communication Protocol

## Overview

The Linux sender transmits relative mouse movement commands to a receiver on the laptop.

## Transport

- Protocol: UDP
- Address family: IPv4
- Destination IP: Configurable
- Destination port: Configurable
- Example port: 5005

## Message Format

Current intended payload format:

```text
dx,dy
```

Example:

```text
50,0
```

Meaning:
- dx = 50: Positive horizontal displacement
- dy = 0: No vertical displacement

The payload is transmitted as text.

## Example Sender Command

```bash
./vision_mouse_sender 192.168.1.50 5005 50 0
```

## Compatibility

The sender and receiver must agree on:

- Message formatting and delimiters
- Character encoding
- Movement units and sign convention
- Input validation
- Handling of invalid messages

The exact behavior should be verified against the working receiver implementation.

## Future Protocol Considerations

Potential extensions include:

- Message versioning
- Mouse button states
- Scrolling commands
- Sequence numbers
- Packet timestamps

Any protocol changes must be coordinated across the sender and receiver.
