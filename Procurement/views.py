from django.shortcuts import render, redirect
from datetime import date
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import enum

# Create your views here.


def PurchaseRequisition(request):
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
           "pending": Pending}
    return render(request, 'purchaseReq.html', ctx)


def CreatePurchaseRequisition(request):
    requisitionNo = ''
    orderDate = ''
    employeeNo = request.session['Employee_No_']
    reason = ""
    expectedReceiptDate = ''
    isConsumable = ""
    myUserId = request.session['User_ID']
    myAction = 'insert'
    if request.method == 'POST':
        try:
            orderDate = request.POST.get('orderDate')
            reason = request.POST.get('reason')
            expectedReceiptDate = request.POST.get('expectedReceiptDate')
            isConsumable = request.POST.get('isConsumable')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('purchase')
    try:
        response = config.CLIENT.service.FnPurchaseRequisitionHeader(
            requisitionNo, orderDate, employeeNo, reason, expectedReceiptDate, isConsumable, myUserId, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('purchase')


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
        for planitem in Res_Proc['value']:
            if planitem['Plan_Year'] == Current_Year.year:
                output_json = json.dumps(planitem)
                Proc.append(json.loads(output_json))
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
           "plans": Proc, "items": Items,
           "gl": Gl_Accounts}
    return render(request, 'purchaseDetail.html', ctx)


def CreatePurchaseLines(request, pk):
    # Create Enum For itemType which is 'Item'
    requisitionNo = pk
    lineNo = 0
    procPlanItem = ''
    itemTypes = ""
    itemNo = ""
    specification = ''
    quantity = 1
    myUserId = request.session['User_ID']
    myAction = 'insert'
    if request.method == 'POST':
        try:
            procPlanItem = request.POST.get('procPlanItem')
            itemTypes = request.POST.get('itemTypes')
            itemNo = request.POST.get('itemNo')
            specification = request.POST.get('specification')
            print(specification)
            quantity = int(request.POST.get('quantity'))

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
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PurchaseDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestInternalRequestApproval(
            myUserID, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('PurchaseDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PurchaseDetail', pk=pk)


def FnCancelPurchaseApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PurchaseDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('PurchaseDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PurchaseDetail', pk=pk)


def RepairRequest(request):
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
           'reject': reject, "pend": pend, "pending": Pending
           }
    return render(request, 'repairReq.html', ctx)


def CreateRepairRequest(request):
    requisitionNo = ''
    orderDate = ''
    employeeNo = request.session['Employee_No_']
    reason = ""
    expectedReceiptDate = ''
    myUserId = request.session['User_ID']
    myAction = 'insert'
    if request.method == 'POST':
        try:
            orderDate = request.POST.get('orderDate')
            reason = request.POST.get('reason')
            expectedReceiptDate = request.POST.get('expectedReceiptDate')
            isConsumable = request.POST.get('isConsumable')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('repair')
    try:
        response = config.CLIENT.service.FnRepairRequisitionHeader(
            requisitionNo, orderDate, employeeNo, reason, expectedReceiptDate, myUserId, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('repair')


def RepairRequestDetails(request, pk):
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
           "asset": my_asset}
    return render(request, 'repairDetail.html', ctx)


def RepairApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('RepairDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('RepairDetail', pk=pk)


def FnCancelRepairApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('RepairDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('RepairDetail', pk=pk)


def CreateRepairLines(request, pk):
    requisitionNo = pk
    lineNo = 0
    assetCode = ''
    description = 'Tests'
    myAction = 'insert'
    if request.method == 'POST':
        try:
            assetCode = request.POST.get('assetCode')
            description = request.POST.get('description')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=requisitionNo)
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


def StoreRequest(request):
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
           "pend": pend, "pending": Pending}
    return render(request, 'storeReq.html', ctx)


def CreateStoreRequisition(request):
    requisitionNo = ''
    employeeNo = request.session['Employee_No_']
    issuingStore = ""
    reason = ""
    expectedReceiptDate = ''
    myUserId = request.session['User_ID']
    myAction = 'insert'
    if request.method == 'POST':
        try:
            issuingStore = request.POST.get('issuingStore')
            reason = request.POST.get('reason')
            expectedReceiptDate = request.POST.get('expectedReceiptDate')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('store')
    try:
        response = config.CLIENT.service.FnStoreRequisitionHeader(
            requisitionNo, employeeNo, issuingStore, reason, expectedReceiptDate, myUserId, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('store')


def StoreRequestDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/QyStoreRequisitionHeaders")
    Item = config.O_DATA.format("/QyItems")
    Location = config.O_DATA.format("/QyLocations")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Item_res = session.get(Item, timeout=10).json()
        Loc_res = session.get(Location, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openImp = []
        res_type = []
        Approvers = []
        items = Item_res['value']
        Location = Loc_res['value']
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
           "Approvers": Approvers, "loc": Location}
    return render(request, 'storeDetail.html', ctx)


def StoreApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('StoreDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=pk)


def FnCancelStoreApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('StoreDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=pk)


def CreateStoreLines(request, pk):
    requisitionNo = pk
    lineNo = 0
    itemCode = ""
    location = ""
    quantity = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            itemCode = request.POST.get('itemCode')
            location = request.POST.get('location')
            quantity = int(request.POST.get('quantity'))
            print(itemCode)
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=requisitionNo)
    try:
        response = config.CLIENT.service.FnStoreRequisitionLine(
            requisitionNo, lineNo, itemCode, location, quantity, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('StoreDetail', pk=requisitionNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=requisitionNo)
