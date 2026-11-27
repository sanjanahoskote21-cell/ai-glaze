"""
app.py - Lead: Member 1 (Technical Lead & System Architect)
AI-GLAZE Master Orchestrator (Customized for Indian Market - INR ₹)
Glues together:
  - vision_engine.py   (Member 1 - CV, Depth, Redesign, Inpaint, YOLO)
  - catalog_manager.py (Member 3 - Product & Material Database)
  - cost_engine.py     (Member 4 - Surface Area Math & BoQ Optimizer)
"""

import os
import json
from vision_engine import run_full_vision_pipeline

# Safely import Teammate B's module (Catalog Manager)
try:
    from catalog_manager import search_by_category, filter_by_budget_tier, get_cheaper_alternative
except ImportError:
    def search_by_category(cat): return []
    def filter_by_budget_tier(tier): return []
    def get_cheaper_alternative(item): return None

# Safely import Teammate C's module (Cost Engine)
try:
    from cost_engine import calculate_flooring_cost, calculate_paint_cost, generate_full_boq
except ImportError:
    def calculate_flooring_cost(l, w, r): return {"total_cost": round(l * w * r * 1.10, 2)}
    def calculate_paint_cost(p, h, r): return {"total_cost": round(p * h * r * 2, 2)}
    def generate_full_boq(f_sqft, f_rate, w_sqft, p_rate, sofa_p, b_cap):
        total = round((f_sqft * f_rate * 1.10) + (w_sqft * p_rate * 2) + sofa_p, 2)
        return {
            "grand_total": total,
            "budget_cap": b_cap,
            "status": "Within Budget" if total <= b_cap else "Over Budget",
            "delta": round(abs(b_cap - total), 2)
        }

