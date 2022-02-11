from django.shortcuts import render, redirect
from datetime import date, datetime
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import enum


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
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "reject": Rejected}
    return render(request, 'imprestReq.html', ctx)


def CreateImprest(request):
    session = requests.Session()
    session.auth = config.AUTHS
    imprestNo = ""
    isOnBehalf = ""
    accountNo = ''
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
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        print(e)
    return redirect('imprestReq')


def ImprestDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/Imprests")
    try:
        response = session.get(Access_Point, timeout=10).json()
        openImp = []
        for imprest in response['value']:
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
                        if imprest['Status'] == 'Open':
                            state = 1
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyImprestLines")
    try:
        response = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for imprest in response['value']:
            if imprest['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(imprest)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    lineNo = 4
    imprestNo = pk
    destination = ""
    imprestType = ''
    travelDate = ''
    returnDate = ''
    requisitionType = ''
    dailyRate = 10
    quantity = ""
    areaCode = ""
    imprestTypes = ''
    businessGroupCode = ''
    dimension3 = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            destination = request.POST.get('destination')
            imprestTypes = request.POST.get('imprestType')
            travelDate = request.POST.get('travel')
            returnDate = request.POST.get('returnDate')
            quantity = int(request.POST.get('quantity'))

        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=imprestNo)

    class Data(enum.Enum):
        values = imprestTypes
    imprestType = (Data.values).value
    try:
        response = config.CLIENT.service.FnImprestLine(
            lineNo, imprestNo, imprestType, destination, travelDate, returnDate, requisitionType, dailyRate, quantity, areaCode, businessGroupCode, dimension3, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('IMPDetails', pk=imprestNo)
    except Exception as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res, "line": openLines, "state": state}
    return render(request, 'imprestDetail.html', ctx)


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
        for imprest in response['value']:
            if imprest['Status'] == 'Open':
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released':
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
        for imprest in r['value']:
            if imprest['Status'] == 'Released':
                output_json = json.dumps(imprest)
                New.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
        counted = len(New)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
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
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
        rej = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts, "rej": rej,
           "response": Approved, "claim": counter, 'reject': Rejected}
    return render(request, 'staffClaim.html', ctx)


def CreateClaim(request):
    claimNo = ""
    claimType = ""
    isOnBehalf = False
    accountNo = ''
    payee = 'Papa'
    purpose = 'Test'
    usersId = request.session['User_ID']
    staffNo = 'AH'
    currency = ""
    imprestSurrDocNo = ''
    myAction = 'insert'
    if request.method == 'POST':
        claimType = int(request.POST.get('claimType'))
        isOnBehalf = request.POST.get('isOnBehalf')
        payee = request.POST.get('payee')
        purpose = request.POST.get('purpose')
    try:
        response = config.CLIENT.service.FnStaffClaimHeader(
            claimNo, claimType, isOnBehalf, accountNo, payee, purpose, usersId, staffNo, currency, imprestSurrDocNo, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('claim')
    except Exception as e:
        print(e)
    return redirect('claim')
