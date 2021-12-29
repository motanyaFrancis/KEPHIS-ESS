from django.shortcuts import render, redirect
from . models import Photo
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime

# Create your views here.


def canvas(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        for image in images:
            photo = Photo.objects.create(
                image=image,
            )
        return redirect('main')
    return render(request, 'offcanvas.html')


def dashboard(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/UpcomingEvents")
    response = session.get(Access_Point).json()

    res = response['value']

    # Get Timezone
    # creating date object
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    photo = Photo.objects.all()
    ctx = {"photo": photo, "today": todays_date, "res": res}
    return render(request, 'main/dashboard.html', ctx)


def details(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/UpcomingEvents")
    response = session.get(Access_Point).json()

    for tender in response['value']:
        if tender['Event_No'] == pk:
            res = tender
            type = tender['Chargeable']
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res, 'type': type}
    return render(request, "main/details.html", ctx)
