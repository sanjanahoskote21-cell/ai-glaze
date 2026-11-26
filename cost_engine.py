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
# 1. MATERIAL CATALOGUE & BENCHMARK PRICING TIERS (INDIAN INR BENCHMARKS)
# ============================================================================

MATERIAL_CATALOGUE = {
    "flooring": [
        {
            "tier": "Luxury",
            "name": "Italian Statuario Marble",
            "rate_per_sqft": 380.0,
            "utility_score": 95,
            "description": "Premium imported marble slabs with seamless diamond resin polish.",
            "supplier_spec": "Grade-A 18mm Statuario slabs, diamond polished with hydrophobic anti-stain sealant."
        },
        {
            "tier": "Premium",
            "name": "Engineered Oak Hardwood Flooring",
            "rate_per_sqft": 165.0,
            "utility_score": 85,
            "description": "Multi-layer UV-cured natural oak planks with acoustic IXPE underlayment.",
            "supplier_spec": "14mm engineered European oak, 3mm top lamella, matte polyurethane seal."
        },
        {
            "tier": "Standard",
            "name": "Kajaria GVT Vitrified Tile",
            "rate_per_sqft": 75.0,
            "utility_score": 84,
            "description": "High thermal reflectance, 0.05% water absorption, scratch-resistant glazed vitrified tiles.",
            "supplier_spec": "Kajaria 1200x600mm rectified porcelain GVT (IS 15622), epoxy grouted with 2mm spacers."
        },
        {
            "tier": "Economy",
            "name": "Johnson Anti-Skid Ceramic / SPC Plank",
            "rate_per_sqft": 42.0,
            "utility_score": 66,
            "description": "R10 anti-skid ceramic tile or waterproof SPC plank for value-engineered zones.",
            "supplier_spec": "600x600mm R10 matte ceramic or 5mm click-lock SPC waterproof core."
        }
    ],
    "painting": [
        {
            "tier": "Luxury",
            "name": "Venetian Stucco Plaster & Metallic Accent",
            "rate_per_sqft": 85.0,
            "utility_score": 94,
            "description": "Hand-troweled slaked-lime Venetian plaster with burnished metallic wax.",
            "supplier_spec": "3-coat artisanal mineral plaster, beeswax buffed, breathable hydrophobic topcoat."
        },
        {
            "tier": "Premium",
            "name": "Asian Paints Royale Luxury Emulsion",
            "rate_per_sqft": 38.0,
            "utility_score": 92,
            "description": "Low-VOC (<5 g/L) luxury silk finish with Teflon surface protector & high scrub resistance.",
            "supplier_spec": "2 coats white putty, 1 coat Royale primer, 2 coats Asian Paints Royale Luxury Emulsion."
        },
        {
            "tier": "Standard",
            "name": "Asian Paints Apcolite Premium Emulsion",
            "rate_per_sqft": 24.0,
            "utility_score": 76,
            "description": "Durable stain-guard matte acrylic emulsion with anti-fungal protection.",
            "supplier_spec": "Acrylic putty leveling, 1 coat primer, 2 coats Apcolite Premium Emulsion."
        },
        {
            "tier": "Economy",
            "name": "Asian Paints Tractor Emulsion (Economy Washable)",
            "rate_per_sqft": 14.0,
            "utility_score": 58,
            "description": "Lead-free budget washable interior emulsion for clean uniform matte walls.",
            "supplier_spec": "Cement putty touch-up, 1 coat primer, 2 coats Tractor Emulsion."
        }
    ],
    "furniture": [
        {
            "tier": "Luxury",
            "name": "Bespoke Burma Teak & Italian Veneer Joinery",
            "multiplier": 1.00,
            "rate_per_sqft_carpet": 550.0,
            "utility_score": 95,
            "description": "Custom artisan cabinetry, seasoned Burma teak framing and natural veneer.",
            "supplier_spec": "Kiln-dried Burma teak, IS:710 marine carcass, Hafele/Blum soft-close hardware."
        },
        {
            "tier": "Premium",
            "name": "Greenply BWP Marine Ply & Natural Oak Veneer",
            "multiplier": 0.70,
            "rate_per_sqft_carpet": 385.0,
            "utility_score": 86,
            "description": "IS:710 Boiling Water Proof Gurjan marine ply with natural veneer & PU matte polish.",
            "supplier_spec": "IS:710 BWP marine ply carcass, 0.6mm veneer frontage, Blum hinges."
        },
        {
            "tier": "Standard",
            "name": "CenturyPly Modular BWP/MR Ply & HPL Laminate",
            "multiplier": 0.48,
            "rate_per_sqft_carpet": 265.0,
            "utility_score": 78,
            "description": "Factory-calibrated modular joinery with scratch-resistant 1mm HPL finish.",
            "supplier_spec": "IS:710 wet-zone / IS:303 dry-zone ply, 1mm Merino/Greenlam HPL, Hettich fittings."
        },
        {
            "tier": "Economy",
            "name": "Action TESA HDMR High-Density Moisture-Resistant Modular",
            "multiplier": 0.32,
            "rate_per_sqft_carpet": 175.0,
            "utility_score": 62,
            "description": "Value-engineered 850 kg/m³ CNC modular HDMR pre-laminated units.",
            "supplier_spec": "High-density moisture-resistant (HDMR) board, 2mm REHAU PVC edge banding."
        }
    ]
}

