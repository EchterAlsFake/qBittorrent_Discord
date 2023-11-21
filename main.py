from pypresence import Presence
from colorama import *

import time
import qbittorrentapi
import getpass

application_id = "1176525076703744090"
image = "qbittorrent"  # Image for the Discord Bot
z = f"{Fore.LIGHTGREEN_EX}[+]{Fore.RESET}"

print(f"{z}Connecting to Discord...")
client = Presence(application_id)
client.connect()
print(f"{z}Connected to Discord!")

print(
    f"----------------------------{Fore.LIGHTYELLOW_EX}CONFIGURATION{Fore.RESET}-------------------------------------")
print(f"!!! Please enter your credentials for the WebUI, you've configured in the qBittorrent Client. !!! ")

print(f"""
Information:

{Fore.LIGHTCYAN_EX}If you have enabled 'Bypass Authentication for localhost' in the WebUI, just press enter when you get asked
for Username and Password.
{Fore.RESET}
""")

username = input(f"{z}Enter your username [Enter to skip authentication]: ")
password = getpass.getpass("Enter your password [None]: ")
host_input = input(f"{z}Enter webUI host [localhost]: ")
port_input = input(f"{z}Enter webUI port [8080]: ")
host = host_input if host_input else "localhost"
port = port_input if port_input else "8080"


conn_info = dict(
    host=host,
    port=port,
    username=username,
    password=password,
)

qbt_client = qbittorrentapi.Client(**conn_info)

try:
    print(f"{z}Connecting to {host}:{port}...")
    qbt_client.auth_log_in()
    print(f"{z}Connected to {host}:{port}!")

except qbittorrentapi.LoginFailed as e:
    print(f"Login failed: {e}")

print(f"{z}qBittorrent: {qbt_client.app.version}")
print(f"{z}qBittorrent Web API: {qbt_client.app.web_api_version}")

while True:

    uploading = 0
    downloading = 0

    # retrieve and show all torrents
    for torrent in qbt_client.torrents_info():
        if torrent.state == qbittorrentapi.TorrentState.UPLOADING:
            uploading += 1

        elif torrent.state == qbittorrentapi.TorrentState.DOWNLOADING:
            downloading += 1

    print(f"{z}Uploading:   ", uploading)
    print(f"{z}Downloading: ", downloading)
    client.update(details=f"qBittorrent: {qbt_client.app.version}", state=f"Uploading: {uploading} | Downloading: "
                                                                          f"{downloading}", large_image="qbittorrent",
                  buttons=[{"label": "Visit Project", "url":
                      "https://github.com/EchterAlsFake/qbittorrent_Discord_RPC"}])  # You can remove that if you want.

    time.sleep(10)  # Updates every 10 seconds
