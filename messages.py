MESSAGES = {
    'ar': {
        'welcome': (
            "👋 *مرحباً بك في بوت إزالة الخلفية!*\n\n"
            "قبل البدء، نحتاج إلى تسجيل إيميلك.\n"
            "📧 أرسل إيميلك الآن:\n"
            "_(Gmail, Yahoo, Hotmail فقط)_"
        ),
        'choose_lang': "🌐 اختر لغتك / Choose your language:",
        'email_invalid': "❌ الإيميل غير صحيح أو غير مدعوم.\nيرجى إدخال إيميل Gmail أو Yahoo أو Hotmail فقط.",
        'email_taken': "⚠️ هذا الإيميل مسجل مسبقاً. جرب إيميلاً آخر.",
        'registered_ok': (
            "✅ *تم التسجيل بنجاح!*\n\n"
            "أرسل لي أي صورة وسأزيل خلفيتها فوراً 🎨\n"
            "📸 *حدك اليومي المجاني: 3 صور/يوم*\n"
            "💎 للاشتراك المميز: /subscribe"
        ),
        'send_photo': "📸 أرسل الصورة التي تريد إزالة خلفيتها:",
        'processing': "⏳ جاري إزالة الخلفية...",
        'done': "✅ تم! إليك صورتك بدون خلفية 🎉",
        'limit_reached': (
            "⛔ *وصلت للحد اليومي المجاني (3 صور)*\n\n"
            "عد غداً للحصول على 3 صور جديدة مجاناً 🔄\n"
            "أو اشترك بـ *3$/شهر* للاستخدام غير المحدود!\n"
            "👉 /subscribe"
        ),
        'subscribe_info': (
            "💎 *الاشتراك المميز - 3$/شهر*\n\n"
            "✅ صور غير محدودة يومياً\n"
            "✅ أولوية في المعالجة\n"
            "✅ دعم فوري\n\n"
            "للاشتراك تواصل مع الدعم:\n"
            "👤 @SUPPORT_USERNAME\n\n"
            "أرسل له: `اريد الاشتراك` وسيرشدك للدفع ✅"
        ),
        'error': "❌ حدث خطأ أثناء المعالجة. حاول مرة أخرى.",
        'usage_status': "📊 *استخدامك اليوم:* {used}/3 صور",
        'already_registered': "✅ أنت مسجل بالفعل! أرسل صورة لإزالة خلفيتها.",
        'language_changed': "✅ تم تغيير اللغة إلى العربية.",
    },
    'en': {
        'welcome': (
            "👋 *Welcome to Background Remover Bot!*\n\n"
            "First, we need your email to get started.\n"
            "📧 Please send your email:\n"
            "_(Gmail, Yahoo, Hotmail only)_"
        ),
        'choose_lang': "🌐 اختر لغتك / Choose your language:",
        'email_invalid': "❌ Invalid or unsupported email.\nPlease use Gmail, Yahoo, or Hotmail only.",
        'email_taken': "⚠️ This email is already registered. Try another one.",
        'registered_ok': (
            "✅ *Registered successfully!*\n\n"
            "Send me any photo and I'll remove its background instantly 🎨\n"
            "📸 *Free daily limit: 3 photos/day*\n"
            "💎 Premium subscription: /subscribe"
        ),
        'send_photo': "📸 Send the photo you want to remove the background from:",
        'processing': "⏳ Removing background...",
        'done': "✅ Done! Here's your photo without background 🎉",
        'limit_reached': (
            "⛔ *You've reached your free daily limit (3 photos)*\n\n"
            "Come back tomorrow for 3 new free photos 🔄\n"
            "Or subscribe for *$3/month* for unlimited use!\n"
            "👉 /subscribe"
        ),
        'subscribe_info': (
            "💎 *Premium Subscription - $3/month*\n\n"
            "✅ Unlimited photos per day\n"
            "✅ Priority processing\n"
            "✅ Instant support\n\n"
            "To subscribe, contact support:\n"
            "👤 @SUPPORT_USERNAME\n\n"
            "Send: `I want to subscribe` and they'll guide you ✅"
        ),
        'error': "❌ An error occurred during processing. Please try again.",
        'usage_status': "📊 *Today's usage:* {used}/3 photos",
        'already_registered': "✅ You're already registered! Send a photo to remove its background.",
        'language_changed': "✅ Language changed to English.",
    }
}

def msg(telegram_id, key, **kwargs):
    from database import get_user_language
    lang = get_user_language(telegram_id)
    text = MESSAGES[lang].get(key, '')
    return text.format(**kwargs) if kwargs else text
