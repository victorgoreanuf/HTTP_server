Here's the updated README with the new `Accept-Encoding` functionality explained:

---

# Simple HTTP Server

This is a simple multithreaded HTTP server implemented in Python. It supports basic HTTP functionalities such as:

- Serving static files from a directory
- Echoing text from URL paths
- Returning the user-agent of incoming requests
- Handling both `GET` and `POST` requests for files
- **Supporting `Accept-Encoding` for gzip compression**

## Features

### 1. Serve Static Files

- When launched with `--directory <path>`, the server will read files from the specified directory and store them in memory.
- Clients can retrieve files via `GET /files/<filename>`.
- Clients can upload new files via `POST /files/<filename>`.

### 2. Echo Functionality

- Accessing `/echo/<message>` will return `<message>` in the response body.

### 3. User-Agent Retrieval

- Sending a request to `/user-agent` will return the `User-Agent` header from the request.

### 4. Root Path Handling

- Requests to `/` will receive a simple `200 OK` response.

### 5. Multithreading

- The server handles multiple client requests concurrently using threads.

### 6. **Gzip Compression with `Accept-Encoding`**

- The server now supports the `Accept-Encoding` header.
- Clients can send requests with `Accept-Encoding: <encoding-types>` where `<encoding-types>` can be a **comma-separated list** (e.g., `"gzip, deflate"`).
- The server will check for supported encodings and **currently supports only `gzip`**.
- If `gzip` is found in the list, the response body will be compressed, and the header `Content-Encoding: gzip` will be added.

## Usage

### Running the Server

```sh
python3 server.py --directory /path/to/your/files
```

- Replace `/path/to/your/files` with the actual directory you want to serve.
- The server will start listening on `localhost:4221`.

### Example Requests

#### Get a File

```sh
curl -X GET http://localhost:4221/files/example.txt
```

#### Upload a File

```sh
curl -X POST --data "Hello, World!" http://localhost:4221/files/newfile.txt
```

#### Echo a Message

```sh
curl -X GET http://localhost:4221/echo/hello
```

Response:

```sh
hello
```

#### Get User-Agent

```sh
curl -X GET -H "User-Agent: MyBrowser" http://localhost:4221/user-agent
```

Response:

```sh
MyBrowser
```

#### Request with `Accept-Encoding: gzip`

```sh
curl -v -H "Accept-Encoding: gzip" http://localhost:4221/echo/hello
```

Response Headers:

```sh
< HTTP/1.1 200 OK
< Content-Type: text/plain
< Content-Encoding: gzip
< Content-Length: 23
```

The body will be compressed in gzip format.

## Error Handling

- `404 Not Found`: If the requested resource does not exist.
- `400 Bad Request`: If the request is malformed.
- `500 Internal Server Error`: If an unexpected error occurs.

## Stopping the Server

- Press `CTRL + C` to stop the server safely.

## Notes

- The server supports only local requests on `localhost:4221`.
- Large file handling should be optimized for better memory usage.
- Consider implementing HTTPS for security in production environments.
