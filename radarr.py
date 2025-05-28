import requests
from datetime import datetime, timezone

class RadarrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        url = f"{self.base_url}/ping"
        headers = {
            "X-Api-Key": self.api_key
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Successfully connected to Radarr.")
        else:
            raise Exception(f"Failed to connect to Radarr. Status code: {response.status_code}")
        
    def is_old(self, date_str, days = 360):
        # Parse the ISO 8601 date string (with 'Z' for UTC)
        added_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days_diff = (now - added_date).days
        return days_diff > days

    def find_matching_movies(self, movie_name) -> list:
        matching_movies = []
        movie_list = self.get_movies()
        for movie in movie_list:
            if movie_name.lower() in movie['title'].lower():
                matching_movies.append(movie)
        return matching_movies
    
    def get_movies(self):
        # Fetches all movies from Radarr.
        url = f"{self.base_url}/api/v3/movie"
        headers = {
            "X-Api-Key": self.api_key
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch movies. Status code: {response.status_code}")
            return []
    
    def get_old_bad_movies(self):
        movie_list = self.get_movies()
        if not movie_list:
            print("No movies found.")
            return []
        low_rating_movies = []
        # Print all movies
        for movie in movie_list:
            if 'imdb' in movie['ratings'] and movie['ratings']['imdb']['value'] < 5.0:
                low_rating_movies.append(movie)
        if not low_rating_movies:
            print("No low-rated movies found.")
            return []
        for movie in low_rating_movies:
            if 'movieFile' in movie and 'dateAdded' in movie['movieFile']:
                date_added = movie['movieFile']['dateAdded']
                if self.is_old(date_added, 30):
                    movie['is_old'] = True
                else:
                    movie['is_old'] = False
            else:
                movie['is_old'] = False
        old_bad_movies = [movie for movie in low_rating_movies if movie.get('is_old', False)]
        return old_bad_movies

    def get_old_movies(self):
        movie_list = self.get_movies()
        # Filter movies that are older than 30 days
        for movie in movie_list:
            if 'movieFile' in movie and 'dateAdded' in movie['movieFile']:
                date_added = movie['movieFile']['dateAdded']
                if self.is_old(date_added):
                    movie['is_old'] = True
                else:
                    movie['is_old'] = False
            else:
                movie['is_old'] = False
        old_movies = [movie for movie in movie_list if movie.get('is_old', False)]
        return old_movies
    
    def get_movie_file(self, movies_id):
        url = f"{self.base_url}/api/v3/movie/{movies_id}"
        headers = {
            "X-Api-Key": self.api_key
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            movie_file = response.json()
            return movie_file.get('movieFile').get('relativePath')
        else:
            print(f"Failed to fetch movie file. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        return None

    def delete_movie(self, movies_id, delete_files=True):
        """
        Deletes a movie from Radarr by its ID.

        :param movies_id: The ID of the movies to delete.
        :param delete_files: Whether to delete the associated files (default: True).
        """
        url = f"{self.base_url}/api/v3/movie/{movies_id}"
        params = {
            "deleteFiles": delete_files
        }
        headers = {
            "X-Api-Key": self.api_key
        }

        response = requests.delete(url, params=params, headers=headers)

        if response.status_code == 200:
            print(f"Successfully deleted movies with ID {movies_id}.")
        else:
            print(f"Failed to delete movies with ID {movies_id}. Status code: {response.status_code}")
            print(f"Response: {response.text}")