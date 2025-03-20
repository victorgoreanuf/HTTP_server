import socket 
import re # noqa: F401


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_adress = server_socket.accept()
        # recv return b"data here" using decode to make the string from bites
        request = client_socket.recv(1024).decode()
        request_line = request.split("\n")[0]
        # Ex GET / HTTP/1.1
        request_line_adress = re.search(r"/[\S]*", request_line)
        request_line_adress = request_line_adress.group()
        #Ex / or /index.html
        if request_line_adress:
            if request_line_adress == "/":
                client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
            else: 
                client_socket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        client_socket.close()


if __name__ == "__main__":
    main()