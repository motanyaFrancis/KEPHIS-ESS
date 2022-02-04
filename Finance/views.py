from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime


# Create your views here.


def ImprestRequisition(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/Imprests")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        for tender in response['value']:
            if tender['Status'] == 'Open':
                output_json = json.dumps(tender)
                open.append(json.loads(output_json))
            if tender['Status'] == 'Released':
                output_json = json.dumps(tender)
                Approved.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter}
    return render(request, 'imprestReq.html', ctx)


def ImprestSurrender(request):

    # Get Timezone
    # creating date object
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'imprestSurr.html', ctx)


def SurrenderDetails(request, pk):
    return redirect('imprestSurr')


def StaffClaim(request):

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'staffClaim.html', ctx)
