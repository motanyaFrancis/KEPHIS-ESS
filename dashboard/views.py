from django.shortcuts import render, redirect
import requests
import json
from django.conf import settings as config
import datetime
from django.contrib import messages
from django.views import View
# Create your views here.


class UserObjectMixin(object):
    model = None
    session = requests.Session()
    session.auth = config.AUTHS

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


class Dashboard(UserObjectMixin, View):

    def get(self, request):
        userId = request.session['User_ID']
        empNo = request.session['Employee_No_']
        todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        try:

            Access_Leave = config.O_DATA.format(
                f"/QyLeaveApplications?$filter=User_ID%20eq%20%27{userId}%27%20")
            Leave = self.get_object(Access_Leave)
            open_leave_list = len(
                [x for x in Leave['value'] if x['Status'] == 'Open'])
            app_leave_list = len(
                [x for x in Leave['value'] if x['Status'] == 'Released'])
            pendLeave = len([x for x in Leave['value']
                            if x['Status'] == 'Pending Approval'])

            Access_Train = config.O_DATA.format(
                f"/QyTrainingRequests?$filter=Employee_No%20eq%20%27{empNo}%27")
            Training = self.get_object(Access_Train)
            open_train_list = len(
                [x for x in Training['value'] if x['Status'] == 'Open'])
            app_train_list = len(
                [x for x in Training['value'] if x['Status'] == 'Released'])
            pendTrain = len([x for x in Training['value']
                            if x['Status'] == 'Pending Approval'])

            Access_Imprest = config.O_DATA.format(
                f"/Imprests?$filter=User_Id%20eq%20%27{userId}%27%20")
            myImprest = self.get_object(Access_Imprest)
            open_imp_list = len(
                [x for x in myImprest['value'] if x['Status'] == 'Open'])
            app_imp_list = len(
                [x for x in myImprest['value'] if x['Status'] == 'Released'])
            pendImp = len([x for x in myImprest['value']
                          if x['Status'] == 'Pending Approval'])

            Access_Surrender = config.O_DATA.format(
                f"/QyImprestSurrenders?$filter=User_Id%20eq%20%27{userId}%27")
            Surrender = self.get_object(Access_Surrender)
            open_surrender_list = len(
                [x for x in Surrender['value'] if x['Status'] == 'Open'])
            app_surrender_list = len(
                [x for x in Surrender['value'] if x['Status'] == 'Released'])
            pendSurrender = len(
                [x for x in Surrender['value'] if x['Status'] == 'Pending Approval'])

            Access_Claim = config.O_DATA.format(
                f"/QyStaffClaims?$filter=User_Id%20eq%20%27{userId}%27")
            Claim = self.get_object(Access_Claim)
            open_claim_list = len(
                [x for x in Claim['value'] if x['Status'] == 'Open'])
            app_claim_list = len(
                [x for x in Claim['value'] if x['Status'] == 'Released'])
            pendClaim = len([x for x in Claim['value']
                            if x['Status'] == 'Pending Approval'])

            Access_purchase = config.O_DATA.format(
                f"/QyPurchaseRequisitionHeaders?$filter=Employee_No_%20eq%20%27{empNo}%27")
            Purchase = self.get_object(Access_purchase)
            open_purchase_list = len(
                [x for x in Purchase['value'] if x['Status'] == 'Open'])
            app_purchase_list = len(
                [x for x in Purchase['value'] if x['Status'] == 'Released'])
            pendPurchase = len(
                [x for x in Purchase['value'] if x['Status'] == 'Pending Approval'])

            Access_Repair = config.O_DATA.format(
                f"/QyRepairRequisitionHeaders?$filter=Requested_By%20eq%20%27{userId}%27")
            Repair = self.get_object(Access_Repair)
            open_repair_list = len(
                [x for x in Repair['value'] if x['Status'] == 'Open'])
            app_repair_list = len(
                [x for x in Repair['value'] if x['Status'] == 'Released'])
            pendRepair = len([x for x in Repair['value']
                             if x['Status'] == 'Pending Approval'])

            Access_Store = config.O_DATA.format(
                f"/QyStoreRequisitionHeaders?$filter=Requested_By%20eq%20%27{userId}%27")
            Store = self.get_object(Access_Store)
            open_store_list = len(
                [x for x in Store['value'] if x['Status'] == 'Open'])
            app_store_list = len(
                [x for x in Store['value'] if x['Status'] == 'Released'])
            pendStore = len([x for x in Store['value']
                            if x['Status'] == 'Pending Approval'])

        except requests.exceptions.ConnectionError as e:
            print(e)
        except KeyError as e:
            print(e)
            messages.success(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {"today": todays_date,
               "res": open, "full": userId,
               "imprest_open": open_imp_list, "pendImp": pendImp, "imprest_app": app_imp_list,
               "open_train": open_train_list, "pendTrain": pendTrain, "app_train": app_train_list,
               "open_store": open_store_list, "app_store": app_store_list, "pendStore": pendStore,
               "leave_open": open_leave_list, "pendLeave": pendLeave, "leave_app": app_leave_list,
               "open_repair": open_repair_list, "app_repair": app_repair_list, "pendRepair": pendRepair,
               "surrender_open": open_surrender_list, "pendSurrender": pendSurrender, "surrender_app": app_surrender_list,
               "open_claim": open_claim_list, "app_claim": app_claim_list, "pendClaim": pendClaim,
               "open_purchase": open_purchase_list, "app_purchase": app_purchase_list, "pendPurchase": pendPurchase,
               }
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
