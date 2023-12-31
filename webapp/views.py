from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from common.models import Invite
from common import config as cfg
from common import utility
from common import logger as log
import time

def index (request):
    if not request.user.is_authenticated:
        user = authenticate(request, cookies=request.COOKIES)
        if user is not None and user.is_active:
            login(request, user)
        else:
            return redirect(login_view)

    return render(request, 'index.html')

async def user_activate (request, invite_id):
    try:
        invite = await Invite.objects.aget(pk=invite_id)
        return render(request, 'index.html')
    except: pass

    return HttpResponse(status=404)

def logout_view (request):
    logout(request)
    return redirect('index')

def login_view(request):
    if request.method == 'GET':
        invalid = False
        if ('invalid' in request.GET and
            request.GET['invalid'] == 'True'):
            invalid = True

        # show the login page
        return render(request, 'login.html',
                      {'invalid': invalid,})

    else:
        if 'username' in request.POST and 'password' in request.POST:
            # Login attempt
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                # Redirect to a success page.
                return redirect(request.GET.get('next') or index)

            # Return an 'invalid login' error message.
            url = request.META['QUERY_STRING'].replace('&invalid=True', '')+'&invalid=True'
            login_url = reverse('login_view')
            return redirect('%s?%s' % (login_url, url))
