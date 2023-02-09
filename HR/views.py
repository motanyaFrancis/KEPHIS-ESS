import base64
import logging
import aiohttp
from django.shortcuts import render, redirect
from datetime import datetime
from asgiref.sync import sync_to_async
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
from myRequest .views import UserObjectMixins
import asyncio

class UserObjectMixin(object):
    model = None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


class Leave_Request(UserObjectMixins, View):
    async def get(self, request):
        try:
            UserId = await sync_to_async(request.session.__getitem__)('User_ID')
            department = await sync_to_async(request.session.__getitem__)('User_Responsibility_Center')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role =await sync_to_async(request.session.__getitem__)('TO_role')
            mechanical_inspector_role =await sync_to_async(request.session.__getitem__)('mechanical_inspector_role')
            
            async with aiohttp.ClientSession() as session:
                task_get_leave = asyncio.ensure_future(self.fetch_one_filtered_data(session,"/QyLeaveApplications",
                                                                                    "User_ID","eq",UserId))
                task_get_leave_types = asyncio.ensure_future(self.simple_fetch_data(session,"/QyLeaveTypes"))
                
                task_get_reliever = asyncio.ensure_future(self.fetch_one_filtered_data(session,"/QYEmployees",
                                                                                       "Global_Dimension_1_Code","eq",
                                                                                       department))
  
                                
                response  = await asyncio.gather(task_get_leave,task_get_leave_types,task_get_reliever)
                
                openLeave = [x for x in response[0]['data'] if x['Status'] == 'Open']  # type: ignore
                pendingLeave = [x for x in response[0]['data'] if x['Status'] == 'Pending Approval'] # type: ignore
                approvedLeave = [x for x in response[0]['data'] if x['Status'] == 'Released'] # type: ignore
                Leave = [x for x in response[1]] # type: ignore
                relievers = [x for x in response[2]['data']] # type: ignore

        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, "connection refused,non-200 response")
            print(e)
            return redirect('dashboard')
        ctx = {"today": self.todays_date, 
               "res": openLeave,
               "response": approvedLeave,
               'leave': Leave,
               "pending": pendingLeave,
               'relievers':relievers,
               "full": full_name,
               "driver_role":driver_role,
               "TO_role":TO_role,
               "mechanical_inspector_role":mechanical_inspector_role,
               }
        return render(request, 'leave.html', ctx)

    async def post(self, request):
        try:
            Employee_No_ = await sync_to_async(request.session.__getitem__)('Employee_No_')
            usersId = await sync_to_async(request.session.__getitem__)('User_ID')
            applicationNo = request.POST.get('applicationNo')
            leaveType = request.POST.get('leaveType')
            plannerStartDate = request.POST.get('plannerStartDate')
            daysApplied = request.POST.get('daysApplied')
            isReturnSameDay = eval(request.POST.get('isReturnSameDay'))
            myAction = request.POST.get('myAction')
            staffNo = request.POST.get('reliever')
            if not daysApplied:
                daysApplied = 0
            plannerStartDate = datetime.strptime(
                plannerStartDate, '%Y-%m-%d').date()
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
        
            response =  self.make_soap_request(soap_headers,'FnLeaveApplication',
                                                   applicationNo,Employee_No_,usersId,leaveType,
                                                   plannerStartDate,daysApplied,isReturnSameDay,myAction)
            if response !='0':
                add_reliever = self.make_soap_request(soap_headers,"FnLeaveReliver",
                                                      response,staffNo,myAction)
                print("reliever response:",add_reliever)
                if add_reliever == True:
                    messages.success(request, "Request Successful")
                    return redirect('LeaveDetail', pk=response)
                if add_reliever == False:
                    messages.info(request, f"Leave reliever not added. Add it on the leave :{response} details section")
                    return redirect('LeaveDetail', pk=response)
            if response == '0':
                messages.error(request,"Not Added")
                return redirect('leave')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('leave')
        return redirect('leave')


