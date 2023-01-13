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
from zeep.client import Client
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
    
    
class Appraisals(UserObjectMixin, View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            Access_Point = config.O_DATA.format(f"/QyEmployeeAppraisal?$filter=AppraiseeID%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            
            open= [
                x for x in response['value'] if x['Status'] == 'Open'
            ]

            Pending = [
                x for x in response['value']
                if x['Status'] == 'Pending Approval'
            ]

            Approved = [
                x for x in response['value'] if x['Status'] == 'Approved'
            ]

            Appraisal = [
                x for x in response['value'] 
                if x['Status'] == 'Approved' and x['DocumentStage'] == 'Appraisal'
            ]

            Supervisor = [
                x for x in response['value'] 
                if x['Status'] == 'Approved' and x['DocumentStage'] == 'Supervisor'
            ]
            
            Completed = [
                x for x in response['value'] 
                if x['Status'] == 'Approved' and x['DocumentStage'] == 'Completed'
            ]

            counts = len(open)

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
            "res": open,
            "count": counts,
            "response": Approved,
            "counter": counter,
            "pend": pend,
            "pending": Pending,
            "year": year,
            "full": userID,
        }
                
        return render(request, 'appraisals.html', ctx)
    
    def post(self, request):
        if request.method == 'POST':
            try:
                apprsailNo = request.POST.get('apprsailNo')
                apprasailPeriod = request.POST.get('apprasailPeriod')
                appraiseeNo = request.session['User_ID']
                appraiserNo = request.POST.get('appraiserNo')
                remarks = request.POST.get('remarks')
                myAction = request.POST.get('myAction')
            
            except ValueError:
                messages.error(request, "Missing Input")
                return redirect('Appraisals')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
            
            if not apprsailNo:
                apprsailNo = " "
                
            try:
                response = config.CLIENT.service.FnAppraisalForm(
                apprsailNo, apprasailPeriod, appraiseeNo, appraiserNo, remarks, myAction )
                messages.success(request, 'request successful')
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('Appraisals')
        return redirect('Appraisals')

class AppraisalDetails(UserObjectMixin, View):
    def get(self, request, pk):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            
            Access_Point = config.O_DATA.format(f"/QyEmployeeAppraisal?$filter=AppraisalNo%20eq%20%27{pk}%27%20and%20AppraiseeID%20eq%20%27{userID}%27")
            response = self.get_object(Access_Point)
            for appraisal in response['value']:
                res = appraisal
                
        except Exception as e:
            print(e)
            messages.info(request, "Wrong UserID")
            return redirect('Appraisals')
        
        ctx = {
            "res": res,
            "today": self.todays_date,
            "year": year,
            'full': userID
            # 'Approvers': Approvers,
            # 'allFiles': allFiles,
            # "line": openLines,
        }
            
        return render(request, 'appraisalDetails.html', ctx)