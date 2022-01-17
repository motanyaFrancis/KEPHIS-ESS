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

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'profile.html', ctx)


def login_request(request):

    return render(request, 'auth.html')
