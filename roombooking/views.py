import base64
from django.shortcuts import render, redirect
from datetime import datetime
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
from myRequest.views import UserObjectMixins
import asyncio
import aiohttp
from asgiref.sync import sync_to_async

# Create your views here.


class UserObjectMixin(object):
    model = None
    session = Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

class InternalRoomBooking(UserObjectMixins, View):

    async def get(self, request):
        try:   
            User_ID = await sync_to_async(request.session.__getitem__)('User_ID')
            openRequest =[]
            Pending = []
            Approved = []
  
            async with aiohttp.ClientSession() as session:
                task_get_reservations = asyncio.ensure_future(self.fetch_one_filtered_data(
                    session,"/QYvisitors","Created_By","eq",User_ID))

                reservation_response = await asyncio.gather(task_get_reservations) 
                
                if reservation_response[0]['status_code'] == 200: # type: ignore
                    openRequest = [x for x in reservation_response[0]['data'] if x['Booking_Status'] == 'Open' ] # type: ignore
                    Pending = [x for x in reservation_response[0]['data'] if x['Booking_Status'] == 'Pending Approval'] #type:ignore
                    Approved = [x for x in reservation_response[0]['data'] if x['Booking_Status'] == 'Approved'] #type:ignore

            ctx = {
                "res": openRequest,
                "pending":Pending,
                'approved':Approved,
                "today": self.todays_date,
                "full": User_ID,
            }
        except Exception as e:
            messages.error(request, "connection refused,non-200 response")
            print(e)
            return redirect('InternalRoomBooking')
        return render(request, 'InternalRoomBooking.html',ctx)

    async def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                bookingNo = request.POST.get('bookingNo')
                myAction = request.POST.get('myAction')
                typeOfService =request.POST.get('typeOfService')
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                Employee_No_ = await sync_to_async(request.session.__getitem__)('Employee_No_')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnInternalBookingCard',
                                                   bookingNo,myAction,typeOfService,
                                                   False,'-None-',userID,Employee_No_)
                                           
                if response != '0':
                    messages.success(request,"success")
                    return redirect('InternalRoomDetails', pk=response)
                if response == '0':
                    messages.error(request,"Failed, non-201 response")
                    return redirect('InternalRoomBooking')
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('InternalRoomBooking')
            except KeyError as e:
                messages.info(request, f'Session expired,login to continue.')
                print(e)
                return redirect('auth')
            except Exception as e:
                messages.info(request, f'{e}')
                print(e)
                return redirect('InternalRoomBooking')
        return redirect('InternalRoomBooking')


class InternalRoomBookingDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            empNo = request.session['Employee_No_']
            full_name = request.session['full_name']
            res ={}

            Access_Point = config.O_DATA.format(
                f"/QYvisitors?$filter=No_%20eq%20%27{pk}%27%20and%20Created_By%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for booking in response['value']:
                res = booking
                # print(res)


            Accommodation = config.O_DATA.format(f"/QyAccommodationBookingLines?$filter=RoomNo%20eq%20%27{pk}%27")
            res_accommodation = self.get_object(Accommodation)
            AccommodationRoom = [x for x in res_accommodation['value']]
            print(Accommodation)

            MeetingRoom = config.O_DATA.format(f"/QyRoomBookingLines?$filter=RoomNo%20eq%20%27{pk}%27")
            Room = self.get_object(MeetingRoom)
            meeting_room = [x for x in Room['value']]
            print(meeting_room)


            BookingItems = config.O_DATA.format(f"/QYRoomBookingItems?$filter=LineNo%20eq%20%27{pk}%27")
            room_item = self.get_object(BookingItems)
            room_items = [x for x in room_item['value']]

            Service = config.O_DATA.format(f"/QYServicerequired")
            service_req = self.get_object(Service)
            all_services = [x for x in service_req['value']]

            MeetingRoomService = [x for x in service_req['value']
                if x['ServiceRequred'] == 'Meeting Room' or x['ServiceRequred'] == 'Meeting Room And Accommodation'
            ]

            

            AccommodationService = [x for x in service_req['value']
                if x['ServiceRequred'] == 'Accommodation' or x['ServiceRequred'] == 'Meeting Room And Accommodation'
            ]

            RoomType = config.O_DATA.format(f"/QyRoomBookingSetUp?$filter=Booked%20eq%20false")
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
            "today": self.todays_date,
            'res': res,
            'file': allFiles,
            'Approvers': Approvers,
            'full': full_name,
            'AccommodationRoom': AccommodationRoom,
            'meeting_room': meeting_room,
            'room_items': room_items,
            'all_services': all_services,
            'MeetingRoomService': MeetingRoomService,
            'AccommodationService': AccommodationService,
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
            messages.success(request, 'Success')
            return redirect('InternalRoomDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
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
            messages.success(request, 'Success')
            return redirect('InternalRoomDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
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
                messages.error(request, f'{e}')
                print(e)
        if response == True:
            messages.success(request, "File(s) Upload Successful")
            return redirect('InternalRoomDetails', pk=pk)
        else:
            messages.error(request, "Failed, Try Again")
            return redirect('InternalRoomDetails', pk=pk)
    return redirect('InternalRoomDetails', pk=pk)


class FnSubmitInternalRoomBooking(UserObjectMixins, View):
    async def post(self, request,pk):
        if request.method == 'POST':
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                bookingNo = request.POST.get('bookingNo')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnSubmitInternalRoomBooking', bookingNo,userID)

                if response == True:
                    messages.success(request, 'Request Submitted successfully')
                    return redirect('InternalRoomDetails', pk=pk)
                if response == False:
                    messages.success(request, 'Request Failed')
                    return redirect('InternalRoomDetails', pk=pk)
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('InternalRoomDetails', pk=pk)
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
                return redirect('InternalRoomDetails', pk=pk)
        return redirect('InternalRoomDetails', pk=pk)
class FnCancelInternalRoomBooking(UserObjectMixins, View):
    async def post(self, request,pk):
        if request.method == 'POST':
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                bookingNo = request.POST.get('bookingNo')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnSubmitInternalRoomBooking', bookingNo,userID)

                if response == True:
                    messages.success(request, 'Success')
                    return redirect('InternalRoomDetails', pk=pk)
                if response == False:
                    messages.success(request, 'Request Failed')
                    return redirect('InternalRoomDetails', pk=pk)
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('InternalRoomDetails', pk=pk)
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
                return redirect('InternalRoomDetails', pk=pk)
        return redirect('InternalRoomDetails', pk=pk)