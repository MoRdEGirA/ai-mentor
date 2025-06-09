from telegram import Update
from telegram.ext import ContextTypes
from handlers.test_fsm import ask_question
from state import Q1

async def handle_test_launch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["profile"] = {"стресс": 0, "тревожность": 0, "позитив": 0, "энергия": 0}
    context.user_data["q_index"] = 0
    await ask_question(update, context)
    return Q1