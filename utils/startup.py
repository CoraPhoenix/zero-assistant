from chat.chat import Config
import requests
import time

def initial_load() -> None:

    """
    Loads the initial configurations for the model.

    Parameters:
    None

    Returned value:
    None
    """

    headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_INFERENCE_TOKEN}"}

    initial_payload = {
        "inputs": "Welcome"
    }

    try:
        response = requests.post(Config.API_URL_INSTRUCT, headers=headers, json=initial_payload, verify=False)
        if response.status_code != 200 and "is currently loading" in response.text:
            print(f"Loading conversational model. It's going to take about {response.json()['estimated_time']} seconds")
            loading_time = float(response.json()["estimated_time"])
            start_time = time.time()
            end_time = start_time
            while end_time - start_time < loading_time:
                print(f"Loading model... {int(100 * (end_time - start_time) / loading_time)}%")
        elif response.status_code == 200:
            print("Model is already loaded.\n")
        else:
            raise Exception(response.text)
    except Exception as e:
        raise SystemExit(f"Fatal: The model couldn't be loaded.\nError info: {e}")