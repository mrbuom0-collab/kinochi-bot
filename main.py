import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from database import init_db
from handlers import router
from aiohttp import web

load_dotenv()

async def handle(request):
    return web.Response(text="Bot is running on Render!")

async def dummy_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Database
    init_db()
    
    # Check token
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        logging.error("Iltimos, .env faylida BOT_TOKEN ni o'rnating!")
        return

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.include_router(router)
    
    logging.info("Bot ishga tushdi...")
    await dummy_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
