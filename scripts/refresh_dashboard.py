#!/usr/bin/env python3
"""
Daily AI Intelligence Dashboard Ingestion & Data Management Script
Fetches live RSS/Atom feeds and web pages across the 14 tracked sources,
calls the Gemini API (via GEMINI_API_KEY) to synthesize 1-2 sentence bullet
takeaways per story, maintains a rolling 5-day archive in data/dashboard_data.json,
and rebuilds index.html.
"""

import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

DASHBOARD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(DASHBOARD_DIR, "data", "dashboard_data.json")
BUILD_SCRIPT = os.path.join(DASHBOARD_DIR, "scripts", "build_html.py")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

# 14 Tracked Sources with primary RSS/Atom feeds and web fallbacks
SOURCES = [
    # Business and enterprise (8)
    {
        "name": "VentureBeat",
        "sector": "Business and enterprise",
        "type": "Web / RSS",
        "url": "https://venturebeat.com/category/ai/",
        "feeds": [
            "https://venturebeat.com/category/ai/feed/",
            "https://venturebeat.com/feed/",
        ],
    },
    {
        "name": "Fortune — Eye on AI",
        "sector": "Business and enterprise",
        "type": "Web / RSS",
        "url": "https://fortune.com/tag/eye-on-ai/",
        "feeds": [
            "https://fortune.com/tag/eye-on-ai/feed/",
            "https://fortune.com/tag/artificial-intelligence/feed/",
            "https://fortune.com/feed/",
        ],
    },
    {
        "name": "Harvard Business Review — AI and Machine Learning",
        "sector": "Business and enterprise",
        "type": "Web / Journal",
        "url": "https://hbr.org/topic/subject/artificial-intelligence",
        "feeds": [
            "http://feeds.hbr.org/harvardbusiness",
            "https://hbr.org/topic/subject/artificial-intelligence",
        ],
    },
    {
        "name": "MIT Sloan — AI at Work",
        "sector": "Business and enterprise",
        "type": "Web / RSS",
        "url": "https://mitsloan.mit.edu/ideas-made-to-matter/topic/artificial-intelligence",
        "feeds": [
            "https://sloanreview.mit.edu/topic/artificial-intelligence/feed/",
            "https://mitsloan.mit.edu/ideas-made-to-matter/topic/artificial-intelligence",
        ],
    },
    {
        "name": "The Batch",
        "sector": "Business and enterprise",
        "type": "Web / Newsletter",
        "url": "https://www.deeplearning.ai/the-batch/",
        "feeds": [
            "https://www.deeplearning.ai/the-batch/feed/",
            "https://www.deeplearning.ai/the-batch/",
        ],
    },
    {
        "name": "The Neuron",
        "sector": "Business and enterprise",
        "type": "Web / Newsletter",
        "url": "https://www.theneurondaily.com/",
        "feeds": [
            "https://www.theneurondaily.com/feed",
            "https://www.theneurondaily.com/",
        ],
    },
    {
        "name": "TLDR AI",
        "sector": "Business and enterprise",
        "type": "Web / Newsletter",
        "url": "https://tldr.tech/ai",
        "feeds": [
            "https://tldr.tech/api/rss/ai",
            "https://bullrich.dev/tldr-rss/ai.rss",
            "https://tldr.tech/ai",
        ],
    },
    {
        "name": "AlphaSignal AI",
        "sector": "Business and enterprise",
        "type": "Web / Newsletter",
        "url": "https://alphasignal.ai/",
        "feeds": [
            "https://alphasignal.ai/feed",
            "https://alphasignal.ai/",
        ],
    },
    # Higher education (5)
    {
        "name": "The Chronicle — Jagged Intelligence",
        "sector": "Higher education",
        "type": "Web / Newsletter",
        "url": "https://www.chronicle.com/newsletter/jagged-intelligence",
        "feeds": [
            "https://www.chronicle.com/newsletter/jagged-intelligence",
            "https://www.chronicle.com/topic/artificial-intelligence",
        ],
    },
    {
        "name": "EDUCAUSE Review",
        "sector": "Higher education",
        "type": "Web / Journal",
        "url": "https://er.educause.edu/topics/emerging-technologies/artificial-intelligence",
        "feeds": [
            "https://er.educause.edu/topics/emerging-technologies/artificial-intelligence",
            "https://er.educause.edu/articles",
        ],
    },
    {
        "name": "Inside Higher Ed — Artificial Intelligence",
        "sector": "Higher education",
        "type": "Web / RSS",
        "url": "https://www.insidehighered.com/tags/artificial-intelligence",
        "feeds": [
            "https://www.insidehighered.com/rss/feed/all",
            "https://www.insidehighered.com/tags/artificial-intelligence",
        ],
    },
    {
        "name": "Campus Technology",
        "sector": "Higher education",
        "type": "Web / RSS",
        "url": "https://campustechnology.com/articles/list/ai.aspx",
        "feeds": [
            "https://campustechnology.com/rss-feeds/news.aspx",
            "https://campustechnology.com/articles/list/ai.aspx",
        ],
    },
    {
        "name": "Jisc — Artificial Intelligence Community",
        "sector": "Higher education",
        "type": "Web / Community",
        "url": "https://www.jisc.ac.uk/national-centre-for-ai",
        "feeds": [
            "https://nationalcentreforai.jiscinvolve.org/wp/feed/",
            "https://www.jisc.ac.uk/national-centre-for-ai",
        ],
    },
    # Cross-sector (1)
    {
        "name": "One Useful Thing",
        "author": "Ethan Mollick",
        "sector": "Cross-sector",
        "type": "Substack / RSS",
        "url": "https://www.oneusefulthing.org/",
        "feeds": [
            "https://www.oneusefulthing.org/feed",
            "https://www.oneusefulthing.org/",
        ],
    },
]

