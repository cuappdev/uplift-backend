# /Users/sophie/Desktop/appdev/uplift-backend/src/utils/firebase_config.py

from src.utils.constants import SERVICE_ACCOUNT_PATH
import logging
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:
        if SERVICE_ACCOUNT_PATH:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_app = firebase_admin.initialize_app(cred)
        else:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set.")
    else:
        logging.info("Importing")
        firebase_app = firebase_admin.get_app()
    return firebase_app

# if __name__ == "__main__":
#     firebase_app = initialize_firebase()
#     print("Firebase app initialized:", firebase_app.name)



# from src.utils.constants import SERVICE_ACCOUNT_PATH
# import firebase_admin
# from firebase_admin import credentials, messaging

# if not firebase_admin._apps:
#     if SERVICE_ACCOUNT_PATH:
#         cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
#         firebase_app = firebase_admin.initialize_app(cred)
#     else:
#         raise ValueError("GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set.")
# else:
#     firebase_app = firebase_admin.get_app()

# registration_token = 'YOUR_REGISTRATION_TOKEN'

# message = messaging.Message(
#     notification=messaging.Notification(
#         title='Python Notification',
#         body='Hello from Python!'
#     ),
#     token=registration_token
# )

# response = messaging.send(message)
# print('Successfully sent message:', response)