# 🥊 UFC Fighter API — Lightweight HTTP Server

A production-style REST API server built **entirely from scratch** using only Python's built-in `socket` and `os` modules — no Flask, no Django, no FastAPI, no external dependencies whatsoever.

This project demonstrates a deep understanding of how HTTP works at the protocol level, from raw TCP byte streams to structured JSON responses.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yagizceyhan/ufc-http-server.git
cd ufc-http-server

# Run the server (no installation needed)
py server.py        # Windows
python3 server.py   # macOS / Linux
```

Then open your browser and navigate to:

```
http://127.0.0.1:8080/
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | HTML dashboard listing all endpoints |
| `GET` | `/api/fighters` | List all fighters (supports query filters) |
| `GET` | `/api/fighters/{id}` | Single fighter by numeric ID |
| `GET` | `/api/weightclasses` | All UFC weight class definitions |
| `GET` | `/api/stats/summary` | Aggregated statistics across the roster |
| `GET` | `/api/stats/top` | Top fighters ranked by a performance metric |
| `POST` | `/api/fighters` | Add a new fighter to the roster |

### Query Parameters

**`GET /api/fighters`**
```
?weight_class=Lightweight
?nationality=Brazilian
?title_holder=true
```

**`GET /api/stats/top`**
```
?metric=ko_rate      # KO win percentage
?metric=sub_rate     # Submission win percentage
?metric=win_rate     # Overall win percentage
?metric=wins         # Raw win count (default)
?limit=5             # Number of results (1–20)
```

### Example Requests

```bash
# All lightweight fighters
curl http://127.0.0.1:8080/api/fighters?weight_class=Lightweight

# Fighter with ID 4 (Alex Pereira)
curl http://127.0.0.1:8080/api/fighters/4

# Top 5 fighters by KO rate
curl http://127.0.0.1:8080/api/stats/top?metric=ko_rate

# Add a new fighter
curl -X POST http://127.0.0.1:8080/api/fighters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paddy Pimblett",
    "nickname": "The Baddy",
    "nationality": "British",
    "weight_class": "Lightweight",
    "age": 29,
    "height_cm": 175,
    "reach_cm": 178,
    "stance": "Orthodox",
    "wins": 22,
    "losses": 3,
    "draws": 0,
    "wins_by_ko": 8,
    "wins_by_sub": 9,
    "wins_by_dec": 5,
    "title_holder": false,
    "rank": 12
  }'
```

---

## 🏗️ Project Architecture

```
ufc-http-server/
├── server.py        ← Entry point — TCP socket, accept loop
├── http_parser.py   ← Raw bytes → HTTPRequest, dict → HTTP response
├── router.py        ← Regex-based URL pattern matcher
├── handlers.py      ← REST endpoint logic
└── data_store.py    ← In-memory fighter database + aggregation
```

### Request Lifecycle

```
Client
  │
  │  TCP connection
  ▼
server.py        →  socket.accept() / conn.recv()
  │
  │  raw bytes
  ▼
http_parser.py   →  HTTPRequest(method, path, query, headers, body)
  │
  │  parsed request
  ▼
router.py        →  regex match  →  handler function
  │
  │  handler result
  ▼
handlers.py      →  query data_store  →  build_response()
  │
  │  HTTP response bytes
  ▼
Client
```

---

## ⚙️ How It Works

### 1. TCP Socket (`server.py`)
The server creates a raw `SOCK_STREAM` socket, binds it to `127.0.0.1:8080`, and enters a blocking `accept()` loop. Each accepted connection is passed to `handle_connection()`.

### 2. HTTP Parsing (`http_parser.py`)
Raw bytes are decoded and split on `\r\n\r\n` to separate headers from the body. The request line (`GET /api/fighters HTTP/1.1`) is parsed to extract the method, path, and query string. Headers are stored as a lowercase dictionary. The body is decoded as JSON for `POST` requests.

### 3. URL Routing (`router.py`)
Routes are registered with `{param}` placeholders that are compiled into named regex capture groups at startup:
```
/api/fighters/{id}  →  ^/api/fighters/(?P<id>[^/]+)$
```
The router distinguishes between **404 Not Found** (path unknown) and **405 Method Not Allowed** (path known, wrong verb).

### 4. Handlers & Data (`handlers.py` / `data_store.py`)
Each handler function receives the parsed request and any URL parameters. Data lives in plain Python lists and dicts — no database, no ORM. Aggregation (filtering, sorting, statistics) is done with pure Python list comprehensions and `sorted()`.

---

## 🗃️ Fighter Dataset

The mock database includes **12 current UFC fighters** across **8 weight classes**:

| Fighter | Division | Record | KO Rate |
|---------|----------|--------|---------|
| Islam Makhachev | Lightweight | 26-1 | 30.8% |
| Jon Jones | Heavyweight | 27-1 | 37.0% |
| Alex Pereira | Light Heavyweight | 11-2 | 81.8% |
| Ilia Topuria | Featherweight | 15-0 | 60.0% |
| Conor McGregor | Lightweight | 22-6 | 86.4% |
| Charles Oliveira | Lightweight | 34-9 | 26.5% |
| Khamzat Chimaev | Welterweight | 13-0 | 38.5% |
| … and more | | | |

---

## 🛠️ Configuration

The server can be configured via environment variables:

```bash
# Custom host and port
HOST=0.0.0.0 PORT=9000 py server.py
```

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `127.0.0.1` | Interface to bind on |
| `PORT` | `8080` | TCP port to listen on |

---

## 📋 Requirements

- Python 3.6+
- No third-party packages — standard library only

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
