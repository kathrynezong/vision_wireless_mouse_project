# Technical Decisions

This document records design choices and proposed choices that affect multiple
parts of the project. A decision marked **Testing** is implemented but has not
yet been validated with the target webcam and should not be treated as final.

## DEC-001: Stabilize two-finger scrolling before UDP integration

- **Status:** Testing
- **Date:** 2026-11-11
- **Scope:** Python hand-gesture prototype

### Context

Scrolling is active after the index and middle fingers are recognized as
extended for three consecutive frames while the ring and pinky are folded.
Cursor movement pauses in the `SCROLL` state. Two invalid gesture frames are
required to leave that state, which prevents a single missed detection from
immediately moving the cursor.

The initial implementation averaged the vertical positions of the index and
middle fingertips (MediaPipe landmarks 8 and 12), then converted frame-to-frame
travel into scroll steps. That design only scrolled while the hand was moving.
Moving the hand back to its starting point reversed the scrolling, and leaving
the frame reset the gesture, so it was difficult to scroll continuously.

Image coordinates increase downward. Therefore:

- Holding the hand above its neutral position decreases `y` and generates
  positive scroll steps.
- Holding the hand below its neutral position increases `y` and generates
  negative scroll steps.

PyAutoGUI interprets positive steps as scrolling up and negative steps as
scrolling down.

MediaPipe landmarks still contain frame-to-frame noise, and PyAutoGUI accepts
whole wheel steps rather than fractional movement. The cursor's exponential
smoothing does not currently apply to scrolling.

### Decision under test

Use anchor-relative, rate-based scrolling:

1. Measure whole-hand vertical movement using the average of the index and
   middle MCP knuckles (landmarks 5 and 9) instead of the fingertips. The
   knuckles should move less when the user changes finger shape.
2. When the system enters `SCROLL`, record the current knuckle height as the
   neutral anchor.
3. Treat displacement above or below that anchor as a requested scroll rate,
   rather than converting distance traveled into a fixed number of steps.
4. Apply a dead zone around the anchor. Returning to this region stops output
   and clears fractional movement.
5. Increase the scroll rate linearly as the hand moves farther from the anchor,
   up to a configured maximum.
6. Accumulate fractional steps using elapsed time so output is not dependent on
   camera frame rate.
7. Limit output to one step in either direction per processed frame so a bad
   landmark update cannot create a large scroll burst.

Initial tuning values:

| Setting | Initial value | Trade-off |
| --- | ---: | --- |
| Anchor dead zone | `0.03` | Larger is steadier but needs more hand movement |
| Offset for maximum speed | `0.18` | Controls the usable speed range |
| Maximum scroll rate | `18` steps/second | Higher scrolls faster but can feel abrupt |
| Maximum steps per frame | `1` | Prevents bursts but limits maximum speed |
| Gesture confirmation | `3` frames | Reduces false entry but delays activation |
| Gesture release | `2` frames | Tolerates one missed detection |

These values must remain configurable because camera resolution, frame rate,
camera angle, lighting, and user hand movement can change the useful range.

### Consequences

- Scrolling should respond to movement of the hand rather than small movements
  of individual fingertips.
- The user can scroll continuously by holding the hand away from the anchor;
  repeated motion or leaving the camera frame is unnecessary.
- Returning to the anchor stops scrolling instead of reversing through the
  distance that was previously traveled.
- The dead zone adds intentional movement before scrolling begins.
- Fast output is rate-limited instead of producing a sudden burst.
- Losing tracking or leaving the two-finger gesture establishes a new anchor
  the next time scrolling begins.
- Scrolling will remain discrete because PyAutoGUI exposes wheel steps. Truly
  high-resolution scrolling would require a platform-specific input API, which
  is outside the first prototype's scope.
- The UDP protocol remains unchanged. Click and scroll messages must be
  designed separately when the gesture prototype is integrated with the C++
  sender and laptop receiver.

### Verification required

This decision has not yet been validated with a real webcam. Manual testing
should record:

- Whether holding the neutral two-finger pose produces unintended steps.
- Whether holding above and below the anchor scrolls continuously in the
  expected directions.
- Whether returning to the anchor stops without oscillating.
- Whether the dead zone and maximum rate feel controllable.
- Perceived activation delay and scroll latency.
- Behavior under different lighting, camera angles, and hand distances.

After testing, update this decision to **Accepted**, revise the initial values,
or record a replacement decision.