SOURCE_CONFIG = {
    "Business and enterprise": [
        {"name": s["name"], "type": s["type"], "url": s["url"]}
        for s in SOURCES
        if s["sector"] == "Business and enterprise"
    ],
    "Higher education": [
        {"name": s["name"], "type": s["type"], "url": s["url"]}
        for s in SOURCES
        if s["sector"] == "Higher education"
    ],
    "Cross-sector": [
        {
            "name": s["name"],
            "author": s.get("author", "Ethan Mollick"),
            "type": s["type"],
            "url": s["url"],
        }
        for s in SOURCES
        if s["sector"] == "Cross-sector"
    ],
}


def clean_html_text(raw_html: str, max_len: int = 800) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not raw_html:
        return ""
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", raw_html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]


def parse_rss_or_atom(xml_bytes: bytes, max_items: int = 5) -> list:
    """Parse RSS 2.0 or Atom XML feed into a list of article dicts."""
    items = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    # RSS 2.0 <item> elements
    for item in root.findall(".//item")[:max_items]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (
            item.findtext("description")
            or item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
            or ""
        )
        pub_date = (item.findtext("pubDate") or item.findtext("{http://purl.org/dc/elements/1.1/}date") or "").strip()
        if title:
            items.append(
                {
                    "title": clean_html_text(title, 200),
                    "url": link,
                    "summary": clean_html_text(desc, 600),
                    "published": pub_date,
                }
            )

    if items:
        return items

    # Atom <entry> elements
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//atom:entry", ns) or root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//entry")
    for entry in entries[:max_items]:
        title_el = entry.find("{http://www.w3.org/2005/Atom}title") if entry.find("title") is None else entry.find("title")
        title = (title_el.text if title_el is not None and title_el.text else "").strip()

        link = ""
        for link_el in entry.findall("{http://www.w3.org/2005/Atom}link") + entry.findall("link"):
            href = link_el.attrib.get("href", "").strip()
            rel = link_el.attrib.get("rel", "alternate")
            if href and rel in ("alternate", ""):
                link = href
                break
            elif href and not link:
                link = href

        summary_el = (
            entry.find("{http://www.w3.org/2005/Atom}summary")
            or entry.find("{http://www.w3.org/2005/Atom}content")
            or entry.find("summary")
            or entry.find("content")
        )
        summary = summary_el.text if summary_el is not None and summary_el.text else ""
        updated_el = entry.find("{http://www.w3.org/2005/Atom}updated") or entry.find("updated") or entry.find("published")
        pub_date = (updated_el.text if updated_el is not None and updated_el.text else "").strip()

        if title:
            items.append(
                {
                    "title": clean_html_text(title, 200),
                    "url": link,
                    "summary": clean_html_text(summary, 600),
                    "published": pub_date,
                }
            )

    return items


