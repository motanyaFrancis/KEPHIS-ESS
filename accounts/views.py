from django.http import response
from django.shortcuts import render, HttpResponse
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import datetime
# Create your views here.


def profile_request(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/UpcomingEvents")
    response = session.get(Access_Point).json()

    res = response['value']
    # Get Timezone
    # creating date object
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res}
    return render(request, 'profile.html', ctx)


def login_request(request):
    '''
    In order to catch exception well, make sure to know what every attribute contains
    '''
    customerNo = '01-00334545'
    eventNo = 'ev00030344'
    RegNo = 'null'
    try:
        if customerNo != '' and eventNo != '':
            result = config.CLIENT.service.RegisterEvent(
                customerNo, eventNo, RegNo)
            print(result)
            notify = "Successfully Added"
        else:
            raise ValueError('Incorrect input!')
    except Exception as e:
        notify = e
    ctx = {"note": notify}
    return render(request, 'auth.html', ctx)
