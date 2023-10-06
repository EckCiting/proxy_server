import socks

def send_data():
    target_host = "127.0.0.1"
    target_port = 1082

    proxy_host = "127.0.0.1"
    proxy_port = 1080

    client_socket = socks.socksocket()
    client_socket.set_proxy(socks.SOCKS5, proxy_host, proxy_port)

    try:
        print("Connecting to the target host and port...")
        client_socket.connect((target_host, target_port))

        print("Connection successful, sending data...")
        data = b'1'
        client_socket.send(data)
        print("Data sent successfully")

    except ConnectionRefusedError:
        print("Unable to connect to the target host and port")

    finally:
        client_socket.close()

if __name__ == '__main__':
    send_data()
