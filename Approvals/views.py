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

from HR.views import Training_Request

# Create your views here.


def Approve(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyApprovalEntries")
        try:
            response = session.get(Access_Point, timeout=10).json()
            openLeave = []
            approvedLeave = []
            rejectedLeave = []
            openSurrender = []
            approveSurrender = []
            rejectSurrender = []
            openClaim = []
            approveClaim = []
            rejectClaim = []
            openPurchase = []
            approvePurchase = []
            rejectPurchase = []
            openRepair = []
            appRepair = []
            rejRepair = []
            openStore = []
            appStore = []
            rejStore = []

            openImp = []
            approvedImp = []
            rejectedImp = []
            openOther = []
            appOther = []
            rejOther = []
            for approve in response['value']:
                # HR
                if  (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open'  and approve['Document_Type'] == 'LeaveApplication') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'TrainingRequest'):
                    output_json = json.dumps(approve)
                    openLeave.append(json.loads(output_json))
                if (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved' and approve['Document_Type'] == 'LeaveApplication') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'TrainingRequest'):
                    output_json = json.dumps(approve)
                    approvedLeave.append(json.loads(output_json))
                if (approve['Approver_ID'] == request.session['User_ID'] and  approve['Status'] == 'Rejected' and approve['Document_Type'] == 'LeaveApplication') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'TrainingRequest'):
                    output_json = json.dumps(approve)
                    rejectedLeave.append(json.loads(output_json))

                # Imprests
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Imprest':
                    output_json = json.dumps(approve)
                    openImp.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Imprest':
                    output_json = json.dumps(approve)
                    approvedImp.append(json.loads(output_json))
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Imprest':
                    output_json = json.dumps(approve)
                    rejectedImp.append(json.loads(output_json))
                # Surrender
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Imprest Surrender':
                    output_json = json.dumps(approve)
                    openSurrender.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Imprest Surrender':
                    output_json = json.dumps(approve)
                    approveSurrender.append(json.loads(output_json))
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Imprest Surrender':
                    output_json = json.dumps(approve)
                    rejectSurrender.append(json.loads(output_json))
                # Staff Claim
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Staff Claim':
                    output_json = json.dumps(approve)
                    openClaim.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Staff Claim':
                    output_json = json.dumps(approve)
                    approveClaim.append(json.loads(output_json))
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Staff Claim':
                    output_json = json.dumps(approve)
                    rejectClaim.append(json.loads(output_json))
                # Purchase Request
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Purchase Requisitions':
                    output_json = json.dumps(approve)
                    openPurchase.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Purchase Requisitions':
                    output_json = json.dumps(approve)
                    approvePurchase.append(json.loads(output_json))
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Purchase Requisitions':
                    output_json = json.dumps(approve)
                    rejectPurchase.append(json.loads(output_json))
                # Repair Request
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Repair':
                    output_json = json.dumps(approve)
                    openRepair.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Repair':
                    output_json = json.dumps(approve)
                    appRepair.append(json.loads(output_json))
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Repair':
                    output_json = json.dumps(approve)
                    rejRepair.append(json.loads(output_json))
                # Store Request
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Store Requisitions':
                    output_json = json.dumps(approve)
                    openStore.append(json.loads(output_json))
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Store Requisitions':
                    output_json = json.dumps(approve)
                    appStore.append(json.loads(output_json))
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID'] and approve['Document_Type'] == 'Store Requisitions':
                    output_json = json.dumps(approve)
                    rejRepair.append(json.loads(output_json))
                # Other Request
                if (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'Payment Voucher') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and  approve['Document_Type'] == 'Petty Cash') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'Petty Cash Surrender') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'Staff Payroll Approval') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open'  and approve['Document_Type'] == 'Invoice') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Open' and approve['Document_Type'] == 'Order'):
                    output_json = json.dumps(approve)
                    openOther.append(json.loads(output_json))
                if (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved' and approve['Document_Type'] == 'Payment Voucher') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved' and  approve['Document_Type'] == 'Petty Cash') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved' and approve['Document_Type'] == 'Petty Cash Surrender') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved' and approve['Document_Type'] == 'Staff Payroll Approval') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved'  and approve['Document_Type'] == 'Invoice') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Approved' and approve['Document_Type'] == 'Order'):
                    output_json = json.dumps(approve)
                    appOther.append(json.loads(output_json))
                if (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Rejected' and approve['Document_Type'] == 'Payment Voucher') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Rejected' and  approve['Document_Type'] == 'Petty Cash') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Rejected' and approve['Document_Type'] == 'Petty Cash Surrender') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Rejected' and approve['Document_Type'] == 'Staff Payroll Approval') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Rejected'  and approve['Document_Type'] == 'Invoice') or (approve['Approver_ID'] == request.session['User_ID'] and approve['Status'] == 'Rejected' and approve['Document_Type'] == 'Order'):
                    output_json = json.dumps(approve)
                    rejOther.append(json.loads(output_json))
            countIMP = len(openImp)
            CountLeave = len(openLeave)
            countSurrender = len(openSurrender)
            countClaim = len(openClaim)
            countPurchase = len(openPurchase)
            countRepair = len(openRepair)
            countStore = len(openStore)
            countOther = len(openOther)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, e)
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "imprest": openImp,"year": year, "full": fullname,
            "countIMP": countIMP, "approvedIMP":approvedImp,"rejectedImp":rejectedImp,
            "openLeave":openLeave,"CountLeave":CountLeave,"approvedLeave":approvedLeave,
            "rejectedLeave":rejectedLeave,"openSurrender":openSurrender,"countSurrender":countSurrender,"approveSurrender":approveSurrender,"rejectSurrender":rejectSurrender,
            "countClaim":countClaim,"openClaim":openClaim,"approveClaim":approveClaim,"rejectClaim":rejectClaim,
            "countPurchase":countPurchase,"openPurchase":openPurchase,"approvePurchase":approvePurchase,
            "rejectPurchase":rejectPurchase, "countRepair":countRepair,"appRepair":appRepair,"rejRepair":rejRepair,
            "countStore":countStore,"openStore":openStore,"appStore":appStore,"rejStore":rejStore,
            "openOther":openOther,"appOther":appOther,"rejOther":rejOther,"countOther":countOther}
    except KeyError as e:
        print (e)
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')       
    return render(request, 'Approve.html', ctx)


