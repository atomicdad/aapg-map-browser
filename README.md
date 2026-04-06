# AAPG Map Browser

<p align="center">
  <img src="/.github/aapg_map_browser.png" width="500"/>
</p>

# Overview

The in-game map browser for America's Army Proving Grounds is horribly inconvenient. The list view is too small and offers no search/favorites/filtering. (hopefully in the next update) This tool aims to solve these shortcomings.

*Note: This tool is primarily intended for server admins, but also includes game commands that do not require admin. For example, all installed maps can be listed and opened locally from the tool.*

AAPG Map Browser is a window that runs alongside the game. It interacts with the game via the in-game console. Quite simply, for every submitted command, it focuses the game window, opens the console, types the chosen command, and presses enter. It does not tamper with game memory in any way. All commands sent to the game console are commands that could be typed by you. This just makes it faster and convenient.

# Setup

Windows:

 1. Download the latest release [here](https://github.com/atomicdad/aapg-map-browser/releases) and unzip it where you would like to
   keep the application.


 2. Run "AAPGMapBrowser.exe".

# Usage

The application is fairly straight-forward. The dropdown in the upper left is the currently selected map list. You can create a new one under the 'File' menu with 'New', create a copy of the current list with 'Save As', or keep 'Default' and overwrite it. This allows for creating lists for multiple servers where available maps may differ.

### Creating Map Lists:

If you would like to create your own map list, a couple of paths need to be set in 'Settings' under 'Folder Paths'. The first is the path to 'AAClient.log'. This is used to extract map names for a server for which you have admin access. The second is 'AA Workshop Content'. This is the folder that contains all of your locally downloaded Steam Workshop maps.

*Note: If you are a server admin and would like to create a list of maps for your server, understand that this software cannot see your admin password, nor will it ever ask for it. Logging in as admin on a server merely dumps the full list of maps on the server to AAClient.log. This software parses that file and stores the list.*

### Server Map Lists:

Open the game, join your server, login as admin, wait 10-15 seconds, and then close the game. If done properly, the game server will have sent a list of all available maps to your AAClient.log. If the AACLient.log path has been set correctly (as described above), navigate to 'Map List' -> 'Get Server Maps'. This will refresh the currently selected map list with all the available maps for your server. You can save the list with 'File' -> 'Save'. This doesn't need to be done again until the maps on the server have changed.

### Local Map Lists:

If the workshop content path has been set correctly (as described above), navigate to 'Map List' -> 'Get Local Maps'. This will refresh the currently selected map list with all the available maps on your computer. You can save the list with 'File' -> 'Save'.

### Map List Options:

Clean names removes the unique identifier number Steam uses on the map files to make it easier to read. Images enabled thumbnails in the list view and a larger preview image on hover.

### Adding Map Images:

The application will search for .jpg images at the launch of the application. If it finds them it will resize and convert the image to a .webp, create a .webp thumbnail, and then delete the original .jpg.

Locate a map without an image in the Map Browser. Open the game and take a Steam screenshot of the map with F12. Open Steam's screenshot viewer, right-click on the image, and click "Show on disk". This will open Windows Explorer with the screenshot selected. Copy or move it to the images folder in the AAPG Map Browser folder.

Rename the screenshot with the map file name. You can easily get the map name by right-clicking the map in the map browser and selecting "Copy Filename".

For example:
   20260403190737_1.jpg -> flo_101stvilla$76561197971401004_ex.jpg

Restart the map browser and the image should load.

*Note: Avoid starting/restarting the map browser before you have renamed any loose .jpgs in the images folder. They will disappear and be converted to .webp files with the wrong filename. You will have to find them to correct the filename.*

### Map Filters:

Map Filters excludes maps from the currently selected list that do not meet the selected criteria. Pick Random Map randomly highlights a map from the current list. It does not submit anything to the game.

Favorites can be toggled by right-clicking on a map in the list view. These can then be filtered with the Favorites filter. Favorites are currently global. Your saved favorites will appear for any selected map list.

### Game Commands:

Game Commands are used to send commands to the in-game console. The Vote section does not require admin and will work without it if the server allows it. Admin commands obviously require logging in as admin in game prior to submission (otherwise they will fail silently). The Open Map option under Local will open a map locally (offline) on the client.

*Note: After logging in as admin it may take 10-15 seconds before the server enumerates the available maps to the game. An attempted map change before this happens will fail. Also, it is unconfirmed but possible that a map change command submitted just as the map change countdown completes may result in a server crash or unjoinable state. This has been experienced once, but it may have been a coincidence. Try to submit a map change before the timer gets below 1.*

## Disclaimer

Releases are compiled into native machine executables with pyinstaller. Apparently pyinstaller binaries are notorious for being flagged as malware by some antivirus/malware scanners. These are false positives. If one wants to be extremely cautious, they should download the repository and run the python files directly or build the pyinstaller executables from scratch. Pyinstaller commands are in the header comment in 'AAPG Map Browser.py'. I, the author of this project, have never knowingly included anything malicious in the project files or releases.

## License

MIT License

Copyright (c) 2026 atomicdad

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
