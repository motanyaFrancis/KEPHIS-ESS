from urllib import request
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


def Leave_Request(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    LeaveTypes = config.O_DATA.format("/QyLeaveTypes")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_types = session.get(LeaveTypes, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Leave = res_types['value']
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

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject, 'leave': Leave}
    return render(request, 'leave.html', ctx)


def CreateLeave(request):
    applicationNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    dimension3 = ''
    leavePeriod = ''
    leaveType = ""
    plannerStartDate = ''
    isReturnSameDay = ''
    daysApplied = ""
    isLeaveAllowancePayable = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            leaveType = request.POST.get('leaveType')
            plannerStartDate = request.POST.get('plannerStartDate')
            isReturnSameDay = request.POST.get('isReturnSameDay')
            daysApplied = int(request.POST.get('daysApplied'))
            isLeaveAllowancePayable = request.POST.get(
                'isLeaveAllowancePayable')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('leave')
    try:
        response = config.CLIENT.service.FnLeaveApplication(
            applicationNo, employeeNo, usersId, dimension3, leavePeriod, leaveType, plannerStartDate, isReturnSameDay, daysApplied, isLeaveAllowancePayable, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('leave')


def Training_Request(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyTrainingRequests")
    currency = config.O_DATA.format("/QyCurrencies")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_currency = session.get(currency, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        cur = res_currency['value']
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
        counts = len(open)
        counter = len(Approved)
        reject = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts, "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject, 'cur': cur}
    return render(request, 'training.html', ctx)


def CreateTrainingRequest(request):
    requestNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    designation = ''
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


def Loan_Request(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLoansRegister")
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

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject}
    return render(request, 'loan.html', ctx)


def CreateLoanRequest(request):
    loanNo = ''
    requestedDate = ''
    usersId = request.session['User_ID']
    pmlNo = ''
    loanProductType = ''
    loanDuration = ''
    requestedAmount = ''
    interestCalculationMethod = ''
    repaymentFrequency = ''
    bankName = ''
    bankAccountNo = ''
    bankBranchName = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            requestedDate = request.POST.get('requestedDate')
            pmlNo = request.POST.get('pmlNo')
            loanProductType = request.POST.get('loanProductType')
            loanDuration = int(request.POST.get('loanDuration'))
            requestedAmount = float(request.POST.get('requestedAmount'))
            interestCalculationMethod = request.POST.get(
                'interestCalculationMethod')
            repaymentFrequency = request.POST.get('repaymentFrequency')
            bankName = request.POST.get('bankName')
            bankAccountNo = request.POST.get('bankAccountNo')
            bankBranchName = request.POST.get('bankBranchName')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('loan')
    try:
        response = config.CLIENT.service.FnTrainingRequest(
            loanNo, requestedDate, usersId, pmlNo, loanProductType, loanDuration, requestedAmount, interestCalculationMethod, repaymentFrequency, bankName, bankAccountNo, bankBranchName, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('loan')
