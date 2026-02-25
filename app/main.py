from collections import Counter
from io import BytesIO
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, HttpUrl
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="roomly-engine", version="0.1.0")


class Recommendation(BaseModel):
    title: str
    category: str
    reason: str


class AffiliateLink(BaseModel):
    retailer: str
    url: HttpUrl
    title: str


class AnalyzeRoomResponse(BaseModel):
    style_tags: List[str]
    dominant_colors: List[str]
    recommendations: List[Recommendation]
    affiliate_links: List[AffiliateLink]


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def extract_dominant_colors(image: Image.Image, count: int = 4) -> List[str]:
    small = image.convert("RGB").resize((128, 128))
    pixels = list(small.getdata())
    quantized = [(r // 16 * 16, g // 16 * 16, b // 16 * 16) for r, g, b in pixels]
    most_common = Counter(quantized).most_common(count)
    return [rgb_to_hex(color) for color, _ in most_common]


def infer_style_tags(image: Image.Image, colors: List[str]) -> List[str]:
    width, height = image.size
    brightness = sum(image.convert("L").getdata()) / (width * height)

    tags = ["interior"]
    if width > height:
        tags.append("wide-layout")
    else:
        tags.append("portrait-layout")

    if brightness > 150:
        tags.append("airy")
    else:
        tags.append("cozy")

    if any(c in {"#f0f0f0", "#e0e0e0", "#d0d0d0", "#c0c0c0"} for c in colors):
        tags.append("minimal")
    else:
        tags.append("contemporary")

    return tags


def build_recommendations(tags: List[str], colors: List[str]) -> List[Recommendation]:
    recommendations = [
        Recommendation(
            title="Textured Throw Blanket",
            category="decor",
            reason=f"Adds warmth that complements {'cozy' if 'cozy' in tags else 'airy'} aesthetics.",
        ),
        Recommendation(
            title="Accent Floor Lamp",
            category="lighting",
            reason="Improves layered lighting and enhances room depth.",
        ),
        Recommendation(
            title="Area Rug",
            category="furniture",
            reason=f"Anchors the palette around dominant tones like {colors[0] if colors else '#cccccc'}.",
        ),
    ]
    return recommendations


def build_affiliate_links(recommendations: List[Recommendation]) -> List[AffiliateLink]:
    retailer_base = {
        "decor": ("Wayfair", "https://www.wayfair.com/keyword.php?keyword="),
        "lighting": ("IKEA", "https://www.ikea.com/us/en/search/?q="),
        "furniture": ("Amazon", "https://www.amazon.com/s?k="),
    }

    links: List[AffiliateLink] = []
    for rec in recommendations:
        retailer, base_url = retailer_base.get(rec.category, ("Amazon", "https://www.amazon.com/s?k="))
        query = rec.title.replace(" ", "+")
        links.append(
            AffiliateLink(
                retailer=retailer,
                url=f"{base_url}{query}",
                title=rec.title,
            )
        )
    return links


@app.post("/analyze-room", response_model=AnalyzeRoomResponse)
async def analyze_room(file: UploadFile = File(...)) -> AnalyzeRoomResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        image = Image.open(BytesIO(content))
        image.load()
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Invalid image file.") from exc

    dominant_colors = extract_dominant_colors(image)
    style_tags = infer_style_tags(image, dominant_colors)
    recommendations = build_recommendations(style_tags, dominant_colors)
    affiliate_links = build_affiliate_links(recommendations)

    return AnalyzeRoomResponse(
        style_tags=style_tags,
        dominant_colors=dominant_colors,
        recommendations=recommendations,
        affiliate_links=affiliate_links,
    )