class LeaveDetail(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userId = request.session['User_ID']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['User_Responsibility_Center']
            full_name = request.session['full_name']
            res ={}

            Access_Point = config.O_DATA.format(
                f"/QyLeaveApplications?$filter=User_ID%20eq%20%27{userId}%27%20and%20Application_No%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for leave in response['value']:
                res = leave
            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            Access_File = config.O_DATA.format(
                f"/QyDocumentAttachments?$filter=No_%20eq%20%27{pk}%27")
            res_file = self.get_object(Access_File)
            allFiles = [x for x in res_file['value']]

            RejectComments = config.O_DATA.format(
                f"/QyApprovalCommentLines?$filter=Document_No_%20eq%20%27{pk}%27")
            RejectedResponse = self.get_object(RejectComments)
            Comments = [x for x in RejectedResponse['value']]
            
            leave_reliever = config.O_DATA.format(
                f"/QyLeaveRelivers?$filter=LeaveCode%20eq%20%27{pk}%27")
            reliever_response = self.get_object(leave_reliever)
            relievers = [x for x in reliever_response['value']]
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request, "500 Server Error, Try Again")
            return redirect('leave')

        ctx = {"today": self.todays_date, "res": res,
               "Approvers": Approvers,
               "relievers":relievers,
               "full": full_name,
               "file": allFiles,
               "Comments": Comments,
               "full": full_name,
               "driver_role":driver_role,
               "TO_role":TO_role,
               "mechanical_inspector_role":mechanical_inspector_role,
               }
        return render(request, 'leaveDetail.html', ctx)

    def post(self, request, pk):
        try:
            attachments = request.FILES.getlist('attachment')
            tableID = 52177494
            attachment_names = []
            response = False

            for file in attachments:
                fileName = file.name
                attachment_names.append(fileName)
                attachment = base64.b64encode(file.read())

                response = config.CLIENT.service.FnUploadAttachedDocument(
                        pk, fileName, attachment, tableID, request.session['User_ID'])
                
            if response is not None:
                if response == True:
                    messages.success(request, "Uploaded {} attachments successfully".format(len(attachments)))
                    return redirect('LeaveDetail', pk=pk)
                messages.error(request, "Upload failed: {}".format(response))
                return redirect('LeaveDetail', pk=pk)
            messages.error(request, "Upload failed: Response from server was None")
            return redirect('LeaveDetail', pk=pk)
        except Exception as e:
            messages.error(request, "Upload failed: {}".format(e))
            logging.exception(e)
            return redirect('LeaveDetail', pk=pk)

def DeleteLeaveAttachment(request, pk):
    if request.method == "POST":
        docID = int(request.POST.get('docID'))
        tableID = int(request.POST.get('tableID'))
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                pk, docID, tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('LeaveDetail', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
    return redirect('LeaveDetail', pk=pk)


def LeaveApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = CLIENT.service.FnRequestLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, f'{e}')
        print(e)
    return redirect('LeaveDetail', pk=pk)


def LeaveCancelApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Cancel Approval Request Successful !!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, f'{e}')
        print(e)
    return redirect('LeaveDetail', pk=pk)


