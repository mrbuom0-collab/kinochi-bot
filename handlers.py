import os
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from database import add_movie, get_movie
from dotenv import load_dotenv

load_dotenv()
router = Router()

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
except ValueError:
    ADMIN_ID = 0

CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003980224305")

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Kino ko'rish uchun menga kino raqamini yuboring."
    )

# Admin sends a video -> save it to DB
@router.message(F.video)
async def handle_video(message: Message):
    if message.from_user.id == ADMIN_ID:
        file_id = message.video.file_id
        caption = message.caption or ""
        movie_id = add_movie(file_id, caption)
        await message.reply(f"✅ Kino bazaga qo'shildi!\n\nKino raqami: <b>{movie_id}</b>")
    else:
        await message.answer("Siz kino qo'sha olmaysiz.")

# User sends a number -> fetch video from DB
@router.message(F.text)
async def handle_movie_code(message: Message):
    text = message.text.strip()
    if text.isdigit():
        if CHANNEL_ID and message.from_user.id != ADMIN_ID:
            try:
                member = await message.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
                if member.status.value in ["left", "kicked"]:
                    await message.answer("❌ Kinoni ko'rish uchun avval homiy kanalimizga a'zo bo'lishingiz kerak!\n\nIltimos, kanalga a'zo bo'lgach, raqamni qayta yuboring.")
                    return
            except Exception as e:
                print(f"Membership check error: {e}")
                await message.answer("⚠️ Xatolik! Bot majburiy a'zolik kanaliga admin qilinmagan. Iltimos, adminlar bilan bog'laning.")
                return

        movie_id = int(text)
        movie = get_movie(movie_id)
        if movie:
            file_id, caption = movie
            await message.answer_video(video=file_id, caption=caption)
        else:
            await message.answer("❌ Kechirasiz, bunday raqamli kino topilmadi.")
    else:
        await message.answer("Iltimos, faqat kino raqamini (sonlarni) yuboring.")
