import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from deluge import DelugeClient
from sonarr import SonarrClient
from radarr import RadarrClient

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


WAITING_FOR_NAME = 1
WAITING_FOR_CONFIRMATION = 2

async def delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Write the name of the movie to delete.")
    return WAITING_FOR_NAME

async def handle_movie_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    await update.message.reply_text(f"Found movie: {movie['title']}. Do you want to delete it? (yes/no)")
    return WAITING_FOR_CONFIRMATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    radarr_client = RadarrClient(radarr_url, radarr_api)
    if user_input.lower() == 'yes':
        movie_id = context.user_data['movie_id']
        filename = radarr_client.get_movie_file(movie_id)
        if filename:
            deluge_client = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)
            deluge_client.delete_old_torrent(filename)
        else:
            await update.message.reply_text("Movie file not found.")
        radarr_client.delete_movie(movie_id)
        await update.message.reply_text(f"Movie {context.user_data['movie_title']} deleted.")
    elif user_input.lower() == 'no':
        await update.message.reply_text("Operation cancelled.")
    else:
        await update.message.reply_text("Invalid input. Please reply with 'yes' or 'no'.")
        return WAITING_FOR_CONFIRMATION
    await update.message.reply_text("Operation completed.")
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
            WAITING_FOR_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(start_handler)
    application.add_handler(timer_handler)
    application.add_handler(delete_movie_handler)
    application.add_handler(unknown_handler)

    application.run_polling()

# Command: Help
# def help_command(update: Update, context: CallbackContext) -> None:
#     commands = """
# Available commands:
# /get_series - List all series in Sonarr
#     """
#     update.message.reply_text(commands)

# def main():
#     print("Welcome to the Streambox Cleaner!")

#     # Initialize the Deluge object with the necessary parameters
#     deluge1 = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)

#     # Initialize the Sonarr object with the necessary parameters
#     sonarr1 = SonarrClient(sonarr_url, sonarr_api)

#     # Initialize the Radarr object with the necessary parameters
#     radarr1 = RadarrClient(radarr_url, radarr_api)

#     print("Choose your option:")
#     print("1. Delete torrents by name")
#     print("2. Delete torrents not registered with the trackers")
#     print("3. Delete series from Sonarr")
#     print("4. Delete movies")
#     print("5. Exit")
#     input_choice = input("Enter your choice: ")
#     if input_choice == '1':
#         print("You chose to delete torrents by name.")
#         input_name = input("Enter the name or part of the name of the torrent: ")
#         deluge1.delete_old_torrent(input_name)
#     elif input_choice == '2':
#         print("You chose to delete torrents not registered with the trackers.")
#         deluge1.delete_unavailable_torrents()
#     elif input_choice == '3':
#         print("You chose to delete series from Sonarr.")
#         sonarr1.get_series()
#         series_id = input("Enter the ID of the series to delete: ")
#         sonarr1.delete_series(series_id)
#     elif input_choice == '4':
#         print("You chose to delete movies from Radarr and Deluge.")
#         radarr1.get_movies()
#         movies_id = input("Enter the ID of the movies to delete: ")
#         path = radarr1.get_movie_file(movies_id)
#         print(f"Path: {path}")
#         if not path:
#             print("Movie file not found.")
#         else:
#             deluge1.delete_old_torrent(path)
#             radarr1.delete_movie(movies_id)
#     elif input_choice == '5':
#         print("Exiting the program.")
# if __name__ == "__main__":
#     main()