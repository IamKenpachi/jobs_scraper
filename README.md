# 🚀 UK Jobs Scraper CLI

A powerful, modular, and highly extensible Command Line Interface (CLI) tool for scraping job listings across **5 major UK job boards**. 

Whether you're looking for "Data Analyst" roles or "Software Engineering" positions, this tool intelligently routes your request to either lightning-fast REST APIs or stealthy Headless Browsers to bypass bot protections.

All data is automatically formatted and saved to a unified **SQLite Database** (`output/jobs.db`), performing bulk upserts to prevent duplicate entries and tracking exactly when jobs were scraped for powerful time-series Data Analysis!

---

## 🛠 Supported Platforms

| Platform | Technology Used | Description | Requires API Key? |
| :--- | :--- | :--- | :--- |
| **Reed.co.uk** | REST API | Lightning fast API integration. Highly reliable. | Yes |
| **Jooble** | REST API | Direct backend API bypasses aggressive Cloudflare protections. | Yes |
| **Milkround** | Playwright Stealth | Headless browser automation. Perfect for graduate roles. | No |
| **CWJobs** | Playwright Stealth | Tech-specific job board powered by the StepStone network. | No |
| **Targetjobs** | Playwright Stealth | Complex React rendering handled via headless browser. | No |

---

## 💻 Installation & Setup

1. **Clone the repository and enter the directory.**
2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Playwright Browsers:**
   ```bash
   playwright install chromium firefox
   ```
4. **(Optional) Add your API Keys:**
   Create a `.env` file in the root directory and add your keys securely:
   ```env
   REED_API_KEY="your_reed_api_key_here"
   JOOBLE_API_KEY="your_jooble_api_key_here"
   ```
   - For **Reed**, get a free key from the [Reed Developer Portal](https://www.reed.co.uk/developers).
   - For **Jooble**, get a free key from the [Jooble API Portal](https://jooble.org/api/about).

---

## 📖 How to Use the CLI

The scraper is entirely controlled via `main.py`. It accepts three main flags to customize your search.

### The Flags Explained

*   `--site` **(Required)**
    *   **What it does:** Tells the CLI which scraper module to trigger.
    *   **Accepted values:** `targetjobs`, `jooble`, `reed`, `milkround`, `cwjobs`, `all`
    *   *Tip:* Using `all` runs every scraper **concurrently** using `asyncio` for maximum speed!
*   `--query` *(Optional)*
    *   **What it does:** The job title or keyword you are searching for. If your search is multiple words, wrap it in quotation marks!
    *   **Default value:** `"graduate data analyst"`
*   `--headed` *(Optional)*
    *   **What it does:** Forces the Playwright browser to open visibly on your screen instead of running invisibly in the background.
    *   **When to use it:** Use this flag if the scraper is failing to return jobs because it is being blocked by a CAPTCHA. This allows you to manually click the CAPTCHA like a real human.

---

## 🎯 Examples

### Example 1: Concurrent Scrape (The fastest way)
Scrape all 5 platforms at exactly the same time. The CLI will report a summary of successes/failures at the end.
```bash
python main.py --site all --query "data analyst"
```

### Example 2: Basic Scrape (Background/Headless)
Scrape Milkround for Data Analyst jobs. The browser will remain completely invisible.
```bash
python main.py --site milkround --query "data analyst"
```

### Example 3: API Scrape
Scrape Reed using the backend API. Because this doesn't use a browser, it is extremely fast and ignores the `--headed` flag entirely.
```bash
python main.py --site reed --query "machine learning engineer"
```

---

## 📂 Output Structure

All scrapers automatically funnel their data into a single, structured SQLite Database:

```text
📁 jobs_scraper/
├── 📁 output/
│   └── 🗄️ jobs.db (SQLite Database)
├── 📄 main.py
├── 📄 database.py
├── 📄 models.py
└── ...
```

The database tracks the following columns, perfect for loading directly into Pandas, Tableau, or PowerBI:
`url`, `title`, `company`, `location`, `salary`, `deadline`, `description`, `source`, `scraped_at`

---
*Happy Scraping! 🕷️*
