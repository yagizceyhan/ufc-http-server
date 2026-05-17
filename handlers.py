"""
handlers.py — REST API Endpoint Handlers
=========================================
Defines all UFC Fighter API endpoints and registers them
on the shared router instance. Each handler receives a
parsed HTTPRequest and returns raw HTTP response bytes.

Registered endpoints:
    GET  /                              — HTML dashboard
    GET  /api/fighters                  — list all fighters (supports query filters)
    GET  /api/fighters/{id}             — single fighter by ID
    GET  /api/weightclasses             — all UFC weight class definitions
    GET  /api/stats/summary             — aggregated statistics across all fighters
    GET  /api/stats/top                 — top fighters ranked by a given metric
    POST /api/fighters                  — add a new fighter to the roster
"""

from router     import router
from http_parser import HTTPRequest, build_response, build_html_response, build_error
from data_store  import (
    get_all_fighters,
    get_fighter_by_id,
    filter_fighters,
    get_summary_stats,
    get_top_fighters,
    get_all_weight_classes,
    FIGHTERS,
)

# ─────────────────────────────────────────────
# DASHBOARD  —  GET /
# ─────────────────────────────────────────────

@router.route("GET", "/")
def dashboard(request: HTTPRequest) -> bytes:
    """
    Serve a minimal HTML landing page that lists all available
    API endpoints. Acts as a quick-start guide for anyone who
    opens the server URL in a browser.
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UFC Fighter API</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0a0a0a; color: #f0f0f0;
      display: flex; justify-content: center;
      padding: 48px 16px;
    }
    .card {
      background: #141414; border: 1px solid #2a2a2a;
      border-radius: 12px; padding: 40px;
      max-width: 680px; width: 100%;
    }
    h1 { font-size: 28px; margin-bottom: 6px; color: #ffffff; }
    .subtitle { color: #888; margin-bottom: 32px; font-size: 14px; }
    .badge {
      display: inline-block; padding: 2px 10px;
      border-radius: 99px; font-size: 11px;
      font-weight: 600; font-family: monospace;
    }
    .get  { background: #0d3321; color: #34d399; }
    .post { background: #1e2d0e; color: #a3e635; }
    table { width: 100%; border-collapse: collapse; }
    td { padding: 12px 8px; border-bottom: 1px solid #1f1f1f;
         font-size: 14px; vertical-align: middle; }
    td:first-child { width: 56px; }
    .path { font-family: monospace; color: #c4b5fd; }
    .desc { color: #9ca3af; font-size: 13px; padding-top: 2px; }
    tr:last-child td { border-bottom: none; }
    .footer { margin-top: 28px; font-size: 12px; color: #444; text-align: center; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🥊 UFC Fighter API</h1>
    <p class="subtitle">
      Lightweight HTTP server built with raw Python sockets &mdash; no frameworks.
    </p>
    <table>
      <tr>
        <td><span class="badge get">GET</span></td>
        <td>
          <div class="path">/api/fighters</div>
          <div class="desc">List all fighters. Filter via ?weight_class= &amp; ?nationality=</div>
        </td>
      </tr>
      <tr>
        <td><span class="badge get">GET</span></td>
        <td>
          <div class="path">/api/fighters/{id}</div>
          <div class="desc">Retrieve a single fighter by numeric ID</div>
        </td>
      </tr>
      <tr>
        <td><span class="badge get">GET</span></td>
        <td>
          <div class="path">/api/weightclasses</div>
          <div class="desc">All UFC weight class definitions with pound limits</div>
        </td>
      </tr>
      <tr>
        <td><span class="badge get">GET</span></td>
        <td>
          <div class="path">/api/stats/summary</div>
          <div class="desc">Aggregated statistics across the entire roster</div>
        </td>
      </tr>
      <tr>
        <td><span class="badge get">GET</span></td>
        <td>
          <div class="path">/api/stats/top</div>
          <div class="desc">Top fighters by metric. ?metric=ko_rate|sub_rate|win_rate|wins</div>
        </td>
      </tr>
      <tr>
        <td><span class="badge post">POST</span></td>
        <td>
          <div class="path">/api/fighters</div>
          <div class="desc">Add a new fighter to the in-memory roster (JSON body required)</div>
        </td>
      </tr>
    </table>
    <p class="footer">UFC-HTTP-Server/1.0 &nbsp;&bull;&nbsp; Built with Python socket &amp; os only</p>
  </div>
</body>
</html>"""
    return build_html_response(html)


