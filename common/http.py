import json
from django.conf import settings
from django.http import HttpResponse

def json_response (response):
    if response in [None, "", "null"]:
        return HttpResponse(status=204)
    elif response in [False, "false"]:
        return HttpResponse(status=500)

    try:
        # convert to string if neccessary
        if not isinstance(response, str):
            if settings.DEBUG:
                response = json.dumps(response, indent=4)
            else:
                response = json.dumps(response)
        return HttpResponse(response, content_type="application/json")
    except:
        return HttpResponse(status=500)
