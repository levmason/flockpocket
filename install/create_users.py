#!/usr/bin/env python
import os
import sys
import django
sys.path.append("/opt/flockpocket/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flockpocket.settings")
django.setup()

from common.models import User
from django.db import IntegrityError

try:
    User.objects.create_superuser('admin@flockpocket.com', 'password')
except IntegrityError: pass
except Exception as e: print(e)
