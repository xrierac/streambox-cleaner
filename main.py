import time
from deluge_client import DelugeRPCClient

def get_torrent_age(added_on):
    current_time = time.time()
    age_in_seconds = current_time - added_on
    age_in_days = age_in_seconds / (86400)
    return age_in_days

def delete_old_torrent(input_name, deluge_host='localhost', deluge_port=58846, user='deluge', password='deluge'):
    # Connect to Deluge
    client = DelugeRPCClient(deluge_host, deluge_port, user, password)
    client.connect()

    # Get list of torrents
    fields = ['name', 'time_added']
    torrents = client.core.get_torrents_status({}, fields)

    for torrent_id, torrent_info in torrents.items():

        torrent_name = torrent_info.get(b'name', b'Unknown Name').decode('utf-8')
        added_on_timestamp = torrent_info.get(b'time_added', None)

        if input_name.lower() in torrent_name.lower():
            age_in_days = get_torrent_age(added_on_timestamp)
            if age_in_days > 30:
                print(f"Deleting torrent: {torrent_name} (Age: {age_in_days:.2f} days)")
                client.core.remove_torrent(torrent_id, remove_data=True)
            else:
                print(f"Skipping torrent: {torrent_name} (Age: {age_in_days:.2f} days)")

    client.disconnect()

if __name__ == "__main__":
    # Take input from user
    input_name = input("Enter the name or part of the name of the torrent: ")
    delete_old_torrent(input_name)