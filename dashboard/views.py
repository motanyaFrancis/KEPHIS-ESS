from django.shortcuts import render, redirect
import requests
from django.conf import settings as config
import datetime
from django.contrib import messages
from django.views import View
import asyncio
import aiohttp
from myRequest .views import UserObjectMixins
from asgiref.sync import sync_to_async
# Create your views here.


class UserObjectMixin(object):
    model = None
    session = requests.Session()
    session.auth = config.AUTHS

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


class Dashboard(UserObjectMixins, View):

    async def get(self, request):
        try:
            User_ID = await sync_to_async(request.session.__getitem__)('User_ID')
            Employee_No_ = await sync_to_async(request.session.__getitem__)('Employee_No_')
            HOD_User = await sync_to_async(request.session.__getitem__)('HOD_User')
            full_name = await sync_to_async(request.session.__getitem__)('full_name')
            driver_role = await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role =await sync_to_async(request.session.__getitem__)('TO_role')
            print('Supervisor:',await sync_to_async(request.session.__getitem__)('SupervisorNo'))
            empAppraisal = ''
            pending_approval_count = 0
            total_leave =0
            ctx = {}
            
            async with aiohttp.ClientSession() as session:
                task_get_leave = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyLeaveApplications",
                                                                                                "User_ID","eq",User_ID))
                task_get_training = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyTrainingRequests",
                                                                                        "Employee_No","eq",Employee_No_))
                
                task_get_imprest = asyncio.ensure_future(self.simple_one_filtered_data(session,"/Imprests",
                                                                                        "User_Id","eq",User_ID))
                task_get_surrender = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyImprestSurrenders",
                                                                                        "User_Id","eq",User_ID))
                task_get_claim = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyStaffClaims",
                                                                                        "User_Id","eq",User_ID))
                task_get_purchase = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyPurchaseRequisitionHeaders",
                                                                                        "Employee_No_","eq",Employee_No_))
                task_get_repair = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyRepairRequisitionHeaders",
                                                                                        "Requested_By","eq",User_ID))
                task_get_store = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QyStoreRequisitionHeaders",
                                                                                        "Requested_By","eq",User_ID))
                task_get_advance = asyncio.ensure_future(self.simple_one_filtered_data(session,"/QySalaryAdvances",
                                                                                        "Employee_No","eq",Employee_No_))
                
                response = await asyncio.gather(task_get_leave,task_get_training,task_get_imprest,task_get_surrender,
                                                task_get_claim,task_get_purchase,task_get_repair,task_get_store,
                                                task_get_advance)
                
                total_leave = len(response[0])  # type: ignore
                open_leave = sum(1 for leave in response[0] if leave['Status'] == 'Open') # type: ignore
                app_leave_list = sum([1 for leave in response[0]  if leave['Status'] == 'Released']) # type: ignore
                pending_leave = sum([1 for leave in response[0] if leave['Status'] == 'Pending Approval'])  # type: ignore
                
                total_training = len(response[1])  # type: ignore
                open_training = sum(1 for training in response[1] if training['Status'] == 'Open') # type: ignore
                app_train_list = sum([1 for training in response[1]  if training['Status'] == 'Released']) # type: ignore
                pendTrain = sum([1 for training in response[1] if training['Status'] == 'Pending Approval'])  # type: ignore
                
                total_imprest = len(response[2])  # type: ignore
                open_imprests = sum(1 for imprest in response[2] if imprest['Status'] == 'Open') # type: ignore
                app_imprest_list = sum([1 for imprest in response[2]  if imprest['Status'] == 'Released']) # type: ignore
                pending_imprest = sum([1 for imprest in response[2] if imprest['Status'] == 'Pending Approval'])  # type: ignore
                
                total_surrender = len(response[3])  # type: ignore
                open_surrender = sum(1 for surrender in response[3] if surrender['Status'] == 'Open') # type: ignore
                app_surrender_list = sum([1 for surrender in response[3]  if surrender['Status'] == 'Released']) # type: ignore
                pending_surrender = sum([1 for surrender in response[3] if surrender['Status'] == 'Pending Approval'])  # type: ignore
                
                total_claims = len(response[4])  # type: ignore
                open_claim = sum(1 for claim in response[4] if claim['Status'] == 'Open') # type: ignore
                app_claim_list = sum([1 for claim in response[4]  if claim['Status'] == 'Released']) # type: ignore
                pending_claims = sum([1 for claim in response[4] if claim['Status'] == 'Pending Approval'])  # type: ignore
                
                total_purchase = len(response[5])  # type: ignore
                open_purchase = sum(1 for purchase in response[5] if purchase['Status'] == 'Open') # type: ignore
                app_purchase_list = sum([1 for purchase in response[5]  if purchase['Status'] == 'Released']) # type: ignore
                pending_purchase = sum([1 for purchase in response[5] if purchase['Status'] == 'Pending Approval'])  # type: ignore
                
                total_repair = len(response[6])  # type: ignore
                open_repair = sum(1 for repair in response[6] if repair['Status'] == 'Open') # type: ignore
                app_repair_list = sum([1 for repair in response[6]  if repair['Status'] == 'Released']) # type: ignore
                pending_repair = sum([1 for repair in response[6] if repair['Status'] == 'Pending Approval'])  # type: ignore
                
                total_store = len(response[7])  # type: ignore
                open_store = sum(1 for store in response[7] if store['Status'] == 'Open') # type: ignore
                app_store_list = sum([1 for store in response[7]  if store['Status'] == 'Released']) # type: ignore
                pending_store = sum([1 for store in response[7] if store['Status'] == 'Pending Approval'])  # type: ignore  
                                                 
                open_advances = sum(1 for advance in response[8] if advance['Loan_Status'] == 'Application') # type: ignore
                Pending_advances = sum([1 for advance in response[8]  if advance['Loan_Status'] == 'Being Processed']) # type: ignore
                approved_advances = sum([1 for advance in response[8] if advance['Loan_Status'] == 'Approved'])  # type: ignore 
                           
            ctx ={
                "total_leave":total_leave,"open_leave":open_leave,"app_leave_list":app_leave_list,
                "pending_leave":pending_leave,"total_training":total_training,"open_training":open_training,
                "app_train_list":app_train_list,"pendTrain":pendTrain,"total_imprest":total_imprest,
                "open_imprests":open_imprests,"app_imprest_list":app_imprest_list,"pending_imprest":pending_imprest,
                "total_surrender":total_surrender,"open_surrender":open_surrender,"app_surrender_list":app_surrender_list,
                "pending_surrender":pending_surrender,"total_claims":total_claims,"open_claim":open_claim,
                "app_claim_list":app_claim_list,"pending_claims":pending_claims,"total_purchase":total_purchase,
                "open_purchase":open_purchase,"app_purchase_list":app_purchase_list,"pending_purchase":pending_purchase,
                "total_repair":total_repair,"open_repair":open_repair,"app_repair_list":app_repair_list,
                "pending_repair":pending_repair,"total_store":total_store,"open_store":open_store,
                "app_store_list":app_store_list,"pending_store":pending_store,"empAppraisal":empAppraisal,
                "pending_approval_count":pending_approval_count,"today": self.todays_date,"full":full_name,
                "HOD_User":HOD_User,"open_advances":open_advances,"driver_role":driver_role,"TO_role":TO_role,
                "Pending_advances":Pending_advances,"approved_advances":approved_advances,
            }
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"Connection Error")
            return redirect('auth')   
        except Exception as e:
            print(e)
            messages.error(request,"Connection/network error,retry")
            return redirect('auth')  
        return render(request, 'main/dashboard.html', ctx)


class Manual(View):
    def get(self, request):
        try:
            userId = request.session['User_ID']
            todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        except KeyError as e:
            print(e)
            messages.success(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {"today": todays_date, "full": userId, }
        return render(request, "manual.html", ctx)

class OffCanvas(UserObjectMixin,View):
    def get(self, request):
        driver_role =request.session['driver_role']
        TO_role =request.session['TO_role']
        ctx ={
            "driver_role":driver_role,
        }
        return render(request,'base.html',ctx)