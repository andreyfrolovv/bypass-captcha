import os
import asyncio
import base64
from fastapi import FastAPI
from playwright.async_api import async_playwright
from io import BytesIO

# Читаем лимит из ENV. Если переменная не задана, по умолчанию будет 5.
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_REQUESTS", 7))

app = FastAPI()

semaphore = asyncio.Semaphore(MAX_CONCURRENT)

@app.get("/getContent")
async def getContent(url: str, width: int = 1280, height: int = 1024):
    async with semaphore:
        content = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": width, "height": height})
                page = await context.new_page()

                await page.goto(url)
                content = await page.content()
                await browser.close()

        except Exception as e:
            return {
                "result": False,
                "message": str(e)
            }

        return {
            "result": True,
            "content": content,
        }


@app.get("/screenshot")
async def getScreenshot(url: str, width: int = 1280, height: int = 1024):
    async with semaphore:
        img_str = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": width, "height": height})
                page = await context.new_page()
                await page.goto(url)

                screenshot_bytes = await page.screenshot(type="png")
                img_str = base64.b64encode(screenshot_bytes).decode("utf-8")

                await browser.close()

        except Exception as e:
            return {
                "result": False,
                "message": str(e)
            }

        return {
            "result": True,
            "content": 'data:image/png;base64,' + img_str,
        }