"""
http_parser.py — HTTP Request Parser & Response Builder
Makes Raw bytes parsed and creates HTTP response
"""

import json

# ─────────────────────────────────────────────
# HTTP STATUS CODES
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
    Raw HTTP byte'larını alır, anlamlı parçalara ayırır.

    Örnek ham istek:
        GET /api/fighters?weight_class=Lightweight HTTP/1.1\r\n
        Host: localhost:8080\r\n
        \r\n
    """

    def __init__(self, raw_data: bytes):
        self.method   = ""
        self.path     = ""
        self.query    = {}   # ?key=value çiftleri
        self.headers  = {}
        self.body     = {}
        self.valid    = False

        self._parse(raw_data)

    def _parse(self, raw_data: bytes):
        try:
            text = raw_data.decode("utf-8", errors="ignore")

            # Header ve body'yi ayır (\r\n\r\n sınır)
            if "\r\n\r\n" in text:
                header_section, body_section = text.split("\r\n\r\n", 1)
            else:
                header_section = text
                body_section   = ""

            lines = header_section.split("\r\n")

            # ── Request Line ──────────────────────────
            # Örnek: GET /api/fighters?weight_class=Lightweight HTTP/1.1
            request_line = lines[0].split(" ")
            if len(request_line) < 3:
                return

            self.method = request_line[0].upper()

            # Path ve query string'i ayır
            full_path = request_line[1]
            if "?" in full_path:
                self.path, query_string = full_path.split("?", 1)
                self.query = self._parse_query(query_string)
            else:
                self.path  = full_path
                self.query = {}

            # ── Headers ───────────────────────────────
            # Örnek: Host: localhost:8080
            for line in lines[1:]:
                if ": " in line:
                    key, value     = line.split(": ", 1)
                    self.headers[key.lower()] = value.strip()

            # ── Body (POST için) ───────────────────────
            if body_section.strip():
                try:
                    self.body = json.loads(body_section.strip())
                except json.JSONDecodeError:
                    self.body = {}

            self.valid = True

        except Exception:
            self.valid = False

    def _parse_query(self, query_string: str) -> dict:
        """
        'weight_class=Lightweight&rank=1' → {'weight_class': 'Lightweight', 'rank': '1'}
        """
        params = {}
        for pair in query_string.split("&"):
            if "=" in pair:
                key, value  = pair.split("=", 1)
                params[key] = value.replace("%20", " ")  # basit URL decode
        return params

    def __repr__(self):
        return f"HTTPRequest(method={self.method}, path={self.path}, query={self.query})"


# ─────────────────────────────────────────────
# RESPONSE BUILDER
# ─────────────────────────────────────────────

def build_response(status_code: int, data, headers: dict = None) -> bytes:
    """
    Python dict/list'i alır, tam HTTP response byte'ı döner.

    Örnek çıktı:
        HTTP/1.1 200 OK\r\n
        Content-Type: application/json\r\n
        Content-Length: 42\r\n
        \r\n
        {"fighters": [...]}
    """
    status_text = STATUS_CODES.get(status_code, "Unknown")
    body        = json.dumps(data, ensure_ascii=False, indent=2)
    body_bytes  = body.encode("utf-8")

    default_headers = {
        "Content-Type":                "application/json; charset=utf-8",
        "Content-Length":              str(len(body_bytes)),
        "Access-Control-Allow-Origin": "*",         # CORS
        "Connection":                  "close",
        "X-Powered-By":                "UFC-HTTP-Server/1.0",
    }

    if headers:
        default_headers.update(headers)

    # Header satırlarını birleştir
    header_lines = "\r\n".join(
        f"{k}: {v}" for k, v in default_headers.items()
    )

    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"{header_lines}\r\n"
        f"\r\n"
    ).encode("utf-8") + body_bytes

    return response


def build_html_response(html: str) -> bytes:
    """
    GET / için HTML sayfası döner.
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
    Hata response'u oluşturur.
    """
    return build_response(status_code, {
        "error":   STATUS_CODES.get(status_code, "Error"),
        "message": message,
        "status":  status_code,
    })