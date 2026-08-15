import asyncio
from sherlock_project.stealth_browser import StealthBrowser

async def main():
    async with StealthBrowser() as browser:
        print("Fetching https://example.com...")
        status, html = await browser.get_html("https://example.com")
        print(f"Status: {status}")
        if html:
            print(f"HTML Preview: {html[:100]}")
        else:
            print("Failed to get HTML content.")

if __name__ == "__main__":
    asyncio.run(main())
