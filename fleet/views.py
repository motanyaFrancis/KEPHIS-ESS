import asyncio
import base64
import logging
import aiohttp
from django.shortcuts import render, redirect
import requests
from requests import Session
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from requests.auth import HTTPBasicAuth
from zeep.client import Client
from zeep.transports import Transport
from django.views import View
from django.http import HttpResponse, JsonResponse
from asgiref.sync import sync_to_async
from myRequest.views import UserObjectMixins
from base64 import b64decode
import io as BytesIO
from django.template.loader import render_to_string
import ast
from datetime import  datetime



# Create your views here.


class UserObjectMixin(object):
    model = None
    session = Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

#################################################
            #Work Tickets 
#################################################
class get_prev_tickets(UserObjectMixin,View):
    def get(self,request):
        value_to_filter = request.GET.get('vehicle')
        work_ticket_endpoint = config.O_DATA.format(f"/QyWorkTicket?$filter=Vehicle%20eq%20%27{value_to_filter}%27%20and%20TicketIssued%20eq%20true")
        api_data = self.get_object(work_ticket_endpoint)
        if 'value' in api_data:
            filtered_data = [item for item in api_data['value'] if item['Work_Ticket_No'] != '']
            options = render_to_string('options.html', {'options': filtered_data})
            options = options.replace("\\", "").replace("\"", "")
            return HttpResponse(options, content_type='application/json')
        else:
            return HttpResponse('error')
class WorkTicket(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            driver_role =request.session['driver_role']
            TO_role =request.session['TO_role']
            full_name = request.session['full_name']
            

            Access_Point = config.O_DATA.format(
                f"/QyWorkTicket?$filter=CreatedBy%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)

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

            IssuedTicket = [
                x for x in response['value'] if x['Status'] == 'Approved' and x['TicketIssued'] == True
            ]
            tickets_waiting_issuing = config.O_DATA.format(
                f"/QyWorkTicket?$filter=Status%20eq%20%27Approved%27%20and%20TicketIssued%20eq%20false")
            tickets_waiting_issuing_response = self.get_object(tickets_waiting_issuing)
            issued_open = [x for x in tickets_waiting_issuing_response['value']]
            
            counts = len(openTicket)
            pend = len(PendingTicket)
            counter = len(ApprovedTicket)
            issued = len(IssuedTicket)


            vehicle = config.O_DATA.format("/QyFixedAssets?$filter=Fixed_Asset_Type%20eq%20%27Fleet%27")
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
            "open": openTicket,
            "count": counts,
            "driver_role":driver_role,
            "TO_role":TO_role,
            "issued_open":issued_open,
            'issued': issued,
            "approved": ApprovedTicket,
            "counter": counter,
            "pend": pend,
            "pending": PendingTicket,
            "full": full_name,
            'Vehicle_No': Vehicle_No,
            'drivers': drivers,
        }
        return render(request, 'workTicket.html', ctx)
    

    def post(self, request):
        if request.method == 'POST':
            try:
                employeeNo = request.session['Employee_No_']
                myUserId = request.session['User_ID']
                
                workTicketNo = request.POST.get('workTicketNo')
                # prevWorkTicketNo =request.POST.get('prevWorkTicketNo')
                driver = request.POST.get('driver')
                reasonForReplacement = request.POST.get('reasonForReplacement')
                currentWorkTicketNo = request.POST.get('currentWorkTicketNo')
                kmCovered = request.POST.get('kmCovered')
                vehicle = request.POST.get('vehicle')
                myAction = request.POST.get('myAction')
                                
                # if not prevWorkTicketNo:
                #     prevWorkTicketNo ='None'

                response = config.CLIENT.service.FnWorkTicket(workTicketNo,employeeNo,myAction,
                                                                driver,reasonForReplacement,
                                                               currentWorkTicketNo,kmCovered,myUserId,vehicle)
                if response == True:
                    messages.success(request, "Request Successful")
                    return redirect('workTicket')
                if response == False:
                    messages.error(request, response)
                return redirect('workTicket')
            except Exception as e:
                messages.error(request, "OOps!! Something went wrong")
                print(e)
                return redirect('workTicket')
        return redirect('workTicket')
    
class FnIssueWorkTicket(UserObjectMixins,View):
    async def post(self,request,pk):
        try:
            user_id = await sync_to_async(request.session.__getitem__)('User_ID')
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            response =  self.make_soap_request(soap_headers,'FnIssueWorkTicket',
                                               pk, user_id)
            
            if response == True:
                messages.success(request, f"Work ticket {pk} issued successfully")
                return redirect('workTicket')
            if response == False:
                messages.error(request,"Issuing Failed")
                return redirect('workTicket')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('workTicket')  

class WorkTicketDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            full_name = request.session['full_name']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            res = {}

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
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }

        return render(request, 'workTicketDetails.html', ctx)


def UploadTicketAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52178012
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
                messages.error(request, "OOps!! Something went wrong")
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
            messages.error(request, "OOps!! Something went wrong" )
            print(e)
    return redirect('WorkTicketDetails', pk=pk)


class FnSubmitWorkTicket(UserObjectMixins, View):
    async def post(self,request, pk):
        if request.method == "POST":
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                workTicketNo = request.POST.get('workTicketNo')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnSubmitWorkTicket', workTicketNo,userID)

                if response == True:
                    messages.success(request, 'Request Submitted successfully')
                    return redirect('WorkTicketDetails', pk=pk)
                if response == False:
                    messages.success(request, 'Request Failed')
                    return redirect('WorkTicketDetails', pk=pk)
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('WorkTicketDetails', pk=pk)
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, "OOps!! Something went wrong")
                print(e)
                return redirect('WorkTicketDetails', pk=pk)
        return redirect('WorkTicketDetails', pk=pk)


def FnCancelWorkTicket(request, pk):
    if request.method == 'POST':
        try:
            workTicketNo = request.POST.get('workTicketNo')
            myUserId = request.session['User_ID']
        except ValueError as e:
            return redirect('WorkTicketDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelWorkTicket(
                workTicketNo, myUserId)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('WorkTicketDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('auth')
    return redirect('WorkTicketDetails', pk=pk)
        
class FnGenerateWorkTicketReport(UserObjectMixins, View):
    async def post(self,request,pk):
        try:
            filenameFromApp = "work_ticket_" + pk + ".pdf"
            user_id = await sync_to_async(request.session.__getitem__)('User_ID')
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            response =  self.make_soap_request(soap_headers,'FnWorkTicketReqister',pk,
                                                                                filenameFromApp,user_id)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
            buffer.getvalue(),content_type="application/pdf",)
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
                messages.error(request, f'{e}')
                print(e)
                return redirect('WorkTicketDetails', pk=pk)

#################################################
            #Vehicle Repair 
