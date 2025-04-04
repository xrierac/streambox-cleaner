import requests

class RadarrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def find_matching_movies(self, movie_name) -> list:
        matching_movies = []
        movie_list = self.get_movies()
        for movie in movie_list:
            if movie_name.lower() in movie['title'].lower():
                matching_movies.append(movie)
        return matching_movies

    def get_movies(self):
        #Fetches all movies from Radarr.
        url = f"{self.base_url}/api/v3/movie"
        headers = {
            "X-Api-Key": self.api_key
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            movies_list = response.json()
            return movies_list
        else:
            print(f"Failed to fetch movies. Status code: {response.status_code}")
    
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