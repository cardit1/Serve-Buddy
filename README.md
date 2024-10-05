# Serve Buddy

Serve Buddy is a simple, lightweight HTTP file server that allows you to easily share files over your local network. It provides a user-friendly web interface for uploading and downloading files from a specified directory.

## Features

- Easy-to-use web interface
- File upload and download functionality
- Cross-platform compatibility (Windows, macOS, Linux)
- Customizable port and directory settings
- Local and network URL access

## Installation

1. Ensure you have Python 3.6 or higher installed on your system.
2. Clone this repository or download the `serve_buddy.py` file.

## Usage Guide

### Basic Usage

To start Serve Buddy with default settings:

```
python serve_buddy.py
```

This will start the server on port 8000 and serve files from the current directory.

### Custom Port and Directory

You can specify a custom port and directory:

```
python serve_buddy.py --port 8080 --dir /path/to/your/directory
```

### Command-line Options

- `--port`: Specify the port number (default: 8000)
- `--dir`: Specify the directory to serve files from (default: current directory)

## Accessing Serve Buddy

Once started, Serve Buddy will display the following information:

- Local URL: `http://localhost:<port>`
- Network URL: `http://<your-ip-address>:<port>`

You can access the web interface using either of these URLs from a web browser.

## Uploading Files

1. Open the Serve Buddy web interface in a browser.
2. Click on the "Choose File" button.
3. Select the file you want to upload.
4. Click the "Upload" button.

## Downloading Files

1. Open the Serve Buddy web interface in a browser.
2. You'll see a list of files in the served directory.
3. Click on a file name to download it.

## Stopping Serve Buddy

To stop Serve Buddy, simply press Ctrl+C in the terminal where it's running. The server will shut down gracefully.

## Notes

- Serve Buddy is designed for local network use. Be cautious when exposing it to the public internet.
- Large file uploads and downloads are handled efficiently, but may still be limited by your network speed.

## Contributing

Contributions to Serve Buddy are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

[MIT License](LICENSE)