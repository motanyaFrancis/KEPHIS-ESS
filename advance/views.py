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
from django.views import View
import base64

# Create your views here.
class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response
        
class advance(UserObjectMixin,View):
    def get(self,request):
        try:
            fullname =  request.session['User_ID']
            year = request.session['years']
            empNo =request.session['Employee_No_']

            Access_Point = config.O_DATA.format(f"/QySalaryAdvances?$filter=Employee_No%20eq%20%27{empNo}%27")
            response = self.get_object(Access_Point)
            # print(response)
            openAdvance = [x for x in response['value'] if x['Loan_Status'] == 'Application']
            Pending = [x for x in response['value'] if x['Loan_Status'] == 'Being Processed']
            Approved = [x for x in response['value'] if x['Loan_Status'] == 'Approved']

            SalaryProducts = config.O_DATA.format("/QyLoanProductTypes")
            SalaryResponse = self.get_object(SalaryProducts)
            salary = SalaryResponse['value']

            counts = len(openAdvance)
            pend = len(Pending)
            counter = len(Approved)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, e)
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print(e)
            messages.error(request,e)
            return redirect('auth')
        ctx = {
            "today": self.todays_date, 
            "res": openAdvance,
            "count": counts, "response": Approved,
            "counter": counter,"pend": pend,
            "pending": Pending, "year": year,
            "full": fullname,"salary":salary}
        return render(request,"advance.html",ctx)
    def post(self, request):
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

class advanceDetail(UserObjectMixin,View):
    def get(self, request,pk):
        try:
            fullname = request.session['User_ID']
            year = request.session['years']
            empNo =request.session['Employee_No_']

            Access_Point = config.O_DATA.format(f"/QySalaryAdvances?$filter=Employee_No%20eq%20%27{empNo}%27%20and%20Loan_No%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for advance in response['value']:
                res = advance
                state = advance['Loan_Status']

            Approver = config.O_DATA.format(f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            RejectComments = config.O_DATA.format(f"/QyApprovalCommentLines?$filter=Document_No_%20eq%20%27{pk}%27")
            RejectedResponse = self.get_object(RejectComments)
            Comments = [x for x in RejectedResponse['value']]

            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request,e)
            return redirect('advance')
        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            print(e)
            return redirect('auth')
        except Exception as e:
                messages.error(request, e)
                print(e)
        ctx = {"today": self.todays_date, "res": res,
                "Approvers": Approvers, "state": state,"file":allFiles,
                "year": year, "full": fullname,"Comments":Comments}

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

def UploadAdvanceAttachment(request, pk):
    if request.method == "POST":
        try:
            tableID = 52177630
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('advanceDetail', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('advanceDetail', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('advanceDetail', pk=pk)
    return redirect('advanceDetail', pk=pk)

def DeleteAdvanceAttachment(request,pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID= int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk,docID,tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully")
                return redirect('advanceDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('advanceDetail', pk=pk)
