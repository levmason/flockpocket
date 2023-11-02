import time
import uuid
import traceback
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
import json
import aiofiles
from asgiref.sync import sync_to_async

from common.http import json_response
from common.models import User
from common import config as cfg
from common import utility
from common import logger as log
from common import email

@sync_to_async
def get_user_from_request(request):
    return request.user.id if bool(request.user) else None

@sync_to_async
def user_login (request, username, password):
    try:
        user = authenticate(username=username, password=password)
        login(request, user)
    except Exception as e:
        log.debug(e)

async def get_user_d ():
    t1 = time.time()
    fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'details']
    user_d = {}
    async for user in User.objects.values(*fields):
        if user['is_active']:
            user['id'] = str(user['id'])
            user.update(user.pop('details') or {})
            user_d[user['id']] = user
            user['full_name'] = f"{user['first_name']} {user['last_name']}"

    t2 = time.time()
    if (t2-t1) > 1:
        log.debug("HTTP Users took: %s" % (t2-t1))

    return user_d

async def ui_config (request):
    user_id = await get_user_from_request(request)

    ret_d = {}
    ret_d['user_d'] = await get_user_d()
    ret_d['user_id'] = str(user_id)

    return json_response(ret_d)

async def users (request):
    user_d = await get_user_d()
    return json_response(user_d)

async def invite_user (request):
    """
    Invite a new user to the flock
    """
    if request.method == "POST":
        # extract the user parameters
        data = json.loads(request.POST.dict()['data']);
        email = data.get("email")

        # create or get the user
        try:
            user = await User.objects.aget(email=email)
            user.is_active = False
            if user.is_active:
                # this user is already here!
                return HttpResponse(status=400)
            else:
                # update the options
                user.details = {}
                user.first_name = data.get("first_name")
                user.last_name = data.get("last_name")
                await user.asave()

        except ObjectDoesNotExist:
            user = await sync_to_async(User.objects.create_user)(
                email,
                None,
                first_name = data.get("first_name"),
                last_name = data.get("last_name"),
                is_active = False,
            )

        # LEVY: send the email
        log.debug(user.id)
        return HttpResponse(status=201)

async def update_user (request, user_id):
    try:
        if request.method == "POST":
            user_id = uuid.UUID(user_id)

            user = await User.objects.aget(pk=user_id)

            # extract the user parameters
            data = json.loads(request.POST.dict()['details']);

            # set the user to active
            user.is_active = True

            # Update the user options
            email = data.pop("email", None)
            if email:
                user.email = email

            password = data.pop("password", None)
            if password:
                user.set_password(password)

            first_name = data.get("first_name")
            if first_name:
                user.first_name = first_name

            last_name = data.get("last_name")
            if last_name:
                user.last_name = last_name

            # build the address
            address = data.get("address", "")
            city = data.pop("city", "")
            state = data.pop("state", "")
            if address and city and state:
                data['address'] = f"{address}, {city}, {state}"

            address = data.get("address")
            if address:
                user.address = address

            user.details.update(data)

            # handle the profile picture
            pic = ""
            try:
                image = request.FILES['profile_picture']
                filename = str(user.id) + ".jpg"
                filepath = "%s/%s" % (cfg.profile_pic_dir, filename)
                # write the file
                async with aiofiles.open(filepath, "wb") as f:
                    for chunk in image.chunks():
                        await f.write(chunk)

                user.details['pic'] = filename
            except Exception as e: pass

            await user.asave()

            # log in the new user
            if password:
                await user_login(request, user.email, password)

            # update or add the user (send to all active websockets)
            await cfg.update_user(user)

            return HttpResponse(status=201)
    except Exception as e:
        log.debug(e)
