"""
http_parser.py — HTTP Request Parser & Response Builder
========================================================
Converts raw TCP bytes into a structured HTTPRequest object,
and serialises Python dicts/lists into valid HTTP responses.
No external libraries are used — only the built-in json module.
"""

import json

# ─────────────────────────────────────────────
# HTTP STATUS CODES
# Subset of standard codes used by this server.
# ─────────────────────────────────────────────
STATUS_CODES = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

# ─────────────────────────────────────────────
# REQUEST PARSER
# ─────────────────────────────────────────────

class HTTPRequest:
    """
    Parses a raw HTTP request received from a TCP socket.

    A typical raw request looks like:
        GET /api/fighters?weight_class=Lightweight HTTP/1.1\r\n
        Host: localhost:8080\r\n
        Content-Type: application/json\r\n
        \r\n
        {"key": "value"}

    After parsing, the following attributes are available:
        method   (str)  — HTTP verb: GET, POST, PUT, DELETE …
        path     (str)  — URL path without query string: /api/fighters
        query    (dict) — query params: {"weight_class": "Lightweight"}
        headers  (dict) — lowercase header names: {"host": "localhost:8080"}
        body     (dict) — decoded JSON body (POST/PUT requests)
        valid    (bool) — False if the request could not be parsed
    """

    def __init__(self, raw_data: bytes):
        self.method  = ""
        self.path    = ""
        self.query   = {}
        self.headers = {}
        self.body    = {}
        self.valid   = False

        self._parse(raw_data)

    def _parse(self, raw_data: bytes):
        """
        Entry point for the parsing pipeline:
            1. Decode bytes to UTF-8 string.
            2. Split on \\r\\n\\r\\n to separate headers from body.
            3. Parse the request line (method, path, protocol).
            4. Extract query string parameters from the path.
            5. Parse each header line into key-value pairs.
            6. Decode the body as JSON (if present).
        """
        try:
            text = raw_data.decode("utf-8", errors="ignore")

            # The blank line (\r\n\r\n) separates headers from the body
            if "\r\n\r\n" in text:
                header_section, body_section = text.split("\r\n\r\n", 1)
            else:
                header_section = text
                body_section   = ""

            lines = header_section.split("\r\n")

            # ── Step 1: Request line ──────────────────
            # Format: METHOD /path?query HTTP/version
            request_line = lines[0].split(" ")
            if len(request_line) < 3:
                return  # Malformed request line — mark as invalid

            self.method = request_line[0].upper()

            # ── Step 2: Path and query string ─────────
            full_path = request_line[1]
            if "?" in full_path:
                self.path, query_string = full_path.split("?", 1)
                self.query = self._parse_query(query_string)
            else:
                self.path  = full_path
                self.query = {}

            # ── Step 3: Headers ───────────────────────
            # Each line after the request line is a "Key: Value" pair.
            # Keys are stored in lowercase for case-insensitive lookup.
            for line in lines[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    self.headers[key.lower()] = value.strip()

            # ── Step 4: Body ──────────────────────────
            # Expected only for POST / PUT requests.
            # We attempt to decode it as JSON; ignore if malformed.
            if body_section.strip():
                try:
                    self.body = json.loads(body_section.strip())
                except json.JSONDecodeError:
                    self.body = {}

            self.valid = True

        except Exception:
            # Any unexpected error marks the request as invalid.
            # The server will return a 400 Bad Request in this case.
            self.valid = False

    def _parse_query(self, query_string: str) -> dict:
        """
        Decode a URL query string into a plain dictionary.

        Example:
            "weight_class=Lightweight&rank=1"
            → {"weight_class": "Lightweight", "rank": "1"}

        Note: Only handles simple key=value pairs and %20 → space.
        A production server would use urllib.parse — we roll our own
        to stay framework-free.
        """
        params = {}
        for pair in query_string.split("&"):
            if "=" in pair:
                key, value  = pair.split("=", 1)
                # Minimal URL decoding: replace %20 with a space
                params[key] = value.replace("%20", " ")
        return params

    def __repr__(self):
        return (
            f"HTTPRequest(method={self.method}, "
            f"path={self.path}, "
            f"query={self.query})"
        )


# ─────────────────────────────────────────────
# RESPONSE BUILDER
# ─────────────────────────────────────────────

def build_response(status_code: int, data, headers: dict = None) -> bytes:
    """
    Serialise a Python object into a complete HTTP/1.1 response.

    Args:
        status_code : integer HTTP status (e.g. 200, 404)
        data        : any JSON-serialisable Python object (dict, list …)
        headers     : optional dict of extra headers to include

    Returns:
        bytes — the full response ready to be sent over the socket.

    Wire format:
        HTTP/1.1 200 OK\\r\\n
        Content-Type: application/json; charset=utf-8\\r\\n
        Content-Length: 42\\r\\n
        ...\\r\\n
        \\r\\n
        {"key": "value"}
    """
    status_text = STATUS_CODES.get(status_code, "Unknown")

    # Serialise the payload to UTF-8 JSON bytes
    body       = json.dumps(data, ensure_ascii=False, indent=2)
    body_bytes = body.encode("utf-8")

    # Default headers sent with every JSON response
    default_headers = {
        "Content-Type":                "application/json; charset=utf-8",
        "Content-Length":              str(len(body_bytes)),
        "Access-Control-Allow-Origin": "*",              # Allow all CORS origins
        "Connection":                  "close",          # No keep-alive (simple server)
        "X-Powered-By":                "UFC-HTTP-Server/1.0",
    }

    # Caller-supplied headers override the defaults
    if headers:
        default_headers.update(headers)

    # Build the header block: one "Key: Value\r\n" per entry
    header_lines = "\r\n".join(
        f"{k}: {v}" for k, v in default_headers.items()
    )

    # Concatenate status line + headers + blank line + body
    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"{header_lines}\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    return response


def build_html_response(html: str) -> bytes:
    """
    Wrap an HTML string in a minimal HTTP/1.1 200 OK response.
    Used exclusively for the GET / dashboard endpoint.
    """
    body_bytes = html.encode("utf-8")

    response = (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    return response


def build_error(status_code: int, message: str) -> bytes:
    """
    Build a standardised JSON error response.

    Response body shape:
        {
            "error":   "Not Found",
            "message": "Endpoint not found: GET /api/xyz",
            "status":  404
        }
    """
    return build_response(status_code, {
        "error":   STATUS_CODES.get(status_code, "Error"),
        "message": message,
        "status":  status_code,
    })