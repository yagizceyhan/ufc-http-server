"""
router.py — URL Router
======================
Maps incoming HTTP requests to the correct handler function
using regex-based pattern matching on the URL path.
No external libraries are used — only the built-in re module.
"""

import re
from http_parser import HTTPRequest, build_error

# ─────────────────────────────────────────────
# ROUTER CLASS
# ─────────────────────────────────────────────

class Router:
    """
    Stores registered routes and resolves incoming requests.

    Each route is stored as a tuple:
        (method: str, pattern: compiled regex, handler: callable)

    Path parameters use curly-brace syntax and are converted
    to named regex capture groups at registration time:
        "/api/fighters/{id}"  →  r"^/api/fighters/(?P<id>[^/]+)$"

    Supported HTTP methods: GET, POST, PUT, DELETE (and any other verb).
    """

    def __init__(self):
        # Internal route table — populated via add_route() or @route decorator
        self.routes = []

    def add_route(self, method: str, path_pattern: str, handler):
        """
        Register a new route.

        Args:
            method       : HTTP verb string, e.g. "GET"
            path_pattern : URL pattern with optional {param} placeholders
            handler      : callable with signature handler(request, **url_params)

        The path pattern is compiled once at registration time so that
        every incoming request pays only a regex-match cost, not a compile cost.
        """
        # Convert {param} placeholders to named regex capture groups.
        # Example: "/api/fighters/{id}" → "/api/fighters/(?P<id>[^/]+)"
        regex_pattern = re.sub(
            r"\{(\w+)\}",
            r"(?P<\1>[^/]+)",
            path_pattern
        )
        # Anchor the pattern so partial matches are rejected
        regex_pattern = f"^{regex_pattern}$"
        compiled      = re.compile(regex_pattern)

        self.routes.append((method.upper(), compiled, handler))

    def route(self, method: str, path_pattern: str):
        """
        Decorator shorthand for add_route().

        Usage:
            @router.route("GET", "/api/fighters")
            def list_fighters(request):
                ...
        """
        def decorator(fn):
            self.add_route(method, path_pattern, fn)
            return fn
        return decorator

    def resolve(self, request: HTTPRequest) -> bytes:
        """
        Find the handler for the incoming request and call it.

        Resolution order:
            1. Iterate over registered routes.
            2. If the path matches a pattern:
                a. If the method also matches → call the handler and return.
                b. Otherwise → record the allowed method and continue.
            3. After all routes are checked:
                - If any path matched but no method matched → 405 Method Not Allowed.
                - If no path matched at all               → 404 Not Found.

        URL parameters extracted from the path (e.g. id="3" from /api/fighters/3)
        are passed to the handler as keyword arguments.
        """
        # Collect methods that match the path (for 405 response)
        matched_methods = []

        for method, pattern, handler in self.routes:
            match = pattern.match(request.path)
            if match:
                matched_methods.append(method)

                if method == request.method:
                    # Extract named groups: /api/fighters/3 → {"id": "3"}
                    url_params = match.groupdict()
                    return handler(request, **url_params)

        # Path was found but the HTTP method is not registered for it
        if matched_methods:
            allowed = ", ".join(set(matched_methods))
            return build_error(
                405,
                f"Method '{request.method}' is not allowed on this endpoint. "
                f"Allowed: {allowed}"
            )

        # No route matched the path at all
        return build_error(
            404,
            f"Endpoint not found: {request.method} {request.path}"
        )


# ─────────────────────────────────────────────
# GLOBAL ROUTER INSTANCE
# ─────────────────────────────────────────────
# A single shared Router instance imported by handlers.py and server.py.
# All routes are registered on this object at module load time.

router = Router()