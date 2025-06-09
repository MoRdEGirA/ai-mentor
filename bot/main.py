from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)
from config import BOT_TOKEN
from handlers.start import start
from handlers.callbacks import handle_test_launch
from handlers.test_fsm import handle_answer, ask_question
from handlers.test import question_states
from state import Q1
from handlers.topic_choice import handle_topic_choice
from handlers.menu import show_main_menu, handle_menu_selection
from handlers.assignments_fsm import (
    generate_assignment,
    show_assignments,
    view_assignment,
    start_assignment,
    complete_assignment,
)
from handlers.achievements import (
    show_achievements,
    achievement_description
)
from handlers.motivation import show_motivation

def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_test_launch, pattern="^start_test$")],
        states={
            state: [CallbackQueryHandler(handle_answer, pattern=f"^q{index}::")]
            for index, state in enumerate(question_states)
        },
        fallbacks=[],
        allow_reentry=True
    ))

    app.add_handler(CallbackQueryHandler(handle_topic_choice, pattern="^topic::"))
    app.add_handler(CommandHandler("menu", show_main_menu))
    app.add_handler(CallbackQueryHandler(handle_menu_selection, pattern="^menu::"))
    app.add_handler(CallbackQueryHandler(show_assignments, pattern="^menu::assignments$"))
    app.add_handler(CallbackQueryHandler(view_assignment, pattern="^assignment::view::"))
    app.add_handler(CallbackQueryHandler(start_assignment, pattern="^assignment::start::"))
    app.add_handler(CallbackQueryHandler(complete_assignment, pattern="^assignment::complete::"))
    app.add_handler(CallbackQueryHandler(generate_assignment, pattern="^assignment::generate$"))
    app.add_handler(CommandHandler("achievements", show_achievements))
    app.add_handler(CallbackQueryHandler(achievement_description, pattern="^ach::desc::"))
    app.add_handler(CallbackQueryHandler(show_motivation, pattern="^menu::motivation$"))

    app.run_polling()
