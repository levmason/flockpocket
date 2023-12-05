import time
import uuid
import traceback
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
import json
import aiofiles
from asgiref.sync import sync_to_async

from common.email import send
from common.http import json_response
from common.models import User, Invite
from common import config as cfg
from common import utility
from common import logger as log
from common import email

@sync_to_async
def get_user_from_request(request):
    return request.user.id if bool(request.user) else None

@sync_to_async
def user_login (request, username, password):
    user = authenticate(username=username, password=password)
    login(request, user)

async def get_user_d ():
    fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'details']
    user_d = {}
    async for user in User.objects.values(*fields):
        if user['is_active']:
            user['id'] = str(user['id'])
            user.update(user.pop('details') or {})
            user_d[user['id']] = user
            user['full_name'] = f"{user['first_name']} {user['last_name']}"

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
            # this user is already here!
            return HttpResponse(status=409)
        except ObjectDoesNotExist: pass

        invite = await Invite.objects.acreate()

        # LEVY: send the email
        try:
            await send(email, "Welcome to FlockPocket!", f"flockpocket.com/user_activate/{invite.id}")
        except: pass

        return json_response({
            'link': f"/user_activate/{invite.id}"
        })

async def create_user (request, invite_id):
    if request.method == "POST":
        try:
            invite = await Invite.objects.aget(pk=invite_id)
        except ObjectDoesNotExist:
            # no such invite id
            return HttpResponse(status=404)

        # extract the user parameters
        data = json.loads(request.POST.dict()['details']);
        # extract the email address
        email = data.pop("email", None)
        # create a new user
        try:
            user = await sync_to_async(User.objects.create_user)(email)
        except IntegrityError:
            return HttpResponse("A user already exists with this email address!", status=409)

        # remove the invite (it's been used now)
        await invite.adelete()

        # update the user params (reuse the update_user function)
        return await update_user(request, str(user.id))

async def update_user (request, user_id):
    if request.method == "POST":
        # extract the user parameters
        data = json.loads(request.POST.dict()['details']);

        user_id = uuid.UUID(user_id)
        user = await User.objects.aget(pk=user_id)

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