class Training_Request(UserObjectMixins, View):
    def get(self, request):
        try:
            empNo = request.session['Employee_No_']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['User_Responsibility_Center']
            full_name = request.session['full_name']

            Access_Point = config.O_DATA.format(
                f"/QyTrainingRequests?$filter=Employee_No%20eq%20%27{empNo}%27")
            response = self.get_object(Access_Point)
            openTraining = [x for x in response['value']
                            if x['Status'] == 'Open']
            pendingTraining = [x for x in response['value']
                               if x['Status'] == 'Pending Approval']
            approvedTraining = [x for x in response['value']
                                if x['Status'] == 'Released']

            trainingNeed = config.O_DATA.format("/QyTrainingNeeds")
            res_train = self.get_object(trainingNeed)
            trains = [x for x in res_train['value']]

            counts = len(openTraining)
            counter = len(approvedTraining)
            pend = len(pendingTraining)

        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request, "500 Server Error")
            return redirect('dashboard')

        ctx = {"today": self.todays_date, "res": openTraining,
               "count": counts, "response": approvedTraining,
               "counter": counter,
               "train": trains,
               "pend": pend, "pending": pendingTraining,
               "full": full_name,
               "full": full_name,
               "driver_role":driver_role,
               "TO_role":TO_role,
               "mechanical_inspector_role":mechanical_inspector_role,}
        return render(request, 'training.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                soap_headers = request.session['soap_headers']
                requestNo = request.POST.get('requestNo')
                employeeNo = request.session['Employee_No_']
                usersId = request.session['User_ID']
                isAdhoc = eval(request.POST.get('isAdhoc'))
                sponsorType = request.POST.get('sponsorType')
                trainingNeed = request.POST.get('trainingNeed')
                myAction = request.POST.get('myAction')

                if not trainingNeed:
                    trainingNeed = ''

                response = self.make_soap_request(soap_headers,"FnTrainingRequest",
                    requestNo, employeeNo, usersId, isAdhoc, sponsorType , trainingNeed, myAction)
                if response == True:
                    messages.success(request, "success")
                    return redirect('training_request')
                elif response == False:
                    messages.error(request, "failed")
                    return redirect('training_request')
                else:
                    messages.error(request, f'{response}')
                    return redirect('training_request')
            except Exception as e:
                messages.error(request, f'{e}')
                logging.exception(e)
                return redirect('training_request')
        return redirect('training_request')


class TrainingDetail(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            empNo = request.session['Employee_No_']
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['User_Responsibility_Center']
            full_name = request.session['full_name']
            res ={}

            Access_Point = config.O_DATA.format(
                f"/QyTrainingRequests?$filter=Employee_No%20eq%20%27{empNo}%27%20and%20Request_No_%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for training in response['value']:
                res = training

            Approver = config.O_DATA.format(
                f"/QyApprovalEntries?$filter=Document_No_%20eq%20%27{pk}%27")
            res_approver = self.get_object(Approver)
            Approvers = [x for x in res_approver['value']]

            destination = config.O_DATA.format("/QyDestinations")
            res_destination = self.get_object(destination)
            Local = [x for x in res_destination['value']
                     if x['Destination_Type'] == 'Local']
            Foreign = [x for x in res_destination['value']
                       if x['Destination_Type'] == 'Foreign']

            RejectComments = config.O_DATA.format(
                f"/QyApprovalCommentLines?$filter=Document_No_%20eq%20%27{pk}%27")
            RejectedResponse = self.get_object(RejectComments)
            Comments = [x for x in RejectedResponse['value']]

            Lines_Res = config.O_DATA.format(
                f"/QyTrainingNeedsRequest?$filter=Source_Document_No%20eq%20%27{pk}%27%20and%20Employee_No%20eq%20%27{empNo}%27")
            responseNeeds = self.get_object(Lines_Res)
            openLines = [x for x in responseNeeds['value']]

        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request, "500 Server Error, Try Again in a few")
            return redirect('training_request')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('training_request')

        ctx = {"today": self.todays_date, "res": res,
               "Approvers": Approvers,"line": openLines,
               "local": Local, "foreign": Foreign, "Comments": Comments,
               "full": full_name,
               "driver_role":driver_role,
               "TO_role":TO_role,
               "mechanical_inspector_role":mechanical_inspector_role,
               }
        return render(request, 'trainingDetail.html', ctx)

    def post(self, request, pk):
        if request.method == 'POST':
            try:
                requestNo = pk
                no = ""
                employeeNo = request.session['Employee_No_']
                myAction = "insert"
                trainingName = request.POST.get('trainingName')
                startDate = request.POST.get('startDate')
                endDate = request.POST.get('endDate')
                trainingArea = request.POST.get('trainingArea')
                trainingObjectives = request.POST.get('trainingObjectives')
                venue = request.POST.get('venue')
                sponsor = request.POST.get('sponsor')
                destination = request.POST.get('destination')
                OtherDestinationName = request.POST.get('OtherDestinationName')
                provider = request.POST.get('provider')

            except ValueError as e:
                messages.error(request, "Invalid Input, Try Again!!")
                return redirect('TrainingDetail', pk=pk)
            if not sponsor:
                sponsor = 0
            sponsor = int(sponsor)

            if not destination:
                destination = 'none'

            if not venue:
                venue = "Online"

            if OtherDestinationName:
                destination = OtherDestinationName
            try:
                response = config.CLIENT.service.FnAdhocTrainingNeedRequest(requestNo,
                                                                            no, employeeNo, trainingName, trainingArea, trainingObjectives, venue, provider, myAction, sponsor, startDate, endDate, destination)
                messages.success(request, "Successfully Added!!")
                print(response)
                return redirect('TrainingDetail', pk=pk)
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
        return redirect('TrainingDetail', pk=pk)


def UploadTrainingAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177501

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID, request.session['User_ID'])
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('TrainingDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('TrainingDetail', pk=pk)

    return redirect('TrainingDetail', pk=pk)


def FnAdhocTrainingEdit(request, pk, no):
    requestNo = pk
    no = no
    employeeNo = request.session['Employee_No_']
    trainingName = ""
    trainingArea = ""
    trainingObjectives = ""
    venue = ""
    provider = ""
    myAction = "modify"

    if request.method == 'POST':
        try:
            trainingName = request.POST.get('trainingName')
            trainingArea = request.POST.get('trainingArea')
            trainingObjectives = request.POST.get('trainingObjectives')
            venue = request.POST.get('venue')
            provider = request.POST.get('provider')

        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnAdhocTrainingNeedRequest(requestNo,
                                                                    no, employeeNo, trainingName, trainingArea, trainingObjectives, venue, provider, myAction)
        messages.success(request, "Successfully Edited!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, f'{e}')
        print(e)
    return redirect('TrainingDetail', pk=pk)


def FnAdhocLineDelete(request, pk):
    requestNo = pk
    needNo = ''
    if request.method == 'POST':
        try:
            needNo = request.POST.get('needNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
        print("requestNo", requestNo)
        print("needno", needNo)
        try:
            response = config.CLIENT.service.FnDeleteAdhocTrainingNeedRequest(
                needNo, requestNo)
            messages.success(request, "Successfully Deleted!!")
            print(response)
            return redirect('TrainingDetail', pk=pk)
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
    return redirect('TrainingDetail', pk=pk)


class TrainingApproval(UserObjectMixins, View):
    async def post(self,request,pk):
        try:
            trainingNo = request.POST.get('trainingNo')
            userID = await sync_to_async(request.session.__getitem__)('User_ID')
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            response =  self.make_soap_request(soap_headers,'FnRequestTrainingApproval',userID,trainingNo)
            if response == True:
                messages.success(request, 'Request Submitted successfully')
                return redirect('TrainingDetail', pk=pk)
            if response == False:
                messages.success(request, 'Request Failed')
                return redirect('TrainingDetail', pk=pk)
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"connect timed out")
            return redirect('TrainingDetail', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
        return redirect('TrainingDetail', pk=pk)


def TrainingCancelApproval(request, pk):
    myUserID = request.session['User_ID']
    trainingNo = ""
    if request.method == 'POST':
        try:
            trainingNo = request.POST.get('trainingNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelTrainingApproval(
            myUserID, trainingNo)
        messages.success(request, "Cancel Approval Request Successful !!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, f'{e}')
        print(e)
    return redirect('TrainingDetail', pk=pk)


class PNineRequest(UserObjectMixin, View):
    def get(self, request):
        try:
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['User_Responsibility_Center']
            full_name = request.session['full_name']

            Access_Point = config.O_DATA.format("/QyPayrollPeriods")
            response = self.get_object(Access_Point)
            res = response['value']

        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('pNine')
        ctx = {"today": self.todays_date,
               "full": full_name, "res": res,
               "driver_role":driver_role,
               "TO_role":TO_role,
               "mechanical_inspector_role":mechanical_inspector_role}
        return render(request, "p9.html", ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                                    for i in range(5))
                employeeNo = request.session['Employee_No_']
                startDate = request.POST.get('startDate')[0:4]
            except ValueError as e:
                messages.error(request, "Not sent. Invalid Input, Try Again!!")
                return redirect('pNine')
            filenameFromApp = "P9_For_" + str(nameChars) + ".pdf"
            year = int(startDate)
            try:
                response = config.CLIENT.service.FnGeneratePNine(
                    employeeNo, filenameFromApp, year)
                try:
                    buffer = BytesIO.BytesIO()
                    content = base64.b64decode(response)
                    buffer.write(content)
                    responses = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/pdf",
                    )
                    responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
                    return responses
                except:
                    messages.error(
                        request, "Payslip not found for the selected period")
                    return redirect('pNine')
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)
                return redirect('pNine')


class PayslipRequest(UserObjectMixin, View):
    def get(self, request):
        try:
            driver_role = request.session['driver_role']
            TO_role = request.session['TO_role']
            mechanical_inspector_role = request.session['User_Responsibility_Center']
            full_name = request.session['full_name']

            Access_Point = config.O_DATA.format(
                f"/QyPayrollPeriods?$filter=Closed%20eq%20true")
            response = self.get_object(Access_Point)
            Payslip = [x for x in response['value']]

        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('payslip')

        ctx = {"today": self.todays_date, 
               "full": full_name, "res": Payslip,
               "driver_role":driver_role,
               "TO_role":TO_role,
               "mechanical_inspector_role":mechanical_inspector_role,}

        return render(request, "payslip.html", ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                employeeNo = request.session['Employee_No_']
                nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                                    for i in range(5))

                paymentPeriod = datetime.strptime(
                    request.POST.get('paymentPeriod'), '%Y-%m-%d').date()

            except ValueError as e:
                messages.error(request, "Not sent. Invalid Input, Try Again!!")
                return redirect('payslip')
            filenameFromApp = "Payslip" + \
                str(paymentPeriod) + str(nameChars) + ".pdf"
            try:
                response = config.CLIENT.service.FnGeneratePayslip(
                    employeeNo, filenameFromApp, paymentPeriod)
                try:
                    buffer = BytesIO.BytesIO()
                    content = base64.b64decode(response)
                    buffer.write(content)
                    responses = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/pdf",
                    )
                    responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
                    return responses
                except:
                    messages.error(
                        request, "Payslip not found for the selected period")
                    return redirect('payslip')
            except Exception as e:
                messages.error(request, f'{e}')
                print(e)


def FnGenerateLeaveReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ''
    applicationNo = pk
    if request.method == 'POST':
        try:
            filenameFromApp = pk
        except ValueError as e:
            messages.error(request, "Invalid Line number, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
        filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
        print("filenameFromApp", filenameFromApp)
        print("applicationNo", applicationNo)
        try:
            response = config.CLIENT.service.FnGenerateLeaveReport(
                employeeNo, filenameFromApp, applicationNo)
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
            messages.error(request, f'{e}')
            print(e)
    return redirect('LeaveDetail', pk=pk)
# Training report


def FnGenerateTrainingReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ''
    applicationNo = pk
    if request.method == 'POST':
        try:
            filenameFromApp = pk
        except ValueError as e:
            messages.error(request, "Invalid Line number, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateTrainingReport(
            employeeNo, filenameFromApp, applicationNo)
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
        messages.error(request, f'{e}')
        print(e)
    return redirect('TrainingDetail', pk=pk)


def Disciplinary(request):
    fullname = request.session['User_ID']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyEmployeeDisciplinaryCases")
    openCase =[]
    counts = 0
    try:
        response = session.get(Access_Point, timeout=10).json()
        for case in response['value']:
            if case['Employee_No'] == request.session['Employee_No_'] and case['Posted'] == False and case['Sent_to_employee'] == True and case['Submit'] == False:
                output_json = json.dumps(case)
                openCase.append(json.loads(output_json))
        counts = len(openCase)
        print(counts)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": openCase,
            "full": fullname,
           "count": counts}
    return render(request, 'disciplinary.html', ctx)


def DisciplineDetail(request, pk):
    fullname = request.session['User_ID']
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    openLines = []
    Access_Point = config.O_DATA.format("/QyEmployeeDisciplinaryCases")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Case = []
        for case in response['value']:
            if case['Employee_No'] == request.session['Employee_No_'] and case['Posted'] == False and case['Sent_to_employee'] == True and case['Submit'] == False:
                output_json = json.dumps(case)
                Case.append(json.loads(output_json))
                for case in Case:
                    if case['Disciplinary_Nos'] == pk:
                        res = case
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyEmployeeDisciplinaryLines")
    try:
        responses = session.get(Lines_Res, timeout=10).json()
        for cases in responses['value']:
            if cases['Refference_No'] == pk and cases['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(cases)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "full": fullname,"line": openLines}
    return render(request, 'disciplineDetail.html', ctx)


def DisciplinaryResponse(request, pk):

    employeeNo = request.session['Employee_No_']
    caseNo = pk
    myResponse = ''

    if request.method == 'POST':
        try:
            myResponse = request.POST.get('myResponse')
        except ValueError as e:
            messages.error(request, "Invalid, Try Again!!")
            return redirect('DisciplineDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnEmployeeDisciplinaryResponse(
            employeeNo, caseNo, myResponse)
        messages.success(request, "Response Successful Sent!!")
        print(response)
        return redirect('DisciplineDetail', pk=pk)
    except Exception as e:
        messages.error(request, f'{e}')
        print(e)
    return redirect('DisciplineDetail', pk=pk)


