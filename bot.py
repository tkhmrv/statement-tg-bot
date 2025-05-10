import logging
import os
from dotenv import load_dotenv
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Загрузка .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логгирование
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()

    logging.info(f"/start от пользователя {full_name} (id={user.id})")

    await update.message.reply_text(
        f"👋 Привет, {full_name}!\n\n"
        f"Это бот фотостудии Statement. Я умею отправлять фидбек с сайта в Telegram-группы.\n"
        f"Добавьте меня в нужный чат и нажмите кнопку активации внутри него.\n\n"
        f"ℹ️ Все команды доступны через меню Telegram или команду /menu."
    )


# /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = chat.id
    chat_title = chat.title or f"{chat.first_name} {chat.last_name or ''}".strip()

    logging.info(f"/status в чате {chat_title} (id={chat_id})")

    await update.message.reply_text(
        f"ℹ️ Текущий чат:\n\n"
        f"- Название: *{chat_title}*\n"
        f"- ID: `{chat_id}`",
        parse_mode="Markdown"
    )


# /activate — кнопка запуска (только в группах)
async def send_activation_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        logging.warning(f"🚫 Попытка активации в личном чате (id={chat.id}) отклонена")
        await update.message.reply_text("⚠️ Активация доступна только в группах.")
        return

    chat_id = chat.id
    keyboard = [
        [InlineKeyboardButton("✅ Запустить бота", callback_data=f"start_bot:{chat_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    logging.info(f"📩 Отправлена кнопка активации в чат (id={chat_id})")

    await context.bot.send_message(
        chat_id=chat_id,
        text="👋 Бот успешно добавлен в этот чат. Нажмите кнопку ниже, чтобы активировать его:",
        reply_markup=reply_markup
    )


# Обработка inline кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat = update.effective_chat
    chat_id = chat.id
    chat_title = chat.title or f"{chat.first_name} {chat.last_name or ''}".strip()

    logging.info(f"✅ Бот активирован в чате {chat_title} (id={chat_id})")

    await query.edit_message_text(
        f"✅ Бот активирован для этого чата!\n\n"
        f"- Название чата: *{chat_title}*\n"
        f"- ID: `{chat_id}`\n\n"
        f"Скопируйте название и ID и вставьте их в админку сайта.",
        parse_mode="Markdown"
    )


# /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        ("/start", "Приветствие и краткая информация о боте"),
        ("/status", "Информация о текущем чате"),
        ("/activate", "Показать кнопку активации (только для групп)"),
        ("/menu", "Показать это меню со всеми командами"),
    ]
    text = "📋 Доступные команды:\n\n" + "\n".join([f"{cmd} — {desc}" for cmd, desc in commands])
    await update.message.reply_text(text)


# Основной запуск
if __name__ == "__main__":
    logging.info("🚀 Бот запускается...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Установка команд в меню Telegram
    async def set_commands(app):
        await app.bot.set_my_commands([
            BotCommand("start", "Приветствие"),
            BotCommand("status", "Информация о текущем чате"),
            BotCommand("activate", "Кнопка запуска (только в группах)"),
            BotCommand("menu", "Список всех команд"),
        ])
    app.post_init = set_commands

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("activate", send_activation_button))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    logging.info("✅ Бот успешно запущен и ждёт команды.")
    app.run_polling()
