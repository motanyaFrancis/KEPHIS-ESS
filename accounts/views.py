from logging import exception
from django.http import response
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import datetime
from zeep import Client
from zeep.transports import Transport
from django.contrib import messages
# Create your views here.


def profile_request(request):

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'profile.html', ctx)


def login_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = Session()
        user.auth = HttpNtlmAuth(f'domain\\{username}', password)
        try:
            CLIENT = Client(config.BASE_URL, transport=Transport(session=user))
            request.session['username'] = username
            logged_in = request.session['username']
            print(logged_in)
            return redirect('dashboard')
        except:
            messages.error(request, "Invalid username or password!!")
            return redirect('auth')

    return render(request, 'auth.html')
