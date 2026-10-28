import json
from pathlib import Path
import sqlite3
import time

import numpy as np
import pandas as pd
from PIL import Image
import torch
from transformers import AutoModel, AutoProcessor

# ---------------- CONFIGURATION ----------------

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.csv"
OUTPUT_DIR = BASE_DIR / "models"

DB_PATH = OUTPUT_DIR / "catalog.db"
INDEX_PATH = OUTPUT_DIR / "catalog_index.npz"
METADATA_PATH = OUTPUT_DIR / "catalog_metadata.json"

MODEL_NAME = "google/siglip-base-patch16-224"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 16  # Batch processing for fast indexing (< 1 min for 200 items on CPU)


# ---------------- LOAD MODEL ----------------

def load_model():
    print(f"Loading SigLIP ({MODEL_NAME}) on {DEVICE}...")
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.to(DEVICE)
    model.eval()
    print("SigLIP model ready.")
    return processor, model


# ---------------- BATCH IMAGE EMBEDDING ----------------

def get_batch_embeddings(images: list[Image.Image], processor, model) -> np.ndarray:
    """
    Computes normalized 768-dimensional float32 SigLIP embeddings
    for a batch of PIL images using inference_mode for maximum speed.
    """
    inputs = processor(images=images, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.inference_mode():
        features = model.get_image_features(**inputs)

        if hasattr(features, "pooler_output"):
            features = features.pooler_output
        elif isinstance(features, tuple):
            features = features[0]
        elif hasattr(features, "last_hidden_state"):
            features = features.last_hidden_state

        if features.ndim == 3:
            features = features.mean(dim=1)

        features = features.reshape(features.shape[0], -1).float()

        # L2-normalize vectors so dot product equals cosine similarity
        norms = torch.norm(features, p=2, dim=-1, keepdim=True).clamp(min=1e-12)
        features = features / norms

    return features.cpu().numpy().astype(np.float32)


# ---------------- SQLITE VECTOR DB SETUP ----------------

def init_sqlite_db(db_path: Path) -> sqlite3.Connection:
    """
    Initializes SQLite database and creates the products table with indexes.
    """
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            tier TEXT NOT NULL,
            price REAL NOT NULL,
            unit TEXT NOT NULL,
            url TEXT,
            supplier TEXT,
            image_path TEXT NOT NULL,
            embedding BLOB NOT NULL
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tier ON products(tier);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON products(price);")
    conn.commit()

    return conn


# ---------------- BUILD INDEX ----------------

def build_index(batch_size: int = BATCH_SIZE):
    start_time = time.perf_counter()

    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog CSV not found: {CATALOG_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    catalog = pd.read_csv(CATALOG_PATH)
    required_cols = {
        "id", "name", "category", "tier", "price",
        "unit", "url", "supplier", "image_path"
    }

    missing = required_cols - set(catalog.columns)
    if missing:
        raise ValueError(f"Missing required catalog columns: {sorted(missing)}")

    print(f"\nFound {len(catalog)} products in {CATALOG_PATH.name}")

    processor, model = load_model()

    # Filter and preload valid records
    valid_items = []
    for _, row in catalog.iterrows():
        rel_path = str(row["image_path"]).strip()
        if not rel_path or rel_path.lower() == "nan":
            print(f"Skipping {row['id']}: missing image_path.")
            continue

        full_img_path = (BASE_DIR / rel_path).resolve()
        if not full_img_path.is_file():
            print(f"Skipping {row['id']}: image not found ({full_img_path}).")
            continue

        valid_items.append({
            "row": row,
            "full_path": full_img_path,
            "rel_path": rel_path,
        })

    if not valid_items:
        print("No valid products with images found.")
        return

    print(f"Processing {len(valid_items)} images in batches of {batch_size}...")

    all_embeddings = []
    all_metadata = []
    db_records = []

    # Batch process images
    for i in range(0, len(valid_items), batch_size):
        chunk = valid_items[i : i + batch_size]
        images = []
        clean_chunk = []

        for item in chunk:
            try:
                with Image.open(item["full_path"]) as img:
                    images.append(img.convert("RGB"))
                    clean_chunk.append(item)
            except Exception as err:
                print(f"Error opening image {item['full_path']}: {err}")

        if not images:
            continue

        batch_vectors = get_batch_embeddings(images, processor, model)

        for item, vec in zip(clean_chunk, batch_vectors):
            row = item["row"]
            prod_id = str(row["id"])
            name = str(row["name"])
            category = str(row["category"]).strip().lower()
            tier = str(row["tier"]).strip().lower()
            price = float(row["price"])
            unit = str(row["unit"])
            url = str(row["url"]) if pd.notna(row["url"]) else ""
            supplier = str(row["supplier"]) if pd.notna(row["supplier"]) else ""
            rel_path = item["rel_path"]

            all_embeddings.append(vec)
            all_metadata.append({
                "id": prod_id,
                "name": name,
                "category": category,
                "tier": tier,
                "price": price,
                "unit": unit,
                "url": url,
                "supplier": supplier,
                "image_path": rel_path,
            })

            # Store float32 numpy array as raw binary BLOB in SQLite
            db_records.append((
                prod_id,
                name,
                category,
                tier,
                price,
                unit,
                url,
                supplier,
                rel_path,
                vec.tobytes(),
            ))

        print(f"Indexed batch: {min(i + batch_size, len(valid_items))}/{len(valid_items)}")

    # 1. Save to SQLite Vector Database
    conn = init_sqlite_db(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO products (id, name, category, tier, price, unit, url, supplier, image_path, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, db_records)
    conn.commit()
    conn.close()
    print(f"\n[OK] SQLite Vector DB built: {DB_PATH} ({len(db_records)} records)")

    # 2. Preserve NPZ and JSON files for backward compatibility
    np.savez_compressed(
        INDEX_PATH,
        embeddings=np.asarray(all_embeddings, dtype=np.float32)
    )
    with METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2)

    elapsed = time.perf_counter() - start_time
    print(f"[OK] NPZ Index: {INDEX_PATH}")
    print(f"[OK] Metadata JSON: {METADATA_PATH}")
    print(f"Total indexing time: {elapsed:.2f} seconds ({len(db_records)} products).")


if __name__ == "__main__":
    build_index()