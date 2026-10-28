from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import re
import sys
import urllib.request

import pandas as pd
from PIL import Image

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_DIR = Path(__file__).resolve().parent
CATALOG_CSV = BASE_DIR / "data" / "catalog.csv"
IMAGES_DIR = BASE_DIR / "data" / "images"

VALID_CATEGORIES = {"flooring", "paint", "sofa", "bed", "table", "lighting"}
VALID_TIERS = {"budget", "mid", "luxury"}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.replace("₹", "INR ").encode("ascii", "replace").decode("ascii"))


def get_next_product_id(catalog_df: pd.DataFrame) -> str:
    """Finds the next sequential product ID (e.g. P021, P022)."""
    if catalog_df.empty or "id" not in catalog_df.columns:
        return "P001"

    existing_nums = []
    for pid in catalog_df["id"].dropna().astype(str):
        match = re.search(r"(\d+)", pid)
        if match:
            existing_nums.append(int(match.group(1)))

    next_num = max(existing_nums, default=0) + 1
    return f"P{next_num:03d}"


def clean_and_save_image(
    image_source: Image.Image | bytes | Path | str,
    output_path: Path,
    target_size: int = 384,
) -> bool:
    """
    Standardizes image: converts to RGB, resizes with aspect ratio preservation,
    centers onto a square white canvas, and saves as optimized JPEG.
    """
    try:
        if isinstance(image_source, Image.Image):
            img = image_source.convert("RGB")
        elif isinstance(image_source, bytes):
            with Image.open(BytesIO(image_source)) as opened:
                img = opened.convert("RGB")
        elif isinstance(image_source, (str, Path)):
            src_path = Path(image_source)
            if not src_path.is_file():
                safe_print(f"Error: Local file '{src_path}' not found.")
                return False
            with Image.open(src_path) as opened:
                img = opened.convert("RGB")
        else:
            safe_print(f"Error: Unsupported image type: {type(image_source)}")
            return False

        # Resize preserving aspect ratio
        img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

        # Center on a clean square white canvas
        canvas = Image.new("RGB", (target_size, target_size), (255, 255, 255))
        offset_x = (target_size - img.width) // 2
        offset_y = (target_size - img.height) // 2
        canvas.paste(img, (offset_x, offset_y))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, "JPEG", quality=92, optimize=True)
        return True

    except Exception as err:
        safe_print(f"Error processing image: {err}")
        return False


