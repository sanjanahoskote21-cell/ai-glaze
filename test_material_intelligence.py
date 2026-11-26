"""
Verification test suite for AI-GLAZE Material Intelligence & Architectural Reasoning Engine.
Tests Pillars 4 & 6 across cost_engine.py, reasoning_engine.py, and contractor_boq_tab.py.
"""

import os
import tempfile
import unittest

import cost_engine
import reasoning_engine


class TestMaterialIntelligenceAndCostEngine(unittest.TestCase):
    def test_floorplan_area_30x40_carpet_792_and_18_gst(self):
        areas = cost_engine.estimate_floorplan_areas(plot_width_ft=30.0, plot_length_ft=40.0)
        self.assertEqual(areas["plot_area_sqft"], 1200.0)
        self.assertEqual(areas["carpet_area_sqft"], 792.0)
        self.assertAlmostEqual(areas["billable_floor_sqft"], 871.2, places=1)

        boq = cost_engine.generate_floorplan_boq(
            carpet_area_sqft=792.0,
            plot_width_ft=30.0,
            plot_length_ft=40.0,
            scope="renovation",
            flooring_tier="Standard",
            painting_tier="Premium",
            furniture_tier="Standard",
            city="Bangalore",
        )
        fin = boq["financial_summary"]
        self.assertEqual(fin["gst_rate"], 0.18)
        self.assertAlmostEqual(fin["gst_amount"], round(fin["pre_gst_total"] * 0.18, 2), places=2)
        self.assertAlmostEqual(fin["grand_total"], round(fin["pre_gst_total"] + fin["gst_amount"], 2), places=2)
        self.assertIn("reasoning_notes", boq)
        self.assertGreaterEqual(len(boq["reasoning_notes"]["material_notes"]), 3)

    def test_full_construction_scope_includes_civil_and_mep(self):
        boq = cost_engine.generate_floorplan_boq(
            carpet_area_sqft=792.0,
            scope="full_construction",
            city="Bangalore",
        )
        categories = [it["category"] for it in boq["line_items"]]
        self.assertIn("Civil & Structural Shell", categories)
        self.assertIn("Electrical & Plumbing (MEP)", categories)
        self.assertEqual(boq["financial_summary"]["gst_percentage"], 18.0)

    def test_material_architectural_intelligence_explanations(self):
        tile_exp = reasoning_engine.explain_material_choice(
            category="flooring",
            material_name="Kajaria GVT Vitrified Tile",
            rate_per_sqft=75.0,
            city="Bangalore",
            area_sqft=792.0,
        )
        self.assertIn("0.05%", tile_exp["why_chosen"])
        self.assertIn("Bangalore", tile_exp["why_chosen"])
        self.assertIn("75", tile_exp["why_chosen"])
        self.assertIn("380", tile_exp["why_chosen"])

        paint_exp = reasoning_engine.explain_material_choice(
            category="painting",
            material_name="Asian Paints Royale Luxury Emulsion",
            rate_per_sqft=38.0,
            city="Bangalore",
        )
        self.assertIn("Low VOC", paint_exp["why_chosen"])
        self.assertIn("Teflon", paint_exp["why_chosen"])

    def test_suggest_budget_cuts_25000_on_marble_boq(self):
        # 140 sq.ft billable flooring: Italian Marble (380) -> Kajaria Vitrified (75) saves ₹42,700 direct
        boq = cost_engine.generate_full_boq(
            floor_sqft=140.0,
            floor_rate=380.0,
            wall_sqft=450.0,
            paint_rate=38.0,
            furniture_price=85000.0,
            budget_cap=160000.0,
            selected_specs={
                "flooring": "Italian Statuario Marble",
                "painting": "Asian Paints Royale Luxury Emulsion",
                "furniture": "Bespoke Burma Teak & Italian Veneer Joinery",
            },
        )
        advice = reasoning_engine.suggest_budget_cuts(boq, target_reduction_inr=25000.0, city="Bangalore")
        self.assertTrue(advice["achievable"])
        self.assertGreaterEqual(advice["total_savings_inr"], 25000.0)
        self.assertLess(advice["new_estimated_total_inr"], advice["original_total_inr"])
        self.assertIn("Kajaria", advice["client_explanation"])
        self.assertIn("42,700", advice["client_explanation"])

        # Natural language query routing
        qa = reasoning_engine.answer_budget_question("How can I cut ₹25,000?", boq, city="Bangalore")
        self.assertEqual(qa["intent"], "budget_cut")
        self.assertTrue(qa["details"]["achievable"])

    def test_export_boq_report_includes_gst_and_reasoning(self):
        boq = cost_engine.generate_floorplan_boq(carpet_area_sqft=792.0, flooring_tier="Luxury", city="Bangalore")
        cuts = cost_engine.suggest_budget_cuts(boq, 25000.0, city="Bangalore")
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_boq.html")
            saved = cost_engine.export_boq_report(cuts["updated_boq"], output_file=out_path, budget_cuts=cuts)
            self.assertTrue(os.path.exists(saved))
            with open(saved, "r", encoding="utf-8") as f:
                html = f.read()
            self.assertIn("Material Intelligence & Architectural Reasoning Notes", html)
            self.assertIn("Statutory Indian GST (18%)", html)
            self.assertIn("Budget Trade-Off Advisor", html)
            self.assertIn("792.0", html)

    def test_optimize_boq_for_budget_preserves_gst(self):
        boq = cost_engine.generate_floorplan_boq(
            carpet_area_sqft=792.0,
            flooring_tier="Luxury",
            painting_tier="Luxury",
            furniture_tier="Luxury",
            budget_cap=650000.0,
        )
        opt = cost_engine.optimize_boq_for_budget(boq, max_budget=650000.0)
        self.assertTrue(opt["is_achievable"])
        self.assertLessEqual(opt["optimized_total"], 650000.0)
        self.assertEqual(opt["optimized_boq"]["financial_summary"]["gst_rate"], 0.18)


if __name__ == "__main__":
    unittest.main(verbosity=2)
