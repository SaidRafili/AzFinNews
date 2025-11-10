# finnews_final_persistent_home.py
# AzFinNews — Actual Financial News of Azerbaijan
# ----------------------------------------------------
# ✅ Persistent APA.az economy scraper with:
#    - Pagination (?page=2, etc.) via "turn <n>"
#    - "list" = alias for "turn 1"
#    - "home" to return to welcome screen anytime
#    - Time/date extraction
#    - Filter out junk (USD, weather)
#    - Source column ("APA.az")
#    - Pretty Rich interface + ASCII header + Welcome screen
# ----------------------------------------------------

import asyncio
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

# ---------------- Config ----------------
BASE_URL = "https://apa.az/economy"
SCRAPE_INTERVAL = 30
LOG_FILE = "seen_links.json"
KEEP_DAYS = 7
MAX_PAGES = 10

console = Console()
articles = []
seen = {}
stop_event = asyncio.Event()


# ---------------- Persistence ----------------
def load_seen():
    """Load and clean old records."""
    if not os.path.exists(LOG_FILE):
        return {}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    cleaned = {}
    for link, info in data.items():
        try:
            ts = datetime.fromisoformat(info.get("timestamp"))
            if ts > cutoff:
                cleaned[link] = info
        except Exception:
            continue
    return cleaned


def save_seen():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(seen, f, indent=2, ensure_ascii=False)
    except Exception as e:
        console.print(f"[red]Error saving seen file: {e}[/red]")


# ---------------- Networking ----------------
async def fetch_html(session, url):
    try:
        async with session.get(url, timeout=25) as resp:
            return await resp.text()
    except Exception as e:
        console.print(f"[red]Fetch error for {url}: {e}[/red]")
        return ""


# ---------------- Parsers ----------------
def parse_listing(html, base_url):
    """Extract article title, link, time/date, and source from APA.az economy listing."""
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.select("a.item[href]")
    found = []

    for a in anchors:
        href = a.get("href")
        if not href:
            continue
        link = href if href.startswith("http") else urljoin(base_url, href)

        # ❌ Skip currency/weather junk
        if "rates" in link or "weather" in link:
            continue

        title_tag = a.select_one("h2.title")
        title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
        if not title or len(title) < 5:
            continue

        # Extract time/date
        date_div = a.select_one("div.date")
        time_text, date_text = "", ""
        if date_div:
            spans = date_div.select("span")
            if len(spans) >= 2:
                time_text, date_text = spans[0].get_text(strip=True), spans[1].get_text(strip=True)
            elif len(spans) == 1:
                date_text = spans[0].get_text(strip=True)

        full_date = f"{time_text} {date_text}".strip()

        # Clean trailing time/date in title
        if any(ch.isdigit() for ch in title[-6:]):
            title = title.rstrip("0123456789:.- ")

        found.append({"title": title, "link": link, "date": full_date, "source": "APA.az"})
    return found


def parse_article(html):
    """Extract full article text."""
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one(
        "body > main > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(2) > "
        "div > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(3) > div:nth-of-type(3)"
    )
    if not node:
        node = soup.select_one("div.texts.mb-site[itemprop='articleBody']")
    if not node:
        node = soup
    return node.get_text("\n\n", strip=True)


# ---------------- Pagination ----------------
async def crawl_page(session, page_num=1):
    url = BASE_URL if page_num == 1 else f"{BASE_URL}?page={page_num}"
    html = await fetch_html(session, url)
    if not html:
        return []
    return parse_listing(html, BASE_URL)


async def scrape_all_pages(session, limit=MAX_PAGES):
    collected = []
    for page in range(1, limit + 1):
        items = await crawl_page(session, page)
        if not items:
            break
        collected.extend(items)
    return collected


# ---------------- Scraper ----------------
async def scraper_loop():
    global articles, seen
    async with aiohttp.ClientSession() as session:
        while not stop_event.is_set():
            found = await scrape_all_pages(session)
            new_count = 0
            for item in found:
                link = item["link"]
                if link not in seen:
                    seen[link] = {
                        "title": item["title"],
                        "timestamp": datetime.now().isoformat(),
                    }
                    articles.append(item)
                    console.print(f"[green]+ New: {item['title']}[/green]")
                    new_count += 1
                else:
                    if not any(a["link"] == link for a in articles):
                        articles.append(item)

            if new_count:
                save_seen()
            else:
                console.print(f"[dim][{datetime.now().strftime('%H:%M:%S')}] No new articles.[/dim]")

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=SCRAPE_INTERVAL)
            except asyncio.TimeoutError:
                continue


# ---------------- UI ----------------
def render_header():
    art = r"""
       d8888           .d888 d8b                                                   
      d88888          d88P"  Y8P                                                   
     d88P888          888                                                          
    d88P 888 88888888 888888 888 88888b.  88888b.   .d88b.  888  888  888 .d8888b  
   d88P  888    d88P  888    888 888 "88b 888 "88b d8P  Y8b 888  888  888 88K      
  d88P   888   d88P   888    888 888  888 888  888 88888888 888  888  888 "Y8888b. 
 d8888888888  d88P    888    888 888  888 888  888 Y8b.     Y88b 888 d88P      X88 
d88P     888 88888888 888    888 888  888 888  888  "Y8888   "Y8888888P"   88888P'                                                                                                                                     
    """
    text = Text(art, style="bold cyan")
    subtitle = Text("Actual Financial News of Azerbaijan", style="bold yellow")
    console.print(Align.center(Panel.fit(Text.assemble(text, "\n", subtitle), border_style="bright_black")))


