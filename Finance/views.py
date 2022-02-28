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


# Create your views here.


def ImprestRequisition(request):
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/Imprests")
    try:
        response = session.get(Access_Point, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        Pending = []
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
            if imprest['Status'] == 'Pending Approval' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Pending.append(json.loads(output_json))
        counts = len(open)

        pend = len(Pending)

        counter = len(Approved)

        reject = len(Rejected)

    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "reject": Rejected, "rej": reject, "pend": pend, "pending": Pending}
    return render(request, 'imprestReq.html', ctx)


def CreateImprest(request):
    session = requests.Session()
    session.auth = config.AUTHS
    imprestNo = ""
    accountNo = request.session['Customer_No_']
    responsibilityCenter = request.session['User_Responsibility_Center']
    travelType = ''
    payee = ''
    purpose = ''
    usersId = request.session['User_ID']
    personalNo = request.session['No_']
    idPassport = ''
    isImprest = ''
    isDsa = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            travelType = int(request.POST.get('travelType'))
            payee = request.POST.get('payee')
            purpose = request.POST.get('purpose')
            idPassport = request.POST.get('idPassport')
            isImprest = request.POST.get('isImprest')
            isDsa = request.POST.get('isDsa')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('imprestReq')
    print(accountNo)
    try:
        response = config.CLIENT.service.FnImprestHeader(
            imprestNo, accountNo, responsibilityCenter, travelType, payee, purpose, usersId, personalNo, idPassport, isImprest, isDsa, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        print(e)
    return redirect('imprestReq')


def ImprestDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/Imprests")
    Imprest_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes")
    Dimension = config.O_DATA.format("/QyDimensionValues")
    destination = config.O_DATA.format("/QyDestinations")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Imprest_RES = session.get(Imprest_Type, timeout=10).json()
        Dimension_RES = session.get(Dimension, timeout=10).json()
        res_dest = session.get(destination, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()

        openImp = []
        res_type = []
        Area = []
        BizGroup = []
        Approvers = []
        Pending = []
        destinations = res_dest['value']
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for types in Dimension_RES['value']:
            if types['Global_Dimension_No_'] == 1:
                output_json = json.dumps(types)
                Area.append(json.loads(output_json))
            if types['Global_Dimension_No_'] == 2:
                output_json = json.dumps(types)
                BizGroup.append(json.loads(output_json))
        for types in Imprest_RES['value']:
            if types['Type'] == "Imprest":
                output_json = json.dumps(types)
                res_type.append(json.loads(output_json))
        for imprest in response['value']:
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
                        if imprest['Status'] == 'Open':
                            state = 1
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
            if imprest['Status'] == "Pending Approval" and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Pending.append(json.loads(output_json))
                for imprest in Pending:
                    if imprest['No_'] == pk:
                        res = imprest
                        if imprest['Status'] == 'Open':
                            state = 2
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyImprestLines")
    try:
        response = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for imprest in response['value']:
            if imprest['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(imprest)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "line": openLines, "state": state, "Approvers": Approvers, "type": res_type, "area": Area, "biz": BizGroup, "des": destinations}
    return render(request, 'imprestDetail.html', ctx)


def ImprestApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            print(requisitionNo)
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('IMPDetails', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPDetails', pk=pk)


def FnRequestPaymentApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('IMPDetails', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPDetails', pk=pk)


def ImprestCancelApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    requisitionNo = ""
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelPaymentApproval(
            employeeNo, requisitionNo)
        messages.success(request, "Cancel Request Successfully Sent!!")
        print(response)
        return redirect('IMPDetails', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPDetails', pk=pk)


def CreateImprestLines(request, pk):
    lineNo = 0
    imprestNo = pk
    destination = ""
    imprestType = ''
    travelDate = ''
    returnDate = ''
    requisitionType = ''
    dailyRate = 10
    quantity = ""
    areaCode = ""
    imprestTypes = ''
    businessGroupCode = ''
    dimension3 = ''
    myAction = 'insert'
    if request.method == 'POST':
        try:
            destination = request.POST.get('destination')
            imprestTypes = request.POST.get('imprestType')
            requisitionType = request.POST.get('requisitionType')
            travelDate = request.POST.get('travel')
            areaCode = request.POST.get("areaCode")
            businessGroupCode = request.POST.get('businessGroupCode')
            returnDate = request.POST.get('returnDate')
            quantity = int(request.POST.get('quantity'))
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=imprestNo)

    class Data(enum.Enum):
        values = imprestTypes
    imprestType = (Data.values).value
    try:
        response = config.CLIENT.service.FnImprestLine(
            lineNo, imprestNo, imprestType, destination, travelDate, returnDate, requisitionType, dailyRate, quantity, areaCode, businessGroupCode, dimension3, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('IMPDetails', pk=imprestNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPDetails', pk=imprestNo)


def ImprestApproval(request, pk):
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
            return redirect('IMPDetails', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Sent!!")
        print(response)
        return redirect('IMPDetails', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPDetails', pk=documentNo)


def ImprestSurrender(request):

    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyImprestSurrenders")
    Released_imprest = config.O_DATA.format("/Imprests")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Released = session.get(Released_imprest, timeout=10).json()
        open = []
        Approved = []
        Reject = []
        APPImp = []
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Reject.append(json.loads(output_json))
        for imprest in Released['value']:
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                APPImp.append(json.loads(output_json))
        counts = len(open)
        request.session['open_surrender'] = counts
        open_surrender = request.session['open_surrender']

        counter = len(Approved)
        request.session['App_surrender'] = counter
        App_surrender = request.session['App_surrender']

        Rejects = len(Reject)
        request.session['Rej_surrender'] = Rejects
        Rej_surrender = request.session['Rej_surrender']
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts,
           "response": Approved, "counter": counter, "reject": Rejects, "rej": Reject, "app": APPImp}
    return render(request, 'imprestSurr.html', ctx)


def CreateSurrender(request):

    surrenderNo = ""
    imprestIssueDocNo = ''
    accountNo = request.session['Customer_No_']
    payee = ""
    purpose = ""
    usersId = request.session['User_ID']
    staffNo = request.session['Employee_No_']
    myAction = 'insert'
    if request.method == 'POST':
        try:
            imprestIssueDocNo = request.POST.get('imprestIssueDocNo')
            payee = request.POST.get('payee')
            purpose = request.POST.get('purpose')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('imprestSurr')
    try:
        response = config.CLIENT.service.FnImprestSurrenderHeader(
            surrenderNo, imprestIssueDocNo, accountNo, payee, purpose, usersId, staffNo, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
    except Exception as e:
        print(e)
    return redirect('imprestSurr')


def SurrenderDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/QyImprestSurrenders")
    Imprest_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Imprest_RES = session.get(Imprest_Type, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openImp = []
        res_type = []
        Approvers = []
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for types in Imprest_RES['value']:
            if types['Type'] == "Imprest":
                output_json = json.dumps(types)
                res_type.append(json.loads(output_json))
        for imprest in response['value']:
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
                        if imprest['Status'] == 'Open':
                            state = 1
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                openImp.append(json.loads(output_json))
                for imprest in openImp:
                    if imprest['No_'] == pk:
                        res = imprest
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyImprestSurrenderLines")
    try:
        response_Lines = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for imprest in response_Lines['value']:
            if imprest['AuxiliaryIndex1'] == pk:
                output_json = json.dumps(imprest)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "state": state, "line": openLines, "Approvers": Approvers, "type": res_type}
    return render(request, 'SurrenderDetail.html', ctx)


def CreateSurrenderLines(request, pk):
    lineNo = 0
    surrenderNo = pk
    expenditureType = ""
    accountNo = request.session['Customer_No_']
    genPostingType = ""
    purpose = ""
    actualSpent = ""
    surrenderReceiptNo = ''
    dimension3 = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            expenditureType = request.POST.get('expenditureType')
            genPostingType = request.POST.get('genPostingType')
            purpose = request.POST.get('purpose')
            actualSpent = float(request.POST.get('actualSpent'))

        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=surrenderNo)
    try:
        response = config.CLIENT.service.FnImprestSurrenderLine(
            lineNo, surrenderNo, expenditureType, accountNo, genPostingType, purpose, actualSpent, surrenderReceiptNo, dimension3, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('IMPSurrender', pk=surrenderNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPSurrender', pk=surrenderNo)


def SurrenderApproval(request, pk):
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
            return redirect('IMPSurrender', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Sent!!")
        print(response)
        return redirect('IMPSurrender', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('IMPSurrender', pk=documentNo)


def StaffClaim(request):

    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyStaffClaims")
    Claim = config.O_DATA.format("/QyImprestSurrenders")
    currency = config.O_DATA.format("/QyCurrencies")
    try:
        response = session.get(Access_Point, timeout=10).json()
        res_claim = session.get(Claim, timeout=10).json()
        res_currency = session.get(currency, timeout=10).json()
        open = []
        Approved = []
        Rejected = []
        My_Claim = []
        all_currency = res_currency['value']

        for imprest in res_claim['value']:
            if imprest['Actual_Amount_Spent'] > imprest['Imprest_Amount']:
                output_json = json.dumps(imprest)
                My_Claim.append(json.loads(output_json))
        for imprest in response['value']:
            if imprest['Status'] == 'Open' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                open.append(json.loads(output_json))
            if imprest['Status'] == 'Released' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Approved.append(json.loads(output_json))
            if imprest['Status'] == 'Rejected' and imprest['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(imprest)
                Rejected.append(json.loads(output_json))
        counts = len(open)

        counter = len(Approved)
        rej = len(Rejected)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": open, "count": counts, "rej": rej,
           "response": Approved, "claim": counter, 'reject': Rejected, "my_claim": My_Claim, "currency": all_currency}
    return render(request, 'staffClaim.html', ctx)


def CreateClaim(request):
    claimNo = ""
    claimType = ""
    accountNo = request.session['Customer_No_']
    payee = ''
    purpose = ''
    usersId = request.session['User_ID']
    staffNo = request.session['Employee_No_']
    currency = ""
    imprestSurrDocNo = ''
    myAction = 'insert'
    if request.method == 'POST':
        claimType = int(request.POST.get('claimType'))
        payee = request.POST.get('payee')
        currency = request.POST.get('currency')
        imprestSurrDocNo = request.POST.get('imprestSurrDocNo')
        purpose = request.POST.get('purpose')
    try:
        response = config.CLIENT.service.FnStaffClaimHeader(
            claimNo, claimType, accountNo, payee, purpose, usersId, staffNo, currency, imprestSurrDocNo, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('claim')
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('claim')


def ClaimDetails(request, pk):
    session = requests.Session()
    session.auth = config.AUTHS
    state = ''
    res = ''
    Access_Point = config.O_DATA.format("/QyStaffClaims")
    Claim_Type = config.O_DATA.format("/QyReceiptsAndPaymentTypes")
    Approver = config.O_DATA.format("/QyApprovalEntries")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Claim_RES = session.get(Claim_Type, timeout=10).json()
        res_approver = session.get(Approver, timeout=10).json()
        openClaim = []
        res_type = []
        Approvers = []
        for approver in res_approver['value']:
            if approver['Document_No_'] == pk:
                output_json = json.dumps(approver)
                Approvers.append(json.loads(output_json))
        for types in Claim_RES['value']:
            if types['Type'] == "Claim":
                output_json = json.dumps(types)
                res_type.append(json.loads(output_json))
        for claim in response['value']:
            if claim['Status'] == 'Released' and claim['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['No_'] == pk:
                        res = claim
            if claim['Status'] == 'Open' and claim['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['No_'] == pk:
                        res = claim
                        if claim['Status'] == 'Open':
                            state = 1
            if claim['Status'] == 'Rejected' and claim['User_Id'] == request.session['User_ID']:
                output_json = json.dumps(claim)
                openClaim.append(json.loads(output_json))
                for claim in openClaim:
                    if claim['No_'] == pk:
                        res = claim
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyStaffClaimLines")
    try:
        res_Line = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for claim in res_Line['value']:
            if claim['No'] == pk:
                output_json = json.dumps(claim)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "state": state, "res_type": res_type, "Approvers": Approvers, "line": openLines}
    return render(request, "ClaimDetail.html", ctx)


def CreateClaimLines(request, pk):
    lineNo = 0
    claimNo = pk
    claimType = ""
    accountNo = request.session['Customer_No_']
    amount = ""
    description = ""
    claimReceiptNo = ""
    dimension3 = ''
    expenditureDate = ""
    expenditureDescription = ""
    myAction = 'insert'
    if request.method == 'POST':
        try:
            claimType = request.POST.get('claimType')
            amount = float(request.POST.get('amount'))
            description = request.POST.get('description')
            expenditureDate = request.POST.get('expenditureDate')
            expenditureDescription = request.POST.get('expenditureDescription')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('IMPDetails', pk=claimNo)
    try:
        response = config.CLIENT.service.FnStaffClaimLine(
            lineNo, claimNo, claimType, accountNo, amount, description, claimReceiptNo, dimension3, expenditureDate, expenditureDescription, myAction)
        messages.success(request, "Successfully Added!!")
        print(response)
        return redirect('ClaimDetail', pk=claimNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('ClaimDetail', pk=claimNo)


def ClaimApproval(request, pk):
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
            return redirect('ClaimDetail', pk=documentNo)
    try:
        response = config.CLIENT.service.FnDocumentApproval(
            entryNo, documentNo, userID, approvalComments, myAction)
        messages.success(request, "Successfully Sent!!")
        print(response)
        return redirect('ClaimDetail', pk=documentNo)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('ClaimDetail', pk=documentNo)
