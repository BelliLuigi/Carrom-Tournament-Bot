import logging
import mysql.connector
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler)
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

STEP1, STEP2, STEP3, STEP4,STEP5, STEPA = range(6)
MATCH, STATS = range(2)

def database_connection():
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return db, db.cursor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data["user"] = user
    db, cursor = database_connection()
    cursor.execute("INSERT INTO users (username) VALUES (%s) ON DUPLICATE KEY UPDATE username=username", (user.first_name,))
    db.commit()
    cursor.close()
    db.close()
    logger.info("User %s (%s) started the conversation.", user.first_name, user.id)
    keyboard = [
        [
            InlineKeyboardButton(u'Register match ✏️', callback_data=MATCH),
            InlineKeyboardButton(u'Stats 📊', callback_data=STATS)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Remember that your oppponent should also be a user of this bot.\n\n")
    await update.message.reply_text(f"Hi {user.first_name}, just did a match?", reply_markup=reply_markup)
    return STEP1

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.user_data.get("user")
    query = update.callback_query
    await query.answer()
    logger.info("User %s (%s) selected 'Register match'", user.first_name, user.id)
    db, cursor = database_connection()
    cursor.execute("SELECT username FROM users")
    oppos = cursor.fetchall()
    cursor.close()
    db.close()
    list_of_opponents = [opponent[0] for opponent in oppos if opponent[0] != user.first_name]
    if not list_of_opponents:
        await query.edit_message_text(text="No users found. Please register at least one user before starting a match.")
        return ConversationHandler.END
    keyboard = [
        [InlineKeyboardButton(opponent, callback_data=opponent) for opponent in list_of_opponents[0:4]],
        [InlineKeyboardButton(opponent, callback_data=opponent) for opponent in list_of_opponents[4:8]],
        [InlineKeyboardButton(opponent, callback_data=opponent) for opponent in list_of_opponents[8:12]],
        [InlineKeyboardButton(opponent, callback_data=opponent) for opponent in list_of_opponents[12:16]],
        [InlineKeyboardButton(u'⛔ Back 🔙', callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Hey {user.first_name}, choose your opponent:", reply_markup=reply_markup
    )
    return STEP2

async def select_opponent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = context.user_data.get("user")
    await query.answer()
    context.chat_data["opponent"] = query.data
    await query.edit_message_text(text=f"{user.first_name}, you chose {query.data}!")
    logger.info("User %s selected opponent: %s", user.first_name, query.data)
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=i) for i in range(7)],
        [InlineKeyboardButton(str(i), callback_data=i) for i in range(7, 13)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Points for {user.first_name}?", reply_markup=reply_markup)
    
    return STEP3

async def me_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.user_data.get("user")
    query = update.callback_query
    await query.answer()
    points = int(query.data)
    context.chat_data["me_points"] = points
    logger.info("User %s selected opponent: %s. Points %s - ?", user.first_name, query.data, points)
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=i) for i in range(7)],
        [InlineKeyboardButton(str(i), callback_data=i) for i in range(7, 13)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"{user.first_name}, you scored {points} points!,\nSelect points for {context.chat_data['opponent']}.",
         reply_markup=reply_markup)
    return STEP4

async def they_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = context.user_data.get("user")
    opponent = context.chat_data.get("opponent")
    await query.answer()
    points = int(query.data)
    context.chat_data["they_points"] = points
    logger.info("User %s selected opponent: %s. Points %s - ?", user.first_name, context.chat_data['me_points'], points)
    keyboard = [
        InlineKeyboardButton(u'⛔ Cancel 🔙', callback_data='cancel'),
        InlineKeyboardButton(u'✅ Confirm 💾', callback_data='confirm')
    ]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await query.edit_message_text(text=f"Match: {user.first_name} vs {context.chat_data['opponent']} - {context.chat_data['me_points']} : {context.chat_data['they_points']}",
                                    reply_markup=reply_markup)
    
    return STEP5



async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = context.user_data.get("user")
    await query.answer()
    if query.data == 'cancel':
        await query.edit_message_text(text="Match cancelled.\n\nPress /start to start again.")
        return ConversationHandler.END
    else:
        db, cursor = database_connection()
        sql = "INSERT INTO matches (player1, player2, score1, score2) VALUES (%s, %s, %s, %s)"
        val = (user.first_name, context.chat_data['opponent'], context.chat_data['me_points'], context.chat_data['they_points'])
        cursor.execute(sql, val)
        db.commit()
        await query.edit_message_text(text="Match Confirmed!\n\nPress /start to start again.")
        logger.info("Match confirmed: %s vs %s - %s : %s", user.first_name, context.chat_data['opponent'], context.chat_data['me_points'], context.chat_data['they_points'])
        cursor.close()
        db.close()
        return ConversationHandler.END



async def sel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.user_data.get("user")
    query = update.callback_query
    await query.answer()
    logger.info("User %s (%s) selected 'Stats'", user.first_name, user.id)
    db, cursor = database_connection()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    keyboard = [
        [InlineKeyboardButton(user[0], callback_data=user[0]) for user in users],
        [InlineKeyboardButton(u'⛔ Back 🔙', callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Choose a user to see their stats:", reply_markup=reply_markup
    )
    return STEPA

async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db, cursor = database_connection()
    cursor.execute(f"SELECT player1, score1 FROM matches WHERE player1 = '{query.data}'")
    a = cursor.fetchall()
    cursor.execute(f"SELECT player2, score2 FROM matches WHERE player2 = '{query.data}'")
    b = cursor.fetchall()
    N_games = len(a+b)
    mean = sum(x[1] for x in a+b) / N_games
    std = (sum((x[1] - mean) ** 2 for x in a+b) / N_games) ** 0.5
    await update.effective_chat.send_message(
        f"Stats for {query.data}:\n"
        f"Total games: {N_games}\n"
        f"Mean score: {mean:.2f}\n"
        f"Standard deviation: {std:.2f}"
    )
    cursor.close()
    db.close()
    logger.info("User %s requested stats for %s", context.user_data.get("user").first_name, query.data)

    return ConversationHandler.END

if __name__ == '__main__':
    load_dotenv('dbdocker.env')
    application = Application.builder().token(os.getenv('THE_HOLY_TOKEN')).build()
    db, cursor = database_connection()
    convo_handler = ConversationHandler(
        entry_points = [CommandHandler("start", start)],
        states = {
            STEP1: [
                CallbackQueryHandler(match, pattern = "^" + str(MATCH) + "$"),
                CallbackQueryHandler(sel_stats, pattern = "^" + str(STATS) + "$")
                ],
            STEP2: [
                CallbackQueryHandler(select_opponent, pattern = "[a-zA-Z0-9_]+")
            ],
            STEP3: [
                CallbackQueryHandler(me_points, pattern = "[0-9]+")
            ],
            STEP4: [
                CallbackQueryHandler(they_points, pattern = "[0-9]+")
            ],
            STEP5: [
                CallbackQueryHandler(confirm, pattern = "^(confirm|cancel)$")
            ],
            STEPA: [
                CallbackQueryHandler(user_stats, pattern = "[a-zA-Z0-9_]+")
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(convo_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