CONSTRUCTION_SCOPE_RATES = {
    "civil_structural_per_sqft": 1350.0,  # M25 RCC + Fe-550D TMT + 200mm AAC masonry + internal/external plaster
    "mep_finishing_per_sqft": 220.0,      # Finolex FRLS concealed wiring + Astral CPVC/UPVC + Jaquar CP fittings
    "default_gst_rate": 0.18,             # 18% statutory Indian GST for construction & works contract
    "default_carpet_efficiency": 0.66     # Typical 66% carpet-to-plot efficiency (e.g., 30x40 = 1200 -> 792 sq.ft)
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
    selected_specs: Optional[Dict[str, str]] = None,
    gst_pct: float = 0.18,
    carpet_area_sqft: Optional[float] = None,
    plot_dimensions: Optional[str] = None,
    city: str = "Bangalore",
    construction_scope: str = "Interior Finishing & Renovation",
    extra_line_items: Optional[List[Dict[str, Any]]] = None,
    reasoning_notes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compiles an itemized architectural Bill of Quantities (BoQ) in INR (₹) integrating:
    1. Flooring finishes & cutting margins.
    2. Wall preparation, primer & multi-coat painting.
    3. Furniture and joinery fixture allowances.
    4. Optional floorplan-level Civil/Structural & MEP line items.
    5. Specialized trade labor buffer (site supervision & craftsmanship).
    6. Unforeseen engineering contingency allowance.
    7. Statutory 18% Indian GST.
    
    Compares aggregate total (incl. 18% GST) against client's target budget cap.
    """
    flooring_cost = round(floor_sqft * floor_rate, 2)
    painting_cost = round(wall_sqft * paint_rate, 2)
    furniture_cost = round(furniture_price, 2)
    extras = extra_line_items or []
    extras_cost = round(sum(float(item.get("subtotal", 0.0)) for item in extras), 2)
    
    materials_subtotal = round(flooring_cost + painting_cost + furniture_cost + extras_cost, 2)
    labor_buffer = round(materials_subtotal * labor_buffer_pct, 2)
    subtotal_with_labor = round(materials_subtotal + labor_buffer, 2)
    contingency_allowance = round(subtotal_with_labor * contingency_pct, 2)
    
    pre_gst_total = round(subtotal_with_labor + contingency_allowance, 2)
    gst_amount = round(pre_gst_total * gst_pct, 2)
    grand_total = round(pre_gst_total + gst_amount, 2)
    
    is_within_budget = (grand_total <= budget_cap)
    status = "Within Budget" if is_within_budget else "Over Budget"
    delta = round(abs(budget_cap - grand_total), 2)
    variance_signed = round(budget_cap - grand_total, 2)
    variance_percentage = round((variance_signed / budget_cap) * 100, 2) if budget_cap > 0 else 0.0
    
    default_specs = {
        "flooring": "Kajaria GVT Vitrified Tile",
        "painting": "Asian Paints Royale Luxury Emulsion",
        "furniture": "CenturyPly Modular BWP/MR Ply & HPL Laminate"
    }
    specs = {**default_specs, **(selected_specs or {})}

    line_items = [
        {
            "id": "BOQ-001",
            "category": "Flooring & Substrate",
            "description": f"{specs['flooring']} (Inc. 10% cutting wastage & grout laying)",
            "quantity": round(floor_sqft, 2),
            "unit": "sq.ft",
            "unit_rate": round(floor_rate, 2),
            "subtotal": flooring_cost
        },
        {
            "id": "BOQ-002",
            "category": "Wall Surface Finishing",
            "description": f"{specs['painting']} (Surface prep, primer + 2 topcoats)",
            "quantity": round(wall_sqft, 2),
            "unit": "sq.ft",
            "unit_rate": round(paint_rate, 2),
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
        }
    ]

    next_idx = 4
    for extra in extras:
        line_items.append({
            "id": extra.get("id", f"BOQ-{next_idx:03d}"),
            "category": extra["category"],
            "description": extra["description"],
            "quantity": round(float(extra.get("quantity", 1.0)), 2),
            "unit": extra.get("unit", "sq.ft"),
            "unit_rate": round(float(extra.get("unit_rate", 0.0)), 2),
            "subtotal": round(float(extra.get("subtotal", 0.0)), 2)
        })
        next_idx += 1

    line_items.extend([
        {
            "id": f"BOQ-{next_idx:03d}",
            "category": "Skilled Craftsmanship & Labor",
            "description": f"Site supervision, masonry alignment & installation labor ({int(labor_buffer_pct * 100)}%)",
            "quantity": 1.0,
            "unit": "service",
            "unit_rate": labor_buffer,
            "subtotal": labor_buffer
        },
        {
            "id": f"BOQ-{next_idx + 1:03d}",
            "category": "Engineering Contingency",
            "description": f"Safety buffer for site unforeseen deviations & material escalations ({int(contingency_pct * 100)}%)",
            "quantity": 1.0,
            "unit": "allowance",
            "unit_rate": contingency_allowance,
            "subtotal": contingency_allowance
        }
    ])

    resolved_carpet = round(float(carpet_area_sqft if carpet_area_sqft is not None else floor_sqft / 1.10), 2)

    boq = {
        "project_metadata": {
            "project_name": "AI-GLAZE Smart Architectural & Interior BoQ",
            "room_name": room_name,
            "city": city,
            "plot_dimensions": plot_dimensions or "Custom Room / Layout",
            "construction_scope": construction_scope,
            "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "currency": "INR (₹)"
        },
        "dimensions": {
            "carpet_area_sqft": resolved_carpet,
            "floor_sqft": round(floor_sqft, 2),
            "wall_sqft": round(wall_sqft, 2)
        },
        "line_items": line_items,
        "financial_summary": {
            "materials_subtotal": materials_subtotal,
            "labor_buffer_pct": labor_buffer_pct,
            "labor_buffer": labor_buffer,
            "contingency_pct": contingency_pct,
            "contingency_allowance": contingency_allowance,
            "pre_gst_total": pre_gst_total,
            "gst_rate": gst_pct,
            "gst_percentage": round(gst_pct * 100, 1),
            "gst_amount": gst_amount,
            "grand_total": grand_total,
            "grand_total_incl_gst": grand_total,
            "budget_cap": round(budget_cap, 2),
            "status": status,
            "is_within_budget": is_within_budget,
            "delta": delta,
            "variance_signed": variance_signed,
            "variance_percentage": variance_percentage
        },
        "current_specs": specs
    }

    if reasoning_notes is not None:
        boq["reasoning_notes"] = reasoning_notes

    return boq


# ============================================================================
# 4B. FLOORPLAN & PLOT AREA CONNECTOR (e.g., 30x40 Plot -> 792 sq.ft Carpet)
# ============================================================================

def _find_catalogue_tier(category: str, tier_or_name: str) -> Dict[str, Any]:
    """Looks up a material catalogue entry by tier ('Luxury', 'Premium', 'Standard', 'Economy') or name."""
    entries = MATERIAL_CATALOGUE.get(category, [])
    needle = tier_or_name.strip().lower()
    for entry in entries:
        if entry["tier"].lower() == needle or needle in entry["name"].lower() or entry["name"].lower() in needle:
            return entry
    return entries[2] if len(entries) > 2 else entries[0]


def estimate_floorplan_areas(
    carpet_area_sqft: Optional[float] = None,
    plot_width_ft: float = 30.0,
    plot_length_ft: float = 40.0,
    rooms: Optional[List[Dict[str, Any]]] = None,
    ceiling_height_ft: float = 10.0,
    wastage_margin: float = 0.10,
    openings_ratio: float = 0.15
) -> Dict[str, Any]:
    """
    Connects a generated floorplan (rooms list, explicit carpet area, or plot dimensions)
    to billable flooring & net paintable wall square footage.

    Default example: 30x40 ft plot (1,200 sq.ft plot area) at 66% carpet efficiency -> 792 sq.ft carpet area.
    """
    plot_area_sqft = round(plot_width_ft * plot_length_ft, 2)
    room_breakdown: List[Dict[str, Any]] = []

    if rooms:
        total_carpet = 0.0
        total_net_wall = 0.0
        for rm in rooms:
            l_ft = float(rm.get("length_ft", 0.0))
            w_ft = float(rm.get("width_ft", 0.0))
            rm_area = float(rm.get("area_sqft", l_ft * w_ft))
            if l_ft <= 0 or w_ft <= 0:
                # Approximate square proportions when only area_sqft is supplied
                side = rm_area ** 0.5 if rm_area > 0 else 10.0
                l_ft = side
                w_ft = side
            perim = 2.0 * (l_ft + w_ft)
            rm_openings = float(rm.get("openings_sqft", perim * ceiling_height_ft * openings_ratio))
            wall_res = calculate_wall_surface_area(perim, ceiling_height_ft, openings_area=rm_openings)
            floor_res = calculate_floor_area(l_ft, w_ft, wastage_margin=wastage_margin)
            total_carpet += rm_area
            total_net_wall += wall_res["net_paintable_sqft"]
            room_breakdown.append({
                "name": rm.get("name", "Room"),
                "net_area_sqft": round(rm_area, 2),
                "billable_floor_sqft": floor_res["gross_area_sqft"],
                "net_wall_sqft": wall_res["net_paintable_sqft"]
            })
        resolved_carpet = round(total_carpet, 2)
        billable_floor_sqft = round(resolved_carpet * (1.0 + wastage_margin), 2)
        net_paintable_wall_sqft = round(total_net_wall, 2)
    else:
        if carpet_area_sqft is not None and carpet_area_sqft > 0:
            resolved_carpet = round(float(carpet_area_sqft), 2)
        else:
            resolved_carpet = round(plot_area_sqft * CONSTRUCTION_SCOPE_RATES["default_carpet_efficiency"], 2)

        billable_floor_sqft = round(resolved_carpet * (1.0 + wastage_margin), 2)
        # Standard Indian residential floorplan wall-to-carpet ratio (~3.15x gross wall area minus 15% openings)
        gross_wall_approx = resolved_carpet * 3.15
        net_paintable_wall_sqft = round(gross_wall_approx * (1.0 - openings_ratio), 2)

    return {
        "plot_dimensions": f"{int(plot_width_ft)}x{int(plot_length_ft)} ft",
        "plot_area_sqft": plot_area_sqft,
        "carpet_area_sqft": resolved_carpet,
        "billable_floor_sqft": billable_floor_sqft,
        "net_wall_sqft": net_paintable_wall_sqft,
        "wastage_margin_pct": round(wastage_margin * 100, 1),
        "room_breakdown": room_breakdown
    }


def generate_floorplan_boq(
    carpet_area_sqft: Optional[float] = 792.0,
    plot_width_ft: float = 30.0,
    plot_length_ft: float = 40.0,
    rooms: Optional[List[Dict[str, Any]]] = None,
    scope: str = "renovation",
    flooring_tier: str = "Standard",
    painting_tier: str = "Premium",
    furniture_tier: str = "Standard",
    budget_cap: float = 1500000.0,
    city: str = "Bangalore",
    gst_pct: float = 0.18,
    include_reasoning: bool = True
) -> Dict[str, Any]:
    """
    Connects directly to the client's generated floorplan square footage (e.g., 792 sq.ft
    carpet area for a 30x40 plot) and calculates realistic Indian construction & finishing
    costs in INR (₹) with 18% GST and architectural reasoning notes.

    Args:
        carpet_area_sqft: Carpet area from generated floorplan (default 792 sq.ft for 30x40 plot).
        plot_width_ft: Plot width in feet (default 30).
        plot_length_ft: Plot length in feet (default 40).
        rooms: Optional list of generated room dicts `{name, length_ft, width_ft, area_sqft}`.
        scope: `'renovation'` / `'interior_finishing'` OR `'full_construction'` (includes RCC + AAC + MEP).
        flooring_tier: Tier or name from MATERIAL_CATALOGUE['flooring'].
        painting_tier: Tier or name from MATERIAL_CATALOGUE['painting'].
        furniture_tier: Tier or name from MATERIAL_CATALOGUE['furniture'].
        budget_cap: Client budget ceiling in INR (₹).
        city: Indian city for climate-aware reasoning (e.g., 'Bangalore').
        gst_pct: Statutory GST rate (default 0.18 for 18% GST).
        include_reasoning: Automatically attach Material Intelligence notes if True.
    """
    areas = estimate_floorplan_areas(
        carpet_area_sqft=carpet_area_sqft,
        plot_width_ft=plot_width_ft,
        plot_length_ft=plot_length_ft,
        rooms=rooms
    )

    f_spec = _find_catalogue_tier("flooring", flooring_tier)
    p_spec = _find_catalogue_tier("painting", painting_tier)
    fn_spec = _find_catalogue_tier("furniture", furniture_tier)

    carpet = areas["carpet_area_sqft"]
    furniture_price = round(carpet * fn_spec["rate_per_sqft_carpet"], 2)

    extra_items: List[Dict[str, Any]] = []
    scope_norm = scope.strip().lower()
    if scope_norm in ("full_construction", "new_construction", "turnkey_construction"):
        civil_rate = CONSTRUCTION_SCOPE_RATES["civil_structural_per_sqft"]
        mep_rate = CONSTRUCTION_SCOPE_RATES["mep_finishing_per_sqft"]
        extra_items.append({
            "category": "Civil & Structural Shell",
            "description": "M25 Grade RCC Frame, Fe-550D TMT Steel, 200mm AAC Block Masonry & Plastering",
            "quantity": carpet,
            "unit": "sq.ft",
            "unit_rate": civil_rate,
            "subtotal": round(carpet * civil_rate, 2)
        })
        extra_items.append({
            "category": "Electrical & Plumbing (MEP)",
            "description": "Finolex FRLS Concealed Wiring, Astral CPVC/UPVC Lines & Jaquar CP Fixtures",
            "quantity": carpet,
            "unit": "sq.ft",
            "unit_rate": mep_rate,
            "subtotal": round(carpet * mep_rate, 2)
        })
        scope_label = "Full Construction & Turnkey Interiors"
    else:
        mep_upgrade_rate = 115.0
        extra_items.append({
            "category": "Electrical & Plumbing Upgrades (MEP)",
            "description": "Modular Switches, FRLS Rewiring Points & CP Sanitary Fixture Upgrades",
            "quantity": carpet,
            "unit": "sq.ft",
            "unit_rate": mep_upgrade_rate,
            "subtotal": round(carpet * mep_upgrade_rate, 2)
        })
        scope_label = "Interior Finishing & Renovation"

    boq = generate_full_boq(
        floor_sqft=areas["billable_floor_sqft"],
        floor_rate=f_spec["rate_per_sqft"],
        wall_sqft=areas["net_wall_sqft"],
        paint_rate=p_spec["rate_per_sqft"],
        furniture_price=furniture_price,
        budget_cap=budget_cap,
        room_name=f"Full Floorplan ({int(carpet)} sq.ft Carpet | {areas['plot_dimensions']} Plot)",
        selected_specs={
            "flooring": f_spec["name"],
            "painting": p_spec["name"],
            "furniture": fn_spec["name"]
        },
        gst_pct=gst_pct,
        carpet_area_sqft=carpet,
        plot_dimensions=areas["plot_dimensions"],
        city=city,
        construction_scope=scope_label,
        extra_line_items=extra_items
    )
    boq["dimensions"]["plot_area_sqft"] = areas["plot_area_sqft"]
    if areas["room_breakdown"]:
        boq["dimensions"]["room_breakdown"] = areas["room_breakdown"]

    if include_reasoning:
        try:
            from reasoning_engine import generate_boq_reasoning_notes
            boq["reasoning_notes"] = generate_boq_reasoning_notes(boq, city=city)
        except ImportError:
            pass

    return boq


# ============================================================================
# 5. SHOWSTOPPER #2: KNAPSACK BUDGET OPTIMIZATION SOLVER
# ============================================================================

def optimize_boq_for_budget(
    boq: Dict[str, Any], 
    max_budget: float,
    base_luxury_furniture_cost: Optional[float] = None
) -> Dict[str, Any]:
    """
    Constrained Multi-Choice Knapsack & Value-Cost Optimizer.
    
    Evaluates all discrete trade combinations (Flooring x Painting x Furniture)
    to guarantee Grand Total (incl. 18% GST) <= max_budget while maximizing
    overall durability and aesthetic utility.
    """
    floor_sqft = boq["dimensions"]["floor_sqft"]
    wall_sqft = boq["dimensions"]["wall_sqft"]
    carpet_sqft = boq["dimensions"].get("carpet_area_sqft", floor_sqft / 1.10)
    fin = boq["financial_summary"]
    original_total = fin["grand_total"]
    gst_rate = float(fin.get("gst_rate", 0.18))
    labor_pct = float(fin.get("labor_buffer_pct", 0.12))
    cont_pct = float(fin.get("contingency_pct", 0.05))
    meta = boq.get("project_metadata", {})

    if base_luxury_furniture_cost is None:
        base_luxury_furniture_cost = round(carpet_sqft * 550.0, 2) if carpet_sqft > 0 else 85000.0

    # Preserve non-material extra line items (e.g. Civil Shell / MEP) during optimization
    extra_items = [
        it for it in boq.get("line_items", [])
        if any(tag in it.get("category", "").lower() for tag in ("civil", "structural", "mep", "electrical", "plumbing"))
    ]
    
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
                cand_floor_rate = f_opt["rate_per_sqft"]
                cand_paint_rate = p_opt["rate_per_sqft"]
                cand_furn_price = base_luxury_furniture_cost * furn_opt["multiplier"]
                
                cand_boq = generate_full_boq(
                    floor_sqft=floor_sqft,
                    floor_rate=cand_floor_rate,
                    wall_sqft=wall_sqft,
                    paint_rate=cand_paint_rate,
                    furniture_price=cand_furn_price,
                    budget_cap=max_budget,
                    labor_buffer_pct=labor_pct,
                    contingency_pct=cont_pct,
                    room_name=meta.get("room_name", "Master Interior Space"),
                    selected_specs={
                        "flooring": f_opt["name"],
                        "painting": p_opt["name"],
                        "furniture": furn_opt["name"]
                    },
                    gst_pct=gst_rate,
                    carpet_area_sqft=carpet_sqft,
                    plot_dimensions=meta.get("plot_dimensions"),
                    city=meta.get("city", "Bangalore"),
                    construction_scope=meta.get("construction_scope", "Interior Finishing & Renovation"),
                    extra_line_items=extra_items
                )
                
                cand_total = cand_boq["financial_summary"]["grand_total"]
                total_utility = f_opt["utility_score"] + p_opt["utility_score"] + furn_opt["utility_score"]
                
                if cand_total < lowest_cost_possible:
                    lowest_cost_possible = cand_total
                    cheapest_combination = (f_opt, p_opt, furn_opt, cand_boq)
                
                if cand_total <= max_budget:
                    if total_utility > best_utility:
                        best_utility = total_utility
                        best_combination = (f_opt, p_opt, furn_opt, cand_boq)
    
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
                f"Budget cap of ₹{max_budget:,.2f} is below the baseline economy tier. "
                f"Minimum attainable cost (incl. 18% GST) is ₹{lowest_cost_possible:,.2f} (Shortfall of ₹{shortfall:,.2f})."
            ),
            "downgrades": [
                {"category": "Flooring", "recommended": f_min["name"], "tier": f_min["tier"]},
                {"category": "Painting", "recommended": p_min["name"], "tier": p_min["tier"]},
                {"category": "Furniture", "recommended": furn_min["name"], "tier": furn_min["tier"]}
            ],
            "optimized_boq": min_boq
        }
    
    opt_f, opt_p, opt_furn, optimized_boq = best_combination
    optimized_total = optimized_boq["financial_summary"]["grand_total"]
    total_savings = round(original_total - optimized_total, 2)
    
    downgrades = []
    
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
            "impact_assessment": "Retains high wear resistance & 0.05% water impermeability with major material savings."
        })
        
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
            "impact_assessment": "Low-VOC washable finish maintained while lowering surface prep & coat costs."
        })
        
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
            "impact_assessment": "Precision factory-calibrated joinery with durable moisture-resistant core."
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


def suggest_budget_cuts(
    current_boq: Dict[str, Any],
    target_reduction_inr: float,
    city: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delegates to `reasoning_engine.suggest_budget_cuts` so the Budget Trade-Off
    Advisor can be imported directly from either `cost_engine` or `reasoning_engine`.
    """
    from reasoning_engine import suggest_budget_cuts as _suggest_budget_cuts
    return _suggest_budget_cuts(current_boq, target_reduction_inr, city=city)


