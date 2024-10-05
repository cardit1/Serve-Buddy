import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import argparse
import sys
import signal
import re

VERSION = "1.0.0"

class FileServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle GET requests
        if self.path == '/':
            # Serve the main page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path.startswith('/download/'):
            # Handle file downloads
            file_name = os.path.join(self.server.upload_dir, urllib.parse.unquote(self.path[10:]))
            if os.path.exists(file_name) and os.path.isfile(file_name):
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_name)}"')
                self.send_header('Content-Length', str(os.path.getsize(file_name)))
                self.end_headers()
                with open(file_name, 'rb') as file:
                    while True:
                        chunk = file.read(8192)  # Read in 8KB chunks
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            else:
                self.send_error(404, 'File not found')
        else:
            self.send_error(404, 'File not found')

    def do_POST(self):
        if self.path == '/upload':
            content_type = self.headers['content-type']
            if not content_type:
                self.send_error(400, "Content-Type header is missing")
                return
            
            # Parse the multipart form data
            content_length = int(self.headers['Content-Length'])
            boundary = content_type.split("=")[1].encode()
            
            # Read the entire payload
            payload = self.rfile.read(content_length)
            
            # Find the file data in the payload
            file_start = payload.find(b'\r\n\r\n') + 4
            file_end = payload.rfind(b'\r\n--' + boundary + b'--') - 2
            file_data = payload[file_start:file_end]
            
            # Extract the filename
            header = payload[:file_start].decode()
            filename_match = re.search(r'filename="(.+)"', header)
            if not filename_match:
                self.send_error(400, "Filename not found in the request")
                return
            
            filename = os.path.basename(filename_match.group(1))
            file_path = os.path.join(self.server.upload_dir, filename)
            
            try:
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
            except Exception as e:
                self.send_error(500, f"Error saving file: {str(e)}")
        else:
            self.send_error(404, 'File not found')

    def get_html(self):
        # Generate HTML for the main page
        files = os.listdir(self.server.upload_dir)
        file_list = ''.join([f'<li><a href="/download/{f}">{f}</a></li>' for f in files if os.path.isfile(os.path.join(self.server.upload_dir, f))])
        return f'''
        <html>
        <head>
            <title>Serve Buddy</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                h1, h2 {{
                    color: #2c3e50;
                }}
                .container {{
                    background-color: white;
                    border-radius: 5px;
                    padding: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                li {{
                    margin-bottom: 10px;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .upload-form {{
                    margin-top: 20px;
                    background-color: #ecf0f1;
                    padding: 20px;
                    border-radius: 5px;
                }}
                input[type="file"] {{
                    margin-bottom: 10px;
                }}
                input[type="submit"] {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }}
                input[type="submit"]:hover {{
                    background-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Serve Buddy</h1>
                <h2>Files in {self.server.upload_dir}:</h2>
                <ul>
                    {file_list}
                </ul>
                <div class="upload-form">
                    <h2>Upload File:</h2>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file">
                        <input type="submit" value="Upload">
                    </form>
                </div>
            </div>
        </body>
        </html>
        '''

class QuickHttpServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, upload_dir):
        super().__init__(server_address, RequestHandlerClass)
        self.upload_dir = upload_dir
        self.running = False

    def serve_forever(self, poll_interval=0.5):
        self.running = True
        while self.running:
            self.handle_request()

    def stop(self):
        self.running = False
        # Create a dummy request to unblock handle_request()
        try:
            socket.create_connection(("localhost", self.server_port), 1).close()
        except:
            pass

class ServeBuddy:
    def __init__(self, port, upload_dir):
        self.port = port
        self.upload_dir = upload_dir
        self.server = None
        self.server_thread = None

    def run(self):
        server_address = ('', self.port)
        self.server = QuickHttpServer(server_address, FileServerHandler, self.upload_dir)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        print(f"Serve Buddy is running on port {self.port}")
        print(f"Serving files from: {self.upload_dir}")
        print(f"Local URL: http://localhost:{self.port}")
        print(f"Network URL: http://{get_ip_address()}:{self.port}")
        print("Press Ctrl+C to stop Serve Buddy")

    def stop(self):
        if self.server:
            print("\nStopping Serve Buddy...")
            self.server.stop()
            self.server_thread.join(timeout=5)  # Wait for the server thread to finish
            print("Serve Buddy has been stopped.")
            print("Thank you for using Serve Buddy! Goodbye!")

def get_ip_address():
    # Get the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def print_intro():
    # Print the introduction message
    intro = f"""
    ╔═══════════════════════════════════════════╗
    ║               Serve Buddy                 ║
    ║               Version {VERSION:<8}            ║
    ╚═══════════════════════════════════════════╝

    Serve Buddy is a simple HTTP file server that allows
    you to upload and download files from a specified directory.

    Usage:
      python {os.path.basename(sys.argv[0])} [options]

    Options:
      -h, --help            Show this help message and exit
      -p PORT, --port PORT  Port to run Serve Buddy on (default: 8000)
      -d DIR, --dir DIR     Directory to serve files from (default: current working directory)

    Once Serve Buddy is running, open a web browser and navigate
    to the provided URL to access the file server interface.
    """
    print(intro)

def signal_handler(signum, frame):
    # Handle termination signals
    print("\nReceived signal to terminate.")
    serve_buddy.stop()
    sys.exit(0)

def check_directory_access(directory):
    # Check if the directory exists and is accessible
    if not os.path.exists(directory):
        raise ValueError(f"The directory '{directory}' does not exist.")
    if not os.path.isdir(directory):
        raise ValueError

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Serve Buddy - Simple HTTP File Server", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show this help message and exit")
    parser.add_argument('-p', '--port', type=int, help="Port to run Serve Buddy on (default: 8000)")
    parser.add_argument('-d', '--dir', help="Directory to serve files from (default: current working directory)")

    args = parser.parse_args()

    if args.help:
        print_intro()
        parser.print_help()
        sys.exit(0)

    print_intro()

    # Get the port number
    port = args.port if args.port else input("Enter the port number for Serve Buddy (default 8000): ").strip()
    
    try:
        port = int(port) if port else 8000
        if port < 1 or port > 65535:
            raise ValueError
    except ValueError:
        print("Invalid port number. Using default port 8000.")
        port = 8000

    # Get the upload directory
    upload_dir = args.dir if args.dir else os.getcwd()
    try:
        check_directory_access(upload_dir)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Create global ServeBuddy instance
    global serve_buddy
    serve_buddy = ServeBuddy(port, upload_dir)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, signal_handler)  # Handle Ctrl+Break on Windows
    else:
        signal.signal(signal.SIGTSTP, signal_handler)  # Handle Ctrl+Z on Unix-like systems

    try:
        # Run the server
        serve_buddy.run()
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        serve_buddy.stop()

if __name__ == "__main__":
    main()