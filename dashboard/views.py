from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime
from django.contrib.sessions.models import Session
# Create your views here.


def dashboard(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/Imprests")
    Access_Leave = config.O_DATA.format("/QyLeaveApplications")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Leave = session.get(Access_Leave, timeout=10).json()
        openLeave = []
        AppLeave = []
        RejLeave = []
        openTraining = []
        AppTraining = []
        RejTraining = []
        Approved = []
        Open = []
        for Leave in Leave['value']:
            if Leave['Status'] == 'Open' and Leave['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(Leave)
                openLeave.append(json.loads(output_json))
            if Leave['Status'] == 'Released' and Leave['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(Leave)
                AppLeave.append(json.loads(output_json))
            if Leave['Status'] == 'Rejected' and Leave['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(Leave)
                RejLeave.append(json.loads(output_json))
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
        for tender in response['value']:
            if tender['Status'] == 'Open':
                output_json = json.dumps(tender)
                Open.append(json.loads(output_json))
            if tender['Status'] == 'Released':
                output_json = json.dumps(tender)
                Approved.append(json.loads(output_json))
        counts = len(Open)
        counter = len(Approved)
        leave_open = len(openLeave)
        leave_App = len(AppLeave)
        leave_rej = len(RejLeave)
    except requests.exceptions.ConnectionError as e:
        print(e)

    Approval = config.O_DATA.format("/QyApprovalEntries")
    try:
        res_App = session.get(Approval, timeout=10).json()
        Approve = []
        for approve in res_App['value']:
            if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                output_json = json.dumps(approve)
                Approve.append(json.loads(output_json))
        countsAPP = len(Approve)
    except requests.exceptions.ConnectionError as e:
        print(e)
    fullname = request.session['fullname']
    Responsibility = request.session['User_Responsibility_Center']
    E_Mail = request.session['E_Mail']
    Employee_No_ = request.session['Employee_No_']
    Customer_No_ = request.session['Customer_No_']

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")

    ctx = {"today": todays_date,
           "res": open, "count": counts,
           "response": Approved, "counter": counter,
           "full": fullname, "Responsibility": Responsibility,
           "E_Mail": E_Mail, "Employee_No_": Employee_No_,
           "Customer_No_": Customer_No_, "apps": Approve, "countsAPP": countsAPP,
           "leave_open": leave_open, "leave_app": leave_App,
           "leave_rej": leave_rej}
    return render(request, 'main/dashboard.html', ctx)


def details(request, pk):

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, "main/details.html", ctx)


def Canvas(request):

    fullname = request.session['fullname']
    ctx = {"fullname": fullname}
    return render(request, "offcanvas.html", ctx)
