# Import necessary classes and modules
from pyapns_client import AsyncAPNSClient, TokenBasedAuth, IOSPayload, IOSNotification, IOSPayloadAlert
from pyapns_client import UnregisteredException, APNSDeviceException, APNSServerException, APNSProgrammingException

from common import config as cfg
from api.chat.ChatThreadHandler import ChatThreadHandler

async def pushiOSMessage(push_token: str, message: dict, thread: ChatThreadHandler):
    async with AsyncAPNSClient(
        mode=AsyncAPNSClient.MODE_DEV,
        authentificator=TokenBasedAuth(
            auth_key_path=f'/opt/flockpocket/AuthKey_{cfg.apns_auth_key_id}.p8',
            auth_key_id=cfg.apns_auth_key_id,
            team_id=cfg.apns_team_id
        )
    ) as client:
        try:
            # Create the payload for the notification
            alert = IOSPayloadAlert(title=message['user'], body=message['text'])
            payload = IOSPayload(alert=alert, sound='bleat.wav', thread_id=thread.id, mutable_content=True)

            # Create the notification object with the payload and other optional parameters
            # the 'topic' value is the iOS Bundle ID
            notification = IOSNotification(payload=payload, priority=10, topic=cfg.ios_bundle_id)

            # Send the notification asynchronously to one or more device tokens
            await client.push(notification=notification, device_token=push_token)
        except UnregisteredException as e:
            print(f'device is unregistered, compare timestamp {e.timestamp_datetime} and remove from db')
        except APNSDeviceException:
            print('flag the device as potentially invalid and remove from db after a few tries')
        except APNSServerException:
            print('try again later')
        except APNSProgrammingException:
            print('check your code and try again later')
        else:
            # Handle successful push
            print('Push notification sent successfully!')
