#import logging
import os
#import asyncio
from dotenv import load_dotenv
from deluge import DelugeClient
from sonarr import SonarrClient
from radarr import RadarrClient
from tautulli import TautulliClient


load_dotenv()

deluge_host = os.environ['DELUGE_HOST']
deluge_port = int(os.environ['DELUGE_PORT'])
deluge_user = os.environ['DELUGE_USER']
deluge_pass = os.environ['DELUGE_PASS']
sonarr_url = os.environ['SONARR_URL']
sonarr_api = os.environ['SONARR_API']
radarr_url = os.environ['RADARR_URL']
radarr_api = os.environ['RADARR_API']
tautulli_url = os.environ['TAUTULLI_URL']
tautulli_api = os.environ['TAUTULLI_API']


def main():
    print("Welcome to the Streambox Cleaner!")

    # Initialize the Deluge object with the necessary parameters
    deluge1 = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)

    # Initialize the Sonarr object with the necessary parameters
    sonarr1 = SonarrClient(sonarr_url, sonarr_api)

    # Initialize the Radarr object with the necessary parameters
    radarr1 = RadarrClient(radarr_url, radarr_api)

    

    while True:
        print("Choose your option:")
        print("1. Delete torrents by name")
        print("2. Delete torrents not registered with the trackers")
        print("3. Delete series from Sonarr")
        print("4. Delete movies")
        print("5. Check if series has been watched in the last 14 days")
        print("6. Exit")
        print("")
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
            print("You chose to delete movies from Radarr and Deluge.")
            radarr1.get_movies()
            movies_id = input("Enter the ID of the movies to delete: ")
            path = radarr1.get_movie_file(movies_id)
            print(f"Path: {path}")
            if not path:
                print("Movie file not found.")
            else:
                deluge1.delete_old_torrent(path)
                radarr1.delete_movie(movies_id)
        elif input_choice == '5':
            print("You chose to check if a series has been watched in the last 14 days.")
            input_name = input("Enter the name of the series: ")
            if has_series_been_watched(input_name):
                print(f"The series '{input_name}' has been watched in the last 14 days.")
            else:
                print(f"The series '{input_name}' has not been watched in the last 14 days.")
        elif input_choice == '6':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
     main()