"""Gesture classification for the vision mouse prototype."""

from dataclasses import dataclass
from enum import Enum
import math
import time


class GestureState(Enum):
    """Mutually exclusive mouse-control states."""

    IDLE = "IDLE"
    MOVE = "MOVE"
    CLICK = "CLICK"
    SCROLL = "SCROLL"


@dataclass(frozen=True)
class GestureResult:
    """Actions produced by one frame of hand landmarks."""

    state: GestureState
    click_requested: bool = False
    scroll_steps: int = 0


class GestureProcessor:
    """Convert MediaPipe hand landmarks into exclusive mouse gestures."""

    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_TIP = 12
    RING_PIP = 14
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_TIP = 20

    def __init__(
        self,
        pinch_start_ratio=0.28,
        pinch_release_ratio=0.40,
        pinch_confirmation_frames=2,
        scroll_confirmation_frames=3,
        scroll_release_frames=2,
        scroll_dead_zone=0.02,
        scroll_max_offset=0.08,
        scroll_max_steps_per_second=90.0,
        max_scroll_steps_per_frame=1,
    ):
        if pinch_start_ratio >= pinch_release_ratio:
            raise ValueError(
                "Pinch start ratio must be less than release ratio"
            )
        if pinch_confirmation_frames < 1:
            raise ValueError(
                "Pinch confirmation frames must be at least 1"
            )
        if scroll_confirmation_frames < 1:
            raise ValueError(
                "Scroll confirmation frames must be at least 1"
            )
        if scroll_release_frames < 1:
            raise ValueError(
                "Scroll release frames must be at least 1"
            )
        if scroll_dead_zone < 0:
            raise ValueError("Scroll dead zone must not be negative")
        if scroll_max_offset <= scroll_dead_zone:
            raise ValueError(
                "Scroll maximum offset must exceed the dead zone"
            )
        if scroll_max_steps_per_second <= 0:
            raise ValueError(
                "Maximum scroll rate must be positive"
            )
        if max_scroll_steps_per_frame < 1:
            raise ValueError(
                "Maximum scroll steps per frame must be at least 1"
            )

        self.pinch_start_ratio = pinch_start_ratio
        self.pinch_release_ratio = pinch_release_ratio
        self.pinch_confirmation_frames = pinch_confirmation_frames
        self.scroll_confirmation_frames = scroll_confirmation_frames
        self.scroll_release_frames = scroll_release_frames
        self.scroll_dead_zone = scroll_dead_zone
        self.scroll_max_offset = scroll_max_offset
        self.scroll_max_steps_per_second = scroll_max_steps_per_second
        self.max_scroll_steps_per_frame = max_scroll_steps_per_frame

        self.state = GestureState.IDLE
        self._pinch_frames = 0
        self._pinch_latched = False
        self._scroll_candidate_frames = 0
        self._scroll_release_frames = 0
        self._scroll_anchor_y = None
        self._last_scroll_timestamp = None
        self._scroll_remainder = 0.0

    @staticmethod
    def _distance(first, second):
        return math.hypot(
            first.x - second.x,
            first.y - second.y,
        )

    @staticmethod
    def _is_extended(hand, tip_index, pip_index, mcp_index):
        return (
            hand[tip_index].y < hand[pip_index].y
            and hand[pip_index].y < hand[mcp_index].y
        )

    @staticmethod
    def _is_folded(hand, tip_index, pip_index):
        return hand[tip_index].y > hand[pip_index].y

    def _is_pinch_candidate(self, hand):
        palm_width = self._distance(
            hand[self.INDEX_MCP],
            hand[self.PINKY_MCP],
        )
        if palm_width <= 1e-6:
            return False

        pinch_ratio = (
            self._distance(
                hand[self.THUMB_TIP],
                hand[self.INDEX_TIP],
            )
            / palm_width
        )
        threshold = (
            self.pinch_release_ratio
            if self._pinch_latched
            else self.pinch_start_ratio
        )
        return pinch_ratio <= threshold

    def _is_scroll_candidate(self, hand):
        return (
            self._is_extended(
                hand,
                self.INDEX_TIP,
                self.INDEX_PIP,
                self.INDEX_MCP,
            )
            and self._is_extended(
                hand,
                self.MIDDLE_TIP,
                self.MIDDLE_PIP,
                self.MIDDLE_MCP,
            )
            and self._is_folded(
                hand,
                self.RING_TIP,
                self.RING_PIP,
            )
            and self._is_folded(
                hand,
                self.PINKY_TIP,
                self.PINKY_PIP,
            )
        )

    def _scroll_position(self, hand):
        # Track the hand at the knuckles instead of the noisier fingertips.
        return (
            hand[self.INDEX_MCP].y
            + hand[self.MIDDLE_MCP].y
        ) / 2.0

    def _reset_scroll_motion(self):
        self._scroll_anchor_y = None
        self._last_scroll_timestamp = None
        self._scroll_remainder = 0.0

    def reset(self):
        """Return to a safe idle state and clear gesture history."""
        self.state = GestureState.IDLE
        self._pinch_frames = 0
        self._pinch_latched = False
        self._scroll_candidate_frames = 0
        self._scroll_release_frames = 0
        self._reset_scroll_motion()

    def update(self, hand, enabled, timestamp=None):
        """Process one frame and return requested mouse actions."""
        current_timestamp = (
            time.monotonic()
            if timestamp is None
            else timestamp
        )

        if not enabled or hand is None:
            self.reset()
            return GestureResult(GestureState.IDLE)

        pinch_candidate = self._is_pinch_candidate(hand)

        if self._pinch_latched:
            if pinch_candidate:
                self.state = GestureState.CLICK
                return GestureResult(self.state)

            self._pinch_latched = False
            self._pinch_frames = 0

        elif pinch_candidate:
            self._pinch_frames += 1
            if self._pinch_frames >= self.pinch_confirmation_frames:
                self._pinch_latched = True
                self._scroll_candidate_frames = 0
                self._scroll_release_frames = 0
                self._reset_scroll_motion()
                self.state = GestureState.CLICK
                return GestureResult(
                    self.state,
                    click_requested=True,
                )
        else:
            self._pinch_frames = 0

        scroll_candidate = self._is_scroll_candidate(hand)

        if self.state == GestureState.SCROLL:
            if scroll_candidate:
                self._scroll_release_frames = 0
            else:
                self._scroll_release_frames += 1
                if (
                    self._scroll_release_frames
                    >= self.scroll_release_frames
                ):
                    self._scroll_candidate_frames = 0
                    self._scroll_release_frames = 0
                    self._reset_scroll_motion()
                    self.state = GestureState.MOVE
                    return GestureResult(self.state)

                # Pause during the short release grace period without using
                # an uncertain hand shape to generate scroll movement.
                self._last_scroll_timestamp = current_timestamp
                return GestureResult(self.state)

            current_y = self._scroll_position(hand)
            if self._scroll_anchor_y is None:
                self._scroll_anchor_y = current_y
                self._last_scroll_timestamp = current_timestamp
                return GestureResult(self.state)

            elapsed = max(
                0.0,
                min(
                    current_timestamp
                    - self._last_scroll_timestamp,
                    0.1,
                ),
            )
            self._last_scroll_timestamp = current_timestamp

            # Image y increases downward. Holding above the anchor produces
            # positive (up) scrolling; holding below produces negative.
            offset = self._scroll_anchor_y - current_y
            if abs(offset) <= self.scroll_dead_zone:
                self._scroll_remainder = 0.0
                return GestureResult(self.state)

            intensity = min(
                1.0,
                (
                    abs(offset) - self.scroll_dead_zone
                ) / (
                    self.scroll_max_offset - self.scroll_dead_zone
                ),
            )
            direction = 1.0 if offset > 0 else -1.0
            self._scroll_remainder += (
                direction
                * intensity
                * self.scroll_max_steps_per_second
                * elapsed
            )

            requested_steps = int(self._scroll_remainder)
            scroll_steps = max(
                -self.max_scroll_steps_per_frame,
                min(
                    self.max_scroll_steps_per_frame,
                    requested_steps,
                ),
            )
            if scroll_steps:
                self._scroll_remainder -= scroll_steps

            return GestureResult(
                self.state,
                scroll_steps=scroll_steps,
            )

        if scroll_candidate:
            self._scroll_candidate_frames += 1
            if (
                self._scroll_candidate_frames
                >= self.scroll_confirmation_frames
            ):
                self.state = GestureState.SCROLL
                self._scroll_release_frames = 0
                self._scroll_anchor_y = self._scroll_position(hand)
                self._last_scroll_timestamp = current_timestamp
                self._scroll_remainder = 0.0
                return GestureResult(self.state)
        else:
            self._scroll_candidate_frames = 0

        self.state = GestureState.MOVE
        return GestureResult(self.state)
