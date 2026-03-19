"""
Scrape all DSIP (DoD SBIR/STTR Innovation Portal) topics with descriptions and Q&A.
Uses Playwright headless browser to render the JavaScript-heavy Angular app.

Usage:
    python scrape_dsip.py [--output FILE]
"""
import json
import re
import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


DSIP_URL = "https://www.dodsbirsttr.mil/topics-app/"
COMPONENTS = [
    "ARMY", "NAVY", "USAF", "CBD", "DARPA", "DHA", "MDA",
    "SOCOM", "OSD", "DTRA", "NGA", "DLA", "DCSA",
]


def parse_topics_from_text(text):
    """Parse topic records from page inner text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    topics = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match topic ID patterns
        if (re.match(r"^[A-Z]{1,10}\d{2,4}[-]?[A-Z]?\d{0,4}[-]?\d*$", line)
                or re.match(r"^HR\d+SB", line)
                or re.match(r"^SF\d+", line)):
            topic_id = line
            status = title = open_date = close_date = ""
            release = solicitation = component = qa = ""
            j = i + 1

            if j < len(lines) and lines[j] in ("Pre-Release", "Open", "Closed"):
                status = lines[j]; j += 1

            title_parts = []
            while j < len(lines) and not re.match(r"^\d{2}/\d{2}/\d{4}$", lines[j]):
                title_parts.append(lines[j]); j += 1
            title = " ".join(title_parts)

            if j < len(lines) and re.match(r"^\d{2}/\d{2}/\d{4}$", lines[j]):
                open_date = lines[j]; j += 1
            if j < len(lines) and re.match(r"^\d{2}/\d{2}/\d{4}$", lines[j]):
                close_date = lines[j]; j += 1
            if j < len(lines) and re.match(r"^\d+$", lines[j]):
                release = lines[j]; j += 1
            if j < len(lines) and ("DoD" in lines[j] or "DoW" in lines[j]):
                solicitation = lines[j]; j += 1
            if j < len(lines) and lines[j] in COMPONENTS:
                component = lines[j]; j += 1
            if j < len(lines) and re.match(r"^\d+$", lines[j]):
                qa = lines[j]; j += 1

            if title:
                topics.append({
                    "topic_id": topic_id, "status": status, "title": title,
                    "open_date": open_date, "close_date": close_date,
                    "release": release, "solicitation": solicitation,
                    "component": component, "qa_count": qa,
                })
            i = j
        else:
            i += 1
    return topics


def scrape_all_topics(output_path=None):
    """Scrape all topics from DSIP portal."""
    if output_path is None:
        output_path = Path(__file__).parent.parent / ".sbir" / "dsip_topics_all.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Loading DSIP topics portal...", file=sys.stderr)
        page.goto(DSIP_URL, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(8000)

        all_topics = []
        seen_ids = set()
        page_num = 0
        max_pages = 10

        while page_num < max_pages:
            # Scroll to ensure content is loaded
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500)

            body_text = page.inner_text("body")
            topics = parse_topics_from_text(body_text)
            new_count = 0
            for t in topics:
                if t["topic_id"] not in seen_ids:
                    seen_ids.add(t["topic_id"])
                    all_topics.append(t)
                    new_count += 1

            print(f"Page {page_num}: parsed {len(topics)} topics, {new_count} new (total: {len(all_topics)})", file=sys.stderr)

            if new_count == 0 and page_num > 0:
                break

            # Navigate to next page using PrimeNG paginator
            next_clicked = False
            # Try Angular Material / PrimeNG next button
            for selector in [
                "button.p-paginator-next:not(.p-disabled)",
                "[class*='paginator-next']:not([class*='disabled'])",
                "button[aria-label='Next Page']",
                ".p-paginator button:last-child:not(.p-disabled)",
            ]:
                btn = page.query_selector(selector)
                if btn:
                    try:
                        btn.click()
                        page.wait_for_timeout(3000)
                        next_clicked = True
                        break
                    except Exception:
                        pass

            if not next_clicked:
                # Try finding page number buttons and clicking next number
                page_btns = page.query_selector_all(".p-paginator-page, [class*='paginator'] [class*='page']")
                for btn in page_btns:
                    text = btn.inner_text().strip()
                    if text.isdigit() and int(text) == page_num + 2:
                        btn.click()
                        page.wait_for_timeout(3000)
                        next_clicked = True
                        break

            if not next_clicked:
                # Last resort: try keyboard navigation or direct JS manipulation
                # Check if there's a paginator with page links
                paginator_html = page.evaluate("""
                    () => {
                        const el = document.querySelector('[class*="paginator"]');
                        return el ? el.innerHTML : 'NO PAGINATOR';
                    }
                """)
                print(f"Paginator HTML: {paginator_html[:500]}", file=sys.stderr)
                break

            page_num += 1

        print(f"\nTotal unique topics scraped: {len(all_topics)}", file=sys.stderr)

        # Fetch descriptions by expanding each topic row
        print("\nExpanding topics for descriptions...", file=sys.stderr)
        page.goto(DSIP_URL, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(8000)

        for idx, topic in enumerate(all_topics):
            tid = topic["topic_id"]
            try:
                # Find the chevron/expand button near the topic ID
                # Use JavaScript to find and click it
                expanded = page.evaluate(f"""
                    () => {{
                        const els = document.querySelectorAll('*');
                        for (const el of els) {{
                            if (el.textContent.trim() === '{tid}' && el.tagName === 'P') {{
                                // Walk up to find the row, then find the toggler
                                let row = el.closest('[class*="row"], tr, [pRowToggler]');
                                if (!row) {{
                                    let p = el.parentElement;
                                    for (let i = 0; i < 8; i++) {{
                                        if (p) {{ row = p; p = p.parentElement; }}
                                    }}
                                }}
                                if (row) {{
                                    const toggler = row.querySelector('[pRowToggler], button, [class*="toggler"], [class*="chevron"]');
                                    if (toggler) {{
                                        toggler.click();
                                        return true;
                                    }}
                                }}
                            }}
                        }}
                        return false;
                    }}
                """)
                if expanded:
                    page.wait_for_timeout(2000)
                    body = page.inner_text("body")
                    # Extract description
                    tid_pos = body.find(tid)
                    if tid_pos >= 0:
                        section = body[tid_pos:tid_pos + 5000]
                        # Look for Description header
                        desc_match = re.search(
                            r"(?:Description|DESCRIPTION)[:\s]*\n?(.*?)(?=Phase [I1]|Anticipated|Keywords|References|TPOC|\Z)",
                            section, re.DOTALL | re.IGNORECASE
                        )
                        if desc_match:
                            topic["description"] = desc_match.group(1).strip()[:3000]
                            print(f"  [{idx+1}/{len(all_topics)}] {tid}: description OK ({len(topic['description'])} chars)", file=sys.stderr)
                        else:
                            # Just grab everything after the title until the next topic
                            topic["description"] = section[:2000]
                            print(f"  [{idx+1}/{len(all_topics)}] {tid}: captured section ({len(topic['description'])} chars)", file=sys.stderr)

                    # Click again to collapse
                    page.evaluate(f"""
                        () => {{
                            const els = document.querySelectorAll('*');
                            for (const el of els) {{
                                if (el.textContent.trim() === '{tid}' && el.tagName === 'P') {{
                                    let row = el.closest('[class*="row"], tr, [pRowToggler]');
                                    if (!row) {{
                                        let p = el.parentElement;
                                        for (let i = 0; i < 8; i++) {{
                                            if (p) {{ row = p; p = p.parentElement; }}
                                        }}
                                    }}
                                    if (row) {{
                                        const toggler = row.querySelector('[pRowToggler], button, [class*="toggler"], [class*="chevron"]');
                                        if (toggler) {{ toggler.click(); return true; }}
                                    }}
                                }}
                            }}
                            return false;
                        }}
                    """)
                    page.wait_for_timeout(500)
                else:
                    print(f"  [{idx+1}/{len(all_topics)}] {tid}: no expand button found", file=sys.stderr)
                    topic["description"] = None
            except Exception as e:
                print(f"  [{idx+1}/{len(all_topics)}] {tid}: error - {str(e)[:80]}", file=sys.stderr)
                topic["description"] = None

        # Take final screenshot
        page.screenshot(path=str(Path(output_path).parent / "dsip_final.png"), full_page=True)

        browser.close()

    # Save results
    output = {
        "scrape_date": "2026-03-18",
        "source": DSIP_URL,
        "total_topics": len(all_topics),
        "topics": all_topics,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str, ensure_ascii=False)

    print(f"\nSaved {len(all_topics)} topics to {output_path}", file=sys.stderr)

    # Print summary
    for t in all_topics:
        desc = "YES" if t.get("description") else "NO"
        print(f'{t["topic_id"]:15s} | {t["status"]:12s} | {t["open_date"]:10s}-{t["close_date"]:10s} | {t["component"]:6s} | Q&A:{t["qa_count"]:3s} | Desc:{desc:3s} | {t["title"][:55]}')

    return all_topics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape DSIP SBIR/STTR topics")
    parser.add_argument("--output", "-o", default=None, help="Output JSON file path")
    args = parser.parse_args()
    scrape_all_topics(args.output)
