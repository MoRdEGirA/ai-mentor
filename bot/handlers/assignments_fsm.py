# bot/handlers/assignments_fsm.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
import httpx
from config import API_BASE_URL
import re
from handlers.achievements import assign_achievement
# Состояния задаются динамически
FEEDBACK = -1

async def show_assignments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE_URL}/students/{telegram_id}")
        student = r.json()

        r2 = await client.get(f"{API_BASE_URL}/assignments/by_student/{student['id']}")
        if r2.status_code != 200:
            assignments = []
        else:
            try:
                assignments = r2.json()
            except Exception:
                assignments = []

    if not isinstance(assignments, list):
        assignments = []

    if not assignments:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🆕 Сгенерировать задание", callback_data="assignment::generate")],
            [InlineKeyboardButton("🔙 Назад", callback_data="menu::back")]
        ])
        await update.callback_query.edit_message_text(
            "На сегодня у тебя нет заданий. Отдохни или попроси новое задание ⬇️",
            reply_markup=keyboard
        )
        return

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"📘 Задание {i+1}", callback_data=f"assignment::view::{assignment.get('id', '')}")]
            for i, assignment in enumerate(assignments) if isinstance(assignment, dict) and 'id' in assignment
        ] + [
            [InlineKeyboardButton("🔙 Назад", callback_data="menu::back")]
        ]
    )
    await update.callback_query.edit_message_text("Твои задания на сегодня:", reply_markup=keyboard)


async def view_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, assignment_id = query.data.split("::")
    context.user_data['current_assignment_id'] = assignment_id

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE_URL}/assignments/{assignment_id}")
        if r.status_code != 200:
            await query.edit_message_text("Ошибка загрузки задания. Попробуй позже.")
            return
        data = r.json()

    if 'content' not in data:
        await query.edit_message_text("Ошибка загрузки задания. Попробуй позже.")
        return

    context.user_data['current_assignment_data'] = data

    presentation_text = {
        "light": "🧘 Ты сегодня выглядишь немного уставшим. Вот лёгкое задание для тебя:",
        "normal": "📚 Держи задание на сегодня:",
        "challenge": "💪 Ты сегодня в отличной форме! Вот задание-вызов:"
    }.get(data.get("presentation_mode", "normal"), "📘 Задание:")

    theory = data['content'].get('theory', '')
    exercise = data['content'].get('exercise', '')
    preview = text_preview(f"{theory}\n\n{exercise}")
    text = f"{presentation_text}\n\n{preview}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Приступить", callback_data=f"assignment::start::{assignment_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu::assignments")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard)


def text_preview(full_text: str, limit: int = 700):
    return full_text[:limit] + ("..." if len(full_text) > limit else "")


async def start_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    assignment_id = query.data.split("::")[-1]
    data = context.user_data.get('current_assignment_data')

    if not data or 'content' not in data:
        await query.edit_message_text("Ошибка загрузки задания. Попробуй позже.")
        return ConversationHandler.END

    theory = data['content'].get('theory', '')
    exercise = data['content'].get('exercise', '')

    text = f"📘 Теория:\n\n{theory}\n\n---\n\n📝 Упражнение:\n{exercise}"

    context.user_data['assignment_text'] = text
    context.user_data['answers'] = []
    context.user_data['questions'] = extract_questions(exercise)
    context.user_data['current_question'] = 0

    return await ask_next_question(update, context)


def extract_questions(text):
    pattern = r"\d+\.\s.*?(?=(?:\n\d+\.|\Z))"
    matches = re.findall(pattern, text, re.DOTALL)
    return [m.strip() for m in matches]


def extract_options(question):
    pattern = r"[a-zA-Z]\)"
    options = re.findall(pattern, question)
    return sorted(set([opt[0] for opt in options]))


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get('current_question', 0)
    questions = context.user_data.get('questions', [])
    if index >= len(questions):
        return await finish_assignment(update, context)

    q = questions[index]
    options = extract_options(q)
    buttons = [[InlineKeyboardButton(opt, callback_data=f"assignment::answer::{opt}")] for opt in options]
    buttons.append([InlineKeyboardButton("🔙 В меню", callback_data="menu::back")])

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.edit_message_text(q, reply_markup=keyboard)
    else:
        await update.message.reply_text(q, reply_markup=keyboard)

    return index


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    answer = query.data.split("::")[-1]

    context.user_data.setdefault('answers', []).append(answer)
    context.user_data['current_question'] += 1

    return await ask_next_question(update, context)


async def finish_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("✅ Задание завершено! Я скоро пришлю обратную связь.")

    assignment_id = context.user_data.get("current_assignment_id")
    telegram_id = str(update.effective_user.id)
    answers = context.user_data.get("answers", [])

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                f"{API_BASE_URL}/assignments/feedback",
                params={"telegram_id": telegram_id, "assignment_id": assignment_id},
                json={"answers": answers}
            )
            if r.status_code == 200:
                feedback = r.json().get("feedback", "Ты молодец!")
                await update.callback_query.message.reply_text(feedback)
            else:
                await update.callback_query.message.reply_text("⚠️ Не удалось получить обратную связь.")
    except Exception as e:
        await update.callback_query.message.reply_text("❌ Произошла ошибка при получении обратной связи.")

    return ConversationHandler.END


async def complete_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assignment_id = context.user_data.get("current_assignment_id")
    if not assignment_id:
        return

    async with httpx.AsyncClient() as client:
        await client.post(f"{API_BASE_URL}/assignments/complete/{assignment_id}")


async def generate_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    

    query = update.callback_query
    await query.answer()
    telegram_id = str(query.from_user.id)
    await assign_achievement(telegram_id, "Энтузиаст")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="menu::back")]
    ])
    await query.edit_message_text("🤖 Подбираю для тебя задание... Это может занять пару секунд. ✨", reply_markup=keyboard)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{API_BASE_URL}/assignments/generate", params={"telegram_id": telegram_id})
            if r.status_code == 200:
                await show_assignments(update, context)
            else:
                await query.edit_message_text("😔 Не удалось сгенерировать задание. Попробуй позже.")
    except Exception as e:
        await query.edit_message_text("❌ Произошла ошибка при генерации задания.")

