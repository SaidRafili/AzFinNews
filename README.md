# 📰 AzFinNews — Actual Financial News of Azerbaijan

**AzFinNews** is a Python-based terminal application that provides **real-time updates** from major Azerbaijani economy news sources.  
It scrapes, displays, and persists live financial news from **APA.az** (and can be extended to others like Trend, Report, or Oxu).  

The interface is powered by [Rich](https://github.com/Textualize/rich) — giving you a modern, colorful command-line experience.

---

## 🚀 Features

✅ Persistent scraping of [APA.az](https://apa.az/economy) economy section  
✅ Automatically refreshes every **30 seconds**  
✅ Command-line interface with **pagination** (`turn <n>`)  
✅ Safe storage of visited links in `seen_links.json`  
✅ Rich, colorful UI with ASCII header  
✅ “Home” screen & real-time command navigation  
✅ Graceful shutdown and session resume  
✅ Supports both Windows PowerShell and macOS/Linux terminals  

---

## 💻 Snapshot

<img width="1890" height="902" alt="Ekran şəkli 2025-11-10 134933" src="https://github.com/user-attachments/assets/0fbc0d83-f6df-4962-8742-a65d2de124b9" />

---

## 🧩 Requirements

Python **3.9+**

Install dependencies via:

```bash
pip install aiohttp beautifulsoup4 rich
```

---

## 💻 Usage

Clone the repository and navigate into it:

```bash
git clone https://github.com/SaidRafili/azfinnews.git
cd azfinnews
```

Run the app:

```bash
python finnews.py
```

---

## 🏁 Commands

| Command | Description |
|----------|--------------|
| `list` | Show latest financial news (same as `turn 1`) |
| `turn <page>` | View older pages from APA.az (e.g. `turn 3`) |
| `read <n>` | Read full article text by number |
| `home` | Return to the welcome screen |
| `quit` | Exit the application safely |

> 💡 Tip: Just press **Enter** on startup to immediately load the latest news.

---

## 📂 Data Persistence

All fetched article links are stored in `seen_links.json` automatically.
- Prevents re-downloading the same articles.
- Keeps records for **7 days** by default (`KEEP_DAYS` can be changed in code).
- Automatically cleans old entries.

Example structure:

```json
{
  "https://apa.az/economy/some-news": {
    "title": "Economic growth in Azerbaijan rises by 5%",
    "timestamp": "2025-11-10T10:45:22.142833"
  }
}
```

---

## 🔄 Auto Refresh

Every **30 seconds**, AzFinNews checks for new economy articles.

When new ones appear, they are:
- Displayed as `[green]+ New: <title>[/green]` in your terminal.
- Added to the in-memory feed and persisted to disk.

---

## ⚙️ Configuration

Inside the source code (`finnews.py`), you can adjust:

| Variable | Description | Default |
|-----------|-------------|----------|
| `BASE_URL` | Main site to scrape | `https://apa.az/economy` |
| `SCRAPE_INTERVAL` | Refresh interval in seconds | `30` |
| `KEEP_DAYS` | Retention for stored links | `7` |
| `MAX_PAGES` | Max pages per scrape | `10` |
| `LOG_FILE` | File where seen links are stored | `seen_links.json` |

---

## 🧠 How It Works

1. Loads previously seen links from `seen_links.json`.
2. Displays a **Welcome Screen**.
3. Fetches article listings and parses:
   - Title
   - Link
   - Date & Time
   - Source
4. Presents them as a **Rich Table**.
5. Periodically refreshes and updates the feed automatically.

---

## 🧾 Example Output

```
📰  AzFinNews — Page 1 — 2025-11-10 14:23:07
───────────────────────────────────────────────────────────────────────────────
 No.  Title                                                   Time & Date      Source
────  ───────────────────────────────────────────────────────  ───────────────  ───────
  1   Dünya bazarlarında neftin qiyməti artıb                 09:40 13 Oct 2025  APA.az
  2   Azərbaycan nefti ucuzlaşıb                              10:55 11 Oct 2025  APA.az
  3   Zəngəzur dəhlizi bölgədə çevik nəqliyyat...             17:05 10 Oct 2025  APA.az
───────────────────────────────────────────────────────────────────────────────
Commands: list | read <n> | turn <page> | home | quit
```

---

## 🧰 Troubleshooting

| Issue | Solution |
|--------|-----------|
| **No news displayed** | Ensure you have internet access. Try deleting `seen_links.json` and restart. |
| **`SyntaxError: name 'articles' is assigned to before global declaration`** | Make sure all global variables (`articles`, `seen`) are defined before functions. |
| **Weird characters in terminal** | Use a Unicode-compatible terminal (Windows Terminal, iTerm2, etc.) |
| **Old data showing up** | Delete `seen_links.json` to reset history. |

---

## 🧩 Extending to More Sources

Want to add **Oxu.az**, **Trend.az**, or **Report.az**?

1. Write a new parser function similar to `parse_listing()`  
2. Add it to the scraper loop  
3. Return unified dicts:
   ```python
   {"title": title, "link": link, "date": date_text, "source": "Oxu.az"}
   ```
4. Append to the global `articles` list before saving.

---

## 🤝 Contributing

Pull requests and bug reports are welcome!  
Please follow these steps:

1. Fork the repository  
2. Create a new branch (`feature/add-trend-source`)  
3. Commit and push changes  
4. Open a Pull Request

---

## 🧾 License

This project is released under the **Creative Commons Zero v1.0 Universal**.  
You are free to use, modify, and distribute it.

---

## ✨ Author

**AzFinNews**  
Developed by Said Rafili
