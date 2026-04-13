import socket

# HTML Content (Valid Response)
HTML_PAGE = """\
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: {length}

<!DOCTYPE html>
<html>
<head>
    <title>Sample Webpage</title>
</head>
<body>
    <h1>Welcome to the Computwer Network Student HTTP Test</h1>
    <p>This is a simple webpage served from the instructor's server.</p>
    <h2>WoW, You can really dance!!!</h2>
    <img src="wow.jpg" alt="Sample Image" width="300">
</body>
</html>
""".replace("\n", "\r\n")  # Ensure proper HTTP newlines

# Error 404 Response
ERROR_PAGE = """\
HTTP/1.1 404 Not Found
Content-Type: text/html
Content-Length: {length}

<!DOCTYPE html>
<html>
<head>
    <title>404 Not Found</title>
</head>
<body>
    <h1>404 Error</h1>
    <p>The requested page was not found on the server.</p>
</body>
</html>
""".replace("\n", "\r\n")

# Image File Path
IMAGE_PATH = "wow.jpg"

def load_image():
    """Load the image as binary data."""
    with open(IMAGE_PATH, "rb") as f:
        return f.read()

def handle_client(conn, addr):
    """Handles incoming HTTP requests."""
    request = conn.recv(1024).decode(errors="ignore")
    print(f"\n--- Received Request from {addr} ---\n{request}")

    # Extract Method and Requested Path
    request_lines = request.split("\r\n")
    if len(request_lines) > 0 and request_lines[0].startswith(("GET", "POST")):
        method, requested_file, _ = request_lines[0].split(" ")
    else:
        requested_file = "/error"
        method = "UNKNOWN"

    # Serve HTML Page
    if method == "GET" and (requested_file == "/index.html" or requested_file == "/"):
        body = HTML_PAGE.format(length=len(HTML_PAGE)).encode()
        response = body
    elif method == "GET" and requested_file == "/wow.jpg":
        image_data = load_image()
        response = b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(image_data)).encode() + b"\r\n\r\n" + image_data
    elif method == "POST" and requested_file == "/post":
        # Extract POST Data
        post_data = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
        print(f"\n--- Received POST Data ---\n{post_data}")
        response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPOST Received!"
    else:
        error_response = ERROR_PAGE.format(length=len(ERROR_PAGE)).encode()
        response = error_response

    # Send Response
    conn.sendall(response)
    conn.close()
    print(f"Response sent to {addr}\n")

def start_server():
    """Starts the HTTP server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen(5)

    print("Server running on port 8080...")
    print("Waiting for connections...")

    while True:
        conn, addr = server_socket.accept()
        handle_client(conn, addr)

# Run the server
start_server()
