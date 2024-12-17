# zero-assistant

This is a basic virtual assistant which you can interact with through text and voice. \
Ask Zero to perform some commands and chat with them.

## Requirements

To be able to use Zero, it's required to have:

- Python
- Hugging Face API token
- Installing the libraries in `requirements.txt` (This can be done through `pip install -r requirements.txt`)
- Installing or configuring a Tkinter theme (Go to `themes/readme.txt` for more details)

## Features

- It's capable to interact through text or audio and execute commands
- It uses Tkinter for GUI and [Qwen's Qwen2.5-Coder-32B-Instruct on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct) for chatting

## Layout

The layout is composed by an animated image which changes states depending on if Zero is speaking or not, boxes for the user and the assistant, and buttons which provide the options to send a text message or an audio message. It's also possible sending the message by pressing the Enter key.

Below is an example of a chat interaction:

**image 1**

To activate commands, you need to start your text or audio with "Zero," so that she can differentiate your intention.

Here is an example of command activation:

**image 2**

## Known Issues

Zero requires connection to the internet as both Hugging Face API and TTS/STT libraries need it. As a result, it cannot operate properly when you're offline. \
There are also a few limitations provided by using Tkinter which are expected to be fixed in the later updates.

## Next Steps

Here are a few steps planned to improve Zero's experience:

- Add more commands
- Personalise user experience
- Improve GUI
- Fix performance issues that might occur

## References

1. [Qwen2.5-Coder-32B-Instruct page on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct)
2. [thindil's tkBreeze repository](https://github.com/thindil/tkBreeze)

