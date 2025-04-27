import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from deluge import DelugeClient
from sonarr import SonarrClient
from radarr import RadarrClient

WAITING_FOR_NAME = 1
WAITING_FOR_CONFIRMATION = 2

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()

deluge_host = os.environ['DELUGE_HOST']
deluge_port = int(os.environ['DELUGE_PORT'])
deluge_user = os.environ['DELUGE_USER']
deluge_pass = os.environ['DELUGE_PASS']
sonarr_url = os.environ['SONARR_URL']
sonarr_api = os.environ['SONARR_API']
radarr_url = os.environ['RADARR_URL']
radarr_api = os.environ['RADARR_API']
telegram_api = os.environ['TELEGRAM_API']

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Streambox Cleaner Bot! Use /help to see available commands.")

async def callback_cleaner(context: ContextTypes.DEFAULT_TYPE):
    deluge_client = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)
    unavailable_torrents = deluge_client.delete_unavailable_torrents()
    for torrent_name in unavailable_torrents:
        await context.bot.send_message(chat_id=context.job.chat_id, text=f"Deleted torrent: {torrent_name}")

async def callback_timer(update: Update, context : ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Scheduler for cleaning started.")
    context.job_queue.run_repeating(callback_cleaner, interval=86400, first=5, chat_id=chat_id)

async def delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Write the name of the movie to delete.")
    return WAITING_FOR_NAME

async def handle_movie_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    keyboard = [
        [
        InlineKeyboardButton("Yes", callback_data='yes'),
        InlineKeyboardButton("No", callback_data='no'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_input = update.message.text
    context.user_data['movie_name'] = user_input
    radarr_client = RadarrClient(radarr_url, radarr_api)
    matching_movies = radarr_client.find_matching_movies(user_input)
    if not matching_movies:
        await update.message.reply_text("No matching movies found.")
        return ConversationHandler.END
    movie = matching_movies[0]
    context.user_data['movie_id'] = movie['id']
    context.user_data['movie_title'] = movie['title']
    await update.message.reply_text(f"Found movie: {movie['title']}.\nDo you want to delete it?", reply_markup=reply_markup)
    return WAITING_FOR_CONFIRMATION

async def handle_movie_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    radarr_client = RadarrClient(radarr_url, radarr_api)
    if query.data == 'yes':
        movie_id = context.user_data['movie_id']
        filename = radarr_client.get_movie_file(movie_id)
        if filename:
            deluge_client = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)
            deluge_client.delete_old_torrent(filename)
        else:
            await query.edit_message_text("Movie file not found.")
        radarr_client.delete_movie(movie_id)
        await query.edit_message_text(f"Movie {context.user_data['movie_title']} deleted.")
    elif query.data == 'no':
        await query.edit_message_text("Operation cancelled.")
    else:
        await update.message.reply_text("Invalid input. Please reply with 'yes' or 'no'.")
        return WAITING_FOR_CONFIRMATION
    return ConversationHandler.END 

async def delete_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Write the name of the series to delete.")
    return WAITING_FOR_NAME

async def handle_series_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
            [
            InlineKeyboardButton("Yes", callback_data='yes'),
            InlineKeyboardButton("No", callback_data='no'),
            ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_input = update.message.text
    context.user_data['movie_name'] = user_input
    sonarr_client = SonarrClient(sonarr_url, sonarr_api)
    matching_series = sonarr_client.find_matching_series(user_input)
    if not matching_series:
        await update.message.reply_text("No matching series found.")
        return ConversationHandler.END
    series = matching_series[0]
    context.user_data['series_id'] = series['id']
    context.user_data['series_title'] = series['title']
    await update.message.reply_text(f"Found series: {series['title']}.\nDo you want to delete it?", reply_markup=reply_markup)
    return WAITING_FOR_CONFIRMATION

async def handle_series_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    sonarr_client = SonarrClient(sonarr_url, sonarr_api)
    if query.data == 'yes':
        series_id = context.user_data['series_id']
        sonarr_client.delete_series(series_id)
        await query.edit_message_text(f"Series {context.user_data['series_title']} deleted.")
    elif query.data == 'no':
        await query.edit_message_text("Operation cancelled.")
    else:
        await update.message.reply_text("Invalid input. Please reply with 'yes' or 'no'.")
        return WAITING_FOR_CONFIRMATION
    return ConversationHandler.END
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_api).build()
 
    start_handler = CommandHandler('start', start)
    timer_handler = CommandHandler('timer', callback_timer)
    delete_movie_handler = ConversationHandler(
        entry_points=[CommandHandler('delete_movie', delete_movie)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_name)],
            WAITING_FOR_CONFIRMATION: [CallbackQueryHandler(handle_movie_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    delete_series_handler = ConversationHandler(
        entry_points=[CommandHandler('delete_series', delete_series)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_series_name)],
            WAITING_FOR_CONFIRMATION: [CallbackQueryHandler(handle_series_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(start_handler)
    application.add_handler(timer_handler)
    application.add_handler(delete_movie_handler)
    application.add_handler(delete_series_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
