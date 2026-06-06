#!/usr/bin/env python3
"""Convert JSON Resume data to RenderCV YAML. Never modifies the input JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

NETWORK_ALIASES = {
    "github": "GitHub",
    "gitlab": "GitLab",
    "linkedin": "LinkedIn",
    "twitter": "X",
    "x": "X",
    "stackoverflow": "StackOverflow",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "mastodon": "Mastodon",
    "orcid": "ORCID",
    "reddit": "Reddit",
    "bluesky": "Bluesky",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "leetcode": "Leetcode",
    "imdb": "IMDB",
    "researchgate": "ResearchGate",
    "google scholar": "Google Scholar",
}


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.lower() == "present":
        return "present"
    if len(normalized) >= 7 and normalized[4] == "-":
        return normalized[:7]
    return normalized


def format_location(location: dict[str, Any] | None) -> str | None:
    if not location:
        return None
    parts: list[str] = []
    for key in ("city", "region", "countryCode"):
        value = location.get(key)
        if value:
            parts.append(str(value))
    return ", ".join(parts) if parts else None


def normalize_network(network: str) -> str:
    return NETWORK_ALIASES.get(network.strip().lower(), network.strip())


def build_social_networks(profiles: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    if not profiles:
        return []

    social_networks: list[dict[str, str]] = []
    for profile in profiles:
        username = profile.get("username")
        if not username:
            continue
        social_networks.append(
            {
                "network": normalize_network(profile.get("network", "")),
                "username": username,
            }
        )
    return social_networks


def build_experience(work: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not work:
        return []

    entries: list[dict[str, Any]] = []
    for job in work:
        entry: dict[str, Any] = {
            "company": job["name"],
            "position": job["position"],
        }
        start_date = normalize_date(job.get("startDate"))
        end_date = normalize_date(job.get("endDate"))
        if start_date:
            entry["start_date"] = start_date
        if end_date:
            entry["end_date"] = end_date
        if job.get("location"):
            entry["location"] = job["location"]
        if job.get("summary"):
            entry["summary"] = job["summary"]
        if job.get("highlights"):
            entry["highlights"] = job["highlights"]
        entries.append(entry)
    return entries


def build_education(education: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not education:
        return []

    entries: list[dict[str, Any]] = []
    for item in education:
        entry: dict[str, Any] = {
            "institution": item["institution"],
            "area": item.get("area", ""),
        }
        if item.get("studyType"):
            entry["degree"] = item["studyType"]
        start_date = normalize_date(item.get("startDate"))
        end_date = normalize_date(item.get("endDate"))
        if start_date:
            entry["start_date"] = start_date
        if end_date:
            entry["end_date"] = end_date
        if item.get("location"):
            entry["location"] = item["location"]
        highlights: list[str] = []
        if item.get("courses"):
            highlights.extend(item["courses"])
        if highlights:
            entry["highlights"] = highlights
        entries.append(entry)
    return entries


def build_project_name(project: dict[str, Any]) -> str:
    name = project["name"]
    keywords = project.get("keywords") or []
    if not keywords:
        return name
    return f"{name} | {', '.join(keywords)}"


def build_projects(projects: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not projects:
        return []

    entries: list[dict[str, Any]] = []
    for project in projects:
        entry: dict[str, Any] = {"name": build_project_name(project)}
        if project.get("description"):
            entry["summary"] = project["description"]
        start_date = normalize_date(project.get("startDate"))
        end_date = normalize_date(project.get("endDate"))
        if start_date:
            entry["start_date"] = start_date
        if end_date:
            entry["end_date"] = end_date
        if project.get("highlights"):
            entry["highlights"] = project["highlights"]
        entries.append(entry)
    return entries


def build_skills_from_json(skills: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    if not skills:
        return []

    entries: list[dict[str, str]] = []
    for skill in skills:
        label = skill.get("name")
        keywords = skill.get("keywords") or []
        if not label:
            continue
        details = ", ".join(keywords)
        if skill.get("level") and details:
            details = f"{details} ({skill['level']})"
        elif skill.get("level"):
            details = skill["level"]
        entries.append({"label": label, "details": details})
    return entries


def build_skills_from_projects(projects: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    if not projects:
        return []

    seen: set[str] = set()
    keywords: list[str] = []
    for project in projects:
        for keyword in project.get("keywords") or []:
            normalized = keyword.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                keywords.append(normalized)

    if not keywords:
        return []
    return [{"label": "Technologies", "details": ", ".join(keywords)}]


def build_cv(resume: dict[str, Any]) -> dict[str, Any]:
    basics = resume.get("basics") or {}
    cv: dict[str, Any] = {}

    if basics.get("name"):
        cv["name"] = basics["name"]
    if basics.get("label"):
        cv["headline"] = basics["label"]
    if basics.get("email"):
        cv["email"] = basics["email"]
    if basics.get("phone"):
        cv["phone"] = basics["phone"]
    if basics.get("url"):
        cv["website"] = basics["url"]

    location = format_location(basics.get("location"))
    if location:
        cv["location"] = location

    social_networks = build_social_networks(basics.get("profiles"))
    if social_networks:
        cv["social_networks"] = social_networks

    sections: dict[str, Any] = {}
    if basics.get("summary"):
        sections["summary"] = [basics["summary"]]

    experience = build_experience(resume.get("work"))
    if experience:
        sections["experience"] = experience

    education = build_education(resume.get("education"))
    if education:
        sections["education"] = education

    projects = build_projects(resume.get("projects"))
    if projects:
        sections["projects"] = projects

    skills = build_skills_from_json(resume.get("skills"))
    if not skills:
        skills = build_skills_from_projects(resume.get("projects"))
    if skills:
        sections["Technical Skills"] = skills

    if sections:
        cv["sections"] = sections

    return cv


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_design(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        design = yaml.safe_load(handle) or {}
    if not isinstance(design, dict):
        raise ValueError(f"Design file must contain a YAML mapping: {path}")
    return design


def build_rendercv_document(resume: dict[str, Any], design: dict[str, Any]) -> dict[str, Any]:
    document = {"cv": build_cv(resume)}
    for key in ("design", "locale", "settings"):
        if key in design:
            document[key] = design[key]
    return document


def write_yaml(document: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            document,
            handle,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=1000,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to resume.json")
    parser.add_argument("--design", required=True, type=Path, help="Path to design.yaml")
    parser.add_argument("--output", required=True, type=Path, help="Path to generated cv.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    resume = load_json(args.input)
    design = load_design(args.design)
    document = build_rendercv_document(resume, design)
    write_yaml(document, args.output)


if __name__ == "__main__":
    main()