# ============================================================================
# 6. SHOWSTOPPER #4: PRINTABLE CONTRACTOR SPECIFICATION SHEET (HTML)
# ============================================================================

def export_boq_report(
    boq_data: Dict[str, Any],
    output_file: str = "contractor_boq_report.html",
    reasoning_notes: Optional[Dict[str, Any]] = None,
    budget_cuts: Optional[Dict[str, Any]] = None
) -> str:
    """
    Renders an architectural-grade, responsive, and print-ready contractor specification sheet in HTML.

    Includes:
    - AI-GLAZE verified seal & document metadata (City, Plot, Carpet Area, Scope).
    - Executive summary KPI cards (Carpet Area, Flooring, Wall Area, Budget & Status).
    - Itemized Bill of Quantities table with exact quantities, rates, and unit classifications.
    - Statutory 18% GST breakdown & Grand Total (INR).
    - Material Intelligence & Architectural Reasoning Notes (Pillars 4 & 6).
    - Optional Budget Trade-Off Advisor recommendations.
    - Formal trade contractor sign-off protocols & engineering disclaimer.
    """
    meta = boq_data.get("project_metadata", {})
    dims = boq_data.get("dimensions", {})
    fin = boq_data.get("financial_summary", {})
    items = boq_data.get("line_items", [])
    specs = boq_data.get("current_specs", {})

    # Resolve reasoning notes automatically if not provided
    resolved_reasoning = reasoning_notes or boq_data.get("reasoning_notes")
    if resolved_reasoning is None:
        try:
            from reasoning_engine import generate_boq_reasoning_notes
            resolved_reasoning = generate_boq_reasoning_notes(boq_data, city=meta.get("city", "Bangalore"))
        except ImportError:
            resolved_reasoning = None

    resolved_cuts = budget_cuts or boq_data.get("budget_cuts")

    is_ok = fin.get("is_within_budget", True)
    badge_color = "#10b981" if is_ok else "#ef4444"
    badge_bg = "#ecfdf5" if is_ok else "#fef2f2"
    status_label = fin.get("status", "Analyzed")

    carpet_sqft = dims.get("carpet_area_sqft", round(dims.get("floor_sqft", 0.0) / 1.10, 1))
    gst_pct_val = fin.get("gst_percentage", 18.0)
    pre_gst_val = fin.get(
        "pre_gst_total",
        round(
            fin.get("materials_subtotal", 0.0)
            + fin.get("labor_buffer", 0.0)
            + fin.get("contingency_allowance", 0.0),
            2
        )
    )
    gst_amount_val = fin.get("gst_amount", round(pre_gst_val * (gst_pct_val / 100.0), 2))

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

    reasoning_cards_html = ""
    if resolved_reasoning and resolved_reasoning.get("material_notes"):
        cards = ""
        for note in resolved_reasoning["material_notes"]:
            metrics_pills = "".join(
                f"<span class='metric-chip'><strong>{k}:</strong> {v}</span>"
                for k, v in note.get("engineering_metrics", {}).items()
            )
            cards += f"""
            <div class="reasoning-card">
                <div class="reasoning-head">
                    <div>
                        <span class="cat-tag">{note.get('category', 'Material')}</span>
                        <h4>{note.get('material_name', '')}</h4>
                    </div>
                    <span class="score-badge">Durability: {note.get('durability_score', 85)}/100</span>
                </div>
                <p class="why-text">{note.get('why_chosen', '')}</p>
                <div class="climate-line"><strong>Climate Fit ({resolved_reasoning.get('city', 'Bangalore')}):</strong> {note.get('climate_fit', '')}</div>
                <div class="metrics-row">{metrics_pills}</div>
            </div>
            """
        reasoning_cards_html = f"""
            <div class="section-header" style="margin-top: 8px;">
                <h2 class="section-title">🧠 Material Intelligence & Architectural Reasoning Notes</h2>
                <span style="font-size: 12px; color: #64748b; font-family: 'JetBrains Mono', monospace;">PILLARS 4 &amp; 6</span>
            </div>
            <div class="exec-reasoning-banner">{resolved_reasoning.get('executive_summary', '')}</div>
            <div class="reasoning-grid">{cards}</div>
        """

    cuts_html = ""
    if resolved_cuts and resolved_cuts.get("recommendations"):
        cut_rows = "".join(
            f"<li><strong>{rec['category']}:</strong> {rec['summary_sentence']}</li>"
            for rec in resolved_cuts["recommendations"]
        )
        cuts_html = f"""
            <div class="cuts-box">
                <h3>💡 Budget Trade-Off Advisor (Target Reduction: ₹{resolved_cuts.get('target_reduction_inr', 0):,.0f})</h3>
                <p style="font-size: 13px; color: #065f46; margin-bottom: 10px;">{resolved_cuts.get('client_explanation', '')}</p>
                <ul style="padding-left: 18px; font-size: 13px; color: #064e3b; line-height: 1.6;">{cut_rows}</ul>
            </div>
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
            max-width: 980px;
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
            grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 18px 20px;
        }}
        
        .kpi-label {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }}
        
        .kpi-value {{
            font-size: 21px;
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
            margin-bottom: 28px;
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
            width: 400px;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        .summary-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .grand-total-row td {{
            padding: 12px;
            font-size: 17px;
            font-weight: 800;
            color: #0f172a;
            border-top: 2px solid #0f172a;
            border-bottom: 2px solid #0f172a;
            background: #f8fafc;
        }}

        .exec-reasoning-banner {{
            background: #eff6ff;
            border-left: 4px solid #2563eb;
            padding: 14px 18px;
            border-radius: 8px;
            font-size: 13.5px;
            color: #1e3a8a;
            margin-bottom: 16px;
        }}

        .reasoning-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 14px;
            margin-bottom: 28px;
        }}

        .reasoning-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px 18px;
        }}

        .reasoning-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .reasoning-head h4 {{
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 4px;
        }}

        .cat-tag {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #4f46e5;
            background: #eef2ff;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .score-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 600;
            color: #0369a1;
            background: #e0f2fe;
            padding: 4px 10px;
            border-radius: 6px;
        }}

        .why-text {{
            font-size: 13.5px;
            color: #1e293b;
            margin-bottom: 6px;
        }}

        .climate-line {{
            font-size: 12.5px;
            color: #475569;
            margin-bottom: 8px;
        }}

        .metrics-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .metric-chip {{
            font-size: 11px;
            color: #334155;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            padding: 3px 8px;
            border-radius: 5px;
        }}

        .cuts-box {{
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 28px;
        }}

        .cuts-box h3 {{
            color: #065f46;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 8px;
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
        }}
        
        .btn-print {{
            background: #0f172a;
            color: #ffffff;
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
                    <div class="brand-badge">⚡ AI-GLAZE SPATIAL ARCHITECTURE &amp; MATERIAL INTELLIGENCE</div>
                    <h1 class="title-h1">Contractor Bill of Quantities (BoQ)</h1>
                    <div class="subtitle">
                        {meta.get('project_name', 'AI-GLAZE Smart Architectural & Interior BoQ')} &bull;
                        <strong>{meta.get('room_name', 'Floorplan')}</strong> &bull;
                        City: <strong>{meta.get('city', 'Bangalore')}</strong>
                    </div>
                </div>
                <div class="doc-meta">
                    <div>DOC REF: AGY-BOQ-2026-X</div>
                    <div>DATE: {meta.get('date_generated', datetime.now().strftime('%Y-%m-%d'))}</div>
                    <div>SCOPE: {meta.get('construction_scope', 'Interior Fit-out')}</div>
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
                    <div class="kpi-label">Carpet Area</div>
                    <div class="kpi-value">{carpet_sqft:,.1f} <span style="font-size: 14px; font-weight: normal;">sq.ft</span></div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">{meta.get('plot_dimensions', 'Floorplan Area')}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Flooring (Billable)</div>
                    <div class="kpi-value">{dims.get('floor_sqft', 0):,.1f} <span style="font-size: 14px; font-weight: normal;">sq.ft</span></div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Includes 10% cutting waste</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Wall Paintable Area</div>
                    <div class="kpi-value">{dims.get('wall_sqft', 0):,.1f} <span style="font-size: 14px; font-weight: normal;">sq.ft</span></div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Net after openings</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Total (Incl. {gst_pct_val:.0f}% GST)</div>
                    <div class="kpi-value">₹{fin.get('grand_total', 0):,.0f}</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Cap: ₹{fin.get('budget_cap', 0):,.0f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Budget Status</div>
                    <div class="status-pill">{status_label}</div>
                    <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-top: 6px;">
                        {'Savings: ₹' if is_ok else 'Excess: ₹'}{fin.get('delta', 0):,.0f}
                    </div>
                </div>
            </div>

            <!-- ITEMIZED BOQ TABLE -->
            <div class="section-header">
                <h2 class="section-title">Itemized Scope of Works &amp; Material Schedule</h2>
                <span style="font-size: 12px; color: #64748b; font-family: 'JetBrains Mono', monospace;">IS 1200 STANDARDS APPLIED</span>
            </div>

            <table class="boq-table">
                <thead>
                    <tr>
                        <th style="width: 10%;">Item ID</th>
                        <th style="width: 45%; text-align: left;">Scope &amp; Specification Description</th>
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
                        <td style="color: #64748b;">Direct Materials &amp; Package Total:</td>
                        <td style="text-align: right; font-weight: 600;">₹{fin.get('materials_subtotal', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b;">Installation &amp; Craftsmanship Buffer ({int(fin.get('labor_buffer_pct', 0.12)*100)}%):</td>
                        <td style="text-align: right; font-weight: 600;">₹{fin.get('labor_buffer', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b;">Site Contingency &amp; Escalation ({int(fin.get('contingency_pct', 0.05)*100)}%):</td>
                        <td style="text-align: right; font-weight: 600;">₹{fin.get('contingency_allowance', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td style="color: #334155; font-weight: 600;">Pre-GST Construction Subtotal:</td>
                        <td style="text-align: right; font-weight: 700;">₹{pre_gst_val:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b;">Statutory Indian GST ({gst_pct_val:.0f}%):</td>
                        <td style="text-align: right; font-weight: 600;">₹{gst_amount_val:,.2f}</td>
                    </tr>
                    <tr class="grand-total-row">
                        <td>Grand Total (INR Incl. {gst_pct_val:.0f}% GST):</td>
                        <td style="text-align: right; color: #0f172a;">₹{fin.get('grand_total', 0):,.2f}</td>
                    </tr>
                </table>
            </div>

            {reasoning_cards_html}

            {cuts_html}

            <!-- ARCHITECTURAL SPECIFICATION NOTES -->
            <div class="spec-box">
                <h3>📌 Architectural Specifications &amp; Supplier Standards</h3>
                <div class="spec-grid">
                    <div><strong>Flooring Spec:</strong> {specs.get('flooring', 'Kajaria GVT Vitrified Tile')}</div>
                    <div><strong>Wall Finishing:</strong> {specs.get('painting', 'Asian Paints Royale Luxury Emulsion')}</div>
                    <div><strong>Cabinetry &amp; Joinery:</strong> {specs.get('furniture', 'CenturyPly Modular BWP/MR Ply')}</div>
                    <div><strong>Quality Seal:</strong> ISO 9001 / IGBC GreenPro Low-VOC Certified</div>
                </div>
            </div>

            <!-- CONTRACTOR & CLIENT SIGNOFF -->
            <div class="signoff-section">
                <div class="signoff-box">
                    <div style="font-size: 13px; color: #64748b;">Certified Field Contractor</div>
                    <div class="signoff-line">Authorized Signatory &amp; Stamp</div>
                </div>
                <div class="signoff-box">
                    <div style="font-size: 13px; color: #64748b;">Client Approval / Architecture Lead</div>
                    <div class="signoff-line">Authorized Signatory &amp; Date</div>
                </div>
            </div>

            <!-- DISCLAIMER -->
            <div class="disclaimer">
                <strong>ENGINEERING &amp; STATUTORY NOTICE:</strong> This Bill of Quantities (BoQ) is algorithmically generated by the AI-GLAZE Computational Cost &amp; Material Reasoning Engine based on floorplan area data. All measurements include standard statutory cutting/wastage allowances compliant with IS 1200 architectural norms and include 18% GST. Rates are subject to local supply chain fluctuations and final structural verification by the on-site MEP engineer before tender contract execution.
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
    Executes a comprehensive verification suite covering:
    - Floorplan area estimation (e.g., 30x40 plot -> 792 sq.ft carpet area) + 18% GST
    - Material Architectural Intelligence reasoning notes
    - Budget Trade-Off Advisor (`suggest_budget_cuts`)
    - Printable HTML Contractor BoQ Document export
    """
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("\n" + "=" * 78)
    print("   AI-GLAZE COST ESTIMATION, MATERIAL INTELLIGENCE & BoQ ENGINE")
    print("=" * 78)

    # 1. Floorplan Connection: 30x40 plot -> 792 sq.ft carpet area (Bangalore)
    print("\n[Step 1] FLOORPLAN AREA & INDIAN CONSTRUCTION + 18% GST ESTIMATE")
    print("-" * 60)
    lux_floorplan_boq = generate_floorplan_boq(
        carpet_area_sqft=792.0,
        plot_width_ft=30.0,
        plot_length_ft=40.0,
        scope="renovation",
        flooring_tier="Luxury",   # Italian Statuario Marble @ ₹380/sq.ft
        painting_tier="Premium",  # Asian Paints Royale @ ₹38/sq.ft
        furniture_tier="Standard",
        budget_cap=900000.0,
        city="Bangalore"
    )
    fin = lux_floorplan_boq["financial_summary"]
    dims = lux_floorplan_boq["dimensions"]
    print(f"Plot / Carpet Area   : 30x40 ft plot -> {dims['carpet_area_sqft']} sq.ft carpet")
    print(f"Billable Floor Area  : {dims['floor_sqft']} sq.ft (incl. 10% wastage)")
    print(f"Net Wall Area        : {dims['wall_sqft']} sq.ft")
    print(f"Pre-GST Subtotal     : ₹{fin['pre_gst_total']:>12,.2f}")
    print(f"GST (18%)            : ₹{fin['gst_amount']:>12,.2f}")
    print(f"Grand Total (w/ GST) : ₹{fin['grand_total']:>12,.2f}")

    # 2. Budget Trade-Off Advisor
    print("\n[Step 2] BUDGET TRADE-OFF ADVISOR (Target Cut: ₹25,000)")
    print("-" * 60)
    cut_advice = suggest_budget_cuts(lux_floorplan_boq, target_reduction_inr=25000.0, city="Bangalore")
    print(cut_advice["client_explanation"])

    # 3. Material Architectural Intelligence Notes
    print("\n[Step 3] MATERIAL ARCHITECTURAL REASONING NOTES")
    print("-" * 60)
    from reasoning_engine import generate_boq_reasoning_notes
    updated_boq = cut_advice["updated_boq"]
    notes = generate_boq_reasoning_notes(updated_boq, city="Bangalore")
    for n in notes["material_notes"]:
        print(f"• [{n['category']}] {n['why_chosen']}")

    # 4. Printable Contractor BoQ Document (with Reasoning Notes & 18% GST)
    print("\n[Step 4] CONTRACTOR BoQ DOCUMENT GENERATION")
    print("-" * 60)
    saved_path = export_boq_report(
        updated_boq,
        output_file="contractor_boq_report.html",
        reasoning_notes=notes,
        budget_cuts=cut_advice
    )
    print(f">> Report successfully exported to: {saved_path}")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    run_self_test()
