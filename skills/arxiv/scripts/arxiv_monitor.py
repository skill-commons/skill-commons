#!/usr/bin/env python3
"""Run a reusable arXiv topic scan with optional seen-paper state."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

API = "https://export.arxiv.org/api/query"
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="arXiv search_query expression")
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="Category filter such as astro-ph.GA; repeat to OR categories",
    )
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--state", type=Path, help="Optional JSON file of seen paper versions")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()
    if not 1 <= args.max_results <= 100:
        parser.error("--max-results must be between 1 and 100 for a bounded monitor")
    if args.start < 0:
        parser.error("--start must be non-negative")
    return args


def combined_query(query: str, categories: list[str]) -> str:
    cleaned = [value.strip() for value in categories if value.strip()]
    if not cleaned:
        return query
    category_query = " OR ".join(f"cat:{value}" for value in cleaned)
    return f"({query}) AND ({category_query})"


def fetch(query: str, max_results: int, start: int) -> bytes:
    params = urllib.parse.urlencode(
        {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "start": start,
            "max_results": max_results,
        }
    )
    request = urllib.request.Request(
        f"{API}?{params}",
        headers={"User-Agent": "skill-commons-arxiv-monitor/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def text(entry: ET.Element, field: str) -> str:
    node = entry.find(field, ATOM)
    return "" if node is None or node.text is None else " ".join(node.text.split())


def parse(payload: bytes) -> list[dict[str, Any]]:
    root = ET.fromstring(payload)
    papers: list[dict[str, Any]] = []
    for entry in root.findall("a:entry", ATOM):
        raw_id = text(entry, "a:id").rsplit("/abs/", 1)[-1]
        papers.append(
            {
                "id": raw_id,
                "title": text(entry, "a:title"),
                "published": text(entry, "a:published")[:10],
                "updated": text(entry, "a:updated")[:10],
                "authors": [text(author, "a:name") for author in entry.findall("a:author", ATOM)],
                "categories": [
                    category.get("term", "")
                    for category in entry.findall("a:category", ATOM)
                    if category.get("term")
                ],
                "summary": text(entry, "a:summary"),
                "abstract_url": f"https://arxiv.org/abs/{raw_id}",
                "pdf_url": f"https://arxiv.org/pdf/{raw_id}",
            }
        )
    return papers


def load_seen(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("seen"), list):
        raise ValueError(f"invalid monitor state: {path}")
    return {str(value) for value in data["seen"]}


def save_seen(path: Path | None, seen: set[str]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps({"seen": sorted(seen)}, indent=2) + "\n")
    temporary.replace(path)


def markdown(papers: list[dict[str, Any]], query: str) -> str:
    lines = ["# arXiv topic monitor", "", f"Query: `{query}`", ""]
    if not papers:
        lines.append("No unseen papers found.")
        return "\n".join(lines)
    for index, paper in enumerate(papers, 1):
        authors = ", ".join(paper["authors"][:5])
        if len(paper["authors"]) > 5:
            authors += " et al."
        lines.extend(
            [
                f"## {index}. {paper['title']}",
                "",
                f"- ID: [{paper['id']}]({paper['abstract_url']})",
                f"- Published: {paper['published']}",
                f"- Authors: {authors}",
                f"- Categories: {', '.join(paper['categories'])}",
                f"- Abstract: {paper['summary']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    query = combined_query(args.query, args.category)
    try:
        papers = parse(fetch(query, args.max_results, args.start))
        seen = load_seen(args.state)
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        print(f"arXiv monitor failed: {exc}", file=sys.stderr)
        return 1
    unseen = [paper for paper in papers if paper["id"] not in seen]
    if args.json:
        print(json.dumps({"query": query, "papers": unseen}, indent=2))
    else:
        print(markdown(unseen, query))
    save_seen(args.state, seen | {paper["id"] for paper in papers})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
