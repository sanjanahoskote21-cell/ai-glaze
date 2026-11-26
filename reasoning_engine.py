"""
AI-GLAZE - Material Intelligence & Architectural Reasoning Engine (Pillars 4 & 6)
Module: reasoning_engine.py
Project: AI-GLAZE (AI-Powered Spatial Planning & Interior Architecture)

Provides:
1. Engineering & architectural justification for chosen construction/interior materials
   (thermal reflectance, water absorption, VOC safety, scrub/scratch resistance,
   IS code compliance, and INR/sq.ft cost-effectiveness vs alternatives).
2. Climate-aware reasoning notes tied to the client's floorplan & Contractor BoQ.
3. Smart Budget Trade-Off Advisor (`suggest_budget_cuts`) that recommends minimum-compromise
   material swaps to achieve a target INR reduction and computes exact savings.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# 1. ARCHITECTURAL & ENGINEERING MATERIAL INTELLIGENCE DATABASE
# ============================================================================

MATERIAL_INTELLIGENCE_DB: Dict[str, List[Dict[str, Any]]] = {
    "flooring": [
        {
            "id": "fl_italian_marble",
            "tier": "Luxury",
            "name": "Italian Statuario Marble",
            "aliases": [
                "Italian Statuario Marble Finish",
                "Italian Marble",
                "Statuario Marble",
                "Italian Carrara Marble",
                "Italian Carrara Polished Marble",
            ],
            "rate_per_sqft": 380.0,
            "utility_score": 95,
            "durability_score": 88,
            "thermal_reflectance": "Moderate-High (SRI ~62); naturally cool underfoot",
            "water_absorption_pct": 0.40,
            "scratch_resistance": "Mohs 3-4 (soft calcite; requires periodic diamond polishing & sealant)",
            "is_code": "IS 1130 (Marble Slabs)",
            "supplier_spec": "Grade-A 18mm Statuario/Carrara slabs, epoxy-filled, diamond honed & hydrophobic sealed.",
            "climate_notes": {
                "Bangalore": "Stays cool in Bangalore summers, though porous veins require annual sealing before monsoon.",
                "Mumbai": "High coastal humidity increases risk of moisture staining without strict underside waterproofing.",
                "Delhi": "High thermal mass keeps interiors cool during peak 45°C summer afternoons.",
                "Chennai": "Cool underfoot in tropical heat, requires anti-stain impregnation.",
                "Default": "Prestigious natural veining; requires periodic re-polishing and stain care."
            },
            "summary_reason": (
                "Selected for iconic book-matched natural veining, cool tactile mass, and flagship luxury aesthetics; "
                "requires periodic hydrophobic sealing due to ~0.40% natural porosity."
            )
        },
        {
            "id": "fl_engineered_oak",
            "tier": "Premium",
            "name": "Engineered Oak Hardwood Flooring",
            "aliases": [
                "Engineered Oak",
                "Hardwood Flooring",
                "Action TESA Engineered Oak Wood",
                "Action TESA Engineered Oak Flooring",
            ],
            "rate_per_sqft": 165.0,
            "utility_score": 85,
            "durability_score": 82,
            "thermal_reflectance": "Low thermal conductivity; warm underfoot insulation",
            "water_absorption_pct": 0.80,
            "scratch_resistance": "UV-cured aluminum oxide matte wear layer (AC4 commercial grade)",
            "is_code": "EN 13489 / Moisture-balanced multi-ply core",
            "supplier_spec": "14mm engineered European oak, 3mm top lamella, acoustic IXPE underlayment.",
            "climate_notes": {
                "Bangalore": "Multi-ply cross-laminated core resists seasonal swelling during Bangalore's monsoon.",
                "Mumbai": "Recommended only for air-conditioned bedrooms due to coastal humidity.",
                "Delhi": "Provides winter warmth and acoustic dampening in multi-storey residences.",
                "Chennai": "Use with moisture vapor barrier in coastal climate.",
                "Default": "Biophilic warmth and acoustic comfort with stronger dimensional stability than solid wood."
            },
            "summary_reason": (
                "Chosen for acoustic warmth, low thermal conductivity in bedrooms, and multi-ply dimensional stability "
                "compared to solid timber."
            )
        },
        {
            "id": "fl_kajaria_gvt",
            "tier": "Standard",
            "name": "Kajaria GVT Vitrified Tile",
            "aliases": [
                "Vitrified Glazed Porcelain Tiles (GVT)",
                "Kajaria Vitrified",
                "Kajaria GVT",
                "GVT Vitrified Tile",
                "Kajaria Double-Charged Vitrified Tile",
                "Kajaria Glazed Vitrified Tiles (GVT)",
            ],
            "rate_per_sqft": 75.0,
            "utility_score": 84,
            "durability_score": 94,
            "thermal_reflectance": "High thermal reflectance (light-bodied glazed surface reduces indoor heat gain)",
            "water_absorption_pct": 0.05,
            "scratch_resistance": "Mohs 6-7 / PEI Class IV-V high abrasion & scratch resistance",
            "is_code": "IS 15622 (Group BIa Porcelain Vitrified Tiles)",
            "supplier_spec": "Kajaria 1200x600mm rectified GVT vitrified slabs, epoxy grouted with 2mm spacers.",
            "climate_notes": {
                "Bangalore": "High thermal reflectance for Bangalore's climate and 0.05% water absorption handles monsoon dampness effortlessly.",
                "Mumbai": "Zero-seepage 0.05% water absorption prevents coastal efflorescence and fungal grout discoloration.",
                "Delhi": "High Mohs 6-7 scratch resistance withstands abrasive summer dust without dulling.",
                "Chennai": "Reflective light-toned vitrified body lowers ambient floor heat in hot coastal weather.",
                "Default": "Impervious 0.05% water absorption, zero sealing maintenance, and exceptional lifecycle durability."
            },
            "summary_reason": (
                "High thermal reflectance for {city}'s climate, 0.05% low water absorption, scratch resistance (Mohs 6-7), "
                "and ₹75/sq.ft cost-effectiveness compared to Italian Marble (₹380/sq.ft)."
            )
        },
        {
            "id": "fl_ceramic_antiskid",
            "tier": "Economy",
            "name": "Johnson Anti-Skid Ceramic / SPC Plank",
            "aliases": ["Ceramic Anti-Skid / Luxury Vinyl Planks (LVP)", "Anti-Skid Ceramic", "SPC Vinyl"],
            "rate_per_sqft": 42.0,
            "utility_score": 66,
            "durability_score": 76,
            "thermal_reflectance": "Moderate reflectance with R10 anti-slip micro-texture",
            "water_absorption_pct": 0.50,
            "scratch_resistance": "PEI Class III glazed wear layer / 0.5mm rigid SPC wear coat",
            "is_code": "IS 15622 (Group BIIa) / DIN 51130 R10",
            "supplier_spec": "600x600mm R10 matte anti-skid ceramic or 5mm click-lock waterproof SPC.",
            "climate_notes": {
                "Bangalore": "R10 slip resistance provides safe footing in utility, balcony, and budget-optimized zones.",
                "Mumbai": "Waterproof SPC/ceramic core prevents monsoon warping.",
                "Delhi": "Easy wet-mop cleaning against heavy particulate dust.",
                "Chennai": "R10 anti-skid glaze stays safe in humid conditions.",
                "Default": "Value-engineered anti-slip surface with rapid installation and lowest capital cost."
            },
            "summary_reason": (
                "Chosen for R10 anti-skid safety, rapid dry/wet installation, and maximum capital efficiency at ₹42/sq.ft."
            )
        }
    ],
    "painting": [
        {
            "id": "pt_venetian_stucco",
            "tier": "Luxury",
            "name": "Venetian Stucco Plaster & Metallic Accent",
            "aliases": ["Venetian Stucco", "Venetian Plaster & Metallic Accent"],
            "rate_per_sqft": 85.0,
            "utility_score": 94,
            "durability_score": 90,
            "voc_level": "Zero-VOC mineral slaked lime base",
            "scrub_resistance": "Beeswax burnished hydrophobic topcoat (damp-wipe cleanable)",
            "special_protection": "Natural alkaline lime resists mold growth & creates marble-like depth",
            "is_code": "EN 13300 Class 2 / Artisanal Lime Plaster Spec",
            "supplier_spec": "3-coat hand-troweled slaked lime Venetian plaster with beeswax seal.",
            "climate_notes": {
                "Bangalore": "Breathable mineral lime regulates indoor humidity across Bangalore's wet-dry seasons.",
                "Mumbai": "Breathable vapor-permeable coat prevents blistered paint under coastal humidity.",
                "Delhi": "Static-free mineral finish resists dust adhesion.",
                "Chennai": "Vapor-permeable lime inhibits damp blistering.",
                "Default": "Bespoke artisanal sheen with breathable mineral longevity."
            },
            "summary_reason": (
                "Chosen for artisanal multi-layered depth, breathable zero-VOC mineral lime base, and natural anti-mold alkalinity."
            )
        },
        {
            "id": "pt_asian_royale",
            "tier": "Premium",
            "name": "Asian Paints Royale Luxury Emulsion",
            "aliases": [
                "Royal Luxury Silk Emulsion (Teflon Coated)",
                "Asian Paints Royale",
                "Asian Paints Royale Luxury Silk",
                "Asian Paints Royale Velvet Texture",
            ],
            "rate_per_sqft": 38.0,
            "utility_score": 92,
            "durability_score": 93,
            "voc_level": "Low VOC (<5 g/L, environmentally safe & GreenPro certified)",
            "scrub_resistance": "High scrub resistance (>10,000 wet scrub cycles, Class 1 washability)",
            "special_protection": "Teflon surface protector repels household stains, grease, and microbial growth",
            "is_code": "IS 15489 / IGBC GreenPro Low-VOC Standard",
            "supplier_spec": "2 coats JK/Birla white wall putty + 1 coat Royale Primer + 2 coats Asian Paints Royale Luxury Emulsion.",
            "climate_notes": {
                "Bangalore": "Anti-fungal barrier and Teflon stain guard protect walls through Bangalore's monsoon humidity.",
                "Mumbai": "High moisture-barrier resin prevents dampness patches in coastal air.",
                "Delhi": "Teflon surface protector lets soot and dust wipe clean without burnishing the sheen.",
                "Chennai": "UV-stable pigments prevent fading under strong tropical sunlight.",
                "Default": "Low VOC indoor air safety paired with Teflon stain-repellent washability."
            },
            "summary_reason": (
                "Low VOC (environmentally safe, <5 g/L), Teflon surface protector with high scrub resistance, "
                "and anti-fungal barrier at ₹38/sq.ft."
            )
        },
        {
            "id": "pt_apcolite_premium",
            "tier": "Standard",
            "name": "Asian Paints Apcolite Premium Emulsion",
            "aliases": ["Premium Interior Acrylic Emulsion", "Apcolite Premium Emulsion"],
            "rate_per_sqft": 24.0,
            "utility_score": 76,
            "durability_score": 80,
            "voc_level": "Low-VOC water-based acrylic formulation (<30 g/L)",
            "scrub_resistance": "Good stain guard & damp-cloth washability (Class 2)",
            "special_protection": "Fungus & mildew resistant acrylic film with smooth matte finish",
            "is_code": "IS 15489 (Interior Acrylic Emulsion)",
            "supplier_spec": "Acrylic putty leveling + 1 coat water-thinnable primer + 2 coats Apcolite Premium Emulsion.",
            "climate_notes": {
                "Bangalore": "Balanced breathability and fungal protection for everyday residential interiors.",
                "Mumbai": "Fungus-resistant acrylic binder handles monsoon humidity well.",
                "Delhi": "Smooth matte finish masks minor masonry undulations.",
                "Chennai": "Color-fast acrylic latex suited for warm interiors.",
                "Default": "Reliable washability and smooth matte coverage at a balanced ₹24/sq.ft rate."
            },
            "summary_reason": (
                "Chosen for balanced stain resistance, anti-fungal acrylic binder, and cost-effective ₹24/sq.ft finish."
            )
        },
        {
            "id": "pt_tractor_emulsion",
            "tier": "Economy",
            "name": "Asian Paints Tractor Emulsion (Economy Washable)",
            "aliases": ["Standard Washable Acrylic Distemper / Emulsion", "Tractor Emulsion"],
            "rate_per_sqft": 14.0,
            "utility_score": 58,
            "durability_score": 65,
            "voc_level": "Water-based low-odor acrylic emulsion (lead & heavy-metal free)",
            "scrub_resistance": "Light dry/damp wiping durability",
            "special_protection": "Smooth uniform matte coverage upgrading over traditional chalk distemper",
            "is_code": "IS 428 / Economical Interior Emulsion Spec",
            "supplier_spec": "1 coat cement primer + 2 coats Tractor Emulsion over putty touch-up.",
            "climate_notes": {
                "Bangalore": "Clean, breathable matte finish suited for low-traffic bedrooms and ceilings.",
                "Mumbai": "Better moisture adhesion than traditional distemper.",
                "Delhi": "Economical fresh coat for quick handover or rental optimization.",
                "Chennai": "Light pastel tones reflect interior light effectively.",
                "Default": "Most economical lead-free emulsion option delivering uniform matte aesthetics."
            },
            "summary_reason": (
                "Chosen for lead-free uniform matte finish and 60%+ material cost reduction compared to luxury emulsions."
            )
        }
    ],
    "furniture": [
        {
            "id": "fn_teak_bespoke",
            "tier": "Luxury",
            "name": "Bespoke Burma Teak & Italian Veneer Joinery",
            "aliases": ["Bespoke Teak Wood & Italian Nappa Leather Package", "Bespoke Teak Wood Package"],
            "multiplier": 1.00,
            "rate_per_sqft_carpet": 550.0,
            "utility_score": 95,
            "durability_score": 96,
            "core_spec": "Seasoned Burma Teak solid framing + IS:710 BWP marine ply carcass",
            "hardware_spec": "Hafele / Blum soft-close concealed channels & hinges (80,000 cycles)",
            "is_code": "IS 710 (Marine Ply) & IS 1326 (Seasoned Teak)",
            "climate_notes": {
                "Bangalore": "Natural teak oils resist termite attack and monsoon swelling across decades.",
                "Mumbai": "BWP marine carcass prevents coastal delamination.",
                "Delhi": "Kiln-seasoned wood (<10% moisture) avoids dry-heat cracking.",
                "Chennai": "High natural oil content resists tropical humidity and borers.",
                "Default": "Heirloom structural joinery with zero particleboard swelling risk."
            },
            "summary_reason": (
                "Chosen for heirloom structural rigidity, natural termite-resistant teak oils, and 80,000-cycle soft-close hardware."
            )
        },
        {
            "id": "fn_oak_marine",
            "tier": "Premium",
            "name": "Greenply BWP Marine Ply & Natural Oak Veneer",
            "aliases": ["Solid Oak & High-Density Performance Fabric Package", "BWP Marine Ply & Veneer"],
            "multiplier": 0.70,
            "rate_per_sqft_carpet": 385.0,
            "utility_score": 86,
            "durability_score": 90,
            "core_spec": "IS:710 Boiling Water Proof (BWP) Gurjan Marine Plywood + 0.6mm natural veneer",
            "hardware_spec": "Blum / Hettich soft-close hardware, PU matte polish",
            "is_code": "IS 710:2010 (BWP Grade Marine Plywood)",
            "climate_notes": {
                "Bangalore": "IS:710 BWP boiling-water-proof glue line guarantees zero delamination in kitchens & wardrobes.",
                "Mumbai": "Ideal for coastal wet zones and kitchens due to 72-hour boiling water resistance.",
                "Delhi": "Low-emission E1/E0 resin bonding protects indoor air quality.",
                "Chennai": "Termite- and borer-proof Gurjan core holds screw grip firmly.",
                "Default": "Delivers 95% of solid-wood durability at 30% lower cost than bespoke teak."
            },
            "summary_reason": (
                "Chosen for IS:710 Boiling Water Proof Gurjan marine core, borer resistance, and superior screw-holding strength."
            )
        },
        {
            "id": "fn_modular_bwp",
            "tier": "Standard",
            "name": "CenturyPly Modular BWP/MR Ply & HPL Laminate",
            "aliases": ["Modular Engineered Wood (BWP Grade) Package", "Modular BWP Laminate"],
            "multiplier": 0.48,
            "rate_per_sqft_carpet": 265.0,
            "utility_score": 78,
            "durability_score": 85,
            "core_spec": "IS:710 BWP wet-zone carcass + IS:303 MR dry-zone ply with 1mm Merino/Greenlam HPL",
            "hardware_spec": "Hettich soft-close hinges & telescopic channels with 2mm PVC edge banding",
            "is_code": "IS 710 / IS 303 / IS 2046 (HPL Laminates)",
            "climate_notes": {
                "Bangalore": "1mm high-pressure laminate (HPL) seals edges against monsoon humidity and scratches.",
                "Mumbai": "BWP carcass in kitchen/vanity zones prevents moisture swelling.",
                "Delhi": "Scratch- and heat-resistant HPL cleans effortlessly in dusty conditions.",
                "Chennai": "2mm machine-pressed PVC edge banding blocks humid air ingress.",
                "Default": "Factory-calibrated modular accuracy with high scratch resistance and half the cost of luxury joinery."
            },
            "summary_reason": (
                "Chosen for factory-calibrated IS:710/303 plywood carcass, scratch-proof 1mm HPL laminate, and zero-maintenance wipe-clean surfaces."
            )
        },
        {
            "id": "fn_hdmr_flatpack",
            "tier": "Economy",
            "name": "Action TESA HDMR High-Density Moisture-Resistant Modular",
            "aliases": ["Minimalist High-Density Particle / Flat-Pack Modular", "HDMR Modular"],
            "multiplier": 0.32,
            "rate_per_sqft_carpet": 175.0,
            "utility_score": 62,
            "durability_score": 70,
            "core_spec": "850 kg/m³ High-Density Moisture-Resistant (HDMR) board with pre-lam finish",
            "hardware_spec": "Standard hydraulic hinges & 2mm REHAU PVC edge banding",
            "is_code": "IS 12406 / High-Density Fiberboard Spec",
            "climate_notes": {
                "Bangalore": "Moisture-resistant HDMR core outperforms standard particleboard in humid weather.",
                "Mumbai": "Use strictly in dry bedroom wardrobes; keep BWP ply under wet sinks.",
                "Delhi": "Smooth CNC-routed surface resists warping in dry summer heat.",
                "Chennai": "High-density resin core prevents fungal decay in dry zones.",
                "Default": "Rapid CNC modular assembly reducing joinery budget by up to 68%."
            },
            "summary_reason": (
                "Chosen for 850 kg/m³ high-density moisture-resistant CNC precision and rapid installation at economy pricing."
            )
        }
    ]
}


# ============================================================================
# 2. LOOKUP & NORMALIZATION HELPERS
# ============================================================================

def _find_material_entry(
    category: str,
    material_name: Optional[str] = None,
    rate_per_sqft: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """Matches a material name (or closest rate) against MATERIAL_INTELLIGENCE_DB."""
    entries = MATERIAL_INTELLIGENCE_DB.get(category, [])
    if not entries:
        return None

    if material_name:
        needle = material_name.strip().lower()
        for entry in entries:
            candidates = [entry["name"].lower()] + [a.lower() for a in entry.get("aliases", [])]
            if any(c == needle or c in needle or needle in c for c in candidates):
                return entry
        keyword_map = {
            "flooring": [("marble", 0), ("statuario", 0), ("carrara", 0), ("oak", 1), ("hardwood", 1), ("kajaria", 2), ("vitrified", 2), ("gvt", 2), ("porcelain", 2), ("ceramic", 3), ("vinyl", 3), ("spc", 3)],
            "painting": [("venetian", 0), ("stucco", 0), ("royale", 1), ("silk", 1), ("teflon", 1), ("velvet", 1), ("apcolite", 2), ("acrylic", 2), ("tractor", 3), ("distemper", 3)],
            "furniture": [("teak", 0), ("nappa", 0), ("oak", 1), ("veneer", 1), ("marine", 2), ("bwp", 2), ("modular", 2), ("hdmr", 3), ("particle", 3)]
        }
        for kw, idx in keyword_map.get(category, []):
            if kw in needle and idx < len(entries):
                return entries[idx]

    if rate_per_sqft is not None and category in ("flooring", "painting"):
        return min(entries, key=lambda e: abs(e["rate_per_sqft"] - float(rate_per_sqft)))

    return entries[2] if len(entries) > 2 else entries[0]


def _get_climate_note(entry: Dict[str, Any], city: str) -> str:
    climate_notes = entry.get("climate_notes", {})
    for k, v in climate_notes.items():
        if k.lower() == city.strip().lower():
            return v
    return climate_notes.get("Default", "")


# ============================================================================
# 3. MATERIAL ARCHITECTURAL INTELLIGENCE EXPLAINER
# ============================================================================

def explain_material_choice(
    category: str,
    material_name: str,
    rate_per_sqft: Optional[float] = None,
    city: str = "Bangalore",
    room_type: str = "Floorplan Interiors",
    area_sqft: Optional[float] = None,
    alternative_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a professional civil & architectural engineering explanation for
    why a given material was selected for the client's floorplan.
    """
    cat = category.lower().strip()
    if "floor" in cat:
        cat_key = "flooring"
    elif "paint" in cat or "wall" in cat:
        cat_key = "painting"
    else:
        cat_key = "furniture"

    entry = _find_material_entry(cat_key, material_name, rate_per_sqft)
    if entry is None:
        return {
            "category": category,
            "material_name": material_name,
            "why_chosen": f"Why {material_name} was chosen: Engineered to meet Indian IS 1200 quality and durability benchmarks for {city}.",
            "engineering_metrics": {},
            "climate_fit": f"Suitable for {city}'s residential conditions.",
            "cost_comparison": "Benchmarked against local market rates.",
            "supplier_spec": material_name,
            "is_code": "IS 1200"
        }

    display_name = entry["name"]
    effective_rate = float(rate_per_sqft) if rate_per_sqft is not None else float(entry.get("rate_per_sqft", entry.get("rate_per_sqft_carpet", 0.0)))
    climate_fit = _get_climate_note(entry, city)

    entries = MATERIAL_INTELLIGENCE_DB[cat_key]
    alt_entry = None
    if alternative_name:
        alt_entry = _find_material_entry(cat_key, alternative_name)
    if alt_entry is None or alt_entry["id"] == entry["id"]:
        alt_entry = entries[0] if entry["id"] != entries[0]["id"] else entries[2]

    if cat_key == "flooring":
        metrics = {
            "Thermal Reflectance": entry["thermal_reflectance"],
            "Water Absorption": f"{entry['water_absorption_pct']:.2f}% (IS 15622)",
            "Scratch & Abrasion Resistance": entry["scratch_resistance"],
            "Durability Score": f"{entry['durability_score']}/100",
            "Standard": entry["is_code"]
        }
        alt_rate = alt_entry["rate_per_sqft"]
        if effective_rate < alt_rate:
            savings_pct = round(((alt_rate - effective_rate) / alt_rate) * 100, 1)
            cost_comp = f"₹{effective_rate:,.0f}/sq.ft vs {alt_entry['name']} (₹{alt_rate:,.0f}/sq.ft) — {savings_pct}% lower material cost"
            if area_sqft:
                delta_total = (alt_rate - effective_rate) * area_sqft
                cost_comp += f" (saves ₹{delta_total:,.0f} on {area_sqft:,.0f} sq.ft)"
        else:
            cost_comp = f"₹{effective_rate:,.0f}/sq.ft flagship luxury spec (vs ₹{alt_rate:,.0f}/sq.ft for {alt_entry['name']})"

        if entry["id"] == "fl_kajaria_gvt":
            why_chosen = (
                f"Why {display_name} was chosen: High thermal reflectance for {city}'s climate, "
                f"{entry['water_absorption_pct']:.2f}% low water absorption, scratch resistance ({entry['scratch_resistance'].split('/')[0].strip()}), "
                f"and ₹{effective_rate:,.0f}/sq.ft cost-effectiveness compared to {alt_entry['name']} (₹{alt_rate:,.0f}/sq.ft)."
            )
        else:
            why_chosen = f"Why {display_name} was chosen: {entry['summary_reason'].format(city=city)} ({cost_comp})."

    elif cat_key == "painting":
        metrics = {
            "VOC Safety": entry["voc_level"],
            "Scrub Resistance": entry["scrub_resistance"],
            "Surface Protection": entry["special_protection"],
            "Durability Score": f"{entry['durability_score']}/100",
            "Standard": entry["is_code"]
        }
        alt_rate = alt_entry["rate_per_sqft"]
        cost_comp = f"₹{effective_rate:,.0f}/sq.ft vs {alt_entry['name']} (₹{alt_rate:,.0f}/sq.ft)"
        if entry["id"] == "pt_asian_royale":
            why_chosen = (
                f"Why {display_name} was chosen: Low VOC (environmentally safe, <5 g/L), "
                f"Teflon surface protector with high scrub resistance, and anti-fungal shield tailored for {city}'s climate."
            )
        else:
            why_chosen = f"Why {display_name} was chosen: {entry['summary_reason']} ({cost_comp})."

    else:
        metrics = {
            "Core Specification": entry["core_spec"],
            "Hardware & Fittings": entry["hardware_spec"],
            "Durability Score": f"{entry['durability_score']}/100",
            "Standard": entry["is_code"]
        }
        own_rate = entry.get("rate_per_sqft_carpet", 0)
        cost_comp = f"Tier {entry['tier']} ({int(entry['multiplier']*100)}% of luxury package; ~₹{own_rate:,.0f}/sq.ft carpet benchmark)"
        why_chosen = f"Why {display_name} was chosen: {entry['summary_reason']} Suitable for {room_type} in {city}."

    return {
        "category": cat_key.title(),
        "material_name": display_name,
        "tier": entry["tier"],
        "rate_per_sqft": effective_rate,
        "why_chosen": why_chosen,
        "engineering_metrics": metrics,
        "climate_fit": climate_fit,
        "cost_comparison": cost_comp,
        "supplier_spec": entry.get("supplier_spec") or f"{entry.get('core_spec', '')}; {entry.get('hardware_spec', '')}".strip("; "),
        "is_code": entry["is_code"],
        "durability_score": entry["durability_score"],
        "utility_score": entry["utility_score"]
    }


