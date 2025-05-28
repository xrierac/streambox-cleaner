import requests
import time

from datetime import datetime, timedelta

class TautulliClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        params = {
            "apikey": self.api_key,
            "cmd": "status"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            print("Successfully connected to Tautulli.")
        else:
            raise Exception(f"Failed to connect to Tautulli. Status code: {response.status_code}")

    def has_series_been_watched(self, series_name: str, days: int = 14) -> bool:
        while (days > 0):
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            params = {
                "start_date": start_date,
                "apikey": self.api_key,
                "cmd": "get_history",
                "media_type": "episode",
                "search": series_name,
                "length": 1  # Only need to know if at least one exists
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            print(data)  # Debugging line to check the response
            watched = data.get("response", {}).get("data", {}).get("data", [])
            if len(watched) > 0:
                print(f"Found watched episode of {series_name} within the last {days} days.")
                return True
            days -= 1
        return False

