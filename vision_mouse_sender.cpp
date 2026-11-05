
#include <iostream>
#include <string>
#include <cstdio>
#include <exception>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

#ifdef _WIN32
using SocketHandle = SOCKET;
constexpr SocketHandle InvalidSocket = INVALID_SOCKET;
#else
using SocketHandle = int;
constexpr SocketHandle InvalidSocket = -1;
#endif

void closeSocket(SocketHandle socketHandle) {
#ifdef _WIN32
    closesocket(socketHandle);
#else
    close(socketHandle);
#endif
}

int main(int argc, char* argv[]) {

    // Validate command-line arguments
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
    } catch (const std::exception& e) {
        std::cerr << "Invalid numeric argument\n";
        return 1;
    }

    if (port < 1 || port > 65535) {
        std::cerr << "Port must be between 1 and 65535\n";
        return 1;
    }

#ifdef _WIN32
    WSADATA wsaData{};
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed\n";
        return 1;
    }
#endif

    // Create UDP socket
    SocketHandle sock = socket(AF_INET, SOCK_DGRAM, 0);

    if (sock == InvalidSocket) {
#ifdef _WIN32
        std::cerr << "socket failed: " << WSAGetLastError() << "\n";
        WSACleanup();
#else
        perror("socket");
#endif
        return 1;
    }

    // Configure destination
    sockaddr_in destination{};
    destination.sin_family = AF_INET;
    destination.sin_port = htons(port);

    if (inet_pton(AF_INET, ip.c_str(),
                  &destination.sin_addr) != 1) {
        std::cerr << "Invalid IP address\n";
        closeSocket(sock);
#ifdef _WIN32
        WSACleanup();
#endif
        return 1;
    }

    // Construct mouse movement message
    std::string message =
        std::to_string(dx) + "," + std::to_string(dy);

    // Send UDP packet
    int sent = sendto(
        sock,
        message.c_str(),
        static_cast<int>(message.size()),
        0,
        reinterpret_cast<sockaddr*>(&destination),
        static_cast<int>(sizeof(destination))
    );

    if (sent == -1) {
#ifdef _WIN32
        std::cerr << "sendto failed: " << WSAGetLastError() << "\n";
        closeSocket(sock);
        WSACleanup();
#else
        perror("sendto");
#endif
        return 1;
    }

    if (static_cast<size_t>(sent) != message.size()) {
        std::cerr << "Incomplete UDP send\n";
        closeSocket(sock);
#ifdef _WIN32
        WSACleanup();
#endif
        return 1;
    }

    std::cout << "Sent: " << message << "\n";

    // Clean up
    closeSocket(sock);
#ifdef _WIN32
    WSACleanup();
#endif

    return 0;
}
