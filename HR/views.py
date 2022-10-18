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
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


class Leave_Planner(UserObjectMixin, View):
    def get(self, request):
        try:
            userId = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyLeavePlannerHeaders?$filter=Employee_No_%20eq%20%27{empNo}%27")
            response = self.get_object(Access_Point)
            Plans = [x for x in response['value']]
        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            print(e)
            return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            print(e)
        ctx = {"today": self.todays_date, "res": Plans,
               "year": year, "full": userId}
        return render(request, 'planner.html', ctx)

    def post(self, request):
        plannerNo = ""
        empNo = request.session['Employee_No_']
        myAction = request.POST.get('myAction')
        try:
            response = config.CLIENT.service.FnLeavePlannerHeader(
                plannerNo, empNo, myAction)
            if response == True:
                messages.success(request, "Request Successful")
                print(response)
                return redirect('LeavePlanner')
        except Exception as e:
            messages.error(request, e)
            print(e)
        return redirect('LeavePlanner')


class PlanDetail(UserObjectMixin, View):
    def get(self, request, pk):
        fullname = request.session['User_ID']
        year = request.session['years']
        empNo = request.session['Employee_No_']

        try:
            Access_Point = config.O_DATA.format(
                f"/QyLeavePlannerHeaders?$filter=Employee_No_%20eq%20%27{empNo}%27%20and%20No_%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for plan in response['value']:
                res = plan
            Lines_Res = config.O_DATA.format(
                f"/QyLeavePlannerLines?$filter=Employee_No_%20eq%20%27{empNo}%27%20and%20Document_No_%20eq%20%27{pk}%27")
            LinesRes = self.get_object(Lines_Res)
            openLines = [x for x in LinesRes['value']
                         if x['Document_No_'] == pk]

        except requests.exceptions.ConnectionError as e:
            print(e)
        ctx = {"today": self.todays_date,
               "year": year, "full": fullname,
               "line": openLines, "res": res}
        return render(request, 'planDetails.html', ctx)

    def post(self, request, pk):
        try:
            plannerNo = pk
            lineNo = int(request.POST.get('lineNo'))
            startDate = datetime.strptime(
                (request.POST.get('startDate')), '%Y-%m-%d').date()
            endDate = datetime.strptime(
                (request.POST.get('endDate')), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')

            response = config.CLIENT.service.FnLeavePlannerLine(
                lineNo, plannerNo, startDate, endDate, myAction)

            if response == True:
                messages.success(request, "Request Successful")
                print(response)
                return redirect('PlanDetail', pk=pk)
        except ValueError as e:
            messages.error(request, "Missing Input")
            return redirect('PlanDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
        return redirect('PlanDetail', pk=pk)


def FnDeleteLeavePlannerLine(request, pk):
    if request.method == 'POST':
        lineNo = int(request.POST.get('lineNo'))
        try:
            response = config.CLIENT.service.FnDeleteLeavePlannerLine(
                pk, lineNo)
            if response == True:
                messages.success(request, "Successfully  Deleted!!")
                print(response)
                return redirect('PlanDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('PlanDetail', pk=pk)


class Leave_Request(UserObjectMixin, View):
    def get(self, request):
        try:
            UserId = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

            Access_Point = config.O_DATA.format(
                f"/QyLeaveApplications?$filter=User_ID%20eq%20%27{UserId}%27")
            response = self.get_object(Access_Point)
            openLeave = [x for x in response['value'] if x['Status'] == 'Open']
            pendingLeave = [x for x in response['value']
                            if x['Status'] == 'Pending Approval']
            approvedLeave = [x for x in response['value']
                             if x['Status'] == 'Released']

            LeaveTypes = config.O_DATA.format("/QyLeaveTypes")
            res_types = self.get_object(LeaveTypes)
            Leave = [x for x in res_types['value']]

            LeavePlanner = config.O_DATA.format(
                f"/QyLeavePlannerLines?$filter=Employee_No_%20eq%20%27{empNo}%27")
            res_planner = self.get_object(LeavePlanner)
            Plan = [x for x in res_planner['value']]

            counts = len(openLeave)
            pend = len(pendingLeave)
            counter = len(approvedLeave)

        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            print(e)

        ctx = {"today": self.todays_date, "res": openLeave,
               "count": counts, "response": approvedLeave,
               "counter": counter, 'leave': Leave,
               "plan": Plan, "pend": pend,
               "pending": pendingLeave, "year": year,
               "full": UserId}
        return render(request, 'leave.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            dimension3 = ''
            employeeNo = request.session['Employee_No_']
            usersId = request.session['User_ID']
            applicationNo = request.POST.get('applicationNo')
            leaveType = request.POST.get('leaveType')
            plannerStartDate = request.POST.get('plannerStartDate')
            daysApplied = request.POST.get('daysApplied')
            isReturnSameDay = eval(request.POST.get('isReturnSameDay'))
            myAction = request.POST.get('myAction')
            if not daysApplied:
                daysApplied = 0
            plannerStartDate = datetime.strptime(
                plannerStartDate, '%Y-%m-%d').date()
            try:
                response = config.CLIENT.service.FnLeaveApplication(
                    applicationNo, employeeNo, usersId, dimension3, leaveType, plannerStartDate, int(daysApplied), isReturnSameDay, myAction)
                messages.success(request, "Request Successful")
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
        return redirect('leave')


class LeaveDetail(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userId = request.session['User_ID']
            year = request.session['years']

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
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request, "500 Server Error, Try Again")
            return redirect('leave')

        ctx = {"today": self.todays_date, "res": res,
               "Approvers": Approvers, "year": year,
               "full": userId, "file": allFiles, "Comments": Comments}
        return render(request, 'leaveDetail.html', ctx)

    def post(self, request, pk):
        if request.method == "POST":
            try:
                attach = request.FILES.getlist('attachment')
                docNo = pk
                tableID = 52177494
                for files in attach:
                    fileName = request.FILES['attachment'].name
                    attachment = base64.b64encode(files.read())

                    response = config.CLIENT.service.FnUploadAttachedDocument(
                        docNo, fileName, attachment, tableID, request.session['User_ID'])
                if response == True:
                    messages.success(request, "Uploaded successfully")
                    return redirect('LeaveDetail', pk=pk)
                else:
                    messages.error(request, "Upload Not Successful")
                    return redirect('LeaveDetail', pk=pk)

            except Exception as e:
                messages.error(request, e)
                print(e)
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
            messages.error(request, e)
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
        messages.error(request, e)
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
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


class Training_Request(UserObjectMixin, View):
    def get(self, request):
        try:
            userId = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

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
               "year": year, "full": userId}
        return render(request, 'training.html', ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                employeeNo = request.session['Employee_No_']
                usersId = request.session['User_ID']
                requestNo = request.POST.get('requestNo')
                isAdhoc = eval(request.POST.get('isAdhoc'))
                trainingNeed = request.POST.get('trainingNeed')
                myAction = request.POST.get('myAction')
            except ValueError:
                messages.error(request, "Not sent. Invalid Input, Try Again!!")
                return redirect('training_request')
            if not requestNo:
                requestNo = ""

            if not trainingNeed:
                trainingNeed = ''
            try:
                response = config.CLIENT.service.FnTrainingRequest(
                    requestNo, employeeNo, usersId, isAdhoc, trainingNeed, myAction)
                messages.success(request, "Successfully Added!!")
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('training_request')
        return redirect('training_request')


class TrainingDetail(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            empNo = request.session['Employee_No_']

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
            messages.error(request, e)
            print(e)
            return redirect('training_request')

        ctx = {"today": self.todays_date, "res": res,
               "Approvers": Approvers, "year": year, "full": userID,
               "line": openLines, "local": Local, "foreign": Foreign, "Comments": Comments}
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
                messages.error(request, e)
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
                messages.error(request, e)
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
        messages.error(request, e)
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
            messages.error(request, e)
            print(e)
    return redirect('TrainingDetail', pk=pk)


def TrainingApproval(request, pk):
    myUserID = request.session['User_ID']
    trainingNo = ""
    Username = request.session['User_ID']
    Password = request.session['password']
    AUTHS = Session()
    AUTHS.auth = HTTPBasicAuth(Username, Password)
    CLIENT = Client(config.BASE_URL, transport=Transport(session=AUTHS))
    if request.method == 'POST':
        try:
            trainingNo = request.POST.get('trainingNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
        try:
            response = CLIENT.service.FnRequestTrainingApproval(
                myUserID, trainingNo)
            messages.success(request, "Approval Request Successfully Sent!!")
            print(response)
            return redirect('TrainingDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
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
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


class PNineRequest(UserObjectMixin, View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format("/QyPayrollPeriods")
            response = self.get_object(Access_Point)
            res = response['value']

        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('pNine')
        ctx = {"today": self.todays_date,
               "year": year, "full": userID, "res": res}
        return render(request, "p9.html", ctx)

    def post(self, request):
        if request.method == 'POST':
            try:
                nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                                    for i in range(5))
                employeeNo = request.session['Employee_No_']
                startDate = request.POST.get('startDate')[0:4]
                year = request.session['years']
            except ValueError as e:
                messages.error(request, "Not sent. Invalid Input, Try Again!!")
                return redirect('pNine')
            filenameFromApp = "P9_For_" + str(nameChars) + str(year) + ".pdf"
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
                messages.error(request, e)
                print(e)
                return redirect('pNine')


class PayslipRequest(UserObjectMixin, View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']

            Access_Point = config.O_DATA.format(
                "/QyPayrollPeriods?$filter=Closed%20eq%20true")
            response = self.get_object(Access_Point)
            Payslip = [x for x in response['value']]

        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('payslip')

        ctx = {"today": self.todays_date, "year": year,
               "full": userID, "res": Payslip}

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
                messages.error(request, e)
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
            messages.error(request, e)
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
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def Disciplinary(request):
    fullname = request.session['User_ID']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyEmployeeDisciplinaryCases")
    try:
        response = session.get(Access_Point, timeout=10).json()
        openCase = []
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
           "year": year, "full": fullname,
           "count": counts}
    return render(request, 'disciplinary.html', ctx)


def DisciplineDetail(request, pk):
    fullname = request.session['User_ID']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
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
        openLines = []
        for cases in responses['value']:
            if cases['Refference_No'] == pk and cases['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(cases)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res,
           "full": fullname, "year": year, "line": openLines}
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
        messages.error(request, e)
        print(e)
    return redirect('DisciplineDetail', pk=pk)