def render_table(page=1):
    t = Table(
        title=f"📰  AzFinNews — Page {page} — {datetime.now():%Y-%m-%d %H:%M:%S}",
        title_style="bold green",
        header_style="bold magenta",
        border_style="bright_black",
    )
    t.add_column("No.", justify="right", style="cyan", no_wrap=True)
    t.add_column("Title", style="bold yellow")
    t.add_column("Time & Date", justify="center", style="dim white")
    t.add_column("Source", justify="center", style="bright_blue")

    for i, art in enumerate(articles, start=1):
        t.add_row(str(i), art["title"], art.get("date", ""), art.get("source", "—"))

    console.clear()
    render_header()
    console.print(t)
    console.print("[dim]Commands: list | read <n> | turn <page> | home | quit[/dim]")


# ---------------- Welcome Screen ----------------
def render_welcome():
    console.clear()
    render_header()
    description = (
        "[bold green]Welcome to AzFinNews![/bold green]\n\n"
        "This tool gives you [yellow]live updates[/yellow] from the APA.az [cyan]Economy[/cyan] section.\n"
        "It continuously monitors and saves recent financial news articles.\n\n"
        "[bold cyan]Available Commands:[/bold cyan]\n"
        " • [yellow]list[/yellow] — Show the latest news (alias for turn 1)\n"
        " • [yellow]read <n>[/yellow] — Open and read the full article text by number\n"
        " • [yellow]turn <page>[/yellow] — Browse older pages of APA.az economy section\n"
        " • [yellow]home[/yellow] — Return to this welcome screen anytime\n"
        " • [yellow]quit[/yellow] — Exit the application safely\n\n"
        "[dim]Tip: The script auto-refreshes every 30 seconds for new articles.[/dim]\n"
    )
    console.print(Panel(description, title="📘  Getting Started", border_style="bright_black"))

    # Press Enter → behave like "turn 1"
    Prompt.ask("\n[bold green]Press Enter to load the latest financial news[/bold green]")


# ---------------- Interactive ----------------
async def interactive_loop():
    async with aiohttp.ClientSession() as session:
        current_page = 1
        render_welcome()
        
        
        while True:
            render_table(current_page)
            cmd = Prompt.ask("[bold green]Command[/bold green]").strip().lower()

            if cmd == "quit":
                console.print("[bold red]Exiting...[/bold red]")
                stop_event.set()
                break
            elif cmd == "home":
                render_welcome()
                continue
            elif cmd == "list":
                # alias for "turn 1"
                current_page = 1
                console.print("[yellow]Loading the latest news (page 1)...[/yellow]")
                items = await crawl_page(session, 1)
                if items:
                    global articles
                    articles = items
                continue
            elif cmd.startswith("turn "):
                parts = cmd.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    console.print("[red]Usage: turn <page_number>[/red]")
                    await asyncio.sleep(0.5)
                    continue
                current_page = int(parts[1])
                console.print(f"[yellow]Turning to page {current_page}...[/yellow]")
                items = await crawl_page(session, current_page)
                if not items:
                    console.print("[red]No articles found on that page.[/red]")
                else:
                    articles = items
                continue
            elif cmd.startswith("read "):
                parts = cmd.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    console.print("[red]Usage: read <n>[/red]")
                    await asyncio.sleep(0.5)
                    continue
                idx = int(parts[1]) - 1
                if idx < 0 or idx >= len(articles):
                    console.print("[red]Invalid index[/red]")
                    await asyncio.sleep(0.5)
                    continue
                art = articles[idx]
                html = await fetch_html(session, art["link"])
                text = parse_article(html)
                console.clear()
                render_header()
                header = f"{art['title']}\n{art['date']} | {art['source']}\n{art['link']}"
                console.print(
                    Panel(
                        text[:20000],
                        title=header,
                        title_align="left",
                        width=110,
                        border_style="bright_black",
                    )
                )
                Prompt.ask("[bold cyan]Press Enter to return[/bold cyan]")
            else:
                console.print("[yellow]Unknown command[/yellow]")
                await asyncio.sleep(0.5)


# ---------------- Entrypoint ----------------
async def main():
    global seen, articles
    seen = load_seen()

    if seen:
        console.print(f"[dim]Loaded {len(seen)} seen articles from previous sessions.[/dim]")
        sorted_seen = sorted(seen.items(), key=lambda kv: kv[1]["timestamp"])
        for link, info in sorted_seen:
            if "rates" not in link and "weather" not in link:
                articles.append({"title": info["title"], "link": link, "date": "", "source": "APA.az"})
    else:
        console.print("[dim]No previous articles found, waiting for new ones...[/dim]")

    scraper = asyncio.create_task(scraper_loop())
    await interactive_loop()
    await scraper


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        stop_event.set()
        console.print("\n[red]Stopped by user.[/red]")
