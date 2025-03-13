import speech_recognition as sr
from gtts import gTTS
import os
import playsound


def get_audio() -> str:

    """
    Gets audio from microphone and converts to text (STT)

    Parameters:
    None

    Returned value:
    String containing the detected speech
    """

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        user_speech = ""
        try:
            user_speech = r.recognize_google(audio)
            print(user_speech)
        except sr.UnknownValueError:
            return "Bot: Sorry, I did not get that."
        except sr.RequestError:
            return "Bot: Sorry, the service is not available"
    return user_speech.lower()

#speak converted audio to text
def speak(text) -> None:

    """
    Gets a text and converts it to an audio file (TTS)

    Parameters:

    text : text to be converted to audio

    Returned value:
    None
    """

    tts = gTTS(text=text, lang='en')
    filename = "data/voice.mp3"
    try:
        os.remove(filename)
    except OSError:
        pass
    tts.save(filename)
    try:
        playsound.playsound(os.path.join(os.getcwd(), filename))
    except playsound.PlaysoundException as pe:
        print(f"Unexpected error caught: {pe}")
        playsound.playsound(os.path.join(os.getcwd(), filename)) # retry playing audio if it fails to read it


# testing TTS and STT
if __name__ == "__main__":

    keep = True

    while keep:
        option = input("Select an option:\n1 - TTS\n2 - STT\n0 - Exit\nAnswer: ")

        if option == "1":
            text = input("Type something...: ")
            speak(text)
        elif option == "2":
            text = get_audio()
            print(f"Extracted text: {text}")
        elif option == "0":
            keep = False
        else:
            print("Invalid option")
