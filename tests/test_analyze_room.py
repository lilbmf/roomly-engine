from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def make_test_image_bytes(color=(240, 240, 240), size=(64, 64)) -> bytes:
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_analyze_room_success():
    image_bytes = make_test_image_bytes()

    response = client.post(
        "/analyze-room",
        files={"file": ("room.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()

    assert "style_tags" in data
    assert "dominant_colors" in data
    assert "recommendations" in data
    assert "affiliate_links" in data

    assert isinstance(data["style_tags"], list)
    assert isinstance(data["dominant_colors"], list)
    assert isinstance(data["recommendations"], list)
    assert isinstance(data["affiliate_links"], list)

    assert all(c.startswith("#") for c in data["dominant_colors"])
    assert all("title" in rec and "category" in rec and "reason" in rec for rec in data["recommendations"])
    assert all("retailer" in link and "url" in link and "title" in link for link in data["affiliate_links"])


def test_analyze_room_rejects_non_image_content_type():
    response = client.post(
        "/analyze-room",
        files={"file": ("room.txt", b"not-an-image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file must be an image."


def test_analyze_room_rejects_invalid_image_binary():
    response = client.post(
        "/analyze-room",
        files={"file": ("broken.png", b"not-really-png", "image/png")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file."


def test_analyze_room_rejects_empty_upload():
    response = client.post(
        "/analyze-room",
        files={"file": ("empty.png", b"", "image/png")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."
