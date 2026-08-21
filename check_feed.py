"""Captura screenshot do feed logado."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1366, "height": 800})
        page = await ctx.new_page()
        # Login via API
        resp = await page.request.post("http://127.0.0.1:5000/api/auth/login", data={
            "username": "pablo",
            "password": "demo1234",
        })
        print(f"Login: {resp.status}")
        await page.goto("http://127.0.0.1:5000/feed", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path="feed_check.png", full_page=False)
        print("Screenshot salvo em feed_check.png")
        await browser.close()


asyncio.run(main())
