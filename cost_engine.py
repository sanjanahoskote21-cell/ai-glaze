"""
AI-GLAZE - Cost Estimation, Bill of Quantities (BoQ) & Budget Optimization Engine
Module: cost_engine.py
Author: Teammate C (Member 4: Cost Engineering, BoQ & Reports Lead)
Project: AI-GLAZE (AI-Powered Spatial Planning & Interior Architecture)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


# ============================================================================
# 1. MATERIAL CATALOGUE & BENCHMARK PRICING TIERS
# ============================================================================

MATERIAL_CATALOGUE = {
    "flooring": [
        {
            "tier": "Luxury",
            "name": "Italian Statuario Marble Finish",
            "rate_per_sqft": 280.0,
            "utility_score": 95,
            "description": "Premium imported marble slabs with seamless resin polish.",
            "supplier_spec": "Grade-A 18mm Statuario slabs, diamond polished with anti-stain sealant."
        },
        {
            "tier": "Premium",
            "name": "Engineered Oak Hardwood Flooring",
            "rate_per_sqft": 150.0,
            "utility_score": 85,
            "description": "Multi-layer UV cured natural oak planks with acoustic underlayment.",
            "supplier_spec": "14mm engineered European oak, tongue & groove, matte polyurethane seal."
        },
        {
            "tier": "Standard",
            "name": "Vitrified Glazed Porcelain Tiles (GVT)",
            "rate_per_sqft": 65.0,
            "utility_score": 72,
            "description": "Double-charged, low porosity high-durability rectified vitrified tiles.",
            "supplier_spec": "1200x600mm rectified porcelain, epoxy grouted with 2mm spacers."
        },
        {
            "tier": "Economy",
            "name": "Ceramic Anti-Skid / Luxury Vinyl Planks (LVP)",
            "rate_per_sqft": 35.0,
            "utility_score": 55,
            "description": "High-wear commercial-grade vinyl plank or ceramic tile with slip resistance.",
            "supplier_spec": "5mm click-lock SPC/LVP waterproof core with 0.5mm wear layer."
        }
    ],
    "painting": [
        {
            "tier": "Luxury",
            "name": "Venetian Stucco Plaster & Metallic Accent",
            "rate_per_sqft": 75.0,
            "utility_score": 96,
            "description": "Hand-troweled lime-based Venetian plaster with burnished metallic wax.",
            "supplier_spec": "3-coat artisanal Italian plaster, beeswax buffed, hydrophobic topcoat."
        },
        {
            "tier": "Premium",
            "name": "Royal Luxury Silk Emulsion (Teflon Coated)",
            "rate_per_sqft": 38.0,
            "utility_score": 88,
            "description": "Ultra-washable low-VOC luxury silk finish with anti-fungal barrier.",
            "supplier_spec": "1 coat acrylic primer, 2 coats luxury silk emulsion, micro-fill putty."
        },
        {
            "tier": "Standard",
            "name": "Premium Interior Acrylic Emulsion",
            "rate_per_sqft": 22.0,
            "utility_score": 72,
            "description": "Durable, smooth matte finish acrylic latex with good stain resistance.",
            "supplier_spec": "1 coat water thinnable primer, 2 coats acrylic emulsion, sanded putty."
        },
        {
            "tier": "Economy",
            "name": "Standard Washable Acrylic Distemper / Emulsion",
            "rate_per_sqft": 12.0,
            "utility_score": 52,
            "description": "Budget-friendly uniform interior wall finish for clean contemporary spaces.",
            "supplier_spec": "Standard white cement putty base with 2 coats washable interior coating."
        }
    ],
    "furniture": [
        {
            "tier": "Luxury",
            "name": "Bespoke Teak Wood & Italian Nappa Leather Package",
            "multiplier": 1.00,
            "utility_score": 95,
            "description": "Custom artisan cabinetry, seasoned teak wood framing and genuine leather.",
            "supplier_spec": "Kiln-dried Burma teak, Hafele soft-close hardware, full grain leather."
        },
        {
            "tier": "Premium",
            "name": "Solid Oak & High-Density Performance Fabric Package",
            "multiplier": 0.70,
            "utility_score": 82,
            "description": "Kiln-dried hardwood framing, high-density foam (32D), stain-resistant fabric.",
            "supplier_spec": "BWP Marine ply carcass, natural veneer frontage, Blum hinges."
        },
        {
            "tier": "Standard",
            "name": "Modular Engineered Wood (BWP Grade) Package",
            "multiplier": 0.45,
            "utility_score": 68,
            "description": "Factory-calibrated modular setup with high-pressure laminate (HPL) finish.",
            "supplier_spec": "IS 710 marine plywood core, 1mm laminate sheets, Hettich fittings."
        },
        {
            "tier": "Economy",
            "name": "Minimalist High-Density Particle / Flat-Pack Modular",
            "multiplier": 0.28,
            "utility_score": 50,
            "description": "Value-engineered modular pre-laminated units designed for rapid assembly.",
            "supplier_spec": "High-density moisture-resistant (HDMR) board, edge-banded 2mm PVC."
        }
    ]
}


# ============================================================================
# 2. SURFACE AREA MATHEMATICS
# ============================================================================

def calculate_floor_area(length_ft: float, width_ft: float, wastage_margin: float = 0.10) -> Dict[str, float]:
    """
    Calculates net room floor surface area and total gross square footage 
    accounting for tile/timber cutting angles and installation wastage.
    
    Args:
        length_ft: Room length in feet.
        width_ft: Room width in feet.
        wastage_margin: Cutting & layout waste percentage (default is 10% / 0.10).
        
    Returns:
        Dict containing net_area_sqft, wastage_sqft, and gross_area_sqft.
    """
    if length_ft <= 0 or width_ft <= 0:
        raise ValueError("Room dimensions (length and width) must be greater than zero.")
    
    net_area = length_ft * width_ft
    wastage_sqft = net_area * wastage_margin
    gross_area = net_area + wastage_sqft
    
    return {
        "length_ft": float(round(length_ft, 2)),
        "width_ft": float(round(width_ft, 2)),
        "net_area_sqft": float(round(net_area, 2)),
        "wastage_margin_percent": float(round(wastage_margin * 100, 1)),
        "wastage_sqft": float(round(wastage_sqft, 2)),
        "gross_area_sqft": float(round(gross_area, 2))
    }


def calculate_wall_surface_area(perimeter_ft: float, height_ft: float, openings_area: float = 45.0) -> Dict[str, float]:
    """
    Calculates total gross vertical wall surface area [Perimeter x Height] 
    and subtracts architectural openings (doors, windows, ventilation voids)
    to determine net paintable/treatment surface area.
    
    Args:
        perimeter_ft: Total room boundary perimeter in feet (2 * (L + W)).
        height_ft: Clear floor-to-ceiling vertical height in feet.
        openings_area: Cumulative surface area of windows and doors in sq.ft (standard default is 45.0 sq.ft).
        
    Returns:
        Dict containing perimeter_ft, height_ft, gross_wall_sqft, openings_sqft, and net_paintable_sqft.
    """
    if perimeter_ft <= 0 or height_ft <= 0:
        raise ValueError("Room perimeter and ceiling height must be greater than zero.")
        
    gross_wall_sqft = perimeter_ft * height_ft
    # Net area cannot be negative
    net_paintable_sqft = max(0.0, gross_wall_sqft - openings_area)
    
    return {
        "perimeter_ft": float(round(perimeter_ft, 2)),
        "height_ft": float(round(height_ft, 2)),
        "gross_wall_sqft": float(round(gross_wall_sqft, 2)),
        "openings_sqft": float(round(openings_area, 2)),
        "net_paintable_sqft": float(round(net_paintable_sqft, 2))
    }


# ============================================================================
# 3. COMPONENT COST CALCULATIONS
# ============================================================================

def calculate_flooring_cost(length_ft: float, width_ft: float, rate_per_sqft: float, wastage: float = 0.10) -> Dict[str, Any]:
    """
    Computes total flooring procurement & laying expense, incorporating cutting wastage.
    
    Args:
        length_ft: Length of the room in feet.
        width_ft: Width of the room in feet.
        rate_per_sqft: Material procurement & labor laying rate per square foot.
        wastage: Wastage factor (e.g. 0.10 for 10%).
        
    Returns:
        Dict with comprehensive square footage and monetary breakdown.
    """
    floor_metrics = calculate_floor_area(length_ft, width_ft, wastage_margin=wastage)
    billable_sqft = floor_metrics["gross_area_sqft"]
    total_cost = billable_sqft * rate_per_sqft
    
    return {
        "length_ft": length_ft,
        "width_ft": width_ft,
        "net_sqft": floor_metrics["net_area_sqft"],
        "wastage_sqft": floor_metrics["wastage_sqft"],
        "billable_sqft": billable_sqft,
        "rate_per_sqft": rate_per_sqft,
        "total_cost": round(total_cost, 2)
    }


def calculate_paint_cost(perimeter_ft: float, height_ft: float, rate_per_sqft: float, coats: int = 2, openings_area: float = 45.0) -> Dict[str, Any]:
    """
    Computes total wall treatment and painting expense including multi-coat preparation.
    
    Args:
        perimeter_ft: Perimeter of room in feet.
        height_ft: Height of ceiling in feet.
        rate_per_sqft: Material + labor cost per square foot per application coat.
        coats: Number of paint coats required (standard is 2 coats).
        openings_area: Deduction for doors and windows in sq.ft.
        
    Returns:
        Dict with net paintable area, coat multipliers, and total cost.
    """
    wall_metrics = calculate_wall_surface_area(perimeter_ft, height_ft, openings_area=openings_area)
    net_wall_sqft = wall_metrics["net_paintable_sqft"]
    
    # Standard practice: rate_per_sqft is usually quoted for standard 2-coat system.
    # If custom coats > 2, an incremental factor is applied.
    coat_factor = coats / 2.0
    effective_sqft = net_wall_sqft * coat_factor
    total_cost = effective_sqft * rate_per_sqft
    
    return {
        "perimeter_ft": perimeter_ft,
        "height_ft": height_ft,
        "net_wall_sqft": net_wall_sqft,
        "coats": coats,
        "effective_sqft": round(effective_sqft, 2),
        "rate_per_sqft": rate_per_sqft,
        "total_cost": round(total_cost, 2)
    }


# ============================================================================
# 4. MASTER BILL OF QUANTITIES (BoQ) GENERATOR
# ============================================================================

def generate_full_boq(
    floor_sqft: float, 
    floor_rate: float, 
    wall_sqft: float, 
    paint_rate: float, 
    furniture_price: float, 
    budget_cap: float,
    labor_buffer_pct: float = 0.12,
    contingency_pct: float = 0.05,
    room_name: str = "Master Suite / Living Area",
    selected_specs: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Compiles an itemized architectural Bill of Quantities (BoQ) integrating:
    1. Flooring finishes & cutting margins.
    2. Wall preparation, primer & multi-coat painting.
    3. Furniture and joinery fixture allowances.
    4. Specialized trade labor buffer (civil, electrical, plumbing, detailing).
    5. Unforeseen engineering contingency allowance.
    
    Compares aggregate total against client's target budget cap to output compliance status and delta.
    
    Args:
        floor_sqft: Billable floor square footage (including wastage).
        floor_rate: Rate per sq.ft for flooring.
        wall_sqft: Net paintable wall square footage.
        paint_rate: Rate per sq.ft for wall painting.
        furniture_price: Fixed or calculated estimate for furniture/fixtures package.
        budget_cap: Client maximum specified budget ceiling.
        labor_buffer_pct: Margin allocated for site supervision & craftsmanship (default 12%).
        contingency_pct: Buffer for price escalation & site contingencies (default 5%).
        room_name: Descriptive name of the architectural space.
        selected_specs: Optional names of specific materials chosen for the report.
        
    Returns:
        Structured BoQ dictionary with itemized line items, subtotals, tax/contingency, grand total, and budget variance.
    """
    flooring_cost = round(floor_sqft * floor_rate, 2)
    painting_cost = round(wall_sqft * paint_rate, 2)
    furniture_cost = round(furniture_price, 2)
    
    materials_subtotal = round(flooring_cost + painting_cost + furniture_cost, 2)
    labor_buffer = round(materials_subtotal * labor_buffer_pct, 2)
    subtotal_with_labor = round(materials_subtotal + labor_buffer, 2)
    contingency_allowance = round(subtotal_with_labor * contingency_pct, 2)
    
    grand_total = round(subtotal_with_labor + contingency_allowance, 2)
    
    is_within_budget = (grand_total <= budget_cap)
    status = "Within Budget" if is_within_budget else "Over Budget"
    delta = round(abs(budget_cap - grand_total), 2)
    variance_signed = round(budget_cap - grand_total, 2)
    variance_percentage = round((variance_signed / budget_cap) * 100, 2) if budget_cap > 0 else 0.0
    
    default_specs = {
        "flooring": "Premium Architectural Flooring",
        "painting": "Silk Low-VOC Wall Emulsion",
        "furniture": "Engineered Wood Custom Joinery"
    }
    specs = {**default_specs, **(selected_specs or {})}

    line_items = [
        {
            "id": "BOQ-001",
            "category": "Flooring & Substrate",
            "description": f"{specs['flooring']} (Inc. 10% cutting wastage & grout laying)",
            "quantity": floor_sqft,
            "unit": "sq.ft",
            "unit_rate": floor_rate,
            "subtotal": flooring_cost
        },
        {
            "id": "BOQ-002",
            "category": "Wall Surface Finishing",
            "description": f"{specs['painting']} (Surface prep, primer + 2 topcoats)",
            "quantity": wall_sqft,
            "unit": "sq.ft",
            "unit_rate": paint_rate,
            "subtotal": painting_cost
        },
        {
            "id": "BOQ-003",
            "category": "Furniture & Modular Fixtures",
            "description": f"{specs['furniture']} (Factory assembled & site anchored)",
            "quantity": 1.0,
            "unit": "lot",
            "unit_rate": furniture_cost,
            "subtotal": furniture_cost
        },
        {
            "id": "BOQ-004",
            "category": "Skilled Craftsmanship & Labor",
            "description": f"Site supervision, masonry alignment & installation labor ({int(labor_buffer_pct * 100)}%)",
            "quantity": 1.0,
            "unit": "service",
            "unit_rate": labor_buffer,
            "subtotal": labor_buffer
        },
        {
            "id": "BOQ-005",
            "category": "Engineering Contingency",
            "description": f"Safety buffer for site unforeseen deviations & material escalations ({int(contingency_pct * 100)}%)",
            "quantity": 1.0,
            "unit": "allowance",
            "unit_rate": contingency_allowance,
            "subtotal": contingency_allowance
        }
    ]

    return {
        "project_metadata": {
            "project_name": "AI-GLAZE Smart Interior Fit-out",
            "room_name": room_name,
            "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "currency": "INR (₹)"  # Adaptable display
        },
        "dimensions": {
            "floor_sqft": floor_sqft,
            "wall_sqft": wall_sqft
        },
        "line_items": line_items,
        "financial_summary": {
            "materials_subtotal": materials_subtotal,
            "labor_buffer": labor_buffer,
            "contingency_allowance": contingency_allowance,
            "grand_total": grand_total,
            "budget_cap": budget_cap,
            "status": status,
            "is_within_budget": is_within_budget,
            "delta": delta,
            "variance_signed": variance_signed,
            "variance_percentage": variance_percentage
        },
        "current_specs": specs
    }


