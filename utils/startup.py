from chat.chat import Config
import requests
import time
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

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
    
def start_calendar_service():
  """
  Starts the Google Calendar API, returning the service object.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("utils/token.json"):
    creds = Credentials.from_authorized_user_file("utils/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "utils/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("utils/token.json", "w") as token:
      token.write(creds.to_json())

  
  return build("calendar", "v3", credentials=creds)