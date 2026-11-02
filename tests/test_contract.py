"""Unit tests for dynamic research and deterministic score diagnostics."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from aggregate_scores import summarize
from score_levels import score_level, validate_score_bands
from benchmark import diagnose
from validate_profiles import ValidationError, load_json, validate, validate_research_profile, validate_hk_five


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_json(ROOT / "examples" / "evaluations.synthetic.json")
        self.pairs = load_json(ROOT / "examples" / "benchmark.synthetic.json")


    def test_score_level_boundaries(self):
        cases = {0: "Needs fundamental revision", 59: "Needs fundamental revision",
                 60: "Weak", 69: "Weak", 70: "Developing", 79: "Developing",
                 80: "Good", 84: "Good", 85: "Very strong", 89: "Very strong",
                 90: "Excellent", 94: "Excellent", 95: "Exceptional within this rubric",
                 100: "Exceptional within this rubric"}
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(score_level(ROOT, value)["label"], expected)
        self.assertIsNone(score_level(ROOT, None))

    def test_score_level_input_validation(self):
        for value in (-1, 101, True, 90.5, "90"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                score_level(ROOT, value)

    def test_score_bands_nonoverlap(self):
        self.assertEqual(len(validate_score_bands(ROOT)["bands"]), 7)
        import json
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as work:
            dest = Path(work) / "rubrics"
            dest.mkdir()
            bands = copy.deepcopy(validate_score_bands(ROOT))
            bands["bands"][1]["min"] = 59
            (dest / "score_bands.json").write_text(json.dumps(bands), encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_score_bands(work)

    def test_score_level_and_readiness_are_independent(self):
        p = copy.deepcopy(self.payload)
        e = p["evaluations"][0]
        for rubric in ("universal", "major_fit"):
            definitions = load_json(ROOT / "rubrics" / (rubric + ".json"))
            for c in definitions["criteria"]:
                e["scores"][c["id"]]["score"] = c["max_points"]
        e["submission_checks"] = {"status": "blocking_issues", "items": ["Verified mandatory length violation"]}
        got = summarize(ROOT, p)["evaluations"][0]
        self.assertEqual(got["total"], 100)
        self.assertEqual(got["score_level"]["label"], "Exceptional within this rubric")
        self.assertEqual(got["submission_status"], "blocking_issues")
        self.assertTrue(got["score_level_provisional"]) # synthetic research

    def test_unchecked_submission_is_not_clear(self):
        result = summarize(ROOT, self.payload)
        self.assertTrue(all(x["submission_status"] == "not_checked" for x in result["evaluations"]))

    def test_blocking_status_requires_explanation(self):
        p = copy.deepcopy(self.payload)
        p["evaluations"][0]["submission_checks"] = {"status": "blocking_issues", "items": []}
        with self.assertRaises(ValidationError):
            summarize(ROOT, p)

    def test_dynamic_no_bundled_profile_required(self):
        got = validate(ROOT)
        self.assertFalse(got["bundled_profiles_required"])
        self.assertEqual(got["total_points"], 100)

    def test_hk_five_completeness(self):
        self.assertEqual(validate_hk_five(ROOT)["university_count"], 5)

    def test_hk_five_units_and_unknowns(self):
        data = load_json(ROOT / "requirements" / "hk-five-2027.json")
        d = {r["id"]: r for r in data["rules"]}
        self.assertEqual(d["hku"]["limit"]["unit"], "words")
        self.assertEqual(d["cuhk"]["limit"]["unit"], "characters")
        self.assertIsNone(d["hkust"]["limit"])
        self.assertIsNone(d["cityuhk"]["limit"])
        self.assertIsNone(d["polyu"]["limit"])
        self.assertEqual(d["cityuhk"]["shared_choices"], "per_programme_statement_in_faq")

    def test_score_aggregation(self):
        got = summarize(ROOT, self.payload)
        self.assertEqual(len(got["evaluations"]), 2)
        self.assertEqual(got["groups"][0]["judge_count"], 2)
        for x in got["evaluations"]:
            self.assertEqual(x["universal"] + x["major_fit"], x["total"])
            self.assertEqual(x["research_status"], "synthetic")

    def test_out_of_range_rejected(self):
        data = copy.deepcopy(self.payload)
        data["evaluations"][0]["scores"]["language"]["score"] = 6
        with self.assertRaises(ValidationError):
            summarize(ROOT, data)

    def test_missing_score_rejected(self):
        data = copy.deepcopy(self.payload)
        del data["evaluations"][0]["scores"]["academic_direction"]
        with self.assertRaises(ValidationError):
            summarize(ROOT, data)

    def test_unknown_major_rejected(self):
        data = copy.deepcopy(self.payload)
        data["evaluations"][0]["target_major"] = "nonexistent"
        with self.assertRaises(ValidationError):
            summarize(ROOT, data)

    def test_order_flip_and_disagreement(self):
        got = diagnose(self.pairs)
        self.assertEqual(got["paired_order_trials"], 2)
        self.assertEqual(got["order_preference_flips"], 1)
        self.assertEqual(got["flip_rate"], 0.5)
        self.assertEqual(got["inter_judge_pairs"], 2)

    def test_missing_pairs_not_treated_as_stable(self):
        got = diagnose({"observations": self.pairs["observations"][:1]})
        self.assertIsNone(got["flip_rate"])

    def test_duplicate_observation_rejected(self):
        p = copy.deepcopy(self.pairs)
        p["observations"].append(copy.deepcopy(p["observations"][0]))
        with self.assertRaises(ValueError):
            diagnose(p)

    def test_boolean_score_rejected(self):
        p = copy.deepcopy(self.payload)
        p["evaluations"][0]["scores"]["language"]["score"] = True
        with self.assertRaises(ValidationError):
            summarize(ROOT, p)

    def test_verified_must_have_evidence(self):
        p = copy.deepcopy(self.payload)
        entry = next(iter(p["profiles"].values()))
        entry["research_status"] = "verified"
        entry["synthetic"] = False
        with self.assertRaises(ValidationError):
            summarize(ROOT, p)

    def test_unavailable_research_requires_universal_only(self):
        p = copy.deepcopy(self.payload)
        entry = next(iter(p["profiles"].values()))
        entry["research_status"] = "unavailable"
        for e in p["evaluations"]:
            for key in ("disciplinary_understanding", "relevant_evidence", "academic_direction"):
                del e["scores"][key]
        got = summarize(ROOT, p)
        for x in got["evaluations"]:
            self.assertIsNone(x["major_fit"])
            self.assertIsNone(x["total"])
            self.assertFalse(x["major_profile_checked"])

    def test_unavailable_research_rejects_fabricated_fit(self):
        p = copy.deepcopy(self.payload)
        next(iter(p["profiles"].values()))["research_status"] = "unavailable"
        with self.assertRaises(ValidationError):
            summarize(ROOT, p)

    def test_malformed_research_date_rejected(self):
        p = copy.deepcopy(self.payload)
        entry = next(iter(p["profiles"].values()))
        entry["researched_on"] = "2026-99-99"
        with self.assertRaises(ValidationError):
            summarize(ROOT, p)

    def test_profile_registry_mismatch_rejected(self):
        p = copy.deepcopy(self.payload)
        entry = next(iter(p["profiles"].values()))
        entry["id"] = "different"
        with self.assertRaises(ValidationError):
            summarize(ROOT, p)


if __name__ == "__main__":
    unittest.main()
