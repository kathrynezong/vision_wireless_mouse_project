#include "udp_sender.h"

#include <stdexcept>
#include <string>

#ifdef _WIN32
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#include <cerrno>
#include <cstring>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace {

// Input: an open or invalid platform-specific socket handle.
// Output: none; closes the socket when the handle is valid.
// Uses the close function required by the current operating system.
void closeSocket(SocketHandle socketHandle) {
#ifdef _WIN32
    closesocket(socketHandle);
#else
    close(socketHandle);
#endif
}

#ifdef _WIN32
// Input: none.
// Output: none; releases the Winsock library.
// This helper is compiled only for Windows.
void cleanupWindowsNetworking() {
    WSACleanup();
}
#endif

}  // namespace

UdpSender::UdpSender(const std::string& ip, int port)
    : socketHandle_(InvalidSocket), destination_{} {
    // Reject invalid ports before initializing platform networking.
    if (port < 1 || port > 65535) {
        throw std::invalid_argument("Port must be between 1 and 65535");
    }

#ifdef _WIN32
    // Winsock must be initialized before creating a Windows socket.
    WSADATA wsaData{};
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        throw std::runtime_error("WSAStartup failed");
    }
#endif

    // Create one IPv4 UDP socket; sendMovement() reuses it for every packet.
    socketHandle_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socketHandle_ == InvalidSocket) {
#ifdef _WIN32
        cleanupWindowsNetworking();
#endif
        throw std::runtime_error("Could not create UDP socket");
    }

    destination_.sin_family = AF_INET;
    // Network APIs expect the port in network byte order.
    destination_.sin_port = htons(static_cast<unsigned short>(port));

    // Convert the human-readable IP address into the binary socket format.
    if (inet_pton(AF_INET, ip.c_str(), &destination_.sin_addr) != 1) {
        closeSocket(socketHandle_);
#ifdef _WIN32
        cleanupWindowsNetworking();
#endif
        throw std::invalid_argument("Invalid IP address");
    }
}

UdpSender::~UdpSender() {
    if (socketHandle_ != InvalidSocket) {
        closeSocket(socketHandle_);
    }

#ifdef _WIN32
    cleanupWindowsNetworking();
#endif
}

void UdpSender::sendMovement(int dx, int dy) const {
    // Match the receiver's required text protocol: "dx,dy".
    const std::string message =
        std::to_string(dx) + "," + std::to_string(dy);

    // Send the packet through the socket created by the constructor.
    const int sent = sendto(
        socketHandle_,
        message.c_str(),
        static_cast<int>(message.size()),
        0,
        reinterpret_cast<const sockaddr*>(&destination_),
        static_cast<int>(sizeof(destination_))
    );

    if (sent == -1) {
        throw std::runtime_error("Could not send UDP packet");
    }

    if (static_cast<std::size_t>(sent) != message.size()) {
        throw std::runtime_error("Incomplete UDP send");
    }
}