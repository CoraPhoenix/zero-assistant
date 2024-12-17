from chat.config import Config
import requests
import time

def _load_model(headers):

    initial_payload = {
        "inputs": "Welcome"
    }

    try:
        response = requests.post(Config.API_URL_INSTRUCT, headers=headers, json=initial_payload, verify=False)
        if response.status_code != 200 and "is currently loading" in response.text:
            print(f"Loading conversational model. It's going to take about {response.json()['estimated_time']} seconds")
            time.sleep(int(response.json()["estimated_time"]))
            return ""
        elif response.status_code == 200:
            return ""
        else:
            raise Exception(response.text)
    except Exception as e:
        print(f"Error loading the model: {e}")
        return "goodbye"

def test_chat():

    # header configuration
    headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_INFERENCE_TOKEN}"}
    chat_history = ""
    user_message = "User: "
    zero_message = "Zero: "

    user_input = _load_model(headers)
    bot_output = None

    while user_input.lower() not in ["goodbye", "bye"]:

        user_input = input("User: ")

        # conversation payload
        if len(chat_history) == 0:
            chat_payload = {
                "inputs": Config.ZERO_CONTEXT + f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
            }
        else:
            chat_payload = {
                "inputs": Config.ZERO_CONTEXT + chat_history + f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
            }

        # getting model's generated response
        response = requests.post(Config.API_URL_INSTRUCT, headers=headers, json=chat_payload, verify=False)
        if response.status_code == 200:
            bot_output = response.json()[0]['generated_text'].split("<|im_start|>assistant")[-1]
            chat_history += f"<|im_start|>user\n{user_input}<|im_end|>\n"
            chat_history += f"<|im_start|>assistant\n{bot_output}<|im_end|>\n"
        elif "is currently loading" in response.text:
            print(f"Something happened and forced the model to reload. It's going to take about {response.json()['estimated_time']} seconds")
            print(f"Returned error: {response.json()['error']}")
            time.sleep(int(response.json()["estimated_time"]))
        else:
            print(f"Error {response.status_code}: {response.text}")
            print("\nAn error has occurred with the model. Test chat will be finished.")
            return None
        
        print("Returned bot reponse:")
        print(bot_output)

def chat(user_input : str, model_url : str = Config.API_URL_INSTRUCT, chat_history : str = "",
         chat_context : str = Config.ZERO_CONTEXT) -> str:

    """
    Receives the user input, and calls a Hugging Face model through Inference API.

    Parameters:

    user_input : the text inserted by the user
    model_url : API endpoint to the Hugging Face model. Default selected model is Qwen/Qwen2.5-Coder-32B-Instruct
    chat_history : the chat history with previous dialogues
    chat_context : the context passed to the chat before starting the interaction

    Returned value:
    The sentence generated by the model
    """

    headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_INFERENCE_TOKEN}"}
    retry = True # in case model suddenly needs to be reloaded

    # conversation payload
    if len(chat_history) == 0:
        chat_payload = {
            "inputs": chat_context+ f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
        }
    else:
        chat_payload = {
            "inputs": chat_context + chat_history + f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
        }

    # getting model's generated response
    while retry:
        response = requests.post(model_url, headers=headers, json=chat_payload, verify=False)
        if response.status_code == 200:
            retry = False
            answer = response.json()[0]['generated_text'].split("<|im_start|>assistant")[-1]
            chat_history += f"<|im_start|>user\n{user_input}<|im_end|>\n"
            chat_history += f"<|im_start|>assistant\n{answer}<|im_end|>\n"
        elif "is currently loading" in response.text:
            print(f"Something happened and forced the model to reload. It's going to take about {response.json()['estimated_time']} seconds")
            print(f"Returned error: {response.json()['error']}")
            time.sleep(int(response.json()["estimated_time"]))
        else:
            retry = False
            return f"Something's wrong with my AI. I'm getting the following error:\nError {response.status_code}: {response.text}"
        
        return answer




