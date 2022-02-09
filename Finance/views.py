from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime
from django.contrib import messages


# Create your views here.


def ImprestRequisition(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/Imprests")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        for tender in response['value']:
            if tender['Status'] == 'Open' and tender['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(tender)
                open.append(json.loads(output_json))
            if tender['Status'] == 'Released':
                output_json = json.dumps(tender)
                Approved.append(json.loads(output_json))
            if tender['Status'] == 'Rejected':
                output_json = json.dumps(tender)
                Rejected.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter}
    return render(request, 'imprestReq.html', ctx)


def CreateImprest(request):
    session = requests.Session()
    session.auth = config.AUTHS
    imprestNo = ""
    isOnBehalf = ""
    accountNo = request.session['No_']
    responsibilityCenter = ''
    travelType = ''
    payee = ''
    purpose = ''
    usersId = request.session['User_ID']
    personalNo = request.session['No_']
    idPassport = ''
    isImprest = ''
    isDsa = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            isOnBehalf = request.POST.get('isOnBehalf')
            travelType = int(request.POST.get('travelType'))
            payee = request.POST.get('payee')
            purpose = request.POST.get('purpose')
            idPassport = request.POST.get('idPassport')
            isImprest = request.POST.get('isImprest')
            isDsa = request.POST.get('isDsa')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('imprestReq')
    try:
        response = config.CLIENT.service.FnImprestHeader(
            imprestNo, isOnBehalf, accountNo, responsibilityCenter, travelType, payee, purpose, usersId, personalNo, idPassport, isImprest, isDsa, myAction)
        print(response)
    except Exception as e:
        print(e)
    return redirect('imprestReq')


def ImprestDetails(request, pk):
    return render(request, 'imprestDetail.html')


def ImprestSurrender(request):

    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyImprestSurrenders")
    Access_Point2 = config.O_DATA.format("/Imprests")
    try:
        response = session.get(Access_Point, timeout=10).json()
        r = session.get(Access_Point2, timeout=10).json()
        open = []
        Approved = []
        New = []
        for tender in response['value']:
            if tender['Status'] == 'Open':
                output_json = json.dumps(tender)
                open.append(json.loads(output_json))
            if tender['Status'] == 'Released':
                output_json = json.dumps(tender)
                Approved.append(json.loads(output_json))
        for tender in r['value']:
            if tender['Status'] == 'Released':
                output_json = json.dumps(tender)
                New.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
        counted = len(New)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, 'new': New, "counted": counted}
    return render(request, 'imprestSurr.html', ctx)


def SurrenderDetails(request, pk):
    return redirect('imprestSurr')


def StaffClaim(request):

    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyStaffClaims")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        for tender in response['value']:
            if tender['Status'] == 'Open':
                output_json = json.dumps(tender)
                open.append(json.loads(output_json))
            if tender['Status'] == 'Released':
                output_json = json.dumps(tender)
                Approved.append(json.loads(output_json))
            if tender['Status'] == 'Rejected':
                output_json = json.dumps(tender)
                Rejected.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter}
    return render(request, 'staffClaim.html', ctx)
