#!/usr/bin/env python3
import os
import sys
import secrets
import string

filepath = "flockpocket.env"
if os.path.exists(filepath):
    print("Config file already exists! Delete it if you'd like to create a new one.")
    sys.exit()

# generate the secret keys
chars = string.ascii_lowercase + string.digits
django_secret_key = ''.join(secrets.choice(chars) for i in range(50))
postgres_password = ''.join(secrets.choice(chars) for i in range(16))

config = {
    'DOMAIN_NAME': input('Domain name: '),
    'DEBUG': True if input('Debug (y/N): ') in ['y', 'yes'] else False,
    'DJANGO_SECRET_KEY': django_secret_key,
    'POSTGRES_PASSWORD': postgres_password,
    'EMAIL_HOST': input('Email host (smtp.example.net): '),
    'EMAIL_PORT': input('Email port (465): '),
    'EMAIL_USER': input('Email user (to login): '),
    'EMAIL_PASSWORD': input('Email password (to log in): '),
    'EMAIL_FROM': input('Email from (can be different from user, but must be valid for your account): '),
}

# write the config file
config_text = ''.join([f"{key}={val}\n" for key,val in config.items()])
with open (filepath, "w") as f:
    f.write(config_text)

print("File created! Edit the flockpocket.env file to make changes.")