# ─────────────────────────────────────────────
# FIGHTERS  —  GET /api/fighters
# ─────────────────────────────────────────────

@router.route("GET", "/api/fighters")
def list_fighters(request: HTTPRequest) -> bytes:
    """
    Return the fighter roster, optionally filtered by query parameters.

    Query parameters (all optional, case-insensitive):
        weight_class  — e.g. ?weight_class=Lightweight
        nationality   — e.g. ?nationality=Brazilian
        title_holder  — e.g. ?title_holder=true

    Response shape:
        {
            "count": 3,
            "filters_applied": {"weight_class": "Lightweight"},
            "fighters": [...]
        }
    """
    q = request.query  # shorthand for the parsed query-string dict

    # Read optional filter parameters from the query string
    weight_class  = q.get("weight_class")
    nationality   = q.get("nationality")

    # Convert the string "true"/"false" to a Python bool (or None = no filter)
    title_holder_raw = q.get("title_holder")
    if title_holder_raw is not None:
        title_holder = title_holder_raw.lower() == "true"
    else:
        title_holder = None

    fighters = filter_fighters(
        weight_class=weight_class,
        nationality=nationality,
        title_holder=title_holder,
    )

    # Build a summary of which filters were actually applied
    filters_applied = {k: v for k, v in {
        "weight_class":  weight_class,
        "nationality":   nationality,
        "title_holder":  title_holder_raw,
    }.items() if v is not None}

    return build_response(200, {
        "count":           len(fighters),
        "filters_applied": filters_applied,
        "fighters":        fighters,
    })


# ─────────────────────────────────────────────
# FIGHTER BY ID  —  GET /api/fighters/{id}
# ─────────────────────────────────────────────

@router.route("GET", "/api/fighters/{id}")
def get_fighter(request: HTTPRequest, id: str) -> bytes:
    """
    Return a single fighter record identified by their numeric ID.

    URL parameter:
        id — must be a positive integer string (e.g. /api/fighters/3)

    Returns 400 if the id is not a valid integer.
    Returns 404 if no fighter with that id exists.
    """
    # Validate that the path parameter is actually an integer
    if not id.isdigit():
        return build_error(400, f"Invalid fighter ID '{id}': must be a positive integer.")

    fighter = get_fighter_by_id(int(id))

    if fighter is None:
        return build_error(404, f"No fighter found with ID {id}.")

    # Compute derived stats before returning
    total_fights = fighter["wins"] + fighter["losses"] + fighter["draws"]
    win_rate     = round(fighter["wins"] / total_fights * 100, 1) if total_fights else 0
    ko_rate      = round(fighter["wins_by_ko"]  / fighter["wins"] * 100, 1) if fighter["wins"] else 0
    sub_rate     = round(fighter["wins_by_sub"] / fighter["wins"] * 100, 1) if fighter["wins"] else 0

    return build_response(200, {
        "fighter": fighter,
        "derived_stats": {
            "total_fights": total_fights,
            "win_rate_pct": win_rate,
            "ko_rate_pct":  ko_rate,
            "sub_rate_pct": sub_rate,
        },
    })


# ─────────────────────────────────────────────
# WEIGHT CLASSES  —  GET /api/weightclasses
# ─────────────────────────────────────────────