def ApproveDetails(request, pk):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        res = ''
        data =''
        state =''
        Access_Point = config.O_DATA.format("/QyApprovalEntries")
        Access_File = config.O_DATA.format("/QyDocumentAttachments")
        Imprest = config.O_DATA.format("/Imprests")
        Leave_Request = config.O_DATA.format("/QyLeaveApplications")
        TrainingRequest = config.O_DATA.format("/QyTrainingRequests")
        SurrenderRequest = config.O_DATA.format("/QyImprestSurrenders")
        ClaimRequest = config.O_DATA.format("/QyStaffClaims")
        PurchaseRequest = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
        ImprestLineRequest=config.O_DATA.format("/QyImprestLines")
        TrainingLineRequest=config.O_DATA.format("/QyTrainingNeedsRequest")

        try:
            response = session.get(Access_Point, timeout=10).json()
            Approves = []
            Imprests = []
            Leaves = []
            Training = []
            Surrender = []
            Claims = []
            ImprestLine = []
            TrainLine = []
    
            for approve in response['value']:
                if approve['Status'] == 'Open' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approves.append(json.loads(output_json))
                    for claim in Approves:
                        if claim['Document_No_'] == pk:
                            res = claim
                if approve['Status'] == 'Approved' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approves.append(json.loads(output_json))
                    for claim in Approves:
                        if claim['Document_No_'] == pk:
                            res = claim
                if approve['Status'] == 'Rejected' and approve['Approver_ID'] == request.session['User_ID']:
                    output_json = json.dumps(approve)
                    Approves.append(json.loads(output_json))
                    for claim in Approves:
                        if claim['Document_No_'] == pk:
                            res = claim
            allFiles = []

            res_file = session.get(Access_File, timeout=10).json()
            for file in res_file['value']:
                if file['No_'] == pk:
                    output_json = json.dumps(file)
                    allFiles.append(json.loads(output_json))
            ImprestResponse = session.get(Imprest, timeout=10).json()
            for imprest in ImprestResponse['value']:
                if imprest['Status'] == "Pending Approval":
                    output_json = json.dumps(imprest)
                    Imprests.append(json.loads(output_json))
                    for imprest in Imprests:
                        if imprest['No_'] == pk:
                            data = imprest
                            if imprest['Status'] == 'Pending Approval':
                                state = 1
            ImpLineResponse = session.get(ImprestLineRequest, timeout=10).json()
            for imprest in ImpLineResponse['value']:
                if imprest['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(imprest)
                    ImprestLine.append(json.loads(output_json))

            LeaveResponse = session.get(Leave_Request, timeout=10).json()
            for leave in LeaveResponse['value']:
                if leave['Status'] == "Pending Approval":
                    output_json = json.dumps(leave)
                    Leaves.append(json.loads(output_json))
                    for myLeave in Leaves:
                        if myLeave['Application_No'] == pk:
                            data = myLeave
                            if myLeave['Status'] == 'Pending Approval':
                                state = 2

            TrainResponse = session.get(TrainingRequest, timeout=10).json()
            for train in TrainResponse['value']:
                if train['Status'] == 'Pending Approval':
                    output_json = json.dumps(train)
                    Training.append(json.loads(output_json))
                    for trains in Training:
                        if trains['Request_No_'] == pk:
                            data = trains
                            if trains['Status'] == 'Pending Approval':
                                state = 3
            TrainLineResponse = session.get(TrainingLineRequest, timeout=10).json()
            for trainLine in TrainLineResponse['value']:
                if trainLine['Source_Document_No'] == pk :
                    output_json = json.dumps(trainLine)
                    TrainLine.append(json.loads(output_json))
            SurrenderResponse = session.get(SurrenderRequest, timeout=10).json()
            for imprest in SurrenderResponse['value']:
                if imprest['Status'] == "Pending Approval":
                    output_json = json.dumps(imprest)
                    Surrender.append(json.loads(output_json))
                    for imprest in Surrender:
                        if imprest['No_'] == pk:
                            data = imprest
                            if imprest['Status'] == 'Pending Approval':
                                state = 4
            Lines_Surrender = config.O_DATA.format("/QyImprestSurrenderLines")
            SurrenderLinesResponse = session.get(Lines_Surrender, timeout=10).json()
            SurrenderLines = []
            for imprest in SurrenderLinesResponse['value']:
                if imprest['No'] == pk:
                    output_json = json.dumps(imprest)
                    SurrenderLines.append(json.loads(output_json))
            ClaimResponse = session.get(ClaimRequest, timeout=10).json()
            for claim in ClaimResponse['value']:
                if claim['Status'] == "Pending Approval":
                    output_json = json.dumps(claim)
                    Claims.append(json.loads(output_json))
                    for claim in Claims:
                        if claim['No_'] == pk:
                            data = claim
                            if claim['Status'] == 'Pending Approval':
                                state = 5
            Lines_Claim = config.O_DATA.format("/QyStaffClaimLines")
            ClaimLineResponse = session.get(Lines_Claim, timeout=10).json()
            ClaimLines = []
            for claim in ClaimLineResponse['value']:
                if claim['No'] == pk:
                    output_json = json.dumps(claim)
                    ClaimLines.append(json.loads(output_json))
            PurchaseResponse = session.get(PurchaseRequest, timeout=10).json()
            for purchase in PurchaseResponse['value']:
                if purchase['No_'] == pk:
                    data = purchase
                    state = 6
            Lines_Purchase = config.O_DATA.format("/QyPurchaseRequisitionLines")
            PurchaseLineResponse = session.get(Lines_Purchase, timeout=10).json()
            PurchaseLines = []
            for document in PurchaseLineResponse['value']:
                if document['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(document)
                    PurchaseLines.append(json.loads(output_json))
            RepairRequest = config.O_DATA.format("/QyRepairRequisitionHeaders")
            RepairResponse = session.get(RepairRequest, timeout=10).json()
            Repair = []
            for repair in RepairResponse['value']:
                if repair['Status'] == "Pending Approval":
                    output_json = json.dumps(repair)
                    Repair.append(json.loads(output_json))
                    for repair in Repair:
                        if repair['No_'] == pk:
                            data = repair
                            if repair['Status'] == 'Pending Approval':
                                state = 7
            Lines_Repair = config.O_DATA.format("/QyRepairRequisitionLines")
            RepairLineResponse = session.get(Lines_Repair, timeout=10).json()
            RepairLines = []
            for document in RepairLineResponse['value']:
                if document['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(document)
                    RepairLines.append(json.loads(output_json))
            StoreRequest = config.O_DATA.format("/QyStoreRequisitionHeaders")
            StoreResponse = session.get(StoreRequest, timeout=10).json()
            Store = []
            for store in StoreResponse['value']:
                if store['Status'] == "Pending Approval":
                    output_json = json.dumps(repair)
                    Store.append(json.loads(output_json))
                    for store in Store:
                        if store['No_'] == pk:
                            data = store
                            if store['Status'] == 'Pending Approval':
                                state = 8
            Lines_Store = config.O_DATA.format("/QyStoreRequisitionLines")
            StoreLineResponse = session.get(Lines_Store, timeout=10).json()
            StoreLines = []
            for document in StoreLineResponse['value']:
                if document['AuxiliaryIndex1'] == pk:
                    output_json = json.dumps(document)
                    StoreLines.append(json.loads(output_json))

            VoucherRequest = config.O_DATA.format("/QyPaymentVoucherHeaders")
            VoucherResponse = session.get(VoucherRequest, timeout=10).json()
            for voucher in VoucherResponse['value']:
                if voucher['No_'] == pk:
                    data = voucher
                    state = "voucher"
            Lines_Voucher = config.O_DATA.format("/QyPaymentVoucherLines")
            VoucherLineResponse = session.get(Lines_Voucher, timeout=10).json()
            VoucherLines = []
            for document in VoucherLineResponse['value']:
                if document['No'] == pk:
                    output_json = json.dumps(document)
                    VoucherLines.append(json.loads(output_json))
            PettyRequest = config.O_DATA.format("/QyPettyCashHeaders")
            PettyResponse = session.get(PettyRequest, timeout=10).json()
            for petty in PettyResponse['value']:
                if petty['No_'] == pk:
                    data = petty
                    state = "petty cash"
            Lines_Petty = config.O_DATA.format("/QyPettyCashLines")
            PettyLineResponse = session.get(Lines_Petty, timeout=10).json()
            PettyLines = []
            for document in PettyLineResponse['value']:
                if document['No'] == pk:
                    output_json = json.dumps(document)
                    PettyLines.append(json.loads(output_json))
            PettySurrenderRequest = config.O_DATA.format("/QyPettyCashSurrenderHeaders")
            PettySurrenderResponse = session.get(PettySurrenderRequest, timeout=10).json()
            for pettySurrender in PettySurrenderResponse['value']:
                if pettySurrender['No_'] == pk:
                    data = pettySurrender
                    state = "petty cash surrender"
            Lines_PettySurrender = config.O_DATA.format("/QyPettyCashSurrenderLines")
            PettySurrenderLineResponse = session.get(Lines_PettySurrender, timeout=10).json()
            PettySurrenderLines = []
            for document in PettySurrenderLineResponse['value']:
                if document['No'] == pk:
                    output_json = json.dumps(document)
                    PettySurrenderLines.append(json.loads(output_json))
            advanceRequest = config.O_DATA.format("/QySalaryAdvances")
            advanceResponse = session.get(advanceRequest, timeout=10).json()
            for advance in advanceResponse['value']:
                if advance['Loan_No'] == pk:
                    data = advance
                    state = "advance"
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, e)
            return redirect('approve')
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res, "full": fullname, "year": year,
        "file":allFiles,"data":data,"state":state,"ImpLine":ImprestLine,"TrainLine":TrainLine,
        "SurrenderLines":SurrenderLines,"ClaimLines":ClaimLines,"PurchaseLines":PurchaseLines,
        "RepairLines":RepairLines,"StoreLines":StoreLines,"VoucherLines":VoucherLines,
        "PettyLines":PettyLines,"PettySurrenderLines":PettySurrenderLines}
    except KeyError as e:
        messages.info(request, "Session Expired. Please Login")
        print(e)
        return redirect('auth')
    return render(request, 'approveDetails.html', ctx)


def All_Approved(request, pk):
    entryNo = ''
    approvalComments = ""
   
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
            response = config.CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, myUserID, approvalComments, myAction)
            messages.success(request, "Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)


def Rejected(request, pk):
    entryNo = ''
    approvalComments = ""
    
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
            response = config.CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, userID, approvalComments, myAction)
            messages.success(request, "Reject Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            messages.info(request, e)
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
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)