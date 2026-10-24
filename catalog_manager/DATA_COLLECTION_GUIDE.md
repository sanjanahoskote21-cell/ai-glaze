# AI-GLAZE: Real Catalog Data Collection & Cleaning Guide

This guide explains how to quickly collect, clean, standardize, and ingest real furniture and interior design products into the AI-GLAZE catalog.

---

## 1. Catalog CSV Schema Standard

Your `catalog.csv` must follow this schema:

| Column | Type | Allowed Values / Format | Example |
| :--- | :--- | :--- | :--- |
| `id` | String | Unique alphanumeric ID | `P101` |
| `name` | String | Clear product title | `Stockholm 3-Seat Leather Sofa` |
| `category`| String | `flooring`, `paint`, `sofa`, `bed`, `table`, `lighting` | `sofa` |
| `tier` | String | `budget`, `mid`, `luxury` | `mid` |
| `price` | Float | Numeric price $\ge 0$ | `24999.00` |
| `unit` | String | `piece`, `sqft`, `metre`, `litre`, etc. | `piece` |
| `url` | String | Product page link | `https://supplier.com/item` |
| `supplier`| String | Brand or retailer name | `IKEA`, `Asian Paints` |
| `image_path`| String | Relative path from `catalog_manager` | `data/images/P101.jpg` |

---

## 2. Fast Data Collection Strategies

### Method A: Retailer Public Catalog APIs (Fastest)
Many modern e-commerce platforms (Shopify stores, headless furniture sites) have open JSON search APIs:
```python
import requests
import pandas as pd

# Example: Scraping a Shopify-based furniture retailer catalog
url = "https://example-furniture-store.com/products.json?limit=250"
response = requests.get(url).json()

products = []
for item in response["products"]:
    variant = item["variants"][0]
    image_url = item["images"][0]["src"] if item["images"] else ""
    products.append({
        "id": f"P{item['id']}",
        "name": item["title"],
        "price": float(variant["price"]),
        "url": f"https://example-furniture-store.com/products/{item['handle']}",
        "raw_image_url": image_url,
    })
```

### Method B: Headless Web Scraping (Playwright / BeautifulSoup)
For sites without JSON endpoints, use Playwright to extract product cards:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://retailer.com/sofas")
    
    cards = page.query_selector_all(".product-card")
    for card in cards:
        name = card.query_selector(".title").inner_text()
        price = card.query_selector(".price").inner_text()
        img_src = card.query_selector("img").get_attribute("src")
        # Save to raw list...
    browser.close()
```

---

## 3. Automated Image Cleaning & Standardization

SigLIP performs best when product images are clean, centered, and have a consistent aspect ratio.

### Pipeline: Aspect-Ratio Square Padding
Never stretch images. Instead, pad them to a square on a clean neutral/white background:

```python
from pathlib import Path
from PIL import Image, ImageOps

def clean_and_save_image(input_path: Path, output_path: Path, target_size: int = 384):
    """
    Loads any image format (WEBP, PNG, HEIC, JPG), converts to RGB,
    pads to a square with a white background, and saves as optimized JPEG.
    """
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        
        # Calculate aspect ratio preserving resize
        img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Create square canvas
        canvas = Image.new("RGB", (target_size, target_size), (255, 255, 255))
        
        # Center image on canvas
        offset_x = (target_size - img.width) // 2
        offset_y = (target_size - img.height) // 2
        canvas.paste(img, (offset_x, offset_y))
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, "JPEG", quality=90)
```

---

## 4. Deduplication via Visual Similarity

To prevent duplicate products from polluting the visual index:
1. When downloading images, compute an MD5 or perceptual hash (`imagehash.phash`).
2. Alternatively, use SigLIP embeddings: if cosine similarity between two catalog images is $> 0.98$ and they share the same category, flag them as duplicates.

---

## 5. Automated Validation & Index Rebuild

Before rebuilding your SQLite vector database, run this fast integrity check:

```python
import pandas as pd
from pathlib import Path

def validate_catalog(csv_path: Path, images_dir: Path):
    df = pd.read_csv(csv_path)
    
    # 1. Check for duplicates in ID
    assert df["id"].is_unique, f"Duplicate product IDs found!"
    
    # 2. Check required categories
    valid_categories = {"flooring", "paint", "sofa", "bed", "table", "lighting"}
    invalid_cats = set(df["category"].str.lower()) - valid_categories
    assert not invalid_cats, f"Invalid categories: {invalid_cats}"
    
    # 3. Check price validity
    assert (df["price"] >= 0).all(), "Negative prices detected!"
    
    # 4. Check that all referenced images exist on disk
    for path_str in df["image_path"]:
        full_path = images_dir.parent / path_str
        assert full_path.is_file(), f"Missing image file: {full_path}"

    print(f"Catalog validation passed! {len(df)} products ready to index.")

if __name__ == "__main__":
    validate_catalog(Path("data/catalog.csv"), Path("data/images"))
```

Once validated, run:
```powershell
python build_index.py
```
Your SQLite vector database (`models/catalog.db`) will be updated automatically in under 1 minute.
