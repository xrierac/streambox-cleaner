import time
from deluge_client import DelugeRPCClient

class DelugeClient:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def delete_unavailable_torrents(self):
        # Connect to Deluge client
        client = DelugeRPCClient(self.host, self.port, self.user, self.password)
        client.connect()
        
        # Get list of torrents
        fields = ['name', 'tracker_status']
        torrents = client.core.get_torrents_status({}, fields)

        # Iterate through torrents and check their status
        for torrent_id, torrent_info in torrents.items():

            torrent_name = torrent_info.get(b'name', b'Unknown Name').decode('utf-8')
            status = torrent_info.get(b'tracker_status', b'Unknown Status').decode('utf-8')
            if "Error: Torrent not registered with this tracker" in status:
                print(f"Deleting torrent: {torrent_name}")
                print(f"Status: {status}")
                client.core.remove_torrent(torrent_id, remove_data=True)
            elif "Error: Complete Season Uploaded" in status:
                print(f"Deleting torrent: {torrent_name}")
                print(f"Status: {status}")
                client.core.remove_torrent(torrent_id, remove_data=True)
        client.disconnect()

    # Function to calculate the age of a torrent in days
    def get_torrent_age(self, added_on):
        current_time = time.time()
        age_in_seconds = current_time - added_on
        age_in_days = age_in_seconds / (86400)
        return age_in_days

    # Function to delete torrents older than 30 days that match the input name
    def delete_old_torrent(self, input_name):
        # Connect to Deluge client
        client = DelugeRPCClient(self.host, self.port, self.user, self.password)
        client.connect()

        # Get list of torrents
        fields = ['name', 'time_added']
        torrents = client.core.get_torrents_status({}, fields)

        for torrent_id, torrent_info in torrents.items():
            torrent_name = torrent_info.get(b'name', b'Unknown Name').decode('utf-8')
            added_on_timestamp = torrent_info.get(b'time_added', None)

            if input_name.lower() in torrent_name.lower():
                age_in_days = self.get_torrent_age(added_on_timestamp)
                if age_in_days > 30:
                    print(f"Deleting torrent: {torrent_name} (Age: {age_in_days:.2f} days)")
                    client.core.remove_torrent(torrent_id, remove_data=True)
                else:
                    print(f"Skipping torrent: {torrent_name} (Age: {age_in_days:.2f} days)")

        client.disconnect()
    