def parse_html_headlines(raw_html: str, base_url: str, max_items: int = 5) -> list:
    """Fallback HTML parser that extracts top article headings and snippets from a web page."""
    items = []
    # Match <h1/h2/h3>...<a href="...">Title</a>...</h1/h2/h3> or <a href="...">...<h2/h3>Title</h2/h3>...</a>
    pattern = re.compile(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        re.S | re.I,
    )
    seen_titles = set()
    for match in pattern.finditer(raw_html):
        href, inner = match.group(1).strip(), match.group(2)
        title = clean_html_text(inner, 200)
        # Filter for meaningful article headlines
        if len(title) < 28 or len(title.split()) < 5:
            continue
        if title.lower() in seen_titles:
            continue
        if any(skip in href.lower() for skip in ("javascript:", "mailto:", "#", "/login", "/subscribe", "/account")):
            continue
        if href.startswith("/"):
            m = re.match(r"^(https?://[^/]+)", base_url)
            if m:
                href = m.group(1) + href
        seen_titles.add(title.lower())
        items.append(
            {
                "title": title,
                "url": href if href.startswith("http") else base_url,
                "summary": "",
                "published": "",
            }
        )
        if len(items) >= max_items:
            break

    # If no anchor headlines matched, extract plain text excerpt from page
    if not items:
        snippet = clean_html_text(raw_html, 1000)
        if snippet:
            items.append(
                {
                    "title": f"Latest updates from {base_url}",
                    "url": base_url,
                    "summary": snippet,
                    "published": "",
                }
            )
    return items


