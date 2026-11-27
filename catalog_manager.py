"""
catalog_manager.py - Lead: Member 3 (Data, Product Catalog & Supplier Lead)
Interface for AI-GLAZE Master Orchestrator (app.py) & Vision Engine
Provides real Indian market catalog records, supplier lookups, and visual alternatives.
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent

# Connect to the full CatalogManager in catalog_manager package
from catalog_manager.catalog_manager import CatalogManager

_catalog = None

def get_catalog() -> CatalogManager:
    global _catalog
    if _catalog is None:
        _catalog = CatalogManager()
    return _catalog

def search_by_category(category: str):
    """Returns all products in a given category."""
    cm = get_catalog()
    cat = category.strip().lower()
    return [
        dict(p)
        for p in cm.metadata
        if str(p.get("category", "")).strip().lower() == cat
    ]

def filter_by_budget_tier(tier: str):
    """Returns products matching a budget tier (budget, mid, luxury)."""
    cm = get_catalog()
    t = tier.strip().lower()
    return [
        dict(p)
        for p in cm.metadata
        if str(p.get("tier", "")).strip().lower() == t
    ]

def get_cheaper_alternative(item_id_or_dict, cheaper_than: bool = True, top_k: int = 3):
    """Finds visually similar cheaper alternative products."""
    cm = get_catalog()
    if isinstance(item_id_or_dict, dict):
        item_id = str(item_id_or_dict.get("id"))
    else:
        item_id = str(item_id_or_dict)
    
    try:
        return cm.get_alternatives(item_id=item_id, cheaper_than=cheaper_than, top_k=top_k)
    except Exception as e:
        print(f"Alternative lookup note: {e}")
        return []

if __name__ == "__main__":
    cm = get_catalog()
    print(f"Catalog loaded with {len(cm.metadata)} products.")
    sofas = search_by_category("sofa")
    print(f"Found {len(sofas)} sofas in Indian market catalog.")
    for s in sofas:
        print(f"  - {s['name']}: ₹{s['price']:,} (Supplier: {s['supplier']})")
