
from pathlib import Path
import time

import cv2
import mediapipe as mp

# Model location relative to this script
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "hand_landmarker.task"
)

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=RunningMode.VIDEO,
    num_hands=1
)

# Hand skeleton connections
CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Could not open webcam")

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

start = time.monotonic()
last_timestamp = -1

try:
    with HandLandmarker.create_from_options(options) as landmarker:
        while True:
            success, frame = camera.read()
            if not success:
                print("Failed to capture frame")
                break

            height, width = frame.shape[:2]

            # Convert OpenCV BGR image to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            # Ensure monotonically increasing timestamps
            timestamp_ms = max(
                int((time.monotonic() - start) * 1000),
                last_timestamp + 1
            )
            last_timestamp = timestamp_ms

            result = landmarker.detect_for_video(
                mp_image, timestamp_ms
            )

            if result.hand_landmarks:
                hand = result.hand_landmarks[0]

                # Draw connections
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

                # Draw landmarks
                for point in hand:
                    position = (
                        int(point.x * width),
                        int(point.y * height)
                    )
                    cv2.circle(frame, position, 4, (0, 0, 255), -1)

                # Index fingertip = landmark 8
                tip = hand[8]
                x = int(tip.x * width)
                y = int(tip.y * height)

                cv2.circle(frame, (x, y), 9, (255, 0, 0), -1)
                cv2.putText(
                    frame,
                    f"Index: ({x}, {y})",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                print(f"TRACKED,{tip.x:.4f},{tip.y:.4f}")

            else:
                cv2.putText(
                    frame, "No hand detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2
                )

            cv2.imshow("MediaPipe Hand Tracking", frame)

            # Press q to stop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    camera.release()
    cv2.destroyAllWindows()
