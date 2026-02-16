AAPG Map Browser
-------

<p align="center">
  <img src="/.github/aapg_map_browser.png" width="500"/>
</p>

Overview
--------
The in-game map browser for America's Army Proving Grounds is horribly inconvenient. The list view is too small and offers no search/favorites/filtering. (hopefully in the next update) This tool aims to solve these shortcomings.

*Note: This tool is primarily intended for server admins, but also includes game commands that do not require admin. Currently, maps lists can only be generated with admin access to a server. Future versions may include the ability to generate a map list for all locally installed maps.*

AAPG Map Browser is a window that runs alongside the game. It interacts with the game via the in-game console. Quite simply, for every submitted command, it focuses the game window, opens the console, types the chosen command, and presses enter. When setup properly it has a list of every available map on a server. 

Setup
-------
Windows:

 1. Download the latest release and unzip it where you would like to
   keep the application.
 2. Open the game, connect to a server, login as admin. Wait 10-15 seconds. Close game.
 3. Open a Windows Terminal window and navigate to the unzipped folder.

    ```bash
    cd 'C:\Users\(Username)\Desktop\AAPG Map Browser v1.1\'
    ```
    
 5. Run MapsFileBuilder.exe with AAClient.log as the only argument.

    ```bash
    .\MapsFileBuilder.exe 'C:\Users\(Username)\Documents\My Games\America''s Army Proving Grounds\AAGame\Logs\AAClient.log'
    ```
 
 7. If successful, a maps.ini file will be created or overwritten in the root directory of the application.
 8. Open AAPG Map Browser.exe and verify that Maps Count matches the number of maps on the server.

Usage
-------
The application is fairly straight-forward once setup. Map Filters excludes maps from the list that do not meet the selected criteria. Clean names removes the unique identifier number Steam uses on the map files to make it easier to read. Pick Random Map randomly highlights a map from the current list. It does not submit anything to the game.

Favorites can be toggled by right-clicking on a map in the list view. These can then be filtered with the Favorites filter.

Game Commands are used to send commands to the in-game console. The Vote section does not require admin and will work without it if the server allows it. Admin commands obviously require logging in as admin prior to submission. The Open Map option under Local will open a map locally on the client.

*Note: After logging in as admin it may take 10-15 seconds before the server enumerates the available maps to the client. An attempted map change before this happens will fail. Also, it is unconfirmed but possible that a map change command submitted just as the map change countdown completes may result in a server crash or unjoinable state. This has been experienced once, but it may have been a coincidence. Try to submit a map change before the timer gets below 1.*

Disclaimer
-------
Releases are compiled into native machine executables with pyinstaller. Apparently pyinstaller binaries are notorious for being flagged as malware by some antivirus/malware scanners. These are false positives. If one wants to be extremely cautious, they should download the repository and run the python files directly or build the pyinstaller executables from scratch. Pyinstaller commands are in the header comment in 'AAPG Map Browser.py'. I, the author of this project, have never knowingly included anything malicious in the project files or releases.

License
-------
MIT License

Copyright (c) 2026 atomicdad

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
