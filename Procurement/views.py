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


def PurchaseRequisition(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
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
        counts = len(open)
        counter = len(Approved)
        reject = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject}
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
    Access_Point = config.O_DATA.format("/QyPurchaseRequisitionHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()

        openImp = []
        res_type = []
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
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyImprestSurrenderLines")
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
           "state": state, "line": openLines, "type": res_type}
    return render(request, 'purchaseDetail.html', ctx)


def PurchaseApproval(request, pk):
    entryNo = 0
    documentNo = pk
    userID = request.session['User_ID']
    approvalComments = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            approvalComments = request.POST.get('approvalComments')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PurchaseDetail', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('PurchaseDetail', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PurchaseDetail', pk=documentNo)


def RepairRequest(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyRepairRequisitionHeaders")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
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
        counts = len(open)
        counter = len(Approved)
        reject = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject}
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
           "state": state, "line": openLines, "type": res_type, "Approvers": Approvers, "asset": my_asset}
    return render(request, 'repairDetail.html', ctx)


def RepairApproval(request, pk):
    entryNo = 0
    documentNo = pk
    userID = request.session['User_ID']
    approvalComments = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            approvalComments = request.POST.get('approvalComments')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('RepairDetail', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('RepairDetail', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('RepairDetail', pk=documentNo)


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
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
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
        counts = len(open)
        counter = len(Approved)
        reject = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "rej": Rejected,
           'reject': reject}
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
    try:
        response = session.get(Access_Point, timeout=10).json()
        Item_res = session.get(Item, timeout=10).json()
        Loc_res = session.get(Location, timeout=10).json()
        openImp = []
        res_type = []
        items = Item_res['value']
        Location = Loc_res['value']
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
           "state": state, "line": openLines, "type": res_type, "items": items, "loc": Location}
    return render(request, 'storeDetail.html', ctx)


def StoreApproval(request, pk):
    entryNo = 0
    documentNo = pk
    userID = request.session['User_ID']
    approvalComments = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            approvalComments = request.POST.get('approvalComments')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('StoreDetail', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('StoreDetail', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('StoreDetail', pk=documentNo)


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
