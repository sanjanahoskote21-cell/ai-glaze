from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image
import torch
from transformers import AutoModel, AutoProcessor

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CATALOG_CSV = BASE_DIR / "data" / "catalog.csv"
DB_PATH = BASE_DIR / "models" / "catalog.db"
INDEX_FILE = BASE_DIR / "models" / "catalog_index.npz"
METADATA_FILE = BASE_DIR / "models" / "catalog_metadata.json"

MODEL_NAME = "google/siglip-base-patch16-224"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------------------------------------------------
# CATALOG MANAGER
# ---------------------------------------------------------

class CatalogManager:
    """
    AI-GLAZE Visual Product Catalog Manager.

    Features:
    - SQLite vector store backing with sub-millisecond query execution.
    - Normalized SigLIP cosine similarity matching.
    - Attribute filtering (category, tier, max_price).
    - Budget Optimizer: Finds visually similar alternative products at a lower price.
    """

    def __init__(
        self,
        db_path: str | Path = DB_PATH,
        catalog_csv: str | Path = CATALOG_CSV,
        index_file: str | Path = INDEX_FILE,
        metadata_file: str | Path = METADATA_FILE,
        model_name: str = MODEL_NAME,
        device: str | None = None,
    ):
        self.db_path = Path(db_path)
        self.catalog_csv = Path(catalog_csv)
        self.index_file = Path(index_file)
        self.metadata_file = Path(metadata_file)

        self.model_name = model_name
        self.device = device or DEVICE

        self.processor = None
        self.model = None

        self.metadata: list[dict[str, Any]] = []
        self.embeddings: np.ndarray = np.empty((0, 768), dtype=np.float32)

        # Load catalog from SQLite (primary) or fallback to NPZ/JSON
        self._load_data()

    # -----------------------------------------------------
    # DATA LOADING (SQLite Primary, NPZ Fallback)
    # -----------------------------------------------------

    def _load_data(self) -> None:
        if self.db_path.exists():
            self._load_from_sqlite()
        elif self.index_file.exists() and self.metadata_file.exists():
            self._load_from_npz()
        else:
            raise FileNotFoundError(
                f"Neither SQLite DB ({self.db_path}) nor NPZ index ({self.index_file}) found. "
                "Please run build_index.py first."
            )

    def _load_from_sqlite(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, category, tier, price, unit, url, supplier, image_path, embedding
            FROM products
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            raise ValueError(f"SQLite database {self.db_path} contains no products.")

        metadata_list = []
        embedding_list = []

        for row in rows:
            prod_id, name, category, tier, price, unit, url, supplier, image_path, blob = row
            metadata_list.append({
                "id": str(prod_id),
                "name": str(name),
                "category": str(category),
                "tier": str(tier),
                "price": float(price),
                "unit": str(unit),
                "url": str(url) if url else "",
                "supplier": str(supplier) if supplier else "",
                "image_path": str(image_path),
            })
            vec = np.frombuffer(blob, dtype=np.float32)
            embedding_list.append(vec)

        self.metadata = metadata_list
        self.embeddings = np.asarray(embedding_list, dtype=np.float32)

        # Ensure unit normalization for cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / np.maximum(norms, 1e-12)

        print(
            f"Loaded {len(self.metadata)} products from SQLite ({self.db_path.name}) "
            f"with embedding dim {self.embeddings.shape[1]}."
        )

    def _load_from_npz(self) -> None:
        index_data = np.load(self.index_file)
        self.embeddings = np.asarray(index_data["embeddings"], dtype=np.float32)

        with open(self.metadata_file, "r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / np.maximum(norms, 1e-12)

        print(
            f"Loaded {len(self.metadata)} products from NPZ fallback "
            f"with embedding dim {self.embeddings.shape[1]}."
        )

    # -----------------------------------------------------
    # LAZY MODEL LOADING
    # -----------------------------------------------------

    def _load_model(self) -> None:
        if self.model is not None and self.processor is not None:
            return

        print(f"Loading SigLIP on {self.device}...")
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        print("SigLIP loaded successfully.")

    # -----------------------------------------------------
    # QUERY EMBEDDING
    # -----------------------------------------------------

    def _image_embedding(self, image: str | Path | Image.Image) -> np.ndarray:
        self._load_model()

        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Query image not found: {image_path}")
            image = Image.open(image_path).convert("RGB")
        elif isinstance(image, Image.Image):
            image = image.convert("RGB")
        else:
            raise TypeError("Image must be a file path or PIL Image.")

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.inference_mode():
            outputs = self.model.get_image_features(**inputs)

            if hasattr(outputs, "pooler_output"):
                outputs = outputs.pooler_output
            elif isinstance(outputs, tuple):
                outputs = outputs[0]
            elif hasattr(outputs, "last_hidden_state"):
                outputs = outputs.last_hidden_state

            if outputs.ndim == 3:
                outputs = outputs.mean(dim=1)

            outputs = outputs.reshape(outputs.shape[0], -1).float()

            embedding = outputs[0].detach().cpu().numpy().astype(np.float32)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

        return embedding

    # -----------------------------------------------------
    # VISUAL PRODUCT SEARCH
    # -----------------------------------------------------

    def search(
        self,
        crop_image: str | Path | Image.Image,
        category: str | None = None,
        top_k: int = 5,
        tier: str | None = None,
        max_price: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for visually similar products using cosine similarity.

        Parameters
        ----------
        crop_image:
            File path or PIL Image of query object.
        category:
            Optional category filter (sofa, bed, table, lighting, flooring, paint).
        top_k:
            Number of top matches to return.
        tier:
            Optional tier filter (budget, mid, luxury).
        max_price:
            Optional upper price limit.

        Returns
        -------
        List of product dictionaries sorted by cosine similarity.
        """
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        if max_price is not None and max_price < 0:
            raise ValueError("max_price cannot be negative.")

        query_embedding = self._image_embedding(crop_image)

        # Cosine similarity via dot product (both vectors are normalized)
        similarities = self.embeddings @ query_embedding

        results = []
        for index, product in enumerate(self.metadata):
            product_category = str(product.get("category", "")).strip().lower()
            product_tier = str(product.get("tier", "")).strip().lower()

            try:
                product_price = float(product.get("price", 0))
            except (TypeError, ValueError):
                continue

            if category is not None and product_category != category.strip().lower():
                continue

            if tier is not None and product_tier != tier.strip().lower():
                continue

            if max_price is not None and product_price > max_price:
                continue

            result = dict(product)
            result["price"] = product_price
            result["similarity"] = float(similarities[index])
            results.append(result)

        # Rank by highest similarity score
        results.sort(key=lambda item: item["similarity"], reverse=True)
        return results[:top_k]

    # -----------------------------------------------------
    # PRODUCT LOOKUP
    # -----------------------------------------------------

    def get_product(self, item_id: str) -> dict[str, Any] | None:
        item_id = str(item_id)
        for product in self.metadata:
            if str(product.get("id")) == item_id:
                return dict(product)
        return None

    def _get_product_embedding(self, item_id: str) -> np.ndarray | None:
        item_id = str(item_id)
        for index, product in enumerate(self.metadata):
            if str(product.get("id")) == item_id:
                return self.embeddings[index]
        return None

    # -----------------------------------------------------
    # BUDGET OPTIMIZER: CHEAPER VISUALLY SIMILAR ALTERNATIVES
    # -----------------------------------------------------

    def get_alternatives(
        self,
        item_id: str,
        cheaper_than: bool = True,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Finds visually similar items at a lower price (for the budget optimizer).

        Computes cosine similarity between the selected product's visual embedding
        and candidate products in the same category.

        Parameters
        ----------
        item_id:
            ID of the target product.
        cheaper_than:
            If True, only consider products costing strictly less than the target item.
        top_k:
            Number of alternatives to return.

        Returns
        -------
        List of alternative products ranked by visual similarity to the target product,
        with price savings and similarity scores.
        """
        selected = self.get_product(item_id)
        if selected is None:
            raise ValueError(f"Product ID '{item_id}' was not found in catalog.")

        selected_vec = self._get_product_embedding(item_id)
        if selected_vec is None:
            raise ValueError(f"Embedding for product '{item_id}' not found.")

        selected_category = str(selected.get("category", "")).strip().lower()
        selected_price = float(selected.get("price", 0))

        # Cosine similarity of all catalog items against the selected product
        similarities = self.embeddings @ selected_vec

        candidates = []
        for index, product in enumerate(self.metadata):
            if str(product.get("id")) == str(item_id):
                continue

            prod_category = str(product.get("category", "")).strip().lower()
            if prod_category != selected_category:
                continue

            try:
                prod_price = float(product.get("price", 0))
            except (TypeError, ValueError):
                continue

            # Budget optimization filter
            if cheaper_than and prod_price >= selected_price:
                continue

            item = dict(product)
            item["price"] = prod_price
            item["similarity"] = float(similarities[index])
            item["price_savings"] = round(selected_price - prod_price, 2)
            item["savings_percent"] = round(
                ((selected_price - prod_price) / max(selected_price, 1e-6)) * 100, 1
            ) if selected_price > 0 else 0.0

            candidates.append(item)

        # Rank candidates by visual similarity to the target product
        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        return candidates[:top_k]


# ---------------------------------------------------------
# CLI TEST
# ---------------------------------------------------------

if __name__ == "__main__":
    catalog = CatalogManager()
    print("\n=== AI-GLAZE Catalog Manager Status ===")
    print(f"Total Products Loaded: {len(catalog.metadata)}")
    print(f"Embedding Shape: {catalog.embeddings.shape}")
    categories = sorted({str(p.get("category")) for p in catalog.metadata})
    print(f"Available Categories: {categories}")
    print("=== Ready ===")