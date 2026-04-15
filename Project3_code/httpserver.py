# httpserver.py
import socket
from fpdf import FPDF

# HTML Content (Valid Response)
HTML_PAGE = """\
<!DOCTYPE html>
<html>
<head>
    <title>Attendance Page</title>
</head>
<body style="margin:0; font-family:Arial, sans-serif; background:#f4f6f8; color:#222;">
    <div style="max-width:700px; margin:40px auto; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 14px rgba(0,0,0,0.08);">
        <h1 style="margin-top:0; color:#1f4e79;">Computer Network Attendance</h1>
        <p style="font-size:16px; line-height:1.5;">
            Use this page to submit attendance and download the generated attendance PDF.
        </p>

        <h2 style="margin-top:30px; color:#333;">Submit Attendance</h2>
        <form action="http://127.0.0.1:8080/post" method="POST" style="margin-top:15px;">
            <label for="student_id" style="display:block; margin-bottom:8px; font-weight:bold;">Student ID</label>
            <input
                type="text"
                id="student_id"
                name="student_id"
                required
                style="width:100%; padding:10px; margin-bottom:18px; border:1px solid #ccc; border-radius:8px; box-sizing:border-box;"
            >

            <label for="name" style="display:block; margin-bottom:8px; font-weight:bold;">Student Name</label>
            <input
                type="text"
                id="name"
                name="name"
                required
                style="width:100%; padding:10px; margin-bottom:20px; border:1px solid #ccc; border-radius:8px; box-sizing:border-box;"
            >

            <button
                type="submit"
                style="background:#1f4e79; color:white; border:none; padding:12px 20px; border-radius:8px; cursor:pointer; font-size:15px;"
            >
                Record Attendance
            </button>
        </form>

        <div style="margin-top:30px; padding-top:20px; border-top:1px solid #e0e0e0;">
            <h2 style="margin-top:0; color:#333;">Download Attendance PDF</h2>
            <a
                href="http://127.0.0.1:8080/document.pdf"
                style="display:inline-block; background:#2e8b57; color:white; text-decoration:none; padding:12px 18px; border-radius:8px;"
            >
                Download PDF
            </a>
        </div>
    </div>
</body>
</html>
""".replace("\n", "\r\n")

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

# File Paths
IMAGE_PATH = "wow.jpg"
PDF_PATH = "document.pdf"

def load_image():
    """Load the image as binary data."""
    with open(IMAGE_PATH, "rb") as f:
        return f.read()

def load_pdf():
    """Generate PDF from attendance.txt and return it as binary data."""
    pdf_path = "document.pdf"
    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    try:
        with open("attendance.txt", "r") as f:
            for line in f:
                pdf.cell(0, 10, txt=line.strip(), ln=True)
    except FileNotFoundError:
        pdf.cell(0, 10, txt="No attendance records found.", ln=True)
    pdf.output(pdf_path)
    # Read and return
    with open(pdf_path, "rb") as f:
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
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(HTML_PAGE.encode())}\r\n"
            "\r\n"
            f"{HTML_PAGE}"
        ).encode()
    elif method == "GET" and requested_file == "/wow.jpg":
        image_data = load_image()
        response = b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(image_data)).encode() + b"\r\n\r\n" + image_data
    elif method == "GET" and requested_file == "/document.pdf":
        try:
            pdf_data = load_pdf()
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/pdf\r\n"
                b"Content-Length: " + str(len(pdf_data)).encode() + b"\r\n\r\n" + pdf_data
            )
        except FileNotFoundError:
            error_response = ERROR_PAGE.format(length=len(ERROR_PAGE)).encode()
            response = error_response
    elif method == "POST" and requested_file == "/post":
        post_data = request.split("\r\n\r\n")[1] if "\r\n\r\n" in request else ""
        print(f"\n--- Received POST Data ---\n{post_data}")

        student_id = ""
        student_name = ""

        fields = post_data.split("&")
        for field in fields:
            if "=" in field:
                key, value = field.split("=", 1)
                if key == "student_id":
                    student_id = value
                elif key == "name":
                    student_name = value.replace("+", " ")

        with open("attendance.txt", "a") as f:
            f.write(f"ID: {student_id}, Name: {student_name}\n")

        success_body = f"""\
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attendance Saved</title>
    </head>
    <body style="margin:0; font-family:Arial, sans-serif; background:#f4f6f8; color:#222;">
        <div style="max-width:700px; margin:40px auto; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 14px rgba(0,0,0,0.08);">
            <h1 style="color:#1f4e79;">Attendance Recorded</h1>
            <p><strong>ID:</strong> {student_id}</p>
            <p><strong>Name:</strong> {student_name}</p>

            <a href="http://127.0.0.1:8080/"
               style="display:inline-block; margin-right:12px; background:#1f4e79; color:white; text-decoration:none; padding:12px 18px; border-radius:8px;">
                Back to Page
            </a>

            <a href="http://127.0.0.1:8080/document.pdf"
               style="display:inline-block; background:#2e8b57; color:white; text-decoration:none; padding:12px 18px; border-radius:8px;">
                Download PDF
            </a>
        </div>
    </body>
    </html>
    """.replace("\n", "\r\n")

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(success_body.encode())}\r\n"
            "\r\n"
            f"{success_body}"
        ).encode()
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
