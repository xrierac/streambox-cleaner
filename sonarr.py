import requests

class SonarrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_series(self):
        #Fetches all series from Sonarr.
        url = f"{self.base_url}/api/v3/series"
        headers = {
            "X-Api-Key": self.api_key
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            series_list = response.json()
            for series in series_list:
                print(f"ID: {series['id']}, Title: {series['title']}")
            return series_list
        else:
            print(f"Failed to fetch series. Status code: {response.status_code}")
            print(f"Response: {response.text}")

    def delete_series(self, series_id, delete_files=True):
        """
        Deletes a series from Sonarr by its ID.

        :param series_id: The ID of the series to delete.
        :param delete_files: Whether to delete the associated files (default: True).
        """
        url = f"{self.base_url}/api/v3/series/{series_id}"
        params = {
            "deleteFiles": delete_files
        }
        headers = {
            "X-Api-Key": self.api_key
        }

        response = requests.delete(url, params=params, headers=headers)

        if response.status_code == 200:
            print(f"Successfully deleted series with ID {series_id}.")
        else:
            print(f"Failed to delete series with ID {series_id}. Status code: {response.status_code}")
            print(f"Response: {response.text}")