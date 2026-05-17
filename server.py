"""
server.py — Main HTTP Server
=============================
Binds a TCP socket to a port, accepts incoming connections,
and dispatches each request through the parser and router.

This is the only entry point for the application:
    py server.py

No external libraries are used — only the built-in socket and os modules.
"""

import socket
import os

# Register all route handlers by importing the module.
# The @router.route decorators run at import time, populating
# the router's route table before the server starts accepting connections.
import handlers
from router      import router
from http_parser import HTTPRequest, build_error

# ─────────────────────────────────────────────
# CONFIGURATION
# These values can be overridden via environment variables.
#   HOST : interface to bind on (0.0.0.0 = all interfaces)
#   PORT : TCP port to listen on
# ─────────────────────────────────────────────
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8080))

# Maximum number of queued connections before the OS starts refusing new ones
BACKLOG = 5

# Size of each recv() call in bytes — enough for typical HTTP/1.1 requests
BUFFER_SIZE = 4096


# ─────────────────────────────────────────────
# REQUEST HANDLER
# ─────────────────────────────────────────────

def handle_connection(conn: socket.socket, addr: tuple):
    """
    Handle a single client connection end-to-end.

    Steps:
        1. Read raw bytes from the socket.
        2. Parse them into an HTTPRequest object.
        3. Resolve the request through the router.
        4. Send the response bytes back to the client.
        5. Close the connection (HTTP/1.0-style, no keep-alive).

    Args:
        conn : the accepted client socket
        addr : (ip, port) tuple of the remote client
    """
    try:
        # Receive the raw HTTP request bytes from the client
        raw_data = conn.recv(BUFFER_SIZE)

        if not raw_data:
            return  # Client closed the connection before sending data

        # Parse the raw bytes into a structured request object
        request = HTTPRequest(raw_data)

        # Log the incoming request to stdout
        print(f"  → {request.method} {request.path} from {addr[0]}:{addr[1]}")

        if not request.valid:
            # Could not parse the request — return 400 Bad Request
            response = build_error(400, "Malformed HTTP request.")
        else:
            # Hand off to the router — it finds the right handler and calls it
            response = router.resolve(request)

        # Send the complete response in one call
        conn.sendall(response)

    except Exception as e:
        # Catch-all: log the error and attempt to return a 500 response
        print(f"  [ERROR] {e}")
        try:
            conn.sendall(build_error(500, "Internal server error."))
        except Exception:
            pass  # Socket may already be broken — nothing we can do

    finally:
        # Always close the connection, even if an exception occurred
        conn.close()


# ─────────────────────────────────────────────
# SERVER BOOTSTRAP
# ─────────────────────────────────────────────

def run():
    """
    Create the server socket, bind it to HOST:PORT, and enter
    the main accept loop.

    Socket options explained:
        AF_INET      — IPv4 address family
        SOCK_STREAM  — TCP (reliable, ordered, connection-based)
        SO_REUSEADDR — allows reusing a port that is in TIME_WAIT state,
                       so we can restart the server immediately after stopping it
                       without waiting ~60 seconds for the OS to release the port.
    """
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the port to be reused immediately after the server restarts
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the configured address and port
    server_socket.bind((HOST, PORT))

    # Start listening — queue up to BACKLOG pending connections
    server_socket.listen(BACKLOG)

    print("=" * 48)
    print("  🥊 UFC Fighter API — HTTP Server")
    print("=" * 48)
    print(f"  Listening on  : http://{HOST}:{PORT}")
    print(f"  Endpoints     : http://{HOST}:{PORT}/api/fighters")
    print(f"  Dashboard     : http://{HOST}:{PORT}/")
    print("  Press Ctrl+C to stop.")
    print("=" * 48)

    try:
        # ── Main accept loop ──────────────────────
        # Blocks on accept() until a client connects.
        # Each connection is handled sequentially (single-threaded).
        while True:
            conn, addr = server_socket.accept()
            handle_connection(conn, addr)

    except KeyboardInterrupt:
        # Ctrl+C — graceful shutdown
        print("\n  Server stopped.")

    finally:
        server_socket.close()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run()