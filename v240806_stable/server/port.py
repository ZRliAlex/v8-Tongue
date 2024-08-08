import socket


def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) != 0


def find_available_port(start=8000, end=19000):
    for port in range(start, end):
        if check_port(port):
            return port
    return None


if __name__ == "__main__":
    port = find_available_port()
    if port:
        print(f"Available port found: {port}")
    else:
        print("No available port found in the specified range.")
