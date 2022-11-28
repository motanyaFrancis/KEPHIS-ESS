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
                f"/QyWorkTicket?$filter=CreatedBy%20eq%20%27{empNo}%27")
            response = self.get_object(Access_Point)
            Access_Point_List = [x for x in response]
            # print(response)
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

            Ticket = config.O_DATA.format("/QyWorkTicket")
            res_tkt = self.get_object(Ticket)
            tkt_no = [x for x in res_tkt['value']]

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
        }
        return render(request, 'workticket.html', ctx)

    def post(self, request):
        try:
            myUserId = request.session['User_ID']
            if request.method == 'POST':
                workTicketNo = request.POST.get('No')
                previoursWorkTicketNo = request.POST.get(
                    'PreviousWorkTicketNumber')
                kmCovered = request.POST.get('KmGone')
                vehicle = request.POST.get('Vehicle')
                myAction = request.POST.get('myAction')

        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('workTicket')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
            # if not workTicketNo:
            #     workTicketNo = ""

        try:
            response = config.CLIENT.service.FnWorkTicket(
                # workTicketNo,
                previoursWorkTicketNo,
                kmCovered,
                myUserId,
                vehicle,
                myAction,
            )
            if response == True:
                messages.success(request, "Request Successful")
                return redirect('workTicket')

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
                f"/QyWorkTicket?$filter=No%20eq%20%27{pk}%27%20")
            response = self.get_object(Access_Point)

            for workTicket in response['value']:
                res = workTicket
                print(res)

        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('imprestReq')

        return render(request, 'workTicketDetails.html')


class VehicleRepaiRequest(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyRepairRequest?EmployeeNo%20eq%20%27{empNo}%27")
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
                reqNo = request.POST.get('No')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('VehicleRegistrationNo')
                odometerReading = request.POST.get('OdometerReading')
                repairInstractionSheet = request.POST.get('InternalDocumentNo')
                myAction = request.POST.get('myAstion')
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('vehicleRepairRequest')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')

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


class VehicleInspection(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyVehicleInspection?StaffNo%20eq%20%27{empNo}%27")
            response = self.get_object(Access_Point)

            print(response)

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
            "full": userID
        }
        return render(request, 'vehicleRepairReq.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                insNo = request.POST.get()
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('RegistrationNo')
                mechanicalInspectionRecommedation = request.POST.get(
                    'ServiceInstruction')
                myAction = request.POST.get('myAction')
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('vehicleInspection')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')

            try:
                response = config.CLIENT.service.FnVehicleInspection(
                    insNo, myUserId, vehicle,
                    mechanicalInspectionRecommedation, myAction)
                messages.success(request, 'Request successful')
            except Exception as e:
                messages.error(request, e)
                return redirect('vehicleInspection')
        return redirect('vehicleInspection')


class VehicleRepaiRequestDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            Access_Point = config.O_DATA.format(f"QyRepairRequest?$filter=%20No%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)

            for repair_req in response['value']:
                res = repair_req
                print(res)

        except Exception as e:
            messages.info(request, 'Wrong UserID')
            return redirect('vehicleRepairRequest')
        

        context = {
            "today": self.todays_date,
            "res": res,
            
        }

        return render(request, 'vehicleRepairDetails.html')