def generate_boq_reasoning_notes(
    boq_data: Dict[str, Any],
    city: Optional[str] = None,
    floorplan_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Produces complete Architectural & Material Reasoning Notes for a generated BoQ.
    Integrates directly into the Contractor BoQ Document tab and HTML report.
    """
    meta = boq_data.get("project_metadata", {})
    dims = boq_data.get("dimensions", {})
    specs = boq_data.get("current_specs", {})
    items = boq_data.get("line_items", [])
    fin = boq_data.get("financial_summary", {})

    resolved_city = city or meta.get("city") or (floorplan_context or {}).get("city") or "Bangalore"
    room_name = meta.get("room_name", "Client Floorplan")
    floor_sqft = float(dims.get("floor_sqft", 0.0))
    wall_sqft = float(dims.get("wall_sqft", 0.0))
    carpet_sqft = float(dims.get("carpet_area_sqft", floor_sqft / 1.10 if floor_sqft else 0.0))

    rate_lookup: Dict[str, float] = {}
    for it in items:
        cat_l = it.get("category", "").lower()
        if "floor" in cat_l:
            rate_lookup["flooring"] = float(it.get("unit_rate", 75.0))
        elif "wall" in cat_l or "paint" in cat_l:
            rate_lookup["painting"] = float(it.get("unit_rate", 38.0))
        elif "furniture" in cat_l or "joinery" in cat_l:
            rate_lookup["furniture"] = float(it.get("subtotal", 0.0))

    material_notes: List[Dict[str, Any]] = [
        explain_material_choice(
            category="flooring",
            material_name=specs.get("flooring", "Kajaria GVT Vitrified Tile"),
            rate_per_sqft=rate_lookup.get("flooring"),
            city=resolved_city,
            room_type=room_name,
            area_sqft=floor_sqft
        ),
        explain_material_choice(
            category="painting",
            material_name=specs.get("painting", "Asian Paints Royale Luxury Emulsion"),
            rate_per_sqft=rate_lookup.get("painting"),
            city=resolved_city,
            room_type=room_name,
            area_sqft=wall_sqft
        ),
        explain_material_choice(
            category="furniture",
            material_name=specs.get("furniture", "CenturyPly Modular BWP/MR Ply & HPL Laminate"),
            rate_per_sqft=None,
            city=resolved_city,
            room_type=room_name,
            area_sqft=carpet_sqft
        )
    ]

    for it in items:
        cat_l = it.get("category", "").lower()
        if "civil" in cat_l or "structural" in cat_l:
            material_notes.append({
                "category": "Civil & Structural Shell",
                "material_name": "Fe-550D TMT Steel + M25 Grade Concrete + AAC Blocks",
                "tier": "IS-Compliant",
                "rate_per_sqft": float(it.get("unit_rate", 0.0)),
                "why_chosen": (
                    f"Why Fe-550D TMT & AAC Blocks were chosen: AAC blocks cut dead load by ~45% over clay bricks "
                    f"and provide 3x thermal insulation for {resolved_city}'s climate, while Fe-550D TMT ensures ductile seismic safety (IS 13920)."
                ),
                "engineering_metrics": {
                    "Thermal Conductivity": "0.16 W/mK (AAC vs 0.81 W/mK red brick)",
                    "Concrete Grade": "M25 Ready-Mix (IS 456)",
                    "Steel Grade": "Fe-550D Ductile TMT (IS 1786)"
                },
                "climate_fit": f"High thermal lag reduces cooling load across {resolved_city}'s daytime temperature swings.",
                "cost_comparison": "Reduces structural steel tonnage by ~8-10% due to lighter AAC wall dead load.",
                "supplier_spec": it.get("description", "IS 456 M25 RCC & 200mm AAC masonry"),
                "is_code": "IS 456 / IS 1786 / IS 2185",
                "durability_score": 95,
                "utility_score": 92
            })
        elif "mep" in cat_l or "electrical" in cat_l or "plumbing" in cat_l:
            material_notes.append({
                "category": "Electrical & Plumbing (MEP)",
                "material_name": "Finolex FRLS Wiring + Astral CPVC/UPVC + Jaquar Fittings",
                "tier": "Standard-Plus",
                "rate_per_sqft": float(it.get("unit_rate", 0.0)),
                "why_chosen": (
                    "Why FRLS Copper & Astral CPVC were chosen: Flame-Retardant Low-Smoke (FRLS) insulation prevents toxic smoke "
                    "during short-circuits, while lead-free CPVC handles hot-water lines up to 93°C without scale buildup."
                ),
                "engineering_metrics": {
                    "Wiring Safety": "99.97% Electrolytic Copper FRLS (IS 694)",
                    "Plumbing Spec": "SDR-11 Lead-Free CPVC (IS 15778)",
                    "Protection": "RCCB 30mA + Surge Protection"
                },
                "climate_fit": f"Corrosion-proof CPVC resists hard-water scaling common in {resolved_city} borewell/municipal supplies.",
                "cost_comparison": "Zero corrosion leakage over 30+ years vs galvanized iron pipes.",
                "supplier_spec": it.get("description", "Concealed FRLS conduits, CPVC hot/cold lines, CP brass fixtures"),
                "is_code": "IS 694 / IS 15778",
                "durability_score": 92,
                "utility_score": 90
            })

    avg_durability = round(sum(n["durability_score"] for n in material_notes) / len(material_notes), 1)
    gst_amount = fin.get("gst_amount", 0.0)
    grand_total = fin.get("grand_total", 0.0)

    executive_summary = (
        f"For this {carpet_sqft:,.0f} sq.ft carpet area layout in {resolved_city}, the material schedule balances "
        f"climate resilience, low-VOC indoor air safety, and IS-code durability (Composite Durability Score: {avg_durability}/100). "
        f"Total estimate is ₹{grand_total:,.2f} (inclusive of 18% statutory GST of ₹{gst_amount:,.2f})."
    )

    return {
        "city": resolved_city,
        "carpet_area_sqft": round(carpet_sqft, 2),
        "composite_durability_score": avg_durability,
        "executive_summary": executive_summary,
        "material_notes": material_notes
    }


# ============================================================================
# 4. BUDGET TRADE-OFF ADVISOR (`suggest_budget_cuts`)
# ============================================================================

def _infer_boq_rates(boq: Dict[str, Any]) -> Tuple[float, float, float]:
    """Extracts current (floor_rate, paint_rate, furniture_subtotal) from a BoQ."""
    floor_rate = 0.0
    paint_rate = 0.0
    furn_cost = 0.0
    for item in boq.get("line_items", []):
        cat = item.get("category", "").lower()
        if "floor" in cat:
            floor_rate = float(item.get("unit_rate", 0.0))
        elif "wall" in cat or "paint" in cat:
            paint_rate = float(item.get("unit_rate", 0.0))
        elif "furniture" in cat or "joinery" in cat:
            furn_cost = float(item.get("subtotal", 0.0))
    return floor_rate, paint_rate, furn_cost


def _apply_swaps_to_boq(
    current_boq: Dict[str, Any],
    swaps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Produces a deep-copied, recalculated BoQ reflecting the selected trade-off swaps."""
    new_boq = copy.deepcopy(current_boq)
    fin = new_boq["financial_summary"]

    mat_sub = float(fin.get("materials_subtotal", 0.0))
    labor_pct = float(fin.get("labor_buffer_pct", 0.12))
    cont_pct = float(fin.get("contingency_pct", 0.05))
    gst_rate = float(fin.get("gst_rate", 0.18))

    if "labor_buffer_pct" not in fin and mat_sub > 0:
        labor_pct = float(fin.get("labor_buffer", 0.0)) / mat_sub
    sub_with_lab = mat_sub + float(fin.get("labor_buffer", 0.0))
    if "contingency_pct" not in fin and sub_with_lab > 0:
        cont_pct = float(fin.get("contingency_allowance", 0.0)) / sub_with_lab

    for swap in swaps:
        cat_key = swap["category_key"]
        for item in new_boq["line_items"]:
            item_cat = item["category"].lower()
            if cat_key == "flooring" and "floor" in item_cat:
                item["unit_rate"] = round(swap["new_rate"], 2)
                item["subtotal"] = round(float(item["quantity"]) * swap["new_rate"], 2)
                item["description"] = f"{swap['to_material']} (Inc. 10% cutting wastage & grout laying)"
                new_boq.setdefault("current_specs", {})["flooring"] = swap["to_material"]
            elif cat_key == "painting" and ("wall" in item_cat or "paint" in item_cat):
                item["unit_rate"] = round(swap["new_rate"], 2)
                item["subtotal"] = round(float(item["quantity"]) * swap["new_rate"], 2)
                item["description"] = f"{swap['to_material']} (Surface prep, primer + 2 topcoats)"
                new_boq.setdefault("current_specs", {})["painting"] = swap["to_material"]
            elif cat_key == "furniture" and ("furniture" in item_cat or "joinery" in item_cat):
                item["unit_rate"] = round(swap["new_subtotal"], 2)
                item["subtotal"] = round(swap["new_subtotal"], 2)
                item["description"] = f"{swap['to_material']} (Factory assembled & site anchored)"
                new_boq.setdefault("current_specs", {})["furniture"] = swap["to_material"]

    direct_items = [
        it for it in new_boq["line_items"]
        if "labor" not in it["category"].lower() and "contingency" not in it["category"].lower()
    ]
    new_materials_sub = round(sum(float(it["subtotal"]) for it in direct_items), 2)
    new_labor = round(new_materials_sub * labor_pct, 2)
    new_sub_with_labor = round(new_materials_sub + new_labor, 2)
    new_contingency = round(new_sub_with_labor * cont_pct, 2)
    new_pre_gst = round(new_sub_with_labor + new_contingency, 2)
    new_gst = round(new_pre_gst * gst_rate, 2)
    new_grand = round(new_pre_gst + new_gst, 2)

    for it in new_boq["line_items"]:
        cat_l = it["category"].lower()
        if "labor" in cat_l:
            it["unit_rate"] = new_labor
            it["subtotal"] = new_labor
        elif "contingency" in cat_l:
            it["unit_rate"] = new_contingency
            it["subtotal"] = new_contingency

    budget_cap = float(fin.get("budget_cap", new_grand))
    is_within = new_grand <= budget_cap
    variance_signed = round(budget_cap - new_grand, 2)

    fin.update({
        "materials_subtotal": new_materials_sub,
        "labor_buffer": new_labor,
        "contingency_allowance": new_contingency,
        "pre_gst_total": new_pre_gst,
        "gst_rate": gst_rate,
        "gst_percentage": round(gst_rate * 100, 1),
        "gst_amount": new_gst,
        "grand_total": new_grand,
        "grand_total_incl_gst": new_grand,
        "status": "Within Budget" if is_within else "Over Budget",
        "is_within_budget": is_within,
        "delta": round(abs(variance_signed), 2),
        "variance_signed": variance_signed,
        "variance_percentage": round((variance_signed / budget_cap) * 100, 2) if budget_cap > 0 else 0.0
    })

    return new_boq


def suggest_budget_cuts(
    current_boq: Dict[str, Any],
    target_reduction_inr: float,
    city: Optional[str] = None
) -> Dict[str, Any]:
    """
    Smart Budget Trade-Off Advisor.
    Given the current BoQ and a target cost reduction in INR (e.g., ₹25,000),
    evaluates realistic Indian material substitutions that preserve durability
    and explains the exact savings and engineering trade-off.
    """
    if target_reduction_inr <= 0:
        return {
            "target_reduction_inr": float(target_reduction_inr),
            "achievable": True,
            "total_savings_inr": 0.0,
            "direct_material_savings_inr": 0.0,
            "original_total_inr": current_boq["financial_summary"]["grand_total"],
            "new_estimated_total_inr": current_boq["financial_summary"]["grand_total"],
            "recommendations": [],
            "client_explanation": "No cost reduction requested (target reduction is ₹0).",
            "updated_boq": current_boq
        }

    dims = current_boq.get("dimensions", {})
    specs = current_boq.get("current_specs", {})
    fin = current_boq.get("financial_summary", {})
    resolved_city = city or current_boq.get("project_metadata", {}).get("city", "Bangalore")

    floor_sqft = float(dims.get("floor_sqft", 0.0))
    wall_sqft = float(dims.get("wall_sqft", 0.0))
    orig_total = float(fin.get("grand_total", 0.0))

    cur_floor_rate, cur_paint_rate, cur_furn_cost = _infer_boq_rates(current_boq)
    cur_floor_entry = _find_material_entry("flooring", specs.get("flooring"), cur_floor_rate)
    cur_paint_entry = _find_material_entry("painting", specs.get("painting"), cur_paint_rate)
    cur_furn_entry = _find_material_entry("furniture", specs.get("furniture"))

    labor_pct = float(fin.get("labor_buffer_pct", 0.12))
    cont_pct = float(fin.get("contingency_pct", 0.05))
    gst_rate = float(fin.get("gst_rate", 0.18))
    cascade_mult = (1.0 + labor_pct) * (1.0 + cont_pct) * (1.0 + gst_rate)

    candidates_by_cat: Dict[str, List[Dict[str, Any]]] = {"flooring": [], "painting": [], "furniture": []}

    for opt in MATERIAL_INTELLIGENCE_DB["flooring"]:
        if opt["rate_per_sqft"] < cur_floor_rate and floor_sqft > 0:
            mat_save = round((cur_floor_rate - opt["rate_per_sqft"]) * floor_sqft, 2)
            total_save = round(mat_save * cascade_mult, 2)
            dur_delta = opt["durability_score"] - (cur_floor_entry["durability_score"] if cur_floor_entry else 85)
            no_compromise = opt["durability_score"] >= 85
            durability_phrase = (
                "without compromising durability" if no_compromise
                else "while retaining reliable everyday wear resistance"
            )
            from_name = cur_floor_entry["name"] if cur_floor_entry else specs.get("flooring", "Current Flooring")
            summary = (
                f"Switching flooring from {from_name} (₹{cur_floor_rate:,.0f}/sq.ft) to "
                f"{opt['name']} (₹{opt['rate_per_sqft']:,.0f}/sq.ft) saves ₹{mat_save:,.0f} in direct material cost "
                f"(₹{total_save:,.0f} total BoQ savings incl. labor & 18% GST) {durability_phrase}."
            )
            candidates_by_cat["flooring"].append({
                "category_key": "flooring",
                "category": "Flooring & Substrate",
                "from_material": from_name,
                "to_material": opt["name"],
                "old_rate": cur_floor_rate,
                "new_rate": opt["rate_per_sqft"],
                "material_savings_inr": mat_save,
                "total_boq_savings_inr": total_save,
                "durability_score": opt["durability_score"],
                "durability_delta": dur_delta,
                "durability_impact": (
                    f"Durability {opt['durability_score']}/100 ({opt['water_absorption_pct']:.2f}% water absorption, {opt['scratch_resistance'].split('/')[0].strip()})"
                ),
                "engineering_explanation": explain_material_choice(
                    "flooring", opt["name"], opt["rate_per_sqft"], resolved_city, area_sqft=floor_sqft, alternative_name=from_name
                )["why_chosen"],
                "summary_sentence": summary
            })

    for opt in MATERIAL_INTELLIGENCE_DB["painting"]:
        if opt["rate_per_sqft"] < cur_paint_rate and wall_sqft > 0:
            mat_save = round((cur_paint_rate - opt["rate_per_sqft"]) * wall_sqft, 2)
            total_save = round(mat_save * cascade_mult, 2)
            dur_delta = opt["durability_score"] - (cur_paint_entry["durability_score"] if cur_paint_entry else 85)
            no_compromise = opt["durability_score"] >= 80
            durability_phrase = (
                "without compromising wall washability or low-VOC safety" if no_compromise
                else "while maintaining a clean matte finish"
            )
            from_name = cur_paint_entry["name"] if cur_paint_entry else specs.get("painting", "Current Painting")
            summary = (
                f"Switching wall finish from {from_name} (₹{cur_paint_rate:,.0f}/sq.ft) to "
                f"{opt['name']} (₹{opt['rate_per_sqft']:,.0f}/sq.ft) saves ₹{mat_save:,.0f} in direct material cost "
                f"(₹{total_save:,.0f} total BoQ savings incl. labor & 18% GST) {durability_phrase}."
            )
            candidates_by_cat["painting"].append({
                "category_key": "painting",
                "category": "Wall Surface Finishing",
                "from_material": from_name,
                "to_material": opt["name"],
                "old_rate": cur_paint_rate,
                "new_rate": opt["rate_per_sqft"],
                "material_savings_inr": mat_save,
                "total_boq_savings_inr": total_save,
                "durability_score": opt["durability_score"],
                "durability_delta": dur_delta,
                "durability_impact": f"Durability {opt['durability_score']}/100 ({opt['voc_level']})",
                "engineering_explanation": explain_material_choice(
                    "painting", opt["name"], opt["rate_per_sqft"], resolved_city, area_sqft=wall_sqft, alternative_name=from_name
                )["why_chosen"],
                "summary_sentence": summary
            })

    cur_mult = cur_furn_entry["multiplier"] if cur_furn_entry else 1.0
    for opt in MATERIAL_INTELLIGENCE_DB["furniture"]:
        if opt["multiplier"] < cur_mult and cur_furn_cost > 0:
            new_sub = round(cur_furn_cost * (opt["multiplier"] / cur_mult), 2)
            mat_save = round(cur_furn_cost - new_sub, 2)
            total_save = round(mat_save * cascade_mult, 2)
            dur_delta = opt["durability_score"] - (cur_furn_entry["durability_score"] if cur_furn_entry else 90)
            from_name = cur_furn_entry["name"] if cur_furn_entry else specs.get("furniture", "Current Joinery")
            durability_phrase = (
                "without compromising structural moisture resistance" if opt["durability_score"] >= 85
                else "with factory-calibrated moisture-resistant boards"
            )
            summary = (
                f"Switching joinery from {from_name} to {opt['name']} saves ₹{mat_save:,.0f} in package cost "
                f"(₹{total_save:,.0f} total BoQ savings incl. labor & 18% GST) {durability_phrase}."
            )
            candidates_by_cat["furniture"].append({
                "category_key": "furniture",
                "category": "Furniture & Modular Fixtures",
                "from_material": from_name,
                "to_material": opt["name"],
                "old_rate": cur_furn_cost,
                "new_rate": new_sub,
                "new_subtotal": new_sub,
                "material_savings_inr": mat_save,
                "total_boq_savings_inr": total_save,
                "durability_score": opt["durability_score"],
                "durability_delta": dur_delta,
                "durability_impact": f"Durability {opt['durability_score']}/100 ({opt['core_spec']})",
                "engineering_explanation": explain_material_choice(
                    "furniture", opt["name"], None, resolved_city, alternative_name=from_name
                )["why_chosen"],
                "summary_sentence": summary
            })

    f_choices = [None] + candidates_by_cat["flooring"]
    p_choices = [None] + candidates_by_cat["painting"]
    fn_choices = [None] + candidates_by_cat["furniture"]

    best_combo: Optional[List[Dict[str, Any]]] = None
    best_score: Tuple[float, int, float] = (-1e9, -99, -1e9)
    max_possible_combo: List[Dict[str, Any]] = []
    max_possible_savings = 0.0

    for fc in f_choices:
        for pc in p_choices:
            for fnc in fn_choices:
                combo = [c for c in (fc, pc, fnc) if c is not None]
                if not combo:
                    continue
                total_save = sum(c["total_boq_savings_inr"] for c in combo)
                if total_save > max_possible_savings:
                    max_possible_savings = total_save
                    max_possible_combo = combo

                if total_save >= target_reduction_inr:
                    avg_dur = sum(c["durability_score"] for c in combo) / len(combo)
                    overshoot = total_save - target_reduction_inr
                    score = (avg_dur, -len(combo), -overshoot / 10000.0)
                    if score > best_score:
                        best_score = score
                        best_combo = combo

    if best_combo is not None:
        chosen_swaps = best_combo
        achievable = True
    else:
        chosen_swaps = max_possible_combo
        achievable = False

    updated_boq = _apply_swaps_to_boq(current_boq, chosen_swaps) if chosen_swaps else copy.deepcopy(current_boq)
    new_total = float(updated_boq["financial_summary"]["grand_total"])
    actual_total_savings = round(orig_total - new_total, 2)
    direct_mat_savings = round(sum(s["material_savings_inr"] for s in chosen_swaps), 2)

    if not chosen_swaps:
        client_explanation = (
            "Your current specification is already at the most cost-effective Economy tier; "
            "no further material downgrades are available without reducing scope area."
        )
    elif achievable:
        sentences = " ".join(s["summary_sentence"] for s in chosen_swaps)
        client_explanation = (
            f"To cut at least ₹{target_reduction_inr:,.0f}: {sentences} "
            f"Revised BoQ Total drops from ₹{orig_total:,.2f} to ₹{new_total:,.2f} (Total reduction: ₹{actual_total_savings:,.2f})."
        )
    else:
        sentences = " ".join(s["summary_sentence"] for s in chosen_swaps)
        shortfall = round(target_reduction_inr - actual_total_savings, 2)
        client_explanation = (
            f"Maximum achievable material savings is ₹{actual_total_savings:,.2f} (short by ₹{shortfall:,.2f} of your ₹{target_reduction_inr:,.0f} target): "
            f"{sentences} Consider phasing joinery or reducing built-up scope to bridge the remaining ₹{shortfall:,.2f}."
        )

    return {
        "target_reduction_inr": round(float(target_reduction_inr), 2),
        "achievable": achievable,
        "original_total_inr": orig_total,
        "new_estimated_total_inr": new_total,
        "direct_material_savings_inr": direct_mat_savings,
        "total_savings_inr": actual_total_savings,
        "recommendations": chosen_swaps,
        "client_explanation": client_explanation,
        "updated_boq": updated_boq
    }


def answer_budget_question(
    question_text: str,
    current_boq: Dict[str, Any],
    city: Optional[str] = None
) -> Dict[str, Any]:
    """
    Natural-language interface for the Budget Trade-Off & Material Intelligence Advisor.
    """
    q = question_text.strip()
    q_lower = q.lower()

    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|lakhs|lacs)\b", q_lower)
    amount_match = re.search(r"(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(k)?", q_lower)

    if any(kw in q_lower for kw in ("cut", "save", "reduce", "lower", "cheaper", "trim", "discount")):
        target = 25000.0
        if lakh_match:
            target = float(lakh_match.group(1)) * 100000.0
        elif amount_match:
            raw_num = float(amount_match.group(1).replace(",", ""))
            if amount_match.group(2) == "k":
                raw_num *= 1000.0
            if raw_num > 0:
                target = raw_num
        result = suggest_budget_cuts(current_boq, target, city=city)
        return {
            "intent": "budget_cut",
            "query": q,
            "answer": result["client_explanation"],
            "details": result
        }

    notes = generate_boq_reasoning_notes(current_boq, city=city)
    reasons = "\n".join(f"- {n['why_chosen']}" for n in notes["material_notes"])
    return {
        "intent": "material_reasoning",
        "query": q,
        "answer": f"{notes['executive_summary']}\n\n{reasons}",
        "details": notes
    }


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("AI-GLAZE Material Intelligence & Architectural Reasoning Engine loaded successfully.")
    sample_floor = explain_material_choice("flooring", "Kajaria GVT Vitrified Tile", 75.0, city="Bangalore", area_sqft=792.0)
    print("\n[Flooring Reasoning]", sample_floor["why_chosen"])
    sample_paint = explain_material_choice("painting", "Asian Paints Royale Luxury Emulsion", 38.0, city="Bangalore")
    print("[Painting Reasoning]", sample_paint["why_chosen"])
