from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt

# Create your views here.


def PurchaseRequisition(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
        counts = len(open)
        counter = len(Approved)
        reject = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject}

    return render(request, 'purchaseReq.html', ctx)


def PurchaseRequestDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    try:
        response = session.get(Access_Point, timeout=10).json()

        openImp = []
        res_type = []
        for imprest in response['value']:
            if imprest['Status'] == 'Released' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['Application_No'] == pk:
                        res = imprest
            if imprest['Status'] == 'Open' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['Application_No'] == pk:
                        res = imprest
                        if imprest['Status'] == 'Open':
                            state = 1
            if imprest['Status'] == 'Released' and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['Application_No'] == pk:
                        res = imprest
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyImprestSurrenderLines")
    try:
        response_Lines = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for imprest in response_Lines['value']:
            if imprest['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(imprest)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "state": state, "line": openLines, "type": res_type}
    return render(request, 'purchaseDetail.html', ctx)


def RepairRequest(request):

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'repairReq.html', ctx)


def StoreRequest(request):

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'storeReq.html', ctx)
