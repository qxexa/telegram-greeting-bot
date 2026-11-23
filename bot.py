import hashlib
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.getenv("PORT", "8080"))
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")

logging.basicConfig(
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


def keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Нажать", callback_data="hello")]]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже.",
        reply_markup=keyboard(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "hello":
        await query.message.reply_text("Привет!")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    if PUBLIC_URL:
        webhook_path = "/telegram-webhook"
        secret_token = hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:32]
        log.info("Запуск webhook на порту %s", PORT)
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path.lstrip("/"),
            webhook_url=f"{PUBLIC_URL}{webhook_path}",
            secret_token=secret_token,
        )
    else:
        log.info("RENDER_EXTERNAL_URL не задан. Запуск polling")
        app.run_polling()


if __name__ == "__main__":
    main()
