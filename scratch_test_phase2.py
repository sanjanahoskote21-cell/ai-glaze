from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
print("1. Testing /health:", client.get("/health").json())
print("2. Testing /categories:", client.get("/categories").json())

prods = client.get("/products?category=sofa").json()
print(f"3. Testing /products (sofas): Found {prods['count']} sofas.")
for p in prods['products']:
    print(f"   - {p['name']} | ₹{p['price']:,} | Supplier: {p['supplier']}")

print("4. Testing /visual-search with real_room.jpeg:")
with open("real_room.jpeg", "rb") as f:
    res = client.post("/visual-search", files={"image": ("real_room.jpeg", f, "image/jpeg")}, data={"category": "sofa", "top_k": 3})

search_res = res.json()
print("   Success:", search_res.get("success"))
for item in search_res.get("results", []):
    print(f"   -> [{item['id']}] {item['name']} | ₹{item['price']:,} | Sim: {item['similarity']:.4f} | {item['supplier']}")
