import os
import asyncio
import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from pyvirtualdisplay import Display
from invisible_playwright.async_api import InvisiblePlaywright

MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_REQUESTS", 7))

# Глобальные переменные для переиспользования
display = None
browser_instance = None
semaphore = asyncio.Semaphore(MAX_CONCURRENT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет стартом и остановкой приложения (Вместо старых @app.on_event)."""
    global display, browser_instance
    # 1. Запускаем один виртуальный дисплей на всё время работы приложения
    display = Display(visible=False, size=(1920, 1080))
    display.start()

    # 2. Инициализируем один глобальный экземпляр браузера
    playwright_context = InvisiblePlaywright()
    browser_instance = await playwright_context.__aenter__()

    yield  # Здесь приложение принимает запросы

    # 3. Чистим ресурсы при выключении сервера
    await playwright_context.__aexit__(None, None, None)
    if display:
        display.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/getContent")
async def get_content(
        url: str,
        width: int = Query(1280, ge=100, le=3840),
        height: int = Query(1024, ge=100, le=2160)
):
    async with semaphore:
        page = None
        try:
            # Переиспользуем браузер, создавая только новую вкладку (страницу)
            page = await browser_instance.new_page(viewport={"width": width, "height": height})
            await page.goto(url, wait_until="domcontentloaded")
            content = await page.content()

            return {"result": True, "content": content}
        except Exception as e:
            return {"result": False, "message": str(e)}
        finally:
            if page:
                await page.close()


@app.get("/screenshot")
async def get_screenshot(
        url: str,
        width: int = Query(1280, ge=100, le=3840),
        height: int = Query(1024, ge=100, le=2160)
):
    async with semaphore:
        page = None
        try:
            page = await browser_instance.new_page(viewport={"width": width, "height": height})
            await page.goto(url, wait_until="networkidle")

            screenshot_bytes = await page.screenshot(type="png", full_page=False)
            img_str = base64.b64encode(screenshot_bytes).decode("utf-8")

            return {
                "result": True,
                "content": f"data:image/png;base64,{img_str}"
            }
        except Exception as e:
            return {"result": False, "message": str(e)}
        finally:
            if page:
                await page.close()
