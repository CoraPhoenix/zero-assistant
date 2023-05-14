import json
import pickle as pkl
import tkinter
from tkinter import *
from functions.input_extract import predict_class, get_response
from functions.context_commands import get_context, context_commands
from tensorflow.keras.models import load_model

# Comment it if no memory issues
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU') 
for device in physical_devices:
    tf.config.experimental.set_memory_growth(device, True)

# loading trained model
model = load_model('data\model.h5')

# loading file
intents = json.loads(open('data\intent_en.json').read())

base = Tk()
base.title("Chatbot")
base.geometry("400x500") 
base.resizable(width=FALSE, height=FALSE)


def chatbot_response(msg):
    """
        Bot answer
    """
    ints = predict_class(msg, model)
    res = get_response(ints, intents)
    return res, ints[0]['intent']

def send():
	"""
		Send a message
	"""
	msg = EntryBox.get("1.0", 'end-1c').strip()
	EntryBox.delete("0.0", END)

	if msg != '':
		Chat.config(state=NORMAL)
		Chat.insert(END, f"You: {msg}\n\n")
		Chat.config(foreground="#000000", font=("Arial", 12))

		response, intent = chatbot_response(msg)
		Chat.insert(END, f"Zero: {response}\n\n")
		
		# context_set based code comes here
		cmd_result = context_commands(msg, get_context(intent))
		if cmd_result != -1:
			Chat.insert(END, f" {cmd_result}\n\n")

		Chat.config(state=DISABLED)
		Chat.yview(END)

# Create chat window
Chat = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)
Chat.config(state=DISABLED)

# Create scrollbar to chat window
scrollbar = Scrollbar(base, command=Chat.yview)
Chat['yscrollcommand'] = scrollbar.set

# Create send a message button, associated to function send
SendButton = Button(base, font=("Verdana", 10, 'bold'), text="Send", width="12", height=2, bd=0, bg="#666", activebackground="#333", fg='#ffffff', command=send)

# Create text box
EntryBox = Text(base, bd=0, bg="white", width="29", height="2", font="Arial")

# Place all components on screen
scrollbar.place(x=376, y=6, height=386)
Chat.place(x=6, y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=50, width=260)
SendButton.place(x=6, y=401, height=50)


base.mainloop()