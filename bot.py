import os
import re
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters,
    ContextTypes
)
from rembg import remove
from PIL import Image
from dotenv import load_dotenv

import database as db
from messages import msg, MESSAGES

load_dotenv()

BOT_TOKEN     = os.getenv("BOT_TOKEN")
ADMIN_ID      = int(os.getenv("ADMIN_ID", "0"))  # تلغرام ID الخاص بك

# حالات المحادثة
WAITING_LANG  = 1
WAITING_EMAIL = 2

VALID_EMAIL_PATTERN = re.compile(
    r'^[\w\.\-\+]+@(gmail|yahoo|hotmail)\.com$', re.IGNORECASE
)

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if db.user_exists(user_id):
        await update.message.reply_text(
            msg(user_id, 'already_registered'), parse_mode='Markdown'
        )
        return ConversationHandler.END

    # اختيار اللغة
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text(
        MESSAGES['ar']['choose_lang'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_LANG

# ========== اختيار اللغة ==========
async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    lang = 'ar' if query.data == 'lang_ar' else 'en'
    context.user_data['language'] = lang

    await query.edit_message_text(
        MESSAGES[lang]['welcome'], parse_mode='Markdown'
    )
    return WAITING_EMAIL

# ========== استقبال الإيميل ==========
async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    email   = update.message.text.strip()
    lang    = context.user_data.get('language', 'ar')

    if not VALID_EMAIL_PATTERN.match(email):
        await update.message.reply_text(
            MESSAGES[lang]['email_invalid']
        )
        return WAITING_EMAIL

    success = db.register_user(user_id, email, lang)

    if not success:
        await update.message.reply_text(
            MESSAGES[lang]['email_taken']
        )
        return WAITING_EMAIL

    await update.message.reply_text(
        MESSAGES[lang]['registered_ok'], parse_mode='Markdown'
    )
    return ConversationHandler.END

# ========== استقبال الصورة ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not db.user_exists(user_id):
        await update.message.reply_text(
            "❌ يرجى التسجيل أولاً بكتابة /start\n"
            "Please register first by typing /start"
        )
        return

    if not db.can_use_today(user_id):
        await update.message.reply_text(
            msg(user_id, 'limit_reached'), parse_mode='Markdown'
        )
        return

    processing_msg = await update.message.reply_text(
        msg(user_id, 'processing')
    )

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        input_image  = Image.open(io.BytesIO(photo_bytes))
        output_image = remove(input_image)

        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        db.increment_usage(user_id)
        used = db.get_daily_usage(user_id)

        await processing_msg.delete()
        await update.message.reply_photo(
            photo=output_buffer,
            caption=(
                f"{msg(user_id, 'done')}\n"
                f"{msg(user_id, 'usage_status', used=used)}"
            ),
            parse_mode='Markdown'
        )

    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(msg(user_id, 'error'))
        print(f"Error: {e}")

# ========== /subscribe ==========
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        msg(user_id, 'subscribe_info'), parse_mode='Markdown'
    )

# ========== /language ==========
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang_ar"),
            InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en"),
        ]
    ]
    await update.message.reply_text(
        MESSAGES['ar']['choose_lang'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    lang = 'ar' if query.data == 'setlang_ar' else 'en'
    db.update_language(user_id, lang)

    await query.edit_message_text(
        MESSAGES[lang]['language_changed']
    )

# ========== /activate (للأدمن فقط) ==========
async def activate_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("استخدام: /activate <telegram_id>")
        return

    target_id = int(context.args[0])
    db.set_subscribed(target_id, 1)
    await update.message.reply_text(f"✅ تم تفعيل الاشتراك للمستخدم {target_id}")

    try:
        lang = db.get_user_language(target_id)
        congrats = (
            "🎉 *تم تفعيل اشتراكك المميز!*\nاستمتع بصور غير محدودة 🚀" if lang == 'ar'
            else "🎉 *Your premium subscription is now active!*\nEnjoy unlimited photos 🚀"
        )
        await context.bot.send_message(target_id, congrats, parse_mode='Markdown')
    except:
        pass

# ========== /deactivate (للأدمن فقط) ==========
async def deactivate_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("استخدام: /deactivate <telegram_id>")
        return

    target_id = int(context.args[0])
    db.set_subscribed(target_id, 0)
    await update.message.reply_text(f"✅ تم إلغاء اشتراك المستخدم {target_id}")

# ========== /emails (للأدمن - تصدير القائمة البريدية) ==========
async def export_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    emails = db.get_all_emails()
    if not emails:
        await update.message.reply_text("لا يوجد إيميلات مسجلة بعد.")
        return

    emails_text = "\n".join(emails)
    emails_file = io.BytesIO(emails_text.encode())
    emails_file.name = "emails_list.txt"

    await update.message.reply_document(
        document=emails_file,
        caption=f"📧 إجمالي الإيميلات: {len(emails)}"
    )

# ========== تشغيل البوت ==========
def main():
    db.init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # محادثة التسجيل
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_LANG:  [CallbackQueryHandler(language_chosen, pattern='^lang_')],
            WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('subscribe',   subscribe))
    app.add_handler(CommandHandler('language',    change_language))
    app.add_handler(CommandHandler('activate',    activate_user))
    app.add_handler(CommandHandler('deactivate',  deactivate_user))
    app.add_handler(CommandHandler('emails',      export_emails))
    app.add_handler(CallbackQueryHandler(set_language_callback, pattern='^setlang_'))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ البوت يعمل الآن 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()
