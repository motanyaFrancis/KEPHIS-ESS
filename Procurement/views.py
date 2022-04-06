import base64
from django.shortcuts import render, redirect
from datetime import date, datetime
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import enum
import secrets
from django.http import HttpResponse
import io as BytesIO
import string
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='auth')
def PurchaseRequisition(request):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        for document in response['value']:
            if document['Status'] == 'Open' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                open.append(json.loads(output_json))
            if document['Status'] == 'Released' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                Approved.append(json.loads(output_json))
            if document['Status'] == 'Rejected' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                Rejected.append(json.loads(output_json))
            if document['Status'] == "Pending Approval" and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
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
           'reject': reject, "pend": pend,
           "pending": Pending, "year": year,
           "full": fullname}
    return render(request, 'purchaseReq.html', ctx)


def CreatePurchaseRequisition(request):
    requisitionNo = ''
    orderDate = ''
    employeeNo = request.session['Employee_No_']
    reason = ""
    expectedReceiptDate = ''
    isConsumable = ""
    myUserId = request.session['User_ID']
    myAction = ' '
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            orderDate = datetime.strptime(
                request.POST.get('orderDate'), '%Y-%m-%d').date()
            reason = request.POST.get('reason')
            expectedReceiptDate = datetime.strptime(
                request.POST.get('expectedReceiptDate'), '%Y-%m-%d').date()
            isConsumable = eval(request.POST.get('isConsumable'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('purchase')
        if not requisitionNo:
            requisitionNo = " "
        try:
            response = config.CLIENT.service.FnPurchaseRequisitionHeader(
                requisitionNo, orderDate, employeeNo, reason, expectedReceiptDate, isConsumable, myUserId, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('purchase')

@login_required(login_url='auth')
def PurchaseRequestDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Current_Year = date.today()
    Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    ProcPlan = config.O_DATA.format("/QyProcurementPlans")
    itemNo = config.O_DATA.format("/QyItems")
    GL_Acc = config.O_DATA.format("/QyGLAccounts")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        Res_Proc = session.get(ProcPlan, timeout=10).json()
        Res_itemNo = session.get(itemNo, timeout=10).json()
        Res_GL = session.get(GL_Acc, timeout=10).json()
        openImp = []
        res_type = []
        Pending = []
        Approvers = []
        Proc = []
        Items = Res_itemNo['value']
        Gl_Accounts = Res_GL['value']
        planitem = Res_Proc['value']
        # for planitem in Res_Proc['value']:
        #     if planitem['Plan_Year'] == Current_Year.year:
        #         output_json = json.dumps(planitem)
        #         Proc.append(json.loads(output_json))
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for document in response['value']:
            if document['Status'] == 'Released' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
            if document['Status'] == 'Open' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Open':
                            state = 1
            if document['Status'] == 'Released' and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Released':
                            state = 3
            if document['Status'] == "Pending Approval" and document['Employee_No_'] == request.session['Employee_No_']:
                output_json = json.dumps(document)
                Pending.append(json.loads(output_json))
                for document in Pending:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyPurchaseRequisitionLines")
    try:
        response_Lines = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for document in response_Lines['value']:
            if document['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(document)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "state": state, "line": openLines,
           "type": res_type, "Approvers": Approvers,
           "plans": planitem, "items": Items,
           "gl": Gl_Accounts}
    return render(request, 'purchaseDetail.html', ctx)


def CreatePurchaseLines(request, pk):
    # Create Enum For itemType which is 'Item'
    requisitionNo = pk
    lineNo = ""
    procPlanItem = ''
    itemTypes = ""
    itemNo = ""
    specification = ''
    quantity = 1
    myUserId = request.session['User_ID']
    myAction = ''
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            procPlanItem = request.POST.get('procPlanItem')
            itemTypes = request.POST.get('itemTypes')
            itemNo = request.POST.get('itemNo')
            specification = request.POST.get('specification')
            quantity = int(request.POST.get('quantity'))
            myAction = request.POST.get('myAction')

        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PurchaseDetail', pk=requisitionNo)

        class Data(enum.Enum):
            values = itemTypes
        itemType = (Data.values).value
        try:
            response = config.CLIENT.service.FnPurchaseRequisitionLine(
                requisitionNo, lineNo, procPlanItem, itemType, itemNo, specification, quantity, myUserId, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
            return redirect('PurchaseDetail', pk=requisitionNo)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('PurchaseDetail', pk=requisitionNo)


def PurchaseApproval(request, pk):
    myUserID = request.session['User_ID']
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PurchaseDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestInternalRequestApproval(
            myUserID, requistionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('PurchaseDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PurchaseDetail', pk=pk)


def UploadPurchaseAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177432

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('PurchaseDetail', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('PurchaseDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('PurchaseDetail', pk=pk)

    return redirect('PurchaseDetail', pk=pk)


def FnCancelPurchaseApproval(request, pk):
    myUserID = request.session['User_ID']
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PurchaseDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelInternalRequestApproval(
            myUserID, requistionNo)
        messages.success(request, "Cancel Approval Successful !!")
        print(response)
        return redirect('PurchaseDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PurchaseDetail', pk=pk)


def FnDeletePurchaseRequisitionHeader(request):
    requisitionNo = ""
    if request.method == 'POST':
        requisitionNo = request.POST.get('requisitionNo')
        try:
            response = config.CLIENT.service.FnDeletePurchaseRequisitionHeader(
                requisitionNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('purchase')


def FnGeneratePurchaseReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    reqNo = pk
    filenameFromApp = ''
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
        except ValueError as e:
            return redirect('PurchaseDetail', pk=pk)
    filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateRequisitionReport(
            reqNo, filenameFromApp)
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
    return redirect('PurchaseDetail', pk=pk)


def FnDeletePurchaseRequisitionLine(request, pk):
    requisitionNo = pk
    lineNo = ""
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeletePurchaseRequisitionLine(
                requisitionNo, lineNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('PurchaseDetail', pk=pk)

@login_required(login_url='auth')
def RepairRequest(request):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyRepairRequisitionHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        for document in response['value']:
            if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                open.append(json.loads(output_json))
            if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                Approved.append(json.loads(output_json))
            if document['Status'] == 'Rejected' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                Rejected.append(json.loads(output_json))
            if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
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
           'reject': reject, "pend": pend,
           "year": year, "full": fullname,
           "pending": Pending
           }
    return render(request, 'repairReq.html', ctx)


def CreateRepairRequest(request):
    requisitionNo = ''
    orderDate = ''
    employeeNo = request.session['Employee_No_']
    reason = ""
    expectedReceiptDate = ''
    myUserId = request.session['User_ID']
    myAction = ' '
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            orderDate = datetime.strptime(
                request.POST.get('orderDate'), '%Y-%m-%d').date()
            reason = request.POST.get('reason')
            expectedReceiptDate = datetime.strptime(
                request.POST.get('expectedReceiptDate'), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('repair')
        if not requisitionNo:
            requisitionNo = " "
        try:
            response = config.CLIENT.service.FnRepairRequisitionHeader(
                requisitionNo, orderDate, employeeNo, reason, expectedReceiptDate, myUserId, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('repair')

@login_required(login_url='auth')
def RepairRequestDetails(request, pk):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    output_json = ''
    Access_Point = config.O_DATA.format("/QyRepairRequisitionHeaders")
    Assets = config.O_DATA.format("/QyFixedAssets")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Assest_res = session.get(Assets, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openImp = []
        res_type = []
        Approvers = []
        my_asset = Assest_res['value']
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for document in response['value']:
            if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Open':
                            state = 1
            if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Released':
                            state = 3

            if document['Status'] == 'Rejected' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
            if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyRepairRequisitionLines")
    try:
        response_Lines = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for document in response_Lines['value']:
            if document['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(document)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "state": state, "line": openLines,
           "type": res_type, "Approvers": Approvers,
           "asset": my_asset, "full": fullname,
           "year": year}
    return render(request, 'repairDetail.html', ctx)


def RepairApproval(request, pk):
    myUserID = request.session['User_ID']
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestInternalRequestApproval(
            myUserID, requistionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('RepairDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('RepairDetail', pk=pk)


def UploadRepairAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177432

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('RepairDetail', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('RepairDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('RepairDetail', pk=pk)

    return redirect('RepairDetail', pk=pk)


def FnCancelRepairApproval(request, pk):
    myUserID = request.session['User_ID']
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelInternalRequestApproval(
            myUserID, requistionNo)
        messages.success(request, "Cancel Approval Successful !!")
        print(response)
        return redirect('RepairDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('RepairDetail', pk=pk)


def CreateRepairLines(request, pk):
    requisitionNo = pk
    lineNo = ""
    assetCode = ''
    description = ''
    myAction = ''
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            assetCode = request.POST.get('assetCode')
            description = request.POST.get('description')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=requisitionNo)
        print("requisitionNo", requisitionNo)
        print("lineNo", lineNo)
        print("assetCode", assetCode)
        print("description", description)
        print("myAction", myAction)
        try:
            response = config.CLIENT.service.FnRepairRequisitionLine(
                requisitionNo, lineNo, assetCode, description, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
            return redirect('RepairDetail', pk=requisitionNo)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('RepairDetail', pk=requisitionNo)


def FnDeleteRepairRequisitionHeader(request):
    requisitionNo = ""
    if request.method == 'POST':
        requisitionNo = request.POST.get('requisitionNo')
        try:
            response = config.CLIENT.service.FnDeleteRepairRequisitionHeader(
                requisitionNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('repair')


def FnDeleteRepairRequisitionLine(request, pk):
    requisitionNo = pk
    lineNo = ""
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        print(requisitionNo, lineNo)
        try:
            response = config.CLIENT.service.FnDeleteRepairRequisitionLine(
                requisitionNo, lineNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('RepairDetail', pk=pk)

@login_required(login_url='auth')
def StoreRequest(request):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyStoreRequisitionHeaders")
    QYStore = config.O_DATA.format("/QyLocations")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Store_res = session.get(QYStore, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        Stores = Store_res['value']
        for document in response['value']:
            if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                open.append(json.loads(output_json))
            if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                Approved.append(json.loads(output_json))
            if document['Status'] == 'Rejected' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                Rejected.append(json.loads(output_json))
            if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
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
           'reject': reject, "store": Stores,
           "pend": pend, "pending": Pending,
           "full": fullname, "year": year}
    return render(request, 'storeReq.html', ctx)


def CreateStoreRequisition(request):
    requisitionNo = ''
    employeeNo = request.session['Employee_No_']
    issuingStore = ""
    reason = ""
    expectedReceiptDate = ''
    myUserId = request.session['User_ID']
    myAction = ''
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            issuingStore = request.POST.get('issuingStore')
            reason = request.POST.get('reason')
            expectedReceiptDate = datetime.strptime(
                request.POST.get('expectedReceiptDate'), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('store')
        if not requisitionNo:
            requisitionNo = " "

        try:
            response = config.CLIENT.service.FnStoreRequisitionHeader(
                requisitionNo, employeeNo, issuingStore, reason, expectedReceiptDate, myUserId, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('store')

@login_required(login_url='auth')
def StoreRequestDetails(request, pk):
    fullname = request.session['fullname']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/QyStoreRequisitionHeaders")
    Item = config.O_DATA.format("/QyItems")
    Location = config.O_DATA.format("/QyLocations")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    Measure = config.O_DATA.format("/QyUnitsOfMeasure")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Item_res = session.get(Item, timeout=10).json()
        Loc_res = session.get(Location, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        res_Measure = session.get(Measure, timeout=10).json()
        openImp = []
        res_type = []
        Approvers = []
        items = Item_res['value']
        Location = Loc_res['value']
        unit = res_Measure['value']
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for document in response['value']:
            if document['Status'] == 'Released' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Released':
                            state = 3
            if document['Status'] == 'Open' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Open':
                            state = 1
            if document['Status'] == 'Rejected' and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
            if document['Status'] == "Pending Approval" and document['Requested_By'] == request.session['User_ID']:
                output_json = json.dumps(document)
                openImp.append(json.loads(output_json))
                for document in openImp:
                    if document['No_'] == pk:
                        res = document
                        if document['Status'] == 'Pending Approval':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyStoreRequisitionLines")
    try:
        response_Lines = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for document in response_Lines['value']:
            if document['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(document)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "state": state, "line": openLines,
           "type": res_type, "items": items,
           "Approvers": Approvers, "loc": Location,
           "year": year, "full": fullname,
           "unit": unit}
    return render(request, 'storeDetail.html', ctx)


def StoreApproval(request, pk):
    myUserID = request.session['User_ID']
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestInternalRequestApproval(
            myUserID, requistionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('StoreDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=pk)


def FnCancelStoreApproval(request, pk):
    myUserID = request.session['User_ID']
    requistionNo = ""
    if request.method == 'POST':
        try:
            requistionNo = request.POST.get('requistionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelInternalRequestApproval(
            myUserID, requistionNo)
        messages.success(request, "Cancel Approval Successful !!")
        print(response)
        return redirect('StoreDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=pk)


def CreateStoreLines(request, pk):
    requisitionNo = pk
    lineNo = ""
    itemCode = ""
    location = ""
    quantity = ""
    unitOfMeasure = ""
    myAction = ''
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            itemCode = request.POST.get('itemCode')
            location = request.POST.get('location')
            unitOfMeasure = request.POST.get('unitOfMeasure')
            quantity = int(request.POST.get('quantity'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=requisitionNo)
    try:
        response = config.CLIENT.service.FnStoreRequisitionLine(
            requisitionNo, lineNo, itemCode, location, quantity, unitOfMeasure, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('StoreDetail', pk=requisitionNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=requisitionNo)

# Delete Store Header


def FnDeleteStoreRequisitionHeader(request):
    requisitionNo = ""
    if request.method == 'POST':
        requisitionNo = request.POST.get('requisitionNo')
        try:
            response = config.CLIENT.service.FnDeleteStoreRequisitionHeader(
                requisitionNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('store')


def FnDeleteStoreRequisitionLine(request, pk):
    requisitionNo = pk
    lineNo = ""
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeleteStoreRequisitionLine(
                requisitionNo, lineNo)
            messages.success(request, "Successfully Deleted")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('StoreDetail', pk=requisitionNo)


def FnGenerateStoreReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    reqNo = pk
    filenameFromApp = ''
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
        except ValueError as e:
            return redirect('StoreDetail', pk=pk)
    filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateStoreReport(
            reqNo, filenameFromApp)
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
    return redirect('StoreDetail', pk=pk)


def FnGenerateRepairReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    reqNo = pk
    filenameFromApp = ''
    if request.method == 'POST':
        try:
            filenameFromApp = request.POST.get('filenameFromApp')
        except ValueError as e:
            return redirect('RepairDetail', pk=pk)
    filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateRepairReport(
            reqNo, filenameFromApp)
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
    return redirect('RepairDetail', pk=pk)


def UploadStoreAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177432

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('StoreDetail', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('StoreDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('StoreDetail', pk=pk)

    return redirect('StoreDetail', pk=pk)
