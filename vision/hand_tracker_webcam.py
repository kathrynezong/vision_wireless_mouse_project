
from pathlib import Path
import time

import cv2
import mediapipe as mp
import pyautogui

from gesture_processor import GestureProcessor, GestureState


# ==========================================
# Configuration
# ==========================================

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "hand_landmarker.task"
)

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Mouse settings
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

MOUSE_ENABLED = False  # Press M to enable
SMOOTHING = 0.25        # 0 < value <= 1
MARGIN = 10             # Keep cursor away from screen edges

# Keep PyAutoGUI's emergency corner fail-safe enabled
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

previous_mouse_x = None
previous_mouse_y = None
gesture_processor = GestureProcessor()


# ==========================================
# MediaPipe Configuration
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=str(MODEL_PATH)
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=1
)


# ==========================================
# Hand Landmark Connections
# ==========================================

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


# ==========================================
# Helper Functions
# ==========================================

def move_mouse(tip_x, tip_y):
    """
    Convert normalized fingertip coordinates
    into smoothed screen coordinates.
    """
    global previous_mouse_x, previous_mouse_y

    # Clamp normalized coordinates between 0 and 1
    tip_x = max(0.0, min(1.0, tip_x))
    tip_y = max(0.0, min(1.0, tip_y))

    # Map fingertip coordinates to screen
    target_x = MARGIN + tip_x * (
        SCREEN_WIDTH - 1 - 2 * MARGIN
    )
    target_y = MARGIN + tip_y * (
        SCREEN_HEIGHT - 1 - 2 * MARGIN
    )

    # Initialize smoothing state
    if previous_mouse_x is None:
        previous_mouse_x = target_x
        previous_mouse_y = target_y

    # Exponential smoothing
    mouse_x = (
        previous_mouse_x
        + SMOOTHING * (target_x - previous_mouse_x)
    )
    mouse_y = (
        previous_mouse_y
        + SMOOTHING * (target_y - previous_mouse_y)
    )

    # Move cursor
    pyautogui.moveTo(
        int(mouse_x),
        int(mouse_y),
        duration=0
    )

    previous_mouse_x = mouse_x
    previous_mouse_y = mouse_y


def draw_hand(frame, hand):
    """
    Draw hand skeleton and landmarks.
    """
    height, width = frame.shape[:2]

    # Draw hand connections
    for a, b in CONNECTIONS:
        p1 = (
            int(hand[a].x * width),
            int(hand[a].y * height)
        )
        p2 = (
            int(hand[b].x * width),
            int(hand[b].y * height)
        )

        cv2.line(frame, p1, p2, (0, 255, 0), 2)

    # Draw all 21 landmarks
    for point in hand:
        position = (
            int(point.x * width),
            int(point.y * height)
        )

        cv2.circle(
            frame,
            position,
            4,
            (0, 0, 255),
            -1
        )

    # Highlight index fingertip (landmark 8)
    tip = hand[8]

    x = int(tip.x * width)
    y = int(tip.y * height)

    cv2.circle(
        frame,
        (x, y),
        9,
        (255, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        f"Index: ({x}, {y})",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    return tip


# ==========================================
# Main Application
# ==========================================

def main():
    global MOUSE_ENABLED
    global previous_mouse_x, previous_mouse_y

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"MediaPipe model not found: {MODEL_PATH}"
        )

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        camera.release()
        raise RuntimeError("Could not open webcam")

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    start_time = time.monotonic()
    last_timestamp = -1
    previous_frame_time = time.monotonic()

    print("MediaPipe Hand Tracking Started")
    print("Press M to enable/disable mouse control")
    print("Press Q to quit")
    print("Mouse control starts OFF")
    print("Gestures: index to move, pinch to click, two fingers to scroll")

    try:
        with HandLandmarker.create_from_options(
            options
        ) as landmarker:

            while True:
                success, frame = camera.read()

                if not success:
                    print("Failed to capture frame")
                    break

                # Mirror preview and control coordinates
                frame = cv2.flip(frame, 1)

                # Convert BGR to RGB
                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb
                )

                # MediaPipe requires increasing timestamps
                timestamp_ms = max(
                    int(
                        (time.monotonic() - start_time)
                        * 1000
                    ),
                    last_timestamp + 1
                )
                last_timestamp = timestamp_ms

                # Detect hand
                result = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms
                )

                if result.hand_landmarks:
                    hand = result.hand_landmarks[0]

                    # Draw hand and get index fingertip
                    tip = draw_hand(frame, hand)

                    gesture = gesture_processor.update(
                        hand,
                        MOUSE_ENABLED,
                    )

                    # Gesture states are exclusive so scrolling and clicking
                    # cannot also move the cursor in the same frame.
                    try:
                        if gesture.state == GestureState.MOVE:
                            move_mouse(tip.x, tip.y)

                        elif gesture.click_requested:
                            pyautogui.click()

                        elif (
                            gesture.state == GestureState.SCROLL
                            and gesture.scroll_steps
                        ):
                            pyautogui.scroll(gesture.scroll_steps)

                    except pyautogui.FailSafeException:
                        MOUSE_ENABLED = False
                        gesture_processor.reset()
                        previous_mouse_x = None
                        previous_mouse_y = None
                        print(
                            "Mouse disabled: "
                            "PyAutoGUI fail-safe triggered"
                        )

                else:
                    # Reset smoothing when tracking is lost
                    gesture = gesture_processor.update(
                        None,
                        MOUSE_ENABLED,
                    )
                    previous_mouse_x = None
                    previous_mouse_y = None

                    cv2.putText(
                        frame,
                        "No hand detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

                gesture_text = f"Gesture: {gesture.state.value}"
                cv2.putText(
                    frame,
                    gesture_text,
                    (10, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )

                # ==================================
                # FPS calculation
                # ==================================

                current_time = time.monotonic()
                elapsed = current_time - previous_frame_time

                fps = 1.0 / elapsed if elapsed > 0 else 0.0
                previous_frame_time = current_time

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                # ==================================
                # Mouse status
                # ==================================

                status = (
                    "Mouse: ON"
                    if MOUSE_ENABLED
                    else "Mouse: OFF"
                )

                status_color = (
                    (0, 255, 0)
                    if MOUSE_ENABLED
                    else (0, 0, 255)
                )

                cv2.putText(
                    frame,
                    status,
                    (10, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    status_color,
                    2
                )

                cv2.putText(
                    frame,
                    "M: Toggle Mouse | Q: Quit",
                    (10, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    1
                )

                cv2.imshow(
                    "MediaPipe Hand Tracking",
                    frame
                )

                # ==================================
                # Keyboard controls
                # ==================================

                key = cv2.waitKey(1) & 0xFF

                if key == ord("m"):
                    MOUSE_ENABLED = not MOUSE_ENABLED

                    gesture_processor.reset()
                    previous_mouse_x = None
                    previous_mouse_y = None

                    print(
                        "Mouse control:",
                        "ON" if MOUSE_ENABLED else "OFF"
                    )

                elif key == ord("q"):
                    print("Exiting...")
                    break

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Camera released. Program stopped.")


if __name__ == "__main__":
    main()
