from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from handlers.assignments_fsm import show_assignments
from handlers.achievements import show_achievements
from handlers.motivation import show_motivation

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Мои задания", callback_data="menu::assignments")],
        [InlineKeyboardButton("🎯 Сменить тему", callback_data="menu::change_topic")],
        [InlineKeyboardButton("👤 Профиль", callback_data="menu::profile")],
        [InlineKeyboardButton("🏆 Достижения", callback_data="menu::achievements")],
        [InlineKeyboardButton("💬 Мотивация", callback_data="menu::motivation")]
    ])

    if update.message:
        await update.message.reply_text("Главное меню:", reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text("Главное меню:", reply_markup=keyboard)

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.split("::")[1]

    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="menu::back")]
    ])

    if action == "assignments":
        await show_assignments(update, context)
    elif action == "change_topic":
        await query.edit_message_text("🎯 Скоро можно будет сменить тему.", reply_markup=back_button)
    elif action == "profile":
        await query.edit_message_text("👤 Здесь будет твой профиль.", reply_markup=back_button)
    elif action == "rewards":
        await query.edit_message_text("🏆 Награды будут отображены здесь.", reply_markup=back_button)
    elif action == "back":
        await show_main_menu(update, context)
    elif action == "achievements":
        await show_achievements(update, context)
    elif action == "motivation":
        await show_motivation(update, context)



