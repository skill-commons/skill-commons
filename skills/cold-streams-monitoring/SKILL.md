---
name: cold-streams-monitoring
description: Automated arXiv monitoring for cold gas filament accretion in galaxy formation. Discovers
  new papers on cold mode accretion, cold flows, cosmological filaments, and related topics. Use for
  on-demand scans or recurring monitoring with the user's scheduler.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# Cold Streams Monitoring — arXiv Paper Tracker

## When to Use
Automated arXiv monitoring for cold gas filament accretion in galaxy formation. Discover new papers on cold mode accretion, cold flows, cosmological filaments, and related topics on demand or through a scheduler chosen by the user.

## Overview
This skill contains a reusable operational workflow. Follow the existing task-specific steps and examples in the sections below.

## Pitfalls
- Do not hardcode credentials, tokens, or personal secrets.
- Verify external service URLs, paths, and permissions before making changes.
- Keep generated outputs reproducible and record input assumptions.

## Verification
- Confirm required inputs and credentials are available.
- Run the smallest safe command or example before scaling up.
- Check produced files, API responses, or plots before reporting success.


Automated discovery of new papers on **cold gas filament accretion** in cosmological simulations — the cold mode of galaxy formation, cold streams, and related phenomena.

## What Counts as Relevant

Papers relevant to this monitoring topic fall into these areas:

- **Cold mode accretion** — cold gas streams feeding galaxies (Kereš et al. 2005 paradigm)
- **Cold flows / cold filaments** — cosmological gas filaments delivering fuel to halos
- **Cold mode vs hot mode** — transition at virial temperature ~10^6 K
- **Galaxy fuel supply** — how galaxies maintain star formation via cold accretion
- **Filamentary ISM / CGM** — cold gas in circumgalactic and intergalactic medium
- **Cosmological simulations with cold gas** — EAGLE, Illustris, TNG, FLAMINGO, etc.
- **High-z galaxy formation** — cold accretion at z > 2
- **Shooting instabilities in filaments** — filament fragmentation, cooling instabilities

## Primary arXiv Search Queries

### Core Query (most specific)
```
(all:"cold stream" OR all:"cold flow" OR all:"cold accretion" OR all:"cold mode")
```
Catches papers explicitly mentioning cold streams/flows/modes.

### Extended Query (broader coverage)
```
(all:"cold stream" OR all:"cold flow" OR all:"cold accretion" OR all:"cold mode"
 OR all:"filament accretion" OR all:"gas filament" OR all:"cooling filament")
```
Catches filament-specific papers.

### Subcategory Queries (for targeted scans)
```
# Filament structure & stability
(all:"filament fragmentation" OR all:"shooting instab*" OR all:"filament cooling")

# CGM/ISM cold gas (related)
(all:"cold phase" OR all:"multiphase CGM" OR all:"multiphase ISM")

# Simulation-based approaches
all:"cold stream*" AND (all:simulation OR all:simul*)
```

### Recommended arXiv Categories
- `astro-ph.GA` — Astrophysics of Galaxies (primary)
- `astro-ph.CO` — Cosmology and Nongalactic Astrophysics
- `astro-ph.HE` — High Energy Astrophysical Phenomena (for AGN-related gas dynamics)
- `astro-ph.IM` — Instrumentation and Methods (for simulation tools)

## Recurring Schedule Setup

Use `scripts/cold_streams_monitor.py` for deterministic scans. Run it once and inspect
the output before adding it to cron, systemd, a CI schedule, or an agent client's
recurring-automation feature. Ask before creating or changing a schedule.

### Minimal: Weekly Cold Streams Scan
```bash
python3 scripts/cold_streams_monitor.py --mode core
```

### Extended: Full Filament Coverage
```bash
python3 scripts/cold_streams_monitor.py --mode extended
```

### Daily (aggressive, more noise but catches everything)
```bash
python3 scripts/cold_streams_monitor.py \
  --query '(all:"cold stream" OR all:"cold flow") AND cat:astro-ph.GA' \
  --max 15
```

For a POSIX cron installation, schedule the command with absolute paths and redirect
stdout and stderr to reviewable files. Do not assume a particular home directory or
delivery channel.

## One-Time Manual Scan

### Quick Scan (via terminal)
```bash
# Core query — 10 most recent papers
curl -sG "https://export.arxiv.org/api/query" \
  --data-urlencode 'search_query=(all:"cold stream" OR all:"cold flow" OR all:"cold accretion" OR all:"cold mode") AND cat:astro-ph.GA' \
  --data-urlencode 'sortBy=submittedDate' \
  --data-urlencode 'sortOrder=descending' \
  --data-urlencode 'max_results=10' | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))[:200]
    summary = entry.find('a:summary', ns).text.strip()
    print(f'{i+1}. [{arxiv_id}] {title} ({published})')
    print(f'   Authors: {authors}')
    print(f'   Abstract: {summary[:500]}...')
    print(f'   PDF: https://arxiv.org/pdf/{arxiv_id}')
    print()
"
```

### Extended Scan — Filament Coverage
```bash
# Extended query with filament keywords
curl -sG "https://export.arxiv.org/api/query" \
  --data-urlencode 'search_query=(all:"cold stream" OR all:"cold flow" OR all:"cold accretion" OR all:"cold mode" OR all:"filament accretion" OR all:"gas filament") AND cat:astro-ph.GA' \
  --data-urlencode 'sortBy=submittedDate' \
  --data-urlencode 'sortOrder=descending' \
  --data-urlencode 'max_results=15' | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))[:200]
    cats = ', '.join(c.get('term') for c in entry.findall('a:category', ns))
    summary = entry.find('a:summary', ns).text.strip()
    print(f'{i+1}. [{arxiv_id}] {title} ({published})')
    print(f'   Authors: {authors}')
    print(f'   Categories: {cats}')
    print(f'   Abstract: {summary[:500]}...')
    print(f'   PDF: https://arxiv.org/pdf/{arxiv_id}')
    print()
"
```

