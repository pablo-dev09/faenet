"""Captura um screenshot da tela de login para validar o blur."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1366, "height": 800})
        await page.goto("http://127.0.0.1:5000/login", wait_until="networkidle")
        await page.wait_for_timeout(800)
        # Coleta avisos do console
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        await page.screenshot(path="login_check.png", full_page=False)
        print("Screenshot salvo em login_check.png")
        # Coleta erros de JS
        errors = await page.evaluate("() => window.__jsErrors || []")
        print(f"Erros JS: {errors}")
        await browser.close()


asyncio.run(main())
