---
name: arxiv
description: Search and retrieve academic papers from arXiv using the free REST API. Query by keyword,
  author, category, or paper ID. Fetch abstracts, full PDFs, generate BibTeX, and explore citations via
  Semantic Scholar.
license: MIT
metadata:
  research-skill.manifest: research-skill.yaml
---

# arXiv Research

## When to Use
Use this skill when the user needs to find, read, or cite academic papers. Tasks include: literature review, finding related work, checking citations, generating BibTeX, or extracting paper content.

## Procedure

### 1. Search papers
```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5&sortBy=submittedDate&sortOrder=descending"
```

### 2. Parse XML to clean output
```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
    summary = entry.find('a:summary', ns).text.strip()[:200]
    cats = ', '.join(c.get('term') for c in entry.findall('a:category', ns))
    print(f'{i+1}. [{arxiv_id}] {title}')
    print(f'   Authors: {authors}')
    print(f'   Published: {published} | Categories: {cats}')
    print(f'   Abstract: {summary}...')
    print(f'   PDF: https://arxiv.org/pdf/{arxiv_id}')
    print()
"
```

### 3. Fetch specific paper by ID
```bash
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300,2401.12345"
```

### 4. Read paper content — use ar5iv HTML, NOT the PDF

Avoid sending a full PDF to a generic remote extraction or summarization service.
Large files may be slow, expensive, or disclose content to an undeclared service.
Prefer ar5iv's compact HTML representation, fetch it with `curl`, and parse it locally.

```bash
ID=2111.01860
# ar5iv HTML rendering (two hosts; second is the fallback)
curl -sL "https://ar5iv.labs.arxiv.org/html/$ID" -o paper.html \
  || curl -sL "https://ar5iv.org/html/$ID" -o paper.html
wc -c paper.html        # expect hundreds of KB; a few hundred bytes => no ar5iv HTML, use abstract fallback

# Parse locally with Python: plain text + figure captions
python3 - <<'PY'
import re, html, pathlib
src = pathlib.Path("paper.html").read_text(errors="ignore")
src = re.sub(r"(?is)<(script|style).*?</\1>", " ", src)     # drop scripts/styles
text = html.unescape(re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", src)))
print(text[:6000])                                          # abstract + intro + method
for m in re.finditer(r"(Figure\s+\d+\s*[.:][^.]{0,400}\.)", text):
    print("CAPTION:", m.group(1).strip())                   # locate the figure you must reproduce
PY
```

Abstract only (fastest, keyless) — use the API:
```bash
curl -s "https://export.arxiv.org/api/query?id_list=2111.01860" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns={'a':'http://www.w3.org/2005/Atom'}
e=ET.parse(sys.stdin).getroot().find('a:entry', ns)
print(e.find('a:summary', ns).text.strip())"
```

> Fallback: if `paper.html` comes back tiny (rare — papers with no TeX source, or just-posted
> ones not yet on ar5iv), use the abstract API above, then fetch the small **abs** page
> (`https://arxiv.org/abs/<id>`) if necessary. Do not send the PDF to an undeclared
> third-party extraction service.

### 5. Generate BibTeX
```bash
curl -s "https://export.arxiv.org/api/query?id_list=1706.03762" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
root = ET.parse(sys.stdin).getroot()
entry = root.find('a:entry', ns)
title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
authors = ' and '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
year = entry.find('a:published', ns).text[:4]
raw_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
cat = entry.find('arxiv:primary_category', ns)
primary = cat.get('term') if cat is not None else 'cs.LG'
last_name = entry.find('a:author', ns).find('a:name', ns).text.split()[-1]
print(f'@article{{{last_name}{year}_{raw_id.replace(\".\", \"\")},')
print(f'  title     = {{{title}}},')
print(f'  author    = {{{authors}}},')
print(f'  year      = {{{year}}},')
print(f'  eprint    = {{{raw_id}}},')
print(f'  archivePrefix = {{arXiv}},')
print(f'  primaryClass  = {{{primary}}},')
print(f'  url       = {{https://arxiv.org/abs/{raw_id}}}')
print('}')
"
```

## arXiv Query Syntax

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:transformer+attention` |
| `ti:` | Title | `ti:large+language+models` |
| `au:` | Author | `au:hinton` |
| `abs:` | Abstract | `abs:reinforcement+learning` |
| `cat:` | Category | `cat:cs.LG` |

Boolean: `all:A+ANDNOT+all:B`, `all:A+OR+all:B`

## Sort and Pagination

| Parameter | Options |
|-----------|---------|
| `sortBy` | `relevance`, `lastUpdatedDate`, `submittedDate` |
| `sortOrder` | `ascending`, `descending` |
| `max_results` | 1–30000 |

## Semantic Scholar (Citations)

For citation counts and related papers (arXiv has no citation data):

```bash
# Paper details + citations
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount,influentialCitationCount,year,abstract"

# Who cited this paper
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10"

# What this paper cites
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10"

# Paper recommendations
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"], "negativePaperIds": []}'
```

## Complete Research Workflow
1. Discover: search arXiv API
2. Assess impact: Semantic Scholar citation counts
3. Read abstract: arXiv API `summary` field (or fetch the small abs page)
4. Read full paper: curl ar5iv HTML + parse locally (NOT the PDF)
5. Find related work: Semantic Scholar references/citations
6. Generate BibTeX: API metadata parsing

## Rate Limits

| API | Rate | Auth |
|-----|------|------|
| arXiv | ~1 req / 3s | None |
| Semantic Scholar | 1 req / second | None |

## Pitfalls
- arXiv returns Atom XML — use the parsing snippet for clean output.
- Old arXiv IDs use format `hep-th/0601001`, new ones use `2402.03300`.
- Do NOT use `/query/tap/` endpoints — they return HTML, not JSON.
- **Do not send a full PDF to a generic remote extractor.** Fetch ar5iv HTML with
  `curl` and parse locally.
- ar5iv URL form is `https://ar5iv.labs.arxiv.org/html/<id>` (HTML), not `/pdf/<id>`.
- Semantic Scholar is read-only — do not attempt to POST paper metadata without the recommendations endpoint.
- Always check for withdrawn papers — summary field may contain withdrawal notices.

## Verification
- Search returns ≥ 1 paper with title, authors, and arXiv ID.
- BibTeX entry parses to a valid `@article{}` block.
- Semantic Scholar returns non-zero citation counts for well-known papers.
- ar5iv HTML fetch returns hundreds of KB and parses to non-empty text + ≥1 figure caption.
