from io import BytesIO
from pathlib import Path
import sys

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="AI-GLAZE API")

# Main project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow Python to import the catalog manager
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from catalog_manager.catalog_manager import CatalogManager

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount catalog images statically
STATIC_IMAGES_DIR = PROJECT_ROOT / "catalog_manager" / "data" / "images"
if STATIC_IMAGES_DIR.exists():
    app.mount(
        "/static/images",
        StaticFiles(directory=str(STATIC_IMAGES_DIR)),
        name="static_images",
    )

_catalog = None


def get_catalog() -> CatalogManager:
    global _catalog

    if _catalog is None:
        _catalog = CatalogManager()

    return _catalog


def format_product(product: dict) -> dict:
    """Ensure product dictionary has a web-accessible image_url."""
    item = dict(product)
    image_path = item.get("image_path", "")
    if image_path:
        filename = Path(image_path).name
        item["image_url"] = f"/static/images/{filename}"
    else:
        item["image_url"] = None
    return item


UI_FILE = Path(__file__).resolve().parent / "ui.html"


@app.get("/", response_class=FileResponse)
def home():
    if UI_FILE.is_file():
        return FileResponse(UI_FILE)
    return {"message": "AI-GLAZE backend is running!"}


@app.get("/ui", response_class=FileResponse)
def ui_page():
    if UI_FILE.is_file():
        return FileResponse(UI_FILE)
    return {"message": "UI file not found"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/categories")
def get_categories():
    catalog = get_catalog()
    categories = sorted(
        {
            str(prod.get("category", "")).strip().lower()
            for prod in catalog.metadata
            if prod.get("category")
        }
    )
    return {"categories": categories}


@app.get("/products")
def list_products(
    category: str | None = Query(None, description="Filter by category"),
    tier: str | None = Query(None, description="Filter by tier (budget, mid, luxury)"),
    max_price: float | None = Query(None, description="Maximum product price"),
    limit: int = Query(50, ge=1, le=100, description="Max products to return"),
):
    if max_price is not None and max_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum price cannot be negative.",
        )

    catalog = get_catalog()
    filtered = []

    for prod in catalog.metadata:
        prod_cat = str(prod.get("category", "")).strip().lower()
        prod_tier = str(prod.get("tier", "")).strip().lower()
        try:
            prod_price = float(prod.get("price", 0))
        except (ValueError, TypeError):
            continue

        if category is not None and prod_cat != category.strip().lower():
            continue

        if tier is not None and prod_tier != tier.strip().lower():
            continue

        if max_price is not None and prod_price > max_price:
            continue

        filtered.append(format_product(prod))

    return {
        "count": len(filtered[:limit]),
        "total": len(filtered),
        "products": filtered[:limit],
    }


@app.get("/products/{product_id}")
def get_product_details(product_id: str):
    catalog = get_catalog()
    product = catalog.get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{product_id}' was not found.",
        )
    return format_product(product)


@app.get("/products/{product_id}/alternatives")
def get_product_alternatives(
    product_id: str,
    cheaper_than: bool = Query(True, description="Only find cheaper alternatives"),
    top_k: int = Query(5, ge=1, le=20, description="Max alternatives to return"),
):
    catalog = get_catalog()
    try:
        alternatives = catalog.get_alternatives(
            item_id=product_id,
            cheaper_than=cheaper_than,
            top_k=top_k,
        )
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))

    return {
        "product_id": product_id,
        "cheaper_than": cheaper_than,
        "count": len(alternatives),
        "alternatives": [format_product(item) for item in alternatives],
    }


@app.post("/visual-search")
async def visual_search(
    image: UploadFile = File(...),
    category: str | None = Form(None),
    max_price: float | None = Form(None),
    tier: str | None = Form(None),
    top_k: int = Form(5),
):
    # Sanitize Swagger UI dummy placeholders ('string', empty, 0)
    if category and category.strip().lower() in ("string", ""):
        category = None
    if tier and tier.strip().lower() in ("string", ""):
        tier = None
    if max_price is not None and max_price <= 0:
        max_price = None

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image.",
        )

    if max_price is not None and max_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum price cannot be negative.",
        )

    if not 1 <= top_k <= 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20.",
        )

    try:
        image_bytes = await image.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded image is empty.",
            )

        with Image.open(BytesIO(image_bytes)) as uploaded_image:
            room_image = uploaded_image.convert("RGB")

        catalog = get_catalog()

        results = catalog.search(
            crop_image=room_image,
            category=category,
            top_k=top_k,
            tier=tier,
            max_price=max_price,
        )

        formatted_results = [format_product(item) for item in results]

        return {
            "success": True,
            "count": len(formatted_results),
            "filters": {
                "category": category,
                "max_price": max_price,
                "tier": tier,
                "top_k": top_k,
            },
            "results": formatted_results,
        }

    except HTTPException:
        raise

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Could not read the image. Please upload a valid image.",
        )

    except Exception as error:
        print(f"Visual search error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Visual search failed. Check the backend terminal.",
        )

    finally:
        await image.close()
