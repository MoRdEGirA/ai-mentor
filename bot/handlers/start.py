import httpx
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import API_BASE_URL
from handlers.achievements import assign_achievement

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = str(user.id)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/students/", json={
                "telegram_id": telegram_id,
                "name": user.first_name or "Unknown"
            })

            try:
                await update.message.delete()
            except:
                pass

            if response.status_code == 200:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Погнали!", callback_data="start_test")]
                ])
                try:
                    await assign_achievement(telegram_id, "Новичок")
                except Exception as e:
                    print(f"[ERROR] Не удалось присвоить достижение: {e}")

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=(
                        f"Привет, {user.first_name}! Я — твой личный ИИ-ментор 👋\n\n"
                        "Для начала давай пройдём небольшой тест, чтобы понять, в каком ты состоянии "
                        "и как лучше всего выстраивать взаимодействие. Готов?"
                    ),
                    reply_markup=keyboard
                )
            else:
                await update.effective_chat.send_message("Ты уже зарегистрирован.")
        except Exception as e:
            print(f"[ERROR] Ошибка при подключении: {e}")
            await update.effective_chat.send_message("Ошибка при подключении к серверу. Попробуй позже.")
