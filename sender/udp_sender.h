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
    /**
     * Creates a reusable IPv4 UDP sender for the specified destination.
     *
     * Inputs:
     *   ip: Destination IPv4 address in dotted-decimal text form.
     *   port: Destination UDP port, from 1 through 65535.
     *
     * Throws:
     *   std::invalid_argument for an invalid port or IP address.
     *   std::runtime_error if socket/network initialization fails.
     */
    UdpSender(const std::string& ip, int port);

    /**
     * Closes the socket and releases platform-specific networking resources.
     *
     * Inputs: None.
     * Output: None.
     */
    ~UdpSender();

    // Socket ownership is unique, so copying or assigning a sender is unsafe.
    UdpSender(const UdpSender&) = delete;
    UdpSender& operator=(const UdpSender&) = delete;

    /**
     * Sends one movement packet using the already-open UDP socket.
     *
     * Inputs:
     *   dx: Horizontal relative movement.
     *   dy: Vertical relative movement.
     *
     * The transmitted payload is the text format "dx,dy".
     *
     * Throws:
     *   std::runtime_error if the packet cannot be sent completely.
     */
    void sendMovement(int dx, int dy) const;

private:
    SocketHandle socketHandle_;
    sockaddr_in destination_;
};