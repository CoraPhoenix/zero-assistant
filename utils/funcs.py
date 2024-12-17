import webbrowser
import re
import winshell
from datetime import datetime
from pygame import mixer
import os

WEB_PAGE_LIST = {"google" : "https://www.google.com",
                 "youtube": "https://www.youtube.com"}

MUSIC_DIRECTORY = "C:\\Users\\chris\\Videos\\Any Video Converter\\MP3"

def open_page(user_input : str, webpage_list : dict[str, str] = WEB_PAGE_LIST) -> None:

    """
    Opens a page from a given list.

    Parameters:

    user_input : The user input containing the page to visit

    Returned value:
    None
    """

    for webpage in webpage_list.keys():
        if webpage in user_input.lower():
            webbrowser.get().open(webpage_list[webpage])

def empty_recycle_bin() -> None:

    """
    Cleans up recycle bin

    Parameters: 
    None

    Returned value:
    None
    """

    winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)

def start_playlist(source : str = MUSIC_DIRECTORY) -> None:

    """
    Plays the songs from a given playlist. If no specific playlist is given, it plays the songs
    from the default location.

    Parameters:

    source : the location from where songs will be played

    Returned value:
    None
    """

    playlist = [song for song in os.listdir(source) if song.endswith("mp3") or song.endswith("flac")]
    mixer.init()
    for song in playlist:
        mixer.music.load(os.path.join(source, song))
        mixer.music.play()

def stop_playlist() -> None:

    """
    Stops the songs from playing in a given playlist.

    Parameters:
    None

    Returned value:
    None
    """

    mixer.music.stop()
    mixer.quit()


def activate_command(user_input : str) -> tuple[str, str]:

    """
    Triggers one of the predefined commands in Zero Assistant.

    Parameters:

    user_input : The given user input

    Returned value:
    A tuple of the format (str, str), containing both bot answer and command type to start a specific action
    """

    message = ""
    command = ""

    if (re.search("Zero,.*(?<!not)\sopen", user_input) and re.search("Zero,.*(?<!don\'t)\sopen", user_input)):
        message = "Right, I'm opening the page right now. If it doesn't show up, it either means the page doesn't exist or that it can't be reached."
        command = "open_page"
    elif re.search("Zero,.*(?<!not)\s(clean|empty)\srecycle", user_input) and re.search("Zero,.*(?<!don\'t)\s(clean|empty)\srecycle", user_input):
        message = "Okay, I'm cleaning up the recycle bin right now. It might take a few minutes, so please be patient."
        command = "empty_recycle_bin"
    elif ("what time" in user_input) or (re.search("Zero,.*(?<!don\'t)\stell.*time", user_input) and re.search("Zero,.*(?<!not)\stell.*time", user_input)):
        current_time = datetime.today().strftime("%H:%M:%S")
        current_date = datetime.today().strftime("%d-%m-%Y")
        message = f"It's {current_time} of the day {current_date}"
        command = "current_time_date"
    elif re.search("Zero,.*(?<!not)\sstop", user_input) and re.search("Zero,.*(?<!don\'t)\sstop", user_input):
        message = "Stopping playlist..."
        command = "stop_playlist"
    elif re.search("Zero,.*(?<!not)\splay", user_input) and re.search("Zero,.*(?<!don\'t)\splay", user_input):
        message = "Starting playlist..."
        command = "start_playlist"
    else:
        message = "Sorry, but I cannot execute this command."
        command = "error"
    
    return message, command