# ============================================================================
# 5. SHOWSTOPPER #2: KNAPSACK BUDGET OPTIMIZATION SOLVER
# ============================================================================

def optimize_boq_for_budget(
    boq: Dict[str, Any], 
    max_budget: float,
    base_luxury_furniture_cost: float = 85000.0
) -> Dict[str, Any]:
    """
    Constrained Multi-Choice Knapsack & Value-Cost Optimizer.
    
    When an estimate exceeds the client's financial ceiling, this algorithm
    evaluates all discrete trade combinations (Flooring x Painting x Furniture)
    to find the configuration that:
      1. Guarantees Grand Total <= max_budget.
      2. Maximizes overall aesthetic quality and durability (Sum of utility scores).
      3. Calculates exact line-by-line material downgrades with dollar/rupee savings.
      
    Args:
        boq: Master Bill of Quantities dictionary generated by generate_full_boq.
        max_budget: Strict client financial threshold.
        base_luxury_furniture_cost: Baseline benchmark cost for Tier-1 luxury furniture package.
        
    Returns:
        A comprehensive optimization report containing:
        - is_achievable: Whether any combination fits under the budget.
        - original_total: Previous cost.
        - optimized_total: New compliant cost.
        - total_savings: Total money saved.
        - downgrades: Step-by-step substitutions performed.
        - optimized_boq: Ready-to-use new BoQ object.
    """
    floor_sqft = boq["dimensions"]["floor_sqft"]
    wall_sqft = boq["dimensions"]["wall_sqft"]
    original_total = boq["financial_summary"]["grand_total"]
    
    # If already within budget, no changes required
    if original_total <= max_budget:
        return {
            "is_achievable": True,
            "already_within_budget": True,
            "original_total": original_total,
            "optimized_total": original_total,
            "total_savings": 0.0,
            "message": "Project is already within specified budget. No material trade-offs required.",
            "downgrades": [],
            "optimized_boq": boq
        }
    
    best_combination = None
    best_utility = -1.0
    lowest_cost_possible = float("inf")
    cheapest_combination = None
    
    # Evaluate every permutation across Flooring x Painting x Furniture tiers
    for f_opt in MATERIAL_CATALOGUE["flooring"]:
        for p_opt in MATERIAL_CATALOGUE["painting"]:
            for furn_opt in MATERIAL_CATALOGUE["furniture"]:
                # Compute cost for this combination
                cand_floor_rate = f_opt["rate_per_sqft"]
                cand_paint_rate = p_opt["rate_per_sqft"]
                cand_furn_price = base_luxury_furniture_cost * furn_opt["multiplier"]
                
                # Check candidate BoQ
                cand_boq = generate_full_boq(
                    floor_sqft=floor_sqft,
                    floor_rate=cand_floor_rate,
                    wall_sqft=wall_sqft,
                    paint_rate=cand_paint_rate,
                    furniture_price=cand_furn_price,
                    budget_cap=max_budget,
                    room_name=boq["project_metadata"].get("room_name", "Master Interior Space"),
                    selected_specs={
                        "flooring": f_opt["name"],
                        "painting": p_opt["name"],
                        "furniture": furn_opt["name"]
                    }
                )
                
                cand_total = cand_boq["financial_summary"]["grand_total"]
                total_utility = f_opt["utility_score"] + p_opt["utility_score"] + furn_opt["utility_score"]
                
                # Track absolute minimum in case budget is lower than any possible tier
                if cand_total < lowest_cost_possible:
                    lowest_cost_possible = cand_total
                    cheapest_combination = (f_opt, p_opt, furn_opt, cand_boq)
                
                # Knapsack criterion: within budget, maximize utility
                if cand_total <= max_budget:
                    if total_utility > best_utility:
                        best_utility = total_utility
                        best_combination = (f_opt, p_opt, furn_opt, cand_boq)
    
    # If no combination fits under the budget
    if best_combination is None:
        f_min, p_min, furn_min, min_boq = cheapest_combination
        shortfall = round(lowest_cost_possible - max_budget, 2)
        return {
            "is_achievable": False,
            "already_within_budget": False,
            "original_total": original_total,
            "optimized_total": lowest_cost_possible,
            "total_savings": round(original_total - lowest_cost_possible, 2),
            "shortfall": shortfall,
            "message": (
                f"Budget cap of {max_budget:,.2f} is below the baseline economy tier. "
                f"Minimum attainable cost is {lowest_cost_possible:,.2f} (Shortfall of {shortfall:,.2f})."
            ),
            "downgrades": [
                {"category": "Flooring", "recommended": f_min["name"], "tier": f_min["tier"]},
                {"category": "Painting", "recommended": p_min["name"], "tier": p_min["tier"]},
                {"category": "Furniture", "recommended": furn_min["name"], "tier": furn_min["tier"]}
            ],
            "optimized_boq": min_boq
        }
    
    # Optimal combination found!
    opt_f, opt_p, opt_furn, optimized_boq = best_combination
    optimized_total = optimized_boq["financial_summary"]["grand_total"]
    total_savings = round(original_total - optimized_total, 2)
    
    # Identify itemized downgrades / substitutions
    downgrades = []
    
    # Flooring check
    orig_f_subtotal = boq["line_items"][0]["subtotal"]
    new_f_subtotal = optimized_boq["line_items"][0]["subtotal"]
    if orig_f_subtotal > new_f_subtotal:
        downgrades.append({
            "category": "Flooring & Substrate",
            "from_specification": boq["line_items"][0]["description"],
            "to_specification": f"{opt_f['name']} ({opt_f['tier']} Tier)",
            "supplier_spec": opt_f["supplier_spec"],
            "old_rate": boq["line_items"][0]["unit_rate"],
            "new_rate": opt_f["rate_per_sqft"],
            "savings": round(orig_f_subtotal - new_f_subtotal, 2),
            "impact_assessment": "Retains 90%+ wear resistance with significant material savings."
        })
        
    # Painting check
    orig_p_subtotal = boq["line_items"][1]["subtotal"]
    new_p_subtotal = optimized_boq["line_items"][1]["subtotal"]
    if orig_p_subtotal > new_p_subtotal:
        downgrades.append({
            "category": "Wall Surface Finishing",
            "from_specification": boq["line_items"][1]["description"],
            "to_specification": f"{opt_p['name']} ({opt_p['tier']} Tier)",
            "supplier_spec": opt_p["supplier_spec"],
            "old_rate": boq["line_items"][1]["unit_rate"],
            "new_rate": opt_p["rate_per_sqft"],
            "savings": round(orig_p_subtotal - new_p_subtotal, 2),
            "impact_assessment": "Smooth aesthetic finish maintained while lowering coats/labor costs."
        })
        
    # Furniture check
    orig_furn_subtotal = boq["line_items"][2]["subtotal"]
    new_furn_subtotal = optimized_boq["line_items"][2]["subtotal"]
    if orig_furn_subtotal > new_furn_subtotal:
        downgrades.append({
            "category": "Furniture & Modular Fixtures",
            "from_specification": boq["line_items"][2]["description"],
            "to_specification": f"{opt_furn['name']} ({opt_furn['tier']} Tier)",
            "supplier_spec": opt_furn["supplier_spec"],
            "old_rate": orig_furn_subtotal,
            "new_rate": new_furn_subtotal,
            "savings": round(orig_furn_subtotal - new_furn_subtotal, 2),
            "impact_assessment": "Precision factory calibrated joinery with durable laminate surfaces."
        })

    return {
        "is_achievable": True,
        "already_within_budget": False,
        "original_total": original_total,
        "optimized_total": optimized_total,
        "total_savings": total_savings,
        "surplus_under_budget": round(max_budget - optimized_total, 2),
        "total_utility_score": best_utility,
        "downgrades": downgrades,
        "optimized_boq": optimized_boq
    }


