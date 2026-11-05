#pragma once

#include <string>

#ifdef _WIN32
#include <winsock2.h>
using SocketHandle = SOCKET;
constexpr SocketHandle InvalidSocket = INVALID_SOCKET;
#else
#include <netinet/in.h>
using SocketHandle = int;
constexpr SocketHandle InvalidSocket = -1;
#endif

class UdpSender {
public:
    UdpSender(const std::string& ip, int port);
    ~UdpSender();

    UdpSender(const UdpSender&) = delete;
    UdpSender& operator=(const UdpSender&) = delete;

    void sendMovement(int dx, int dy) const;

private:
    SocketHandle socketHandle_;
    sockaddr_in destination_;
};