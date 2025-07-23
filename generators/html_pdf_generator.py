import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def html_to_pdf_async(html_path: str, pdf_path: str):
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()

    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Open the HTML file using file:// URL
        await page.goto(f"file://{html_path}", wait_until="load")

        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},

        )
        # margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},

        await browser.close()
        print(f"✅ PDF saved to {pdf_path}")


def html_to_pdf(html_path: str, pdf_path: str):
    asyncio.run(html_to_pdf_async(html_path, pdf_path))
