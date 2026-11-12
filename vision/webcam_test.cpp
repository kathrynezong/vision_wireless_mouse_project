#include <opencv2/opencv.hpp>

#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

constexpr int DefaultCameraIndex = 0;
constexpr const char* WindowName = "Webcam Test";

int parseCameraIndex(int argc, char* argv[]) {
    if (argc > 2) {
        throw std::invalid_argument(
            "Usage: webcam_test [camera_index]"
        );
    }

    if (argc == 2) {
        const int cameraIndex = std::stoi(argv[1]);
        if (cameraIndex < 0) {
            throw std::invalid_argument(
                "Camera index must not be negative"
            );
        }
        return cameraIndex;
    }

    return DefaultCameraIndex;
}

}  // namespace

/**
 * Opens a webcam and displays frames until the user presses q or Escape.
 *
 * Input:
 *   Optional argv[1]: non-negative camera index. Defaults to 0.
 *
 * Output:
 *   Returns 0 after a normal exit, or 1 if the camera cannot be opened,
 *   a frame cannot be read, or the camera index is invalid.
 */
int main(int argc, char* argv[]) {
    try {
        const int cameraIndex = parseCameraIndex(argc, argv);
        cv::VideoCapture camera(cameraIndex);

        if (!camera.isOpened()) {
            std::cerr << "Could not open camera " << cameraIndex << "\n";
            return 1;
        }

        cv::Mat frame;
        cv::namedWindow(WindowName, cv::WINDOW_AUTOSIZE);

        while (true) {
            if (!camera.read(frame) || frame.empty()) {
                std::cerr << "Could not read a frame from the camera\n";
                camera.release();
                cv::destroyAllWindows();
                return 1;
            }

            cv::imshow(WindowName, frame);

            // waitKey keeps the window responsive and checks for a quit key.
            const int key = cv::waitKey(1);
            if (key == 'q' || key == 'Q' || key == 27) {
                break;
            }
        }

        camera.release();
        cv::destroyAllWindows();
    } catch (const std::exception& error) {
        std::cerr << "Webcam test error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
