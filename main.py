import os.path
import time

from io import TextIOWrapper
from qbittorrentapi import Client
from pypresence import Presence
from configparser import ConfigParser



class QBittorrentDiscord:
    def __init__(self):
        self.show_upload_speed = None
        self.show_download_speed = None
        self.show_total_downloaded_gb = None
        self.show_total_uploaded_gb = None
        self.show_share_ratio = None
        self.show_seeding = None
        self.show_uploading = None
        self.show_downloading = None
        self.setup_config_file()
        self.application_id = "1176525076703744090"
        self.image = "qbittorrent"  # Image for the Discord Bot
        self.uploading = 0
        self.downloading = 0
        self.update_delay = None
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.conf = None
        self.qbt_client = None
        self.client = None
        self.rpc = Presence(self.application_id)
        self.rpc.connect()
        self.load_configuration()
        while True:
            self.menu()


    @staticmethod
    def write_config_file():
        data = """[Setup]
username = None
password = None
host = None
port = None
setup_completed = false

[Configuration]
show_downloading = true
show_uploading = true
show_seeding = true
show_share_ratio = true
show_total_uploaded_gb = false
show_total_downloaded_gb = false
"""

        with open("config.ini", "w") as configuration_file: #type: TextIOWrapper
            configuration_file.write(data)


    def setup_config_file(self):
        if not os.path.isfile("config.ini"):
            self.write_config_file()

        self.conf = ConfigParser()
        self.conf.read("config.ini")

        sections = ["Setup", "Configuration"]
        options_setup = ["username", "password", "host", "port"]
        options_configuration = ["show_downloading", "show_uploading", "show_seeding", "show_share_ratio",
                                 "show_total_uploaded_gb", "show_total_downloaded_gb"]

        for section in sections:
            if not self.conf.has_section(section):
                self.write_config_file()

        for option in options_setup:
            if not self.conf.has_option(section="Setup", option=option):
                self.write_config_file()

        for option in options_configuration:
            if not self.conf.has_option(section="Configuration", option=option):
                self.write_config_file()

        if self.conf["Setup"]["setup_completed"] == "false":
            self.setup_connection()
            self.setup_discord_configuration()

    def setup_connection(self):
        print(f"""
Make sure you have the qbittorrent Web UI enabled. If you are using the default settings you can just
click enter on all options. If you want to also skip the password authentication you can enable 
the option "Bypass authentication for clients on localhost" and then leave username and password empty.
""")
        host = input(f"Enter your qbittorrent Web UI host (IP) [localhost] -->:")
        host = host if host else "localhost"
        port = input(f"Enter your qbittorrent Web UI port [8080] -->:")
        port = port if port else "8080"
        username = input(f"Enter your username [skip authentication] -->")
        password = input(f"Enter your password [skip authentication] -->")

        self.conf.set("Setup", "host", host)
        self.conf.set("Setup", "port", port)
        self.conf.set("Setup", "username", username)
        self.conf.set("Setup", "password", password)
        self.conf.set("Setup", "setup_completed", "true")

        with open("config.ini", "w") as conf: #type: TextIOWrapper
            self.conf.write(conf)

    def setup_discord_configuration(self):
        print(f"""
You can configure your Discord RPC now. This will affect what shows up in Discord, when you run this script
""")
        show_downloading = input(f"Do you want to show how many torrents you currently download? [true/false")
        show_uploading = input(f"Doy you want to show many torrents you currently upload? [true/false]")
        show_seeding = input(f"Do you want to show how many torrents you currently seed? [true/false]")
        show_share_ration = input(f"Do you want to show your total share ration? [true/false]")
        show_total_uploaded = input(f"Do you want to show how much you uploaded (in total)? [true/false")
        show_total_downloaded = input(f"Do you want to show how much you downloaded (in total)? [true/false]")
        show_upload_speed = input(f"Do you want to show your current upload speed? [true/false]")
        show_download_speed = input(f"Do you want to show your current download speed? [true/false]")

        self.conf.set("Configuration", "show_downloading", show_downloading)
        self.conf.set("Configuration", "show_uploading", show_uploading)
        self.conf.set("Configuration", "show_seeding", show_seeding)
        self.conf.set("Configuration", "show_share_ration", show_share_ration)
        self.conf.set("Configuration", "show_total_uploaded_gb", show_total_uploaded)
        self.conf.set("Configuration", "show_total_downloaded_gb", show_total_downloaded)
        self.conf.set("Configuration", "show_upload_speed", show_upload_speed)
        self.conf.set("Configuration", "show_download_speed", show_download_speed)

        with open("config.ini", "w") as conf: #type: TextIOWrapper
            self.conf.write(conf)

    def load_configuration(self):
        self.conf = ConfigParser()
        self.conf.read("config.ini")

        self.username = self.conf["Setup"]["username"]
        self.password = self.conf["Setup"]["password"]
        self.host = self.conf["Setup"]["host"]
        self.port = self.conf["Setup"]["port"]

        self.show_downloading = self.conf["Configuration"]["show_downloading"]
        self.show_uploading = self.conf["Configuration"]["show_uploading"]
        self.show_seeding = self.conf["Configuration"]["show_seeding"]
        self.show_share_ratio = self.conf["Configuration"]["show_share_ratio"]
        self.show_total_uploaded_gb = self.conf["Configuration"]["show_total_uploaded_gb"]
        self.show_total_downloaded_gb = self.conf["Configuration"]["show_total_downloaded_gb"]
        self.show_download_speed = self.conf["Configuration"]["show_download_speed"]
        self.show_upload_speed = self.conf["Configuration"]["show_upload_speed"]


        self.client = Client(host=self.host, port=self.port, username=self.username, password=self.password)
        self.client.auth_log_in()

    def start(self):
        while True:
            qb = self.client
            app_info = qb.app_version()
            transfer_info = qb.transfer_info()
            torrents_info = qb.torrents_info()

            # Initialize counters and totals
            downloading_count = 0
            uploading_count = 0
            seeding_count = 0
            total_uploaded = 0
            total_downloaded = 0
            total_share_ratio = 0
            torrents_with_ratio = 0

            for torrent in torrents_info:
                # Count torrents by state
                if torrent.state == 'downloading':
                    downloading_count += 1
                elif torrent.state == 'uploading':
                    uploading_count += 1
                elif torrent.state == 'stalledUP':
                    seeding_count += 1

                total_uploaded += torrent.uploaded
                total_downloaded += torrent.downloaded

                if torrent.downloaded > 0:
                    total_share_ratio += torrent.ratio
                    torrents_with_ratio += 1

            # Calculate averages and conversions
            total_uploaded_gb = total_uploaded / (1024 ** 3)  # Convert to GB
            total_downloaded_gb = total_downloaded / (1024 ** 3)  # Convert to GB
            average_share_ratio = total_share_ratio / torrents_with_ratio if torrents_with_ratio else 0
            total_share_ratio = total_uploaded_gb / total_downloaded_gb

            # Current upload/download speeds in MB/s
            upload_speed = transfer_info['up_info_speed'] / (1024 ** 2)  # Convert to MB/s
            download_speed = transfer_info['dl_info_speed'] / (1024 ** 2)  # Convert to MB/s

            # Print information
            print(f"qBittorrent Version: {app_info}")
            print(f"Torrents Downloading: {downloading_count}")
            print(f"Torrents Uploading: {uploading_count}")
            print(f"Torrents Seeding: {seeding_count}")
            print(f"Average Share Ratio: {total_share_ratio:.2f}")
            print(f"Total Uploaded: {total_uploaded_gb:.2f} GB")
            print(f"Total Downloaded: {total_downloaded_gb:.2f} GB")
            print(f"Current Upload Speed: {upload_speed:.2f} MB/s")
            print(f"Current Download Speed: {download_speed:.2f} MB/s")

            display_data = []

            if self.show_downloading == "true":
                display_data.append(f"Downloading: {downloading_count}")
            if self.show_uploading == "true":
                display_data.append(f"Uploading: {uploading_count}")
            if self.show_seeding == "true":
                display_data.append(f"Seeding: {seeding_count}")
            if self.show_share_ratio == "true":
                display_data.append(f"Ratio: {total_share_ratio:.2f}")
            if self.show_total_uploaded_gb == "true":
                display_data.append(f"Uploaded: {total_uploaded_gb:.2f} GB")
            if self.show_total_downloaded_gb == "true":
                display_data.append(f"Downloaded: {total_downloaded_gb:.2f} GB")
            if self.show_upload_speed == "true":
                display_data.append(f"USpeed: {upload_speed:.2f} MB/s")
            if self.show_download_speed == "true":
                display_data.append(f"DLSpeed: {download_speed:.2f} MB/s")

            # Split display_data into details and state
            details_data = " | ".join(display_data[:2])  # First two items
            state_data = " | ".join(display_data[2:]) if len(display_data) > 2 else "No additional info"

            # Update the Discord Rich Presence
            self.rpc.update(
                details = details_data,
                state=state_data,
                large_image="qbittorrent",
                large_text=app_info
            )
            time.sleep(5)

    def menu(self):
        options = input(f"""
1) Start
2) Settings
3) Credits

99) Exit

""")

        if options == "1":
            self.start()

        elif options == "2":
            self.settings()

        elif options == "3":
            self.credits()

        elif options == "99":
            exit(0)


    def settings(self):
        options = input(f"""
1) Change Server configuration
2) Change Discord configuration
3) Back""")

        if options == "1":
            self.setup_connection()

        elif options == "2":
            self.setup_discord_configuration()

        elif options == "3":
            self.menu()

    @staticmethod
    def credits():
        input(f"""

qBittorrent Discord Integration

- Developed by EchterAlsFake (Johannes Habel)
- https://github.com/EchterAlsFake/qBittorrent_Discord

Licensed under the GPL License (See https://www.gnu.org/licenses/gpl-3.0.en.html)

This project uses the following libraries:

- qBittorrent API: https://github.com/rmartin16/qbittorrent-api  (Licensed under the MIT License)
- pypresence     : https://github.com/qwertyquerty/pypresence    (Licensed under the MIT License)
- colorama       : https://github.com/tartley/colorama           (Licensed under BSD-3 Clause License)


Press any key to continue...""")


if __name__ == "__main__":
    QBittorrentDiscord()