def download_and_clean_image(url: str, output_path: Path, target_size: int = 384) -> bool:
    """Downloads an image from URL and cleans/pads it."""
    safe_print(f"Downloading: {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            image_bytes = response.read()
        return clean_and_save_image(image_bytes, output_path, target_size=target_size)
    except Exception as err:
        safe_print(f"Failed to download '{url}': {err}")
        return False


def add_product(
    name: str,
    category: str,
    tier: str,
    price: float,
    unit: str,
    url: str,
    supplier: str,
    image_source: str | Path,
    rebuild: bool = True,
) -> str | None:
    """
    Adds a new product to catalog.csv, cleans its image, and optionally rebuilds SQLite index.
    image_source can be a local file path OR an http/https URL.
    """
    category = category.strip().lower()
    tier = tier.strip().lower()

    if category not in VALID_CATEGORIES:
        safe_print(f"Error: Invalid category '{category}'. Must be one of: {sorted(VALID_CATEGORIES)}")
        return None

    if tier not in VALID_TIERS:
        safe_print(f"Error: Invalid tier '{tier}'. Must be one of: {sorted(VALID_TIERS)}")
        return None

    if price < 0:
        safe_print("Error: Price cannot be negative.")
        return None

    # Load or initialize catalog DataFrame
    if CATALOG_CSV.exists():
        df = pd.read_csv(CATALOG_CSV)
    else:
        df = pd.DataFrame(columns=[
            "id", "name", "category", "tier", "price", "unit", "url", "supplier", "image_path"
        ])

    product_id = get_next_product_id(df)
    image_filename = f"{product_id.lower()}_{category}.jpg"
    target_image_path = IMAGES_DIR / image_filename
    relative_image_path = f"data/images/{image_filename}"

    # Handle image acquisition
    is_url = str(image_source).startswith(("http://", "https://"))
    if is_url:
        success = download_and_clean_image(str(image_source), target_image_path)
    else:
        success = clean_and_save_image(image_source, target_image_path)

    if not success:
        safe_print(f"Could not save image for product {product_id}. Aborting product add.")
        return None

    # Append to catalog DataFrame
    new_row = {
        "id": product_id,
        "name": str(name).strip(),
        "category": category,
        "tier": tier,
        "price": float(price),
        "unit": str(unit).strip(),
        "url": str(url).strip(),
        "supplier": str(supplier).strip(),
        "image_path": relative_image_path,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CATALOG_CSV, index=False)
    safe_print(f"[OK] Added product {product_id}: '{name}' ({category}, tier: {tier}, price: ₹{price:,.2f})")

    if rebuild:
        safe_print("Rebuilding SQLite index...")
        from catalog_manager.build_index import build_index
        build_index()

    return product_id


def import_csv(csv_path: str | Path, rebuild: bool = True):
    """
    Imports multiple products from a CSV file.
    Expected columns: name, category, tier, price, unit, url, supplier, image
    (where 'image' can be a URL or local file path).
    """
    csv_file = Path(csv_path)
    if not csv_file.is_file():
        safe_print(f"Error: CSV file not found at '{csv_file}'.")
        return

    import_df = pd.read_csv(csv_file)
    safe_print(f"Found {len(import_df)} rows in '{csv_file.name}' to import.")

    added = 0
    for _, row in import_df.iterrows():
        pid = add_product(
            name=row["name"],
            category=row["category"],
            tier=row.get("tier", "mid"),
            price=float(row.get("price", 0)),
            unit=row.get("unit", "piece"),
            url=row.get("url", ""),
            supplier=row.get("supplier", "Imported"),
            image_source=row["image"],
            rebuild=False,  # Rebuild once at the end
        )
        if pid:
            added += 1

    safe_print(f"\nImported {added}/{len(import_df)} products successfully.")

    if rebuild and added > 0:
        safe_print("Updating SQLite vector index...")
        from catalog_manager.build_index import build_index
        build_index()


def main():
    parser = argparse.ArgumentParser(
        description="AI-GLAZE Catalog Data Collection & Image Cleaning Tool"
    )
    parser.add_argument(
        "--import-csv",
        type=str,
        default=None,
        help="Path to an external CSV containing products to batch import",
    )
    parser.add_argument(
        "--add",
        action="store_true",
        help="Add a single product via CLI arguments",
    )
    parser.add_argument("--name", type=str, help="Product name")
    parser.add_argument("--category", type=str, help="Product category (sofa, bed, table, lighting, flooring, paint)")
    parser.add_argument("--tier", type=str, default="mid", help="Price tier (budget, mid, luxury)")
    parser.add_argument("--price", type=float, help="Product price")
    parser.add_argument("--unit", type=str, default="piece", help="Unit (piece, sqft, litre, etc.)")
    parser.add_argument("--url", type=str, default="", help="Product supplier URL")
    parser.add_argument("--supplier", type=str, default="Supplier", help="Supplier or brand name")
    parser.add_argument("--image", type=str, help="Image URL or local image file path")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        default=True,
        help="Rebuild SQLite vector database after adding products",
    )

    args = parser.parse_args()

    if args.import_csv:
        import_csv(args.import_csv, rebuild=args.rebuild)
    elif args.add:
        if not args.name or not args.category or args.price is None or not args.image:
            safe_print("Error: When using --add, you must provide --name, --category, --price, and --image.")
            return

        add_product(
            name=args.name,
            category=args.category,
            tier=args.tier,
            price=args.price,
            unit=args.unit,
            url=args.url,
            supplier=args.supplier,
            image_source=args.image,
            rebuild=args.rebuild,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
