from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import urllib.parse

TOKEN = "8705200128:AAGFcXTF2lss7l4Hj8WHH6Bg9pAnr9PxWZs"
ADMIN_ID = 7748781319


users = {}

# ================= MENUS =================

def main_menu():
    return ReplyKeyboardMarkup([
        ["احجز ميعاد 🚀"],
        ["✈️ حجز طيران", "🏨 حجز فنادق"],
        ["📂 تجهيز ملفات", "➕ خدمات أخرى"],
        ["تواصل واتساب 📲"]
    ], resize_keyboard=True)

def back():
    return ReplyKeyboardMarkup([["🔙 رجوع"]], resize_keyboard=True)

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {}

    await update.message.reply_text(
        "👋 أهلاً بيك في خدمات السفر ✈️\n\n"
        "🔥 احجز بسهولة في أقل من دقيقة\n"
        "⚠️ المواعيد محدودة وبتخلص بسرعة\n\n"
        "👇 اختار الخدمة وابدأ دلوقتي",
        reply_markup=main_menu()
    )

# ================= HANDLE =================

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    user = users.setdefault(user_id, {})

    # ================= رجوع =================
    if text == "🔙 رجوع":
        user.clear()
        await update.message.reply_text("رجعنا 👌", reply_markup=main_menu())
        return

    # ================= واتساب =================
    if text == "تواصل واتساب 📲":
        await update.message.reply_text(
            "تواصل مباشر 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("واتساب 📲", url="https://wa.me/201032013792")]
            ])
        )
        return

    # ================= احجز ميعاد (فيزا) =================

    if text == "احجز ميعاد 🚀":
        user.clear()
        user["mode"] = "visa"

        await update.message.reply_text(
            "📌 معاك باسبور؟",
            reply_markup=ReplyKeyboardMarkup([["نعم","لا"],["🔙 رجوع"]], resize_keyboard=True)
        )
        return

    if user.get("mode") == "visa" and "passport" not in user:
        if text == "نعم":
            user["passport"] = True
            await update.message.reply_text(
                "🌍 اختار الدولة:",
                reply_markup=ReplyKeyboardMarkup([
                    ["إيطاليا 🇮🇹","هولندا 🇳🇱"],
                    ["البرتغال 🇵🇹","اليونان 🇬🇷"],
                    ["🔙 رجوع"]
                ], resize_keyboard=True)
            )
            return
        else:
            await update.message.reply_text("❌ لازم باسبور ساري")
            return

    if user.get("mode") == "visa" and "country" not in user:
        user["country"] = text

        if "إيطاليا" in text:
            keyboard = [
                ["سياحة","بزنس"],
                ["عقد عمل","ضم عائلي"],
                ["🔙 رجوع"]
            ]
        else:
            keyboard = [
                ["سياحة","بزنس"],
                ["🔙 رجوع"]
            ]

        await update.message.reply_text("📄 نوع الفيزا:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text == "عقد عمل":
        await update.message.reply_text(
            "اختار نوع العقد:",
            reply_markup=ReplyKeyboardMarkup([["عقد عمل 2025","عقد عمل 2026"],["🔙 رجوع"]], resize_keyboard=True)
        )
        return

    if "عقد عمل" in text:
        user["visa"] = text
        await update.message.reply_text("📄 جواز + عقد")
        user["step"] = "name"
        await update.message.reply_text("👤 اسمك:")
        return

    if text == "ضم عائلي":
        await update.message.reply_text(
            "اختار:",
            reply_markup=ReplyKeyboardMarkup([["لم شمل الأسرة","لم شمل الأطفال"],["🔙 رجوع"]], resize_keyboard=True)
        )
        return

    if "لم شمل" in text:
        user["visa"] = text
        await update.message.reply_text("📄 جواز فقط")
        user["step"] = "name"
        await update.message.reply_text("👤 اسمك:")
        return

    if text == "سياحة":
        user["visa"] = "سياحة"
        await update.message.reply_text("📄 جواز فقط")
        user["step"] = "name"
        await update.message.reply_text("👤 اسمك:")
        return

    if text == "بزنس":
        user["visa"] = "بزنس"
        await update.message.reply_text("📄 جواز + دعوة")
        user["step"] = "name"
        await update.message.reply_text("👤 اسمك:")
        return

    # ================= الطيران =================

    if text == "✈️ حجز طيران":
        user.clear()
        user["service"] = "flight"
        user["step"] = "type"

        await update.message.reply_text(
            "✈️ نوع الرحلة؟",
            reply_markup=ReplyKeyboardMarkup([["ذهاب وعودة","ذهاب فقط"],["🔙 رجوع"]], resize_keyboard=True)
        )
        return

    if user.get("service") == "flight":

        if user["step"] == "type":
            user["type"] = text
            user["step"] = "from"
            await update.message.reply_text("📍 منين؟")
            return

        if user["step"] == "from":
            user["from"] = text
            user["step"] = "to"
            await update.message.reply_text("📍 رايح فين؟")
            return

        if user["step"] == "to":
            user["to"] = text
            user["step"] = "date"
            await update.message.reply_text("📅 تاريخ السفر؟")
            return

        if user["step"] == "date":
            user["date"] = text
            user["step"] = "people"
            await update.message.reply_text("👥 عدد المسافرين؟")
            return

        if user["step"] == "people":
            user["people"] = text
            user["step"] = "name"
            await update.message.reply_text("👤 اسمك:")
            return

    # ================= الفنادق =================

    if text == "🏨 حجز فنادق":
        user.clear()
        user["service"] = "hotel"
        user["step"] = "city"

        await update.message.reply_text("🏨 المدينة؟", reply_markup=back())
        return

    if user.get("service") == "hotel":

        if user["step"] == "city":
            user["city"] = text
            user["step"] = "nights"
            await update.message.reply_text("🌙 عدد الليالي؟")
            return

        if user["step"] == "nights":
            user["nights"] = text
            user["step"] = "people"
            await update.message.reply_text("👥 عدد الأفراد؟")
            return

        if user["step"] == "people":
            user["people"] = text
            user["step"] = "name"
            await update.message.reply_text("👤 اسمك:")
            return

    # ================= تجهيز ملفات =================

    if text == "📂 تجهيز ملفات":
        user.clear()
        user["service"] = "docs"
        user["step"] = "name"

        await update.message.reply_text("📂 تجهيز ملف\n👤 اسمك:", reply_markup=back())
        return

    # ================= خدمات أخرى =================

    if text == "➕ خدمات أخرى":
        user.clear()
        user["service"] = "custom"
        user["step"] = "custom"

        await update.message.reply_text("📝 اكتب طلبك:", reply_markup=back())
        return

    if user.get("service") == "custom" and user.get("step") == "custom":
        user["custom"] = text
        user["step"] = "name"
        await update.message.reply_text("👤 اسمك:")
        return

    # ================= الاسم =================

    if user.get("step") == "name":
        user["name"] = text
        user["step"] = "phone"
        await update.message.reply_text("📞 رقمك:")
        return

    # ================= الرقم =================

    if user.get("step") == "phone":
        user["phone"] = text

        wa_client = f"https://wa.me/{text.replace('0','20',1)}"

        msg = f"""
🔥 عميل جديد

👤 {user['name']}
📞 {user['phone']}
🛠️ {user.get('service','فيزا')}
🌍 {user.get('country','')}
📄 {user.get('visa','')}
📲 {wa_client}
"""

        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        encoded = urllib.parse.quote(msg)
        my_wa = f"https://wa.me/201032013792?text={encoded}"

        await update.message.reply_text(
            "✅ تم تسجيل طلبك\n🔥 تواصل دلوقتي لتأكيد الحجز",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 واتساب", url=my_wa)]
            ])
        )

        users[user_id] = {}

# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.run_polling()