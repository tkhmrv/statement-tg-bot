import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логгирование под Railway
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
        f"Я бот фотостудии и помогу вам получать уведомления в Telegram-группах.\n"
        f"Добавьте меня в нужный чат и нажмите кнопку активации внутри него."
    )

# /status — информация о текущем чате
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = chat.id
    chat_title = chat.title or f"{chat.first_name} {chat.last_name or ''}".strip()

    logging.info(f"/status в чате {chat_title} (id={chat_id})")

    await update.message.reply_text(
        f"ℹ️ Текущий чат:\n"
        f"• Название: *{chat_title}*\n"
        f"• ID: `{chat_id}`",
        parse_mode="Markdown"
    )

# Обработка inline-кнопки "Запустить бота"
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat = update.effective_chat
    chat_id = chat.id
    chat_title = chat.title or f"{chat.first_name} {chat.last_name or ''}".strip()

    logging.info(f"✅ Бот активирован в чате {chat_title} (id={chat_id})")

    await query.edit_message_text(
        f"✅ Бот активирован для этого чата!\n\n"
        f"📍 Название чата: *{chat_title}*\n"
        f"🆔 ID: `{chat_id}`\n\n"
        f"📥 Пожалуйста, скопируйте этот ID и вставьте его в админку сайта.",
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
        text="👋 Бот добавлен в этот чат. Нажмите кнопку ниже, чтобы активировать его:",
        reply_markup=reply_markup
    )

# Запуск
if __name__ == "__main__":
    logging.info("🚀 Бот запускается...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("activate", send_activation_button))

    logging.info("✅ Бот успешно запущен и ждет команды.")
    app.run_polling()
