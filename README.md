# roomly-engine

Backend API for Roomly built with FastAPI.

## Features

- `POST /analyze-room` accepts a room image upload (`multipart/form-data`)
- Returns:
  - `style_tags`: list of inferred style labels
  - `dominant_colors`: list of hex color values
  - `recommendations`: list of recommendation objects (`title`, `category`, `reason`)
  - `affiliate_links`: list of affiliate link objects (`retailer`, `url`, `title`)

## Run locally

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

API will be available at `http://127.0.0.1:8000`.

### 4. Example request

```bash
curl -X POST "http://127.0.0.1:8000/analyze-room" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/room.jpg"
```

## Run locally (Mac)

Assumes macOS with Python **3.11+** installed.

### 1) Verify Python version

```bash
python3 --version
```

### 2) Create a virtual environment

```bash
python3 -m venv .venv
```

### 3) Activate the virtual environment

```bash
source .venv/bin/activate
```

### 4) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5) Confirm main app file and start command

- **Main file:** `app/main.py`
- **FastAPI app object:** `app`
- **Start command:**

```bash
uvicorn app.main:app --reload
```

### 6) Test `POST /analyze-room` with `curl`

```bash
curl -X POST "http://127.0.0.1:8000/analyze-room" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/room.jpg;type=image/jpeg"
```

## Run tests

```bash
pytest
```