## Workflow: From Scan to Analysis

1. **Run scan** — use the bundled script, one-time commands, or scheduler output
2. **Filter** — identify simulation-based papers (look for: hydro, SPH, GADGET, AREPO, ENZEL, Illustris, TNG, EAGLE, FLAMINGO, RAMSES, GIZMO)
3. **Deep dive** — fetch arxiv.org/abs pages or ar5iv HTML for more context
4. **Classify** — mark as simulation/analytical/observational/theoretical
5. **Track** — note key findings in a user-approved file or system

### Simulation Code Keywords (filtering signal from noise)
- **SPH codes**: GADGET, AREPO, ENZEL, GASOL, PHANTOM, SWIFT, ART
- **Grid codes**: RAMSES, ENZO, FLASH, ENZO, CLOUDDY
- **Hybrid**: GIZMO, FLASH
- **Projects**: Illustris, TNG (TNG100/TNG300), EAGLE, FLAMINGO, SIMBA, MAGNETICUM, OA
- **Analysis**: HOP, SUBFIND, ROCKSTAR, HALO FINDER

## Classic Papers (Baseline References)

These are discovery seeds from the source workflow. Verify exact titles, authors,
journal metadata, and relevance against ADS, arXiv, or the publisher before citing
them; the monitor does not validate bibliography records.

| Paper | Key Result |
|-------|-----------|
| Kereš et al. 2005, MNRAS 363, 1 | Introduced cold mode accretion concept |
| Keres et al. 2005, Phys. Rev. D 72, 043514 | Cold streams at z~2-3 in massive halos |
| Davé et al. 2001, MNRAS 326, 62 | Early work on warm vs hot accretion |
| Dekel & Birnboim 2006, MNRAS 368, 2 | Cold mode below virial T~10^6 K |
| Birnboim & Dekel 2003, MNRAS 345, 349 | Halo shock stability analysis |
| Fabian 1994, ARA&A 32, 277 | Early review of gas accretion in halos |
| Ocvirk et al. 2008, MNRAS 390, 1 | Simulation of cold flows in halos |
| Dekel et al. 2009, MNRAS 395, 1757 | Cold mode in Lambda-CDM |
| van de Voosten et al. 2011, MNRAS 414, 3463 | Cold flows vs feedback in TNG-like sims |
| Nelson et al. 2018, MNRAS 475, 624 (TNG) | IllustrisTNG cold accretion analysis |

## Customizing the Monitor

### Narrow to specific simulations
```
all:"cold stream" AND (all:AREPO OR all:GADGET OR all:RAMSES OR all:ENZO) AND cat:astro-ph.GA
```

### Narrow to redshift range
```
(abs:"z > 2" OR abs:"high z" OR abs:high-redshift) AND all:"cold stream" AND cat:astro-ph.GA
```

### Focus on CGM context
```
(all:"cold stream" OR all:"cold flow") AND (all:CGM OR all:circumgalactic) AND cat:astro-ph.GA
```

### Track specific authors
```
au:"Pavel Dekel" AND cat:astro-ph.GA
au:"Daniel Ceverino" AND cat:astro-ph.GA
au:"Researcher Name" AND cat:astro-ph.GA
```

## Rate Limits & Tips

- **arXiv API**: ~1 req / 3 sec. If you get rate-limited, back off 6+ seconds.
- **TLS certificate verification failures**: Repair the local CA trust store or
  institution proxy configuration. Do not disable certificate verification or use an
  unverified SSL context.
- **Browser-based extraction**: It can time out or depend on paid services. Prefer the
  API or `curl` patterns above.
- **Batch id_list queries**: Up to ~10 IDs per call to minimize round trips.
- **Semantic Scholar**: Use for citation tracking of key papers. Check citationCount for new papers on this topic.

## Integration with Existing Skills

- **arxiv** — Core search and parsing; this skill wraps it with domain-specific queries
- **reana** — If simulation analysis is needed, run the monitoring on REANA with large datasets
- **datashader** — If visualizing cold stream distributions in simulation data
- **matplotlib-figs** — Plotting results from papers found by the monitor

## Recurring-Agent Prompt Examples

If the selected client can run recurring prompts, use the following text as the task
body. Configure timing and delivery with that client's documented scheduler.

### Weekly comprehensive scan
> Run the cold streams arXiv monitor: search for papers containing “cold stream,”
> “cold flow,” “cold accretion,” or “cold mode” in category astro-ph.GA, sorted by
> submitted date descending, with at most 15 results. For each paper show title, arXiv
> ID, date, lead author, categories, and abstract summary. Flag simulation-based papers
> using named simulation-code signals. End with a one-line summary of the scan.

### Monthly literature review draft
> Compile a mini literature review of recent cold-stream papers. Search arXiv for
> papers on cold streams, flows, or accretion in astro-ph.GA from the past month. For
> the five most relevant, provide a citation, a three-sentence summary, the simulation
> method when applicable, the paper's stated key finding, and its relation to the
> Kereš–Dekel–Birnboim framework. Distinguish paper claims from your interpretation.
