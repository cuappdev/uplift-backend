from app import firebase_app
from firebase_admin import messaging

def send_notification():
    # This registration token comes from the client FCM SDKs.
    registration_token = 'ccaJP_JdMkNEspPbl1fYvx:APA91bGN-8BytPPNXeq5Yq_1wmmEHkMh-eO1RfCfZx15ac-LKvTlQCE8sW-B3Q1KPu1S3W9TYsVfPt42e7L_TPHd3Ul6FGdfnZivbmmENAXaf3OEJqiLdvBNfYWMxP9jOsbfF_aOkDUA'

    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)

send_notification()


# import requests
# import json
# from src.utils.constants import SERVICE_ACCOUNT_PATH

# # Replace with the provided FCM registration token
# FCM_TOKEN = "ccaJP_JdMkNEspPbl1fYvx:APA91bGN-8BytPPNXeq5Yq_1wmmEHkMh-eO1RfCfZx15ac-LKvTlQCE8sW-B3Q1KPu1S3W9TYsVfPt42e7L_TPHd3Ul6FGdfnZivbmmENAXaf3OEJqiLdvBNfYWMxP9jOsbfF_aOkDUA"

# # Prepare the message payload
# message = {
#     "to": FCM_TOKEN,
#     "notification": {
#         "title": "Test Notification",
#         "body": "This is a test message from your server!",
#     },
#     "data": {
#         "extra_data": "This can contain additional data."
#     }
# }

# # Send the request to FCM
# headers = {
#     'Content-Type': 'application/json',
#     'Authorization': f'key={SERVICE_ACCOUNT_PATH}'
# }

# # Make the request to send the notification
# response = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(message))

# # Print the response for debugging
# print("Response Status Code:", response.status_code)
# print("Response JSON:", response.json())

# # Check for successful sending
# if response.status_code == 200:
#     print("Notification sent successfully!")
# else:
#     print("Failed to send notification:", response.json())


# # Subscribe to topic
# def subscribe_to_topic(token, topic):
#     url = f"https://fcm.googleapis.com/fcm/subscribe"
#     payload = {
#         "to": f"/topics/{topic}",
#         "registration_tokens": [token],
#     }
    
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'key={SERVER_KEY}'
#     }
    
#     response = requests.post(url, headers=headers, data=json.dumps(payload))
    
#     print("Subscribe Response Status Code:", response.status_code)
#     print("Subscribe Response JSON:", response.json())
    
#     if response.status_code == 200:
#         print(f"Successfully subscribed to topic: {topic}")
#     else:
#         print(f"Failed to subscribe to topic: {response.json()}")

# # Call the subscription function
# subscribe_to_topic(FCM_TOKEN, TOPIC)