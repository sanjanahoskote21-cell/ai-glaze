# AI-GLAZE: AI-Powered Product Catalog & Visual Search Engine

AI-GLAZE is an intelligent interior design product catalog and visual search system. Upload any furniture or room decor image to find visually matching products, filter by category and price tier, and discover budget-friendly alternatives using Google's SigLIP vision transformer and an embedded SQLite vector database.

---

## 📁 Project Structure

```
AI-GLAZE/
├── backend/
│   ├── main.py                    # FastAPI server (visual search, static images, CORS, products API)
│   └── ui.html                    # Visual Search Studio web interface
├── catalog_manager/
│   ├── __init__.py                # Package initializer
│   ├── catalog_manager.py         # CatalogManager class (SQLite vectors, cosine search, budget optimizer)
│   ├── build_index.py             # Batch SigLIP indexer (< 1 min for 200 items on CPU)
│   ├── test_catalog.py            # CLI visual search & alternatives test script
│   ├── collect_data.py            # Automated image download, square-padding & CSV import tool
│   ├── DATA_COLLECTION_GUIDE.md   # Complete guide on scraping, cleaning & deduplicating data
│   ├── requirements.txt           # Catalog manager dependencies
│   ├── data/
│   │   ├── catalog.csv            # Master product catalog (6 categories, 3 price tiers)
│   │   ├── import_template.csv    # Template for batch product additions
│   │   └── images/                # Product image repository
│   └── models/
│       ├── catalog.db             # SQLite vector database (768-dim float32 embeddings)
│       ├── catalog_index.npz      # Compressed NumPy vectors (fallback)
│       └── catalog_metadata.json  # Exported JSON metadata (fallback)
├── .gitignore                     # Git ignore file
└── README.md                      # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Launch the Visual Search Studio Web App
Start the FastAPI server:
```powershell
.\.venv\Scripts\uvicorn.exe backend.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
👉 **http://127.0.0.1:8000/**

- Drag and drop any furniture or room photo.
- View matching product cards with similarity percentages and price tags in ₹.
- Click **"💡 Cheaper Alternatives"** to see budget-friendly swaps with calculated savings!

---

### 2. Run the Visual Search CLI Test Script
Test visual similarity search with any image directly from the terminal:
```powershell
# Test with default sample image
.\.venv\Scripts\python.exe catalog_manager\test_catalog.py

# Test with your own furniture photo
.\.venv\Scripts\python.exe catalog_manager\test_catalog.py --image "path\to\your_photo.jpg" --category sofa --top_k 3
```

---

### 3. Add New Products & Rebuild the Vector Index
Add products and automatically square-pad images and update the vector database:
```powershell
# Add a single product from a URL
.\.venv\Scripts\python.exe catalog_manager\collect_data.py --add `
  --name "Velvet Scandinavian Armchair" `
  --category sofa `
  --tier mid `
  --price 16500 `
  --image "https://images.unsplash.com/photo-1580481077195-c3a8b2735741?w=500"

# Rebuild the SQLite vector index manually
.\.venv\Scripts\python.exe catalog_manager\build_index.py
```

---

## 🛠️ Core Technology Stack

- **Vision Transformer**: `google/siglip-base-patch16-224` (768-dimensional normalized embeddings)
- **Vector Database**: Embedded **SQLite** (`models/catalog.db`) with sub-millisecond dot-product cosine similarity
- **API Framework**: **FastAPI** + **Uvicorn** with CORS and static asset serving
- **Image Processing**: **Pillow (PIL)** with Lanczos aspect-ratio preserving square padding
- **Interactive UI**: Standalone responsive HTML5/CSS3/JavaScript web studio
