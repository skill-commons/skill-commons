#!/usr/bin/env python3
"""
Cold Streams arXiv Monitor
Query arXiv API for papers on cold gas accretion in galaxy formation.
Outputs clean, structured reports.

Usage:
    python3 cold_streams_monitor.py              # Core query, 10 results
    python3 cold_streams_monitor.py --extended   # Extended query, 15 results
    python3 cold_streams_monitor.py --top50      # Top 50, core query
    python3 cold_streams_monitor.py --query "your+custom+query" --max 20
    python3 cold_streams_monitor.py --categories astro-ph.HE,astro-ph.CO

Simulation codes are auto-detected and flagged.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# ── Configuration ──────────────────────────────────────────────────────────

ARXIV_API = "https://export.arxiv.org/api/query"
CORE_TOPIC_QUERY = (
    '(all:"cold stream" OR all:"cold flow" OR all:"cold accretion" OR all:"cold mode")'
)
EXTENDED_TOPIC_QUERY = (
    '(all:"cold stream" OR all:"cold flow" OR all:"cold accretion" OR all:"cold mode"'
    ' OR all:"filament accretion" OR all:"gas filament")'
)

QUERIES = {
    "core": {
        "search": CORE_TOPIC_QUERY,
        "max_results": 10,
        "description": "Core cold streams query",
    },
    "extended": {
        "search": EXTENDED_TOPIC_QUERY,
        "max_results": 15,
        "description": "Extended with filament coverage",
    },
    "top50": {
        "search": CORE_TOPIC_QUERY,
        "max_results": 50,
        "description": "Top 50 core-query results",
    },
}

SIM_CODE_KEYWORDS = [
    # Truly unique simulation code/project names (no false-positive matches)
    "arepo",
    "trilberry",
    "trilix",
    "enzo",
    "gizmo",
    "flamingo",
    "simba",
    "magneticum",
    "subfind",
    "gasol",
    "illustris",
    # Broad signal phrases (not code-specific, but signal simulation work)
    "cosmological simulation",
    "cosmological hydro",
    "hydrodynamical simulation",
    "simulation",
]

CATEGORY_LABELS = {
    "astro-ph.GA": "Astrophysics of Galaxies",
    "astro-ph.CO": "Cosmology & NGA",
    "astro-ph.HE": "High Energy Astrophysics",
    "astro-ph.IM": "Instrumentation & Methods",
    "physics.comp-ph": "Computational Physics",
}


def fetch_arxiv(search_query: str, max_results: int = 10, start: int = 0) -> str:
    """Fetch results from arXiv API."""
    encoded_q = urllib.parse.quote(search_query, safe="+")
    url = (
        f"{ARXIV_API}?search_query={encoded_q}"
        f"&sortBy=submittedDate"
        f"&sortOrder=descending"
        f"&start={start}"
        f"&max_results={max_results}"
    )
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "ColdStreamsMonitor/1.0 (skill-commons)")
    time.sleep(3)  # arXiv rate limit: ~1 req / 3 sec

    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8")


def parse_entries(xml_data: str):
    """Parse arXiv API XML into list of dicts."""
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    entries = []
    for entry in root.findall("a:entry", ns):
        title = entry.find("a:title", ns).text.strip().replace("\n", " ")
        arxiv_id = entry.find("a:id", ns).text.strip().split("/abs/")[-1]
        published = entry.find("a:published", ns).text[:10]
        authors = [a.find("a:name", ns).text for a in entry.findall("a:author", ns)]
        summary = entry.find("a:summary", ns).text.strip()
        categories = [c.get("term") for c in entry.findall("a:category", ns)]

        # Detect simulation codes
        text_lower = (title + " " + summary).lower()
        sim_codes = [kw for kw in SIM_CODE_KEYWORDS if kw in text_lower]
        is_simulation = len(sim_codes) > 0

        entries.append(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "published": published,
                "authors": authors,
                "authors_str": ", ".join(authors[:5]) + (" et al." if len(authors) > 5 else ""),
                "summary": summary,
                "categories": categories,
                "is_simulation": is_simulation,
                "sim_codes": sim_codes,
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
                "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
            }
        )
    return entries


def classify_paper(entry: dict) -> str:
    """Classify paper as simulation/theoretical/observational/mixed."""
    text = entry["title"].lower() + " " + entry["summary"].lower()
    labels = []

    if entry["is_simulation"] or entry["sim_codes"]:
        labels.append("SIM")
    if any(
        kw in text
        for kw in ["analytic", "analytical", "model", "scaling", "semianalytic", "semi-analytic"]
    ):
        labels.append("THEORY")
    if any(
        kw in text
        for kw in [
            "observed",
            "observation",
            "survey",
            "data",
            "spectroscopic",
            "imaging",
            "integral-field",
            "ifs",
        ]
    ):
        labels.append("OBS")
    if any(kw in text for kw in ["semi-analytic", "subgrid", "sub-grid"]):
        labels.append("HYBRID")

    return "+".join(labels) if labels else "UNC"


def format_report(entries: list, title: str = "Cold Streams arXiv Monitor") -> str:
    """Format entries as a clean report."""
    paper_label = "paper" if len(entries) == 1 else "papers"
    lines = [
        f"## {title}",
        f"\nFound {len(entries)} {paper_label}.",
        "",
    ]

    sim_count = sum(1 for e in entries if e["is_simulation"])
    total = len(entries)
    lines.append(
        f"**Breakdown:** {sim_count}/{total} simulation-based, {total - sim_count} non-simulation"
    )
    lines.append("")

    for i, entry in enumerate(entries, 1):
        cls = classify_paper(entry)
        lines.append(f"### {i}. [{entry['arxiv_id']}] {entry['title']}")
        lines.append(f"- **Date:** {entry['published']}")
        lines.append(f"- **Authors:** {entry['authors_str']}")
        lines.append(
            f"- **Categories:** {', '.join(CATEGORY_LABELS.get(c, c) for c in entry['categories'])}"
        )
        lines.append(f"- **Type:** {cls}")
        if entry["sim_codes"]:
            lines.append(f"- **Sim codes:** {', '.join(entry['sim_codes'])}")
        lines.append(f"- **Abstract:** {entry['summary'][:800]}...")
        lines.append(f"- **PDF:** {entry['pdf_url']}")
        lines.append(f"- **Abs:** {entry['abs_url']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Cold Streams arXiv Monitor")
    parser.add_argument("--query", default=None, help="Custom arXiv search query")
    parser.add_argument(
        "--mode",
        choices=["core", "extended", "top50"],
        default=None,
        help="Predefined mode (overrides --query)",
    )
    parser.add_argument(
        "--top50", action="store_true", help="Compatibility shortcut for --mode top50"
    )
    parser.add_argument(
        "--extended", action="store_true", help="Compatibility shortcut for --mode extended"
    )
    parser.add_argument("--max", type=int, default=None, help="Max results")
    parser.add_argument("--categories", default=None, help="Comma-separated arXiv categories")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--start", type=int, default=0, help="Start offset")
    args = parser.parse_args()

    # Determine query and max_results
    shortcut_count = int(args.top50) + int(args.extended)
    if shortcut_count and args.mode:
        parser.error("use either --mode or a shortcut flag, not both")
    if shortcut_count > 1:
        parser.error("--top50 and --extended are mutually exclusive")
    selected_mode = "top50" if args.top50 else "extended" if args.extended else args.mode
    if selected_mode and selected_mode in QUERIES:
        q = QUERIES[selected_mode]
        search_query = q["search"]
        max_results = args.max or q["max_results"]
    elif args.query:
        search_query = args.query
        max_results = args.max or 10
    else:
        search_query = QUERIES["core"]["search"]
        max_results = args.max or QUERIES["core"]["max_results"]

    # Explicit categories replace the predefined default. Custom-query category
    # clauses remain intact and are combined with any explicit category filter.
    if args.categories:
        cats = [item.strip() for item in args.categories.split(",") if item.strip()]
        if not cats:
            parser.error("--categories requires at least one non-empty category")
        category_query = " OR ".join(f"cat:{item}" for item in cats)
        search_query = f"({search_query}) AND ({category_query})"
    elif not args.query:
        search_query = f"{search_query} AND cat:astro-ph.GA"

    progress_stream = sys.stderr if args.json else sys.stdout
    print(f"Query: {search_query}", file=progress_stream)
    print(f"Max results: {max_results}\n", file=progress_stream)

    try:
        xml_data = fetch_arxiv(search_query, max_results, start=args.start)
        entries = parse_entries(xml_data)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("No results found.")
        return

    if args.json:
        print(json.dumps(entries, indent=2))
    else:
        title = "Cold Streams arXiv Monitor"
        if selected_mode:
            title += f" ({QUERIES[selected_mode]['description']})"
        print(format_report(entries, title))


if __name__ == "__main__":
    main()
