from django.shortcuts import render, redirect
import requests
from django.conf import settings as config
import json
from django.contrib import messages
import datetime as dt
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from requests import Session

# Create your views here.
def advance(request):
    try:
        fullname =  request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QySalaryAdvances")
        try:
            response = session.get(Access_Point, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            Pending = []
            for imprest in response['value']:
                if imprest['Loan_Status'] == 'Application' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    open.append(json.loads(output_json))
                if imprest['Loan_Status'] == 'Approved' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    Approved.append(json.loads(output_json))
                if imprest['Loan_Status'] == 'Rejected' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    Rejected.append(json.loads(output_json))
                if imprest['Loan_Status'] == 'Being Processed' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
            SalaryProducts = config.O_DATA.format("/QyLoanProductTypes")
            SalaryResponse = session.get(SalaryProducts, timeout=10).json()
            salary = SalaryResponse['value']
            counts = len(open)

            pend = len(Pending)

            counter = len(Approved)

            reject = len(Rejected)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, e)
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

        ctx = {"today": todays_date, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "reject": Rejected,
            "rej": reject, "pend": pend,
            "pending": Pending, "year": year,
            "full": fullname,"salary":salary}
    except KeyError as e:
        print(e)
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request,"advance.html",ctx)

def RequestAdvance(request):
    if request.method == "POST":
        try:
            loanNo = request.POST.get('loanNo')
            employeeNo = request.session['Employee_No_'] 
            productType = request.POST.get('productType')
            amountRequested = float(request.POST.get('amountRequested'))
            myUserId = request.session['User_ID']
            myAction = request.POST.get('myAction')
        except ValueError as e:
            print(e)
            messages.error(request,e)
            return redirect('advance')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnSalaryAdvanceApplication(
                loanNo, employeeNo,productType,amountRequested,myUserId, myAction)
            print(response)
            if response == True:
                messages.success(request, "Request Successful")
                return redirect('advance')
        
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('advance')

def advanceDetail(request,pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        res = ''
        state = ''
        Access_Point = config.O_DATA.format("/QySalaryAdvances")
        Approver = config.O_DATA.format("/QyApprovalEntries")
        try:
            response = session.get(Access_Point, timeout=10).json()
            res_approver = session.get(Approver, timeout=10).json()
            Approvers = []
            for approver in res_approver['value']:
                if approver['Document_No_'] == pk:
                    output_json = json.dumps(approver)
                    Approvers.append(json.loads(output_json))
            for advance in response['value']:
                if advance['Employee_No'] == request.session['Employee_No_'] and advance['Loan_No'] == pk:
                    res = advance
                    state = advance['Loan_Status']

        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request,e)
            return redirect('advance')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res,
            "Approvers": Approvers, "state": state,
            "year": year, "full": fullname,}
    except KeyError as e:
        messages.info(request, "Session Expired. Please Login")
        print(e)
        return redirect('auth')

    return render(request,"advanceDetails.html",ctx)

def FnRequestSalaryAdvanceApproval(request,pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == "POST":
        try:
            response = CLIENT.service.FnRequestSalaryAdvanceApproval(
                request.session['Employee_No_'],pk)
            print(response)
            if response == True:
                messages.success(request, "Approval Request Sent Successfully ")
                return redirect('advance')
        except Exception as e:
            messages.error(request, e)
            print(e)        
    return redirect('advanceDetail', pk=pk)

def FnCancelSalaryAdvanceApproval(request,pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == "POST":
        try:
            response = CLIENT.service.FnCancelSalaryAdvanceApproval(
                request.session['Employee_No_'],pk)
            print(response)
            if response == True:
                messages.success(request, "Approval Request Sent Successfully ")
                return redirect('advance')
        except Exception as e:
            messages.error(request, e)
            print(e)        
    return redirect('advanceDetail', pk=pk)
