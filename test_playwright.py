import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating...")
        await page.goto('https://targetjobs.co.uk/search/jobs?search=data', wait_until='networkidle')
        print("Extracting HTML...")
        html = await page.content()
        with open('rendered.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Done.")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
