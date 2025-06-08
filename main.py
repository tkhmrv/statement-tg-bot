from ping_server import start_ping_server
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from dotenv import load_dotenv

start_ping_server()

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логгирование
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start — приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()

    logging.info(f"/start от пользователя {full_name} (id={user.id})")

    await update.message.reply_text(
        f"👋 Привет, {full_name}!\n\n"
        f"Это бот фотостудии Statement. Я умею отправлять фидбек с сайта в Telegram-группы.\n"
        f"Добавьте меня в нужный чат и нажмите кнопку активации внутри него.",
        reply_markup=ReplyKeyboardRemove()
    )

# /status — информация о текущем чате
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

# /activate — показать кнопку активации (только для групп)
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

# Обработка нажатия inline-кнопки "Запустить бота"
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
        f"Пожалуйста, скопируйте название чата и ID и вставьте их в админку сайта.",
        parse_mode="Markdown"
    )

# Установка команд при запуске
async def set_commands(app):
    commands = [
        BotCommand("start", "Приветствие и информация о боте"),
        BotCommand("status", "Информация о текущем чате"),
        BotCommand("activate", "Показать кнопку активации (только для групп)"),
        BotCommand("menu", "Показать список команд"),
    ]
    await app.bot.set_my_commands(commands)

# /menu — список всех команд
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        ("/start", "Приветствие и информация о боте"),
        ("/status", "Информация о текущем чате"),
        ("/activate", "Показать кнопку активации (только для групп)"),
        ("/menu", "Показать список команд"),
    ]
    text = "\U0001F4DD Доступные команды:\n\n" + "\n".join([f"{cmd} — {desc}" for cmd, desc in commands])
    await update.message.reply_text(text)

# Запуск
if __name__ == "__main__":
    logging.info("🚀 Бот запускается...")

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_commands).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("activate", send_activation_button))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    logging.info("✅ Бот успешно запущен и ждет команды.")
    app.run_polling()
