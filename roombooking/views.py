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


class InternalRoomBooking(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(f"/QYvisitors?$filter=Created_By%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            # InternalBooking = [x for x in response['value']]
            # print(response)

            openRequest = [
                x for x in response['value'] if x['Booking_Status'] == 'Open'
            ]

            Pending = [
                x for x in response['value']
                if x['Booking_Status'] == 'Pending Approval'
            ]

            Approved = [
                x for x in response['value']
                if x['Booking_Status'] == 'Approved'
            ]

            counts = len(openRequest)

            pend = len(Pending)

            counter = len(Approved)

        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('InternalRoomBooking')
        context = {
            "today": self.todays_date,
            "year": year,
            "full": userID,
            "res": openRequest,
            'count': counts,
            'pend': pend,
            'counter': counter
        }
        return render(request, 'InternalRoomBooking.html', context)

    def post(self, request):
        if request.method == 'POST':
            try:
                bookingNo = request.POST.get('bookingNo')
                typeOfService = request.POST.get('typeOfService')
                myAction = request.POST.get('myAction')
                userID = request.session['User_ID']
                employeeNo = request.session['Employee_No_']
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('InternalRoomBooking')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            if not bookingNo:
                bookingNo = " "

            try:
                response = config.CLIENT.service.FnInternalBookingCard(
                    bookingNo,
                    myAction,
                    typeOfService,
                    userID,
                    employeeNo,
                )
                messages.success(request, "Request Successful")
                print(response)
            except Exception as e:
                messages.info(request, e)
                print(e)
                return redirect('InternalRoomBooking')
        return redirect('InternalRoomBooking')


class InternalRoomBookingDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QYvisitors?$filter=No_%20eq%20%27{pk}%27%20and%20Created_By%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for booking in response['value']:
                res = booking
                # print(res)


            Accommodation = config.O_DATA.format(f"/QyAccommodationBookingLines?$filter=RoomNo%20eq%20%27{pk}%27")
            res_accommodation = self.get_object(Accommodation)
            AccommodationRoom = [x for x in res_accommodation['value']]

            MeetingRoom = config.O_DATA.format(f"/QyRoomBookingLines?$filter=RoomNo%20eq%20%27{pk}%27")
            Room = self.get_object(MeetingRoom)
            meeting_room = [x for x in Room['value']]
            # print(meeting_room)


            BookingItems = config.O_DATA.format(f"/QYRoomBookingItems?$filter=LineNo%20eq%20%27{pk}%27")
            room_item = self.get_object(BookingItems)
            room_items = [x for x in room_item['value']]

            Service = config.O_DATA.format(f"/QYServicerequired")
            service_req = self.get_object(Service)
            all_services = [x for x in service_req['value']]

            RoomType = config.O_DATA.format(f"/QYRooms?$filter=PurposeOfRoom%20eq%20%27Meeting%20Room%27")
            RoomType_req = self.get_object(RoomType)
            room_type = [x for x in RoomType_req['value']]

            # Employee_Access = config.O_DATA.format(f'/QYEmployees')
            # EmployeeList = self.get_object(Employee_Access)
            # Employees = [x for x in EmployeeList['value']]

            # BookingAttendee = config.O_DATA.format(
            #     f"/QYRoombookingattendees?$filter=RoomNo%20eq%20%{pk}%27")
            # res_attendees = self.get_object(BookingAttendee)
            # BookingAttendees = [x for x in res_attendees['value']]

            Approver = config.O_DATA.format(f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]


        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('InternalRoomBooking')

        ctx = {
            'res': res,
            'file': allFiles,
            'Approvers': Approvers,
            'full': userID,
            'accommodationLines': AccommodationRoom,
            'meeting_room': meeting_room,
            'room_items': room_items,
            'all_services': all_services,
            'room_type': room_type,
            # 'Employees': Employees,
            # 'BookingAttendees': BookingAttendees,
        }

        return render(request, 'InternalRoomDetails.html', ctx)


def FnRoomBookingLine(request, pk):
    if request.method == 'POST':
        try:
            bookingNo = request.POST.get('bookingNo')
            typeofRoom = request.POST.get('typeofRoom')
            lineNo = request.POST.get('lineNo')
            myAction = request.POST.get('myAction')
            userCode = request.session['User_ID']
            serviceRequired = request.POST.get('serviceRequired')
            bookingDate = request.POST.get('bookingDate')
            startTime = request.POST.get('startTime')
            endTime = request.POST.get('endTime')
            noOfPeople = request.POST.get('noOfPeople')
            noOfDays = request.POST.get('noOfDays')

        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('InternalRoomDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnRoomBookingLine(
                bookingNo, typeofRoom, lineNo, myAction, userCode,
                serviceRequired, bookingDate, startTime, endTime, noOfPeople,
                noOfDays)
            messages.success(request, 'Request successful')
            return redirect('InternalRoomDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('InternalRoomDetails', pk=pk)
    return redirect('InternalRoomDetails', pk=pk)




def FnAccommodationBookingLine(request, pk):
    if request.method == 'POST':
        try:
            bookingNo = request.POST.get('bookingNo')
            myAction = request.POST.get('myAction')
            userCode = request.session['User_ID']
            serviceRequired = request.POST.get('serviceRequired')
            noOfRooms = request.POST.get('noOfRooms')
            lineNo = request.POST.get('lineNo')
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')

        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('InternalRoomDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnAccomodationBookingLine(
                bookingNo, myAction, userCode, serviceRequired, noOfRooms, lineNo, startDate, endDate
            )
            messages.success(request, 'Request successful')
            return redirect('InternalRoomDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            return redirect('InternalRoomDetails', pk=pk)
    return redirect('InternalRoomDetails', pk=pk)


def UploadRoomBookingAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177430
        except Exception as e:
            return redirect('InternalRoomDetails', pk=pk)
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
            return redirect('InternalRoomDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('InternalRoomDetails', pk=pk)
    return redirect('InternalRoomDetails', pk=pk)


def FnRequestInternalRequestApproval(request, pk):
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))

    tReqNo = ""

    if request.method == 'POST':
        try:
            myUserId = request.session['User_ID']
            requistionNo = request.POST.get('requistionNo')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnRequestInternalRequestApproval(
                requistionNo, myUserId)
            print(response)
            messages.success(request, 'Request Submitted successfully')
            return redirect('InternalRoomDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('InternalRoomDetails', pk=pk)
    return redirect('InternalRoomDetails', pk=pk)