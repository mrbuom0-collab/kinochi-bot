import os
from aiogram import Router, F
import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_movie, get_movie, delete_movie, increment_views, add_user, get_stats, get_all_users
from dotenv import load_dotenv

load_dotenv()
router = Router()

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
except ValueError:
    ADMIN_ID = 0

CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003980224305")

class AdminStates(StatesGroup):
    broadcast = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✉️ Xabar yuborish")]
            ],
            resize_keyboard=True
        )
        await message.answer("👋 Assalomu alaykum, Admin!\n\nQuyidagi menyudan kerakli bo'limni tanlang:", reply_markup=markup)
    else:
        await message.answer(
            "👋 Assalomu alaykum!\n\n"
            "Kino ko'rish uchun menga kino raqamini yuboring."
        )

@router.message(F.text == "📊 Statistika")
async def btn_stat(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    users_count, movies_count = get_stats()
    text = f"📊 <b>Bot Statistikasi:</b>\n\n👥 Umumiy foydalanuvchilar: {users_count} ta\n🎬 Jami kinolar: {movies_count} ta"
    await message.answer(text)

@router.message(F.text == "✉️ Xabar yuborish")
async def btn_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("✉️ Xabaringizni yuboring. Barcha turdagi xabarlar qo'llab-quvvatlanadi.\n\nBekor qilish uchun /cancel ni bosing.")
    await state.set_state(AdminStates.broadcast)

@router.message(Command("cancel"), AdminStates.broadcast)
async def cmd_cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Xabar yuborish bekor qilindi.")

@router.message(AdminStates.broadcast)
async def handle_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    users = get_all_users()
    sent = 0
    await message.answer(f"⏳ Xabar yuborish boshlandi. Jami foydalanuvchilar: {len(users)} ta...")
    for user_id in users:
        try:
            await message.send_copy(chat_id=user_id)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"✅ Xabar yuborish yakunlandi!\n\nMuvaffaqiyatli yetib bordi: {sent} ta")

# Admin sends a video -> save it to DB
@router.message(F.video)
async def handle_video(message: Message):
    if message.from_user.id == ADMIN_ID:
        file_id = message.video.file_id
        caption = message.caption or ""
        file_name = message.video.file_name or "Noma'lum"
        movie_id = add_movie(file_id, caption, file_name)
        btn = InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_{movie_id}")
        markup = InlineKeyboardMarkup(inline_keyboard=[[btn]])
        
        file_name = message.video.file_name or "Noma'lum"
        reply_text = (
            f"🎬 Kino nomi: {file_name}\n"
            f"🔑 Kino kodi: <b>{movie_id}</b>\n"
            f"🎭 Janri: Boshqa\n"
            f"👁 Ko'rishlar soni: 0\n\n"
            f"📝 Tavsif: Avtomatik yuklangan kino"
        )
        await message.reply(reply_text, reply_markup=markup)
    else:
        await message.answer("Siz kino qo'sha olmaysiz.")

# User sends a number -> fetch video from DB
@router.message(F.text)
async def handle_movie_code(message: Message):
    add_user(message.from_user.id)
    text = message.text.strip()
    if text.isdigit():
        if CHANNEL_ID and message.from_user.id != ADMIN_ID:
            try:
                member = await message.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
                status = getattr(member.status, "value", member.status)
                if status in ["left", "kicked"]:
                    try:
                        chat = await message.bot.get_chat(CHANNEL_ID)
                        invite_link = chat.invite_link or await message.bot.export_chat_invite_link(CHANNEL_ID)
                        btn = InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=invite_link)
                        markup = InlineKeyboardMarkup(inline_keyboard=[[btn]])
                        await message.answer("❌ Kinoni ko'rish uchun avval homiy kanalimizga a'zo bo'lishingiz kerak!\n\nIltimos, kanalga a'zo bo'lgach, raqamni qayta yuboring.", reply_markup=markup)
                    except Exception as e:
                        print(f"Error generating link: {e}")
                        await message.answer("❌ Kinoni ko'rish uchun avval homiy kanalimizga a'zo bo'lishingiz kerak!\n\nIltimos, kanalga a'zo bo'lgach, raqamni qayta yuboring.")
                    return
            except Exception as e:
                print(f"Membership check error: {e}")
                await message.answer("⚠️ Xatolik! Bot majburiy a'zolik kanaliga admin qilinmagan. Iltimos, adminlar bilan bog'laning.")
                return

        movie_id = int(text)
        movie = get_movie(movie_id)
        if movie:
            file_id, caption, file_name, views = movie
            increment_views(movie_id)
            views += 1 # Update views for current display
            
            dynamic_caption = (
                f"🎬 Kino nomi: {file_name}\n"
                f"🔑 Kino kodi: <b>{movie_id}</b>\n"
                f"🎭 Janri: Boshqa\n"
                f"👁 Ko'rishlar soni: {views}\n\n"
                f"📝 Tavsif: Avtomatik yuklangan kino"
            )
            await message.answer_video(video=file_id, caption=dynamic_caption)
        else:
            await message.answer("❌ Kechirasiz, bunday raqamli kino topilmadi.")
    else:
        await message.answer("Iltimos, faqat kino raqamini (sonlarni) yuboring.")

@router.message(Command("delete"))
async def cmd_delete(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Iltimos, o'chirmoqchi bo'lgan kino raqamini kiriting. Masalan: /delete 12")
        return
        
    movie_id_str = args[1]
    if not movie_id_str.isdigit():
        await message.answer("Kino raqami faqat sonlardan iborat bo'lishi kerak.")
        return
        
    movie_id = int(movie_id_str)
    if delete_movie(movie_id):
        await message.answer(f"✅ {movie_id} - raqamli kino muvaffaqiyatli o'chirildi.")
    else:
        await message.answer(f"❌ {movie_id} - raqamli kino topilmadi.")

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stat")],
        [InlineKeyboardButton(text="✉️ Xabar yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close")]
    ])
    await message.answer("🛠 <b>Admin Panelga xush kelibsiz!</b>\n\nQuyidagi menyudan kerakli bo'limni tanlang:", reply_markup=markup)

@router.callback_query(F.data == "admin_stat")
async def cb_admin_stat(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    users_count, movies_count = get_stats()
    text = f"📊 <b>Bot Statistikasi:</b>\n\n👥 Umumiy foydalanuvchilar: {users_count} ta\n🎬 Jami kinolar: {movies_count} ta"
    await call.answer(text, show_alert=True)

@router.callback_query(F.data == "admin_close")
async def cb_admin_close(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    await call.message.delete()

@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await call.message.answer("✉️ Xabaringizni yuboring. Barcha turdagi xabarlar (rasm, video, matn) qo'llab-quvvatlanadi.\n\nBekor qilish uchun /cancel ni bosing.")
    await state.set_state(AdminStates.broadcast)
    await call.answer()


@router.callback_query(F.data.startswith("del_"))
async def cb_delete(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizda bu huquq yo'q!", show_alert=True)
        return
        
    movie_id = int(call.data.split("_")[1])
    if delete_movie(movie_id):
        await call.message.edit_text(f"✅ {movie_id} - raqamli kino o'chirildi.")
        await call.answer("O'chirildi")
    else:
        await call.answer("Kino allaqachon o'chirilgan yoki topilmadi.", show_alert=True)
