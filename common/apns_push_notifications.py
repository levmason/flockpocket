# Import necessary classes and modules
from pyapns_client import AsyncAPNSClient, TokenBasedAuth, IOSPayload, IOSNotification
from pyapns_client import UnregisteredException, APNSDeviceException, APNSServerException, APNSProgrammingException

from common import config as cfg

async def pushiOSMessage(push_token: str, message: dict, thread: str):
    async with AsyncAPNSClient(
        mode=AsyncAPNSClient.MODE_DEV,
        authentificator=TokenBasedAuth(
            auth_key_path=f'/opt/flockpocket/AuthKey_{cfg.APNS_AUTH_KEY_ID}.p8',
            auth_key_id=cfg.APNS_AUTH_KEY_ID,
            team_id=cfg.APNS_TEAM_ID
        )
    ) as client:
        try:
            # Create the payload for the notification
            # log.debug(message)
            payload = IOSPayload(alert=message['text'], sound='bleat.wav', thread_id=thread.id)

            # Create the notification object with the payload and other optional parameters
            # the 'topic' value is the iOS Bundle ID
            notification = IOSNotification(payload=payload, priority=10, topic="net.snowskeleton.FlockPocket")

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
