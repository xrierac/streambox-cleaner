import os
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
    try :
        # Initialize the client objects with the necessary parameters
        deluge1 = DelugeClient(deluge_host, deluge_port, deluge_user, deluge_pass)
        sonarr1 = SonarrClient(sonarr_url, sonarr_api)
        radarr1 = RadarrClient(radarr_url, radarr_api)
        tautulli1 = TautulliClient(tautulli_url, tautulli_api)

    except Exception as e:
        print(f"Error initializing clients: {e}")
        return
    
    else:
        print("Clients initialized successfully.")
    
    try:
        # Delete unavailable torrents
        deluge1.delete_unavailable_torrents()

    except Exception as e:
        print(f"Error deleting unavailable torrents: {e}")
        return
    
    else:
        print("Unavailable torrents deleted successfully.")

    try:
        old_bad_movies = radarr1.get_old_bad_movies()
        for movie in old_bad_movies:
            print(f"Deleting old bad movie: {movie['title']} (ID: {movie['id']})")
            path = radarr1.get_movie_file(movie['id'])
            deluge1.delete_old_torrent(path)
            radarr1.delete_movie(movie['id'], delete_files=True)
        
    except Exception as e:
        print(f"Error fetching movies from Radarr: {e}")
        return

if __name__ == "__main__":
    main()