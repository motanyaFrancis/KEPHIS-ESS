import base64
from django.shortcuts import render, redirect
from datetime import datetime
import requests
from requests import Session
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import enum
import secrets
import string
from django.http import HttpResponse
import io as BytesIO
from django.template.response import TemplateResponse
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
from django.views import View

# Create your views here.
class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

class ImprestRequisition(UserObjectMixin,View):
    def get(self,request):
        try:
            userID =  request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(f"/Imprests?$filter%20=User_Id%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            openImprest = [x for x in response['value'] if x['Status'] == 'Open']
            Pending = [x for x in response['value'] if x['Status'] == 'Pending Approval']
            Approved = [x for x in response['value'] if x['Status'] == 'Released']

            counts = len(openImprest)

            pend = len(Pending)

            counter = len(Approved)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "res": openImprest,
            "count": counts, "response": Approved,
            "counter": counter, "pend": pend,
            "pending": Pending, "year": year,
            "full": userID}
        return render(request, 'imprestReq.html', ctx)
    def post(self,request):
        if request.method == 'POST':
            try:
                accountNo = request.session['Customer_No_']
                responsibilityCenter = request.session['User_Responsibility_Center']
                usersId = request.session['User_ID']
                personalNo = request.session['Employee_No_']
                imprestNo = request.POST.get('imprestNo')
                travelType = int(request.POST.get('travelType'))
                purpose = request.POST.get('purpose')
                isImprest = eval(request.POST.get('isImprest'))
                isDsa = eval(request.POST.get('isDsa'))
                myAction = request.POST.get('myAction')
                imprestNo = request.POST.get('imprestNo')
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('imprestReq')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            if not imprestNo:
                imprestNo = ""
            if isImprest == False and isDsa == False:
                messages.info(request,"Both DSA and Imprest cannot be empty.")
                return redirect('imprestReq')
            print(travelType)
            try:
                response = config.CLIENT.service.FnImprestHeader(
                    imprestNo, accountNo, responsibilityCenter, travelType, purpose, usersId, personalNo, isImprest, isDsa, myAction)
                messages.success(request, "Request Successful")
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('imprestReq')
        return redirect('imprestReq')


