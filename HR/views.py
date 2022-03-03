from curses.ascii import isdigit
from urllib import request
from django.shortcuts import render, redirect
from datetime import date, datetime
from isodate import date_isoformat
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages

# Create your views here.


def Leave_Request(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    LeaveTypes = config.O_DATA.format("/QyLeaveTypes")
    LeavePlanner = config.O_DATA.format("/QyLeavePlannerLines")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_types = session.get(LeaveTypes, timeout=10).json()
        res_planner = session.get(LeavePlanner, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        Leave = res_types['value']
        Planner = res_planner['value']
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
            if imprest['Status'] == "Pending Approval" and imprest['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Pending.append(json.loads(output_json))
        counts = len(open)
        pend = len(Pending)

        counter = len(Approved)

        reject = len(Rejected)

    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open,
           "count": counts, "response": Approved,
           "counter": counter, "rej": Rejected,
           'reject': reject, 'leave': Leave,
           "plan": Planner, "pend": pend,
           "pending": Pending}
    return render(request, 'leave.html', ctx)


def CreateLeave(request):
    applicationNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    dimension3 = ''
    leaveType = ""
    plannerStartDate = "",
    daysApplied = ""
    isReturnSameDay = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            leaveType = request.POST.get('leaveType')
            plannerStartDate = datetime.strptime(
                (request.POST.get('plannerStartDate')), '%Y-%m-%d')
            daysApplied = int(request.POST.get('daysApplied'))
            isReturnSameDay = request.POST.get('isReturnSameDay')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('leave')
    print(plannerStartDate)
    try:
        response = config.CLIENT.service.FnLeaveApplication(
            applicationNo, employeeNo, usersId, dimension3, leaveType, plannerStartDate, daysApplied, isReturnSameDay, myAction)
        messages.success(request, "You have successfully  Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('leave')


def LeaveDetail(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    state = ''
    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openClaim = []
        Approvers = []
        Pending = []
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for claim in response['value']:
            if claim['Status'] == 'Released' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        res = claim
            if claim['Status'] == 'Open' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        res = claim
                        if claim['Status'] == 'Open':
                            state = 1
            if claim['Status'] == 'Rejected' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        res = claim
            if claim['Status'] == "Pending Approval" and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                Pending.append(json.loads(output_json))
                for claim in Pending:
                    if claim['Application_No'] == pk:
                        res = claim
                        if claim['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "Approvers": Approvers, "state": state}
    return render(request, 'leaveDetail.html', ctx)


def LeaveApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


def LeaveCancelApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Cancel Request Successfully Sent!!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


def Training_Request(request):
    print("emps", request.session['Employee_No_'])
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyTrainingRequests")
    currency = config.O_DATA.format("/QyCurrencies")
    trainingNeed = config.O_DATA.format("/QyTrainingNeeds")
    destination = config.O_DATA.format("/QyDestinations")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_currency = session.get(currency, timeout=10).json()
        res_train = session.get(trainingNeed, timeout=10).json()
        res_dest = session.get(destination, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        cur = res_currency['value']
        trains = res_train['value']
        destinations = res_dest['value']
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
            if imprest['Status'] == 'Pending Approval' and imprest['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(imprest)
                Pending.append(json.loads(output_json))
        counts = len(open)

        counter = len(Approved)

        reject = len(Rejected)

        pend = len(Pending)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open,
           "count": counts, "response": Approved,
           "counter": counter, "rej": Rejected,
           'reject': reject, 'cur': cur,
           "train": trains, "des": destinations,
           "pend": pend, "pending": Pending}
    return render(request, 'training.html', ctx)


def CreateTrainingRequest(request):
    requestNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    designation = request.session['User_Responsibility_Center']
    isAdhoc = ""
    trainingNeed = ""
    description = ""
    startDate = ''
    endDate = ''
    destination = ''
    currency = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            isAdhoc = request.POST.get('isAdhoc')
            description = request.POST.get('description')
            startDate = request.POST.get('startDate')
            trainingNeed = request.POST.get('trainingNeed')
            destination = request.POST.get('destination')
            endDate = request.POST.get('endDate')
            currency = request.POST.get('currency')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('training_request')
    try:
        response = config.CLIENT.service.FnTrainingRequest(
            requestNo, employeeNo, usersId, designation, isAdhoc, trainingNeed, description, startDate, endDate, destination, currency, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('training_request')


def TrainingDetail(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    state = ""
    Access_Point = config.O_DATA.format("/QyTrainingRequests")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openClaim = []
        Approvers = []
        Pending = []
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for claim in response['value']:
            if claim['Status'] == 'Released' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Request_No_'] == pk:
                        res = claim
            if claim['Status'] == 'Open' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Request_No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Open':
                            state = 1
            if claim['Status'] == 'Rejected' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Request_No_'] == pk:
                        res = claim
            if claim['Status'] == 'Pending Approval' and claim['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(claim)
                Pending.append(json.loads(output_json))
                for claim in Pending:
                    if claim['Request_No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "Approvers": Approvers, "state": state}
    return render(request, 'trainingDetail.html', ctx)


def TrainingApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def TrainingCancelApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Cancel Request Successfully Sent!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)
