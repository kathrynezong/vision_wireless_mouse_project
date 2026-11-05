
#include "udp_sender.h"

#include <chrono>
#include <iostream>
#include <string>
#include <exception>
#include <thread>

/**
 * Parses sender settings and transmits a finite sequence of movement packets.
 *
 * Inputs:
 *   argv[1]: Destination IPv4 address.
 *   argv[2]: Destination UDP port, from 1 through 65535.
 *   argv[3]: Horizontal movement (dx).
 *   argv[4]: Vertical movement (dy).
 *   argv[5]: Optional packet count, at least 1.
 *   argv[6]: Optional interval between packets in milliseconds, at least 0.
 *
 * With no optional values, the program sends 20 packets 50 milliseconds apart.
 *
 * Returns:
 *   0 when all packets are sent successfully; 1 for invalid input or a
 *   sender error.
 */
int main(int argc, char* argv[]) {
    if (argc != 5 && argc != 7) {
        std::cerr << "Usage: " << argv[0]
                  << " <IP> <port> <dx> <dy> [count] [interval_ms]\n";
        return 1;
    }

    std::string ip = argv[1];
    int port;
    int dx;
    int dy;
    int count = 20;
    int intervalMs = 50;

    try {
        port = std::stoi(argv[2]);
        dx = std::stoi(argv[3]);
        dy = std::stoi(argv[4]);
        if (argc == 7) {
            count = std::stoi(argv[5]);
            intervalMs = std::stoi(argv[6]);
        }
    } catch (const std::exception&) {
        std::cerr << "Invalid numeric argument\n";
        return 1;
    }

    if (port < 1 || port > 65535) {
        std::cerr << "Port must be between 1 and 65535\n";
        return 1;
    }

    if (count < 1) {
        std::cerr << "Count must be at least 1\n";
        return 1;
    }

    if (intervalMs < 0) {
        std::cerr << "Interval must not be negative\n";
        return 1;
    }

    try {
        UdpSender sender(ip, port);

        for (int packet = 0; packet < count; ++packet) {
            sender.sendMovement(dx, dy);
            std::cout << "Sent packet " << packet + 1 << "/" << count
                      << ": " << dx << "," << dy << "\n";

            if (packet + 1 < count) {
                std::this_thread::sleep_for(
                    std::chrono::milliseconds(intervalMs)
                );
            }
        }
    } catch (const std::exception& error) {
        std::cerr << "Sender error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
