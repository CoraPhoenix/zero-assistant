import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from mutagen.mp3 import MP3
from chat.chat import chat
from utils.startup import initial_load, start_calendar_service
from utils.funcs import *
from utils.speech import *
from config.config import ZeroConfig
import threading
import time
import warnings
import logging

warnings.filterwarnings("ignore")


class ZeroAssistant:

    """
    This class is used to invoke Zero Assistant interface and functions.

    Parameters:

        active_frame_durations (list) : holds the duration of each frame belonging to one of the animations (active state)
        active_frames (list) : holds a collection of frames related to one of the animations (active state)
        bot_answer (str) : the answer given by Zero, which is either set by a rule or generated through a langauge model
        command_caller (utils.funcs.ZeroCommands) : a ZeroCommands object which allows Zero to execute commands
        command_type (str) : the type of command given by the user; it selects the command to be triggered
        gif: the Tkinter widget holding the animation
        inactive (bool) : a flag which alternates the animation between inactive and active states
        inactive_frame_durations (list) : holds the duration of each frame belonging to one of the animations (inactive state)
        inactive_frames (list) : holds a collection of frames related to one of the animations (inactive state)
        initial_speech (str) : used to trigger Zero's TTS when the class is initialised
        speaking_duration (float) : the amount of time Zero will be speaking; used to indicate when the animation should change states
        user_input (str) : a given user input in the text box
        window (tkinter.Tk) : the Tkinter window object, which holds the GUI

    Public methods:

        run() -> None : opens the GUI and run all functions and commands required by Zero to operate

    """

    # ======================================= constructor ======================================= #
    def __init__(self):

        """
        ZeroAssistant class constructor. Used to initalise variables.

        Parameters:
            None

        Returned value:
            None
        """

        self.inactive = False
        self.user_input = ""
        self.command_type = ""
        self.command_caller = ZeroCommands()
        self.bot_answer = "Hello! My name is Zero, and I'm your personal assistant. Let's talk!"
        self.speaking_duration = 0
        self.initial_speech = True

        self.inactive_frames = []
        self.inactive_frame_durations = []

        self.active_frames = []
        self.active_frame_durations = []

        self.window = None
        self.gif = None

    # ===================================== public methods ====================================== #

    def run(self) -> None:

        """
        Opens the GUI and run all functions and commands required by Zero to operate.

        Parameters:
            None

        Returned value:
            None
        """

        self._open_window()
        self._load_gif()
        self._load_images()
        self._load_widgets()
        self._configure_window()
        self._window_mainloop()

    # ===================================== private methods ===================================== #

    def _open_window(self) -> None:

        """
        Creates and configures the theme to the GUI window.

        Parameters:
            None

        Returned value:
            None
        """

        # Creating window
        self.window = tk.Tk()
        self.window.title("Zero Assistant")
        self.window.geometry("800x600") # setting window default size
        logging.info("Zero Assistant window is created.")

        # Setting up theme
        style = ttk.Style(self.window)
        self.window.tk.call('source', ZeroConfig.TTK_THEME_FILE)
        style.theme_use(ZeroConfig.TTK_THEME)
        logging.info("Zero Assistant window is configured")

    def _load_gif_frames(self, animated_gif, frame_list, frame_durations) -> None:

        """
        Loads the gif frames into a list, and the duration of each frame to another.

        Parameters:
            animated_gif : the gif to be loaded.
            frame_list (list) : the list which will contain the frames.
            frame_durations (list) : the list to store the duration of each frame.

        Returned value:
            None
        """

        for frame in ImageSequence.Iterator(animated_gif):
            frame_list.append(ImageTk.PhotoImage(frame.copy()))
            frame_duration = animated_gif.info.get("duration", 100)
            frame_durations.append(frame_duration)

    def _load_gif(self) -> None:
        
        """
        Loads the animated images and display them on the GUI window.

        Parameters:
            None

        Returned value:
            None
        """

        # getting images
        inactive_gif = Image.open(ZeroConfig.INACTIVE_GIF_PATH)
        active_gif = Image.open(ZeroConfig.ACTIVE_GIF_PATH)

        # loading gif frames

        self._load_gif_frames(inactive_gif, self.inactive_frames, self.inactive_frame_durations)
        self._load_gif_frames(active_gif, self.active_frames, self.active_frame_durations)

        ## ----------------------- widget displaying ----------------------- ##

        # Animated gif
        if self.inactive:
            self.gif = ttk.Label(self.window, image = self.inactive_frames[0], anchor=tk.CENTER, background= ZeroConfig.BACKGROUND_COLOUR)
            self.gif.image = self.inactive_frames[0]
        else:
            self.gif = ttk.Label(self.window, image = self.active_frames[0], anchor=tk.CENTER, background= ZeroConfig.BACKGROUND_COLOUR)
            self.gif.image = self.active_frames[0]
        self.gif.grid(row=0, column=0, columnspan=4, sticky="nsew")
        logging.info("Animated GIF is loaded.")

    def _load_images(self) -> None:

        """
        Loads the non-animated images.

        Parameters:
            None

        Returned value:
            None
        """
        # Opening images
        mic = Image.open(ZeroConfig.MICROPHONE_PATH)
        send = Image.open(ZeroConfig.SEND_ICON_PATH)

        # Loading images to be added to buttons
        self.mic_img = ImageTk.PhotoImage(mic)
        self.send_img = ImageTk.PhotoImage(send)


    def _load_widgets(self) -> None:

        """
        Creates the GUI widgets and display them on the window.

        Parameters:
            None

        Returned value:
            None
        """

        # Zero label
        self.zero_label = ttk.Label(self.window, text="Zero: ", width = 6, background= ZeroConfig.BACKGROUND_COLOUR, font=ZeroConfig.LABEL_FONT)
        self.zero_label.grid(row=1, column=0, padx=10, pady=1)  # placed at first row and column

        # Zero text
        #self.zero_text = ttk.Label(self.window, text = self.bot_answer, background=ZeroConfig.ZERO_BG_COLOUR, font=ZeroConfig.ZERO_FONT)
        self.zero_text = tk.Text(self.window, height = 5, state=tk.DISABLED, background=ZeroConfig.ZERO_BG_COLOUR, font=ZeroConfig.ZERO_FONT)
        self.zero_text.grid(row=1, column=1, sticky="nsew", columnspan=2, padx=10)
        self.zero_text_scroll = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.zero_text.yview)
        self.zero_text_scroll.grid(row=1, column=3, sticky="nsew", padx=10)

        # User label
        self.user_label = ttk.Label(self.window, text="User: ", width = 6, background= ZeroConfig.BACKGROUND_COLOUR, font=ZeroConfig.LABEL_FONT)
        self.user_label.grid(row=2, column=0, padx=10, pady=1)  # placed at second row and first column

        # User text
        self.user_text = tk.Text(self.window, height = 3)
        self.user_text.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        # User buttons

        self.audio_button = ttk.Button(self.window, text="Speak", image=self.mic_img, command=self._tk_send_audio)
        self.audio_button.grid(row=2, column=2, padx=10, pady=10)

        self.text_button = ttk.Button(self.window, text="Send", image=self.send_img, command=self._send_input)
        self.text_button.grid(row=2, column=3, padx=10, pady=10)
        logging.info("Widgets loaded successfully.")
    
    def _configure_window(self) -> None:

        """
        Configures window and widgets parameters, as well as calling event functions.

        Parameters:
            None

        Returned value:
            None
        """

        ## --------------------- window configuration ---------------------- ##

        # binding the <Configure> event of the root window to dynamically adjust the widgets
        # Configure rows and columns of the root window
        self.window.rowconfigure(0, weight=1)  # The main content area (above the text boxes)
        self.window.rowconfigure(1, weight=0)  # Text box 1
        self.window.rowconfigure(2, weight=0)  # Text box 2
        self.window.columnconfigure(0, weight=0)
        self.window.columnconfigure(1, weight=1)  # Allow the text boxes to stretch horizontally
        self.window.configure(bg=ZeroConfig.BACKGROUND_COLOUR)

        self.zero_text.config(yscrollcommand=self.zero_text_scroll.set)
        self.zero_text.config(state=tk.NORMAL)
        self.zero_text.insert(tk.END, self.bot_answer)
        self.zero_text.config(state=tk.DISABLED)
        logging.info("Windows elements are set.")

        self.zero_text.bind("<Configure>", self._resize_text)
        self.user_text.bind("<Return>", self._on_pressing_enter)
        logging.info("Widget actions are set.")

    def _window_mainloop(self) -> None:

        """
        Calls the main functions, including the mainloop() function.

        Parameters:
            None

        Returned value:
            None
        """

        ## ------------------------- main functions ------------------------ ##

        self._animate(0)
        self._answer()
        self._reset_gif()
        self._tk_execute_command()

        ## ---------------------- main loop function ----------------------- ##

        self.window.mainloop()


    # ====================================== main functions ===================================== #

    def _animate(self, frame_index : int) -> None:

        """
        Updates the displayed frame of the animated GIF.

        Parameters:
            frame_index : the index of the animation's frame.

        Returned value:
            None
        """

        # updates inactive state GIF if Zero is not speaking
        if self.inactive:
            # update the image of the label to the current frame
            frame = self.inactive_frames[frame_index]
            self.gif.config(image=frame)
            self.gif.image = frame

            # Schedule the next frame update
            next_frame = (frame_index + 1) % len(self.inactive_frames)
            self.window.after(self.inactive_frame_durations[frame_index], self._animate, next_frame)

        else:
            frame = self.active_frames[frame_index]
            self.gif.config(image=frame)
            self.gif.image = frame

            next_frame = (frame_index + 1) % len(self.active_frames)
            self.window.after(self.active_frame_durations[frame_index], self._animate, next_frame)


    def _answer(self) -> None:

        """
        Gets Zero's response to user input, triggers TTS and assigns values to parameters to control
        animations. Also triggers Zero's inital TTS.

        Parameters:
            None

        Returned value:
            None
        """

        # executed when Zero is started
        if self.initial_speech:
            threading.Thread(target=self._perform_tts).start()
            self.initial_speech = False
            self.speaking_duration = (len(self.bot_answer) / 7)

        # When user types or say something, Zero will automatically answer
        if len(self.user_input) > 0:

            self.inactive = False

            if self.user_input.lower().lstrip().startswith("zero,"):
                self.bot_answer, self.command_type = self.command_caller.activate_command(self.user_input.lstrip())
            else: # Hugging Face bot is called when no command is sent
                self.bot_answer = chat(self.user_input)

            # sets Zero's text to display, user command, triggers TTS, set variables to control animations
            self.zero_text.config(state=tk.NORMAL)
            self.zero_text.delete("1.0", tk.END)
            self.zero_text.insert(tk.END, self.bot_answer.lstrip())
            self.zero_text.config(state=tk.DISABLED)
            #self.zero_text.config(text=self.bot_answer.lstrip())
            self.user_input = ""
            threading.Thread(target=self._perform_tts).start()
            self.speaking_duration = (len(self.bot_answer) / 7)
        
        self.window.after(1000, self._answer)
    

    def _resize_text(self, event) -> None:

        """
        Resizes the text to fit the grid cell.

        Parameters:
            event : the event which triggers the function.

        Returned value:
            None
        """
        new_width = event.width

        # update the label wrap length with the new window length
        self.zero_text.config(wrap=tk.WORD)
    
    # ===================================== helper functions ==================================== #

    def _execute_command(self) -> None:

        """
        Triggers an action depending on the selected command.

        Parameters:
            None

        Returned value:
            None
        """
        
        if "open_page" in self.command_type: # triggers opening web page action
            self.command_caller.open_page(self.command_type)
        elif "open_app" in self.command_type: # triggers opening program action
            try:
                app_name = re.findall(r"\((.*?)\)", self.command_type)[-1]
                self.command_caller.open_app(app_name)
            except Exception as e:
                logging.error(f"Error while running open_app(): {str(e)}")
                self.bot_answer = str(e)
                speak(str(e))
        elif "close_app" in self.command_type: # triggers closing program action
            try:
                command_input = self.command_type
                app_name = re.findall(r"\((.*?)\)", command_input)[-1]
                if app_name == "name":
                    app_name = re.findall(r"e:\s.*", command_input)[-1].replace("e: ", "")
                self.command_caller.close_app(app_name)
            except Exception as e:
                logging.error(f"Error while running close_app(): {str(e)}")
                self.bot_answer = str(e)
                speak(str(e))
        elif "open_folder" in self.command_type: # triggers opening folder action
            try:
                command_input = self.command_type
                folder_name = re.findall(r"\((.*?)\)", command_input)[-1]
                if folder_name == "folder_name":
                    folder_name = re.findall(r"e:\s.*", command_input)[-1].replace("e: ", "")
                self.command_caller.open_folder(folder_name)
            except Exception as e:
                logging.error(f"Error while running open_folder(): {str(e)}")
                self.bot_answer = str(e)
                speak(str(e))
        elif "empty_recycle_bin" in self.command_type: # triggers cleaning recycle bin action
            self.command_caller.empty_recycle_bin()
        elif "start_playlist" in self.command_type: # triggers playing songs from a playlist action
            if not "default" in self.command_type:
                self.command_caller.start_playlist(self.command_type)
            else:
                self.command_caller.start_playlist()
        elif "stop_playlist" in self.command_type: # triggers stopping mixer playlist action
            self.command_caller.stop_playlist()
        elif "play_song" in self.command_type: # triggers playing specific song action
            try:
                filtered_content = (re.findall(r"\((.*?)\)", self.command_type)[-1]).split("\",")
                if len(filtered_content) < 2 or len(filtered_content) > 3:
                    filtered_content = (re.findall(r"s\:(.*)\s", self.command_type)[-1]).split(",")
                    filtered_content = [item.split("`")[1].replace(" ", "").strip() for item in filtered_content]
                else:
                    filtered_content = [item.replace('"', "") for item in filtered_content]
                name = filtered_content[0].replace("name=", "").strip()
                artist = filtered_content[1].replace("artist=", "").strip()
                print(filtered_content)
                if len(filtered_content) == 3:
                    self.command_caller.play_song(name, artist, playlist=filtered_content[2].replace("playlist=", "").strip())
                else:
                    self.command_caller.play_song(name, artist)
            except ValueError as ve:
                self.bot_answer = str(ve)
                speak(str(ve))
            except Exception as e:
                logging.error(f"Error while running play_song(): {str(e)}")
                self.bot_answer = "Failed to play the song. Please try again."
                speak("Failed to play the song. Please try again.")


    def _on_pressing_enter(self, event) -> None:

        """
        Triggers the _send_input() function when user presses the Enter key.

        Parameters:
            None

        Returned value:
            None
        """

        self._send_input()

    def _perform_tts(self) -> None:

        """
        Triggers Zero's TTS.

        Parameters:
            None

        Returned value:
            None
        """

        speak(self.bot_answer)

    
    def _reset_gif(self) -> None:

        """
        Returns gif to inactive state when Zero stops speaking.

        Parameters:
            None

        Returned value:
            None
        """

        if (self.speaking_duration <= 0):
            self.inactive = True
        else:
            self.speaking_duration -= 1

        self.window.after(1000, self._reset_gif)
    
    def _send_audio(self) -> None:

        """
        Sends user audio input to Zero.

        Parameters:
            None

        Returned value:
            None
        """

        self.user_input = get_audio()

    def _send_input(self) -> None:

        """
        Sends user input to Zero and clears text box.

        Parameters:
            None

        Returned value:
            None
        """
        
        self.user_input = self.user_text.get("1.0",'end-1c')
        self.user_text.delete("1.0", tk.END)
    
    def _tk_execute_command(self) -> None:

        """
        Creates a thread to allow the execution of commands.

        Parameters:
            None

        Returned value:
            None
        """

        if len(self.command_type) > 0:
            threading.Thread(target=self._execute_command, daemon=True).start()
            self.command_type = "" # resets command_type so that a new thread is not open every second

        self.window.after(1000, self._tk_execute_command)
    
    def _tk_send_audio(self):

        """
        Creates a thread to allow the STT.

        Parameters:
            None

        Returned value:
            None
        """

        threading.Thread(target=self._send_audio, daemon=True).start()


# ===================================== main() function ===================================== #

def main() -> None:

    """
    Zero Assistant's main function, where chat is displayed into a Tkinter interface

    Parameters:
        None

    Returned value:
        None
    """

    try:

        initial_load() # tries to load HuggingFace inference model
        start_calendar_service() # tries to load Google Calendar API service

        zero = ZeroAssistant() # intialises Zero
        zero.run()

    except SystemExit as se:
        logging.error(se)
    except Exception as e:
        logging.error(f"Unexpected exception caught: {e}")


# ===================================== execution block ===================================== #

if __name__ == "__main__":

    # tkinter requires execution in the main thread so main function must be directly called
    main()

    logging.info("Execution finished")
    time.sleep(3)