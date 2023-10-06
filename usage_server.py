import socket


def start_server():
    host = "127.0.0.1"
    port = 1082

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server started, listening on address: {host}, port: {port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Received connection from {client_address[0]}:{client_address[1]}")

            data = client_socket.recv(1024)
            if data:
                print(f"Received data: {data.decode()}")

            client_socket.close()

    except OSError as e:
        print(f"Server failed to start: {e}")

    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()
