import os
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv("chat/.env")
SECRET_KEY = os.getenv("SECRET_KEY")

# Generate key if not set
if SECRET_KEY is None:
    SECRET_KEY = Fernet.generate_key().decode()
    with open("chat/.env", "a") as f:
        f.write(f"\nSECRET_KEY={SECRET_KEY}\n")

cipher = Fernet(SECRET_KEY.encode())

def encrypt_data(data) -> bytes:
    """
    Encrypts the data using Fernet encryption.

    Parameters:
        data: the data to be encrypted

    Returned value:
        bytes: the encrypted data
    """
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted_data):
    """
    Decrypts the data using Fernet encryption.
    
    Parameters:
        encrypted_data: the data to be decrypted

    Returned value:
        Any: the decrypted data
    """
    return cipher.decrypt(encrypted_data).decode()

def save_secure_json(filename : str, data) -> None:
    """
    Encrypts and saves a dictionary to a binary file.

    Parameters:
        filename (str): the name of the file to be saved
        data: the content to be saved in the file

    Returned value:
        None
    """
    encrypted_data = encrypt_data(json.dumps(data))
    with open(filename, "wb") as f:
        f.write(encrypted_data)

def load_secure_json(filename : str):
    """
    Loads and decrypts a binary file.
    Parameters:
        filename (str): the name of the file to be loaded

    Returned value:
        Any: a dictionary containing the decrypted data
    """
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            encrypted_data = f.read()
        return json.loads(decrypt_data(encrypted_data))
    return {}

# Example Usage
if __name__ == "__main__":
    try:
        # Store sensitive data
        with open("data/settings_raw.json", "r") as f:
            data = json.load(f)
        save_secure_json("data/settings.data", data)

        # Retrieve and decrypt data
        retrieved_data = load_secure_json("data/settings.data")
        print("Decrypted Data:", retrieved_data)
    except Exception as inv_sig:
        print(f"Secret key: {SECRET_KEY}")