def fetch_source_items(source: dict, timeout: int = 12) -> list:
    """Fetch live RSS/Atom items or web headlines for a single source."""
    for feed_url in source.get("feeds", []) + [source["url"]]:
        try:
            req = urllib.request.Request(
                feed_url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html;q=0.9, */*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw_bytes = resp.read(500_000)
                content_type = (resp.headers.get("Content-Type") or "").lower()

            # Try XML/RSS/Atom first
            if b"<rss" in raw_bytes[:2000].lower() or b"<feed" in raw_bytes[:2000].lower() or "xml" in content_type:
                parsed = parse_rss_or_atom(raw_bytes)
                if parsed:
                    return parsed

            # Fallback to HTML headline extraction
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            parsed_html = parse_html_headlines(raw_text, source["url"])
            if parsed_html:
                return parsed_html
        except Exception as e:
            print(f"  [warn] {source['name']} ({feed_url}): {e}")
            continue

    return []


def fetch_all_sources() -> dict:
    """Fetch latest items across all 14 sources."""
    collected = {}
    print(f"Fetching live feeds across {len(SOURCES)} sources...")
    for src in SOURCES:
        items = fetch_source_items(src)
        collected[src["name"]] = {
            "source": src["name"],
            "sector": src["sector"],
            "type": src["type"],
            "default_url": src["url"],
            "items": items,
        }
        print(f"  - {src['name']}: {len(items)} item(s) fetched")
    return collected


def build_gemini_prompt(today_str: str, collected_feeds: dict) -> str:
    """Construct the structured prompt for Gemini to synthesize the daily pull."""
    feed_dump = json.dumps(collected_feeds, indent=2, ensure_ascii=False)
    return f"""You are an executive intelligence editor curating the Daily AI Intelligence Dashboard for {today_str}.
Below is the raw feed data fetched today across 14 tracked sources in three sectors:
- Business and enterprise (8 sources)
- Higher education (5 sources)
- Cross-sector (1 source: One Useful Thing by Ethan Mollick)

Your task:
1. Synthesize a high-level `headline` (1 concise, informative line) and `executiveSummary` (2-3 sentences connecting today's overarching enterprise, higher education, and cross-sector AI themes).
2. For EACH of the 14 sources, select the single most important, relevant AI story from its fetched items (or synthesize the source's latest AI focus if only general items were returned) and write:
   - `title`: Clear, specific story headline.
   - `url`: The direct article URL from the fetched items (or the source's `default_url` if no specific article URL was present).
   - `bullets`: Exactly 2 concise bullet points (1-2 sentences each) explaining what happened and why it matters for enterprise or higher education leaders.
   - `tags`: 3 to 4 short topical tags (without '#' prefix, e.g. ["EnterpriseAI", "Governance", "LLMs"]).
   - `readTime`: Estimated read time (e.g. "3 min").
   - `importance`: Either "High" (for the top 5-7 stories of the day) or "Medium".

Return strictly valid JSON matching this exact schema:
{{
  "date": "{today_str}",
  "headline": "...",
  "executiveSummary": "...",
  "metrics": {{
    "sourcesReported": 14,
    "totalStories": 14,
    "highImpactCount": 6,
    "primarySector": "..."
  }},
  "stories": [
    {{
      "id": "story-{today_str}-01",
      "source": "VentureBeat",
      "sector": "Business and enterprise",
      "title": "...",
      "url": "https://...",
      "accessType": "Web / RSS",
      "bullets": [
        "1-2 sentence takeaway bullet 1.",
        "1-2 sentence takeaway bullet 2."
      ],
      "tags": ["Tag1", "Tag2", "Tag3"],
      "readTime": "3 min",
      "importance": "High"
    }}
  ]
}}

Ensure all 14 sources appear in `stories` in their exact sector ("Business and enterprise", "Higher education", or "Cross-sector").

RAW FETCHED FEEDS:
{feed_dump}
"""


def call_gemini_api(prompt: str, api_key: str, model: str = GEMINI_MODEL) -> dict:
    """Call the Gemini generateContent REST API and return parsed JSON."""
    models_to_try = [model]
    for fallback_model in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"):
        if fallback_model not in models_to_try:
            models_to_try.append(fallback_model)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }
    body_bytes = json.dumps(payload).encode("utf-8")

    last_error = None
    for candidate_model in models_to_try:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{candidate_model}:generateContent?key={api_key}"
        )
        req = urllib.request.Request(
            endpoint,
            data=body_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            print(f"Calling Gemini API ({candidate_model})...")
            with urllib.request.urlopen(req, timeout=90) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            text_out = (
                resp_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            if not text_out:
                raise ValueError("Empty response text from Gemini API")
            # Strip optional markdown code fences if present
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text_out.strip())
            return json.loads(cleaned)
        except Exception as e:
            last_error = e
            print(f"  [warn] Gemini API call with {candidate_model} failed: {e}")

    raise RuntimeError(f"All Gemini API model attempts failed. Last error: {last_error}")


def build_fallback_pull_from_feeds(today_str: str, collected_feeds: dict, existing_pull: dict = None) -> dict:
    """
    If GEMINI_API_KEY is not set or the API is unreachable, construct a valid pull
    using fetched RSS items (or preserve the existing pull if offline).
    """
    total_fetched = sum(len(v.get("items", [])) for v in collected_feeds.values())
    if total_fetched == 0 and existing_pull:
        print("No live items fetched (offline mode) and no GEMINI_API_KEY set; keeping existing pull data.")
        return existing_pull

    stories = []
    for idx, src in enumerate(SOURCES, start=1):
        info = collected_feeds.get(src["name"], {})
        items = info.get("items", [])
        if items:
            top = items[0]
            title = top.get("title") or f"Latest AI Briefing from {src['name']}"
            url = top.get("url") or src["url"]
            summary = top.get("summary") or f"Latest updates from {src['name']} in {src['sector']}."
            bullets = [summary[:260] + ("..." if len(summary) > 260 else "")]
            if len(items) > 1 and items[1].get("title"):
                bullets.append(f"Also trending: {items[1]['title']}.")
            else:
                bullets.append(f"Source coverage tracked via {src['type']} ({src['sector']}).")
        elif existing_pull:
            # Fall back to matching source story in existing_pull
            prev = next((s for s in existing_pull.get("stories", []) if s.get("source") == src["name"]), None)
            if prev:
                stories.append(prev)
                continue
            title = f"Latest AI Updates from {src['name']}"
            url = src["url"]
            bullets = [f"Visit {src['name']} for current coverage across {src['sector']}."]
        else:
            title = f"Latest AI Updates from {src['name']}"
            url = src["url"]
            bullets = [f"Visit {src['name']} for current coverage across {src['sector']}."]

        stories.append(
            {
                "id": f"story-{today_str}-{idx:02d}",
                "source": src["name"],
                "sector": src["sector"],
                "title": title,
                "url": url,
                "accessType": src["type"],
                "bullets": bullets,
                "tags": ["AI", src["sector"].split()[0]],
                "readTime": "3 min",
                "importance": "High" if idx <= 6 else "Medium",
            }
        )

    return {
        "date": today_str,
        "headline": f"Daily AI Intelligence Briefing Across 14 Enterprise & Higher Ed Sources ({today_str})",
        "executiveSummary": (
            "Automated RSS/web feed pull across Business & Enterprise, Higher Education, and Cross-Sector sources. "
            "Set GEMINI_API_KEY in your environment or GitHub Secrets to enable AI-synthesized executive takeaways."
        ),
        "metrics": {
            "sourcesReported": len(stories),
            "totalStories": len(stories),
            "highImpactCount": sum(1 for s in stories if s.get("importance") == "High"),
            "primarySector": "Enterprise & Higher Education AI",
        },
        "stories": stories,
    }


def refresh():
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Load existing dashboard_data.json if present
    old_current = None
    old_archive = []
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            old_current = old_data.get("currentPull")
            old_archive = old_data.get("archive", [])
        except Exception as e:
            print(f"Notice reading existing data: {e}")

    # Step 1: Fetch live RSS/web feeds across all 14 sources
    collected_feeds = fetch_all_sources()

    # Step 2: Synthesize daily pull via Gemini API if GEMINI_API_KEY is available
    new_pull = None
    if GEMINI_API_KEY:
        try:
            prompt = build_gemini_prompt(today_str, collected_feeds)
            new_pull = call_gemini_api(prompt, GEMINI_API_KEY, GEMINI_MODEL)
            new_pull["date"] = today_str
            print(f"Successfully synthesized {len(new_pull.get('stories', []))} stories via Gemini API.")
        except Exception as e:
            print(f"[error] Gemini synthesis failed, falling back to direct feed items: {e}")

    if not new_pull:
        new_pull = build_fallback_pull_from_feeds(today_str, collected_feeds, existing_pull=old_current)

    # Step 3: Roll over the 5-day archive when the date advances
    if old_current and old_current.get("date") != new_pull.get("date"):
        archive_pulls = [old_current] + [
            p for p in old_archive if p.get("date") != old_current.get("date")
        ]
    else:
        archive_pulls = old_archive

    archive_pulls = archive_pulls[:5]

    data = {
        "metadata": {
            "title": "Daily AI Intelligence Dashboard",
            "subtitle": "14-Source Curated Executive Briefing across Enterprise & Higher Education",
            "lastUpdated": datetime.now(timezone.utc).astimezone().isoformat(),
            "targetRefreshTime": "Daily at 07:00 AM EDT",
            "sourcesTracked": 14,
            "archiveDaysRetained": 5,
            "colorPalette": {
                "crimsonPrimary": "#990000",
                "creamPrimary": "#F8EFE2",
                "lightCrimson": "#F41C40",
                "darkCrimson": "#6D0808",
                "darkCream": "#F5E3CC",
                "lightGrey": "#EEEEF0",
                "darkGrey": "#B9C1C6",
                "iuBlack": "#072332",
            },
        },
        "sourceDirectory": SOURCE_CONFIG,
        "currentPull": new_pull,
        "archive": archive_pulls,
    }

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {DATA_PATH} with latest pull: {data['currentPull']['date']}")
    print(f"Archive retained ({len(data['archive'])}): {[p['date'] for p in data['archive']]}")

    # Step 4: Rebuild standalone index.html
    if os.path.exists(BUILD_SCRIPT):
        subprocess.run([sys.executable, BUILD_SCRIPT], check=True)
    else:
        print("Build script not found, skipped HTML compilation.")


if __name__ == "__main__":
    refresh()
