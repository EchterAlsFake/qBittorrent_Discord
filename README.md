qBittorrent Discord RPC Integration
====================================

Overview
--------
This Python script integrates qBittorrent with Discord Rich Presence, displaying the number of torrents being uploaded or downloaded, and the version of qBittorrent being used.

Table of Contents
-----------------

- [Setup and Configuration](#setup-and-configuration)
- [Running the Script](#running-the-script)
- [Note](#note)
- [Downloads](#downloads)
- [Credits](#credits)
- [License](#license)

Setup and Configuration
-----------------------
1. Install Required Libraries:
   - pypresence
   - colorama
   - qbittorrentapi

   Use the command: `pip install pypresence colorama qbittorrent-api`


2. Configure qBittorrent WebUI:
   - Enable WebUI in qBittorrent settings.
   - Note the host and port for the WebUI.

Running the Script
------------------
1. Run the script.
2. Enter the qBittorrent WebUI credentials.
   - If 'Bypass Authentication for localhost' is enabled, press Enter for username and password.
3. Enter the WebUI host and port (default: localhost and 8080).

The script will connect to Discord and qBittorrent and start displaying the Rich Presence.

Note
----
- The script updates Discord Rich Presence every 10 seconds.
- The provided GitHub link in the Discord status is optional and can be removed.

Downloads
---------

**Downloads for Windows and Linux can be found in the [releases]()**



# Credits

* [qBittorrent API](https://github.com/rmartin16/qbittorrent-api)
* [ChatGPT](https://chat.openai.com)

# License

Copyright (C) 2023 Johannes Habel
<br>Licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)

# Support

If you want more features or you have any feedback, please let me know in the Discussions.
<br>I don't care sooo much about this repo, so I'll be happy to hear your ideas :)


