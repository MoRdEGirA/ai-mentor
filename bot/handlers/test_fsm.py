from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from handlers.test import questions, question_states
from state import TEST_DONE
import httpx
from config import API_BASE_URL

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("q_index", 0)
    question = questions[index]
    keyboard = InlineKeyboardMarkup.from_column([
        InlineKeyboardButton(text=opt, callback_data=f"q{index}::{opt}")
        for opt in question["options"]
    ])

    if "last_msg_id" in context.user_data:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data["last_msg_id"])
        except:
            pass

    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question["text"],
        reply_markup=keyboard
    )
    context.user_data["last_msg_id"] = msg.message_id


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # формат: q0::Солнце

    try:
        q_index, answer = data.split("::")
        q_index = int(q_index[1:])
        effects = questions[q_index]["options"][answer]
        profile = context.user_data.get("profile", {"стресс": 0, "тревожность": 0, "позитив": 0, "энергия": 0})

        for key in effects:
            profile[key] += effects[key]

        context.user_data["profile"] = profile
        context.user_data["q_index"] = q_index + 1

        await query.edit_message_reply_markup(None)

        if q_index + 1 < len(questions):
            await ask_question(update, context)
            return question_states[q_index + 1]
        else:
            telegram_id = str(update.effective_user.id)
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{API_BASE_URL}/students/{telegram_id}")
                if r.status_code != 200:
                    raise Exception("Student not found")
                student_id = r.json()["id"]
                await client.post(f"{API_BASE_URL}/mood_logs/", json={
                    "student_id": student_id,
                    "score_stress": profile["стресс"],
                    "score_anxiety": profile["тревожность"],
                    "score_positive": profile["позитив"],
                    "score_energy": profile["энергия"]
                })

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🧱 Времена", callback_data="topic::tenses"),
                    InlineKeyboardButton("🧠 Слова", callback_data="topic::vocab")
                ],
                [
                    InlineKeyboardButton("🧩 Идиомы", callback_data="topic::idioms"),
                    InlineKeyboardButton("🎧 Аудирование", callback_data="topic::listening")
                ],
                [
                    InlineKeyboardButton("🗣️ Разговор", callback_data="topic::conversation"),
                    InlineKeyboardButton("🎯 Квизы", callback_data="topic::quiz")
                ]
            ])

            await query.edit_message_text(
                "Спасибо! Я получил информацию о твоем самочувствии 🧠\n\n"
                "Теперь выбери направление, в котором хочешь прокачаться:\n\n"
                "Его можно будет изменить в любой момент в меню",
                reply_markup=keyboard
            )
            return TEST_DONE

    except Exception as e:
        await query.edit_message_text(f"Произошла ошибка:\n{e}")
        return TEST_DONE