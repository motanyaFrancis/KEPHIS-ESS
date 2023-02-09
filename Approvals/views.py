from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import io as BytesIO
import base64
from django.http import HttpResponse
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

class Approve(UserObjectMixin,View):
    def get(self,request):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['mechanical_inspector_role']
            full_name = request.session['full_name']
          

            Access_Point = config.O_DATA.format(f"/QyApprovalEntries?$filter=Approver_ID%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)

            openLeave = [x for x in response['value'] if (x['Status'] == 'Open' and x['Document_Type']=='LeaveApplication') or (x['Status']=='Open' and x['Document_Type']=='TrainingRequest')]
            approvedLeave = [x for x in response['value'] if (x['Status'] == 'Approved' and x['Document_Type']=='LeaveApplication') or (x['Status']=='Approved' and x['Document_Type']=='TrainingRequest')]
            rejectedLeave = [x for x in response['value'] if (x['Status'] == 'Rejected' and x['Document_Type']=='LeaveApplication') or (x['Status']=='Rejected' and x['Document_Type']=='TrainingRequest')]

            # Imprests
            openImp = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='Imprest']
            approvedImp = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='Imprest']
            rejectedImp = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='Imprest']

            # Surrender
            openSurrender = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='Imprest Surrender']
            approveSurrender = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='Imprest Surrender']
            rejectSurrender = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='Imprest Surrender']

            # Staff Claim
            openClaim = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='Staff Claim']
            approveClaim = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='Staff Claim']
            rejectClaim = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='Staff Claim']

            # Purchase Request
            openPurchase = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='Purchase Requisitions']
            approvePurchase = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='Purchase Requisitions']
            rejectPurchase = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='Purchase Requisitions']

            # Repair Request
            openRepair = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='Repair']
            appRepair = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='Repair']
            rejRepair = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='Repair']

            # Store Request
            openStore = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='Store Requisitions']
            appStore = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='Store Requisitions']
            rejStore = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='Store Requisitions']

            # Other Request
            openOther = [x for x in response['value'] if (x['Status'] == 'Open' and x['Document_Type']=='Payment Voucher') or (x['Status']=='Open' and x['Document_Type']=='Petty Cash') or (x['Status']=='Open' and x['Document_Type']=='Petty Cash Surrender') or (x['Status']=='Open' and x['Document_Type']=='Staff Payroll Approval') or (x['Status']=='Open' and x['Document_Type']=='Invoice') or (x['Status']=='Open' and x['Document_Type']=='Order')]
            appOther = [x for x in response['value'] if (x['Status'] == 'Approved' and x['Document_Type']=='Payment Voucher') or (x['Status']=='Approved' and x['Document_Type']=='Petty Cash') or (x['Status']=='Approved' and x['Document_Type']=='Petty Cash Surrender') or (x['Status']=='Approved' and x['Document_Type']=='Staff Payroll Approval') or (x['Status']=='Approved' and x['Document_Type']=='Invoice') or (x['Status']=='Approved' and x['Document_Type']=='Order')]
            rejOther = [x for x in response['value'] if (x['Status'] == 'Rejected' and x['Document_Type']=='Payment Voucher') or (x['Status']=='Rejected' and x['Document_Type']=='Petty Cash') or (x['Status']=='Rejected' and x['Document_Type']=='Petty Cash Surrender') or (x['Status']=='Rejected' and x['Document_Type']=='Staff Payroll Approval') or (x['Status']=='Rejected' and x['Document_Type']=='Invoice') or (x['Status']=='Rejected' and x['Document_Type']=='Order')]

            #Vehicle Inspection
            openInspection = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='VehicleInspection']
            appInspection = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='VehicleInspection']
            rejInspection = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='VehicleInspection']
            
            #Work Ticket
            openTickets = [x for x in response['value'] if x['Status'] == 'Open' and x['Document_Type']=='WorkTicketReplacement']
            appTickets = [x for x in response['value'] if x['Status'] == 'Approved' and x['Document_Type']=='WorkTicketReplacement']
            rejTickets = [x for x in response['value'] if x['Status'] == 'Rejected' and x['Document_Type']=='WorkTicketReplacement']

            countIMP = len(openImp)
            CountLeave = len(openLeave)
            countSurrender = len(openSurrender)
            countClaim = len(openClaim)
            countPurchase = len(openPurchase)
            countRepair = len(openRepair)
            countStore = len(openStore)
            countOther = len(openOther)
            countInspection = len(openInspection)
            countTickets = len(openTickets)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, f'{e}')
            return redirect('auth')
        except KeyError as e:
            print (e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth') 

        ctx = {
            "today": self.todays_date, "imprest": openImp, "full": userID,
            "countIMP": countIMP, "approvedIMP":approvedImp,"rejectedImp":rejectedImp,
            "openLeave":openLeave,"CountLeave":CountLeave,"approvedLeave":approvedLeave,
            "rejectedLeave":rejectedLeave,"openSurrender":openSurrender,"countSurrender":countSurrender,"approveSurrender":approveSurrender,"rejectSurrender":rejectSurrender,
            "countClaim":countClaim,"openClaim":openClaim,"approveClaim":approveClaim,"rejectClaim":rejectClaim,
            "countPurchase":countPurchase,"openPurchase":openPurchase,"approvePurchase":approvePurchase,
            "rejectPurchase":rejectPurchase, "countRepair":countRepair,"appRepair":appRepair,"rejRepair":rejRepair,
            "countStore":countStore,"openStore":openStore,"appStore":appStore,"rejStore":rejStore,
            "countInspection":countInspection,"openInspection": openInspection, "appInspection": appInspection, "rejInspection": rejInspection,
            "openTickets":openTickets,"appTickets":appTickets,"rejTickets":rejTickets,"countTickets":countTickets,
            "openOther":openOther,"appOther":appOther,"rejOther":rejOther,"countOther":countOther,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
            "mechanical_inspector_role":mechanical_inspector_role
            }
              
        return render(request, 'Approve.html', ctx)


class ApproveDetails(UserObjectMixin, View):
    def get(self, request,pk):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['mechanical_inspector_role']
            full_name = request.session['full_name']
            data = ''
            state = ''
            res ={}
  
            Access_Point = config.O_DATA.format(f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27%20and%20Approver_ID%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for approve in response['value']:
                res = approve
            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            Imprest = config.O_DATA.format(f"/Imprests?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            ImprestResponse = self.get_object(Imprest)
            for imprest in ImprestResponse['value']:
                data = imprest
                state = 1

            Leave_Request = config.O_DATA.format(f"/QyLeaveApplications?$filter=Application_No%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            LeaveResponse = self.get_object(Leave_Request)
            for leave in LeaveResponse['value']:
                data = leave
                state = 2

            TrainingRequest = config.O_DATA.format(f"/QyTrainingRequests?$filter=Request_No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            TrainResponse = self.get_object(TrainingRequest)
            for train in TrainResponse['value']:
                data = train
                state = 3

            SurrenderRequest = config.O_DATA.format(f"/QyImprestSurrenders?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            SurrenderResponse = self.get_object(SurrenderRequest)
            for imprest in SurrenderResponse['value']:
                data = imprest
                state = 4
            Lines_Surrender = config.O_DATA.format(f"/QyImprestSurrenderLines?$filter=No%20eq%20%27{pk}%27")
            ResponseSurrenderLines = self.get_object(Lines_Surrender)
            SurrenderLines = [x for x in ResponseSurrenderLines['value'] if x['No'] == pk]

            ClaimRequest = config.O_DATA.format(f"/QyStaffClaims?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            ClaimResponse = self.get_object(ClaimRequest)
            for claim in ClaimResponse['value']:
                data = claim
                state = 5
            Lines_Claim = config.O_DATA.format(f"/QyStaffClaimLines?$filter=No%20eq%20%27{pk}%27")
            ClaimLineResponse = self.get_object(Lines_Claim)
            ClaimLines = [x for x in ClaimLineResponse['value'] if x['No'] == pk]

            PurchaseRequest = config.O_DATA.format(f"/QyPurchaseRequisitionHeaders?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            PurchaseResponse = self.get_object(PurchaseRequest)
            for purchase in PurchaseResponse['value']:
                data = purchase
                state = 6
            Lines_Purchase = config.O_DATA.format(f"/QyPurchaseRequisitionLines?$filter=AuxiliaryIndex1%20eq%20%27{pk}%27")
            PurchaseLineResponse = self.get_object(Lines_Purchase)
            PurchaseLines = [x for x in PurchaseLineResponse['value'] if x['AuxiliaryIndex1'] == pk]
            

            ImprestLineRequest=config.O_DATA.format(f"/QyImprestLines?$filter=AuxiliaryIndex1%20eq%20%27{pk}%27")
            ResponseImprestLine = self.get_object(ImprestLineRequest)
            ImprestLine = [x for x in ResponseImprestLine['value'] if x['AuxiliaryIndex1'] == pk]


            TrainingLineRequest=config.O_DATA.format(f"/QyTrainingNeedsRequest?$filter=Source_Document_No%20eq%20%27{pk}%27")
            TrainLineResponse = self.get_object(TrainingLineRequest)
            TrainLine = [x for x in TrainLineResponse['value'] if x['Source_Document_No'] == pk]

            RepairRequest = config.O_DATA.format(f"/QyRepairRequisitionHeaders?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            RepairResponse = self.get_object(RepairRequest)
            for repair in RepairResponse['value']:
                data = repair
                state = 7
            Lines_Repair = config.O_DATA.format(f"/QyRepairRequisitionLines?$filter=AuxiliaryIndex1%20eq%20%27{pk}%27")
            RepairLineResponse = self.get_object(Lines_Repair)
            RepairLines = [x for x in RepairLineResponse['value'] if x['AuxiliaryIndex1'] == pk]

            StoreRequest = config.O_DATA.format(f"/QyStoreRequisitionHeaders?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            StoreResponse = self.get_object(StoreRequest)
            for store in StoreResponse['value']:
                data = store
                state = 8 
            Lines_Store = config.O_DATA.format(f"/QyStoreRequisitionLines?$filter=AuxiliaryIndex1%20%20eq%20%27{pk}%27")
            StoreLineResponse = self.get_object(Lines_Store)
            StoreLines =  [x for x in StoreLineResponse['value'] if x['AuxiliaryIndex1'] == pk]

            VoucherRequest = config.O_DATA.format(f"/QyPaymentVoucherHeaders?$filter=No_%20eq%20%27{pk}%27")
            VoucherResponse = self.get_object(VoucherRequest)
            for voucher in VoucherResponse['value']:
                data = voucher
                state = "voucher"
            Lines_Voucher = config.O_DATA.format(f"/QyPaymentVoucherLines?$filter=No%20eq%20%27{pk}%27")
            VoucherLineResponse = self.get_object(Lines_Voucher)
            VoucherLines = [x for x in VoucherLineResponse['value'] if x['No'] == pk]

            PettyRequest = config.O_DATA.format(f"/QyPettyCashHeaders?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            PettyResponse = self.get_object(PettyRequest)
            for petty in PettyResponse['value']:
                data = petty
                state = "petty cash"
            Lines_Petty = config.O_DATA.format("/QyPettyCashLines")
            PettyLineResponse = self.get_object(Lines_Petty)
            PettyLines = [x for x in PettyLineResponse['value'] if x['No'] == pk]

            PettySurrenderRequest = config.O_DATA.format(f"/QyPettyCashSurrenderHeaders?$filter=No_%20eq%20%27{pk}%27%20and%20Status%20eq%20%27Pending%20Approval%27")
            PettySurrenderResponse = self.get_object(PettySurrenderRequest)
            for pettySurrender in PettySurrenderResponse['value']:
                data = pettySurrender
                state = "petty cash surrender"
            Lines_PettySurrender = config.O_DATA.format(f"/QyPettyCashSurrenderLines?$filter=No%20eq%20%27{pk}%27")
            PettySurrenderLineResponse = self.get_object(Lines_PettySurrender)
            PettySurrenderLines = [x for x in PettySurrenderLineResponse['value'] if x['No'] == pk]

            advanceRequest = config.O_DATA.format(f"/QySalaryAdvances?$filter=Loan_No%20eq%20%27{pk}%27")
            advanceResponse = self.get_object(advanceRequest)
            for advance in advanceResponse['value']:
                data = advance
                state = "advance"               
                
                
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, f'{e}')
            return redirect('approve')
        except KeyError as e:
            messages.info(request, f"{e}")
            print(e)
            return redirect('auth')
        except Exception as e:
            messages.info(request,f'{e}')
            return redirect('auth')

        ctx = {
            "today": self.todays_date,
            "res": res, "file":allFiles,"data":data,
            "state":state,"ImpLine":ImprestLine,
            "TrainLine":TrainLine,
            "SurrenderLines":SurrenderLines,
            "ClaimLines":ClaimLines,"PurchaseLines":PurchaseLines,
            "RepairLines":RepairLines,"StoreLines":StoreLines,
            "VoucherLines":VoucherLines,
            "PettyLines":PettyLines,"PettySurrenderLines":PettySurrenderLines,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
            "mechanical_inspector_role":mechanical_inspector_role
            }
        return render(request, 'approveDetails.html', ctx)


def All_Approved(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    entryNo = ''
    approvalComments = ""
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            myUserID = request.session['User_ID']
            myAction = 'approve'
            documentNo = pk
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, myUserID, approvalComments, myAction)
            messages.success(request, "Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            print(e)
            messages.info(request, f'{e}')
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)


def Rejected(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    entryNo = ''
    approvalComments = ""
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            approvalComments = request.POST.get('approvalComments')
            myAction = 'reject'
            documentNo = pk
            userID = request.session['User_ID']
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('ApproveData', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, userID, approvalComments, myAction)
            messages.success(request, "Reject Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            messages.info(request, f'{e}')
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)

def viewDocs(request,pk,id):
    if request.method == 'POST':
        docNo = pk
        attachmentID = int(request.POST.get('attachmentID'))
        File_Name = request.POST.get('File_Name')
        File_Extension = request.POST.get('File_Extension')
        tableID = int(id)

        try:
            response = config.CLIENT.service.FnGetDocumentAttachment(
                docNo, attachmentID, tableID)
            
            filenameFromApp = File_Name + "." + File_Extension
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/ms-excel",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.info(request, f'{e}')
            return redirect('auth')
    return redirect('auth')