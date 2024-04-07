import configparser
import sys
import time
import qbittorrentapi
import getpass

from pypresence import Presence
from colorama import *
from configparser import ConfigParser

z = f"{Fore.LIGHTGREEN_EX}[+]{Fore.RESET}"


class QBittorrentDiscord:
    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read("config.ini")
        self.check_configuration_file()
        self.application_id = "1176525076703744090"
        self.image = "qbittorrent"  # Image for the Discord Bot
        self.uploading = 0
        self.downloading = 0
        self.update_delay = None
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.qbt_client = None
        self.client = None

        self.conf.read("config.ini")
        self.discord()
        self.server_configuration()
        self.menu()

    def menu(self):
        options = input(f"""
1) Start
2) Settings
3) Credits
99) Exit
---------------->:""")

        if options == "1":
            self.start()

        elif options == "2":
            self.settings()

        elif options == "3":
            self.credits()

        elif options == "99":
            sys.exit(0)

    def check_configuration_file(self):
        sections = ["Server", "Discord"]
        options_server = ["host", "port", "username", "password", "authentication"]
        options_discord = ["show_uploads", "show_downloads", "update_delay"]

        try:
            for section in sections:
                if self.conf.has_section(section) is False:
                    self.write_configuration_file()

            for option in options_server:
                if self.conf.has_option(section="Server", option=option) is False:
                    self.write_configuration_file()

            for option in options_discord:
                if self.conf.has_option(section="Discord", option=option) is False:
                    self.write_configuration_file()

        except (configparser.NoSectionError, configparser.NoOptionError):
            self.write_configuration_file()

    @classmethod
    def write_configuration_file(cls):
        default = """[Server]
host = localhost
port = 8080
username = 
password = 
first_run = true

[Discord]
show_uploading = 1
show_downloading = 1
update_delay = 10"""

        with open("config.ini", "w") as config_file:
            config_file.write(default)

    def server_configuration(self):
        if self.conf.get("Server", "first_run") == "true":
            print(
                f"----------------------------{Fore.LIGHTYELLOW_EX}CONFIGURATION{Fore.RESET}"
                f"-------------------------------------")
            print(f"Please enter your credentials for the WebUI, you've configured in the qBittorrent Client.")

            print(f"""
{Fore.RED}Information:

{Fore.LIGHTCYAN_EX}If you have enabled 'Bypass Authentication for localhost' in the WebUI, just press enter when you 
get asked for Username and Password. {Fore.RESET}
            """)

            username = input(f"{z}Enter your username [Enter to skip authentication]: ")
            password = getpass.getpass("Enter your password [None]: ")
            host_input = input(f"{z}Enter webUI host [localhost]: ")
            port_input = input(f"{z}Enter webUI port [8080]: ")
            host = host_input if host_input else "localhost"
            port = port_input if port_input else "8080"

            self.conf.set("Server", "username", username)
            self.conf.set("Server", "password", password)
            self.conf.set("Server", "host", host)
            self.conf.set("Server", "port", port)
            self.conf.set("Server", "first_run", "false")
            self.conf.set("Discord", "update_delay", "10")
            self.update_delay = 10

            with open("config.ini", "w") as config:
                self.conf.write(config)
                print("Wrote to configuration file")

        else:
            host = self.conf.get("Server", "host")
            port = self.conf.get("Server", "port")
            username = self.conf.get("Server", "username")
            password = self.conf.get("Server", "password")
            self.update_delay = self.conf.get("Discord", "update_delay")

        conn_info = dict(
            host=host,
            port=port,
            username=username,
            password=password,
        )

        self.qbt_client = qbittorrentapi.Client(**conn_info)

        try:
            print(f"{z}Connecting to {host}:{port}...")
            self.qbt_client.auth_log_in()
            print(f"{z}Connected to {host}:{port}!")

        except qbittorrentapi.LoginFailed as e:
            print(f"Login failed: {e}, please check your credentials... Entering Settings")
            self.settings()

    def discord(self):
        print(f"{z}Connecting to Discord...")
        self.client = Presence(self.application_id)
        self.client.connect()
        print(f"{z}Connected to Discord :)")

    def start(self):

        while True:
            # retrieve and show all torrents
            for torrent in self.qbt_client.torrents_info():
                if torrent.state == qbittorrentapi.TorrentState.UPLOADING:
                    self.uploading += 1

                elif torrent.state == qbittorrentapi.TorrentState.DOWNLOADING:
                    self.downloading += 1

            if self.conf.get("Discord", "show_uploading") == "1":
                uploading = f"Uploading: {self.uploading}"

            else:
                uploading = None

            if self.conf.get("Discord", "show_downloading") == "1":
                downloading = f"Downloading: {self.downloading}"

            else:
                downloading = None

            print(f"Uploading (Seeding) : {self.uploading}")
            print(f"Downloading: {self.downloading}")

            self.client.update(details=f"qBittorrent: {self.qbt_client.app.version}", state=f"{uploading} | "
                                                                                            f"{downloading}",
                               large_image="qbittorrent",
                               buttons=[{"label": "Visit Project", "url":
                                   "https://github.com/EchterAlsFake/qbittorrent_Discord_RPC"}])  # can be removed

            time.sleep(int(self.update_delay))
            self.uploading = 0
            self.downloading = 0

    def settings(self):
        while True:
            options = input(f"""
1) Change the server configuration
2) Enable / Disable showing the amount of downloading torrents
3) Enable / Disable showing the amount of uploading torrents
4) Change update delay

99) Exit
""")

            try:
                if options == "1":
                    self.conf.set("Server", "first_run", "true")
                    print(
                        f"{z} Please restart the script. You will be prompted to enter the new server configuration...")

                elif options == "2":
                    if self.conf.get("Discord", "show_downloading") == "1":
                        self.conf.set("Discord", "show_downloading", "0")

                    elif self.conf.get("Discord", "show_downloading") == "0":
                        self.conf.set("Discord", "show_downloading", "1")

                elif options == "3":
                    if self.conf.get("Discord", "show_uploading") == "1":
                        self.conf.set("Discord", "show_uploading", "0")

                    elif self.conf.get("Discord", "show_uploading") == "0":
                        self.conf.set("Discord", "show_uploading", "1")

                elif options == "4":
                    delay = input(f"{z} Please enter the new delay -->: ")
                    self.conf.set("Discord", "update_delay", delay)

                elif options == "99":
                    self.menu()

            finally:
                with open("config.ini", "w") as config_file:
                    self.conf.write(config_file)

    @classmethod
    def credits(cls):
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
