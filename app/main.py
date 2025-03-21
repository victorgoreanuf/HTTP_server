import socket 
import threading

def handle_client(client_socket):
    # recv return b"data here" using decode to make the string from bites
    client_msg = client_socket.recv(1024).decode().split()
    print(client_socket)
    if client_msg[1] == '/':
        response = "HTTP/1.1 200 OK\r\n\r\n".encode()
    elif client_msg[1].startswith("/echo/"):
        value = client_msg[1].split("/echo/")[1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode()
    elif client_msg[1] == "/user-agent":
        index = client_msg.index("User-Agent:") + 1
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(client_msg[index])}\r\n\r\n{client_msg[index]}".encode()
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
    client_socket.sendall(response)
    client_socket.close()

def main():
    # creating the server socket
    port = 4221
    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    # server_socket.listen()
    try:
        while True:
            client_socket, client_adress = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")  
    finally:
        server_socket.close()
        print("Server has been shut down.")


if __name__ == "__main__":
    main()