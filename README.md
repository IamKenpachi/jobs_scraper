# 🚀 UK Jobs Scraper CLI

A powerful, modular, and highly extensible Command Line Interface (CLI) tool for scraping job listings across **6 major UK job boards**. 

Whether you're looking for "Data Analyst" roles or "Software Engineering" positions, this tool intelligently routes your request to either lightning-fast REST APIs or stealthy Headless Browsers to bypass bot protections.

All data is automatically formatted into clean CSVs and saved to a timestamped `output/` directory, making it perfect for building historical datasets for Data Analysis!

---

## 🛠 Supported Platforms

| Platform | Technology Used | Description | Requires API Key? |
| :--- | :--- | :--- | :--- |
| **Reed.co.uk** | REST API | Lightning fast API integration. Highly reliable. | Yes |
| **Jooble** | REST API | Direct backend API bypasses aggressive Cloudflare protections. | Yes |
| **Milkround** | Playwright Stealth | Headless browser automation. Perfect for graduate roles. | No |
| **CWJobs** | Playwright Stealth | Tech-specific job board powered by the StepStone network. | No |
| **Totaljobs** | Playwright Stealth | The flagship StepStone board. Very high volume of jobs. | No |
| **Targetjobs** | Playwright Stealth | Complex React rendering handled via headless browser. | No |

---

## 💻 Installation & Setup

1. **Clone the repository and enter the directory.**
2. **Install the required dependencies:**
   ```bash
   pip install pandas beautifulsoup4 playwright playwright-stealth requests
   ```
3. **Install Playwright Browsers:**
   ```bash
   playwright install firefox
   ```
4. **(Optional) Add your API Keys:**
   - For **Reed**, open `reed_scraper.py` and replace the placeholder with your free key from the [Reed Developer Portal](https://www.reed.co.uk/developers).
   - For **Jooble**, open `jooble_scraper.py` and replace the placeholder with your free key from the [Jooble API Portal](https://jooble.org/api/about).

---

## 📖 How to Use the CLI

The scraper is entirely controlled via `main.py`. It accepts three main flags to customize your search.

### The Flags Explained

*   `--site` **(Required)**
    *   **What it does:** Tells the CLI which scraper module to trigger.
    *   **Accepted values:** `targetjobs`, `jooble`, `reed`, `milkround`, `cwjobs`, `totaljobs`
*   `--query` *(Optional)*
    *   **What it does:** The job title or keyword you are searching for. If your search is multiple words, wrap it in quotation marks!
    *   **Default value:** `"graduate data analyst"`
*   `--headed` *(Optional)*
    *   **What it does:** Forces the Playwright browser to open visibly on your screen instead of running invisibly in the background.
    *   **When to use it:** Use this flag if the scraper is failing to return jobs because it is being blocked by a CAPTCHA (very common on high-traffic sites like **Totaljobs**). This allows you to manually click the CAPTCHA like a real human, after which the scraper will automatically resume its job!

---

## 🎯 Examples

### Example 1: Basic Scrape (Background/Headless)
Scrape Milkround for Data Analyst jobs. The browser will remain completely invisible.
```bash
python main.py --site milkround --query "data analyst"
```

### Example 2: API Scrape
Scrape Reed using the backend API. Because this doesn't use a browser, it is extremely fast and ignores the `--headed` flag entirely.
```bash
python main.py --site reed --query "machine learning engineer"
```

### Example 3: Bypassing CAPTCHAs (Headed Mode)
Totaljobs is notorious for aggressive Cloudflare protections. Run this command to open the browser visibly so you can manually click "Verify you are human".
```bash
python main.py --site totaljobs --query "junior data scientist" --headed
```

---

## 📂 Output Structure

To prevent accidental data loss, the CLI automatically generates an `output/` directory and saves your data with a timestamp.

```text
📁 jobs_scraper/
├── 📁 output/
│   ├── 📄 cwjobs_2024-05-20_14-30-00.csv
│   ├── 📄 reed_2024-05-20_14-35-12.csv
│   └── 📄 milkround_2024-05-20_14-40-05.csv
├── 📄 main.py
├── 📄 cwjobs_scraper.py
└── ...
```

Each CSV contains clean, standardized columns ready for Pandas analysis:
`Job Title`, `Company`, `Location`, `Salary`, `Deadline`, `URL`, `Description`

---
*Happy Scraping! 🕷️*
