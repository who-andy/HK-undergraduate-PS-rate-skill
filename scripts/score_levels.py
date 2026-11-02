#!/usr/bin/env python3
"""Deterministic lookup for experimental PS score labels (not admissions predictions)."""
from pathlib import Path

from validate_profiles import ValidationError, load_json


def validate_score_bands(root):
    data = load_json(Path(root) / "rubrics" / "score_bands.json")
    bands = data.get("bands")
    if not isinstance(data.get("version"), str) or not isinstance(bands, list) or not bands:
        raise ValidationError("Missing score-band version or bands")
    expected_min = 0
    for band in bands:
        low, high = band.get("min"), band.get("max")
        if type(low) is not int or type(high) is not int or low != expected_min or high < low or high > 100:
            raise ValidationError("Score bands must be contiguous, integer, non-overlapping and cover 0..100")
        for key in ("label", "label_zh", "typical_evidence", "priority"):
            if not isinstance(band.get(key), str) or not band[key].strip():
                raise ValidationError("Missing band metadata: " + key)
        expected_min = high + 1
    if expected_min != 101:
        raise ValidationError("Score bands must end at 100")
    return data


def score_level(root, total):
    """Return None when the full 100-point total is unknown; never rescale /70."""
    bands = validate_score_bands(root)["bands"]
    if total is None:
        return None
    if type(total) is not int or total < 0 or total > 100:
        raise ValidationError("Full score must be an integer from 0 to 100")
    band = next(b for b in bands if b["min"] <= total <= b["max"])
    return {"min": band["min"], "max": band["max"],
            "label": band["label"], "label_zh": band["label_zh"]}
