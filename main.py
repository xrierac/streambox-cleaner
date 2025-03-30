from deluge import *

if __name__ == "__main__":
    # Take input from user
    print("Welcome to the Streambox Cleaner!")
    deluge1 = DeleteTorrent('localhost', 1111, 'user', 'password')
    print("Choose your option:")
    print("1. Delete torrents by name")
    print("2. Delete torrents not registered with the trackers")
    input_choice = input("Enter your choice: ")
    if input_choice == '1':
        print("You chose to delete torrents by name.")
        input_name = input("Enter the name or part of the name of the torrent: ")
        deluge1.delete_old_torrent(input_name)
    elif input_choice == '2':
        print("You chose to delete torrents not registered with the trackers.")
        deluge1.delete_unavailable_torrents()