@router.route("GET", "/api/weightclasses")
def list_weight_classes(request: HTTPRequest) -> bytes:
    """
    Return all UFC weight class definitions.

    Response shape:
        {
            "count": 9,
            "weight_classes": [
                {"id": 1, "name": "Strawweight", "limit_lbs": 115},
                ...
            ]
        }
    """
    weight_classes = get_all_weight_classes()
    return build_response(200, {
        "count":          len(weight_classes),
        "weight_classes": weight_classes,
    })


# ─────────────────────────────────────────────
# SUMMARY STATS  —  GET /api/stats/summary
# ─────────────────────────────────────────────

@router.route("GET", "/api/stats/summary")
def stats_summary(request: HTTPRequest) -> bytes:
    """
    Return aggregated statistics computed across all fighters.

    Metrics include: total fighters, title holders, average age,
    average reach, average KO rate, and diversity counts.
    """
    return build_response(200, {
        "summary": get_summary_stats()
    })


# ─────────────────────────────────────────────
# TOP FIGHTERS  —  GET /api/stats/top
# ─────────────────────────────────────────────

@router.route("GET", "/api/stats/top")
def stats_top(request: HTTPRequest) -> bytes:
    """
    Return the top fighters ranked by a chosen performance metric.

    Query parameters:
        metric — one of: wins | ko_rate | sub_rate | win_rate  (default: wins)
        limit  — number of results to return, 1–20             (default: 5)

    Response shape:
        {
            "metric": "ko_rate",
            "limit": 5,
            "rankings": [...]
        }
    """
    metric = request.query.get("metric", "wins")
    limit  = request.query.get("limit",  "5")

    # Validate the metric name
    allowed_metrics = ("wins", "ko_rate", "sub_rate", "win_rate")
    if metric not in allowed_metrics:
        return build_error(
            400,
            f"Unknown metric '{metric}'. Allowed values: {', '.join(allowed_metrics)}"
        )

    # Validate and clamp the limit
    if not limit.isdigit() or not (1 <= int(limit) <= 20):
        return build_error(400, "Parameter 'limit' must be an integer between 1 and 20.")

    return build_response(200, {
        "metric":   metric,
        "limit":    int(limit),
        "rankings": get_top_fighters(metric=metric, limit=int(limit)),
    })


# ─────────────────────────────────────────────
# ADD FIGHTER  —  POST /api/fighters
# ─────────────────────────────────────────────

@router.route("POST", "/api/fighters")
def add_fighter(request: HTTPRequest) -> bytes:
    """
    Add a new fighter to the in-memory roster.

    Expected JSON body (all fields required):
        {
            "name":         "Fighter Name",
            "nickname":     "The Nickname",
            "nationality":  "Brazilian",
            "weight_class": "Middleweight",
            "age":          28,
            "height_cm":    180,
            "reach_cm":     185,
            "stance":       "Orthodox",
            "wins":         10,
            "losses":       1,
            "draws":        0,
            "wins_by_ko":   5,
            "wins_by_sub":  2,
            "wins_by_dec":  3,
            "title_holder": false,
            "rank":         8
        }

    Returns 400 if any required field is missing.
    Returns 201 Created on success, with the newly created fighter record.
    """
    required_fields = [
        "name", "nickname", "nationality", "weight_class",
        "age", "height_cm", "reach_cm", "stance",
        "wins", "losses", "draws",
        "wins_by_ko", "wins_by_sub", "wins_by_dec",
        "title_holder", "rank",
    ]

    # Check that every required field is present in the request body
    missing = [field for field in required_fields if field not in request.body]
    if missing:
        return build_error(
            400,
            f"Missing required fields: {', '.join(missing)}"
        )

    # Assign a new sequential ID (max existing ID + 1)
    new_id = max(f["id"] for f in FIGHTERS) + 1

    new_fighter = {"id": new_id, **request.body}
    FIGHTERS.append(new_fighter)

    return build_response(201, {
        "message": "Fighter added successfully.",
        "fighter": new_fighter,
    })