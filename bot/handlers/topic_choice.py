import httpx
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import API_BASE_URL

async def handle_topic_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, topic = query.data.split("::")
    telegram_id = str(update.effective_user.id)

    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{API_BASE_URL}/students/{telegram_id}",
            json={"interest_topics": topic}
        )
        r = await client.get(f"{API_BASE_URL}/students/{telegram_id}")
        student = r.json()

    text = (
        f"✅ Готово! Профиль сформирован.\n\n"
        f"👤 *{student['name']}*\n"
        f"📘 Тема: *{student.get('interest_topics') or 'не выбрана'}*\n"
        f"💬 Уровень: *{student.get('eng_level') or 'не указан'}*\n\n"
        f"Выбери, с чего начнём 👇"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Мои задания", callback_data="menu::assignments")],
        [InlineKeyboardButton("🎯 Сменить тему", callback_data="menu::change_topic")],
        [InlineKeyboardButton("👤 Профиль", callback_data="menu::profile")],
        [InlineKeyboardButton("🏆 Достижения", callback_data="menu::achievements")],
        [InlineKeyboardButton("💬 Мотивация", callback_data="menu::motivation")]
    ])

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
