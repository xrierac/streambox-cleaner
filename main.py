from dotenv import load_dotenv
from deluge import *
from sonarr import *
import os

load_dotenv()

deluge_host = os.environ['DELUGE_HOST']
deluge_port = int(os.environ['DELUGE_PORT'])
deluge_user = os.environ['DELUGE_USER']
deluge_pass = os.environ['DELUGE_PASS']
sonarr_url = os.environ['SONARR_URL']
sonarr_api = os.environ['SONARR_API']

if __name__ == "__main__":
    print("Welcome to the Streambox Cleaner!")

    # Initialize the Deluge object with the necessary parameters
    deluge1 = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)

    # Initialize the Sonarr object with the necessary parameters
    sonarr1 = SonarrClient(sonarr_url, sonarr_api)


    print("Choose your option:")
    print("1. Delete torrents by name")
    print("2. Delete torrents not registered with the trackers")
    print("3. Delete series from Sonarr")
    print("4. Exit")
    input_choice = input("Enter your choice: ")
    if input_choice == '1':
        print("You chose to delete torrents by name.")
        input_name = input("Enter the name or part of the name of the torrent: ")
        deluge1.delete_old_torrent(input_name)
    elif input_choice == '2':
        print("You chose to delete torrents not registered with the trackers.")
        deluge1.delete_unavailable_torrents()
    elif input_choice == '3':
        print("You chose to delete series from Sonarr.")
        sonarr1.get_series()
        series_id = input("Enter the ID of the series to delete: ")
        sonarr1.delete_series(series_id)
    elif input_choice == '4':
        print("Exiting the program.")