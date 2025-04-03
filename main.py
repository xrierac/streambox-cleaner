import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from deluge import DelugeClient
from sonarr import SonarrClient
from radarr import RadarrClient

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

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

async def list_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deluge_client = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)
    torrents = deluge_client.list_torrents()
    response = "Torrents:\n"
    if torrents:
        for torrent_id, torrent_info in torrents.items():
            torrent_name = torrent_info.get(b'name', b'Unknown Name').decode('utf-8')
            print(f"Torrent: {torrent_name}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Torrent: {torrent_name}")
    else:
        response = "No torrents found."

async def del_unavailable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deluge_client = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)
    unavailable_torrents = deluge_client.delete_unavailable_torrents()
    for torrent_name in unavailable_torrents:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Deleted torrent: {torrent_name}")
    if not unavailable_torrents:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No torrents to be deleted.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_api).build()
    
    start_handler = CommandHandler('start', start)
    list_handler = CommandHandler('list_torrents', list_torrents)
    del_unavailable_handler = CommandHandler('del_unavailable', del_unavailable)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(start_handler)
    application.add_handler(list_handler)
    application.add_handler(del_unavailable_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()

# Command: Help
# def help_command(update: Update, context: CallbackContext) -> None:
#     commands = """
# Available commands:
# /get_series - List all series in Sonarr
#     """
#     update.message.reply_text(commands)

# # Command: Get Series
# def get_series(update: Update, context: CallbackContext, sonarr_client) -> None:
#     series_list = sonarr_client.get_series()
#     if series_list:
#         response = "\n".join([f"ID: {series['id']}, Title: {series['title']}" for series in series_list])
#     else:
#         response = "No series found."
#     update.message.reply_text(response)

# # Main function to start the bot
# def main():

#     # Initialize the Deluge object with the necessary parameters
#     deluge1 = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)

#     # Initialize the Sonarr object with the necessary parameters
#     sonarr1 = SonarrClient(sonarr_url, sonarr_api)

#     # Initialize the Radarr object with the necessary parameters
#     radarr1 = RadarrClient(radarr_url, radarr_api)

#     # Initialize the bot with your token
#     updater = Updater(os.environ['TELEGRAM_API'])

#     # Get the dispatcher to register handlers
#     dispatcher = updater.dispatcher

#     # Register command handlers
#     dispatcher.add_handler(CommandHandler("start", start))
#     dispatcher.add_handler(CommandHandler("help", help_command))
#     dispatcher.add_handler(CommandHandler("get_series", get_series(sonarr_client=sonarr1)))

#     # Start the bot
#     updater.start_polling()
#     updater.idle()

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