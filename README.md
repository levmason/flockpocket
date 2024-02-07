# flockpocket
A platform for church flocks.

# Running with Docker
~~~
cd docker/
./configure.py
docker-compose up -d
~~~


# Push Notifications
Navigate to your Apple Developer account and creat a new key [here](https://developer.apple.com/account/resources/authkeys/list).
* Give your key a name
* Enable *Apple Push Notifications service (APNs)*
* *Continue*
* *Register*
* *Download*. This will give you a file named `AuthKey_[key id].p8`.
Add this file to the flockpocket base directory without changing the file name.
\** ***Danger*** **  Treat this key like a password, and keep it save from prying eyes.
Anyone with access to this key can send arbitrary push notifications to your app.

During the `configure.py` script, provide the following values:
* `APNS_AUTH_KEY_ID`. Select the appropriate key from your [key list](https://developer.apple.com/account/resources/authkeys/list), use the value labeled *Key ID*
* `APNS_TEAM_ID`. Found on your [Apple Developer membership card](https://developer.apple.com/account#MembershipDetailsCard).
