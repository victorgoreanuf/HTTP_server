import socket
import threading
import sys
import mimetypes
import gzip
from pathlib import Path

files_hash = {}

def handle_client(client_socket):
    try:
        client_msg = client_socket.recv(1024).decode(errors='ignore').split("\r\n")
        if not client_msg:
            return
        
        print(client_msg)
        method, path = client_msg[0].split()[0], client_msg[0].split()[1]

        # responde constructor
        response = ""
        http_status_code = ""
        headers = ""
        body = ""
        
        if path == '/':
            http_status_code = "HTTP/1.1 200 OK\r\n"
            headers = "\r\n"
            body = ""
            # response = "HTTP/1.1 200 OK\r\n\r\n"
        
        elif path.startswith("/echo/"):
            value = path.split("/echo/")[1]
            http_status_code = "HTTP/1.1 200 OK\r\n"
            headers = f"Content-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n"
            body = value
            # response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
        
        elif path == "/user-agent":
            try:
                user_agent  = next((line.split("User-Agent: ")[1] for line in client_msg if line.startswith("User-Agent:")), None)
                http_status_code = "HTTP/1.1 200 OK\r\n"
                headers = f"Content-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n"
                body = user_agent
                # response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
            except ValueError:
                http_status_code = "HTTP/1.1 400 Bad Request\r\n"
                headers = "\r\n"
                body = ""
                # response = "HTTP/1.1 400 Bad Request\r\n\r\n"
        
        elif path.startswith("/files/"):
            file_name = path.split("/files/")[1]
            if method == "GET":
                if file_name in files_hash:
                    content = files_hash[file_name]
                    mime_type, _ = mimetypes.guess_type(file_name)
                    mime_type = mime_type or "application/octet-stream"
                    http_status_code = "HTTP/1.1 200 OK\r\n"
                    headers = f"Content-Type: {mime_type}\r\nContent-Length: {len(content)}\r\n\r\n"
                    body = content
                    # response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(content)}\r\n\r\n{content}"
            
            elif method == "POST":
                try:
                    index_path = sys.argv.index("--directory") + 1
                    directory = sys.argv[index_path]
                    file_path = Path(directory) / file_name
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(client_msg[-1])
                    
                    http_status_code = "HTTP/1.1 201 Created\r\n"
                    headers = "\r\n"
                    body = ""
                    # response = "HTTP/1.1 201 Created\r\n\r\n"
                    files_hash[file_name] = client_msg[-1]  # Update in-memory store
                except (IndexError, OSError):
                    http_status_code = "HTTP/1.1 500 Internal Server Error\r\n"
                    headers = "\r\n"
                    body = ""
                    # response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
        
        if not http_status_code:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        else:
            accept_encoding = next((line for line in client_msg if line.startswith("Accept-Encoding:")), None)
            if accept_encoding:
                accept_encoding = accept_encoding.split("Accept-Encoding: ")[1]
                accept_encoding = accept_encoding.split(", ")
                if "gzip" in accept_encoding:
                    body = body.encode()
                    body = gzip.compress(body)

                    headers = headers[:-2]
                    headers = headers.split("\r\n")
                    headers.insert(1, "Content-Encoding: gzip")
                    #need to edit the "Content-Length" header
                    headers[-2] = f"Content-Length: {len(body)}"
                    headers = "\r\n".join(headers) + "\r\n"
                    response = (http_status_code + headers).encode()  # Convert headers to bytes
                    client_socket.sendall(response + body)
                    return
        response = http_status_code + headers + body
        client_socket.sendall(response.encode())
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def handle_directory(path):
    global files_hash
    try:
        for child in Path(path).iterdir():
            if child.is_file():
                files_hash[child.name] = child.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Error reading directory: {e}")

def main():
    if "--directory" in sys.argv:
        try:
            index_path = sys.argv.index("--directory") + 1
            handle_directory(sys.argv[index_path])
        except IndexError:
            print("Error: Missing directory path argument.")
            sys.exit(1)
    
    port = 4221
    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    
    print(f"Server running on port {port}...")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server_socket.close()
        print("Server has been shut down.")

if __name__ == "__main__":
    main()
