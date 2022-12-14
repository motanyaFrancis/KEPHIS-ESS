import base64
from django.shortcuts import render, redirect
from datetime import datetime
# from isodate import date_isoformat
import requests
from requests import Session
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from django.http import HttpResponse
import io as BytesIO
import secrets
import string
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from django.views import View

# Create your views here.


class UserObjectMixin(object):
    model = None
    session = Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


class WorkTicket(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyWorkTicket?$filter=CreatedBy%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            Access_Point_List = [x for x in response]
            
            openTicket = [
                x for x in response['value'] if x['Status'] == 'Open'
            ]
            PendingTicket = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]
            ApprovedTicket = [
                x for x in response['value'] if x['Status'] == 'Approved'
            ]

            counts = len(openTicket)
            pend = len(PendingTicket)

            counter = len(ApprovedTicket)

            vehicle = config.O_DATA.format("/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            Ticket = config.O_DATA.format(f"/QyWorkTicket?$filter=CreatedBy%20eq%20%27{userID}%27")
            res_tkt = self.get_object(Ticket)
            tkt_no = [x for x in res_tkt['value']]
            
            driver = config.O_DATA.format(f"/QyDrivers")
            req_driver = self.get_object(driver)
            drivers = [x for x in req_driver['value']]

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {
            "today": self.todays_date,
            "open": openTicket,
            "count": counts,
            "approved": ApprovedTicket,
            "counter": counter,
            "pend": pend,
            "pending": PendingTicket,
            "year": year,
            "full": userID,
            'Vehicle_No': Vehicle_No,
            'tkt_no': tkt_no,
            'drivers': drivers,
        }
        return render(request, 'workticket.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                employeeNo = request.session['Employee_No_']
                myUserId = request.session['User_ID']
                workTicketNo = request.POST.get('No')
                previoursWorkTicketNo = request.POST.get(
                    'previoursWorkTicketNo')
                driver = request.POST.get('driver')
                currentworkTicketNo = request.POST.get('currentworkTicketNo')
                reasoForReplacement = request.POST.get('reasoForReplacement')
                kmCovered = request.POST.get('kmCovered')
                vehicle = request.POST.get('vehicle')
                myAction = request.POST.get('myAction')

            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('workTicket')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')

            if not workTicketNo:
                workTicketNo = " "

            try:
                response = config.CLIENT.service.FnWorkTicket(
                    workTicketNo, 
                    employeeNo,
                    myAction,
                    previoursWorkTicketNo,
                    driver,
                    currentworkTicketNo,
                    reasoForReplacement, 
                    kmCovered, 
                    myUserId,
                    vehicle, 
                    )
                messages.success(request, "Request Successful")
                print(response)

            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('workTicket')
        return redirect('workTicket')


class WorkTicketDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyWorkTicket?$filter=No%20eq%20%27{pk}%27%20and%20CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)

            for workTicket in response['value']:
                res = workTicket

            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('imprestReq')

        ctx = {
            'res': res,
            'file': allFiles,
            'Approvers': Approvers,
        }

        return render(request, 'workTicketDetails.html', ctx)


def UploadTicketAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('WorkTicketDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('WorkTicketDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('WorkTicketDetails', pk=pk)
    return redirect('WorkTicketDetails', pk=pk)


def DeleteTicketAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('WorkTicketDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('WorkTicketDetails', pk=pk)


def FnSubmitWorkTicket(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    workTicketNo = ""
    if request.method == 'POST':
        workTicketNo = request.POST.get('workTicketNo')
        myUserID = request.session['User_ID']

        try:
            response = config.CLIENT.service.FnSubmitWorkTicket(
                workTicketNo,
                myUserID,
            )
            messages.success(request, "Approval Request Sent Successfully")
            return redirect('WorkTicketDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('WorkTicketDetails', pk=pk)
    return redirect('WorkTicketDetails', pk=pk)


class VehicleRepaiRequest(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"//QyRepairRequest?$filter=RequestedBy%20eq%20%27{userID}%27%20and%20DocumentType%20eq%20%27Repair%27")
            response = self.get_object(Access_Point)

            vehicle = config.O_DATA.format("/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            openRepairReq = [
                x for x in response['value'] if x['Status'] == 'Open'
            ]
            PendingRepairReq = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]
            ApprovedRepair = [
                x for x in response['value'] if x['Status'] == 'Released'
            ]

            counts = len(openRepairReq)
            pend = len(PendingRepairReq)

            counter = len(ApprovedRepair)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {
            "today": self.todays_date,
            "open": openRepairReq,
            "count": counts,
            "approved": ApprovedRepair,
            "counter": counter,
            "pend": pend,
            "pending": PendingRepairReq,
            "year": year,
            "full": userID,
            "Vehicle_No": Vehicle_No,
        }
        return render(request, 'vehicleRepairReq.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                reqNo = request.POST.get('reqNo')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                odometerReading = request.POST.get('odometerReading')
                repairInstractionSheet = request.POST.get(
                    'repairInstractionSheet')
                myAction = request.POST.get('myAction')

            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('vehicleRepairRequest')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')

            if not reqNo:
                reqNo = " "

            try:
                response = config.CLIENT.service.FnRepairRequestHeader(
                    reqNo, myUserId, vehicle, odometerReading,
                    repairInstractionSheet, myAction)
                if response == True:
                    messages.success(request, "Request Successful")
                    return redirect('vehicleRepairRequest')
                # print(response)
            except Exception as e:
                messages.error(request, e)
                return redirect('vehicleRepairRequest')
        return redirect('vehicleRepairRequest')


class VehicleRepairRequestDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            empNo = request.session['Employee_No_']
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(
                f"/QyRepairRequest?$filter=RequestedBy%20eq%20%27{userID}%27%20and%20No%20eq%20%27{pk}%27"
            )
            response = self.get_object(Access_Point)
            repair_response = [x for x in response['value']]
            for repair_req in response['value']:
                repair_response = repair_req
            
            Access = config.O_DATA.format(
                 f"/QyRepairRequestLines?$filter=DocumentNo%20eq%20%27{pk}%27"
            )
            LinesRes = self.get_object(Access)
            openLines = [x for x in LinesRes['value']
                         if x['DocumentNo'] == pk]

            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

        except Exception as e:
            messages.info(request, 'Wrong UserID')
            return redirect('vehicleRepairRequest')

        context = {
            "today": self.todays_date,
            "res": repair_response,
            'allFiles': allFiles,
            "Approvers": Approvers,
            "line": openLines,
        }

        return render(request, 'vehicleRepairDetails.html', context)


def UploadRepairAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('vehicleRepairDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('vehicleRepairDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('vehicleRepairDetails', pk=pk)
    return redirect('vehicleRepairDetails', pk=pk)


def DeleteRepairAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('vehicleRepairDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('vehicleRepairDetails', pk=pk)


def FnRepairRequestLines(request, pk):
    if request.method == 'POST':
        try:
            myUserId = request.session['User_ID']
            defectsType = request.POST.get('defectsType')
            severity = request.POST.get('severity')
            action = request.POST.get('action')
            myAction = request.POST.get('myAction')

        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('vehicleRepairDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnRepairRequestLine(
                myUserId, defectsType, severity, action, myAction)
            messages.success(request, "Request Successful")
            return redirect('vehicleRepairDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('vehicleRepairDetails', pk=pk)
    return redirect('vehicleRepairDetails', pk=pk)


class VehicleInspection(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyVehicleInspection?$filter=CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)

            vehicle = config.O_DATA.format("/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            openRepairReq = [
                x for x in response['value'] if x['Status'] == 'Open'
            ]
            PendingRepairReq = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]
            ApprovedRepair = [
                x for x in response['value'] if x['Status'] == 'Approved'
            ]

            counts = len(openRepairReq)
            pend = len(PendingRepairReq)

            counter = len(ApprovedRepair)
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {
            "today": self.todays_date,
            "open": openRepairReq,
            "count": counts,
            "approved": ApprovedRepair,
            "counter": counter,
            "pend": pend,
            "pending": PendingRepairReq,
            "year": year,
            "full": userID,
            "Vehicle_No": Vehicle_No,
        }
        return render(request, 'vehicleInspection.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                insNo = request.POST.get('insNo')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                mechanicalInspectionRecommedation = request.POST.get(
                    'mechanicalInspectionRecommedation')
                myAction = request.POST.get('myAction')
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('vehicleInspection')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')

            if not insNo:
                insNo = " "

            try:
                response = config.CLIENT.service.FnVehicleInspection(
                    insNo, myUserId, vehicle,
                    mechanicalInspectionRecommedation, myAction)
                messages.success(request, 'Request successful')
            except Exception as e:
                messages.error(request, e)
                return redirect('vehicleInspection')
        return redirect('vehicleInspection')


class VehicleInspectionDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(
                f"/QyVehicleInspection?$filter=No%20eq%20%27{pk}%27%20and%20CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)
            for inspection in response['value']:
                res = inspection

            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('vehicleInspection')

        context = {
            'res': res,
            'Approvers': Approvers,
            'allFiles': allFiles,
        }
        return render(request, 'VehicleInspectionDetails.html', context)


def UploadInspectionAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('VehicleInspectionDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('VehicleInspectionDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('VehicleInspectionDetails', pk=pk)
    return redirect('VehicleInspectionDetails', pk=pk)


def DeleteInspectionAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('VehicleInspectionDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('VehicleInspectionDetails', pk=pk)


def FnBookForInspection(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))

    if request.method == 'POST':
        try:
            insNo = request.POST.get('insNo')
            myUserId = request.session['User_ID']
        except ValueError as e:
            return redirect('VehicleInspectionDetails', pk=pk)

        try:
            response = CLIENT.service.FnBookForInspection(insNo, myUserId)
            messages.success(request, "Book for Inspecton Successfull")

        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('auth')
    return redirect('VehicleInspectionDetails', pk=pk)


class Accidents(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(
                f"/QyaccidentsMaintenance?$filter=CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)
            report = [x for x in response['value']]

            vehicle = config.O_DATA.format(f"/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            driver = config.O_DATA.format(f"/QyDrivers")
            req_driver = self.get_object(driver)
            drivers = [x for x in req_driver['value']]

            count = len(report)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {
            "today": self.todays_date,
            "count": count,
            "User_ID": userID,
            "Vehicle_No": Vehicle_No,
            'drivers': drivers,
            "report": report,
        }

        return render(request, 'Accidents.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                accidentNo = request.POST.get('accidentNo')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                driver = request.POST.get('driver')
                dateOfAccident = request.POST.get('dateOfAccident')
                timeOfAccident = request.POST.get('timeOfAccident')
                descriptionOfAccident = request.POST.get(
                    'descriptionOfAccident')
                location = request.POST.get('location')
                policeStation = request.POST.get('policeStation')
                oBNo = request.POST.get('oBNo')
                insuranceStatus = request.POST.get('insuranceStatus')
                myAction = request.POST.get('myAction')

            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('Accidents')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            if not accidentNo:
                accidentNo = ""

            try:
                response = config.CLIENT.service.FnAccidents(
                    accidentNo,
                    myUserId,
                    vehicle,
                    driver,
                    dateOfAccident,
                    timeOfAccident,
                    descriptionOfAccident,
                    location,
                    policeStation,
                    oBNo,
                    insuranceStatus,
                    myAction,
                )
                messages.success(request, "Request Successful")
                # print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('Accidents')
        return redirect('Accidents')


class AccidentDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(
                f"/QyaccidentsMaintenance?$filter=No%20eq%20%27{pk}%27%20and%20CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)
            for accidents in response['value']:
                res = accidents

            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('Accidents')

        ctx = {
            "res": res,
            'Approvers': Approvers,
            'allFiles': allFiles,
        }
        return render(request, 'AccidentDetails.html', ctx)


def UploadAccidentAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('AccidentDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('AccidentDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('AccidentDetails', pk=pk)
    return redirect('AccidentDetails', pk=pk)


def DeleteAccidentAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('AccidentDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('AccidentDetails', pk=pk)


def FnSubmitAccidents(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    
    accidentNo = ""
    
    if request.method == 'POST':
        try:
            myUserId = request.session['User_ID']
            accidentNo = request.POST.get('accidentNo')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
            
        try:
            response = config.CLIENT.service.FnSubmitAccidents(
                accidentNo, myUserId
            )
            messages.success(request, 'Report Submitted successfuly')
            return redirect('AccidentDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('AccidentDetails', pk=pk)
    return redirect('AccidentDetails', pk=pk)
    

class TransportRequest(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(
                f"/QyTransportRequest?$filter=UserID%20eq%20%27{userID}%27"
            )

            response = self.get_object(Access_Point)

            openTransportRequest = [
                x for x in response['value'] if x['Status'] == 'Open'
            ]

            Pending = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]

            Approved = [
                x for x in response['value'] if x['Status'] == 'Approved'
            ]

            counts = len(openTransportRequest)

            pend = len(Pending)

            counter = len(Approved)

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {
            "today": self.todays_date,
            "res": openTransportRequest,
            "count": counts,
            "response": Approved,
            "counter": counter,
            "pend": pend,
            "pending": Pending,
            "year": year,
            "User_ID": userID,
            "full": userID,
        }

        return render(request, 'TransportRequest.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                tReqNo = request.POST.get('tReqNo')
                myUserId = request.session['User_ID']
                reasonForTravel = request.POST.get('reasonForTravel')
                typeOfTransport = request.POST.get('typeOfTransport')
                destination = request.POST.get('destination')
                approximateDistanceKM = request.POST.get(
                    'approximateDistanceKM')
                tripeStartDate = request.POST.get('tripeStartDate')
                startTime = request.POST.get('startTime')
                tripeEndDate = request.POST.get('tripeEndDate')
                returnTime = request.POST.get('returnTime')
                myAction = request.POST.get('myAction')

            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('imprestReq')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            if not tReqNo:
                tReqNo = " "

            try:
                response = config.CLIENT.service.FnTransportRequest(
                    tReqNo, myUserId, reasonForTravel,typeOfTransport,destination, 
                    approximateDistanceKM,tripeStartDate, startTime, tripeEndDate, returnTime,myAction )
                messages.success(request, "Request Successful")
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('TransportRequest')
        return redirect('TransportRequest')



class TransportRequestDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            
            Access_Point = config.O_DATA.format(
                f"/QyTransportRequest?$filter=RequestNo%20eq%20%27{pk}%27%20and%20UserID%20eq%20%27{userID}%27%20and%20Document_Type%20eq%20%27Service%27"
            )
            response = self.get_object(Access_Point)
            res = [x for x in response['value']]
            print(res)
            # for transport_req in response['value']:
            #     res = transport_req
                
            Access = config.O_DATA.format(f"/QyTransportRequestEmployee?$filter=Request_No_%20eq%20%27{pk}%27")
            LinesRes = self.get_object(Access)
            openLines = [x for x in LinesRes['value']
                         if x['Request_No_'] == pk]
            
            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]
            

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]
        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('TransportRequest')

        ctx = {
            "res": res,
            'Approvers': Approvers,
            'allFiles': allFiles,
            "line": openLines,
        }
        return render(request, 'TransportRequestDetails.html', ctx)

def FnTravelEmployeeLine(request, pk):
    if request.method == 'POST':
        try:
            reqNo = request.POST.get('reqNo')
            myUserId = request.session['User_ID']
            vehicle = request.POST.get('vehicle')
            driver = request.POST.get('driver')
            lineNo = request.POST.get('lineNo')
            myAction = request.POST.get('myAction')
            
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('TransportRequestDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnTravelEmployeeLine(
                reqNo,
                myUserId,
                vehicle,
                driver,
                lineNo,
                myAction,
            )
            messages.success(request, 'request Successful')
            return redirect('TransportRequestDetails', pk=pk )
            
        except Exception as e:
                messages.error(request, e)
                return redirect('TransportRequestDetails', pk=pk )
    return redirect('TransportRequestDetails', pk=pk )



def UploadTransportRequestAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('ServiceRequestDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('TransportRequestDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('TransportRequestDetails', pk=pk)
    return redirect('TransportRequestDetails', pk=pk)


def DeleteTransportRequestAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('TransportRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('TransportRequestDetails', pk=pk)


def FnSubmitTrnsportRequest(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    
    insNo = ""
    
    if request.method == 'POST':
        try:
            myUserId = request.session['User_ID']
            insNo = request.POST.get('insNo')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
            
        try:
            response = config.CLIENT.service.FnSubmitServiceRequest(
                insNo, myUserId
            )
            messages.success(request, 'Request Submited successfuly')
            return redirect('TransportRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('TransportRequestDetails', pk=pk)
    return redirect('TransportRequestDetails', pk=pk)
    

class ServiceRequest(UserObjectMixin, View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            
            Access_Point  = config.O_DATA.format(
                f"/QyServiceRequest?$filter=RequestedBy%20eq%20%27{userID}%27%20and%20Document_Type%20eq%20%27Service%27"
            )
            response = self.get_object(Access_Point)
            
            openServiceRequest = [
                x for x in response['value'] if x['Status'] == 'Open'
            ]

            Pending = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]

            Approved = [
                x for x in response['value'] if x['Status'] == 'Approved'
            ]

            counts = len(openServiceRequest)

            pend = len(Pending)

            counter = len(Approved)
            
            
            vehicle = config.O_DATA.format("/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]
            
            driver = config.O_DATA.format(f"/QyDrivers")
            req_driver = self.get_object(driver)
            drivers = [x for x in req_driver['value']]
            
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {
            "today": self.todays_date,
            "res": openServiceRequest,
            "count": counts,
            "response": Approved,
            "counter": counter,
            "pend": pend,
            "pending": Pending,
            "year": year,
            "User_ID": userID,
            "full": userID,
            "Vehicle_No": Vehicle_No,
            'drivers': drivers,
        }
        return render(request, 'ServiceRequest.html', ctx)
    
    
    def post(self, request):
        if request.method == 'POST':
            try:
                reqNo = request.POST.get('reqNo')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                driver = request.POST.get('driver')
                serviceType = request.POST.get('serviceType')
                currentMileage = request.POST.get('currentMileage')
                costOfRepair = request.POST.get('costOfRepair')
                myAction = request.POST.get('myAction')
            except ValueError:
                messages.error(request, 'Missing Input')
                return redirect('ServiceRequest')
            except KeyError:
                messages.info(request, 'Session Expired, please Login')
                return redirect('auth')
            if not reqNo:
                reqNo = ""
            
            try:
                response = config.CLIENT.service.FnServiceRequest(
                    reqNo,
                    myUserId,
                    vehicle,
                    driver,
                    serviceType,
                    currentMileage,
                    costOfRepair,
                    myAction,
                )
                messages.success(request, 'Request Successful')
                
            except Exception as e:
                messages.error(request, e)
                return redirect('ServiceRequest')
        return redirect('ServiceRequest')
    
    
    
class ServiceRequestDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            
            Access_Point = config.O_DATA.format(
                f"/QyServiceRequest?$filter=No%20eq%20%27{pk}%27%20and%20RequestedBy%20eq%20%27{userID}%27%20and%20Document_Type%20eq%20%27Service%27"
            )
            response = self.get_object(Access_Point)
            for service_req in response['value']:
                res = service_req
                
            Access = config.O_DATA.format(f"/QyServiceRequestLine?$filter=AuxiliaryIndex1%20eq%20%27{pk}%27")
            LinesRes = self.get_object(Access)
            openLines = [x for x in LinesRes['value']
                         if x['AuxiliaryIndex1'] == pk]
            
            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]
            

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]
        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('ServiceRequest')

        ctx = {
            "res": res,
            'Approvers': Approvers,
            'allFiles': allFiles,
            "line": openLines,
        }
        return render(request, 'ServiceRequestDetails.html', ctx)
    
    
def FnServiceRequestLine(request, pk):
    if request.method == 'POST':
        try:
            lineNo = request.POST.get('lineNo')
            myAction = request.POST.get('myAction')
            myUserId = request.session['User_ID']
            defectsType = request.POST.get('defectsType')
            severity = request.POST.get('severity')
            recommendedAction = request.POST.get('recommendedAction')
            serviceDueKM = request.POST.get('serviceDueKM')
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('ServiceRequestDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnServiceRequestLine(
                lineNo,
                myAction,
                myUserId,
                defectsType,
                severity,
                recommendedAction,
                serviceDueKM,
            )
            messages.success(request, 'request Successful')
            return redirect('ServiceRequestDetails', pk=pk )
            
        except Exception as e:
                messages.error(request, e)
                return redirect('ServiceRequestDetails', pk=pk )
    return redirect('ServiceRequestDetails', pk=pk )



def UploadServiceRequestAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('ServiceRequestDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('ServiceRequestDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('ServiceRequestDetails', pk=pk)
    return redirect('ServiceRequestDetails', pk=pk)


def DeleteServiceRequestAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('ServiceRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('ServiceRequestDetails', pk=pk)


def FnSubmitServiceRequest(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    
    insNo = ""
    
    if request.method == 'POST':
        try:
            myUserId = request.session['User_ID']
            insNo = request.POST.get('insNo')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
            
        try:
            response = config.CLIENT.service.FnSubmitServiceRequest(
                insNo, myUserId
            )
            messages.success(request, 'Request Submited successfuly')
            return redirect('ServiceRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('ServiceRequestDetails', pk=pk)
    return redirect('ServiceRequestDetails', pk=pk)
    