def run_aiglaze_pipeline(
    image_path="real_room.jpeg",
    style="Scandinavian Minimalist",
    user_budget=120000.0,  # ₹1.2 Lakhs Budget
    inpaint_surface="floor",
    new_material="Italian Carrara Marble"
):
    """
    Executes the complete end-to-end AI-GLAZE pipeline with Indian Market Pricing (INR ₹):
    Perceive -> Redesign -> Inpaint -> Source -> Budget & Optimize
    """
    print("\n" + "=" * 65)
    print("       AI-GLAZE: END-TO-END SYSTEM EXECUTION PIPELINE        ")
    print("                   (INDIAN MARKET EDITION - ₹)               ")
    print("=" * 65 + "\n")

    if not os.path.exists(image_path):
        if os.path.exists("real_room.jpeg"):
            image_path = "real_room.jpeg"
        elif os.path.exists("real_room.jpg"):
            image_path = "real_room.jpg"
        else:
            image_path = "test_room.jpg"

    # -------------------------------------------------------------
    # STAGE 1: SPATIAL PERCEPTION & GENERATIVE VISION (MEMBER 1)
    # -------------------------------------------------------------
    print(">>> [STAGE 1/4] Running Computer Vision & Generative AI...")
    vision_data = run_full_vision_pipeline(
        image_path=image_path,
        style=style,
        inpaint_surface=inpaint_surface,
        new_material=new_material
    )

    metrics = vision_data["spatial_metrics"]
    detected_items = vision_data["detected_objects"]
    floor_sqft = metrics["floor_area_sqft"]
    wall_sqft = metrics["wall_surface_area_sqft"]

    # -------------------------------------------------------------
    # STAGE 2: PRODUCT SOURCING (INDIAN MARKET BRANDS & INR ₹)
    # -------------------------------------------------------------
    print(">>> [STAGE 2/4] Retrieving Real Indian Products & Suppliers...")
    
    # Real Indian material rates per sq.ft
    if "marble" in new_material.lower():
        flooring_item = {
            "name": "Italian Carrara Polished Marble", 
            "rate_sqft": 380.00, 
            "tier": "Luxury", 
            "supplier": "A-Class Marble Gallery, Bangalore"
        }
    elif "wood" in new_material.lower():
        flooring_item = {
            "name": "Action TESA Engineered Oak Flooring", 
            "rate_sqft": 175.00, 
            "tier": "Mid-Range", 
            "supplier": "Nordic Wood & Laminates, Bangalore"
        }
    else:
        flooring_item = {
            "name": "Kajaria Glazed Vitrified Tiles (GVT)", 
            "rate_sqft": 65.00, 
            "tier": "Budget", 
            "supplier": "Kajaria Tile World, Bangalore"
        }

    paint_item = {
        "name": "Asian Paints Royale Luxury Emulsion", 
        "rate_sqft": 28.00, 
        "coats": 2, 
        "supplier": "Asian Paints Colour Idea Store"
    }
    
    sofa_item = {
        "name": "Modern 3-Seater L-Shape Fabric Sectional", 
        "price": 38000.00, 
        "supplier": "Urban Ladder / Pepperfry"
    }

    # -------------------------------------------------------------
    # STAGE 3: COST ESTIMATION & BILL OF QUANTITIES (MEMBER 4)
    # -------------------------------------------------------------
    print(">>> [STAGE 3/4] Computing Bill of Quantities (BoQ in ₹)...")
    
    def compute_boq(f_sqft, f_rate, w_sqft, p_rate, sofa_p, b_cap):
        floor_cost = round(f_sqft * f_rate * 1.10, 2)  # 10% wastage margin
        paint_cost = round(w_sqft * p_rate * 2, 2)     # 2 coats of paint
        total = round(floor_cost + paint_cost + sofa_p, 2)
        return {
            "flooring_subtotal": floor_cost,
            "painting_subtotal": paint_cost,
            "furniture_subtotal": sofa_p,
            "grand_total": total,
            "budget_cap": b_cap,
            "status": "Within Budget" if total <= b_cap else "Over Budget",
            "delta": round(abs(b_cap - total), 2)
        }

    initial_boq = compute_boq(
        floor_sqft,
        flooring_item["rate_sqft"],
        wall_sqft,
        paint_item["rate_sqft"],
        sofa_item["price"],
        user_budget
    )

    # -------------------------------------------------------------
    # STAGE 4: BUDGET SHOCKWAVE OPTIMIZER (KNAPSACK SOLVER)
    # -------------------------------------------------------------
    print(">>> [STAGE 4/4] Evaluating Budget Constraints...")
    final_boq = initial_boq.copy()
    optimization_notes = []

    if initial_boq["grand_total"] > user_budget:
        print(f"⚠️  Design is OVER BUDGET by ₹{initial_boq['delta']:,.2f}!")
        print("⚡ Triggering Knapsack Optimization: Swapping for budget alternatives...")
        
        # Auto-swap premium Italian marble to Kajaria Vitrified Tiles
        if flooring_item["tier"] == "Luxury":
            cheaper_floor = {
                "name": "Kajaria Double-Charged Vitrified Tile", 
                "rate_sqft": 75.00, 
                "tier": "Budget", 
                "supplier": "Kajaria World, Bangalore"
            }
            savings = round((flooring_item["rate_sqft"] - cheaper_floor["rate_sqft"]) * floor_sqft * 1.10, 2)
            optimization_notes.append(f"Swapped '{flooring_item['name']}' to '{cheaper_floor['name']}' (Saved: ₹{savings:,.2f})")
            flooring_item = cheaper_floor
            
            # Recalculate BoQ with optimized Indian materials
            final_boq = compute_boq(
                floor_sqft,
                flooring_item["rate_sqft"],
                wall_sqft,
                paint_item["rate_sqft"],
                sofa_item["price"],
                user_budget
            )
            final_boq["optimization_applied"] = True
    else:
        print("✅ Design is strictly WITHIN BUDGET!")
        final_boq["optimization_applied"] = False

    # -------------------------------------------------------------
    # BUNDLE MASTER PROJECT SPECIFICATION
    # -------------------------------------------------------------
    master_project_output = {
        "project_name": "AI-GLAZE Living Room Transformation",
        "market": "India (INR ₹)",
        "input_photo": image_path,
        "style_chosen": style,
        "target_budget_inr": user_budget,
        "vision_outputs": {
            "depth_heatmap": vision_data["depth_heatmap_path"],
            "structural_edges": vision_data["structural_edges_path"],
            "redesign_render": vision_data["redesign_path"],
            "inpaint_render": vision_data["inpaint_path"],
            "room_dimensions": metrics,
            "detected_furniture_count": len(detected_items)
        },
        "procurement_and_sourcing": [
            flooring_item,
            paint_item,
            sofa_item
        ],
        "bill_of_quantities_inr": final_boq,
        "optimization_notes": optimization_notes
    }

    # Save to JSON
    json_output_path = "aiglaze_project_output.json"
    with open(json_output_path, "w") as f:
        json.dump(master_project_output, f, indent=4)
    print(f"\n📁 Saved complete project specification to: {json_output_path}")

    # -------------------------------------------------------------
    # PRINT ARCHITECT-GRADE TERMINAL SUMMARY (IN RUPEES)
    # -------------------------------------------------------------
    print("\n" + "=" * 65)
    print("             AI-GLAZE: FINAL IMPLEMENTATION PLAN             ")
    print("                   (INDIAN MARKET EDITION)                   ")
    print("=" * 65)
    print(f" • Interior Style     : {style}")
    print(f" • Room Floor Area    : {floor_sqft} sq.ft")
    print(f" • Wall Surface Area  : {wall_sqft} sq.ft")
    print(f" • Flooring Material  : {flooring_item['name']} (₹{flooring_item['rate_sqft']}/sq.ft)")
    print(f" • Supplier           : {flooring_item['supplier']}")
    print(f" • Paint Selected     : {paint_item['name']} (₹{paint_item['rate_sqft']}/sq.ft)")
    print(f" • Target Budget Cap  : ₹{user_budget:,.2f}")
    print(f" • Grand Total Cost   : ₹{final_boq['grand_total']:,.2f}")
    print(f" • Status             : {final_boq['status']} (₹{final_boq['delta']:,.2f} difference)")
    if optimization_notes:
        print(f" • Budget Optimization: {optimization_notes[0]}")
    print("=" * 65 + "\n")

    return master_project_output

if __name__ == "__main__":
    # Automatically finds real_room.jpeg, real_room.jpg, or test_room.jpg
    if os.path.exists("real_room.jpeg"):
        test_img = "real_room.jpeg"
    elif os.path.exists("real_room.jpg"):
        test_img = "real_room.jpg"
    else:
        test_img = "test_room.jpg"
        
    print(f"Using image: {test_img}")
    
    # Run master orchestrator with Indian renovation budget (₹1.2 Lakhs)
    project_result = run_aiglaze_pipeline(
        image_path=test_img,
        style="Scandinavian Minimalist",
        user_budget=120000.0,
        inpaint_surface="floor",
        new_material="Italian Carrara Marble"
    )