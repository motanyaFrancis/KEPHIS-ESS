from urllib import request
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

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
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


def LeaveDetail(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    Access_Point = config.O_DATA.format("/QyLeaveApplications")
    try:
        response = session.get(Access_Point, timeout=10).json()
        openClaim = []
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
            if claim['Status'] == 'Rejected' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['Application_No'] == pk:
                        res = claim
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res}
    return render(request, 'leaveDetail.html', ctx)


def Training_Request(request):
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
        counts = len(open)
        counter = len(Approved)
        reject = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts, "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject, 'cur': cur, "train": trains, "des": destinations}
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


def Loan_Request(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLoansRegister")
    Banks = config.O_DATA.format("/QyBanks")
    Branch_Name = config.O_DATA.format("/QyBankBranches")
    PMLNo = config.O_DATA.format("/QyCustomers")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_banks = session.get(Banks, timeout=10).json()
        res_branch = session.get(Branch_Name, timeout=10).json()
        res_PML = session.get(PMLNo, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        PMLs = []
        Bank_response = res_banks['value']
        Branch_Code = res_branch['value']
        for pml in res_PML['value']:
            if pml['PML'] == True:
                output_json = json.dumps(pml)
                PMLs.append(json.loads(output_json))
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
           'reject': reject, "banks": Bank_response, "branch": Branch_Code, "pml": PMLs}
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


def LoanLines(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/QyLoansRegister")
    try:
        response = session.get(Access_Point, timeout=10).json()
        openClaim = []
        for claim in response['value']:
            if claim['Status'] == 'Released' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['No_'] == pk:
                        res = claim
            if claim['Status'] == 'Open' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Open':
                            state = 1
            if claim['Status'] == 'Rejected' and claim['User_ID'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['No_'] == pk:
                        res = claim
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res, "state": state}
    return render(request, 'LoanDetails.html', ctx)


def FnLoanCollateral(request, pk):
    collateralCode = ''
    loanNo = pk
    collateralType = ""
    maturityDate = ""
    collateralValue = ""
    isPerfected = ''
    isExcludedActivities = ""
    isNemaCompliant = ""
    securityType = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            collateralType = request.POST.get('collateralType')
            maturityDate = request.POST.get('maturityDate')
            collateralValue = float(request.POST.get('collateralValue'))
            isPerfected = request.POST.get('isPerfected')
            isExcludedActivities = int(
                request.POST.get('isExcludedActivities'))
            isNemaCompliant = int(request.POST.get('isNemaCompliant'))
            securityType = request.POST.get('securityType')

        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=loanNo)
    try:
        response = config.CLIENT.service.FnImprestSurrenderLine(
            collateralCode, loanNo, collateralType, maturityDate, collateralValue, isPerfected, isExcludedActivities, isNemaCompliant, securityType, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('LoanLines', pk=loanNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LoanLines', pk=loanNo)