class ImprestDetails(UserObjectMixin, View):
    def get(self, request,pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']


            Access_Point = config.O_DATA.format(f"/Imprests?$filter=No_%20eq%20%27{pk}%27%20and%20User_Id%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for imprest in response['value']:
                res = imprest

            Imprest_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes?$filter=Type%20eq%20%27Imprest%27")
            Imprest_RES = self.get_object(Imprest_Type)
            res_type = [x for x in Imprest_RES['value']]

            Dimension = config.O_DATA.format("/QyDimensionValues")
            Dimension_RES = self.get_object(Dimension)
            Area = [x for x in Dimension_RES['value'] if x['Global_Dimension_No_'] == 1]
            BizGroup = [x for x in Dimension_RES['value'] if x['Global_Dimension_No_'] == 2]

            destination = config.O_DATA.format("/QyDestinations")
            res_dest = self.get_object(destination)
            Local = [x for x in res_dest['value'] if x['Destination_Type'] == 'Local']
            ForegnDest = [x for x in res_dest['value'] if x['Destination_Type'] == 'Foreign']

            Approver = config.O_DATA.format(f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Lines_Res = config.O_DATA.format(f"/QyImprestLines?$filter=AuxiliaryIndex1%20eq%20%27{pk}%27")
            responses = self.get_object(Lines_Res)
            openLines = [x for x in responses['value'] if x['AuxiliaryIndex1'] == pk]

            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            RejectComments = config.O_DATA.format(f"/QyApprovalCommentLines?$filter=Document_No_%20eq%20%27{pk}%27")
            RejectedResponse = self.get_object(RejectComments)
            Comments = [x for x in RejectedResponse['value']]
        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('imprestReq')
                        
        ctx = {"today": self.todays_date, "res": res,"line": openLines,"Approvers": Approvers,
               "type": res_type,"area": Area, "biz": BizGroup,"Local": Local, "year": year,
               "full": userID, "Foreign": ForegnDest, "dest": destination,"file":allFiles,"Comments":Comments}
        return render(request, 'imprestDetail.html', ctx)


def UploadAttachment(request, pk):
    
    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
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
            return redirect('IMPDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('IMPDetails', pk=pk)
    return redirect('IMPDetails', pk=pk)

def FnDeleteImprestLine(request, pk):
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
        except ValueError as e:
            return redirect('IMPDetails', pk=pk)

        try:
            response = config.CLIENT.service.FnDeleteImprestLine(
                lineNo, pk)
            messages.success(request, "Deleted Successfully")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('IMPDetails', pk=pk)
    return redirect('IMPDetails', pk=pk)


def FnGenerateImprestReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':

        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateImprestReport(
                request.session['Employee_No_'], filenameFromApp, pk)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('auth')
    return redirect('IMPDetails', pk=pk)

def DeleteImprestAttachment(request,pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID= int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk,docID,tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('IMPDetails', pk=pk)

def FnRequestPaymentApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPDetails', pk=pk)
        try:
            response = CLIENT.service.FnRequestPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('auth')
    return redirect('IMPDetails', pk=pk)


def FnCancelPaymentApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('auth')
    return redirect('IMPDetails', pk=pk)


def CreateImprestLines(request, pk):
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            destination = request.POST.get('destination')
            imprestTypes = request.POST.get('imprestType')
            requisitionType = request.POST.get('requisitionType')
            DSAType= request.POST.get('DSAType')
            travelDate = datetime.strptime(
                request.POST.get('travel'), '%Y-%m-%d').date()
            amount = float(request.POST.get("amount"))
            returnDate = datetime.strptime(
                request.POST.get('returnDate'), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('IMPDetails', pk=pk)

        class Data(enum.Enum):
            values = imprestTypes
        imprestType = (Data.values).value

        if not amount:
            amount = 0
        
        if not imprestType:
            messages.info(request,"Both Imprest and DSA can't be empty.")
            return redirect('IMPDetails', pk=pk)

        if DSAType:
            requisitionType = DSAType
        try:
            response = config.CLIENT.service.FnImprestLine(
                lineNo, pk, imprestType, destination, travelDate, returnDate, requisitionType, float(amount), myAction)
            messages.success(request, "Request Successful")
            print(response)
            return redirect('IMPDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('IMPDetails', pk=pk)
    return redirect('IMPDetails', pk=pk)

class ImprestSurrender(UserObjectMixin,View):
    def get(self,request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(f"/QyImprestSurrenders?$filter=User_Id%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            openSurrender = [x for x in response['value'] if x['Status'] == 'Open']
            Pending = [x for x in response['value'] if x['Status'] == 'Pending Approval']
            Approved = [x for x in response['value'] if x['Status'] == 'Released']

            Released_imprest = config.O_DATA.format(f"/Imprests?$filter=User_Id%20eq%20%27{userID}%27%20and%20Status%20eq%20%27Released%27")
            Released = self.get_object(Released_imprest)
            APPImp=[x for x in Released['value'] if x['Imprest'] == True and x['Surrendered'] ==False and x['Posted'] == True ]

            counts = len(openSurrender)

            counter = len(Approved)

            pend = len(Pending)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "res": openSurrender,
            "count": counts, "full": userID,
            "response": Approved, "counter": counter,
            "app": APPImp, "year": year,
            "pend": pend, "pending": Pending}
        
        return render(request, 'imprestSurr.html', ctx)
    def post(self,request):
        if request.method == 'POST':
            try:
                usersId = request.session['User_ID']
                staffNo = request.session['Employee_No_']
                accountNo = request.session['Customer_No_']
                surrenderNo = request.POST.get('surrenderNo')
                imprestIssueDocNo = request.POST.get('imprestIssueDocNo')
                purpose = request.POST.get('purpose')
                myAction = request.POST.get('myAction')
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('imprestSurr')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            if not surrenderNo:
                surrenderNo = " "
            try:
                response = config.CLIENT.service.FnImprestSurrenderHeader(
                    surrenderNo, imprestIssueDocNo, accountNo, purpose, usersId, staffNo, myAction)
                messages.success(request, "Request Successful")
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('imprestSurr')
        return redirect('imprestSurr')
    


class SurrenderDetails(UserObjectMixin, View):
    def get(self, request,pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
 

            Access_Point = config.O_DATA.format(f"/QyImprestSurrenders?$filter=No_%20eq%20%27{pk}%27%20and%20User_Id%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for imprest in response['value']:
                res = imprest

            Imprest_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes?$filter=Type%20eq%20%27Imprest%27")
            Imprest_RES = self.get_object(Imprest_Type)
            res_type = [x for x in Imprest_RES['value']]

            Approver = config.O_DATA.format(f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            RejectComments = config.O_DATA.format(f"/QyApprovalCommentLines?$filter=Document_No_%20eq%20%27{pk}%27")
            RejectedResponse = self.get_object(RejectComments)
            Comments = [x for x in RejectedResponse['value']]

            Lines_Res = config.O_DATA.format(f"/QyImprestSurrenderLines?$filter=No%20eq%20%27{pk}%27")
            responses = self.get_object(Lines_Res)
            openLines = [x for x in responses['value'] if x['No'] == pk]
  

        except requests.exceptions.ConnectionError as e:
            print(e)
            return redirect('imprestSurr')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "res": res,"line": openLines,
            "Approvers": Approvers, "type": res_type, "year": year, "full": userID,"file":allFiles,"Comments":Comments}
        
        return render(request, 'SurrenderDetail.html', ctx)
    def post(self, request,pk):
        if request.method == 'POST':
            try:
                lineNo = int(request.POST.get('lineNo'))
                actualSpent = float(request.POST.get('actualSpent'))
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('IMPDetails', pk=pk)
            try:
                response = config.CLIENT.service.FnImprestSurrenderLine(
                    lineNo, pk, actualSpent)
                messages.success(request, "Request Successful")
                print(response)
                return redirect('IMPSurrender', pk=pk)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('IMPSurrender', pk=pk)
        return redirect('IMPSurrender', pk=pk)


def UploadSurrenderAttachment(request, pk):
    if request.method == "POST":
        try:
            tableID = 52177430
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPSurrender', pk=pk)
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
            return redirect('IMPSurrender', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('IMPSurrender', pk=pk)
    return redirect('IMPSurrender', pk=pk)

def DeleteSurrenderAttachment(request,pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID= int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk,docID,tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('IMPSurrender', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('IMPSurrender', pk=pk)

def FnGenerateImprestSurrenderReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':
        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateImprestSurrenderReport(
                pk, filenameFromApp)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('IMPSurrender', pk=pk)
    return redirect('IMPSurrender', pk=pk)


def SurrenderApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPSurrender', pk=pk)
        try:
            response = CLIENT.service.FnRequestPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('IMPSurrender', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('IMPSurrender', pk=pk)


def FnCancelSurrenderApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('IMPSurrender', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Cancel Approval Successful !!")
            print(response)
            return redirect('IMPSurrender', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('IMPSurrender', pk=pk)


class StaffClaim(UserObjectMixin,View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(f"/QyStaffClaims?$filter=User_Id%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            openClaim = [x for x in response['value'] if x['Status'] == 'Open']
            Pending = [x for x in response['value'] if x['Status'] == 'Pending Approval']
            Approved = [x for x in response['value'] if x['Status'] == 'Released']

            Claim = config.O_DATA.format("/QyImprestSurrenders")
            res_claim = self.get_object(Claim)
            My_Claim = [x for x in res_claim['value'] if x['Actual_Amount_Spent'] > x['Imprest_Amount']]
                

            counts = len(openClaim)
            counter = len(Approved)
            pend = len(Pending)
        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.info(request,e)
            return redirect('auth')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "res": openClaim,
            "count": counts,"response": Approved, "claim": counter,
            "my_claim": My_Claim,"pend": pend,
            "year": year, "pending": Pending,
            "full": userID}
        return render(request, 'staffClaim.html', ctx)
    def post(self,request):
        if request.method == 'POST':
            accountNo = request.session['Customer_No_']
            usersId = request.session['User_ID']
            staffNo = request.session['Employee_No_']
            claimNo = request.POST.get('claimNo')
            claimType = int(request.POST.get('claimType'))
            imprestSurrDocNo = request.POST.get('imprestSurrDocNo')
            purpose = request.POST.get('purpose')
            myAction = request.POST.get('myAction')
            if not claimNo:
                claimNo = " "
            if not imprestSurrDocNo:
                imprestSurrDocNo = " "
            try:
                response = config.CLIENT.service.FnStaffClaimHeader(
                    claimNo, claimType, accountNo, purpose, usersId, staffNo, imprestSurrDocNo, myAction)
                messages.success(request, "Request Successful")
                print(response)
                return redirect('claim')
            except Exception as e:
                messages.error(request, e)
                print(e)
        return redirect('claim')


class ClaimDetails(UserObjectMixin, View):
    def get(self, request,pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(f"/QyStaffClaims?$filter=No_%20eq%20%27{pk}%27%20and%20User_Id%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for claim in response['value']:
                res = claim

            Claim_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes?$filter=Type%20eq%20%27Claim%27")
            Claim_RES = self.get_object(Claim_Type)
            res_type = [x for x in Claim_RES['value']]
            
            Approver = config.O_DATA.format(f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            RejectComments = config.O_DATA.format(f"/QyApprovalCommentLines?$filter=Document_No_%20eq%20%27{pk}%27")
            RejectedResponse = self.get_object(RejectComments)
            Comments = [x for x in RejectedResponse['value']]

            Lines_Res = config.O_DATA.format(f"/QyStaffClaimLines?$filter=No%20eq%20%27{pk}%27")
            res_Line = self.get_object(Lines_Res)
            openLines = [x for x in res_Line['value'] if x['No'] == pk]
 
        except requests.exceptions.ConnectionError as e:
            print(e)
            return redirect('claim')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "res": res,
              "res_type": res_type,"Approvers": Approvers, "line": openLines,
            "year": year, "full": userID,"file":allFiles,"Comments":Comments}
        
        return render(request, "ClaimDetail.html", ctx)


def CreateClaimLines(request, pk):
    lineNo = ""
    claimNo = pk
    claimType = ""
    
    amount = ""
    claimReceiptNo = ""
    dimension3 = ''
    expenditureDate = ""
    expenditureDescription = ""
    myAction = ''
    if request.method == 'POST':
        try:
            accountNo = request.session['Customer_No_']
            lineNo = int(request.POST.get('lineNo'))
            claimType = request.POST.get('claimType')
            amount = float(request.POST.get('amount'))
            expenditureDate = datetime.strptime(
                request.POST.get('expenditureDate'), '%Y-%m-%d').date()
            expenditureDescription = request.POST.get('expenditureDescription')
            attach = request.FILES.getlist('attachment')
            myAction = request.POST.get('myAction')
            tableID = 52177431
        except Exception as e:
            messages.error(request, "Invalid Input.")
            return redirect('ClaimDetail', pk=pk)

        try:
            response = config.CLIENT.service.FnStaffClaimLine(
                lineNo, claimNo, claimType, accountNo, amount, claimReceiptNo, dimension3, expenditureDate, expenditureDescription, myAction)
            print(response)
            if response != 0:
                for files in attach:
                    fileName = request.FILES['attachment'].name
                    attachment = base64.b64encode(files.read())
                    try:
                        responses = config.CLIENT.service.FnUploadAttachedDocument(
                            pk +'#'+str(response), fileName, attachment, tableID,request.session['User_ID'])
                        if responses == True:
                            messages.success(request, "Request Successful")
                            return redirect('ClaimDetail', pk=pk)
                        else:
                            messages.error(request, "Failed, Try Again")
                            return redirect('ClaimDetail', pk=pk)
                    except Exception as e:
                        messages.error(request, e)
                        print(e)

        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)


def ClaimApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('ClaimDetail', pk=pk)
        try:
            response = CLIENT.service.FnRequestPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Approval Request Sent Successfully")
            print(response)
            return redirect('ClaimDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)

def DeleteClaimAttachment(request,pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID= int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk,docID,tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('ClaimDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)

def FnCancelClaimApproval(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            return redirect('ClaimDetail', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelPaymentApproval(
                request.session['Employee_No_'], requisitionNo)
            messages.success(request, "Cancel Approval Successful !!")
            print(response)
            return redirect('ClaimDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)

def FnDeleteStaffClaimLine(request, pk):
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeleteStaffClaimLine(lineNo,
                                                                    pk)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)


def FnGenerateStaffClaimReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    if request.method == 'POST':
        filenameFromApp = pk + str(nameChars) + ".pdf"
        try:
            response = config.CLIENT.service.FnGenerateStaffClaimReport(
                request.session['Employee_No_'], filenameFromApp, pk)
            messages.success(request, "Successfully Sent!!")
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ClaimDetail', pk=pk)