#################################################
class VehicleRepairRequest(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            full_name = request.session['full_name']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']

            Access_Point = config.O_DATA.format(
                f"/QyRepairRequest?$filter=Requested_By%20eq%20%27{userID}%27%20and%20Document_Type%20eq%20%27Repair%27")
            response = self.get_object(Access_Point)
            

            vehicle = config.O_DATA.format("/QyFixedAssets?$filter=Fixed_Asset_Type%20eq%20%27Fleet%27")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            driver = config.O_DATA.format(f"/QyDrivers")
            req_driver = self.get_object(driver)
            drivers = [x for x in req_driver['value']]


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
            "openRepairReq":openRepairReq,
            "pending":PendingRepairReq,
            "approved":ApprovedRepair,
            "Vehicle_No": Vehicle_No,
            'drivers': drivers,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }
        return render(request, 'vehicleRepairReq.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                typeOfRepair = int(request.POST.get('typeOfRepair'))
                reqNo = request.POST.get('reqNo')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                driver = request.POST.get('driver')
                odometerReading = request.POST.get('odometerReading')
                costOfRepair = request.POST.get('costOfRepair')
                repairInstractionSheet = request.POST.get(
                    'repairInstractionSheet')
                myAction = request.POST.get('myAction')
                towingCost= float(request.POST.get('towingCost'))
                invoiceNo= request.POST.get('invoiceNo')

                response = config.CLIENT.service.FnRepairRequestHeader(
                    reqNo, myUserId, vehicle,  odometerReading, driver,
                    myAction, typeOfRepair, costOfRepair, invoiceNo, towingCost)
                if response == True:
                    messages.success(request, "Request Successful")
                    return redirect('vehicleRepairRequest')
            except Exception as e:
                print(f'{e}')
                messages.error(request, "Oops!! Something Went Wrong")
                return redirect('vehicleRepairRequest')
        return redirect('vehicleRepairRequest')

class FnConfirmRepaireRequest (UserObjectMixins,View):
    async def post(self,request,pk):
        if request.method == 'POST':
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnConfirmRepaireRequest',pk,userID)
                print(response)

                if response == True:
                    messages.success(request, 'Confirmation successful')
                    return redirect('vehicleRepairRequest')
                if response == False:
                    messages.success(request, 'Request Failed')
                    return redirect('vehicleRepairRequest')
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('vehicleRepairRequest')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, "OOps!! Something went wrong")
                print(e)
                return redirect('vehicleRepairRequest')
        return redirect('vehicleRepairRequest')
                

class VehicleRepairRequestDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            full_name = request.session['full_name']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']


            Access_Point = config.O_DATA.format(
                f"/QyRepairRequest?$filter=No_%20eq%20%27{pk}%27%20and%20Requested_By%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)
            repair_response = [x for x in response['value']]
            for repair_req in response['value']:
                repair_response = repair_req

            Access = config.O_DATA.format(
                 f"/QyRepairRequestLines"
            )
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

            Employee = config.O_DATA.format(f"/QYEmployees")
            EmployeeRes = self.get_object(Employee)
            Employees = [x for x in EmployeeRes['value']]

            Vendor = config.O_DATA.format(f"/VendorDetails?$filter=Vendor_Type%20eq%20%27Garage%27")
            VendorRes = self.get_object(Vendor)
            Vendors = [x for x in VendorRes['value']]
            

            ServeInstruction = config.O_DATA.format(f"/QyServiceIntrustionsSheet?$filter=No%20eq%20%27{pk}%27")
            ServeInstructionRes = self.get_object(ServeInstruction)
            ServeInstructions = [x for x in ServeInstructionRes['value']]
            print(ServeInstructions)

        except Exception as e:
            messages.info(request, f'{e}')
            return redirect('vehicleRepairRequest')

        context = {
            "today": self.todays_date,
            "res": repair_response,
            "line": openLines,
            'allFiles': allFiles,
            "Approvers": Approvers,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
            'Employees': Employees,
            'Vendors': Vendors,
            'ServeInstructions': ServeInstructions,
        }

        return render(request, 'vehicleRepairDetails.html', context)


def UploadRepairAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177432
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
                messages.error(request, "OOps!! Something went wrong")
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
            messages.error(request, "OOps!! Something went wrong")
            print(e)
    return redirect('vehicleRepairDetails', pk=pk)


def FnRepairRequestLines(request, pk):
    if request.method == 'POST':
        try:
            requisitionNo = request.POST.get('requisitionNo')
            defectsType = request.POST.get('defectsType')
            specification = request.POST.get('specification')
            lineNo = int(request.POST.get('lineNo'))
            myUserId = request.session['User_ID']
            myAction = request.POST.get('myAction')

            response = config.CLIENT.service.FnRepairRequestLine(
                requisitionNo,
                defectsType,
                specification,
                lineNo,
                myUserId,
                myAction,
                )
            if response == True:
                messages.success(request, "Request Successful")
                return redirect('vehicleRepairDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            return redirect('vehicleRepairDetails', pk=pk)
    return redirect('vehicleRepairDetails', pk=pk)


class FnRaiseRepairRequest(UserObjectMixins, View):
    async def post(self,request,pk):
        if request.method == 'POST':
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                insNo = request.POST.get('insNo')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnSubmitRepaireRequest', insNo,userID)
                
                print(response)

                if response == True:
                    messages.success(request, 'Request Submitted successfully')
                    return redirect('vehicleRepairDetails', pk=pk)
                if response == False:
                    messages.success(request, 'Request Failed')
                    return redirect('vehicleRepairDetails', pk=pk)
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('vehicleRepairDetails', pk=pk)
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, "OOps!! Something went wrong")
                print(e)
                return redirect('vehicleRepairDetails', pk=pk)
        return redirect('vehicleRepairDetails', pk=pk)


def FnCancelRepairRequest(request, pk):
    if request.method == 'POST':
        try:
            reqNo = request.POST.get('reqNo')
            myUserId = request.session['User_ID']
        except ValueError as e:
            return redirect('vehicleRepairDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelRepairRequest(
               reqNo, myUserId)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('vehicleRepairDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('auth')
    return redirect('vehicleRepairDetails', pk=pk)



class FNServiceInstructionsSheet(UserObjectMixins,View):
    async def post(self, request, pk):
        if request.method == 'POST':
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                vrNo= pk
                lineNo= request.POST.get('lineNo')
                serviceOrRepair= request.POST.get('serviceOrRepair')
                garage= request.POST.get('garage')
                myAction= request.POST.get('myAction')
                quote= request.POST.get('quote')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FNServiceInstructionsSheet', vrNo, myAction, lineNo, userID, serviceOrRepair,garage, quote)
                
                print(response)

                if response == True:
                    messages.success(request, 'Request Submitted successfully')
                    return redirect('vehicleRepairDetails', pk=pk)
                if response == False:
                    messages.info(request, 'Request Failed')
                    return redirect('vehicleRepairDetails', pk=pk)
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('vehicleRepairDetails', pk=pk)
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, "OOps!! Something went wrong")
                print(e)
                return redirect('vehicleRepairDetails', pk=pk)
        return redirect('vehicleRepairDetails', pk=pk)



#################################################
    #        Inspection
#################################################
class VehicleInspection(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']

            Access_Point = config.O_DATA.format(
                f"/QyVehicleInspection?$filter=CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)



            openInspectionReq = [
                x for x in response['value'] if x['Status'] == 'Open'
            ]
            PendingInspectionReq = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]
            ApprovedInspection = [
                x for x in response['value']
                if x['Status'] == 'Approved' 
            ]
            BookedInspection = [
                x for x in response['value']
                if x['Booked_For_Inspection'] == True
            ]
            Inspected = [
                x for x in response['value']
                if x['Status'] == 'Inspected'
            ]

            mechanical_e_url = config.O_DATA.format(
                f"/QyVehicleInspection?$filter=Status%20eq%20%27Approved%27%20and%20Booked_For_Inspection%20eq%20false"
            )
            m_response = self.get_object(mechanical_e_url)
            
            mechanical_response = [x for x in m_response['value']]

            counts = len(openInspectionReq)
            pend = len(PendingInspectionReq)
            counter = len(ApprovedInspection)
            bookedCount = len(BookedInspection)

            vehicle = config.O_DATA.format("/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            driver = config.O_DATA.format(f"/QyDrivers")
            req_driver = self.get_object(driver)
            drivers = [x for x in req_driver['value']]
            
            Inspector = config.O_DATA.format(f'/QyMechanicalInspectors')
            inspector_data = self.get_object(Inspector)
            Inspectors = [x for x in inspector_data['value']]

            TransportOfficer = config.O_DATA.format(f'/QyTransportOfficers')
            tOfficer_data = self.get_object(TransportOfficer)
            TransportOfficers = [x for x in tOfficer_data['value']]

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
            "open": openInspectionReq,
            "count": counts,
            "approved": ApprovedInspection,
            "counter": counter,
            "pend": pend,
            'booked': BookedInspection,
            'bookedCount': bookedCount,
            'inspected': Inspected,
            "pending": PendingInspectionReq,
            "Vehicle_No": Vehicle_No,
            'drivers': drivers,
            'Inspectors': Inspectors,
            'TransportOfficers': TransportOfficers,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
            "mechanical_response":mechanical_response,
        }
        return render(request, 'vehicleInspection.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                insNo = request.POST.get('insNo')
                myAction = request.POST.get('myAction')
                employeeNo = request.session['Employee_No_']
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                driver = request.POST.get('driver')
                mechanicalInspectionRecommedation = request.POST.get(
                    'mechanicalInspectionRecommedation')
            
                response = config.CLIENT.service.FnVehicleInspection(
                    insNo, 
                    myAction,
                    employeeNo,
                    myUserId, 
                    vehicle, 
                    driver, 
                    mechanicalInspectionRecommedation, 
                    )
                if response != '0':
                    messages.success(request, "Request Successful")
                    return redirect('VehicleInspectionDetails', pk=response)
                messages.error(request, f"{response}")
                return redirect('vehicleInspection')
            except Exception as e:
                messages.error(request, f'{e}')
                return redirect('vehicleInspection')
        return redirect('vehicleInspection')


class VehicleInspectionDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']

            Access_Point = config.O_DATA.format(
                f"/QyVehicleInspection?$filter=No%20eq%20%27{pk}%27"
            )
            response = self.get_object(Access_Point)
            res = [x for x in response['value']]
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
            
            Lines_Res = config.O_DATA.format(
                f"/QyVehicleInspectionLines?$filter=No%20eq%20%27{pk}%27")
            responses = self.get_object(Lines_Res)
            openLines = [x for x in responses['value']]

        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('vehicleInspection')

        context = {
            'res': res,
            'Approvers': Approvers,
            'allFiles': allFiles,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
            "openLines":openLines,
        }
        return render(request, 'VehicleInspectionDetails.html', context)

def InspectionDefects(request, pk):
    if request.method == 'POST':
        try:
            defectsType = request.POST.get('defectsType')
            specification = request.POST.get('specification')
            lineNo = int(request.POST.get('lineNo'))
            myUserId = request.session['User_ID']
            myAction = request.POST.get('myAction')

            response = config.CLIENT.service.FnVehicleInspectionLines(
                pk,
                myAction,lineNo,myUserId,defectsType,
                specification
                )
            if response == True:
                messages.success(request, "Request Successful")
                return redirect('VehicleInspectionDetails', pk=pk)
            if response == False:
                messages.error(request,f'{response}')
                return redirect('VehicleInspectionDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            return redirect('VehicleInspectionDetails', pk=pk)
    return redirect('VehicleInspectionDetails', pk=pk)


def UploadInspectionAttachment(request, pk):
    try:
        attach = request.FILES.getlist('attachment')
        tableID = 52178014
        for files in attach:
            fileName = request.FILES['attachment'].name
            print(tableID)
            attachment = base64.b64encode(files.read())
            response = config.CLIENT.service.FnUploadAttachedDocument(
                    pk, fileName, attachment, tableID,
                    request.session['User_ID'])
                
            if response == True:
                messages.success(request, "File(s) Upload Successful")
                return redirect('VehicleInspectionDetails', pk=pk)
    except Exception as e:
        messages.error(request, f'{e}')
        print(e)
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
            messages.error(request, f'{e}')
            print(e)
    return redirect('VehicleInspectionDetails', pk=pk)


class  FnSubmitVehicleInspection(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            insNo = request.POST.get('insNo')
            myUserId = request.session['User_ID']

            response = self.make_soap_request(soap_headers,'FnSubmitVehicleInspection',
                                              insNo, myUserId)
            if response == True:
                messages.success(request, "Request Successful")
                return redirect('VehicleInspectionDetails', pk=pk)
            messages.error(request, "Request Successful")
            return redirect('VehicleInspectionDetails', pk=pk)

        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('VehicleInspectionDetails', pk=pk)

class Submit2_TO(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            myUserId = request.session['User_ID']

            response = self.make_soap_request(soap_headers,'FnSubmitVehicleInspection',
                                              pk, myUserId)
            if response == True:
                messages.success(request, "Submitted")
                return redirect('VehicleInspectionDetails', pk=pk)
            if response == False:
                messages.success(request, f'{response}')
                return redirect('VehicleInspectionDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('VehicleInspectionDetails', pk=pk)

class FnMarkInspected(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            myUserId = request.session['User_ID']

            response = self.make_soap_request(soap_headers,'FnMarkInspected',
                                              pk, myUserId)
            if response == True:
                messages.success(request, "Submitted")
                return redirect('vehicleInspection')
            if response == False:
                messages.success(request, f'{response}')
                return redirect('vehicleInspection')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('vehicleInspection')

class FnBookForInspection(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            myUserId = request.session['User_ID']
            
            response = self.make_soap_request(soap_headers,'FnBookForInspection',
                                              pk, myUserId)
            if response == True:
                messages.success(request, "Booking Successful")
                return redirect('vehicleInspection')
            elif response == False:
                messages.error(request, f"{response}")
                return redirect('vehicleInspection')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('vehicleInspection')

def FnCancelBooking(request, pk):
    if request.method == 'POST':
        try:
            bookingNo = pk
            userCode = request.session['User_ID']
        except ValueError as e:
            return redirect('VehicleInspectionDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelBooking(
                bookingNo, userCode)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('VehicleInspectionDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('auth')
    return redirect('VehicleInspectionDetails', pk=pk)

#################################################
    #       Accidents
#################################################
class Accidents(UserObjectMixin, View):

    def get(self, request):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']

            Access_Point = config.O_DATA.format(
                f"/QyaccidentsMaintenance?$filter=CreatedBy%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)
            report = [x for x in response['value'] if x['DocumentStage'] == 'Not-Submitted']

            submitted = [x for x in response['value'] if x['DocumentStage'] == 'Submitted']

            vehicle = config.O_DATA.format(f"/QyFixedAssets")
            res_veh = self.get_object(vehicle)
            Vehicle_No = [x for x in res_veh['value']]

            driver = config.O_DATA.format(f"/QyDrivers")
            req_driver = self.get_object(driver)
            drivers = [x for x in req_driver['value']]

            count = len(report)

            submit_count = len(submitted)

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
            'submit_count': submit_count,
            "Vehicle_No": Vehicle_No,
            'drivers': drivers,
            "report": report,
            'submitted': submitted,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }

        return render(request, 'Accidents.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                accidentNo = request.POST.get('accidentNo')
                myUserId = request.session['User_ID']
                vehicle = request.POST.get('vehicle')
                driver = request.POST.get('driver')
                dateOfAccident =  datetime.strptime(request.POST.get('dateOfAccident'), '%Y-%m-%d').date()
                timeOfAccident = datetime.strptime(request.POST.get('timeOfAccident'), '%H:%M').time()
                descriptionOfAccident = request.POST.get(
                    'descriptionOfAccident')
                location = request.POST.get('location')
                policeStation = request.POST.get('policeStation')
                oBNo = request.POST.get('oBNo')
                insuranceStatus = request.POST.get('insuranceStatus')
                myAction = request.POST.get('myAction')
                ReinstatementFee = float(request.POST.get('ReinstatementFee'))
                damage_repair_cost = float(request.POST.get('damage_repair_cost'))
                Towing_cost = float(request.POST.get('Towing_cost'))
                Excess_cost = float(request.POST.get('Excess_cost'))
                damage_repair = request.POST.get('damage_repair')
                Remarks = request.POST.get('Remarks')
                
                if not Excess_cost:
                    Excess_cost  = 0

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
                    ReinstatementFee,
                    damage_repair,
                    Towing_cost,
                    damage_repair_cost,
                    Remarks,
                    Excess_cost
                )
                if response != '0':
                    messages.success(request, "Request Successful")
                    return redirect('AccidentDetails',pk=response)
                else:
                    messages.error(request, f"{response}")
                    return redirect('Accidents')
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
                return redirect('Accidents')
        return redirect('Accidents')


class AccidentDetails(UserObjectMixin, View):

    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']
            res = {}

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
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }
        return render(request, 'AccidentDetails.html', ctx)


def UploadAccidentAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 50002 #52177430
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
                messages.error(request, f'{e}')
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
            messages.error(request, f'{e}')
            print(e)
    return redirect('AccidentDetails', pk=pk)


class  FnSubmitAccidents(UserObjectMixins, View):
    async def post(self,request,pk):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            accidentNo = request.POST.get('accidentNo')
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
            response =  self.make_soap_request(soap_headers,'FnSubmitAccidents',accidentNo,userID)

            if response == True:
                messages.success(request, 'Submitted Successfully')
                return redirect('AccidentDetails', pk=pk)
            if response == False:
                messages.success(request, 'Request Failed')
                return redirect('AccidentDetails', pk=pk)
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"connect timed out")
            return redirect('AccidentDetails', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'{e}')
            return redirect('AccidentDetails', pk=pk)
        return redirect('AccidentDetails', pk=pk)


#################################################
    #    Transport Request
#################################################

class TransportRequest(UserObjectMixins, View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']

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

            destination = config.O_DATA.format("/QyDestinations")
            res_dest = self.get_object(destination)
            Local = [
                x for x in res_dest['value']
                if x['Destination_Type'] == 'Local'
            ]


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
            'Local': Local,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }

        return render(request, 'TransportRequest.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                tReqNo = request.POST.get('tReqNo')
                myUserId = request.session['User_ID']
                reasonForTravel = request.POST.get('reasonForTravel')
                typeOfTransport = int(request.POST.get('typeOfTransport'))
                destination = request.POST.get('destination')
                tripeStartDate = datetime.strptime(request.POST.get('tripeStartDate'), '%Y-%m-%d').date()
                startTime = datetime.strptime(request.POST.get('startTime'), '%H:%M').time()
                tripeEndDate = datetime.strptime(request.POST.get('tripeEndDate'), '%Y-%m-%d').date()
                myAction = request.POST.get('myAction')
                TravelingEmployees = request.POST.get('TravelingEmployees')
                
                if not TravelingEmployees:
                    TravelingEmployees = 0

                response = config.CLIENT.service.FnTransportRequest(
                    tReqNo, myUserId, reasonForTravel,typeOfTransport,destination,
                    tripeStartDate, startTime, tripeEndDate,myAction,int(TravelingEmployees))
                if response != '0':
                    messages.success(request, "Request Successful")
                    return redirect('TransportRequestDetails', pk=response)
                messages.error(request, f"{response}")
                return redirect('TransportRequest')
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
                return redirect('TransportRequest')
        return redirect('TransportRequest')


class TransportRequestDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']
            res = {}

            Access_Point = config.O_DATA.format(
                f"/QyTransportRequest?$filter=RequestNo%20eq%20%27{pk}%27%20and%20UserID%20eq%20%27{userID}%27"
            )
            response = self.get_object(Access_Point)
            for transport_req in response['value']:
                res = transport_req
                # print(res)

            Access = config.O_DATA.format(f"/QyTransportRequestEmployee?$filter=Request_No_%20eq%20%27{pk}%27")
            LinesRes = self.get_object(Access)
            openLines = [x for x in LinesRes['value']
                         if x['Request_No_'] == pk]

            Employee = config.O_DATA.format(f"/QYEmployees")
            EmployeeRes = self.get_object(Employee)
            Employees = [x for x in EmployeeRes['value']]

            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]


            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            destination = config.O_DATA.format("/QyDestinations")
            res_dest = self.get_object(destination)
            Local = [x for x in res_dest['value']
                     if x['Destination_Type'] == 'Local']
            Foreign = [x for x in res_dest['value']
                          if x['Destination_Type'] == 'Foreign']

        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('TransportRequest')

        ctx = {
            "res": res,
            "today": self.todays_date,
            'Approvers': Approvers,
            'allFiles': allFiles,
            "line": openLines,
            'Employees': Employees,
            'Local': Local,
            'Foreign': Foreign,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }
        return render(request, 'TransportRequestDetails.html', ctx)

def FnTravelEmployeeLine(request, pk):
    if request.method == 'POST':
        try:
            reqNo = request.POST.get('reqNo')
            myUserId = request.session['User_ID']
            employeeNo = request.POST.get('employeeNo')
            lineNo = request.POST.get('lineNo')
            myAction = request.POST.get('myAction')

        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('TransportRequestDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnTravelEmployeeLine(
                reqNo, myUserId, employeeNo, lineNo, myAction,
            )
            print(response)
            messages.success(request, 'request Successful')
            return redirect('TransportRequestDetails', pk=pk )

        except Exception as e:
            messages.error(request, f'{e}')
            return redirect('TransportRequestDetails', pk=pk )
    return redirect('TransportRequestDetails', pk=pk )



def UploadTransportRequestAttachment(request, pk):

    response = ''
    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
            tableID = 52177518
        except Exception as e:
            return redirect('TransportRequestDetails', pk=pk)
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
            messages.error(request, f'{e}')
            print(e)
    return redirect('TransportRequestDetails', pk=pk)


class FnSubmitTravelRequest(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            myUserId = request.session['User_ID']
            tReqNo = request.POST.get('tReqNo')

            response = self.make_soap_request(soap_headers,'FnSubmitTravelRequests',
                                              tReqNo, myUserId)
            if response == True:
                messages.success(request, 'Request Submitted successfully')
                return redirect('TransportRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('TransportRequestDetails', pk=pk)


class FnNotifyBothRequesterAndDrivers(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            docNo = pk

            response = self.make_soap_request(soap_headers,'FnNotifyBothRequesterAndDrivers',
                                              docNo)
            if response == True:
                messages.success(request, 'Request Submitted successfully')
                return redirect('TransportRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('TransportRequestDetails', pk=pk)


#################################################
    #       Service Request
#################################################

        
class ServiceRequest(UserObjectMixins, View):
    async def get(self, request):
        try:
            User_ID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role =await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role =await sync_to_async(request.session.__getitem__)('TO_role')
            full_name =await sync_to_async(request.session.__getitem__)('full_name')
            
            openServiceRequest = []
            Pending = []
            Approved = []
            Vehicle_No = []
            drivers = []
            
            async with aiohttp.ClientSession() as session:
                task_get_service = asyncio.ensure_future(self.simple_double_filtered_data(session,"/QyServiceRequest",
                                    "RequestedBy","eq",User_ID,"and","Document_Type","eq","Service"))
                
                task_get_assets = asyncio.ensure_future(self.simple_fetch_data(session,"/QyFixedAssets"))
                
                task_get_drivers = asyncio.ensure_future(self.simple_fetch_data(session,'/QyDrivers'))
                
                response = await asyncio.gather(task_get_service,task_get_assets,task_get_drivers)
                
                openServiceRequest = [x for x in response[0] if x['Status'] == 'Open' ] # type: ignore
                Pending = [x for x in response[0] if x['Status'] == 'Pending Approval'] #type:ignore
                Approved = [x for x in response[0] if x['Status'] == 'Approved'] #type:ignore

                Vehicle_No = [x for x in response[1]] # type: ignore
                
                drivers = [x for x in response[2]] # type: ignore
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"Authentication Error: Invalid credentials")
            return redirect('dashboard')   
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print(e)
            messages.error(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('dashboard')

        ctx = {
            "today": self.todays_date,
            "res": openServiceRequest,
            "response": Approved,
            "pending": Pending,
            "User_ID": User_ID,
            "Vehicle_No": Vehicle_No,
            'drivers': drivers,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }
        return render(request, 'ServiceRequest.html', ctx)


    async def post(self, request):
        try:
            reqNo = request.POST.get('reqNo')
            vehicle = request.POST.get('vehicle')
            driver = request.POST.get('driver')
            serviceType = request.POST.get('serviceType')
            currentMileage = request.POST.get('currentMileage')
            costOfRepair = request.POST.get('costOfRepair')
            myAction = request.POST.get('myAction')
            
            userID = await sync_to_async(request.session.__getitem__)('User_ID')

            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
            response =  self.make_soap_request(soap_headers,'FnServiceRequest',
                                               reqNo, userID, vehicle, driver,
                                               serviceType, currentMileage,
                                               costOfRepair, myAction )
            
            print(response)

            if response == True:
                messages.success(request, 'Success')
                return redirect('ServiceRequest')
            if response == False:
                messages.success(request, 'Request Failed')
                return redirect('ServiceRequest')
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"connect timed out")
            return redirect('ServiceRequest')
        except ValueError:
            messages.error(request, 'Missing Input')
            return redirect('ServiceRequest')
        except KeyError:
            messages.info(request, 'Session Expired, please Login')
            return redirect('auth')

        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('ServiceRequest')
        return redirect('ServiceRequest')



class ServiceRequestDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            full_name = request.session['full_name']
            
            res ={}

            Access_Point = config.O_DATA.format(
                f"/QyServiceRequest?$filter=No%20eq%20%27{pk}%27%20and%20RequestedBy%20eq%20%27{userID}%27%20and%20Document_Type%20eq%20%27Service%27"
            )
            response = self.get_object(Access_Point)
            for service_req in response['value']:
                res = service_req

            Access = config.O_DATA.format(f"/QyServiceRequestLine?$filter=Document_No_%20eq%20%27{pk}%27")
            LinesRes = self.get_object(Access)
            
            line = [line for line in LinesRes['value']]
            

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
            "line":line,
            "full": full_name,
            "driver_role":driver_role,
            "TO_role":TO_role,
        }
        return render(request, 'ServiceRequestDetails.html', ctx)


def FnServiceRequestLine(request, pk):
    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            reqNo = request.POST.get('reqNo')
            myAction = request.POST.get('myAction')
            myUserId = request.session['User_ID']
            defectsType = request.POST.get('defectsType')
            severity = request.POST.get('severity')
            recommendedAction = request.POST.get('recommendedAction')
            
            response = config.CLIENT.service.FnServiceRequestLine(
                reqNo,
                defectsType,
                severity,
                recommendedAction,
                lineNo,
                myUserId,
                myAction
            )
            print(response)
            if response == True:
                messages.success(request, 'request Successful')
                return redirect('ServiceRequestDetails', pk=pk )
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('ServiceRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
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
                messages.error(request, f'{e}')
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
            messages.error(request, f'{e}')
            print(e)
    return redirect('ServiceRequestDetails', pk=pk)


class FnSubmitServiceRequest(UserObjectMixins, View):
    async def post(self, request,pk):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            insNo = request.POST.get('insNo')
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
            response =  self.make_soap_request(soap_headers,'FnSubmitServiceRequest',insNo,userID)

            if response == True:
                messages.success(request, 'Submitted Successfully')
                return redirect('ServiceRequestDetails', pk=pk)
            if response == False:
                messages.success(request, 'Request Failed')
                return redirect('ServiceRequestDetails', pk=pk)
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"connect timed out")
            return redirect('ServiceRequestDetails', pk=pk)
           
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        except Exception as e:
            messages.error(request, f'{e}')
            return redirect('ServiceRequestDetails', pk=pk)
        return redirect('ServiceRequestDetails', pk=pk)


def FnCancelServiceRequest(request, pk):
    if request.method == 'POST':
        try:
            insNo = request.POST.get('insNo')
            myUserId = request.session['User_ID']
        except ValueError as e:
            return redirect('ServiceRequestDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnCancelServiceRequest(
                myUserId, insNo)
            messages.success(request, "Cancel Approval Successful")
            print(response)
            return redirect('ServiceRequestDetails', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('auth')
    return redirect('ServiceRequestDetails', pk=pk)



#################################################
    #       Fuel Consumption
#################################################

class FuelConsumption(UserObjectMixins,View):
    async def get(self,request):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role = await sync_to_async(request.session.__getitem__)('TO_role')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            employeeNo =  await sync_to_async(request.session.__getitem__)('Employee_No_')
            
            print(employeeNo)

            full_name = request.session['full_name']
            openRequest = []
            submitted = []


            async with aiohttp.ClientSession() as session:
                task_get_reservations = asyncio.ensure_future(self.fetch_one_filtered_data(
                    session,"/QyFuelRegister","Created_By","eq",userID))

                task_get_vendor = asyncio.ensure_future(self.simple_one_filtered_data(session,'/VendorDetails',
                                                                                    'Vendor_Type',"eq",
                                                                                    'Fuel Station'))
                task_get_vehicle = asyncio.ensure_future(self.simple_one_filtered_data(session,'/QyFixedAssets',
                                                                                    'Fixed_Asset_Type',"eq",
                                                                                    'Fleet'))
                task_get_generator = asyncio.ensure_future(self.simple_one_filtered_data(session,'/QyFixedAssets',
                                                                                    'Fixed_Asset_Type',"eq",
                                                                                    'Machinery'))
                
                task_get_drivers = asyncio.ensure_future(self.simple_fetch_data(session,'/QyDrivers'))

                response = await asyncio.gather(task_get_reservations,task_get_vendor,task_get_vehicle, task_get_drivers, task_get_generator)

                fuel_response = await asyncio.gather(task_get_reservations) 

                vendors = [x for x in response[1]] # type: ignore
                vehicle = [x for x in response[2]] # type: ignore 
                drivers = [x for x in response[3]] # type: ignore 
                generators = [x for x in response[4]] # type: ignore 

                if fuel_response[0]['status_code'] == 200: # type: ignore
                    openRequest = [x for x in fuel_response[0]['data'] if  x['Submitted'] == False ] # type: ignore
                    submitted = [x for x in fuel_response[0]['data'] if  x['Submitted'] == True ] # type: ignore
                
                
            
            ctx = {
               "full": full_name,
                "driver_role":driver_role,
                "TO_role":TO_role, 
                'openRequest':openRequest,
                'submitted': submitted,
                'vendors':vendors,
                'vehicles':vehicle,
                "drivers": drivers,
                'generators': generators,
                'userID':userID,
                'employeeNo': employeeNo,
            }
        except Exception as e:
            logging.exception(e)
            return redirect('fuel')
        return render(request,"fuel.html",ctx)
    
class FnFuelConsumptionVehicle(UserObjectMixins,View):
    def post(self,request):
        try:
            soap_headers = request.session['soap_headers']
            fuelNo = request.POST.get('fuelNo')
            myAction = request.POST.get('myAction')
            assetType = int(request.POST.get('assetType'))
            fuelCardType = int(request.POST.get('fuelCardType'))
            receiptNo = request.POST.get('receiptNo')
            vehicle = request.POST.get('vehicle')
            driver = request.POST.get('driver')
            fuelStation = request.POST.get('fuelStation')
            fuelType = int(request.POST.get('fuelType'))
            costPerLtr = float(request.POST.get('costPerLtr'))
            quantityInLtrs = float(request.POST.get('quantityInLtrs'))
            remarks = request.POST.get('remarks')
            currentOdometerReading = request.POST.get('currentOdometerReading')
            userID = request.session['User_ID']
            
            response = self.make_soap_request(soap_headers,
                                            'FnFuelConsumptionVehicle',
                                                fuelNo, myAction,assetType,
                                                    fuelCardType,receiptNo,vehicle,
                                                        driver,fuelStation,costPerLtr,
                                                        quantityInLtrs,remarks,fuelType,
                                                            currentOdometerReading,userID)
            if response !='0':
                messages.success(request,'success')
                return redirect('FuelDetails', pk=response)

            messages.error(request, f'{response}')
            return redirect('fuel')
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('fuel')
     
class FnFuelConsumptionGenerator(UserObjectMixins,View):
    def post(self,request):
        try:
            soap_headers = request.session['soap_headers']
            fuelNo = request.POST.get('fuelNo')
            myAction = request.POST.get('myAction')
            assetType = int(request.POST.get('assetType'))
            fuelCardType = int(request.POST.get('fuelCardType'))
            receiptNo = request.POST.get('receiptNo')
            generator = request.POST.get('generator')
            driver = request.POST.get('driver')
            currenthoursReadings = request.POST.get('currenthoursReadings')
            fuelType = int(request.POST.get('fuelType'))
            fuelStation = request.POST.get('fuelStation')
            costPerLtr = float(request.POST.get('costPerLtr'))
            quantityInLtrs = float(request.POST.get('quantityInLtrs'))
            remarks = request.POST.get('remarks')
            
            response = self.make_soap_request(soap_headers,
                                            'FnFuelConsumptionGenerator',
                                                fuelNo, myAction,assetType,
                                                    fuelCardType,receiptNo,generator,
                                                        driver,currenthoursReadings,fuelType,
                                                            fuelStation,costPerLtr,quantityInLtrs,remarks)
            if response !='0':
                messages.success(request,'success')
                return redirect('FuelDetails', pk=response)

            messages.error(request, f'{response}')
            return redirect('fuel')
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('fuel')
        
class FuelDetails(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role = await sync_to_async(request.session.__getitem__)('TO_role')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            res = {}
            ctx = {}

            async with aiohttp.ClientSession() as session:
                get_consumption = asyncio.ensure_future(self.simple_double_filtered_data(
                    session,"/QyFuelRegister","Code", 
                    "eq",pk,'and','Created_By','eq',userID))

                get_files = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                    '/QyDocumentAttachments','No_','eq',pk))
                response = await asyncio.gather(get_consumption,get_files)
                for data in response[0]:
                    res = data
                allFiles = [x for x in response[1]]  # type: ignore 

                ctx = {
                    "res":res,
                    "allFiles":allFiles,
                    "driver_role":driver_role,
                    'TO_role':TO_role,
                    'full':full_name,
                    
                }
        except Exception as e:
            print(e)
            messages.info(request, f'{e}')
            return redirect('fuel')
        return render(request,'fuelDetails.html',ctx)

class FnSubmitFuelConsumption(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            userID = request.session['User_ID']
            response = self.make_soap_request(soap_headers,'FnSubmitFuelConsumption',
                                              pk,userID)
            print(response)
            if response == True:
                messages.success(request,'Success')
                return redirect('FuelDetails', pk=pk)
            else:
                messages.error(request, f'{response}')
                return redirect('FuelDetails',pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            logging.exception(e)
            return redirect('FuelDetails', pk=pk)

#################################################
    #       Speed Governor
#################################################        

class SpeedGovernor(UserObjectMixins,View):
    async def get(self,request):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role = await sync_to_async(request.session.__getitem__)('TO_role')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            openRequest = []
            submitted = []

            full_name = request.session['full_name']
            
            async with aiohttp.ClientSession() as session:
                task_get_reservations = asyncio.ensure_future(self.simple_one_filtered_data(
                    session,"/QySpeedGovernorReplacement","Created_By","eq",userID))
                
                task_get_vendor = asyncio.ensure_future(self.simple_one_filtered_data(session,'/VendorDetails',
                                                                                    'Vendor_Type',"eq",
                                                                                    'Speed Governor'))
                task_get_vehicle = asyncio.ensure_future(self.simple_one_filtered_data(session,'/QyFixedAssets',
                                                                                    'Fixed_Asset_Type',"eq",
                                                                                    'Fleet'))
                
                

                response = await asyncio.gather(task_get_reservations,task_get_vendor,task_get_vehicle) 
                
                openRequest = [x for x in response[0] if x['DocumentStage'] == 'Not-Submitted' ] # type: ignore
                submitted = [x for x in response[0] if x['DocumentStage'] == 'Submitted'] #type:ignore
                
                vendors = [x for x in response[1]] # type: ignore
                vehicle = [x for x in response[2]] # type: ignore 

            ctx = {
               "full": full_name,
                "driver_role":driver_role,
                "TO_role":TO_role, 
                'vendors':vendors,
                'vehicles':vehicle,
                'openRequest':openRequest,
                'submitted':submitted,
            }
        except Exception as e:
            logging.exception(e)
            return redirect('fuel')
        return render(request,"speedGovernor.html",ctx)
    
    async def post(self,request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            speedGNo = request.POST.get('speedGNo')
            vehicle = request.POST.get('vehicle')
            fittedVendor = request.POST.get('fittedVendor')
            speed_governor_make = request.POST.get('speed_governor_make')
            serial_number = request.POST.get('serial_number')
            speed_governor_expiry_date = datetime.strptime(request.POST.get('speed_governor_expiry_date'),'%Y-%m-%d').date()
            remarks = request.POST.get('remarks')
            certified_by = request.POST.get('certified_by')
            date_of_installation_inspection = datetime.strptime(request.POST.get('date_of_installation_inspection'),'%Y-%m-%d').date()
            trackID = request.POST.get('trackID')
            myAction = request.POST.get('myAction')
            userID = await sync_to_async(request.session.__getitem__)('User_ID')          
            
            response =self.make_soap_request(soap_headers,
                                             'FnSpeedGovernor',
                                                speedGNo,vehicle,fittedVendor,
                                                    speed_governor_make,serial_number,speed_governor_expiry_date,
                                                        remarks,certified_by,date_of_installation_inspection,
                                                            trackID,myAction,userID)
            if response !='0':
                messages.success(request,'success')
                return redirect('GovernorDetails',pk=response)
            elif response == 0:
                messages.error(request, f'{response}')
                return redirect('GovernorDetails',pk=response)
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('SpeedGovernor')
        
class GovernorDetails(UserObjectMixins,View):
    async def get(self,request,pk):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role = await sync_to_async(request.session.__getitem__)('TO_role')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            res = {}
            ctx = {}

            async with aiohttp.ClientSession() as session:
                get_speed_governor = asyncio.ensure_future(self.simple_double_filtered_data(session,
                                            '/QySpeedGovernorReplacement','SpeedGovernorNo',
                                            'eq',pk,'and','Created_By','eq',userID))
                get_files = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                    '/QyDocumentAttachments','No_','eq',pk))
                response = await asyncio.gather(get_speed_governor,get_files)
                for data in response[0]:
                    res = data
                allFiles = [x for x in response[1]]  # type: ignore 
                print(allFiles)

                ctx = {
                   "res":res,
                    "allFiles":allFiles,
                    "driver_role":driver_role,
                    'TO_role':TO_role,
                    'full':full_name,
                }

        except Exception as e:
            print(e)
            messages.info(request, f'{e}')
            return redirect('SpeedGovernor')
        return render(request,'governorDetails.html',ctx)

class FnSubmitSpeedGovernor(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            userID = request.session['User_ID']
            response = self.make_soap_request(soap_headers,'FnSubmitSpeedGovernor',
                                              pk,userID)
            print(response)
            if response == True:
                messages.success(request,'Success')
                return redirect('SpeedGovernor')
            else:
                messages.error(request, f'{response}')
                return redirect('GovernorDetails',pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            logging.exception(e)
            return redirect('GovernorDetails',pk=pk)


class UploadSpeedGovernorAttachment(UserObjectMixin, View):
    def post(self, request, pk):
        response = ''
        if request.method == "POST":
            try:
                attach = request.FILES.getlist('attachment')
                tableID = 50024 #52177430

                for files in attach:

                    fileName = request.FILES['attachment'].name
                    attachment = base64.b64encode(files.read())
                    
                    response = config.CLIENT.service.FnUploadAttachedDocument(
                        pk, fileName, attachment, tableID,
                        request.session['User_ID'])
                    
                    if response == True:
                        messages.success(request, "File(s) Upload Successful")
                        return redirect('GovernorDetails', pk=pk)
                    
                    else:
                        messages.error(request, "Failed, Try Again")
                        return redirect('GovernorDetails', pk=pk)
                    
            except Exception as e:
                messages.error(request, "Oooops!!! something went Wrong!!!")
                print(e)

        return redirect('GovernorDetails', pk=pk)

class DeleteSpeedGovernor(UserObjectMixin, View):
    def post(self, request, pk):
        if request.method == "POST":
            docID = int(request.POST.get('docID'))
            tableID = int(request.POST.get('tableID'))
            try:
                response = config.CLIENT.service.FnDeleteDocumentAttachment(
                    pk, docID, tableID)
                print(response)
                if response == True:
                    messages.success(request, "Deleted Successfully ")
                    return redirect('GovernorDetails', pk=pk)
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
        return redirect('GovernorDetails', pk=pk)

#################################################
    #       GVCU
#################################################
            
class GVCU(UserObjectMixins,View):
    async def get(self,request):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role = await sync_to_async(request.session.__getitem__)('TO_role')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')

            full_name = request.session['full_name']
            drivers = []
            
            async with aiohttp.ClientSession() as session:
                task_get_reservations = asyncio.ensure_future(self.simple_one_filtered_data(
                    session,"/QyGovermentCheckUnit","Created_By","eq",userID))
                
                task_get_vehicle = asyncio.ensure_future(self.simple_one_filtered_data(session,'/QyFixedAssets',
                                                                                    'Fixed_Asset_Type',"eq",
                                                                                    'Fleet'))
                task_get_driver = asyncio.ensure_future(self.simple_fetch_data(session,'/QyDrivers'))

                response = await asyncio.gather(task_get_reservations,task_get_vehicle,
                                                task_get_driver) 
                               
                openRequest = [x for x in response[0] if x['Submitted'] == False ] # type: ignore
                submitted = [x for x in response[0] if x['Submitted'] == True] #type:ignore
                vehicle = [x for x in response[1]] # type: ignore 
                drivers = [x for x in response[2]] # type: ignore 
                   
            ctx = {
               "full": full_name,
                "driver_role":driver_role,
                "TO_role":TO_role, 
                'openRequest':openRequest,
                'submitted':submitted,
                'vehicles':vehicle,
                'drivers':drivers,
                
            }
        except Exception as e:
            logging.exception(e)
            print(e)
            return redirect('gvcu')
        return render(request,"gvcu.html",ctx)
    
    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            gcuNo = request.POST.get('gcuNo')
            date =  datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            vehicle = request.POST.get('vehicle')
            driver = request.POST.get('driver')
            natureOfIrregularity = request.POST.get('natureOfIrregularity')
            surcharge = float(request.POST.get('surcharge'))
            locationOfTheVehicle  = request.POST.get('locationOfTheVehicle')
            myAction = request.POST.get('myAction')
            user_id = await sync_to_async(request.session.__getitem__)('User_ID')
            response = self.make_soap_request(soap_headers,'FnGovermentCheckUnit',
                                              gcuNo,date,vehicle,driver,natureOfIrregularity,
                                                    surcharge,locationOfTheVehicle,myAction,
                                                        user_id)
            if response != '0':
                messages.success(request,'success')
                return redirect('gvcuDetails',pk=response)
            else:
                messages.error(request,f'{response}')
                return redirect('gvcu')
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('gvcu')       
class GVCU_Details(UserObjectMixins,View):
    async def get(self,request,pk):
        try:
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role = await sync_to_async(request.session.__getitem__)('TO_role')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            res = {}
            ctx = {}

            async with aiohttp.ClientSession() as session:
                get_speed_governor = asyncio.ensure_future(self.simple_double_filtered_data(session,
                                            '/QyGovermentCheckUnit','GCU_No',
                                            'eq',pk,'and','Created_By','eq',userID))
                get_files = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                    '/QyDocumentAttachments','No_','eq',pk))
                
                get_employees = asyncio.ensure_future(self.simple_fetch_data(session, '/QYEmployees'))

                get_travel_employees = asyncio.ensure_future(self.simple_one_filtered_data(session, '/QyTravelEmployee', 'RequestNo', 'eq', pk))

                response = await asyncio.gather(get_speed_governor,get_files, get_employees, get_travel_employees)
                for data in response[0]:
                    res = data
                    
                allFiles = [x for x in response[1]]  # type: ignore 
                employees = [x for x in response[2]]
                travelEmployees = [x for x in response[3]]
                
                ctx = {
                    "res":res,
                    "allFiles":allFiles,
                    "driver_role":driver_role,
                    'TO_role':TO_role,
                    'full':full_name,
                    'employees': employees,
                    'travelEmployees': travelEmployees,
                }

        except Exception as e:
            print(e)
            messages.info(request, f'{e}')
            return redirect('gvcuDetails')
        return render(request,'gvcuDetails.html',ctx)
    
class FnSubmitGovermmentCheckUnit(UserObjectMixins, View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            userID = request.session['User_ID']
            response = self.make_soap_request(soap_headers,'FnSubmitGovermmentCheckUnit',
                                              pk,userID)
            print(response)
            if response == True:
                messages.success(request,'Success')
                return redirect('gvcuDetails', pk=pk)
            else:
                messages.error(request, f'{response}')
                return redirect('gvcuDetails',pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            logging.exception(e)
            return redirect('gvcuDetails', pk=pk)


class UploadGVCUAttachment(UserObjectMixin, View):
    def post(self, request, pk):
        response = ''
        if request.method == "POST":
            try:
                attach = request.FILES.getlist('attachment')
                tableID = 50033 #52177430

                for files in attach:

                    fileName = request.FILES['attachment'].name
                    attachment = base64.b64encode(files.read())
                    
                    response = config.CLIENT.service.FnUploadAttachedDocument(
                        pk, fileName, attachment, tableID,
                        request.session['User_ID'])
                    
                    if response == True:
                        messages.success(request, "File(s) Upload Successful")
                        return redirect('gvcuDetails', pk=pk)
                    
                    else:
                        messages.error(request, "Failed, Try Again")
                        return redirect('gvcuDetails', pk=pk)
                    
            except Exception as e:
                messages.error(request, "Oooops!!! something went Wrong!!!")
                print(e)

        return redirect('gvcuDetails', pk=pk)


class DeleteGVCUAttachment(UserObjectMixin, View):
    def post(self, request, pk):
        if request.method == "POST":
            docID = int(request.POST.get('docID'))
            tableID = int(request.POST.get('tableID'))
            try:
                response = config.CLIENT.service.FnDeleteDocumentAttachment(
                    pk, docID, tableID)
                print(response)
                if response == True:
                    messages.success(request, "Deleted Successfully ")
                    return redirect('gvcuDetails', pk=pk)
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
        return redirect('gvcuDetails', pk=pk)


class FnGVCUPassangers(UserObjectMixins,View):
    async def post(self, request, pk):
        if request.method == 'POST':
            try:
                userID = await sync_to_async(request.session.__getitem__)('User_ID')
                reqNo= pk
                employeeNo= request.POST.get('employeeNo')
                lineNo= request.POST.get('lineNo')
                myAction= request.POST.get('myAction')
                soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
                response =  self.make_soap_request(soap_headers,'FnGVCUPassangers', reqNo ,userID, employeeNo,lineNo,myAction)
                
                print(response)

                if response == True:
                    messages.success(request, 'Request Submitted successfully')
                    return redirect('gvcuDetails', pk=pk)
                if response == False:
                    messages.success(request, 'Request Failed')
                    return redirect('gvcuDetails', pk=pk)
            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
                print(e)
                messages.error(request,"connect timed out")
                return redirect('gvcuDetails', pk=pk)
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            except Exception as e:
                messages.error(request, "OOps!! Something went wrong")
                print(e)
                return redirect('gvcuDetails', pk=pk)
        return redirect('gvcuDetails', pk=pk)