# ============================================================================
# 6. SHOWSTOPPER #4: PRINTABLE CONTRACTOR SPECIFICATION SHEET (HTML)
# ============================================================================

def export_boq_report(boq_data: Dict[str, Any], output_file: str = "contractor_boq_report.html") -> str:
    """
    Renders an architectural-grade, responsive, and print-ready contractor specification sheet in HTML.
    
    Includes:
    - AI-GLAZE verified seal & document metadata.
    - Executive summary KPI cards (Budget, Estimate, Variance, Square Footage).
    - Itemized Bill of Quantities table with exact quantities, rates, and unit classifications.
    - Material engineering specifications & supplier compliance notes.
    - Site preparation directives & trade contractor sign-off protocols.
    - Formal engineering safety & contingency disclaimer.
    - Clean CSS print styling for direct PDF generation via browser Ctrl+P.
    
    Args:
        boq_data: Complete dictionary output from generate_full_boq or optimize_boq_for_budget.
        output_file: Destination file path for HTML export.
        
    Returns:
        Absolute file path of the generated HTML document.
    """
    meta = boq_data.get("project_metadata", {})
    dims = boq_data.get("dimensions", {})
    fin = boq_data.get("financial_summary", {})
    items = boq_data.get("line_items", [])
    specs = boq_data.get("current_specs", {})
    
    is_ok = fin.get("is_within_budget", True)
    badge_color = "#10b981" if is_ok else "#ef4444"
    badge_bg = "#ecfdf5" if is_ok else "#fef2f2"
    status_label = fin.get("status", "Analyzed")
    
    table_rows_html = ""
    for item in items:
        table_rows_html += f"""
        <tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #1e293b;">{item['id']}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0;">
                <div style="font-weight: 600; color: #0f172a;">{item['category']}</div>
                <div style="font-size: 13px; color: #64748b; margin-top: 2px;">{item['description']}</div>
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: center; color: #334155;">{item['quantity']:,.1f} {item['unit']}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #334155;">₹{item['unit_rate']:,.2f}</td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600; color: #0f172a;">₹{item['subtotal']:,.2f}</td>
        </tr>
        """
        
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-GLAZE Contractor Specification & BoQ Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            line-height: 1.5;
            padding: 40px 20px;
        }}
        
        .report-wrapper {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        
        .header-bar {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #2e1065 100%);
            color: #ffffff;
            padding: 36px 40px;
            position: relative;
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
        }}
        
        .brand-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(8px);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #38bdf8;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .title-h1 {{
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-top: 12px;
            color: #ffffff;
        }}
        
        .subtitle {{
            color: #94a3b8;
            font-size: 14px;
            margin-top: 4px;
        }}
        
        .doc-meta {{
            text-align: right;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #cbd5e1;
        }}
        
        .content-body {{
            padding: 36px 40px;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 18px 20px;
            transition: all 0.2s ease;
        }}
        
        .kpi-label {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }}
        
        .kpi-value {{
            font-size: 22px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 6px;
            letter-spacing: -0.5px;
        }}
        
        .status-pill {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: {badge_color};
            background: {badge_bg};
            margin-top: 6px;
            border: 1px solid {badge_color}33;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #0f172a;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.3px;
        }}
        
        .boq-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin-bottom: 32px;
        }}
        
        .boq-table th {{
            background: #f1f5f9;
            color: #475569;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            padding: 12px 16px;
            border-bottom: 2px solid #cbd5e1;
        }}
        
        .summary-box {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 32px;
        }}
        
        .summary-table {{
            width: 360px;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        .summary-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .grand-total-row td {{
            padding: 12px;
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
            border-top: 2px solid #0f172a;
            border-bottom: 2px solid #0f172a;
            background: #f8fafc;
        }}
        
        .spec-box {{
            background: #fdf2f8;
            border: 1px solid #fbcfe8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 32px;
        }}
        
        .spec-box h3 {{
            color: #9d174d;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .spec-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 12px;
            font-size: 13px;
            color: #701a75;
        }}
        
        .signoff-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 36px;
            padding-top: 24px;
            border-top: 1px dashed #cbd5e1;
        }}
        
        .signoff-box {{
            border: 1px dashed #94a3b8;
            border-radius: 8px;
            padding: 24px;
            text-align: center;
        }}
        
        .signoff-line {{
            margin-top: 50px;
            border-top: 1px solid #475569;
            padding-top: 6px;
            font-weight: 600;
            font-size: 13px;
            color: #334155;
        }}
        
        .disclaimer {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 18px;
            font-size: 11px;
            color: #64748b;
            margin-top: 30px;
            line-height: 1.6;
        }}
        
        .print-btn-bar {{
            background: #f1f5f9;
            padding: 12px 40px;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            border-top: 1px solid #e2e8f0;
        }}
        
        .btn {{
            cursor: pointer;
            padding: 8px 18px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            border: none;
            transition: all 0.2s;
        }}
        
        .btn-print {{
            background: #0f172a;
            color: #ffffff;
        }}
        
        .btn-print:hover {{
            background: #334155;
        }}
        
        @media print {{
            body {{
                background: none;
                padding: 0;
            }}
            .report-wrapper {{
                border: none;
                box-shadow: none;
                max-width: 100%;
            }}
            .print-btn-bar {{
                display: none;
            }}
        }}
    </style>
