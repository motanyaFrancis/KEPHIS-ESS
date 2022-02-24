from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages

# Create your views here.


def PurchaseRequisition(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        for document in response['value']:
            if document['Status'] == 'Open' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                open.append(json.loads(output_json))
            if document['Status'] == 'Released' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                Approved.append(json.loads(output_json))
            if document['Status'] == 'Rejected' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
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


def CreatePurchaseRequisition(request):
    requisitionNo = ''
    orderDate = ''
    employeeNo = request.session['Employee_No_']
    reason = ""
    expectedReceiptDate = ''
    isConsumable = ""
    myUserId = request.session['User_ID']
    myAction = 'insert'
    if request.method == 'POST':
        try:
            orderDate = request.POST.get('orderDate')
            reason = request.POST.get('reason')
            expectedReceiptDate = request.POST.get('expectedReceiptDate')
            isConsumable = request.POST.get('isConsumable')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('purchase')
    try:
        response = config.CLIENT.service.FnPurchaseRequisitionHeader(
            requisitionNo, orderDate, employeeNo, reason, expectedReceiptDate, isConsumable, myUserId, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('purchase')


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
    return render(request, 'repairReq.html', ctx)


def RepairRequestDetails(request, pk):
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
    return render(request, 'repairDetail.html', ctx)


def StoreRequest(request):
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
    return render(request, 'storeReq.html', ctx)


def StoreRequestDetails(request, pk):
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
    return render(request, 'storeDetail.html', ctx)
