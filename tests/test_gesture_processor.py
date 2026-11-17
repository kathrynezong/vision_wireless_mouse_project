import unittest
from dataclasses import dataclass

from vision.gesture_processor import GestureProcessor, GestureState


@dataclass
class Landmark:
    x: float = 0.5
    y: float = 0.5


def make_hand():
    hand = [Landmark() for _ in range(21)]

    hand[4] = Landmark(0.10, 0.35)
    hand[5] = Landmark(0.30, 0.60)
    hand[6] = Landmark(0.30, 0.48)
    hand[8] = Landmark(0.30, 0.30)
    hand[9] = Landmark(0.45, 0.60)
    hand[10] = Landmark(0.45, 0.50)
    hand[12] = Landmark(0.45, 0.68)
    hand[14] = Landmark(0.55, 0.52)
    hand[16] = Landmark(0.55, 0.68)
    hand[17] = Landmark(0.70, 0.60)
    hand[18] = Landmark(0.65, 0.54)
    hand[20] = Landmark(0.65, 0.70)

    return hand


def make_scroll_hand(y_offset=0.0):
    hand = make_hand()
    hand[5].y = 0.60 + y_offset
    hand[6].y = 0.48 + y_offset
    hand[8].y = 0.30 + y_offset
    hand[9].y = 0.60 + y_offset
    hand[10].y = 0.49 + y_offset
    hand[12].y = 0.31 + y_offset
    return hand


def move_scroll_fingertips(hand, y_offset):
    hand[8].y += y_offset
    hand[12].y += y_offset
    return hand


class GestureProcessorTests(unittest.TestCase):
    def test_disabled_control_stays_idle(self):
        processor = GestureProcessor()

        result = processor.update(make_hand(), enabled=False)

        self.assertEqual(result.state, GestureState.IDLE)
        self.assertFalse(result.click_requested)
        self.assertEqual(result.scroll_steps, 0)

    def test_regular_hand_moves_cursor(self):
        processor = GestureProcessor()

        result = processor.update(make_hand(), enabled=True)

        self.assertEqual(result.state, GestureState.MOVE)

    def test_pinch_requests_only_one_click_until_release(self):
        processor = GestureProcessor(pinch_confirmation_frames=2)
        pinched_hand = make_hand()
        pinched_hand[4] = Landmark(0.29, 0.30)

        first = processor.update(pinched_hand, enabled=True)
        second = processor.update(pinched_hand, enabled=True)
        held = processor.update(pinched_hand, enabled=True)

        self.assertFalse(first.click_requested)
        self.assertTrue(second.click_requested)
        self.assertEqual(second.state, GestureState.CLICK)
        self.assertFalse(held.click_requested)

        processor.update(make_hand(), enabled=True)
        processor.update(pinched_hand, enabled=True)
        next_pinch = processor.update(pinched_hand, enabled=True)
        self.assertTrue(next_pinch.click_requested)

    def test_pinch_hysteresis_ignores_small_release_motion(self):
        processor = GestureProcessor(pinch_confirmation_frames=1)
        hand = make_hand()
        hand[4] = Landmark(0.29, 0.30)
        processor.update(hand, enabled=True)

        hand[4] = Landmark(0.43, 0.30)
        result = processor.update(hand, enabled=True)

        self.assertEqual(result.state, GestureState.CLICK)
        self.assertFalse(result.click_requested)

    def test_scroll_requires_confirmation_and_pauses_move(self):
        processor = GestureProcessor(scroll_confirmation_frames=3)
        hand = make_scroll_hand()

        first = processor.update(hand, enabled=True)
        second = processor.update(hand, enabled=True)
        third = processor.update(hand, enabled=True)

        self.assertEqual(first.state, GestureState.MOVE)
        self.assertEqual(second.state, GestureState.MOVE)
        self.assertEqual(third.state, GestureState.SCROLL)

    def test_holding_above_anchor_continuously_scrolls_up(self):
        processor = GestureProcessor(
            scroll_confirmation_frames=1,
            scroll_dead_zone=0.02,
            scroll_max_offset=0.12,
            scroll_max_steps_per_second=20.0,
        )
        processor.update(
            make_scroll_hand(),
            enabled=True,
            timestamp=0.0,
        )

        first = processor.update(
            make_scroll_hand(y_offset=-0.12),
            enabled=True,
            timestamp=0.1,
        )
        second = processor.update(
            make_scroll_hand(y_offset=-0.12),
            enabled=True,
            timestamp=0.2,
        )

        self.assertEqual(first.state, GestureState.SCROLL)
        self.assertEqual(first.scroll_steps, 1)
        self.assertEqual(second.scroll_steps, 1)

    def test_holding_below_anchor_continuously_scrolls_down(self):
        processor = GestureProcessor(
            scroll_confirmation_frames=1,
            scroll_dead_zone=0.02,
            scroll_max_offset=0.12,
            scroll_max_steps_per_second=20.0,
        )
        processor.update(
            make_scroll_hand(),
            enabled=True,
            timestamp=0.0,
        )

        result = processor.update(
            make_scroll_hand(y_offset=0.12),
            enabled=True,
            timestamp=0.1,
        )

        self.assertEqual(result.scroll_steps, -1)

    def test_anchor_dead_zone_stops_scrolling(self):
        processor = GestureProcessor(
            scroll_confirmation_frames=1,
            scroll_dead_zone=0.03,
            scroll_max_steps_per_second=20.0,
        )
        processor.update(
            make_scroll_hand(),
            enabled=True,
            timestamp=0.0,
        )

        result = processor.update(
            make_scroll_hand(y_offset=-0.02),
            enabled=True,
            timestamp=1.0,
        )

        self.assertEqual(result.scroll_steps, 0)

    def test_fingertip_motion_does_not_scroll_without_hand_motion(self):
        processor = GestureProcessor(
            scroll_confirmation_frames=1,
        )
        processor.update(
            make_scroll_hand(),
            enabled=True,
            timestamp=0.0,
        )

        result = processor.update(
            move_scroll_fingertips(make_scroll_hand(), -0.06),
            enabled=True,
            timestamp=0.1,
        )

        self.assertEqual(result.state, GestureState.SCROLL)
        self.assertEqual(result.scroll_steps, 0)

    def test_scroll_release_grace_period_does_not_emit_motion(self):
        processor = GestureProcessor(
            scroll_confirmation_frames=1,
            scroll_release_frames=2,
        )
        processor.update(make_scroll_hand(), enabled=True)

        grace = processor.update(make_hand(), enabled=True)
        released = processor.update(make_hand(), enabled=True)

        self.assertEqual(grace.state, GestureState.SCROLL)
        self.assertEqual(grace.scroll_steps, 0)
        self.assertEqual(released.state, GestureState.MOVE)

    def test_tracking_loss_resets_pinch_latch(self):
        processor = GestureProcessor(pinch_confirmation_frames=1)
        hand = make_hand()
        hand[4] = Landmark(0.29, 0.30)
        self.assertTrue(
            processor.update(hand, enabled=True).click_requested
        )

        lost = processor.update(None, enabled=True)
        new_hand = processor.update(hand, enabled=True)

        self.assertEqual(lost.state, GestureState.IDLE)
        self.assertTrue(new_hand.click_requested)


if __name__ == "__main__":
    unittest.main()
