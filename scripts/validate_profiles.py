#!/usr/bin/env python3
"""Validate stable rubrics and on-demand research snapshot contracts (stdlib only)."""
import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


class ValidationError(ValueError):
    pass


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def rubric_from_file(path):
    rubric = load_json(path)
    if not isinstance(rubric, dict) or not isinstance(rubric.get("criteria"), list):
        raise ValidationError(f"Invalid criteria: {path}")
    ids = [c.get("id") for c in rubric["criteria"]]
    if not ids or len(ids) != len(set(ids)) or any(not isinstance(x, str) or not x for x in ids):
        raise ValidationError(f"Criteria IDs missing or duplicated: {path}")
    points = [c.get("max_points") for c in rubric["criteria"]]
    if any(type(p) is not int or p <= 0 for p in points):
        raise ValidationError(f"max_points must be positive integers: {path}")
    if sum(points) != rubric.get("total_points"):
        raise ValidationError(f"Rubric total does not equal criteria points: {path}")
    if not isinstance(rubric.get("version"), str):
        raise ValidationError(f"Rubric version missing: {path}")
    return rubric


def validate_research_profile(profile_id, item):
    """Validate the evidence envelope, never claim that cited claims are true."""
    if not isinstance(item, dict):
        raise ValidationError(f"Invalid profile object: {profile_id}")
    for key in ("id", "version", "researched_on", "target_intake", "route", "university", "programme", "interpretation_note"):
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise ValidationError(f"Invalid {key}: {profile_id}")
    if item["id"] != profile_id:
        raise ValidationError(f"Profile registry key/id mismatch: {profile_id}")
    try:
        date.fromisoformat(item["researched_on"])
    except ValueError as exc:
        raise ValidationError(f"Invalid researched_on: {profile_id}") from exc
    status = item.get("research_status")
    if status not in ("verified", "partial", "unavailable", "synthetic"):
        raise ValidationError(f"Invalid research_status: {profile_id}")
    if status == "synthetic" and item.get("synthetic") is not True:
        raise ValidationError(f"Synthetic fixture must be flagged explicitly: {profile_id}")
    for key in ("official_facts", "major_signals", "sources", "unknowns"):
        if not isinstance(item.get(key), list):
            raise ValidationError(f"Expected list {key}: {profile_id}")
    for signal in item["major_signals"]:
        if not isinstance(signal, dict) or not all(isinstance(signal.get(k), str) and signal[k].strip() for k in ("topic", "look_for", "basis")):
            raise ValidationError(f"Invalid major_signal: {profile_id}")
    for source in item["sources"]:
        if not isinstance(source, dict):
            raise ValidationError(f"Invalid source: {profile_id}")
        url = urlparse(str(source.get("url", "")))
        if (url.scheme != "https" or not url.netloc or not isinstance(source.get("kind"), str)
                or not isinstance(source.get("title"), str) or not source["title"].strip()):
            raise ValidationError(f"Invalid source: {profile_id}")
    if status == "verified" and (not item["sources"] or not item["official_facts"] or not item["major_signals"]):
        raise ValidationError(f"Verified research requires sources, facts, and major_signals: {profile_id}")
    if status == "partial" and not item["sources"]:
        raise ValidationError(f"Partial research requires at least one source: {profile_id}")
    return item



HK_FIVE_IDS = {"hku", "cuhk", "hkust", "cityuhk", "polyu"}
HK_FIVE_STATUSES = {"required", "required_as_applicant_statement", "optional_for_most_programmes"}


def validate_hk_five(root):
    """Check coverage, URL shape, scopes, and known limits; cannot verify live policy."""
    data = load_json(Path(root) / "requirements" / "hk-five-2027.json")
    if data.get("intake") != "2027" or not isinstance(data.get("scope"), str):
        raise ValidationError("HK five baseline must specify 2027 international/non-HKDSE scope")
    try:
        date.fromisoformat(data["reviewed_on"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValidationError("HK five baseline must have valid review date") from exc
    rules = data.get("rules")
    if not isinstance(rules, list) or len(rules) != 5 or {r.get("id") for r in rules} != HK_FIVE_IDS:
        raise ValidationError("HK five baseline must contain five unique university IDs")
    by_id = {r["id"]: r for r in rules}
    for r in rules:
        if r.get("ps_status") not in HK_FIVE_STATUSES or not isinstance(r.get("route"), str) or not r["route"]:
            raise ValidationError("Invalid route or PS status: " + r["id"])
        if r.get("shared_choices") not in ("one_statement_for_all_choices", "per_programme_statement_in_faq", "unconfirmed"):
            raise ValidationError("Invalid choices policy: " + r["id"])
        for field in ("purpose", "exceptions", "unknowns", "sources"):
            if field not in r or not r[field]:
                raise ValidationError("Missing " + field + ": " + r["id"])
        for src in r["sources"]:
            url = urlparse(src.get("url", ""))
            if url.scheme != "https" or not url.netloc or not src.get("title") or not src.get("kind"):
                raise ValidationError("Invalid source URL: " + r["id"])
    if by_id["hku"]["limit"] != {"value": 1000, "unit": "words"}:
        raise ValidationError("HKU verified word limit must remain 1000 words")
    if by_id["cuhk"]["limit"] != {"value": 6000, "unit": "characters"}:
        raise ValidationError("CUHK verified character limit must remain 6000 characters")
    for name in ("hkust", "cityuhk", "polyu"):
        if by_id[name]["limit"] is not None:
            raise ValidationError(name + " has no verified universal length limit")
    if by_id["polyu"]["ps_status"] != "optional_for_most_programmes":
        raise ValidationError("PolyU optionality scope must remain explicit")
    if by_id["cityuhk"]["shared_choices"] != "per_programme_statement_in_faq":
        raise ValidationError("CityUHK per-programme statements must not be recast as shared")
    return {"university_count": len(rules), "intake": "2027", "reviewed_on": data["reviewed_on"]}


def validate(root):
    root = Path(root)
    a = rubric_from_file(root / "rubrics" / "universal.json")
    b = rubric_from_file(root / "rubrics" / "major_fit.json")
    if a["total_points"] != 70 or b["total_points"] != 30:
        raise ValidationError("Experimental baseline must total 70+30 points")
    if {x["id"] for x in a["criteria"]} & {x["id"] for x in b["criteria"]}:
        raise ValidationError("Duplicate IDs across rubrics")
    school_rules = validate_hk_five(root)
    from score_levels import validate_score_bands
    score_bands = validate_score_bands(root)
    return {"score_band_version": score_bands["version"], "total_points": 100, "research_mode": "dynamic", "bundled_profiles_required": False, "hk_five_baseline": school_rules}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--profile", help="Optional JSON research snapshot to validate")
    args = parser.parse_args()
    result = validate(args.root)
    if args.profile:
        obj = load_json(args.profile)
        validate_research_profile(obj.get("id"), obj)
        result["validated_profile"] = obj["id"]
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
