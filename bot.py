import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─────────────────────────────────────────────
#  CONFIG  — faqat shu ikki qatorni o'zgartiring
# ─────────────────────────────────────────────
BOT_TOKEN = "8018963742:AAHQiG7DOmcWsJirtd91lmTUVsFKCjXdzmg"
ADMIN_IDS = [705457366, 5427459567, 433236357]
# ─────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("📝 Anonim xabar yuborish")]],
    resize_keyboard=True,
    one_time_keyboard=False,
)

WAITING_FOR_MESSAGE: set[int] = set()


def get_user_info(user) -> str:
    """Telegramdan mavjud ma'lumotlarni yig'adi — hech qanday ro'yxatdan o'tishsiz."""
    name = user.full_name or "Noma'lum"
    username = f"@{user.username}" if user.username else "Yo'q"
    user_id = user.id

    lines = [
        f"👤 *Ism:* {name}",
        f"🔗 *Username:* {username}",
        f"🆔 *Telegram ID:* `{user_id}`",
    ]
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 *Maktab Anonim Portaliga xush kelibsiz!*\n\n"
        "Bu yerda istalgan muammo, shikoyat yoki taklifingizni "
        "mutlaqo anonim tarzda yuborishingiz mumkin.\n\n"
        "Boshlash uchun pastdagi tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ *Qanday ishlaydi?*\n\n"
        "1. *📝 Anonim xabar yuborish* tugmasini bosing\n"
        "2. Xabaringizni yozing va yuboring\n"
        "3. Tayyor!\n\n"
        "✅ Hech qanday ro'yxatdan o'tish kerak emas.\n"
        "✅ Xohlagancha xabar yuborishingiz mumkin.",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


async def button_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    WAITING_FOR_MESSAGE.add(update.effective_user.id)
    await update.message.reply_text(
        "✍️ Xabaringizni yozing va yuboring.\n"
        "_(U adminlarga yetkaziladi.)_",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    text = update.message.text

    if text == "📝 Anonim xabar yuborish":
        await button_pressed(update, context)
        return

    if user_id not in WAITING_FOR_MESSAGE:
        await update.message.reply_text(
            "Xabar yuborish uchun *📝 Anonim xabar yuborish* tugmasini bosing.",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    WAITING_FOR_MESSAGE.discard(user_id)

    user_info = get_user_info(user)

    forward_text = (
        "📩 *Yangi Xabar*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{user_info}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 *Xabar:*\n{text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    sent_count = 0
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=forward_text,
                parse_mode="Markdown",
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Adminga yuborishda xatolik {admin_id}: {e}")

    if sent_count > 0:
        await update.message.reply_text(
            "✅ *Xabaringiz yuborildi!*\n\n"
            "Ovoz berganing uchun rahmat. Har bir xabar muhim. 💙",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD,
        )
    else:
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.",
            reply_markup=MAIN_KEYBOARD,
        )


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
