import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO)

TAROT_CARDS = ["🃏 Шут","☀️ Солнце","🌙 Луна","⭐ Звезда","🗼 Башня","⚖️ Справедливость","💀 Смерть","😈 Дьявол","🌍 Мир","❤️ Влюблённые","🏆 Сила","🧙 Маг","👸 Жрица","🏛️ Иерофант","🚂 Колесо Фортуны","⚔️ Страшный Суд","🕌 Отшельник","🚀 Колесница","👑 Императрица"]

SYSTEM_PROMPT = """Ты Авелина — великий Бог Таро. Говоришь загадочно но несёшь полную чушь. Используй выдуманные термины: возбмунарот, квантовая аура, астральный фуфел, кармический пендель. Связывай карты с бытовыми вещами (холодильник, носки, маршрутка №42). Ссылайся на мудреца Зюзю из Урюпинска. Пиши 3-4 предложения с эмодзи 🔮✨🌙. В конце намекай на платный возбмунарот. Это юмор!"""

SPREADS = {
    "love": "любовь и сердечные дела",
    "money": "деньги и финансовый фуфел",
    "future": "будущее и квантовая аура",
    "poworot": "разворот судьбы",
    "vozbmunarot": "тайный возбмунарот",
}

def get_prediction(spread_type, cards, name):
    client = Groq(api_key=GROQ_API_KEY)
    cards_str = ", ".join(cards)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{name} просит расклад на: {SPREADS[spread_type]}. Карты: {cards_str}"}
        ],
        max_tokens=300
    )
    return completion.choices[0].message.content

def main_menu():
    keyboard = [
        [InlineKeyboardButton("❤️ Приворот / Отворот", callback_data="love")],
        [InlineKeyboardButton("💰 Денежный расклад", callback_data="money")],
        [InlineKeyboardButton("🔮 Общий расклад", callback_data="future")],
        [InlineKeyboardButton("🌀 Поворот судьбы", callback_data="poworot")],
        [InlineKeyboardButton("⚡ Возбмунарот!", callback_data="vozbmunarot")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🔮 *Приветствую тебя, {user.first_name}!*\n\nЯ — *Авелина*, Бог Таро и Повелительница Возбмунарота!\n\n_⚠️ Всё это юмор и развлечение!_\n\nВыбери расклад:",
        parse_mode="Markdown", reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu":
        await query.edit_message_text("🔮 Выбери расклад:", parse_mode="Markdown", reply_markup=main_menu())
        return
    if query.data in SPREADS:
        await query.edit_message_text("🌀 *Авелина колдует... возбмунарот активирован...* ✨", parse_mode="Markdown")
        cards = random.sample(TAROT_CARDS, k=3)
        try:
            prediction = get_prediction(query.data, cards, query.from_user.first_name)
        except Exception as e:
            prediction = "Астральные серверы перегружены! Меркурий в ретрограде. Попробуй позже 🔮"
        cards_display = " | ".join(cards)
        keyboard = [[InlineKeyboardButton("🔄 Ещё расклад!", callback_data="menu")]]
        await query.edit_message_text(
            f"🃏 *Твои карты:*\n{cards_display}\n\n🔮 *Авелина вещает:*\n\n{prediction}\n\n_⚠️ Это юмор! Авелина желает удачи! 🌙_",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
