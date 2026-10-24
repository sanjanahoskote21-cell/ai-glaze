from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from catalog_manager.catalog_manager import CatalogManager


def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        clean = text.replace("₹", "INR ")
        try:
            print(clean)
        except UnicodeEncodeError:
            print(clean.encode("ascii", "replace").decode("ascii"))


def print_item(label: str, item: dict, extra: str = ""):
    price_val = item.get("price", 0)
    sim = item.get("similarity", 0.0)
    tier = item.get("tier", "N/A")
    cat = item.get("category", "N/A")
    msg = f"{label} [{item.get('id')}] {item.get('name')} | Cat: {cat} | Tier: {tier} | Price: ₹{price_val:,.2f} | Similarity: {sim:.4f}"
    if extra:
        msg += f" | {extra}"
    safe_print(msg)


def main():
    parser = argparse.ArgumentParser(
        description="AI-GLAZE Catalog & Visual Search Test Script"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to query furniture image (defaults to sample sofa)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Optional category filter (sofa, bed, table, lighting, flooring, paint)",
    )
    parser.add_argument(
        "--tier",
        type=str,
        default=None,
        help="Optional price tier (budget, mid, luxury)",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="Number of results to return",
    )
    args = parser.parse_args()

    default_image = (
        Path(__file__).resolve().parent / "data" / "images" / "sofa1.jpg"
    )
    query_image = Path(args.image) if args.image else default_image

    if not query_image.exists():
        safe_print(f"Error: Query image not found at '{query_image}'.")
        safe_print("Please provide a valid image path via --image.")
        return

    safe_print("==================================================")
    safe_print("      AI-GLAZE Visual Search & Catalog Test       ")
    safe_print("==================================================")

    # 1. Initialize Catalog Manager (loads SQLite database)
    catalog = CatalogManager()

    safe_print(f"\n[Test 1] Visual Product Search")
    safe_print(f"Query Image : {query_image.name}")
    safe_print(f"Filters     : Category={args.category}, Tier={args.tier}, Top_K={args.top_k}")
    safe_print("Computing SigLIP visual embedding and running cosine search...\n")

    results = catalog.search(
        crop_image=query_image,
        category=args.category,
        top_k=args.top_k,
        tier=args.tier,
    )

    if not results:
        safe_print("No matching products found for the given criteria.")
    else:
        for idx, item in enumerate(results, start=1):
            print_item(f"  {idx}.", item)

    # 2. Test Budget Optimizer (Visually Similar Cheaper Alternatives)
    safe_print("\n--------------------------------------------------")
    safe_print("[Test 2] Budget Optimizer: Visually Similar Cheaper Alternatives")

    # Pick a mid or luxury item to demonstrate finding cheaper alternatives
    test_target_id = "P008"  # Modern Three Seater Sofa (₹18,000)
    target_product = catalog.get_product(test_target_id)

    if target_product:
        orig_price = target_product.get("price", 0)
        safe_print(
            f"Target Item : [{target_product['id']}] {target_product['name']} "
            f"(Price: ₹{orig_price:,.2f}, Tier: {target_product.get('tier')})"
        )
        safe_print("Finding cheaper alternatives in the same category ranked by visual similarity...\n")

        alternatives = catalog.get_alternatives(
            item_id=test_target_id,
            cheaper_than=True,
            top_k=3,
        )

        if not alternatives:
            safe_print("No cheaper alternatives found.")
        else:
            for idx, alt in enumerate(alternatives, start=1):
                savings = alt.get("price_savings", 0)
                pct = alt.get("savings_percent", 0)
                extra_info = f"Savings: ₹{savings:,.2f} ({pct}%)"
                print_item(f"  Alt {idx}.", alt, extra=extra_info)

    safe_print("\n==================================================")
    safe_print("               All Tests Completed!               ")
    safe_print("==================================================")


if __name__ == "__main__":
    main()