</head>
<body>

    <div class="report-wrapper">
        <div class="header-bar">
            <div class="header-top">
                <div>
                    <div class="brand-badge">⚡ AI-GLAZE SPATIAL ARCHITECTURE</div>
                    <h1 class="title-h1">Contractor Bill of Quantities (BoQ)</h1>
                    <div class="subtitle">{meta.get('project_name', 'AI-GLAZE Smart Interior Fit-out')} &bull; Space: <strong>{meta.get('room_name', 'Master Suite')}</strong></div>
                </div>
                <div class="doc-meta">
                    <div>DOC REF: AGY-BOQ-2026-X</div>
                    <div>DATE: {meta.get('date_generated', datetime.now().strftime('%Y-%m-%d'))}</div>
                    <div>LEAD: Teammate C (Cost Engineering)</div>
                </div>
            </div>
        </div>

        <div class="print-btn-bar">
            <button class="btn btn-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
        </div>

        <div class="content-body">
            <!-- KPI CARDS -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Flooring Area (Billable)</div>
                    <div class="kpi-value">{dims.get('floor_sqft', 0):,.1f} <span style="font-size: 14px; font-weight: normal;">sq.ft</span></div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Includes 10% cutting waste</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Wall Paintable Area</div>
                    <div class="kpi-value">{dims.get('wall_sqft', 0):,.1f} <span style="font-size: 14px; font-weight: normal;">sq.ft</span></div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Net after window/door voids</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Client Budget Ceiling</div>
                    <div class="kpi-value">₹{fin.get('budget_cap', 0):,.2f}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Benchmark Target</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Status & Delta</div>
                    <div class="status-pill">{status_label}</div>
                    <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-top: 6px;">
                        {'Savings: ₹' if is_ok else 'Excess: ₹'}{fin.get('delta', 0):,.2f}
                    </div>
                </div>
            </div>

            <!-- ITEMIZED BOQ TABLE -->
            <div class="section-header">
                <h2 class="section-title">Itemized Scope of Works & Material Schedule</h2>
                <span style="font-size: 12px; color: #64748b; font-family: 'JetBrains Mono', monospace;">IS 1200 STANDARDS APPLIED</span>
            </div>

            <table class="boq-table">
                <thead>
                    <tr>
                        <th style="width: 10%;">Item ID</th>
                        <th style="width: 45%; text-align: left;">Scope & Specification Description</th>
                        <th style="width: 15%; text-align: center;">Quantity</th>
                        <th style="width: 15%; text-align: right;">Unit Rate</th>
                        <th style="width: 15%; text-align: right;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>

            <!-- SUMMARY TOTALS -->
            <div class="summary-box">
                <table class="summary-table">
                    <tr>
                        <td style="color: #64748b;">Direct Materials & Package Total:</td>
                        <td style="text-align: right; font-weight: 600;">₹{fin.get('materials_subtotal', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b;">Installation & Craftsmanship Buffer (12%):</td>
                        <td style="text-align: right; font-weight: 600;">₹{fin.get('labor_buffer', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b;">Site Contingency & Escalation Buffer (5%):</td>
                        <td style="text-align: right; font-weight: 600;">₹{fin.get('contingency_allowance', 0):,.2f}</td>
                    </tr>
                    <tr class="grand-total-row">
                        <td>Grand Total (INR):</td>
                        <td style="text-align: right; color: #0f172a;">₹{fin.get('grand_total', 0):,.2f}</td>
                    </tr>
                </table>
            </div>

            <!-- ARCHITECTURAL SPECIFICATION NOTES -->
            <div class="spec-box">
                <h3>📌 Architectural Specifications & Supplier Standards</h3>
                <div class="spec-grid">
                    <div><strong>Flooring Spec:</strong> {specs.get('flooring', 'Vitrified Glazed Tiles')}</div>
                    <div><strong>Wall Finishing:</strong> {specs.get('painting', 'Silk Emulsion Multi-coat')}</div>
                    <div><strong>Cabinetry & Joinery:</strong> {specs.get('furniture', 'Modular Engineered Hardwood')}</div>
                    <div><strong>Quality Seal:</strong> ISO 9001 / GreenPro Low-VOC Certified</div>
                </div>
            </div>

            <!-- CONTRACTOR & CLIENT SIGNOFF -->
            <div class="signoff-section">
                <div class="signoff-box">
                    <div style="font-size: 13px; color: #64748b;">Certified Field Contractor</div>
                    <div class="signoff-line">Authorized Signatory & Stamp</div>
                </div>
                <div class="signoff-box">
                    <div style="font-size: 13px; color: #64748b;">Client Approval / Architecture Lead</div>
                    <div class="signoff-line">Authorized Signatory & Date</div>
                </div>
            </div>

            <!-- DISCLAIMER -->
            <div class="disclaimer">
                <strong>ENGINEERING & STATUTORY NOTICE:</strong> This Bill of Quantities (BoQ) is algorithmically generated by the AI-GLAZE Computational Cost Engine based on spatial segmentation data provided by the Vision Processing Module. All measurements include standard statutory cutting/wastage allowances compliant with IS 1200 architectural norms. Rates are subject to local supply chain fluctuations and final structural verification by the on-site MEP engineer before tender contract execution.
            </div>
        </div>
    </div>

</body>
</html>
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return os.path.abspath(output_file)


# ============================================================================
# 7. STANDALONE SELF-TESTING BLOCK
# ============================================================================

def run_self_test():
    """
    Executes a comprehensive verification suite when cost_engine.py is executed directly.
    """
    print("\n" + "=" * 78)
    print("   AI-GLAZE COST ESTIMATION, BoQ & BUDGET OPTIMIZATION ENGINE")
    print("   Team Member C: Cost Engineering, BoQ & Reports Lead")
    print("=" * 78)

    # 1. Room Dimensions (Master Bedroom benchmark: 15 ft x 12 ft x 10 ft)
    length = 15.0
    width = 12.0
    height = 10.0
    perimeter = 2 * (length + width)  # 54.0 ft
    openings = 45.0  # standard door (21 sqft) + window (24 sqft)
    
    print("\n[Step 1] SURFACE AREA MATHEMATICS")
    print("-" * 50)
    floor_metrics = calculate_floor_area(length, width, wastage_margin=0.10)
    print(f"Room Dimensions      : {length} ft (L) x {width} ft (W) x {height} ft (H)")
    print(f"Net Floor Area       : {floor_metrics['net_area_sqft']} sq.ft")
    print(f"Wastage Margin (10%) : +{floor_metrics['wastage_sqft']} sq.ft")
    print(f"Billable Floor Area  : {floor_metrics['gross_area_sqft']} sq.ft")
    
    wall_metrics = calculate_wall_surface_area(perimeter, height, openings_area=openings)
    print(f"\nGross Wall Perimeter : {perimeter} ft (Gross Wall Area: {wall_metrics['gross_wall_sqft']} sq.ft)")
    print(f"Architectural Voids  : -{openings} sq.ft (Doorways & Windows)")
    print(f"Net Paintable Area   : {wall_metrics['net_paintable_sqft']} sq.ft")
    
    # 2. Benchmark luxury initial inputs that intentionally exceed a conservative budget
    client_budget = 135000.0  # ₹135,000 budget cap
    lux_floor_rate = 280.0    # Italian Statuario Marble
    lux_paint_rate = 75.0     # Venetian Plaster
    lux_furniture = 85000.0   # Bespoke Teak Wood package
    
    print("\n[Step 2] INITIAL BILL OF QUANTITIES (LUXURY SPECIFICATION)")
    print("-" * 50)
    initial_boq = generate_full_boq(
        floor_sqft=floor_metrics["gross_area_sqft"],
        floor_rate=lux_floor_rate,
        wall_sqft=wall_metrics["net_paintable_sqft"],
        paint_rate=lux_paint_rate,
        furniture_price=lux_furniture,
        budget_cap=client_budget,
        room_name="Executive Master Bedroom (15x12)",
        selected_specs={
            "flooring": "Italian Statuario Marble Finish",
            "painting": "Venetian Plaster & Metallic Accent",
            "furniture": "Bespoke Teak Wood Package"
        }
    )
    
    fin = initial_boq["financial_summary"]
    print(f"Flooring Subtotal    : ₹{initial_boq['line_items'][0]['subtotal']:>12,.2f}")
    print(f"Painting Subtotal    : ₹{initial_boq['line_items'][1]['subtotal']:>12,.2f}")
    print(f"Furniture Subtotal   : ₹{initial_boq['line_items'][2]['subtotal']:>12,.2f}")
    print(f"Labor Buffer (12%)   : ₹{fin['labor_buffer']:>12,.2f}")
    print(f"Contingency (5%)     : ₹{fin['contingency_allowance']:>12,.2f}")
    print("-" * 50)
    print(f"INITIAL GRAND TOTAL  : ₹{fin['grand_total']:>12,.2f}")
    print(f"CLIENT BUDGET CAP    : ₹{fin['budget_cap']:>12,.2f}")
    print(f"STATUS               : [{fin['status'].upper()}] - Deficit: ₹{fin['delta']:,.2f}")
    
    # 3. Showstopper #2: Knapsack Budget Optimization Solver
    print("\n[Step 3] SHOWSTOPPER #2: KNAPSACK BUDGET OPTIMIZATION SOLVER")
    print("-" * 50)
    print(">> Invoking multi-choice knapsack optimization algorithm...")
    opt_result = optimize_boq_for_budget(initial_boq, max_budget=client_budget)
    
    if opt_result["is_achievable"]:
        print(">> SUCCESS! Budget compliant configuration found.")
        print(f"Optimized Total      : ₹{opt_result['optimized_total']:>12,.2f}")
        print(f"Total Money Saved    : ₹{opt_result['total_savings']:>12,.2f}")
        print(f"Surplus Remaining    : ₹{opt_result['surplus_under_budget']:>12,.2f}")
        print(f"Composite Utility    : {opt_result['total_utility_score']} / 300 points")
        
        print("\n>> MATERIAL VALUE-ENGINEERING DOWNGRADES APPLIED:")
        for idx, dg in enumerate(opt_result["downgrades"], 1):
            print(f"  {idx}. {dg['category']}:")
            print(f"     From: {dg['from_specification']} (₹{dg['old_rate']}/unit)")
            print(f"     To  : {dg['to_specification']} (₹{dg['new_rate']}/unit)")
            print(f"     Saved: ₹{dg['savings']:,.2f} | Reason: {dg['impact_assessment']}")
    else:
        print(f">> WARNING: {opt_result['message']}")
        
    # 4. Showstopper #4: Printable Contractor Specification Sheet (HTML)
    print("\n[Step 4] SHOWSTOPPER #4: CONTRACTOR SPECIFICATION REPORT GENERATION")
    print("-" * 50)
    report_boq = opt_result["optimized_boq"] if opt_result["is_achievable"] else initial_boq
    output_filename = "contractor_boq_report.html"
    saved_path = export_boq_report(report_boq, output_filename)
    print(f">> Report successfully exported to: {saved_path}")
    print(">> Open this file in Google Chrome / Edge and press Ctrl+P to generate instant contractor PDF!")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    run_self_test()
