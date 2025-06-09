import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import API_BASE_URL

API_URL = f"{API_BASE_URL}/achievements/"

async def assign_achievement(telegram_id: str, name: str):
    async with httpx.AsyncClient() as client:
        try:
            achievements = (await client.get(API_URL)).json()
            achievement = next((a for a in achievements if a["name"] == name), None)
            if achievement:
                r = await client.post(f"{API_URL}assign", params={
                    "telegram_id": telegram_id,
                    "achievement_id": achievement["id"]
                })
                print("[DEBUG] Статус кода:", r.status_code)
                print("[DEBUG] Тело ответа:", r.text)

                if r.status_code == 200:
                    try:
                        print("[DEBUG] Ответ JSON:", r.json())
                    except Exception as e:
                        print("[ERROR] Ответ не JSON:", e)
                else:
                    print(f"[ERROR] Сервер вернул ошибку {r.status_code}")
        except Exception as e:
            print(f"[ERROR] Не удалось присвоить достижение: {e}")


async def show_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}students/{telegram_id}/achievements", follow_redirects=True)
        print("[DEBUG] Статус кода:", r.status_code)
        print("[DEBUG] Тело ответа:", r.text)

        try:
            achievements = r.json()
        except Exception as e:
            print("[ERROR] Невозможно распарсить JSON:", e)
            achievements = []

    if not achievements:
        text = "У вас пока нет достижений."
    else:
        text = "Ваши достижения:\n\n" + "\n".join(
            f"{a['icon']} <b>{a['name']}</b>\n{a['description']}\n" for a in achievements
        )

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="menu::back")]]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

async def achievement_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, name = query.data.split("::")

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}")
        achievements = r.json()
        achievement = next((a for a in achievements if a["name"] == name), None)

    if achievement:
        await query.edit_message_text(
            text=f"{achievement['icon']} <b>{achievement['name']}</b>\n\n{achievement['description']}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Назад", callback_data="ach::back")]
            ])
        )

