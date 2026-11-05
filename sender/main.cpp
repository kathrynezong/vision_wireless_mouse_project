
#include "udp_sender.h"

#include <iostream>
#include <string>
#include <exception>

int main(int argc, char* argv[]) {
    if (argc != 5) {
        std::cerr << "Usage: " << argv[0]
                  << " <IP> <port> <dx> <dy>\n";
        return 1;
    }

    std::string ip = argv[1];
    int port, dx, dy;

    try {
        port = std::stoi(argv[2]);
        dx = std::stoi(argv[3]);
        dy = std::stoi(argv[4]);
    } catch (const std::exception&) {
        std::cerr << "Invalid numeric argument\n";
        return 1;
    }

    if (port < 1 || port > 65535) {
        std::cerr << "Port must be between 1 and 65535\n";
        return 1;
    }

    try {
        UdpSender sender(ip, port);
        sender.sendMovement(dx, dy);
        std::cout << "Sent: " << dx << "," << dy << "\n";
    } catch (const std::exception& error) {
        std::cerr << "Sender error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
