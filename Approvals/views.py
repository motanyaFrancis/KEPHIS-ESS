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


def Approve(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        for approve in response['value']:
            if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                output_json = json.dumps(approve)
                open.append(json.loads(output_json))
        counts = len(open)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts}
    return render(request, 'Approve.html', ctx)


def ApproveDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    Access_Point = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Approves = []
        for approve in response['value']:
            if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                output_json = json.dumps(approve)
                Approves.append(json.loads(output_json))
                for claim in Approves:
                    if claim['Document_No_'] == pk:
                        res = claim
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res}
    return render(request, 'approveDetails.html', ctx)


def All_Approved(request, pk):
    entryNo = 0
    documentNo = pk
    userID = request.session['User_ID']
    approvalComments = ""
    myAction = 'approve'
    if request.method == 'POST':
        try:
            approvalComments = request.POST.get('approvalComments')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('ApproveData', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('ApproveData', pk=documentNo)


def Rejected(request, pk):
    entryNo = 0
    documentNo = pk
    userID = request.session['User_ID']
    approvalComments = ""
    myAction = 'reject'
    if request.method == 'POST':
        try:
            approvalComments = request.POST.get('approvalComments')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('ApproveData', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('ApproveData', pk=documentNo)
