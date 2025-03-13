import webbrowser
import re
import winshell
import subprocess
from datetime import datetime, timedelta, timezone
from pygame import mixer
from mutagen.id3 import ID3
from mutagen.flac import FLAC
import os
from chat.config import Config
from utils.startup import start_calendar_service
from data.settings import load_secure_json
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
import warnings
import requests
import json
from types import NoneType
from typing import Union

warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

data = load_secure_json("data/settings.data")["system_settings"]

WEB_PAGE_LIST = data["directly_accessed_links"]
APP_LIST = data["standard_program_paths"]
PROCESS_LIST = data["windows_default_processes"]
FOLDER_LIST = data["windows_default_folders"]
MUSIC_DIRECTORY = data["default_music_directory"]

GOOGLE_CALENDAR_SERVICE = start_calendar_service()

class ZeroCommands:

  def __init__(self):
     
    self.headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_INFERENCE_TOKEN}"}
    self.song_info = (None, None)

  def open_page(self, user_input : str, webpage_list : dict[str, str] = WEB_PAGE_LIST) -> None:

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

  def empty_recycle_bin(self) -> None:

      """
      Cleans up recycle bin

      Parameters: 
      None

      Returned value:
      None
      """

      winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)

  def open_app(self, name : str) -> None:
     """
     Opens an external program from a given list.

     Parameters:
     name (str): the name of the program to be opened

     Returns:
     None
     """

     try:
        subprocess.Popen([APP_LIST[name.split(" ")[-1].lower().replace("\"", "")], '-new-tab'])
     except Exception as e:
        raise FileNotFoundError("The executable program was not found.")

  def close_app(self, name : str) -> None:
     
     """
     Checks if the given program is open and closes it.

     Parameters:
     name (str): the name of the program to be closed

     Returns:
     None
     """

     try:
        process = PROCESS_LIST[name.split(" ")[-1].lower().replace("\"", "")]
        active_process_list = subprocess.check_output(['wmic', 'process', 'list', 'brief'])

        if process in str(active_process_list):
           os.system(f"taskkill /IM {process}")
        else:
           raise FileNotFoundError("Could not find program.")

     except Exception as e:
        print(e)
        raise FileNotFoundError("The executable program is already closed or does not exist.")

  def open_folder(self, folder_name : str) -> None:
     
     """
     Opens a folder from a given list.

     Parameters:
     folder_name (str): the name of the folder to be opened

     Returns:
     None
     """

     try:
      folder_path = FOLDER_LIST[folder_name.split(" ")[-1].lower().replace("\"", "")]

      if os.name == "nt":
         os.startfile(folder_path)
      elif os.name == "posix":
         subprocess.run(["open", folder_path])

     except NameError as ne:
        raise NameError("Could not open folder. It either doesn't exist or could not be found.")


  def start_playlist(self, source : str = "default") -> None:

      """
      Plays the songs from a given playlist. If no specific playlist is given, it plays the songs
      from the default location.

      Parameters:

      source : a key referencing the location from where songs will be played

      Returned value:
      None
      """

      if "default" in source or "(playlist)" in source:
        playlist_source = MUSIC_DIRECTORY
      else:
        ref_name = (re.findall(r"\((.*?)\)", source)[-1])
        playlist_source = data["playlist_directories"][ref_name]

      playlist = [song for song in os.listdir(playlist_source) if song.endswith("mp3") or song.endswith("flac")]
      mixer.init()
      for song in playlist:
          mixer.music.load(os.path.join(playlist_source, song))

          if song.endswith("mp3"):
              audio = ID3(os.path.join(playlist_source, song))
              title_info = audio["TIT2"].text[0]
              artist_info = audio["TPE1"].text[0]
          elif song.endswith("flac"):
              audio = FLAC(os.path.join(playlist_source, song))
              title_info = audio.get("title", ["Unknown"])[0]
              artist_info = audio.get("artist", ["Unknown"])[0]

          self.song_info = (title_info, artist_info)

          mixer.music.play()

  def stop_playlist(self, ) -> None:

      """
      Stops the songs from playing in a given playlist.

      Parameters:
      None

      Returned value:
      None
      """

      mixer.music.stop()
      mixer.quit()

  def play_song(self, name : str, artist : str, playlist : str = "default") -> None:
      """
      Searchs for a song in a playlist and play it if found, else raises an error.

      Parameters:
        name (str): name of the song
        artist (str): name of the song's artist
        playlist (str): name of the playlist song is located

      Returns:
        None
      """

      song_path = None

      # select playlist
      if playlist in ["playlist", "default", "", "None"]:
        source = MUSIC_DIRECTORY
      else:
        source = data["playlist_directories"][playlist]

      # look for audio file
      for song in os.listdir(source):
        
        if song.endswith("mp3"):
          audio = ID3(os.path.join(source, song))
          title_info = audio["TIT2"].text[0]
          artist_info = audio["TPE1"].text[0]
        elif song.endswith("flac"):
            audio = FLAC(os.path.join(source, song))
            title_info = audio.get("title", ["Unknown"])[0]
            artist_info = audio.get("artist", ["Unknown"])[0]

        if name in title_info and artist in artist_info:
            song_path = os.path.join(source, song)
            break

      if song_path is None:
        raise ValueError("Sorry, but I could not find the required song. Please provide a playlist name, if you didn't, or try with another playlist.")

      # check if mixer is initialised
      if mixer.get_init() is None:
        mixer.init()

      # checks if there is any song being played by mixer; if found, the music stops
      if mixer.music.get_busy():
        mixer.music.stop()

      # plays song
      mixer.music.load(song_path)
      self.song_info = (title_info, artist_info)
      mixer.music.play()

  def get_song_info(self) -> str:
     """
     Gets track name and artist of a song, if it's being played by pygame.mixer.

     Parameters:
      None

     Returns:
      None
     """

     # returns message indicating no song is being played
     if mixer.get_init() is None:
        return "No song is being played at the moment."
     if not mixer.music.get_busy():
        return "No song is being played at the moment."
     
     return f"The song being played is {self.song_info[0]} by {self.song_info[1]}"


  def get_next_events(self, service, freq: str = "day", top: Union[int, NoneType] = 30) -> str:

    """
    Gets a list of next events on Google Calendar using Google Calendar API, and return a text with its info structured accordingly.

    Parameters:
      service: the Google Calendar API service object
      freq (str): a keyword indicating the time range of the events to be returned. Its values are:
              'day': returns the events in the current day
              'week': returns the events in the next 7 days
      top (int): the number of incoming events to be returned

    Returns:
      str: the message containing the incoming events
    """

    message = ""

    try:
      now = datetime.now(timezone.utc).isoformat()
      if freq == "week":
        time_max = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
      else:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        tomorrow = tomorrow - timedelta(hours=datetime.now().hour)
        tomorrow = tomorrow - timedelta(minutes=datetime.now().minute)
        time_max = tomorrow.isoformat()

      query_params = {
          "calendarId": "primary",
          "timeMin": now,
          "singleEvents": True,
          "orderBy": "startTime"
      }

      if top is not None:
          query_params["maxResults"] = top
      else:
          query_params["timeMax"] = time_max

      events_result = service.events().list(**query_params).execute()

      events = events_result.get("items", [])

      if not events:
        message += "No upcoming events found."

      # Prints the start and name of the incoming events
      else:
        period = "today" if freq == "day" else "the next 7 days"
        message += (f"Here are the upcoming events for {period}:\n" if top is None else f"Here are the next {top} events from now:\n")
        for event in events:
          start = event["start"].get("dateTime", event["start"].get("date"))
          event_date = [start[:start.index("T")], start[start.index("T") + 1:]]
          event_date[0] = datetime.strptime(event_date[0], "%Y-%m-%d").strftime("%d %B %Y")
          event_date[1] = event_date[1][:event_date[1].index("-")]
          message += (f"On {event_date[0]}, at {event_date[1]}: {event['summary']}\n" if freq != "day" or top is not None else f"At {event_date[1]}: {event['summary']}\n")
          #print(start, event["summary"])
      
      return message

    except HttpError as error:
      print(f"An error occurred: {error}")
      return "Could not retrieve events. Please try again later."
    except ValueError as error:
      print(f"An error occurred: {error}")
      return "Sorry, I couldn't understand. Please say it again."

  def _get_event_info(self, content: str) -> dict:
    """
    Auxiliary function to set_new_event. It gets the arguments identified by the AI and convert them to a structured
    format to be sent to a Google Calendar API request.

    Parameters:
      content (str): the arguments identified by the AI. It always assumes the following format:
        (arg1, arg2, arg3, arg4)
      
    Returns
      dict: a dictionary containing the structured info to be sent to API request
    """



    try:
      filtered_content = (re.findall(r"\((.*?)\)", content)[-1]).split("\",")
      if len(filtered_content) != 4:
        raise ValueError("Not enough amount of information was retrieved.")
      filtered_content = [item.replace('"', "") for item in filtered_content]
      
      # get starting date
      prompt = f"""<|im_start|>system
      You are an AI assistant. Your task is to get a date in the format
      "YYYY-mm-dd HH:MM:SS" which satisfies the user input, having as reference the following date:
      {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<|im_end|>
      <|im_start|>user
      {filtered_content[1].strip()}<|im_end|>
      <|im_start|>assistant
      """

      payload = {
          "inputs" : prompt
      }
      
      response = requests.post(Config.API_URL_INSTRUCT, headers=self.headers, json=payload, verify=False)
      if response.status_code == 200:
          bot_output = response.json()[0]['generated_text'].split("<|im_start|>assistant")[-1]
          starting_date = re.findall(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}", bot_output)[-1]
          starting_date = datetime.strptime(starting_date, "%Y-%m-%d %H:%M:%S")
      # get end date

      if "minute" in filtered_content[2]:
        timestamp = 1 if "a" in filtered_content[2] else int(''.join(re.findall(r'\d', filtered_content[2])))
      elif "hour" in filtered_content[2]:
        timestamp = 1 if "an" in filtered_content[2] else 60 * int(''.join(re.findall(r'\d', filtered_content[2])))
      
      end_date = (starting_date + timedelta(minutes=timestamp)).isoformat()
      starting_date = starting_date.isoformat()
      
      # get reminder

      if "minute" in filtered_content[-1]:
        timestamp = 1 if "a" in filtered_content[-1] else int(''.join(re.findall(r'\d', filtered_content[-1])))
      elif "hour" in filtered_content[-1]:
        timestamp = 1 if "an" in filtered_content[-1] else 60 * int(''.join(re.findall(r'\d', filtered_content[-1])))

      return {
          'summary': filtered_content[0].strip(),
          'location': 'Unknown',
          'description': 'Event generated through Google Calendar API',
          'start': {
              'dateTime': starting_date,
              'timeZone': 'America/Sao_Paulo',
          },
          'end': {
              'dateTime': end_date,
              'timeZone': 'America/Sao_Paulo',
          },
          'attendees': [
              {'email': 'chrisPPS80@gmail.com'},
          ],
          'reminders': {
              'useDefault': False,
              'overrides': [
                  {'method': 'popup', 'minutes': timestamp},
              ],
          },
      }

    except ValueError as ve:
      print(str(ve))
      return {"error": "Couldn't get the required info to create the event. Please try again."}
    except Exception as e:
      print(str(e))
      return {"error": "Unexpected error caught. Please try again later."}

  def set_new_event(self, service, event_info:dict) -> str:

    """
    Create a new event on Google Calendar using Google Calendar API, and return a text with confirmation.

    Parameters:
      service: the Google Calendar API service object
      event_info (dict): a dictionary containing information about the event to be added

    Returns:
      str: the message confirming the event creation
    """

    try:

      if "error" in list(event_info.keys()):
        return event_info["error"]

      event = service.events().insert(calendarId='primary', body=event_info).execute()
      print(f"Event created: {event.get('htmlLink')}")
      return "A new event was added to your Google Calendar successfully."

    except HttpError as error:
      print(f"An error occurred: {error}")
      return "Could not create event. Please try again later."


  def activate_command(self, user_input : str) -> tuple[str, str]:

      """
      Triggers one of the predefined commands in Zero Assistant.

      Parameters:

      user_input : The given user input

      Returned value:
      A tuple of the format (str, str), containing both bot answer and command type to start a specific action
      """

      # sub functions

      prompt = f"""<|im_start|>system
      You are an AI assistant. Analyze the user's input and determine which function to call: 
      - "open_page(page)" to open a web page.
      - "open_app(name)" to open a program.
      - "close_app(name)" to close a program.
      - "open_folder(folder_name)" to open a folder.
      - "empty_recycle_bin()" to clear the recycle bin.
      - "get_current_time()" to get the current time and date.
      - "get_next_events(period, number_of_events)" to get the next events in the calendar over a period of time.
      - "set_new_event(name, start_date, duration, reminder)" to set a new task, as well as its start date, duration and reminder.
      - "stop_playlist()" to stop current playlist.
      - "start_playlist(playlist)" to start a playlist.
      - "play_song(name, artist, playlist)" to find a song in a playlist by its name and artist and play it.
      - "get_song_info()" to get the info of song being played.<|im_end|>
      <|im_start|>user
      {user_input}<|im_end|>
      <|im_start|>assistant
      """
      bot_output = ""

      headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_INFERENCE_TOKEN}"}

      payload = {
          "inputs" : prompt
      }

      response = requests.post(Config.API_URL_INSTRUCT, headers=headers, json=payload, verify=False)
      if response.status_code == 200:
          bot_output = response.json()[0]['generated_text'].split("<|im_start|>assistant")[-1]

      message = ""
      command = bot_output

      if "open_page" in bot_output:
          message = "Right, I'm opening the page right now. If it doesn't show up, it either means the page doesn't exist or that it can't be reached."
      elif "open_app" in bot_output:
          message = "Opening program..."
      elif "close_app" in bot_output:
          message = "Closing program..."
      elif "open_folder" in bot_output:
          message = "Opening folder..."
      elif "empty_recycle_bin" in bot_output:
          message = "Okay, I'm cleaning up the recycle bin right now. It might take a few minutes, so please be patient."
      elif "get_current_time" in bot_output:
          current_time = datetime.today().strftime("%H:%M:%S")
          current_date = datetime.today().strftime("%d-%m-%Y")
          message = f"It's {current_time} of the day {current_date}"
      elif "get_next_events" in bot_output:
          freq = "week" if "week" in bot_output else "day"
          top = ''.join(re.findall(r'\d', bot_output))
          top = int(top) if len(top) >= 1 else None
          message = self.get_next_events(GOOGLE_CALENDAR_SERVICE, freq=freq, top=top)
      elif "set_new_event" in bot_output:
          event_info = self._get_event_info(bot_output)
          message = self.set_new_event(GOOGLE_CALENDAR_SERVICE, event_info)
      elif "stop_playlist" in bot_output:
          message = "Playlist stopped."
      elif "start_playlist" in bot_output:
          message = "Starting playlist..."
      elif "play_song" in bot_output:
          message = "Playing selected song..."
      elif "get_song_info" in bot_output:
          message = self.get_song_info()
      else:
          message = "Sorry, but I cannot execute this command."

      print("Message:", message)
      
      return message, command