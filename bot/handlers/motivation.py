from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import httpx
from config import API_BASE_URL

async def show_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        telegram_id = str(query.from_user.id)
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{API_BASE_URL}/motivation/", params={"telegram_id": telegram_id})
            print("[DEBUG] Статус кода:", r.status_code)
            print("[DEBUG] Тело ответа:", r.text)
            if r.status_code == 200:
                message = r.json().get("text", "Ты молодец. Продолжай в том же духе!")
            else:
                message = "Сегодня ты справляешься лучше, чем думаешь. Продолжай! ✨"
    except Exception:
        message = "Ты — сила! Даже если кажется, что нет. 💪"

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu::back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)
