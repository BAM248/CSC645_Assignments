# httpclient.py
import socket
import os
import webbrowser

# Server Configuration
SERVER_IP = input("Enter the server IP address): ")
SERVER_PORT = 8080

# Student Inputs HTTP Method and Path
http_method = input("Enter HTTP method (GET or POST): ").strip().upper()
request_path = input("Enter request path (e.g., /index.html, /wow.jpg, /document.pdf, or /post): ").strip()

# Handle POST request (attendance)
post_data = ""
if http_method == "POST":
    student_id = input("Enter student ID: ")
    student_name = input("Enter student name: ")

    student_name = student_name.replace(" ", "+")
    post_data = f"student_id={student_id}&name={student_name}"

    content_length = len(post_data)

    http_request = (
        f"{http_method} {request_path} HTTP/1.1\r\n"
        f"Host: {SERVER_IP}\r\n"
        f"Content-Length: {content_length}\r\n"
        f"Content-Type: text/plain\r\n\r\n"
        f"{post_data}"
    )
else:  # Handle GET request
    http_request = f"{http_method} {request_path} HTTP/1.1\r\nHost: {SERVER_IP}\r\n\r\n"

print("\n--- Sending HTTP Request ---")
print(http_request)

# Create Socket and Send Request
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
sock.sendall(http_request.encode())

# Receive Response
response = b""
while True:
    chunk = sock.recv(4096)
    if not chunk:
        break
    response += chunk

# Close Socket
sock.close()

# Ensure we received data
if not response:
    print("Error: No response received from the server.")
    exit(1)

# Attempt to split headers and body safely
if b"\r\n\r\n" in response:
    headers, body = response.split(b"\r\n\r\n", 1)
    print("\n--- Received HTTP Response Headers ---")
    print(headers.decode(errors="ignore"))
else:
    print("\nError: Received an invalid HTTP response.")
    print(response.decode(errors="ignore"))
    exit(1)

# Handle GET Response: Save and Open Webpage or Image
if http_method == "GET":
    if request_path == "/index.html" or request_path == "/":
        html_path = "downloaded_page.html"
        with open(html_path, "wb") as f:
            f.write(body)
        webbrowser.open("file://" + os.path.abspath(html_path))
        print(f"\nDownloaded webpage saved as {html_path} and opened in browser.")
    elif request_path == "/wow.jpg":
        img_path = "wow.jpg"
        with open(img_path, "wb") as f:
            f.write(body)
        print(f"\nImage saved as {img_path}. Open it manually.")
    elif request_path == "/document.pdf":
        pdf_path = "downloaded_document.pdf"
        with open(pdf_path, "wb") as f:
            f.write(body)
        print(f"\nPDF saved as {pdf_path}. Open it manually.")
